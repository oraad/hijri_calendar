"""Test Hijri month-starts calendar events."""

from __future__ import annotations

import datetime as dt

from hijridate import Hijri
from homeassistant.components.calendar import CalendarEvent
from homeassistant.helpers import entity_registry as er

from custom_components.hijri_calendar.calendar_common import CalendarEventConfig
from custom_components.hijri_calendar.const import (
    CONF_HIJRI_MONTH_STARTS_CALENDAR_LANGUAGE,
    DAY_BOUNDARY_MIDNIGHT,
    DOMAIN,
)
from custom_components.hijri_calendar.month_start_calendar_events import (
    build_month_start_calendar_events,
)


def _month_starts_entity_id(hass, entry_id: str) -> str:
    """Return entity_id for the Hijri month-starts calendar."""
    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id(
        "calendar", DOMAIN, f"{entry_id}-hijri_month_starts"
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
    """Build month-start calendar events for a Gregorian date range."""
    if config is None:
        config = CalendarEventConfig(
            display_language="en",
            day_boundary=DAY_BOUNDARY_MIDNIGHT,
            offset_days=0,
        )
    start_dt = dt.datetime.combine(start, dt.time())
    end_dt = dt.datetime.combine(end, dt.time())
    return build_month_start_calendar_events(hass, config, start_dt, end_dt)


def _month_start_on(
    events: list[CalendarEvent], day: dt.date, month: int
) -> CalendarEvent | None:
    """Return a month-start event on a Gregorian day."""
    uid = f"{DOMAIN}:month_start:{month}:{day.isoformat()}"
    return next((event for event in events if event.uid == uid), None)


async def test_ramadan_month_start(hass, setup_integration) -> None:
    """Test 1 Ramadan produces a month-start event."""
    ramadan_day = Hijri(1447, 9, 1).to_gregorian()
    day = dt.date(ramadan_day.year, ramadan_day.month, ramadan_day.day)
    events = _events_in_range(
        hass, day - dt.timedelta(days=1), day + dt.timedelta(days=1)
    )

    event = _month_start_on(events, day, 9)
    assert event is not None
    assert event.summary == "Start of Ramadan"
    assert event.description is not None
    assert "1447 AH" in event.description
    assert "britannica.com/topic/Islamic-calendar" in event.description


async def test_twelve_month_starts_in_hijri_year(hass, setup_integration) -> None:
    """Test a Hijri year yields exactly 12 month-start events."""
    start = Hijri(1447, 1, 1).to_gregorian()
    end = Hijri(1448, 1, 1).to_gregorian()
    start_date = dt.date(start.year, start.month, start.day)
    end_date = dt.date(end.year, end.month, end.day) - dt.timedelta(days=1)
    events = _events_in_range(hass, start_date, end_date)

    assert len(events) == 12
    months = {int(event.uid.split(":")[2]) for event in events}
    assert months == set(range(1, 13))


async def test_month_start_arabic(hass, setup_integration) -> None:
    """Test Arabic calendar language uses Arabic month names."""
    ramadan_day = Hijri(1447, 9, 1).to_gregorian()
    day = dt.date(ramadan_day.year, ramadan_day.month, ramadan_day.day)
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
    event = _month_start_on(events, day, 9)
    assert event is not None
    assert "رمضان" in event.summary


async def test_month_start_turkish(hass, setup_integration) -> None:
    """Test Turkish calendar language uses Turkish month names."""
    ramadan_day = Hijri(1447, 9, 1).to_gregorian()
    day = dt.date(ramadan_day.year, ramadan_day.month, ramadan_day.day)
    events = _events_in_range(
        hass,
        day,
        day,
        config=CalendarEventConfig(
            display_language="tr",
            day_boundary=DAY_BOUNDARY_MIDNIGHT,
            offset_days=0,
        ),
    )
    event = _month_start_on(events, day, 9)
    assert event is not None
    assert "Ramazan" in event.summary


async def test_month_start_german_template(hass, setup_integration) -> None:
    """Test German uses German template text with English hijridate month names."""
    ramadan_day = Hijri(1447, 9, 1).to_gregorian()
    day = dt.date(ramadan_day.year, ramadan_day.month, ramadan_day.day)
    events = _events_in_range(
        hass,
        day,
        day,
        config=CalendarEventConfig(
            display_language="de",
            day_boundary=DAY_BOUNDARY_MIDNIGHT,
            offset_days=0,
        ),
    )
    event = _month_start_on(events, day, 9)
    assert event is not None
    assert event.summary == "Beginn von Ramadan"
    assert event.description is not None
    assert "Hijri-Kalender" in event.description
    assert "de.wikipedia.org" in event.description


async def test_month_start_entity_async_get_events(hass, setup_integration) -> None:
    """Test the month-starts calendar entity returns events."""
    entity_id = _month_starts_entity_id(hass, setup_integration.entry_id)
    entity = hass.data["entity_components"]["calendar"].get_entity(entity_id)
    assert entity is not None

    muharram_day = Hijri(1447, 1, 1).to_gregorian()
    day = dt.date(muharram_day.year, muharram_day.month, muharram_day.day)
    start = dt.datetime.combine(day, dt.time())
    end = dt.datetime.combine(day + dt.timedelta(days=1), dt.time())

    events = await entity.async_get_events(hass, start, end)
    summaries = {event.summary for event in events}
    assert "Start of Muharram" in summaries


async def test_month_start_offset(hass, setup_integration) -> None:
    """Test a positive day offset shifts month-start events one day earlier."""
    ramadan_day = Hijri(1447, 9, 1).to_gregorian()
    day = dt.date(ramadan_day.year, ramadan_day.month, ramadan_day.day)
    shifted = day - dt.timedelta(days=1)

    base_events = _events_in_range(hass, day, day)
    offset_events = _events_in_range(
        hass,
        shifted,
        shifted,
        config=CalendarEventConfig(
            display_language="en",
            day_boundary=DAY_BOUNDARY_MIDNIGHT,
            offset_days=1,
        ),
    )

    assert _month_start_on(base_events, day, 9) is not None
    assert _month_start_on(offset_events, shifted, 9) is not None
    assert _month_start_on(base_events, shifted, 9) is None


async def test_month_starts_coordinator_language(hass) -> None:
    """Test month-starts calendar language options resolve on the coordinator."""
    from homeassistant.config_entries import ConfigEntryState
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    mock_config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={"language": "en", "day_boundary": DAY_BOUNDARY_MIDNIGHT},
        options={
            CONF_HIJRI_MONTH_STARTS_CALENDAR_LANGUAGE: "tr",
        },
        version=2,
        unique_id=f"{DOMAIN}-month-starts-lang",
    )
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.LOADED

    coordinator = mock_config_entry.runtime_data
    assert coordinator.month_starts_display_language == "tr"

    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()
