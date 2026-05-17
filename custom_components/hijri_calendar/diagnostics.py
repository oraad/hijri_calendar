"""Diagnostics support for Hijri Calendar."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from .coordinator import HijriCalendarUpdateCoordinator
from .data import HijriCalendarConfigEntry

TO_REDACT: set[str] = set()


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: HijriCalendarConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: HijriCalendarUpdateCoordinator = entry.runtime_data
    data = coordinator.data

    return async_redact_data(
        {
            "config": entry.data,
            "options": entry.options,
            "hijri_date": data.hijri.isoformat(),
            "gregorian_date": data.gregorian_date.isoformat(),
            "language": data.language,
            "day_boundary": data.day_boundary,
            "offset_days": data.offset_days,
        },
        TO_REDACT,
    )
