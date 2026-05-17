"""Data classes for hijri_calendar."""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import TYPE_CHECKING

from hijridate import Hijri

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

    from .coordinator import HijriCalendarUpdateCoordinator


type HijriCalendarConfigEntry = ConfigEntry[HijriCalendarUpdateCoordinator]


@dataclass(frozen=True)
class HijriCalendarData:
    """Runtime data computed by the coordinator."""

    language: str
    day_boundary: str
    offset_days: int
    gregorian_date: dt.date
    hijri: Hijri
