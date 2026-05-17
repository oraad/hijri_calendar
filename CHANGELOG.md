# Changelog

All notable changes to this project are documented in this file.

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
