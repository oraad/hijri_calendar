"""Test translation JSON coverage for holiday constants."""

import json
from pathlib import Path

from custom_components.hijri_calendar.holidays import ALL_HOLIDAY_IDS, ALL_HOLIDAY_TYPES

STRINGS_PATH = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "hijri_calendar"
    / "strings.json"
)


def test_holiday_state_and_types_in_strings_json() -> None:
    """Every holiday id and type constant has a strings.json entry."""
    with STRINGS_PATH.open(encoding="utf-8") as file:
        strings = json.load(file)

    holiday = strings["entity"]["sensor"]["holiday"]
    state_keys = set(holiday["state"])
    type_keys = set(holiday["types"])

    missing_states = ALL_HOLIDAY_IDS - state_keys
    missing_types = ALL_HOLIDAY_TYPES - type_keys

    assert not missing_states, f"Missing state keys in strings.json: {missing_states}"
    assert not missing_types, f"Missing types keys in strings.json: {missing_types}"
