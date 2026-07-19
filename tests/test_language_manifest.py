"""Language manifest and YAML drift tests."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

from custom_components.hijri_calendar.const import (
    CALENDAR_LANGUAGE_DEFAULT,
    CALENDAR_LANGUAGE_OPTIONS,
    SUPPORTED_LANGUAGES,
    canonical_language,
)

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components" / "hijri_calendar"
DATA_DIR = ROOT / "scripts" / "translation_data"
MANIFEST = DATA_DIR / "manifest.yaml"
SERVICES_YAML = COMPONENT / "services.yaml"
BLUEPRINT_YAML = (
    ROOT
    / "blueprints"
    / "automation"
    / "hijri_calendar"
    / "calibrate_offset_helper.yaml"
)


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _load_blueprint_metadata(path: Path) -> dict:
    """Load blueprint header only (automation body uses HA !input tags)."""
    text = path.read_text(encoding="utf-8")
    blueprint_section, _, _ = text.partition("\ntrigger:\n")
    return yaml.safe_load(blueprint_section)


def _language_lists_from_services(data: dict) -> list[list[str]]:
    lists: list[list[str]] = []
    for service in data.values():
        language_field = service.get("fields", {}).get("language", {})
        selector = language_field.get("selector", {}).get("language", {})
        if languages := selector.get("languages"):
            lists.append(languages)
    return lists


def test_manifest_matches_supported_languages() -> None:
    """Manifest language list must match runtime SUPPORTED_LANGUAGES."""
    manifest = _load_yaml(MANIFEST)
    assert tuple(manifest["languages"]) == SUPPORTED_LANGUAGES


def test_translation_and_calendar_files_exist() -> None:
    """Every supported language has translation and calendar content files."""
    for lang in SUPPORTED_LANGUAGES:
        translation = COMPONENT / "translations" / f"{lang}.json"
        calendar = COMPONENT / "calendar_content" / f"{lang}.json"
        assert translation.is_file(), f"Missing translations/{lang}.json"
        assert calendar.is_file(), f"Missing calendar_content/{lang}.json"


def test_locale_yaml_exists_for_each_language() -> None:
    """Every supported language has a source YAML locale file."""
    for lang in SUPPORTED_LANGUAGES:
        assert (DATA_DIR / f"{lang}.yaml").is_file(), f"Missing {lang}.yaml"


def test_services_yaml_languages_match_supported() -> None:
    """Service language selectors list every supported integration language."""
    services = _load_yaml(SERVICES_YAML)
    expected = list(SUPPORTED_LANGUAGES)
    for languages in _language_lists_from_services(services):
        assert languages == expected


def test_calendar_language_options_are_valid_translation_keys() -> None:
    """Selector options satisfy hassfest's key rule and resolve to languages."""
    valid_key = re.compile(r"^[a-z0-9-_]+$")
    for option in CALENDAR_LANGUAGE_OPTIONS:
        assert valid_key.match(option), f"Invalid selector option key: {option}"
        if option != CALENDAR_LANGUAGE_DEFAULT:
            assert canonical_language(option) in SUPPORTED_LANGUAGES

    strings = json.loads((COMPONENT / "strings.json").read_text(encoding="utf-8"))
    options = strings["selector"]["hijri_month_starts_calendar_language"]["options"]
    assert set(options) == set(CALENDAR_LANGUAGE_OPTIONS)


def test_blueprint_languages_match_supported() -> None:
    """Blueprint language selector lists every supported integration language."""
    blueprint = _load_blueprint_metadata(BLUEPRINT_YAML)
    languages = blueprint["blueprint"]["input"]["language"]["selector"]["language"][
        "languages"
    ]
    assert languages == list(SUPPORTED_LANGUAGES)
