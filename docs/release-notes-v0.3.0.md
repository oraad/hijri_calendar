## What's new

- **`calendar.hijri_month_starts`**: third calendar entity with one all-day event on the first day of each Hijri month (Muharram through Dhul Hijjah). Summaries use localized month names where [hijridate](https://hijridate.readthedocs.io/) provides them (`en`, `ar`, `bn`, `tr`); other languages use English month names with localized template text.
- **Month starts calendar language**: choose integration language (default) or any of the 20 supported integration languages for event titles, descriptions, and reference links.
- **17 new integration languages**: Bengali, German, Spanish, Persian, French, Hebrew, Indonesian, Italian, Japanese, Korean, Dutch, Polish, Portuguese, Portuguese (Brazil), Russian, Ukrainian, and Chinese (Simplified) — full UI, holiday, and calendar-content translations.
- **`hijridate_language()` resolver**: Hijri month/day formatting uses native hijridate locales for `en`, `ar`, `bn`, and `tr`, with English fallback for all other supported languages.
- **Translation build pipeline**: per-language source in `scripts/translation_data/` with manifest drift tests to keep languages, services, and blueprints in sync.

## Requirements

- Home Assistant **2026.3.0** or newer
- [HACS](https://hacs.xyz/) **2.0.5** or newer

## Installation

1. Install or update **Hijri Calendar** in HACS and restart Home Assistant.
2. Open integration options to set **Month starts calendar language** if you want a language other than your integration default.

## Disclaimer

This integration uses the calculated **Umm al-Qura** calendar. Dates may differ from local moon-sighting announcements. Use **calibrate_date** or **Day offset** in options to align with your community when needed.

Full changelog: [CHANGELOG.md](https://github.com/oraad/hijri_calendar/blob/v0.3.0/CHANGELOG.md)
