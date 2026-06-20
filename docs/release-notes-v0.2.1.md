## What's changed

- **Observances calendar renamed**: `calendar.hijri_events` now displays as **Observances** (English), **المناسبات** (Arabic), and **Gözlemler** (Turkish). The entity ID is unchanged.
- **Hijra removed from Islamic history**: the `calendar.islamic_history` entry on 1 Muharram is gone so it no longer overlaps with Islamic New Year on the Observances calendar. Hijra may return later with a definitive commemoration date.

## Requirements

- Home Assistant **2026.3.0** or newer
- [HACS](https://hacs.xyz/) **2.0.5** or newer

## Installation

1. Install or update **Hijri Calendar** in HACS and restart Home Assistant.

## Disclaimer

This integration uses the calculated **Umm al-Qura** calendar. Dates may differ from local moon-sighting announcements. Use **calibrate_date** or **Day offset** in options to align with your community when needed.

Full changelog: [CHANGELOG.md](https://github.com/oraad/hijri_calendar/blob/v0.2.1/CHANGELOG.md)
