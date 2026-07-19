"""Test Islamic history calendar events."""

from __future__ import annotations

import datetime as dt

from hijridate import Hijri
from homeassistant.components.calendar import CalendarEvent
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import translation

from custom_components.hijri_calendar.calendar_common import CalendarEventConfig
from custom_components.hijri_calendar.const import DAY_BOUNDARY_MIDNIGHT, DOMAIN
from custom_components.hijri_calendar.history_calendar_events import (
    build_history_calendar_events,
)


def _history_entity_id(hass, entry_id: str) -> str:
    """Return entity_id for the Islamic history calendar."""
    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id(
        "calendar", DOMAIN, f"{entry_id}-islamic_history"
    )
    assert entity_id is not None
    return entity_id


def _events_in_range(
    hass,
    start: dt.date,
    end: dt.date,
    *,
    config: CalendarEventConfig | None = None,
) -> list[CalendarEvent]:
    """Build history calendar events for a Gregorian date range."""
    if config is None:
        config = CalendarEventConfig(
            display_language="en",
            day_boundary=DAY_BOUNDARY_MIDNIGHT,
            offset_days=0,
        )
    start_dt = dt.datetime.combine(start, dt.time())
    end_dt = dt.datetime.combine(end, dt.time())
    return build_history_calendar_events(hass, config, start_dt, end_dt)


def _history_event_on(
    events: list[CalendarEvent], day: dt.date, event_id: str
) -> CalendarEvent | None:
    """Return a history event on a Gregorian day."""
    uid = f"{DOMAIN}:history:{event_id}:{day.isoformat()}"
    return next((event for event in events if event.uid == uid), None)


async def test_battle_of_badr(hass, setup_integration) -> None:
    """Test Battle of Badr maps to 17 Ramadan."""
    badr_day = Hijri(1447, 9, 17).to_gregorian()
    day = dt.date(badr_day.year, badr_day.month, badr_day.day)
    events = _events_in_range(
        hass, day - dt.timedelta(days=1), day + dt.timedelta(days=1)
    )

    event = _history_event_on(events, day, "battle_of_badr")
    assert event is not None
    assert event.summary == "Battle of Badr"
    assert event.description is not None
    assert "2 AH" in event.description
    assert "britannica.com/event/Battle-of-Badr" in event.description


async def test_dual_events_on_15_rajab(hass, setup_integration) -> None:
    """Test Yarmouk and Jerusalem both appear on 15 Rajab."""
    rajab_day = Hijri(1447, 7, 15).to_gregorian()
    day = dt.date(rajab_day.year, rajab_day.month, rajab_day.day)
    events = _events_in_range(hass, day, day)

    yarmouk = _history_event_on(events, day, "battle_of_yarmouk")
    jerusalem = _history_event_on(events, day, "conquest_of_jerusalem")
    assert yarmouk is not None
    assert jerusalem is not None


async def test_history_arabic_reference(hass, setup_integration) -> None:
    """Test Arabic calendar language uses Arabic reference URLs."""
    await translation.async_get_translations(
        hass, "ar", "entity", integrations=[DOMAIN]
    )
    badr_day = Hijri(1447, 9, 17).to_gregorian()
    day = dt.date(badr_day.year, badr_day.month, badr_day.day)
    events = _events_in_range(
        hass,
        day,
        day,
        config=CalendarEventConfig(
            display_language="ar",
            day_boundary=DAY_BOUNDARY_MIDNIGHT,
            offset_days=0,
        ),
    )
    event = _history_event_on(events, day, "battle_of_badr")
    assert event is not None
    assert event.description is not None
    assert "ar.wikipedia.org/wiki" in event.description


async def test_history_entity_async_get_events(hass, setup_integration) -> None:
    """Test the history calendar entity returns events."""
    entity_id = _history_entity_id(hass, setup_integration.entry_id)
    entity = hass.data["entity_components"]["calendar"].get_entity(entity_id)
    assert entity is not None

    badr_day = Hijri(1447, 9, 17).to_gregorian()
    day = dt.date(badr_day.year, badr_day.month, badr_day.day)
    start = dt.datetime.combine(day, dt.time())
    end = dt.datetime.combine(day + dt.timedelta(days=1), dt.time())

    events = await entity.async_get_events(hass, start, end)
    summaries = {event.summary for event in events}
    assert "Battle of Badr" in summaries
