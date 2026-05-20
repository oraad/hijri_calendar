# Changelog

All notable changes to this project are documented in this file.

## [0.1.0] - 2026-05-19

First stable release. Includes all changes from `0.1.0-beta.3` below.

## [0.1.0-beta.3] - 2026-05-19

### Added

- HACS `zip_release`: install from published GitHub releases (`hijri_calendar.zip`); enable *Show beta versions* for pre-releases.
- Integration Quality Scale: Platinum tier (`quality_scale.yaml`).
- **`calibrate_date` service**: relative day offset (±2) or announced Hijri date for today (persists to integration options).
- **`set_day_offset` service**: absolute day offset (−2 to +2).
- Countdown sensors (disabled by default): days until Ramadan and Eid al-Fitr.
- Automation blueprints: Ramadan mode, Eid greetings, daily Hijri date, iftar reminder, offset calibration.
- Repairs: sunset-unavailable warning when day boundary is *After sunset*.
- Brand assets: updated icons and logos.

### Changed

- Day offset limited to −2..+2; config entry migration (v2) clamps legacy values.
- Config flow options use number selector for offset.

## [0.1.0-beta.2] - 2026-05-17

### Added

- Calendar entity **Hijri observances** (`calendar.hijri_events`): all-day Gregorian events for Islamic holidays with merged Ramadan and Hajj season spans.
- Sensor device classes: `DATE` (Hijri date), `ENUM` (holiday), `MEASUREMENT` (days in month/year).
- Holiday sensor exposes enum state (`none`, `ramadan`, …) with localized `names` attribute when multiple observances apply.

## [0.1.0-beta.1] - 2026-05-17

### Added

- Hijri Calendar integration for Home Assistant 2026.3+ (Umm al-Qura via hijridate).
- Sensors: Hijri date, holiday, days in month/year.
- Binary sensors: Ramadan, Eid al-Fitr, Eid al-Adha, Hajj season.
- Services: convert_to_hijri, convert_to_gregorian, calibrate_date.
- Config flow: language (en, ar, tr), day boundary (midnight or sunset), day offset option.
- Localized holiday names/types and formatted date attributes (formatted, formatted_eastern).
- HACS custom repository support.
