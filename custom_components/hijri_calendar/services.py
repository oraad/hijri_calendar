"""Services for Hijri Calendar."""

from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant.const import CONF_LANGUAGE
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
    callback,
)
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.selector import LanguageSelector, LanguageSelectorConfig

from .const import (
    ATTR_DATE,
    ATTR_HIJRI,
    ATTR_OFFSET,
    CONF_DAY_BOUNDARY,
    CONF_OFFSET_DAYS,
    DEFAULT_DAY_BOUNDARY,
    DEFAULT_LANGUAGE,
    DEFAULT_OFFSET_DAYS,
    DOMAIN,
    OFFSET_DAYS_MAX,
    OFFSET_DAYS_MIN,
    SERVICE_CALIBRATE_DATE,
    SERVICE_CONVERT_TO_GREGORIAN,
    SERVICE_CONVERT_TO_HIJRI,
    SERVICE_SET_DAY_OFFSET,
    SUPPORTED_LANGUAGES,
)
from .data import HijriCalendarConfigEntry
from .helpers import (
    async_compute_offset_for_hijri_today,
    async_gregorian_to_hijri,
    async_hijri_to_gregorian,
    async_parse_hijri_date,
    async_resolve_effective_gregorian_date,
    format_gregorian_dict,
    format_hijri_dict,
)

_LOGGER = logging.getLogger(__name__)

LANGUAGE_SELECTOR = LanguageSelector(
    LanguageSelectorConfig(languages=list(SUPPORTED_LANGUAGES)),
)

_CALIBRATE_LANGUAGE = {
    vol.Optional(CONF_LANGUAGE, default=DEFAULT_LANGUAGE): LANGUAGE_SELECTOR,
}

CALIBRATE_SCHEMA = vol.Any(
    vol.Schema(
        {
            vol.Required(ATTR_OFFSET): vol.All(
                vol.Coerce(int),
                vol.Range(min=OFFSET_DAYS_MIN, max=OFFSET_DAYS_MAX),
            ),
            **_CALIBRATE_LANGUAGE,
        }
    ),
    vol.Schema(
        {
            vol.Required(ATTR_HIJRI): cv.string,
            **_CALIBRATE_LANGUAGE,
        }
    ),
)

CONVERT_TO_HIJRI_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_DATE): cv.date,
        vol.Optional(CONF_LANGUAGE, default=DEFAULT_LANGUAGE): LANGUAGE_SELECTOR,
    }
)

CONVERT_TO_GREGORIAN_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_DATE): cv.string,
        vol.Optional(CONF_LANGUAGE, default=DEFAULT_LANGUAGE): LANGUAGE_SELECTOR,
    }
)

SET_DAY_OFFSET_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_OFFSET): vol.All(
            vol.Coerce(int),
            vol.Range(min=OFFSET_DAYS_MIN, max=OFFSET_DAYS_MAX),
        ),
    }
)


def _get_config_entry(hass: HomeAssistant) -> HijriCalendarConfigEntry | None:
    """Return the Hijri Calendar config entry if configured."""
    entries = hass.config_entries.async_entries(DOMAIN)
    if not entries:
        return None
    return entries[0]


def _get_config_defaults(hass: HomeAssistant) -> tuple[str, int, str]:
    """Return language, offset, and day boundary from the config entry if present."""
    entry = _get_config_entry(hass)
    if entry is None:
        return DEFAULT_LANGUAGE, DEFAULT_OFFSET_DAYS, DEFAULT_DAY_BOUNDARY

    return (
        entry.data.get(CONF_LANGUAGE, DEFAULT_LANGUAGE),
        int(entry.options.get(CONF_OFFSET_DAYS, DEFAULT_OFFSET_DAYS)),
        entry.data.get(CONF_DAY_BOUNDARY, DEFAULT_DAY_BOUNDARY),
    )


def _clamp_offset(offset: int) -> int:
    """Clamp offset to integration options range."""
    return max(OFFSET_DAYS_MIN, min(OFFSET_DAYS_MAX, offset))


async def _async_set_offset(
    hass: HomeAssistant, entry: HijriCalendarConfigEntry, new_offset: int
) -> int:
    """Persist day offset to the config entry options and reload if changed."""
    new_offset = _clamp_offset(new_offset)
    current = int(entry.options.get(CONF_OFFSET_DAYS, DEFAULT_OFFSET_DAYS))
    if new_offset == current:
        return new_offset

    hass.config_entries.async_update_entry(
        entry,
        options={**entry.options, CONF_OFFSET_DAYS: new_offset},
    )
    await hass.config_entries.async_reload(entry.entry_id)
    return new_offset


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    """Set up Hijri Calendar services."""

    async def convert_to_hijri(call: ServiceCall) -> ServiceResponse:
        """Convert a Gregorian date to Hijri."""
        language, offset_days, day_boundary = _get_config_defaults(hass)
        language = call.data.get(CONF_LANGUAGE, language)

        if ATTR_DATE in call.data:
            gregorian_date = call.data[ATTR_DATE]
        else:
            gregorian_date = await async_resolve_effective_gregorian_date(
                hass, day_boundary, offset_days
            )

        hijri = await async_gregorian_to_hijri(hass, gregorian_date)
        return format_hijri_dict(hijri, language)

    async def convert_to_gregorian(call: ServiceCall) -> ServiceResponse:
        """Convert a Hijri date to Gregorian."""
        language, _, day_boundary = _get_config_defaults(hass)
        language = call.data.get(CONF_LANGUAGE, language)

        if ATTR_DATE in call.data:
            hijri = await async_parse_hijri_date(hass, call.data[ATTR_DATE])
        else:
            _, offset_days, _ = _get_config_defaults(hass)
            effective = await async_resolve_effective_gregorian_date(
                hass, day_boundary, offset_days
            )
            hijri = await async_gregorian_to_hijri(hass, effective)

        gregorian = await async_hijri_to_gregorian(hass, hijri)
        return format_gregorian_dict(gregorian, language)

    async def calibrate_date(call: ServiceCall) -> ServiceResponse:
        """Calibrate integration day offset from a relative tweak or announced Hijri date."""
        entry = _get_config_entry(hass)
        if entry is None:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="calibrate_no_config_entry",
            )

        language, current_offset, day_boundary = _get_config_defaults(hass)
        language = call.data.get(CONF_LANGUAGE, language)
        previous_offset = current_offset

        if ATTR_OFFSET in call.data:
            new_offset = _clamp_offset(current_offset + call.data[ATTR_OFFSET])
        else:
            target_hijri = await async_parse_hijri_date(hass, call.data[ATTR_HIJRI])
            computed = await async_compute_offset_for_hijri_today(
                hass, day_boundary, target_hijri
            )
            new_offset = _clamp_offset(computed)
            if new_offset != computed:
                raise HomeAssistantError(
                    translation_domain=DOMAIN,
                    translation_key="calibrate_offset_out_of_range",
                    translation_placeholders={
                        "offset": str(computed),
                        "min": str(OFFSET_DAYS_MIN),
                        "max": str(OFFSET_DAYS_MAX),
                    },
                )

        new_offset = await _async_set_offset(hass, entry, new_offset)

        effective_gregorian = await async_resolve_effective_gregorian_date(
            hass, day_boundary, new_offset
        )
        hijri = await async_gregorian_to_hijri(hass, effective_gregorian)

        result = format_hijri_dict(hijri, language)
        result["offset"] = new_offset
        result["previous_offset"] = previous_offset
        result["effective_gregorian"] = effective_gregorian.isoformat()
        return result

    async def set_day_offset(call: ServiceCall) -> None:
        """Persist day offset to the config entry options."""
        entry = _get_config_entry(hass)
        if entry is None:
            return
        await _async_set_offset(hass, entry, call.data[ATTR_OFFSET])

    if not hass.services.has_service(DOMAIN, SERVICE_CONVERT_TO_HIJRI):
        hass.services.async_register(
            DOMAIN,
            SERVICE_CONVERT_TO_HIJRI,
            convert_to_hijri,
            schema=CONVERT_TO_HIJRI_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_CONVERT_TO_GREGORIAN):
        hass.services.async_register(
            DOMAIN,
            SERVICE_CONVERT_TO_GREGORIAN,
            convert_to_gregorian,
            schema=CONVERT_TO_GREGORIAN_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_CALIBRATE_DATE):
        hass.services.async_register(
            DOMAIN,
            SERVICE_CALIBRATE_DATE,
            calibrate_date,
            schema=CALIBRATE_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_SET_DAY_OFFSET):
        hass.services.async_register(
            DOMAIN,
            SERVICE_SET_DAY_OFFSET,
            set_day_offset,
            schema=SET_DAY_OFFSET_SCHEMA,
        )
