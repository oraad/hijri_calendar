"""Test helper functions."""

import datetime as dt

import pytest
from hijridate import Hijri
from homeassistant.exceptions import HomeAssistantError

from custom_components.hijri_calendar.helpers import (
    format_hijri_dict,
    gregorian_to_hijri,
    hijri_to_gregorian,
    parse_hijri_date,
)


def test_gregorian_to_hijri_known_date() -> None:
    """Test conversion for a known date."""
    hijri = gregorian_to_hijri(dt.date(2024, 4, 9))
    assert hijri.year == 1445
    assert hijri.month == 9
    assert hijri.day == 30


def test_hijri_to_gregorian_round_trip() -> None:
    """Test round-trip conversion."""
    hijri = Hijri(1446, 11, 17)
    gregorian = hijri_to_gregorian(hijri)
    assert gregorian_to_hijri(gregorian).datetuple() == hijri.datetuple()


def test_parse_hijri_date() -> None:
    """Test parsing ISO Hijri dates."""
    hijri = parse_hijri_date("1446-11-17")
    assert hijri.year == 1446
    assert hijri.month == 11
    assert hijri.day == 17


def test_format_hijri_dict() -> None:
    """Test formatted output includes expected keys."""
    hijri = Hijri(1446, 1, 1)
    result = format_hijri_dict(hijri, "en")
    assert result["hijri"] == "1446-01-01"
    assert result["month_name"] == hijri.month_name("en")
    assert "notation" in result
    assert "formatted" in result
    assert "formatted_eastern" in result
    assert "١" in result["formatted_eastern"]


def test_parse_invalid_hijri_date() -> None:
    """Test invalid dates raise HomeAssistantError."""
    with pytest.raises(HomeAssistantError):
        parse_hijri_date("not-a-date")
