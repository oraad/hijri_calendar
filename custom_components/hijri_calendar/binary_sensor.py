"""Binary sensor platform for hijri_calendar."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .data import HijriCalendarConfigEntry, HijriCalendarData
from .entity import HijriCalendarSunsetEntity
from .holidays import (
    EVENT_EID_AL_ADHA,
    EVENT_EID_AL_FITR,
    EVENT_HAJJ_SEASON,
    EVENT_RAMADAN,
    get_active_events,
)

PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class HijriCalendarBinarySensorDescription(BinarySensorEntityDescription):
    """Description for a Hijri calendar binary sensor."""

    is_on_fn: Callable[[HijriCalendarData], bool]


BINARY_SENSORS: tuple[HijriCalendarBinarySensorDescription, ...] = (
    HijriCalendarBinarySensorDescription(
        key="ramadan",
        translation_key="ramadan",
        icon="mdi:moon-waning-crescent",
        is_on_fn=lambda data: EVENT_RAMADAN in _active_events(data),
    ),
    HijriCalendarBinarySensorDescription(
        key="eid_al_fitr",
        translation_key="eid_al_fitr",
        icon="mdi:star-crescent",
        is_on_fn=lambda data: EVENT_EID_AL_FITR in _active_events(data),
    ),
    HijriCalendarBinarySensorDescription(
        key="eid_al_adha",
        translation_key="eid_al_adha",
        icon="mdi:star-crescent",
        is_on_fn=lambda data: EVENT_EID_AL_ADHA in _active_events(data),
    ),
    HijriCalendarBinarySensorDescription(
        key="hajj_season",
        translation_key="hajj_season",
        icon="mdi:kaaba",
        is_on_fn=lambda data: EVENT_HAJJ_SEASON in _active_events(data),
    ),
)


def _active_events(data: HijriCalendarData) -> set[str]:
    return get_active_events(data.hijri)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: HijriCalendarConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Hijri calendar binary sensors."""
    async_add_entities(
        HijriCalendarBinarySensor(config_entry, description)
        for description in BINARY_SENSORS
    )


class HijriCalendarBinarySensor(HijriCalendarSunsetEntity, BinarySensorEntity):
    """Representation of a Hijri calendar binary sensor."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    entity_description: HijriCalendarBinarySensorDescription

    @property
    def is_on(self) -> bool:
        """Return true if the event is active."""
        return self.entity_description.is_on_fn(self.coordinator.data)
