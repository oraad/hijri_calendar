"""Data update coordinator for Hijri calendar."""

from __future__ import annotations

import datetime as dt
import logging

import homeassistant.util.dt as dt_util
from homeassistant.const import CONF_LANGUAGE
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.helpers import event
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_DAY_BOUNDARY,
    CONF_OFFSET_DAYS,
    DAY_BOUNDARY_SUNSET,
    DEFAULT_DAY_BOUNDARY,
    DEFAULT_LANGUAGE,
    DEFAULT_OFFSET_DAYS,
    DOMAIN,
)
from .data import HijriCalendarConfigEntry, HijriCalendarData
from .helpers import (
    async_gregorian_to_hijri,
    async_resolve_effective_gregorian_date,
    next_sunset,
)
from .repairs import async_update_sunset_repairs

_LOGGER = logging.getLogger(__name__)


class HijriCalendarUpdateCoordinator(DataUpdateCoordinator[HijriCalendarData]):
    """Coordinator for Hijri calendar data."""

    config_entry: HijriCalendarConfigEntry
    _attr_should_poll = False

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: HijriCalendarConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(hass, _LOGGER, name=DOMAIN, config_entry=config_entry)
        self._unsub_sunset: CALLBACK_TYPE | None = None

    @property
    def language(self) -> str:
        """Return configured language."""
        return self.config_entry.data.get(CONF_LANGUAGE, DEFAULT_LANGUAGE)

    @property
    def day_boundary(self) -> str:
        """Return configured day boundary."""
        return self.config_entry.data.get(CONF_DAY_BOUNDARY, DEFAULT_DAY_BOUNDARY)

    @property
    def offset_days(self) -> int:
        """Return configured offset in days."""
        return int(self.config_entry.options.get(CONF_OFFSET_DAYS, DEFAULT_OFFSET_DAYS))

    async def _async_update_data(self) -> HijriCalendarData:
        """Compute Hijri date for the effective Gregorian day."""
        effective_gdate = await async_resolve_effective_gregorian_date(
            self.hass,
            self.day_boundary,
            self.offset_days,
        )
        hijri = await async_gregorian_to_hijri(self.hass, effective_gdate)

        next_midnight = dt_util.start_of_local_day() + dt.timedelta(days=1)
        _LOGGER.debug(
            "Updated Hijri date: %s (Gregorian %s), next refresh at %s",
            hijri.isoformat(),
            effective_gdate,
            next_midnight,
        )

        if self._unsub_refresh:
            self._unsub_refresh()
        self._unsub_refresh = event.async_track_point_in_time(
            self.hass, self._handle_scheduled_update, next_midnight
        )

        if self._unsub_sunset:
            self._unsub_sunset()
            self._unsub_sunset = None

        if self.day_boundary == DAY_BOUNDARY_SUNSET:
            sunset = next_sunset(self.hass)
            if sunset is not None and sunset < next_midnight:
                self._unsub_sunset = event.async_track_point_in_time(
                    self.hass, self._handle_scheduled_update, sunset
                )

        await async_update_sunset_repairs(self.hass, self.config_entry)

        return HijriCalendarData(
            language=self.language,
            day_boundary=self.day_boundary,
            offset_days=self.offset_days,
            gregorian_date=effective_gdate,
            hijri=hijri,
        )

    async def async_shutdown(self) -> None:
        """Cancel sunset timer before base shutdown clears midnight refresh."""
        if self._unsub_sunset:
            self._unsub_sunset()
            self._unsub_sunset = None
        await super().async_shutdown()

    @callback
    def _handle_scheduled_update(self, _now: dt.datetime) -> None:
        """Handle scheduled refresh at midnight or sunset."""
        self.hass.async_create_task(self.async_request_refresh())
