> **Beta release** — enable *Show beta versions* in HACS settings to install this version.

## What's new

- **Calendar — Hijri observances** (`calendar.hijri_events`): all-day events on the Gregorian calendar for Ramadan (merged span), Hajj season (merged span), Eids, Ashura, Mawlid, and other holidays from the integration.
- Respects the same **language**, **day offset**, and **day boundary** settings as sensors (calendar mapping uses local midnight; see README for sunset caveat).
- **Sensor device classes**: Hijri date (`DATE`), holiday (`ENUM` with localized `names` when multiple apply), days in month/year (`MEASUREMENT`).

## Requirements

- Home Assistant **2026.3.0** or newer
- [HACS](https://hacs.xyz/) **2.0.5** or newer

## Installation

1. Add the custom repository in HACS (Integration) or use the README My Home Assistant badges.
2. Install or update **Hijri Calendar** and restart Home Assistant.
3. Open **Settings → Devices & services → Calendar** to use the new calendar, or add the integration if not already configured.

## Disclaimer

This integration uses the calculated **Umm al-Qura** calendar. Dates may differ from local moon-sighting announcements. Use the **day offset** option to align with your community when needed.

Full changelog: [CHANGELOG.md](https://github.com/oraad/hijri_calendar/blob/v0.1.0-beta.2/CHANGELOG.md)
