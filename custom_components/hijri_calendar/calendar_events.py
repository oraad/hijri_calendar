"""Build Home Assistant calendar events for Hijri observances."""

from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING

from homeassistant.components.calendar import CalendarEvent
from homeassistant.helpers.translation import async_get_cached_translations

from .calendar_common import (
    CalendarEventConfig,
    clamp_range,
    merge_span_days,
    scan_days,
)
from .const import DOMAIN, HijriLanguage
from .holidays import (
    EVENT_HAJJ_SEASON,
    EVENT_RAMADAN,
    HOLIDAY_HAJJ,
    HOLIDAY_RAMADAN,
    SPAN_HAJJ_SEASON,
    SPAN_RAMADAN,
)
from .locale import (
    build_observance_description,
    holiday_display_name,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

POINT_EXCLUDED_IN_SPAN = frozenset({HOLIDAY_RAMADAN, HOLIDAY_HAJJ})


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
    start, end = clamp_range(start_date, end_date)
    days = scan_days(hass, config.day_boundary, config.offset_days, start, end)
    events: list[CalendarEvent] = []
    language = config.display_language

    ramadan_spans = merge_span_days(
        days, is_active=lambda day: EVENT_RAMADAN in day.active_events
    )
    for span_start, span_end, hijri_year in ramadan_spans:
        events.append(
            CalendarEvent(
                start=span_start,
                end=span_end + dt.timedelta(days=1),
                summary=_span_summary(hass, language, SPAN_RAMADAN, hijri_year),
                description=build_observance_description(hass, SPAN_RAMADAN, language),
                uid=f"{DOMAIN}:span:{SPAN_RAMADAN}:{span_start.isoformat()}",
            )
        )

    hajj_spans = merge_span_days(
        days, is_active=lambda day: EVENT_HAJJ_SEASON in day.active_events
    )
    for span_start, span_end, hijri_year in hajj_spans:
        events.append(
            CalendarEvent(
                start=span_start,
                end=span_end + dt.timedelta(days=1),
                summary=_span_summary(hass, language, SPAN_HAJJ_SEASON, hijri_year),
                description=build_observance_description(
                    hass, SPAN_HAJJ_SEASON, language
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
                    summary=holiday_display_name(hass, holiday.id, language),
                    description=build_observance_description(
                        hass, holiday.id, language
                    ),
                    uid=f"{DOMAIN}:{holiday.id}:{day.gregorian_date.isoformat()}",
                )
            )

    return events
