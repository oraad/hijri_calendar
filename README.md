# Hijri Calendar

Home Assistant custom integration for the Islamic (Hijri) calendar using the [Umm al-Qura](https://hijridate.readthedocs.io/) calendar via [hijridate](https://pypi.org/project/hijridate/).

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![homeassistant](https://img.shields.io/badge/Home%20Assistant-2026.3.0+-blue.svg)](https://www.home-assistant.io/)

## Features

- **Sensors**: current Hijri date (with attributes), active holidays, days in month/year
- **Binary sensors**: Ramadan, Eid al-Fitr, Eid al-Adha, Hajj season
- **Services**: convert between Hijri and Gregorian, calibrate with a day offset
- **Options**: configurable day offset for local moon-sighting differences
- **Day boundary**: roll the Hijri day at local midnight (default) or after sunset

## Installation

### Prerequisites

- [HACS](https://hacs.xyz/) installed
- Home Assistant **2026.3.0** or newer

### HACS (recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=oraad&repository=hijri_calendar&category=integration)

[![Open your Home Assistant instance and install this integration in HACS.](https://my.home-assistant.io/badges/hacs_integration.svg)](https://my.home-assistant.io/redirect/hacs_integration/?domain=hijri_calendar)

1. Click **Add to HACS** (first button) to open the custom repository dialog with this repo pre-filled.
2. Confirm category **Integration**, then download and install **Hijri Calendar**.
3. Or click **Install integration** (second button) if the repository is already in HACS.
4. Restart Home Assistant.
5. Go to **Settings → Devices & services → Add integration** and search for **Hijri Calendar**.

#### Manual HACS setup

If the buttons above do not work (for example, without [My Home Assistant](https://my.home-assistant.io/)):

1. Open **HACS → Integrations →** ⋮ **→ Custom repositories**.
2. Add repository URL `https://github.com/oraad/hijri_calendar` with category **Integration**.
3. Install **Hijri Calendar**, restart Home Assistant, then add the integration.

### Manual

Copy `custom_components/hijri_calendar` into your Home Assistant `custom_components` folder and restart Home Assistant.

## Configuration

1. Go to **Settings → Devices & services → Add integration**.
2. Search for **Hijri Calendar**.
3. Choose:
   - **Language** for month/day names (`en`, `ar`, `tr`)
   - **Day boundary**: local midnight or after sunset

### Options

- **Day offset** (−30 to +30): shift displayed dates when your locality announces a different day than Umm al-Qura. Use the `calibrate_date` service to find the right offset without changing options.

## Entities

| Entity | Description |
|--------|-------------|
| `sensor.hijri_date` | Today's Hijri date (ISO) with year, month, day, names |
| `sensor.holiday` | Active holidays (comma-separated ids) |
| `binary_sensor.ramadan` | On during Ramadan |
| `binary_sensor.eid_al_fitr` | On on 1 Shawwal |
| `binary_sensor.eid_al_adha` | On on 10 Dhul Hijjah |
| `binary_sensor.hajj_season` | On during Hajj days 8–13 |

## Services

### `hijri_calendar.convert_to_hijri`

Convert a Gregorian date to Hijri.

```yaml
service: hijri_calendar.convert_to_hijri
data:
  date: "2025-04-14"
  language: "ar"
```

### `hijri_calendar.convert_to_gregorian`

Convert a Hijri date (ISO `YYYY-MM-DD`) to Gregorian.

```yaml
service: hijri_calendar.convert_to_gregorian
data:
  date: "1446-10-15"
  language: "en"
```

### `hijri_calendar.calibrate_date`

Apply a day offset to a Gregorian date and return the resulting Hijri date (does not save the offset).

```yaml
service: hijri_calendar.calibrate_date
data:
  date: "2025-04-14"
  offset: 1
  language: "en"
```

## Disclaimer

This integration uses the official **Umm al-Qura** calculated calendar. It may differ from dates announced by local authorities based on moon sighting. Use the **day offset** option to align with your community when needed.

Supported date range: approximately 1924–2077 CE (1343–1500 AH). See [hijridate documentation](https://hijridate.readthedocs.io/) for details.

## Development

```bash
scripts/setup
scripts/lint
pytest tests
scripts/develop
```

## License

MIT — see [LICENSE](LICENSE).
