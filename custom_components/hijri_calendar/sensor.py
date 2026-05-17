"""Sensor platform for hijri_calendar."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .data import HijriCalendarConfigEntry, HijriCalendarData
from .entity import HijriCalendarSunsetEntity
from .holidays import get_holidays

PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class HijriCalendarSensorDescription(SensorEntityDescription):
    """Description for a Hijri calendar sensor."""

    value_fn: Callable[[HijriCalendarData], str | int]
    attr_fn: Callable[[HijriCalendarData], dict[str, str | int]] | None = None


INFO_SENSORS: tuple[HijriCalendarSensorDescription, ...] = (
    HijriCalendarSensorDescription(
        key="date",
        translation_key="hijri_date",
        icon="mdi:calendar-star",
        value_fn=lambda data: data.hijri.isoformat(),
        attr_fn=lambda data: {
            "hijri_year": data.hijri.year,
            "hijri_month": data.hijri.month,
            "hijri_day": data.hijri.day,
            "month_name": data.hijri.month_name(data.language),
            "day_name": data.hijri.day_name(data.language),
            "gregorian_date": data.gregorian_date.isoformat(),
        },
    ),
    HijriCalendarSensorDescription(
        key="holiday",
        translation_key="holiday",
        icon="mdi:star-crescent",
        value_fn=lambda data: ", ".join(
            holiday.id for holiday in get_holidays(data.hijri)
        )
        or "none",
        attr_fn=lambda data: {
            "ids": ", ".join(holiday.id for holiday in get_holidays(data.hijri)),
            "types": ", ".join(
                dict.fromkeys(holiday.type for holiday in get_holidays(data.hijri))
            ),
        },
    ),
    HijriCalendarSensorDescription(
        key="days_in_month",
        translation_key="days_in_month",
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.hijri.month_length(),
    ),
    HijriCalendarSensorDescription(
        key="days_in_year",
        translation_key="days_in_year",
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.hijri.year_length(),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: HijriCalendarConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Hijri calendar sensors."""
    async_add_entities(
        HijriCalendarSensor(config_entry, description) for description in INFO_SENSORS
    )


class HijriCalendarSensor(HijriCalendarSunsetEntity, SensorEntity):
    """Representation of a Hijri calendar sensor."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    entity_description: HijriCalendarSensorDescription

    @property
    def native_value(self) -> str | int:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, str | int]:
        """Return state attributes."""
        if self.entity_description.attr_fn is None:
            return {}
        return self.entity_description.attr_fn(self.coordinator.data)
