"""Alternate calendar provider exposing Hijri dates to Home Assistant core."""

import datetime as dt

from hijridate import Hijri
from homeassistant.components.calendar.alternate_calendar import (
    AlternateCalendarProvider,
    AlternateCalendarRegistry,
    AlternateDate,
)
from homeassistant.exceptions import HomeAssistantError

from .const import CALENDAR_TYPE_HIJRI, DEFAULT_LANGUAGE, HijriLanguage
from .helpers import gregorian_to_hijri
from .hijridate_locale import hijridate_language
from .locale import format_hijri_display


@AlternateCalendarRegistry.register(CALENDAR_TYPE_HIJRI)
class HijriAlternateCalendarProvider(AlternateCalendarProvider):
    """Convert Gregorian dates to Hijri dates for the core alternate calendar API."""

    def __init__(self, language: HijriLanguage = DEFAULT_LANGUAGE) -> None:
        """Initialize the provider with a language for display names."""
        self._language = language

    @property
    def calendar_type(self) -> str:
        """Return the identifier of the alternate calendar system."""
        return CALENDAR_TYPE_HIJRI

    def convert_date(self, gregorian_date: dt.date) -> AlternateDate:
        """Convert a Gregorian date to a Hijri date."""
        try:
            hijri = gregorian_to_hijri(gregorian_date)
        except HomeAssistantError:
            return AlternateDate(CALENDAR_TYPE_HIJRI, display_name="", date_str="")
        hijridate_lang = hijridate_language(self._language)
        return AlternateDate(
            calendar_type=CALENDAR_TYPE_HIJRI,
            display_name=format_hijri_display(hijri, self._language),
            date_str=hijri.isoformat(),
            metadata={
                "hijri_year": hijri.year,
                "hijri_month": hijri.month,
                "hijri_day": hijri.day,
                "month_name": hijri.month_name(hijridate_lang),
                "notation": Hijri.notation(hijridate_lang),
            },
        )
