"""Hijri Calendar integration for Home Assistant."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import CONF_LANGUAGE, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import translation

from .const import DEFAULT_LANGUAGE, DOMAIN
from .coordinator import HijriCalendarUpdateCoordinator
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


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up Hijri Calendar services."""
    async_setup_services(hass)
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: HijriCalendarConfigEntry,
) -> bool:
    """Set up Hijri Calendar from a config entry."""
    language = config_entry.data.get(CONF_LANGUAGE, DEFAULT_LANGUAGE)
    await translation.async_get_translations(
        hass, language, "entity", integrations=[DOMAIN]
    )

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
    return unload_ok
