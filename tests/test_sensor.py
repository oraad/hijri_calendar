"""Test Hijri calendar sensor entities."""

from __future__ import annotations

import datetime as dt

from hijridate import Hijri
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import ATTR_DEVICE_CLASS
from homeassistant.helpers import entity_registry as er

from custom_components.hijri_calendar.const import DAY_BOUNDARY_MIDNIGHT, DOMAIN
from custom_components.hijri_calendar.data import HijriCalendarData
from custom_components.hijri_calendar.holidays import (
    ALL_HOLIDAY_IDS,
    HOLIDAY_NONE,
    HOLIDAY_RAMADAN,
)
from custom_components.hijri_calendar.sensor import INFO_SENSORS


def _entity_id(hass, entry_id: str, key: str) -> str:
    """Return entity_id for a sensor key."""
    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id("sensor", DOMAIN, f"{entry_id}-{key}")
    assert entity_id is not None
    return entity_id


def test_sensor_description_device_classes() -> None:
    """Test sensor descriptions declare device and state classes."""
    descriptions = {description.key: description for description in INFO_SENSORS}
    assert descriptions["date"].device_class == SensorDeviceClass.DATE
    assert descriptions["holiday"].device_class == SensorDeviceClass.ENUM
    assert descriptions["days_in_month"].state_class == SensorStateClass.MEASUREMENT
    assert descriptions["days_in_year"].state_class == SensorStateClass.MEASUREMENT


async def test_sensor_device_classes(hass, setup_integration) -> None:
    """Test enabled sensors expose the correct device classes in state."""
    entry_id = setup_integration.entry_id

    hijri_date = hass.states.get(_entity_id(hass, entry_id, "date"))
    assert hijri_date is not None
    assert hijri_date.attributes[ATTR_DEVICE_CLASS] == SensorDeviceClass.DATE
    assert hijri_date.state not in ("unknown", "unavailable")

    holiday = hass.states.get(_entity_id(hass, entry_id, "holiday"))
    assert holiday is not None
    assert holiday.attributes[ATTR_DEVICE_CLASS] == SensorDeviceClass.ENUM


async def test_holiday_sensor_enum_options(hass, setup_integration) -> None:
    """Test holiday sensor options match all holiday ids."""
    state = hass.states.get(_entity_id(hass, setup_integration.entry_id, "holiday"))
    assert state is not None
    assert set(state.attributes["options"]) == set(ALL_HOLIDAY_IDS)


async def _set_coordinator_data(hass, setup_integration, hijri: Hijri) -> None:
    """Push coordinator data and refresh entities."""
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


async def test_holiday_sensor_state_is_primary_id(hass, setup_integration) -> None:
    """Test holiday state uses the first holiday id during Ramadan."""
    await _set_coordinator_data(hass, setup_integration, Hijri(1445, 9, 15))

    state = hass.states.get(_entity_id(hass, setup_integration.entry_id, "holiday"))
    assert state is not None
    assert state.state == HOLIDAY_RAMADAN
    assert HOLIDAY_RAMADAN in state.attributes["ids"]
    assert state.attributes["names"]


async def test_holiday_sensor_none_state(hass, setup_integration) -> None:
    """Test holiday state is none when no holiday is active."""
    await _set_coordinator_data(hass, setup_integration, Hijri(1446, 2, 15))

    state = hass.states.get(_entity_id(hass, setup_integration.entry_id, "holiday"))
    assert state is not None
    assert state.state == HOLIDAY_NONE


async def test_hijri_date_attributes(hass, setup_integration) -> None:
    """Test Hijri date sensor exposes formatted attributes."""
    state = hass.states.get(_entity_id(hass, setup_integration.entry_id, "date"))
    assert state is not None
    assert "formatted" in state.attributes
    assert "gregorian_date" in state.attributes
    assert "hijri_year" in state.attributes
