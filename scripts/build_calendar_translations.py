"""Generate integration translation JSON and calendar content from locale YAML."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components" / "hijri_calendar"
DATA_DIR = Path(__file__).resolve().parent / "translation_data"
CALENDAR_CONTENT = COMPONENT / "calendar_content"
TRANSLATIONS = COMPONENT / "translations"
MANIFEST = DATA_DIR / "manifest.yaml"
LANGUAGE_LABELS = DATA_DIR / "language_labels.yaml"
MONTH_STARTS = DATA_DIR / "month_starts.yaml"
EN_TEMPLATE = TRANSLATIONS / "en.json"


def _load_manifest() -> list[str]:
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    return list(manifest["languages"])


def _load_locale(lang: str) -> dict[str, Any]:
    path = DATA_DIR / f"{lang}.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _set_nested(data: dict[str, Any], path: tuple[str, ...], value: str) -> None:
    node = data
    for key in path[:-1]:
        node = node.setdefault(key, {})
    node[path[-1]] = value


def _build_translation_file(
    _lang: str,
    locale: dict[str, Any],
    language_labels: dict[str, str],
) -> dict[str, Any]:
    template = copy.deepcopy(json.loads(EN_TEMPLATE.read_text(encoding="utf-8")))
    ui = locale["ui"]
    holidays = locale["holidays"]

    mapping: list[tuple[tuple[str, ...], str]] = [
        (("config", "step", "user", "title"), "config_user_title"),
        (("config", "step", "user", "description"), "config_user_description"),
        (("config", "step", "user", "data", "language"), "config_user_language"),
        (("config", "step", "user", "data", "day_boundary"), "config_user_day_boundary"),
        (("config", "step", "reconfigure", "title"), "config_reconfigure_title"),
        (("config", "abort", "already_configured"), "config_abort_already_configured"),
        (("options", "step", "init", "title"), "options_title"),
        (("options", "step", "init", "data", "offset_days"), "options_offset_days"),
        (
            ("options", "step", "init", "data", "observances_calendar_language"),
            "options_observances_calendar_language",
        ),
        (
            ("options", "step", "init", "data", "islamic_history_calendar_language"),
            "options_islamic_history_calendar_language",
        ),
        (
            ("options", "step", "init", "data", "hijri_month_starts_calendar_language"),
            "options_hijri_month_starts_calendar_language",
        ),
        (("selector", "day_boundary", "options", "midnight"), "selector_midnight"),
        (("selector", "day_boundary", "options", "sunset"), "selector_sunset"),
        (
            ("selector", "observances_calendar_language", "options", "default"),
            "selector_integration_language",
        ),
        (
            ("selector", "observances_calendar_language", "options", "ar"),
            "selector_arabic_label",
        ),
        (("entity", "sensor", "hijri_date", "name"), "entity_hijri_date"),
        (("entity", "sensor", "holiday", "name"), "entity_holiday"),
        (("entity", "sensor", "days_in_month", "name"), "entity_days_in_month"),
        (("entity", "sensor", "days_in_year", "name"), "entity_days_in_year"),
        (("entity", "sensor", "days_until_ramadan", "name"), "entity_days_until_ramadan"),
        (
            ("entity", "sensor", "days_until_eid_al_fitr", "name"),
            "entity_days_until_eid_al_fitr",
        ),
        (("entity", "calendar", "hijri_events", "name"), "entity_calendar_observances"),
        (("entity", "calendar", "islamic_history", "name"), "entity_calendar_history"),
        (
            ("entity", "calendar", "hijri_month_starts", "name"),
            "entity_calendar_month_starts",
        ),
        (("entity", "binary_sensor", "ramadan", "name"), "entity_ramadan"),
        (("entity", "binary_sensor", "eid_al_fitr", "name"), "entity_eid_al_fitr"),
        (("entity", "binary_sensor", "eid_al_adha", "name"), "entity_eid_al_adha"),
        (("entity", "binary_sensor", "hajj_season", "name"), "entity_hajj_season"),
        (("issues", "sunset_unavailable", "title"), "issue_sunset_title"),
        (("issues", "sunset_unavailable", "description"), "issue_sunset_description"),
        (("services", "calibrate_date", "name"), "service_calibrate_name"),
        (("services", "calibrate_date", "description"), "service_calibrate_description"),
        (
            ("services", "calibrate_date", "fields", "offset", "name"),
            "service_calibrate_offset_name",
        ),
        (
            ("services", "calibrate_date", "fields", "offset", "description"),
            "service_calibrate_offset_description",
        ),
        (
            ("services", "calibrate_date", "fields", "hijri", "name"),
            "service_calibrate_hijri_name",
        ),
        (
            ("services", "calibrate_date", "fields", "hijri", "description"),
            "service_calibrate_hijri_description",
        ),
        (
            ("services", "calibrate_date", "fields", "language", "name"),
            "service_calibrate_language_name",
        ),
        (
            ("services", "calibrate_date", "fields", "language", "description"),
            "service_calibrate_language_description",
        ),
        (("exceptions", "date_out_of_range", "message"), "exception_date_out_of_range"),
        (("exceptions", "sunset_unavailable", "message"), "exception_sunset_unavailable"),
        (
            ("exceptions", "calibrate_no_config_entry", "message"),
            "exception_calibrate_no_config_entry",
        ),
        (
            ("exceptions", "calibrate_offset_out_of_range", "message"),
            "exception_calibrate_offset_out_of_range",
        ),
    ]

    for path, ui_key in mapping:
        _set_nested(template, path, ui[ui_key])

    template["selector"]["islamic_history_calendar_language"] = copy.deepcopy(
        template["selector"]["observances_calendar_language"]
    )

    month_starts_selector: dict[str, str] = {
        "default": ui["selector_integration_language"],
        **language_labels,
    }
    template["selector"]["hijri_month_starts_calendar_language"] = {
        "options": month_starts_selector,
    }

    template["entity"]["sensor"]["holiday"]["state"] = holidays

    return template


def _build_calendar_content(
    lang: str,
    locale: dict[str, Any],
    month_starts_templates: dict[str, Any],
) -> dict[str, Any]:
    calendar = locale["calendar"]
    observance_descriptions: dict[str, str] = {}
    observance_urls: dict[str, str] = {}
    for event_id, content in calendar["observances"].items():
        observance_descriptions[event_id] = content["description"]
        observance_urls[event_id] = content["reference_url"]

    history_names: dict[str, str] = {}
    history_descriptions: dict[str, str] = {}
    history_urls: dict[str, str] = {}
    for event_id, content in calendar["history"].items():
        history_names[event_id] = content["name"]
        history_descriptions[event_id] = content["description"]
        history_urls[event_id] = content["reference_url"]

    month_starts = month_starts_templates[lang]
    reference_url = calendar["observances"]["hijri_new_year"]["reference_url"]

    return {
        "reference_label": calendar["reference_label"],
        "hijri_events": {
            "description": observance_descriptions,
            "reference_url": observance_urls,
        },
        "islamic_history": {
            "event_name": history_names,
            "description": history_descriptions,
            "reference_url": history_urls,
            "year_suffix": calendar["year_suffix"],
        },
        "hijri_month_starts": {
            "summary_template": month_starts["summary_template"],
            "description_template": month_starts["description_template"],
            "reference_url": reference_url,
        },
    }


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    languages = _load_manifest()
    language_labels = _load_yaml(LANGUAGE_LABELS)["labels"]
    month_starts_templates = _load_yaml(MONTH_STARTS)

    for lang in languages:
        locale = _load_locale(lang)
        translation = _build_translation_file(lang, locale, language_labels)
        calendar_content = _build_calendar_content(lang, locale, month_starts_templates)

        if lang == "en":
            _write_json(COMPONENT / "strings.json", translation)
        _write_json(TRANSLATIONS / f"{lang}.json", translation)
        _write_json(CALENDAR_CONTENT / f"{lang}.json", calendar_content)


if __name__ == "__main__":
    main()
