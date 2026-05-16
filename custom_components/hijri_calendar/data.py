"""Custom types for hijri_calendar."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .coordinator import HijriCalendarDataUpdateCoordinator


type HijriCalendarConfigEntry = ConfigEntry[HijriCalendarData]


@dataclass
class HijriCalendarData:
    """Data for the Blueprint integration."""

    coordinator: HijriCalendarDataUpdateCoordinator
    integration: Integration
