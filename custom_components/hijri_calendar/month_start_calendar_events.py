"""Build Home Assistant calendar events for Hijri month starts."""

from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING

from hijridate import Hijri
from homeassistant.components.calendar import CalendarEvent

from .calendar_common import CalendarEventConfig, clamp_range, scan_days
from .const import DOMAIN
from .hijridate_locale import hijridate_language
from .locale import build_month_start_description, calendar_month_start_summary

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


def build_month_start_calendar_events(
    hass: HomeAssistant,
    config: CalendarEventConfig,
    start_date: dt.datetime,
    end_date: dt.datetime,
) -> list[CalendarEvent]:
    """Build month-start calendar events for the requested Gregorian datetime range."""
    start, end = clamp_range(start_date, end_date)
    days = scan_days(hass, config.day_boundary, config.offset_days, start, end)
    events: list[CalendarEvent] = []
    language = config.display_language

    for day in days:
        if day.hijri_day != 1:
            continue
        hijri = Hijri(day.hijri_year, day.hijri_month, 1)
        month_name = hijri.month_name(hijridate_language(language))
        events.append(
            CalendarEvent(
                start=day.gregorian_date,
                end=day.gregorian_date + dt.timedelta(days=1),
                summary=calendar_month_start_summary(
                    hass, month_name, language
                ),
                description=build_month_start_description(
                    hass, month_name, day.hijri_year, language
                ),
                uid=(
                    f"{DOMAIN}:month_start:{day.hijri_month}:"
                    f"{day.gregorian_date.isoformat()}"
                ),
            )
        )

    return events
