"""Localization helpers for Hijri calendar display."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Final

from hijridate import Hijri
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.translation import async_get_cached_translations

from .const import DOMAIN, SUPPORTED_LANGUAGES, HijriLanguage
from .hijridate_locale import hijridate_language

EASTERN_ARABIC_DIGITS: Final = "٠١٢٣٤٥٦٧٨٩"
_WESTERN_DIGITS: Final = "0123456789"
_CALENDAR_CONTENT_DIR = Path(__file__).parent / "calendar_content"


def to_eastern_arabic_numerals(value: str | int) -> str:
    """Convert Western digits in a string to Eastern Arabic numerals."""
    text = str(value)
    return text.translate(str.maketrans(_WESTERN_DIGITS, EASTERN_ARABIC_DIGITS))


def format_hijri_display(
    hijri: Hijri, language: HijriLanguage, *, eastern_digits: bool = False
) -> str:
    """Return a human-readable Hijri date in the configured language."""
    hijridate_lang = hijridate_language(language)
    display = (
        f"{hijri.day} {hijri.month_name(hijridate_lang)} {hijri.year} "
        f"{Hijri.notation(hijridate_lang)}"
    )
    if eastern_digits:
        return to_eastern_arabic_numerals(display)
    return display


@lru_cache(maxsize=len(SUPPORTED_LANGUAGES))
def _load_calendar_content(language: HijriLanguage) -> dict[str, Any]:
    """Load calendar event text from bundled JSON files."""
    path = _CALENDAR_CONTENT_DIR / f"{language}.json"
    if not path.is_file():
        path = _CALENDAR_CONTENT_DIR / "en.json"
    with path.open(encoding="utf-8") as file:
        return json.load(file)


@callback
def _entity_translation(
    hass: HomeAssistant, language: HijriLanguage, subkey: str, value: str
) -> str:
    """Return a flattened entity translation for the holiday sensor."""
    key = f"component.{DOMAIN}.entity.sensor.holiday.{subkey}.{value}"
    translations = async_get_cached_translations(hass, language, "entity", DOMAIN)
    return translations.get(key, value)


@callback
def _calendar_translation(
    hass: HomeAssistant,
    language: HijriLanguage,
    calendar_key: str,
    section: str,
    event_id: str,
) -> str:
    """Return a calendar content translation."""
    content = _load_calendar_content(language)
    return content[calendar_key][section].get(event_id, event_id)


@callback
def _calendar_scalar(hass: HomeAssistant, language: HijriLanguage, *path: str) -> str:
    """Return a scalar calendar translation at the given path."""
    node: Any = _load_calendar_content(language)
    for part in path:
        node = node[part]
    return str(node)


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


def _apply_month_start_template(template: str, month_name: str) -> str:
    """Replace month placeholder in a month-start template."""
    return template.replace("{month}", month_name)


@callback
def calendar_month_start_summary(
    hass: HomeAssistant,
    month_name: str,
    language: HijriLanguage,
) -> str:
    """Return localized summary for a month-start calendar event."""
    template = _calendar_scalar(
        hass, language, "hijri_month_starts", "summary_template"
    )
    return _apply_month_start_template(template, month_name)


@callback
def build_month_start_description(
    hass: HomeAssistant,
    month_name: str,
    hijri_year: int,
    language: HijriLanguage,
) -> str:
    """Return formatted month-start calendar event description."""
    template = _calendar_scalar(
        hass, language, "hijri_month_starts", "description_template"
    )
    body = _apply_month_start_template(template, month_name)
    reference_url = _calendar_scalar(
        hass, language, "hijri_month_starts", "reference_url"
    )
    return format_calendar_event_description(
        body,
        calendar_reference_label(hass, language),
        reference_url,
        year_line=format_history_year(hass, hijri_year, language),
    )
