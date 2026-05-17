"""Test Hijri calendar events."""

from __future__ import annotations

import datetime as dt

from hijridate import Hijri
from homeassistant.components.calendar import CalendarEvent
from homeassistant.const import CONF_LANGUAGE
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.hijri_calendar.calendar_events import (
    SPAN_RAMADAN,
    CalendarEventConfig,
    build_calendar_events,
)
from custom_components.hijri_calendar.const import (
    CONF_DAY_BOUNDARY,
    CONF_OFFSET_DAYS,
    DAY_BOUNDARY_MIDNIGHT,
    DOMAIN,
)
from custom_components.hijri_calendar.holidays import HOLIDAY_EID_AL_FITR


def _calendar_entity_id(hass, entry_id: str) -> str:
    """Return entity_id for the hijri events calendar."""
    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id(
        "calendar", DOMAIN, f"{entry_id}-hijri_events"
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
    """Build calendar events for a Gregorian date range."""
    if config is None:
        config = CalendarEventConfig(
            language="en",
            day_boundary=DAY_BOUNDARY_MIDNIGHT,
            offset_days=0,
        )
    start_dt = dt.datetime.combine(start, dt.time())
    end_dt = dt.datetime.combine(end, dt.time())
    return build_calendar_events(hass, config, start_dt, end_dt)


def _point_event_on(
    events: list[CalendarEvent], day: dt.date, holiday_id: str
) -> CalendarEvent | None:
    """Return the point event for a holiday on a Gregorian day, if any."""
    uid = f"{DOMAIN}:{holiday_id}:{day.isoformat()}"
    return next((event for event in events if event.uid == uid), None)


def _span_events(events: list[CalendarEvent], span_key: str) -> list[CalendarEvent]:
    """Return merged span events for a span key."""
    prefix = f"{DOMAIN}:span:{span_key}:"
    return [event for event in events if event.uid.startswith(prefix)]


def test_eid_gregorian_date() -> None:
    """Sanity-check hijridate mapping for Eid al-Fitr 1447."""
    gregorian = Hijri(1447, 10, 1).to_gregorian()
    assert gregorian.year >= 2025


async def test_ramadan_span(hass, setup_integration) -> None:
    """Test Ramadan produces a merged span event in a week of month 9."""
    ramadan_start = Hijri(1447, 9, 1).to_gregorian()
    start = dt.date(ramadan_start.year, ramadan_start.month, ramadan_start.day)
    end = start + dt.timedelta(days=6)
    events = _events_in_range(hass, start, end)

    spans = _span_events(events, SPAN_RAMADAN)
    assert spans
    assert spans[0].start == start
    assert "Ramadan" in spans[0].summary
    assert "1447 AH" in spans[0].summary


async def test_eid_al_fitr_point_event(hass, setup_integration) -> None:
    """Test 1 Shawwal maps to an Eid al-Fitr all-day event."""
    eid_day = Hijri(1447, 10, 1).to_gregorian()
    day = dt.date(eid_day.year, eid_day.month, eid_day.day)
    window_start = day - dt.timedelta(days=3)
    window_end = day + dt.timedelta(days=3)
    events = _events_in_range(hass, window_start, window_end)

    event = _point_event_on(events, day, HOLIDAY_EID_AL_FITR)
    assert event is not None
    assert event.summary == "Eid al-Fitr"
    assert event.end == day + dt.timedelta(days=1)


async def test_offset_shifts_events(hass, setup_integration) -> None:
    """Test a positive day offset shifts observances on the Gregorian calendar."""
    eid_day = Hijri(1447, 10, 1).to_gregorian()
    day = dt.date(eid_day.year, eid_day.month, eid_day.day)
    window_start = day - dt.timedelta(days=5)
    window_end = day + dt.timedelta(days=5)

    events_offset_0 = _events_in_range(hass, window_start, window_end)
    events_offset_1 = _events_in_range(
        hass,
        window_start,
        window_end,
        config=CalendarEventConfig(
            language="en",
            day_boundary=DAY_BOUNDARY_MIDNIGHT,
            offset_days=1,
        ),
    )

    eid_0 = _point_event_on(events_offset_0, day, HOLIDAY_EID_AL_FITR)
    assert eid_0 is not None

    shifted_day = day - dt.timedelta(days=1)
    eid_1 = _point_event_on(events_offset_1, shifted_day, HOLIDAY_EID_AL_FITR)
    assert eid_1 is not None
    assert _point_event_on(events_offset_1, day, HOLIDAY_EID_AL_FITR) is None


async def test_calendar_entity_async_get_events(hass, setup_integration) -> None:
    """Test the calendar entity returns events via async_get_events."""
    entity_id = _calendar_entity_id(hass, setup_integration.entry_id)
    entity = hass.data["entity_components"]["calendar"].get_entity(entity_id)
    assert entity is not None

    eid_day = Hijri(1447, 10, 1).to_gregorian()
    day = dt.date(eid_day.year, eid_day.month, eid_day.day)
    start = dt.datetime.combine(day - dt.timedelta(days=1), dt.time())
    end = dt.datetime.combine(day + dt.timedelta(days=1), dt.time())

    events = await entity.async_get_events(hass, start, end)
    summaries = {event.summary for event in events}
    assert "Eid al-Fitr" in summaries


async def test_offset_via_config_entry(hass) -> None:
    """Test configured offset shifts calendar events when offset is set in options."""
    mock_config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_LANGUAGE: "en", CONF_DAY_BOUNDARY: DAY_BOUNDARY_MIDNIGHT},
        options={CONF_OFFSET_DAYS: 1},
        unique_id=f"{DOMAIN}-offset",
    )
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    eid_day = Hijri(1447, 10, 1).to_gregorian()
    day = dt.date(eid_day.year, eid_day.month, eid_day.day)
    shifted = day - dt.timedelta(days=1)
    coordinator = mock_config_entry.runtime_data
    events = _events_in_range(
        hass,
        shifted - dt.timedelta(days=1),
        shifted + dt.timedelta(days=1),
        config=CalendarEventConfig(
            language=coordinator.language,  # type: ignore[arg-type]
            day_boundary=coordinator.day_boundary,
            offset_days=coordinator.offset_days,
        ),
    )
    assert _point_event_on(events, shifted, HOLIDAY_EID_AL_FITR) is not None

    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()
