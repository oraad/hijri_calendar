"""Calendar platform for hijri_calendar."""

from __future__ import annotations

import datetime as dt

from homeassistant.components.calendar import (
    CalendarEntity,
    CalendarEntityDescription,
    CalendarEvent,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from .calendar_events import CalendarEventConfig, build_calendar_events
from .data import HijriCalendarConfigEntry
from .entity import HijriCalendarEntity

PARALLEL_UPDATES = 0

CALENDAR_DESCRIPTION = CalendarEntityDescription(
    key="hijri_events",
    translation_key="hijri_events",
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: HijriCalendarConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Hijri calendar events."""
    async_add_entities([HijriCalendarCalendarEntity(config_entry)])


class HijriCalendarCalendarEntity(HijriCalendarEntity, CalendarEntity):
    """Calendar of Hijri observances mapped to Gregorian dates."""

    _attr_entity_category = None
    entity_description = CALENDAR_DESCRIPTION

    def __init__(self, config_entry: HijriCalendarConfigEntry) -> None:
        """Initialize the calendar entity."""
        super().__init__(config_entry, CALENDAR_DESCRIPTION)

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming calendar event."""
        now = dt_util.now()
        end = now + dt.timedelta(days=365)
        events = build_calendar_events(
            self.hass,
            CalendarEventConfig(
                language=self.coordinator.language,  # type: ignore[arg-type]
                day_boundary=self.coordinator.day_boundary,
                offset_days=self.coordinator.offset_days,
            ),
            now,
            end,
        )
        for event in sorted(events, key=lambda item: item.start_datetime_local):
            if event.start_datetime_local >= now:
                return event
        return None

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: dt.datetime,
        end_date: dt.datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        return build_calendar_events(
            hass,
            CalendarEventConfig(
                language=self.coordinator.language,  # type: ignore[arg-type]
                day_boundary=self.coordinator.day_boundary,
                offset_days=self.coordinator.offset_days,
            ),
            start_date,
            end_date,
        )

    def _update_times(self) -> list[dt.datetime | None]:
        """Return update times; calendar refreshes via coordinator."""
        return []
