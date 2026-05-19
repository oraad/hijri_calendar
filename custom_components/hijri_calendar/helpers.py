"""Helper functions for hijridate conversion and date boundaries."""

from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING

from hijridate import Gregorian, Hijri
from homeassistant.const import SUN_EVENT_SUNSET
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.sun import get_astral_event_date
from homeassistant.util import dt as dt_util

from .const import (
    DAY_BOUNDARY_MIDNIGHT,
    DAY_BOUNDARY_SUNSET,
    DOMAIN,
    HijriLanguage,
)
from .locale import format_hijri_display

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


def gregorian_to_hijri(gregorian_date: dt.date) -> Hijri:
    """Convert a Gregorian date to Hijri."""
    try:
        return Gregorian.fromdate(gregorian_date).to_hijri()
    except (OverflowError, ValueError) as err:
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key="date_out_of_range",
        ) from err


def hijri_to_gregorian(hijri: Hijri) -> Gregorian:
    """Convert a Hijri date to Gregorian."""
    try:
        return hijri.to_gregorian()
    except (OverflowError, ValueError) as err:
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key="date_out_of_range",
        ) from err


def parse_hijri_date(date_string: str) -> Hijri:
    """Parse an ISO Hijri date string."""
    try:
        return Hijri.fromisoformat(date_string)
    except (OverflowError, ValueError) as err:
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key="date_out_of_range",
        ) from err


async def async_gregorian_to_hijri(
    hass: HomeAssistant, gregorian_date: dt.date
) -> Hijri:
    """Convert a Gregorian date to Hijri without blocking the event loop."""
    return await hass.async_add_executor_job(gregorian_to_hijri, gregorian_date)


async def async_hijri_to_gregorian(hass: HomeAssistant, hijri: Hijri) -> Gregorian:
    """Convert a Hijri date to Gregorian without blocking the event loop."""
    return await hass.async_add_executor_job(hijri_to_gregorian, hijri)


async def async_parse_hijri_date(hass: HomeAssistant, date_string: str) -> Hijri:
    """Parse an ISO Hijri date string without blocking the event loop."""
    return await hass.async_add_executor_job(parse_hijri_date, date_string)


async def async_resolve_effective_gregorian_date(
    hass: HomeAssistant,
    day_boundary: str,
    offset_days: int,
    *,
    reference: dt.datetime | None = None,
) -> dt.date:
    """Resolve effective Gregorian date without blocking the event loop."""
    return await hass.async_add_executor_job(
        resolve_effective_gregorian_date,
        hass,
        day_boundary,
        offset_days,
        reference=reference,
    )


def format_hijri_dict(hijri: Hijri, language: HijriLanguage) -> dict[str, str | int]:
    """Return a dictionary of formatted Hijri date fields."""
    return {
        "hijri": hijri.isoformat(),
        "year": hijri.year,
        "month": hijri.month,
        "day": hijri.day,
        "month_name": hijri.month_name(language),
        "day_name": hijri.day_name(language),
        "notation": Hijri.notation(language),
        "formatted": format_hijri_display(hijri, language, eastern_digits=False),
        "formatted_eastern": format_hijri_display(hijri, language, eastern_digits=True),
    }


def format_gregorian_dict(
    gregorian: Gregorian, language: HijriLanguage
) -> dict[str, str | int]:
    """Return a dictionary of formatted Gregorian date fields."""
    return {
        "gregorian": gregorian.isoformat(),
        "year": gregorian.year,
        "month": gregorian.month,
        "day": gregorian.day,
        "month_name": gregorian.month_name(language),
        "day_name": gregorian.day_name(language),
        "notation": Gregorian.notation(language),
    }


def is_after_sunset(hass: HomeAssistant, on_date: dt.date | None = None) -> bool:
    """Return True if the current local time is after sunset."""
    today = on_date or dt_util.now().date()
    event_date = get_astral_event_date(hass, SUN_EVENT_SUNSET, today)
    if event_date is None:
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key="sunset_unavailable",
        )
    sunset = dt_util.as_local(event_date)
    return dt_util.now() > sunset


def gregorian_to_date(gregorian: Gregorian) -> dt.date:
    """Return a datetime.date from a hijridate Gregorian instance."""
    return dt.date(gregorian.year, gregorian.month, gregorian.day)


def compute_offset_for_hijri_today(
    hass: HomeAssistant,
    day_boundary: str,
    target_hijri: Hijri,
    *,
    reference: dt.datetime | None = None,
) -> int:
    """Return the day offset so today (per boundary) shows the target Hijri date."""
    base = resolve_effective_gregorian_date(
        hass, day_boundary, offset_days=0, reference=reference
    )
    target_gregorian = gregorian_to_date(hijri_to_gregorian(target_hijri))
    return (target_gregorian - base).days


async def async_compute_offset_for_hijri_today(
    hass: HomeAssistant,
    day_boundary: str,
    target_hijri: Hijri,
    *,
    reference: dt.datetime | None = None,
) -> int:
    """Compute offset for target Hijri today without blocking the event loop."""
    return await hass.async_add_executor_job(
        compute_offset_for_hijri_today,
        hass,
        day_boundary,
        target_hijri,
        reference=reference,
    )


def resolve_effective_gregorian_date(
    hass: HomeAssistant,
    day_boundary: str,
    offset_days: int,
    *,
    reference: dt.datetime | None = None,
) -> dt.date:
    """Resolve the effective Gregorian date for Hijri conversion."""
    now = reference or dt_util.now()
    base_date = now.date()

    if day_boundary == DAY_BOUNDARY_SUNSET:
        if is_after_sunset(hass, base_date):
            base_date += dt.timedelta(days=1)
    elif day_boundary != DAY_BOUNDARY_MIDNIGHT:
        msg = f"Unknown day boundary: {day_boundary}"
        raise ValueError(msg)

    if offset_days:
        base_date += dt.timedelta(days=offset_days)

    return base_date


def next_sunset(hass: HomeAssistant) -> dt.datetime | None:
    """Return the next sunset datetime in local time."""
    today = dt_util.now().date()
    event_date = get_astral_event_date(hass, SUN_EVENT_SUNSET, today)
    if event_date is None:
        return None
    sunset = dt_util.as_local(event_date)
    if dt_util.now() >= sunset:
        tomorrow = today + dt.timedelta(days=1)
        event_date = get_astral_event_date(hass, SUN_EVENT_SUNSET, tomorrow)
        if event_date is None:
            return None
        return dt_util.as_local(event_date)
    return sunset
