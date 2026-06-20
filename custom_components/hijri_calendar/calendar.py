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

from .calendar_common import CalendarEventConfig
from .calendar_events import build_calendar_events
from .data import HijriCalendarConfigEntry
from .entity import HijriCalendarEntity
from .history_calendar_events import build_history_calendar_events

PARALLEL_UPDATES = 0

OBSERVANCES_CALENDAR_DESCRIPTION = CalendarEntityDescription(
    key="hijri_events",
    translation_key="hijri_events",
)

HISTORY_CALENDAR_DESCRIPTION = CalendarEntityDescription(
    key="islamic_history",
    translation_key="islamic_history",
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: HijriCalendarConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Hijri calendar events."""
    async_add_entities(
        [
            HijriObservancesCalendarEntity(config_entry),
            IslamicHistoryCalendarEntity(config_entry),
        ]
    )


class _HijriCalendarBase(HijriCalendarEntity, CalendarEntity):
    """Shared calendar behavior."""

    _attr_entity_category = None

    def _update_times(self) -> list[dt.datetime | None]:
        """Return update times; calendar refreshes via coordinator."""
        return []


class HijriObservancesCalendarEntity(_HijriCalendarBase):
    """Calendar of Hijri observances mapped to Gregorian dates."""

    entity_description = OBSERVANCES_CALENDAR_DESCRIPTION

    def __init__(self, config_entry: HijriCalendarConfigEntry) -> None:
        """Initialize the calendar entity."""
        super().__init__(config_entry, OBSERVANCES_CALENDAR_DESCRIPTION)

    def _event_config(self) -> CalendarEventConfig:
        coordinator = self.coordinator
        return CalendarEventConfig(
            display_language=coordinator.observances_display_language,  # type: ignore[arg-type]
            day_boundary=coordinator.day_boundary,
            offset_days=coordinator.offset_days,
        )

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming calendar event."""
        now = dt_util.now()
        end = now + dt.timedelta(days=365)
        events = build_calendar_events(self.hass, self._event_config(), now, end)
        for item in sorted(events, key=lambda event: event.start_datetime_local):
            if item.start_datetime_local >= now:
                return item
        return None

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: dt.datetime,
        end_date: dt.datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        return build_calendar_events(hass, self._event_config(), start_date, end_date)


class IslamicHistoryCalendarEntity(_HijriCalendarBase):
    """Calendar of Islamic historical milestones."""

    entity_description = HISTORY_CALENDAR_DESCRIPTION

    def __init__(self, config_entry: HijriCalendarConfigEntry) -> None:
        """Initialize the history calendar entity."""
        super().__init__(config_entry, HISTORY_CALENDAR_DESCRIPTION)

    def _event_config(self) -> CalendarEventConfig:
        coordinator = self.coordinator
        return CalendarEventConfig(
            display_language=coordinator.history_display_language,  # type: ignore[arg-type]
            day_boundary=coordinator.day_boundary,
            offset_days=coordinator.offset_days,
        )

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming history event."""
        now = dt_util.now()
        end = now + dt.timedelta(days=365)
        events = build_history_calendar_events(
            self.hass, self._event_config(), now, end
        )
        for item in sorted(events, key=lambda event: event.start_datetime_local):
            if item.start_datetime_local >= now:
                return item
        return None

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: dt.datetime,
        end_date: dt.datetime,
    ) -> list[CalendarEvent]:
        """Return history calendar events within a datetime range."""
        return build_history_calendar_events(
            hass, self._event_config(), start_date, end_date
        )
