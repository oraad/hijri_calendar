## What's new

- **`calendar.islamic_history`**: second calendar entity with curated Islamic milestones (Hijra, Badr, conquest of Mecca, Constantinople, and more), recurring on Hijri month/day with AH year in each description.
- **Expanded `calendar.hijri_events`**: Islamic New Year, first day of Ramadan, Laylat al-Qadr, Isra and Mi'raj, multi-day Eid spans, plus descriptions and reference links on every entry (including Ramadan and Hajj seasons).
- **Per-calendar language options**: show observances or history calendar text in your integration language or force Arabic (reference URLs follow the same language).
- **Localized descriptions and links**: English, Arabic, and Turkish text with per-language reference URLs on all calendar events.

## Removed

- **Mawlid** (12 Rabi I) removed from the holiday sensor and observances calendar.

## Requirements

- Home Assistant **2026.3.0** or newer
- [HACS](https://hacs.xyz/) **2.0.5** or newer

## Installation

1. Install or update **Hijri Calendar** in HACS and restart Home Assistant.
2. Open integration options to set **Observances calendar language** and **Islamic history calendar language** if you want Arabic text and links on either calendar.

## Disclaimer

This integration uses the calculated **Umm al-Qura** calendar. Dates may differ from local moon-sighting announcements. Use **calibrate_date** or **Day offset** in options to align with your community when needed.

Full changelog: [CHANGELOG.md](https://github.com/oraad/hijri_calendar/blob/v0.2.0/CHANGELOG.md)
