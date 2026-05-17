> **Beta release** — enable *Show beta versions* in HACS settings to install this version.

## Features

- **Hijri Calendar** custom integration using the Umm al-Qura calendar via [hijridate](https://pypi.org/project/hijridate/) 2.6.0
- **Sensors**: Hijri date (ISO state + localized `formatted` / `formatted_eastern` attributes), active holidays, days in Hijri month/year
- **Binary sensors**: Ramadan, Eid al-Fitr, Eid al-Adha, Hajj season
- **Services**: `convert_to_hijri`, `convert_to_gregorian`, `calibrate_date`
- **Configuration**: language `en` / `ar` / `tr`; day boundary at local midnight or after sunset; day offset −30 to +30
- **Localization**: holiday names and types via Home Assistant entity translations (`ar`, `en`, `tr`)
- **HACS**: add custom repository `https://github.com/oraad/hijri_calendar` (Integration category)

## Requirements

- Home Assistant **2026.3.0** or newer
- [HACS](https://hacs.xyz/) **2.0.5** or newer

## Installation

1. Add the custom repository in HACS (Integration) or use the README My Home Assistant badges.
2. Install **Hijri Calendar** and restart Home Assistant.
3. Go to **Settings → Devices & services → Add integration** and search for **Hijri Calendar**.

## Disclaimer

This integration uses the calculated **Umm al-Qura** calendar. Dates may differ from local moon-sighting announcements. Use the **day offset** option to align with your community when needed.

Full changelog: [CHANGELOG.md](https://github.com/oraad/hijri_calendar/blob/v0.1.0-beta.1/CHANGELOG.md)
