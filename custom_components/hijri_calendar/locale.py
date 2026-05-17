"""Localization helpers for Hijri calendar display."""

from __future__ import annotations

from typing import Final

from hijridate import Hijri
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.translation import async_get_cached_translations

from .const import DOMAIN, HijriLanguage

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
    return _entity_translation(hass, language, "types", type_id)
