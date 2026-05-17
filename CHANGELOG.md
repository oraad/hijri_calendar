# Changelog

All notable changes to this project are documented in this file.

## [0.1.0-beta.1] - 2026-05-17

### Added

- Hijri Calendar integration for Home Assistant 2026.3+ (Umm al-Qura via hijridate).
- Sensors: Hijri date, holiday, days in month/year.
- Binary sensors: Ramadan, Eid al-Fitr, Eid al-Adha, Hajj season.
- Services: convert_to_hijri, convert_to_gregorian, calibrate_date.
- Config flow: language (en, ar, tr), day boundary (midnight or sunset), day offset option.
- Localized holiday names/types and formatted date attributes (formatted, formatted_eastern).
- HACS custom repository support.
