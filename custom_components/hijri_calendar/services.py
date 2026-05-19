"""Services for Hijri Calendar."""

from __future__ import annotations

import datetime as dt
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
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.selector import LanguageSelector, LanguageSelectorConfig
from homeassistant.util import dt as dt_util

from .const import (
    ATTR_DATE,
    ATTR_OFFSET,
    CONF_DAY_BOUNDARY,
    CONF_OFFSET_DAYS,
    DEFAULT_DAY_BOUNDARY,
    DEFAULT_LANGUAGE,
    DEFAULT_OFFSET_DAYS,
    DOMAIN,
    SERVICE_CALIBRATE_DATE,
    SERVICE_CONVERT_TO_GREGORIAN,
    SERVICE_CONVERT_TO_HIJRI,
    SERVICE_SET_DAY_OFFSET,
    SUPPORTED_LANGUAGES,
)
from .helpers import (
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

CALIBRATE_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_DATE): cv.date,
        vol.Optional(ATTR_OFFSET, default=DEFAULT_OFFSET_DAYS): vol.All(
            vol.Coerce(int),
            vol.Range(min=-30, max=30),
        ),
        vol.Optional(CONF_LANGUAGE, default=DEFAULT_LANGUAGE): LANGUAGE_SELECTOR,
    }
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
            vol.Range(min=-30, max=30),
        ),
    }
)


def _get_config_defaults(hass: HomeAssistant) -> tuple[str, int, str]:
    """Return language, offset, and day boundary from the config entry if present."""
    entries = hass.config_entries.async_entries(DOMAIN)
    if not entries:
        return DEFAULT_LANGUAGE, DEFAULT_OFFSET_DAYS, "midnight"

    entry = entries[0]

    return (
        entry.data.get(CONF_LANGUAGE, DEFAULT_LANGUAGE),
        int(entry.options.get(CONF_OFFSET_DAYS, DEFAULT_OFFSET_DAYS)),
        entry.data.get(CONF_DAY_BOUNDARY, DEFAULT_DAY_BOUNDARY),
    )


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
        """Return Hijri date for a Gregorian date with an optional offset."""
        language, _, _ = _get_config_defaults(hass)
        language = call.data.get(CONF_LANGUAGE, language)

        input_date: dt.date = call.data.get(ATTR_DATE, dt_util.now().date())
        offset: int = call.data.get(ATTR_OFFSET, DEFAULT_OFFSET_DAYS)
        adjusted_date = input_date + dt.timedelta(days=offset)
        hijri = await async_gregorian_to_hijri(hass, adjusted_date)

        result = format_hijri_dict(hijri, language)
        result["input_gregorian"] = input_date.isoformat()
        result["adjusted_gregorian"] = adjusted_date.isoformat()
        result["offset"] = offset
        return result

    async def set_day_offset(call: ServiceCall) -> None:
        """Persist day offset to the config entry options."""
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            return
        entry = entries[0]
        offset: int = call.data[ATTR_OFFSET]
        hass.config_entries.async_update_entry(
            entry,
            options={**entry.options, CONF_OFFSET_DAYS: offset},
        )
        await hass.config_entries.async_reload(entry.entry_id)

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
