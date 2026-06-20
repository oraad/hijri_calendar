"""Build Home Assistant calendar events for Islamic historical milestones."""

from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING

from homeassistant.components.calendar import CalendarEvent

from .calendar_common import CalendarEventConfig, clamp_range, scan_days
from .const import DOMAIN
from .historical_events import events_by_hijri_date
from .locale import build_history_description, calendar_history_name

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


def build_history_calendar_events(
    hass: HomeAssistant,
    config: CalendarEventConfig,
    start_date: dt.datetime,
    end_date: dt.datetime,
) -> list[CalendarEvent]:
    """Build history calendar events for the requested Gregorian datetime range."""
    start, end = clamp_range(start_date, end_date)
    days = scan_days(hass, config.day_boundary, config.offset_days, start, end)
    history_index = events_by_hijri_date()
    events: list[CalendarEvent] = []
    language = config.display_language

    for day in days:
        historical = history_index.get((day.hijri_month, day.hijri_day), ())
        events.extend(
            CalendarEvent(
                start=day.gregorian_date,
                end=day.gregorian_date + dt.timedelta(days=1),
                summary=calendar_history_name(hass, milestone.id, language),
                description=build_history_description(
                    hass, milestone.id, milestone.hijri_year, language
                ),
                uid=(
                    f"{DOMAIN}:history:{milestone.id}:{day.gregorian_date.isoformat()}"
                ),
            )
            for milestone in historical
        )

    return events
