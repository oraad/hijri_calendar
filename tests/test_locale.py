"""Test localization helpers."""

import pytest
from hijridate import Hijri
from homeassistant.helpers import translation

from custom_components.hijri_calendar.const import DOMAIN
from custom_components.hijri_calendar.holidays import (
    HOLIDAY_NONE,
    HOLIDAY_RAMADAN,
    TYPE_EID,
    TYPE_RAMADAN,
)
from custom_components.hijri_calendar.locale import (
    format_hijri_display,
    holiday_display_name,
    holiday_type_display_name,
    to_eastern_arabic_numerals,
)


def test_to_eastern_arabic_numerals() -> None:
    """Test Western to Eastern Arabic digit conversion."""
    assert to_eastern_arabic_numerals("1446-10-15") == "١٤٤٦-١٠-١٥"
    assert to_eastern_arabic_numerals(15) == "١٥"


def test_format_hijri_display_english() -> None:
    """Test formatted display in English with Western digits."""
    hijri = Hijri(1446, 10, 15)
    result = format_hijri_display(hijri, "en", eastern_digits=False)
    assert "15" in result
    assert "Shawwal" in result
    assert "1446" in result
    assert "AH" in result


def test_format_hijri_display_arabic_eastern() -> None:
    """Test formatted display in Arabic with Eastern digits."""
    hijri = Hijri(1446, 10, 15)
    result = format_hijri_display(hijri, "ar", eastern_digits=True)
    assert "شوال" in result
    assert "١٥" in result
    assert "١٤٤٦" in result
    assert "هـ" in result
    assert "15" not in result


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        ("en", "Ramadan"),
        ("ar", "رمضان"),
        ("tr", "Ramazan"),
    ],
)
async def test_holiday_display_name(hass, language: str, expected: str) -> None:
    """Test localized holiday state names via HA translations."""
    await translation.async_get_translations(
        hass, language, "entity", integrations=[DOMAIN]
    )
    assert holiday_display_name(hass, HOLIDAY_RAMADAN, language) == expected


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        ("en", "Ramadan"),
        ("ar", "رمضان"),
        ("tr", "Ramazan"),
    ],
)
async def test_holiday_type_display_name(hass, language: str, expected: str) -> None:
    """Test localized holiday type labels via HA translations."""
    await translation.async_get_translations(
        hass, language, "entity", integrations=[DOMAIN]
    )
    assert holiday_type_display_name(hass, TYPE_RAMADAN, language) == expected


async def test_holiday_none_display_name(hass) -> None:
    """Test localized label when no holiday is active."""
    for language, expected in (("en", "None"), ("ar", "لا يوجد"), ("tr", "Yok")):
        await translation.async_get_translations(
            hass, language, "entity", integrations=[DOMAIN]
        )
        assert holiday_display_name(hass, HOLIDAY_NONE, language) == expected


async def test_holiday_type_eid_arabic(hass) -> None:
    """Test a non-ramadan holiday type translation."""
    await translation.async_get_translations(
        hass, "ar", "entity", integrations=[DOMAIN]
    )
    assert holiday_type_display_name(hass, TYPE_EID, "ar") == "عيد"
