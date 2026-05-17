"""Entity base class for Hijri Calendar."""

from __future__ import annotations

import datetime as dt
from abc import abstractmethod

from homeassistant.core import CALLBACK_TYPE, callback
from homeassistant.helpers import event
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import ATTRIBUTION, DAY_BOUNDARY_SUNSET, DOMAIN
from .coordinator import HijriCalendarUpdateCoordinator
from .data import HijriCalendarConfigEntry
from .helpers import next_sunset


class HijriCalendarEntity(CoordinatorEntity[HijriCalendarUpdateCoordinator]):
    """Base entity for Hijri Calendar."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _attr_should_poll = False
    _update_unsub: CALLBACK_TYPE | None = None

    def __init__(
        self,
        config_entry: HijriCalendarConfigEntry,
        description: EntityDescription,
    ) -> None:
        """Initialize a Hijri Calendar entity."""
        super().__init__(config_entry.runtime_data)
        self.entity_description = description
        self._attr_unique_id = f"{config_entry.entry_id}-{description.key}"
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, config_entry.entry_id)},
        )

    async def async_added_to_hass(self) -> None:
        """Schedule entity updates when added."""
        await super().async_added_to_hass()
        self._schedule_update()

    async def async_will_remove_from_hass(self) -> None:
        """Cancel scheduled updates when removed."""
        if self._update_unsub:
            self._update_unsub()
            self._update_unsub = None
        await super().async_will_remove_from_hass()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Reschedule updates when coordinator data changes."""
        self._schedule_update()
        super()._handle_coordinator_update()

    @abstractmethod
    def _update_times(self) -> list[dt.datetime | None]:
        """Return datetimes when this entity should refresh."""

    def _schedule_update(self) -> None:
        """Schedule the next entity-specific update."""
        now = dt_util.now()
        update = dt_util.start_of_local_day() + dt.timedelta(days=1)

        for update_time in self._update_times():
            if update_time is not None and now < update_time < update:
                update = update_time

        if self._update_unsub:
            self._update_unsub()

        self._update_unsub = event.async_track_point_in_time(
            self.hass, self._update, update
        )

    @callback
    def _update(self, _now: dt.datetime | None = None) -> None:
        """Refresh entity state."""
        self._update_unsub = None
        self._schedule_update()
        self.async_write_ha_state()


class HijriCalendarSunsetEntity(HijriCalendarEntity):
    """Entity that refreshes at sunset when that boundary is configured."""

    def _update_times(self) -> list[dt.datetime | None]:
        """Return sunset as update time when sunset boundary is active."""
        if self.coordinator.day_boundary != DAY_BOUNDARY_SUNSET:
            return []
        return [next_sunset(self.hass)]
