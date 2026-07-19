# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

### Fixed

- Hassfest translation validation: month-starts calendar language selector option keys are now lowercase (`pt-br`, `zh-hans`) to satisfy translation key rules; previously stored mixed-case option values continue to resolve.
- Month-starts offset test asserted the wrong shift direction for a positive day offset.

### Changed

- Bumped ruff to 0.15.22 and applied its formatting.

## [0.3.0] - 2026-06-20

### Added

- **`calendar.hijri_month_starts`**: third calendar entity with one event on the first day of each Hijri month; calendar language can be set to any supported integration language.
- **17 new integration languages** with full UI, holiday, and calendar-content translations: Bengali, German, Spanish, Persian, French, Hebrew, Indonesian, Italian, Japanese, Korean, Dutch, Polish, Portuguese, Portuguese (Brazil), Russian, Ukrainian, and Chinese (Simplified).
- `hijridate_language()` resolver so Hijri month/day formatting uses native hijridate locales for `en`, `ar`, `bn`, and `tr`, with English fallback for all other supported languages.
- Per-language translation source in `scripts/translation_data/` and manifest drift tests to keep `SUPPORTED_LANGUAGES`, `services.yaml`, and blueprints in sync.

## [0.2.1] - 2026-05-19

### Changed

- Renamed `calendar.hijri_events` display name from "Hijri observances" to "Observances" (all languages).

### Removed

- **Hijra** milestone removed from `calendar.islamic_history` (pending a definitive commemoration date).

## [0.2.0] - 2026-05-19

### Added

- **`calendar.islamic_history`**: curated Islamic milestones and conquests with localized descriptions and per-language reference links.
- Additional **Hijri observances** on `calendar.hijri_events`: Islamic New Year, first day of Ramadan, Laylat al-Qadr, Isra and Mi'raj, multi-day Eids.
- **Calendar language options**: show observances or history calendar text in integration language or Arabic (reference URLs follow the same language).
- Event **descriptions and reference links** on all calendar entries (including Ramadan and Hajj spans).

### Removed

- **Mawlid** observance (12 Rabi I) from the holiday sensor and observances calendar.

### Changed

- Calendar event builders share `calendar_common` helpers; observance descriptions replace type-only labels.

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
