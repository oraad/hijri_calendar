"""Hijri Calendar integration for Home Assistant."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import CONF_LANGUAGE, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import translation

from .calendar_common import resolve_calendar_display_language
from .const import (
    CONF_ISLAMIC_HISTORY_CALENDAR_LANGUAGE,
    CONF_OBSERVANCES_CALENDAR_LANGUAGE,
    DEFAULT_CALENDAR_LANGUAGE,
    DEFAULT_LANGUAGE,
    DOMAIN,
    HijriLanguage,
)
from .coordinator import HijriCalendarUpdateCoordinator
from .repairs import async_clear_sunset_repairs
from .services import async_setup_services

if TYPE_CHECKING:
    from homeassistant.helpers.typing import ConfigType

    from .data import HijriCalendarConfigEntry

__all__ = ["DOMAIN"]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.CALENDAR,
]


async def _preload_calendar_languages(
    hass: HomeAssistant,
    integration_language: HijriLanguage,
    options: dict,
) -> None:
    """Preload entity translations for resolved calendar display languages."""
    languages: set[HijriLanguage] = {integration_language}
    for option_key in (
        CONF_OBSERVANCES_CALENDAR_LANGUAGE,
        CONF_ISLAMIC_HISTORY_CALENDAR_LANGUAGE,
    ):
        resolved = resolve_calendar_display_language(
            integration_language,
            str(options.get(option_key, DEFAULT_CALENDAR_LANGUAGE)),
        )
        languages.add(resolved)
    for language in languages:
        for category in ("entity", "calendar_content"):
            await translation.async_get_translations(
                hass, language, category, integrations=[DOMAIN]
            )


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up Hijri Calendar services."""
    async_setup_services(hass)
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: HijriCalendarConfigEntry,
) -> bool:
    """Set up Hijri Calendar from a config entry."""
    language: HijriLanguage = config_entry.data.get(CONF_LANGUAGE, DEFAULT_LANGUAGE)  # type: ignore[assignment]
    await _preload_calendar_languages(hass, language, config_entry.options)

    coordinator = HijriCalendarUpdateCoordinator(hass, config_entry)
    await coordinator.async_config_entry_first_refresh()

    config_entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    config_entry: HijriCalendarConfigEntry,
) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    ):
        await config_entry.runtime_data.async_shutdown()
        async_clear_sunset_repairs(hass, config_entry)
    return unload_ok
