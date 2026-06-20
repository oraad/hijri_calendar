"""Localization helpers for Hijri calendar display."""

from __future__ import annotations

from typing import Final

from hijridate import Hijri
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.translation import async_get_cached_translations

from .const import DOMAIN, HijriLanguage

CALENDAR_CONTENT_CATEGORY = "calendar_content"

EASTERN_ARABIC_DIGITS: Final = "٠١٢٣٤٥٦٧٨٩"
_WESTERN_DIGITS: Final = "0123456789"


def to_eastern_arabic_numerals(value: str | int) -> str:
    """Convert Western digits in a string to Eastern Arabic numerals."""
    text = str(value)
    return text.translate(str.maketrans(_WESTERN_DIGITS, EASTERN_ARABIC_DIGITS))


def format_hijri_display(
    hijri: Hijri, language: HijriLanguage, *, eastern_digits: bool = False
) -> str:
    """Return a human-readable Hijri date in the configured language."""
    display = (
        f"{hijri.day} {hijri.month_name(language)} {hijri.year} "
        f"{Hijri.notation(language)}"
    )
    if eastern_digits:
        return to_eastern_arabic_numerals(display)
    return display


@callback
def _entity_translation(
    hass: HomeAssistant, language: HijriLanguage, subkey: str, value: str
) -> str:
    """Return a flattened entity translation for the holiday sensor."""
    key = f"component.{DOMAIN}.entity.sensor.holiday.{subkey}.{value}"
    translations = async_get_cached_translations(hass, language, "entity", DOMAIN)
    return translations.get(key, value)


@callback
def _calendar_content_translations(
    hass: HomeAssistant, language: HijriLanguage
) -> dict[str, str]:
    """Return flattened calendar content translations."""
    return async_get_cached_translations(
        hass, language, CALENDAR_CONTENT_CATEGORY, DOMAIN
    )


@callback
def _calendar_translation(
    hass: HomeAssistant,
    language: HijriLanguage,
    calendar_key: str,
    section: str,
    event_id: str,
) -> str:
    """Return a flattened calendar content translation."""
    key = (
        f"component.{DOMAIN}.{CALENDAR_CONTENT_CATEGORY}."
        f"{calendar_key}.{section}.{event_id}"
    )
    return _calendar_content_translations(hass, language).get(key, event_id)


@callback
def _calendar_scalar(hass: HomeAssistant, language: HijriLanguage, *path: str) -> str:
    """Return a scalar calendar translation at the given path."""
    suffix = ".".join(path)
    key = f"component.{DOMAIN}.{CALENDAR_CONTENT_CATEGORY}.{suffix}"
    return _calendar_content_translations(hass, language).get(key, path[-1])


def format_calendar_event_description(
    body: str,
    reference_label: str,
    reference_url: str,
    *,
    year_line: str | None = None,
) -> str:
    """Build a calendar event description with optional year line and reference."""
    parts: list[str] = [body.strip()]
    if year_line:
        parts.append(year_line.strip())
    if reference_url:
        parts.append(f"{reference_label}: {reference_url}")
    return "\n\n".join(part for part in parts if part)


@callback
def holiday_display_name(
    hass: HomeAssistant, holiday_id: str, language: HijriLanguage
) -> str:
    """Return the localized display name for a holiday id."""
    return _entity_translation(hass, language, "state", holiday_id)


@callback
def holiday_type_display_name(
    hass: HomeAssistant, type_id: str, language: HijriLanguage
) -> str:
    """Return the localized display name for a holiday type."""
    return _entity_translation(hass, language, "state", f"type_{type_id}")


@callback
def calendar_reference_label(hass: HomeAssistant, language: HijriLanguage) -> str:
    """Return the localized label for calendar reference links."""
    return _calendar_scalar(hass, language, "reference_label")


@callback
def calendar_observance_detail(
    hass: HomeAssistant, event_id: str, language: HijriLanguage
) -> tuple[str, str]:
    """Return localized description and reference URL for an observance."""
    description = _calendar_translation(
        hass, language, "hijri_events", "description", event_id
    )
    reference_url = _calendar_translation(
        hass, language, "hijri_events", "reference_url", event_id
    )
    return description, reference_url


@callback
def calendar_history_name(
    hass: HomeAssistant, event_id: str, language: HijriLanguage
) -> str:
    """Return localized summary for a history calendar event."""
    return _calendar_translation(
        hass, language, "islamic_history", "event_name", event_id
    )


@callback
def calendar_history_detail(
    hass: HomeAssistant, event_id: str, language: HijriLanguage
) -> tuple[str, str]:
    """Return localized description and reference URL for a history event."""
    description = _calendar_translation(
        hass, language, "islamic_history", "description", event_id
    )
    reference_url = _calendar_translation(
        hass, language, "islamic_history", "reference_url", event_id
    )
    return description, reference_url


@callback
def format_history_year(
    hass: HomeAssistant, hijri_year: int, language: HijriLanguage
) -> str:
    """Return a localized AH year line for history events."""
    template = _calendar_scalar(hass, language, "islamic_history", "year_suffix")
    year_text = str(hijri_year)
    if language == "ar":
        year_text = to_eastern_arabic_numerals(year_text)
    return template.replace("{year}", year_text)


@callback
def build_observance_description(
    hass: HomeAssistant,
    event_id: str,
    language: HijriLanguage,
) -> str:
    """Return formatted observance calendar event description."""
    body, reference_url = calendar_observance_detail(hass, event_id, language)
    return format_calendar_event_description(
        body,
        calendar_reference_label(hass, language),
        reference_url,
    )


@callback
def build_history_description(
    hass: HomeAssistant,
    event_id: str,
    hijri_year: int,
    language: HijriLanguage,
) -> str:
    """Return formatted history calendar event description."""
    body, reference_url = calendar_history_detail(hass, event_id, language)
    return format_calendar_event_description(
        body,
        calendar_reference_label(hass, language),
        reference_url,
        year_line=format_history_year(hass, hijri_year, language),
    )
