"""Test translation JSON coverage for holiday and calendar constants."""

from __future__ import annotations

import json
import re
from pathlib import Path

from custom_components.hijri_calendar.const import SUPPORTED_LANGUAGES
from custom_components.hijri_calendar.historical_events import ALL_HISTORICAL_EVENT_IDS
from custom_components.hijri_calendar.holidays import (
    ALL_HOLIDAY_IDS,
    ALL_HOLIDAY_TYPES,
    ALL_OBSERVANCE_CALENDAR_EVENT_IDS,
)

COMPONENT = Path(__file__).resolve().parents[1] / "custom_components" / "hijri_calendar"
CALENDAR_CONTENT_FILES = tuple(
    COMPONENT / "calendar_content" / f"{lang}.json" for lang in SUPPORTED_LANGUAGES
)
HTTPS_URL = re.compile(r"^https://")


def _load(path: Path) -> dict:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def test_holiday_state_and_types_in_strings_json() -> None:
    """Every holiday id and type constant has a strings.json entry."""
    strings = _load(COMPONENT / "strings.json")
    holiday = strings["entity"]["sensor"]["holiday"]
    state_keys = set(holiday["state"])

    missing_states = ALL_HOLIDAY_IDS - state_keys
    missing_types = {f"type_{type_id}" for type_id in ALL_HOLIDAY_TYPES} - state_keys

    assert not missing_states, f"Missing state keys in strings.json: {missing_states}"
    assert not missing_types, (
        f"Missing type state keys in strings.json: {missing_types}"
    )
    assert "mawlid" not in state_keys


def test_observance_calendar_translations_in_all_language_files() -> None:
    """Every observance calendar event has description and URL in all languages."""
    for path in CALENDAR_CONTENT_FILES:
        data = _load(path)
        calendar = data["hijri_events"]
        descriptions = set(calendar["description"])
        urls = set(calendar["reference_url"])
        missing = ALL_OBSERVANCE_CALENDAR_EVENT_IDS - descriptions
        assert not missing, f"{path.name} missing observance descriptions: {missing}"
        assert descriptions == urls, f"{path.name} description/url keys mismatch"
        for event_id in ALL_OBSERVANCE_CALENDAR_EVENT_IDS:
            assert HTTPS_URL.match(calendar["reference_url"][event_id]), event_id


def test_history_calendar_translations_in_all_language_files() -> None:
    """Every history event has name, description, and URL in all languages."""
    for path in CALENDAR_CONTENT_FILES:
        data = _load(path)
        calendar = data["islamic_history"]
        names = set(calendar["event_name"])
        descriptions = set(calendar["description"])
        urls = set(calendar["reference_url"])
        missing = ALL_HISTORICAL_EVENT_IDS - names
        assert not missing, f"{path.name} missing history names: {missing}"
        assert names == descriptions == urls, f"{path.name} history key mismatch"
        for event_id in ALL_HISTORICAL_EVENT_IDS:
            assert HTTPS_URL.match(calendar["reference_url"][event_id]), event_id
        assert "{year}" in calendar["year_suffix"]


def test_month_start_calendar_translations_in_all_language_files() -> None:
    """Every language file has month-start templates and a reference URL."""
    for path in CALENDAR_CONTENT_FILES:
        data = _load(path)
        month_starts = data["hijri_month_starts"]
        assert "{month}" in month_starts["summary_template"], path.name
        assert "{month}" in month_starts["description_template"], path.name
        assert HTTPS_URL.match(month_starts["reference_url"]), path.name
