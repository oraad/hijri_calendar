"""Sensor platform for hijri_calendar."""

from __future__ import annotations

import datetime as dt

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import HijriLanguage
from .data import HijriCalendarConfigEntry, HijriCalendarData
from .entity import HijriCalendarSunsetEntity
from .holidays import (
    ALL_HOLIDAY_IDS,
    HOLIDAY_NONE,
    days_until_eid_al_fitr,
    days_until_ramadan,
    get_holidays,
)
from .locale import (
    format_hijri_display,
    holiday_display_name,
    holiday_type_display_name,
)

PARALLEL_UPDATES = 0

HOLIDAY_SENSOR_OPTIONS: tuple[str, ...] = tuple(sorted(ALL_HOLIDAY_IDS))


INFO_SENSORS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="date",
        translation_key="hijri_date",
        icon="mdi:calendar-star",
        device_class=SensorDeviceClass.DATE,
    ),
    SensorEntityDescription(
        key="holiday",
        translation_key="holiday",
        icon="mdi:star-crescent",
        device_class=SensorDeviceClass.ENUM,
        options=HOLIDAY_SENSOR_OPTIONS,
    ),
    SensorEntityDescription(
        key="days_in_month",
        translation_key="days_in_month",
        entity_registry_enabled_default=False,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="days_in_year",
        translation_key="days_in_year",
        entity_registry_enabled_default=False,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="days_until_ramadan",
        translation_key="days_until_ramadan",
        icon="mdi:calendar-clock",
        entity_registry_enabled_default=False,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="days_until_eid_al_fitr",
        translation_key="days_until_eid_al_fitr",
        icon="mdi:calendar-clock",
        entity_registry_enabled_default=False,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)


def _native_value(data: HijriCalendarData, key: str) -> dt.date | str | int:
    """Return native state for a sensor key."""
    if key == "date":
        return dt.date(data.hijri.year, data.hijri.month, data.hijri.day)
    if key == "holiday":
        holidays = get_holidays(data.hijri)
        return HOLIDAY_NONE if not holidays else holidays[0].id
    if key == "days_in_month":
        return data.hijri.month_length()
    if key == "days_in_year":
        return data.hijri.year_length()
    if key in ("days_until_ramadan", "days_until_eid_al_fitr"):
        counter = (
            days_until_ramadan
            if key == "days_until_ramadan"
            else days_until_eid_al_fitr
        )
        count = counter(data.hijri)
        return count if count is not None else 0
    msg = f"Unknown sensor key: {key}"
    raise ValueError(msg)


def _date_attributes(data: HijriCalendarData) -> dict[str, str | int]:
    """Return extra state attributes for the Hijri date sensor."""
    return {
        "hijri_year": data.hijri.year,
        "hijri_month": data.hijri.month,
        "hijri_day": data.hijri.day,
        "month_name": data.hijri.month_name(data.language),
        "day_name": data.hijri.day_name(data.language),
        "gregorian_date": data.gregorian_date.isoformat(),
        "formatted": format_hijri_display(
            data.hijri, data.language, eastern_digits=False
        ),
        "formatted_eastern": format_hijri_display(
            data.hijri, data.language, eastern_digits=True
        ),
    }


def _holiday_attributes(
    hass: HomeAssistant, data: HijriCalendarData
) -> dict[str, str | int]:
    """Return extra state attributes for the holiday sensor."""
    language: HijriLanguage = data.language  # type: ignore[assignment]
    holidays = get_holidays(data.hijri)
    if not holidays:
        names = holiday_display_name(hass, HOLIDAY_NONE, language)
    else:
        names = ", ".join(
            holiday_display_name(hass, holiday.id, language) for holiday in holidays
        )
    return {
        "ids": ", ".join(holiday.id for holiday in holidays),
        "names": names,
        "types": ", ".join(
            holiday_type_display_name(hass, holiday_type, language)
            for holiday_type in dict.fromkeys(holiday.type for holiday in holidays)
        ),
    }


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

    _attr_entity_category = None
    entity_description: SensorEntityDescription

    @property
    def native_value(self) -> dt.date | str | int:
        """Return the state of the sensor."""
        return _native_value(self.coordinator.data, self.entity_description.key)

    @property
    def extra_state_attributes(self) -> dict[str, str | int] | None:
        """Return extra state attributes."""
        key = self.entity_description.key
        data = self.coordinator.data
        if key == "date":
            return _date_attributes(data)
        if key == "holiday":
            return _holiday_attributes(self.hass, data)
        return None
