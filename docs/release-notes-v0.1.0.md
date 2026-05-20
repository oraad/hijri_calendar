## What's new

- **HACS zip releases**: install from published GitHub releases (`hijri_calendar.zip`).
- **Integration Quality Scale**: Platinum tier; quality tracked in `quality_scale.yaml`.
- **`calibrate_date` service**: adjust day offset by ±2 days or from the announced Hijri date for today (saves to integration options).
- **`set_day_offset` service**: set absolute day offset (−2 to +2).
- **Calendar — Hijri observances** (`calendar.hijri_events`): all-day Gregorian events for Islamic holidays.
- **Countdown sensors** (disabled by default): days until Ramadan and Eid al-Fitr.
- **Automation blueprints** in the repository for Ramadan mode, Eid greetings, daily Hijri date, iftar reminder, and offset calibration.
- **Repairs**: sunset-unavailable warning when day boundary is *After sunset*.
- **Brand assets**: updated icons and logos; trimmed transparent padding.
- **Day offset** limited to −2..+2 (config entry migration clamps legacy values).

## Requirements

- Home Assistant **2026.3.0** or newer
- [HACS](https://hacs.xyz/) **2.0.5** or newer

## Installation

1. Install or update **Hijri Calendar** in HACS and restart Home Assistant.
2. Reconfigure if you had a large day offset; migration clamps to ±2.

## Disclaimer

This integration uses the calculated **Umm al-Qura** calendar. Dates may differ from local moon-sighting announcements. Use **calibrate_date** or **Day offset** in options to align with your community when needed.

Full changelog: [CHANGELOG.md](https://github.com/oraad/hijri_calendar/blob/v0.1.0/CHANGELOG.md)
