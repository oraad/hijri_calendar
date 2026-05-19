"""Test Hijri calendar binary sensor entities."""

from __future__ import annotations

import datetime as dt

from hijridate import Hijri
from homeassistant.helpers import entity_registry as er

from custom_components.hijri_calendar.const import DAY_BOUNDARY_MIDNIGHT, DOMAIN
from custom_components.hijri_calendar.data import HijriCalendarData
from custom_components.hijri_calendar.holidays import (
    EVENT_EID_AL_ADHA,
    EVENT_EID_AL_FITR,
    EVENT_HAJJ_SEASON,
    EVENT_RAMADAN,
)


def _binary_entity_id(hass, entry_id: str, key: str) -> str:
    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id(
        "binary_sensor", DOMAIN, f"{entry_id}-{key}"
    )
    assert entity_id is not None
    return entity_id


async def _set_coordinator_data(hass, setup_integration, hijri: Hijri) -> None:
    coordinator = setup_integration.runtime_data
    gregorian = hijri.to_gregorian()
    coordinator.async_set_updated_data(
        HijriCalendarData(
            language="en",
            day_boundary=DAY_BOUNDARY_MIDNIGHT,
            offset_days=0,
            gregorian_date=dt.date(gregorian.year, gregorian.month, gregorian.day),
            hijri=hijri,
        )
    )
    await hass.async_block_till_done()


async def test_ramadan_binary_sensor(hass, setup_integration) -> None:
    """Test Ramadan binary sensor is on during Ramadan."""
    await _set_coordinator_data(hass, setup_integration, Hijri(1445, 9, 15))
    state = hass.states.get(
        _binary_entity_id(hass, setup_integration.entry_id, "ramadan")
    )
    assert state is not None
    assert state.state == "on"

    await _set_coordinator_data(hass, setup_integration, Hijri(1446, 2, 15))
    state = hass.states.get(
        _binary_entity_id(hass, setup_integration.entry_id, "ramadan")
    )
    assert state is not None
    assert state.state == "off"


async def test_eid_al_fitr_binary_sensor(hass, setup_integration) -> None:
    """Test Eid al-Fitr binary sensor on 1 Shawwal."""
    await _set_coordinator_data(hass, setup_integration, Hijri(1445, 10, 1))
    state = hass.states.get(
        _binary_entity_id(hass, setup_integration.entry_id, "eid_al_fitr")
    )
    assert state is not None
    assert state.state == "on"


async def test_eid_al_adha_binary_sensor(hass, setup_integration) -> None:
    """Test Eid al-Adha binary sensor on 10 Dhul Hijjah."""
    await _set_coordinator_data(hass, setup_integration, Hijri(1445, 12, 10))
    state = hass.states.get(
        _binary_entity_id(hass, setup_integration.entry_id, "eid_al_adha")
    )
    assert state is not None
    assert state.state == "on"


async def test_hajj_season_binary_sensor(hass, setup_integration) -> None:
    """Test Hajj season binary sensor during days 8-13."""
    await _set_coordinator_data(hass, setup_integration, Hijri(1445, 12, 9))
    state = hass.states.get(
        _binary_entity_id(hass, setup_integration.entry_id, "hajj_season")
    )
    assert state is not None
    assert state.state == "on"


async def test_active_events_keys(hass, setup_integration) -> None:
    """Test expected event keys for a Hajj day."""
    from custom_components.hijri_calendar.holidays import get_active_events

    events = get_active_events(Hijri(1445, 12, 10))
    assert EVENT_RAMADAN not in events
    assert EVENT_EID_AL_FITR not in events
    assert EVENT_EID_AL_ADHA in events
    assert EVENT_HAJJ_SEASON in events
