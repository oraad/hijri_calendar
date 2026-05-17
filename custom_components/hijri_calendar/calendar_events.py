"""Build Home Assistant calendar events for Hijri observances."""

from __future__ import annotations

import datetime as dt
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from hijridate import Hijri
from homeassistant.components.calendar import CalendarEvent
from homeassistant.helpers.translation import async_get_cached_translations
from homeassistant.util import dt as dt_util

from .const import DOMAIN, HijriLanguage
from .helpers import gregorian_to_hijri, resolve_effective_gregorian_date
from .holidays import (
    EVENT_HAJJ_SEASON,
    EVENT_RAMADAN,
    HOLIDAY_HAJJ,
    HOLIDAY_RAMADAN,
    HijriHoliday,
    get_active_events,
    get_holidays,
)
from .locale import holiday_display_name, holiday_type_display_name

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

MAX_RANGE_DAYS = 3 * 365

SPAN_RAMADAN = "ramadan"
SPAN_HAJJ_SEASON = "hajj_season"

POINT_EXCLUDED_IN_SPAN = frozenset({HOLIDAY_RAMADAN, HOLIDAY_HAJJ})


@dataclass(frozen=True)
class CalendarEventConfig:
    """Settings used when building calendar events."""

    language: HijriLanguage
    day_boundary: str
    offset_days: int


@dataclass(frozen=True)
class _DayObservances:
    """Observances mapped to a Gregorian calendar day."""

    gregorian_date: dt.date
    hijri_year: int
    holidays: tuple[HijriHoliday, ...]
    active_events: frozenset[str]


def _clamp_range(
    start_date: dt.datetime, end_date: dt.datetime
) -> tuple[dt.date, dt.date]:
    """Return local date bounds, capped to MAX_RANGE_DAYS."""
    start = dt_util.as_local(start_date).date()
    end = dt_util.as_local(end_date).date()
    end = max(end, start)
    if (end - start).days > MAX_RANGE_DAYS:
        end = start + dt.timedelta(days=MAX_RANGE_DAYS)
    return start, end


def _effective_hijri(
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


def _scan_days(
    hass: HomeAssistant,
    day_boundary: str,
    offset_days: int,
    start: dt.date,
    end: dt.date,
) -> list[_DayObservances]:
    """Scan Gregorian days and collect observances for each."""
    days: list[_DayObservances] = []
    current = start
    while current <= end:
        try:
            hijri, _ = _effective_hijri(hass, day_boundary, offset_days, current)
        except Exception:  # noqa: BLE001 - skip days outside hijridate range
            current += dt.timedelta(days=1)
            continue
        holidays = tuple(get_holidays(hijri))
        days.append(
            _DayObservances(
                gregorian_date=current,
                hijri_year=hijri.year,
                holidays=holidays,
                active_events=frozenset(get_active_events(hijri)),
            )
        )
        current += dt.timedelta(days=1)
    return days


def _merge_span_days(
    days: list[_DayObservances],
    is_active: Callable[[_DayObservances], bool],
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


def _span_summary(
    hass: HomeAssistant,
    language: HijriLanguage,
    span_key: str,
    hijri_year: int,
) -> str:
    """Return a localized summary for a merged span event."""
    if span_key == SPAN_RAMADAN:
        name = holiday_display_name(hass, HOLIDAY_RAMADAN, language)
        return f"{name} {hijri_year} AH"
    if span_key == SPAN_HAJJ_SEASON:
        translations = async_get_cached_translations(hass, language, "entity", DOMAIN)
        key = f"component.{DOMAIN}.entity.binary_sensor.hajj_season.name"
        return translations.get(key, "Hajj season")
    return span_key


def build_calendar_events(
    hass: HomeAssistant,
    config: CalendarEventConfig,
    start_date: dt.datetime,
    end_date: dt.datetime,
) -> list[CalendarEvent]:
    """Build calendar events for the requested Gregorian datetime range."""
    start, end = _clamp_range(start_date, end_date)
    days = _scan_days(hass, config.day_boundary, config.offset_days, start, end)
    events: list[CalendarEvent] = []

    ramadan_spans = _merge_span_days(
        days, is_active=lambda day: EVENT_RAMADAN in day.active_events
    )
    for span_start, span_end, hijri_year in ramadan_spans:
        events.append(
            CalendarEvent(
                start=span_start,
                end=span_end + dt.timedelta(days=1),
                summary=_span_summary(hass, config.language, SPAN_RAMADAN, hijri_year),
                uid=f"{DOMAIN}:span:{SPAN_RAMADAN}:{span_start.isoformat()}",
            )
        )

    hajj_spans = _merge_span_days(
        days, is_active=lambda day: EVENT_HAJJ_SEASON in day.active_events
    )
    for span_start, span_end, hijri_year in hajj_spans:
        events.append(
            CalendarEvent(
                start=span_start,
                end=span_end + dt.timedelta(days=1),
                summary=_span_summary(
                    hass, config.language, SPAN_HAJJ_SEASON, hijri_year
                ),
                uid=f"{DOMAIN}:span:{SPAN_HAJJ_SEASON}:{span_start.isoformat()}",
            )
        )

    for day in days:
        for holiday in day.holidays:
            if holiday.id in POINT_EXCLUDED_IN_SPAN:
                continue
            events.append(
                CalendarEvent(
                    start=day.gregorian_date,
                    end=day.gregorian_date + dt.timedelta(days=1),
                    summary=holiday_display_name(hass, holiday.id, config.language),
                    description=holiday_type_display_name(
                        hass, holiday.type, config.language
                    ),
                    uid=f"{DOMAIN}:{holiday.id}:{day.gregorian_date.isoformat()}",
                )
            )

    return events
