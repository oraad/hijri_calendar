"""Shared helpers for Hijri calendar event builders."""

from __future__ import annotations

import datetime as dt
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from hijridate import Hijri
from homeassistant.util import dt as dt_util

from .const import (
    CALENDAR_LANGUAGE_ARABIC,
    CALENDAR_LANGUAGE_DEFAULT,
    HijriLanguage,
    is_supported_language,
)
from .helpers import gregorian_to_hijri, resolve_effective_gregorian_date
from .holidays import HijriHoliday, get_active_events, get_holidays

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

MAX_RANGE_DAYS = 3 * 365


@dataclass(frozen=True)
class CalendarEventConfig:
    """Settings used when building calendar events."""

    display_language: HijriLanguage
    day_boundary: str
    offset_days: int


@dataclass(frozen=True)
class DayObservances:
    """Observances mapped to a Gregorian calendar day."""

    gregorian_date: dt.date
    hijri_year: int
    hijri_month: int
    hijri_day: int
    holidays: tuple[HijriHoliday, ...]
    active_events: frozenset[str]


def resolve_calendar_display_language(
    integration_language: HijriLanguage,
    calendar_language_option: str,
) -> HijriLanguage:
    """Return the language used for calendar event text."""
    if calendar_language_option == CALENDAR_LANGUAGE_DEFAULT:
        return integration_language
    if is_supported_language(calendar_language_option):
        return calendar_language_option
    if calendar_language_option == CALENDAR_LANGUAGE_ARABIC:
        return "ar"
    return integration_language


def clamp_range(
    start_date: dt.datetime, end_date: dt.datetime
) -> tuple[dt.date, dt.date]:
    """Return local date bounds, capped to MAX_RANGE_DAYS."""
    start = dt_util.as_local(start_date).date()
    end = dt_util.as_local(end_date).date()
    end = max(end, start)
    if (end - start).days > MAX_RANGE_DAYS:
        end = start + dt.timedelta(days=MAX_RANGE_DAYS)
    return start, end


def effective_hijri(
    hass: HomeAssistant,
    day_boundary: str,
    offset_days: int,
    gregorian_day: dt.date,
) -> tuple[Hijri, dt.date]:
    """Return Hijri date and effective Gregorian date for a calendar day."""
    reference = dt_util.start_of_local_day(
        dt_util.as_local(dt.datetime.combine(gregorian_day, dt.time()))
    )
    effective_gregorian = resolve_effective_gregorian_date(
        hass,
        day_boundary,
        offset_days,
        reference=reference,
    )
    return gregorian_to_hijri(effective_gregorian), effective_gregorian


def scan_days(
    hass: HomeAssistant,
    day_boundary: str,
    offset_days: int,
    start: dt.date,
    end: dt.date,
) -> list[DayObservances]:
    """Scan Gregorian days and collect observances for each."""
    days: list[DayObservances] = []
    current = start
    while current <= end:
        try:
            hijri, _ = effective_hijri(hass, day_boundary, offset_days, current)
        except Exception:  # noqa: BLE001 - skip days outside hijridate range
            current += dt.timedelta(days=1)
            continue
        holidays = tuple(get_holidays(hijri))
        days.append(
            DayObservances(
                gregorian_date=current,
                hijri_year=hijri.year,
                hijri_month=hijri.month,
                hijri_day=hijri.day,
                holidays=holidays,
                active_events=frozenset(get_active_events(hijri)),
            )
        )
        current += dt.timedelta(days=1)
    return days


def merge_span_days(
    days: list[DayObservances],
    is_active: Callable[[DayObservances], bool],
) -> list[tuple[dt.date, dt.date, int]]:
    """Merge consecutive days into spans; return (start, end, hijri_year)."""
    spans: list[tuple[dt.date, dt.date, int]] = []
    span_start: dt.date | None = None
    span_end: dt.date | None = None
    span_year: int | None = None

    for day in days:
        if is_active(day):
            if span_start is None:
                span_start = day.gregorian_date
                span_end = day.gregorian_date
                span_year = day.hijri_year
            else:
                span_end = day.gregorian_date
        elif span_start is not None and span_end is not None and span_year is not None:
            spans.append((span_start, span_end, span_year))
            span_start = None
            span_end = None
            span_year = None

    if span_start is not None and span_end is not None and span_year is not None:
        spans.append((span_start, span_end, span_year))

    return spans
