# Hijri Calendar

Home Assistant custom integration for the Islamic (Hijri) calendar using the [Umm al-Qura](https://hijridate.readthedocs.io/) calendar via [hijridate](https://pypi.org/project/hijridate/).

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![homeassistant](https://img.shields.io/badge/Home%20Assistant-2026.3.0+-blue.svg)](https://www.home-assistant.io/)
[![quality scale](https://img.shields.io/badge/quality%20scale-platinum-99d0ff.svg)](https://www.home-assistant.io/docs/quality_scale/)

## Features

- **Sensors**: current Hijri date (with attributes), active holidays, days in month/year, days until Ramadan/Eid (disabled by default)
- **Binary sensors**: Ramadan, Eid al-Fitr, Eid al-Adha, Hajj season
- **Calendar**: Observances, Islamic history, and month-starts calendars with localized descriptions and reference links
- **Services**: convert between Hijri and Gregorian, calibrate day offset (relative ±2 or announced Hijri date), set day offset directly
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

HACS installs from published **GitHub releases** (`hijri_calendar.zip`), not the default branch. Enable **Show beta versions** in HACS settings to see pre-releases such as `v0.1.0-beta.x`.

### Manual

Copy `custom_components/hijri_calendar` into your Home Assistant `custom_components` folder and restart Home Assistant.

## Configuration

1. Go to **Settings → Devices & services → Add integration**.
2. Search for **Hijri Calendar**.
3. Choose:
   - **Language** — integration UI, holiday names, calendar descriptions, and formatted date text (see [Supported languages](#supported-languages) below)
   - **Day boundary**: local midnight or after sunset

The Hijri date sensor state stays in ISO format (`1446-10-15`) for automations. For display, use attributes:

- `formatted` — localized date with Western digits (e.g. `15 Shawwal 1446 AH` or `15 شوال 1446 هـ`)
- `formatted_eastern` — same text with Eastern Arabic numerals (e.g. `١٥ شوال ١٤٤٦ هـ`)

### Options

- **Day offset** (−2 to +2): shift displayed dates when your locality announces a different day than Umm al-Qura. Use the `calibrate_date` service to adjust by ±2 days or from the announced Hijri date for today.
- **Observances calendar language** and **Islamic history calendar language**: show each calendar's event titles and descriptions in the integration language (default) or Arabic. Reference links match the selected calendar language.
- **Month starts calendar language**: show month-start event text in the integration language (default) or any supported integration language. Reference links match the selected calendar language.

### Supported languages

The integration supports **20** [Home Assistant language codes](https://developers.home-assistant.io/docs/translations/):

| Code | Language | Hijri month/day names in date attributes |
|------|----------|------------------------------------------|
| `en` | English | English (hijridate) |
| `ar` | Arabic | Arabic (hijridate) |
| `bn` | Bengali | Bengali (hijridate) |
| `tr` | Turkish | Turkish (hijridate) |
| `de` | German | English fallback |
| `es` | Spanish | English fallback |
| `fr` | French | English fallback |
| `it` | Italian | English fallback |
| `nl` | Dutch | English fallback |
| `pl` | Polish | English fallback |
| `pt` | Portuguese | English fallback |
| `pt-BR` | Portuguese (Brazil) | English fallback |
| `ru` | Russian | English fallback |
| `uk` | Ukrainian | English fallback |
| `zh-Hans` | Chinese (Simplified) | English fallback |
| `ja` | Japanese | English fallback |
| `ko` | Korean | English fallback |
| `he` | Hebrew | English fallback |
| `fa` | Persian | English fallback |
| `id` | Indonesian | English fallback |

Holiday names, config flow labels, service text, and calendar event descriptions are fully localized for every language above. The [hijridate](https://hijridate.readthedocs.io/) library only provides native Hijri/Gregorian month and day names for `en`, `ar`, `bn`, and `tr`. For all other integration languages, `sensor.hijri_date` attributes such as `month_name` and `formatted` use **English** month names while the rest of the UI stays localized.

Eastern Arabic numerals in `formatted_eastern` apply when the integration language is `ar` only.

## Entities

| Entity | Description |
|--------|-------------|
| `sensor.hijri_date` | Today's Hijri date (ISO state; attributes include `formatted`, `formatted_eastern`, names) |
| `sensor.holiday` | Primary active holiday id (`none`, `ramadan`, …; UI label via entity translations). Use `ids`, `names`, and `types` when multiple holidays apply |
| `sensor.days_until_ramadan` | Days until 1 Ramadan (disabled by default) |
| `sensor.days_until_eid_al_fitr` | Days until 1 Shawwal / Eid al-Fitr (disabled by default) |
| `binary_sensor.ramadan` | On during Ramadan |
| `binary_sensor.eid_al_fitr` | On on 1 Shawwal |
| `binary_sensor.eid_al_adha` | On on 10 Dhul Hijjah |
| `binary_sensor.hajj_season` | On during Hajj days 8–13 |
| `calendar.hijri_events` | Religious observances (Ramadan/Hajj spans, Eids, Ashura, Laylat al-Qadr, and more) |
| `calendar.islamic_history` | Curated Islamic milestones and conquests (recurring Hijri anniversaries) |
| `calendar.hijri_month_starts` | First day of each Hijri month (12 events per Hijri year) |

### Calendars

Three calendar entities appear in **Settings → Devices & services → Calendar**, the Calendar dashboard, and `calendar.get_events` automations. All use the same Umm al-Qura rules, **day offset**, and **day boundary** as the sensors.

**Observances** (`calendar.hijri_events`):

- **Ramadan** and **Hajj season** show as single multi-day all-day entries.
- Other observances (Eid al-Fitr, Eid al-Adha, Ashura, Islamic New Year, Laylat al-Qadr, multi-day Eids, etc.) appear on their mapped Gregorian days.
- Event details include a short description and a reference link (language follows the observances calendar language option).

**Islamic history** (`calendar.islamic_history`):

- Recurring anniversaries of curated milestones (Badr, conquest of Mecca, fall of Constantinople, and others).
- Descriptions include the original AH year and a reference link (language follows the Islamic history calendar language option).

**Month starts** (`calendar.hijri_month_starts`):

- One all-day event on the first day of each Hijri month (Muharram through Dhul Hijjah).
- Summaries use localized month names where [hijridate](https://hijridate.readthedocs.io/) provides them (`en`, `ar`, `bn`, `tr`); other calendar languages use English month names with localized template text.
- Descriptions include the AH year and a reference link (language follows the month-starts calendar language option, which supports any integration language).

**Known limitations**: Observance and history Hijri dates are indicative; scholarly sources sometimes differ (for example Laylat al-Qadr or exact battle dates). The history calendar is educational, not a scholarly authority. Umm al-Qura calculation may differ from local moon-sighting announcements—use **Day offset** or `calibrate_date` to align observances when needed.

## Data updates

This integration does not poll. A coordinator refreshes data:

- At **local midnight** every day (always).
- At **sunset** as well when **Day boundary** is set to *After sunset*.

Changing **Day offset** in options reloads the integration automatically. Entity-specific timers may also refresh state at midnight or sunset.

Domain services (`convert_to_hijri`, etc.) are registered once at startup and remain available while Home Assistant is running.

## Use cases

- Show today’s Hijri date on a dashboard using the `formatted` attribute on the Hijri date sensor.
- Automate lights, scenes, or notifications when `binary_sensor.ramadan` turns on or when the holiday sensor becomes an Eid.
- Align dates with a local moon-sighting announcement using **Day offset** and the `calibrate_date` service.
- Feed `calendar.hijri_events` into the Calendar dashboard or `calendar.get_events` automations.
- Convert arbitrary dates in scripts via `convert_to_hijri` and `convert_to_gregorian`.

## Examples

Ready-made automations are in [`blueprints/automation/`](blueprints/automation/). See [`blueprints/README.md`](blueprints/README.md) for how to import them.

| Blueprint | Purpose |
|-----------|---------|
| [ramadan_mode.yaml](blueprints/automation/hijri_calendar/ramadan_mode.yaml) | Scene or notify when Ramadan starts |
| [eid_greeting.yaml](blueprints/automation/hijri_calendar/eid_greeting.yaml) | Notify on Eid al-Fitr or Eid al-Adha |
| [hijri_new_year.yaml](blueprints/automation/hijri_calendar/hijri_new_year.yaml) | Notify on 1 Muharram |
| [daily_hijri_date.yaml](blueprints/automation/hijri_calendar/daily_hijri_date.yaml) | Daily morning Hijri date notification |
| [iftar_reminder.yaml](blueprints/automation/hijri_calendar/iftar_reminder.yaml) | Reminder before sunset during Ramadan |
| [calibrate_offset_helper.yaml](blueprints/automation/hijri_calendar/calibrate_offset_helper.yaml) | Adjust offset by −2..+2 via `calibrate_date` and notify |

### Template example

Display the localized Hijri date in a template sensor:

```yaml
template:
  - sensor:
      - name: Hijri date display
        state: "{{ state_attr('sensor.hijri_date', 'formatted') }}"
```

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

Calibrate **today** (per your day boundary) and save the integration day offset. Provide **either**:

- `offset` (−2 to +2): add to the current offset (e.g. `1` bumps the stored offset by one day).
- `hijri`: announced Hijri date for today (ISO); the service computes and saves the required offset.

```yaml
# Nudge offset by one day
service: hijri_calendar.calibrate_date
data:
  offset: 1

# Or set from the announced Hijri date
service: hijri_calendar.calibrate_date
data:
  hijri: "1446-10-15"
  language: "en"
```

### `hijri_calendar.set_day_offset`

Save a **day offset** (−2 to +2) to integration options (reloads the integration).

```yaml
service: hijri_calendar.set_day_offset
data:
  offset: 1
```

## Troubleshooting

### Hijri date does not match my local announcement

**Symptom:** The Hijri date sensor or calendar differs from your mosque or country’s announced date.

**Resolution:**

1. Call `hijri_calendar.calibrate_date` with the announced `hijri` date for today, or use `offset: 1` / `offset: -1` to nudge by a day or two.
2. Alternatively use **Settings → Devices & services → Hijri Calendar → Configure → Day offset**, or `hijri_calendar.set_day_offset` for a direct absolute offset (−2 to +2).

### Service or conversion fails with “outside the supported range”

**Symptom:** Logs or UI show `date_out_of_range`.

**Resolution:** Umm al-Qura via hijridate supports roughly 1924–2077 CE (1343–1500 AH). Pick a date inside that range.

### Sunset boundary does not work / repair issue appears

**Symptom:** With **Day boundary** set to *After sunset*, dates do not change at sunset, or **Settings → Repairs** shows a sunset warning.

**Resolution:** Set **Settings → System → General → Location** so Home Assistant can compute sunset. In polar regions where sunset is undefined, switch **Day boundary** to *Local midnight* via reconfigure.

### Calendar and sensors show different dates near sunset

**Symptom:** Around maghrib, a binary sensor has already flipped but the calendar grid for “today” still shows the previous Hijri day.

**Resolution:** Both use the same rules per Gregorian day; the calendar labels each calendar day at local midnight reference. For automations at the exact sunset transition, prefer binary sensors and the holiday sensor.

## Removing the integration

1. Go to **Settings → Devices & services**.
2. Open **Hijri Calendar**.
3. Select the menu (⋮) → **Delete**.
4. If you installed manually (not via HACS), remove `custom_components/hijri_calendar` from your config folder and restart Home Assistant.

## Known limitations

- Uses the **Umm al-Qura** calculated calendar; local moon-sighting may differ (use **Day offset**).
- Supported range: approximately 1924–2077 CE (1343–1500 AH). See [hijridate documentation](https://hijridate.readthedocs.io/).
- Sunset-based day boundary requires a valid Home Assistant location.
- Hijri month and day names in `sensor.hijri_date` attributes follow hijridate locales (`en`, `ar`, `bn`, `tr` only). Other integration languages show English month names in those attributes while UI strings remain localized.
- Eastern Arabic numerals (`formatted_eastern`) are used for integration language `ar` only.

## Disclaimer

This integration uses the official **Umm al-Qura** calculated calendar. It may differ from dates announced by local authorities based on moon sighting. Use the **day offset** option to align with your community when needed.

## Development

```bash
scripts/setup
scripts/lint
pytest tests
scripts/develop
```

### Integration quality scale

This integration targets the Home Assistant [Integration Quality Scale](https://www.home-assistant.io/docs/quality_scale/) **Platinum** tier. Progress is tracked in [`quality_scale.yaml`](custom_components/hijri_calendar/quality_scale.yaml).

### Brand assets

Edit SVG masters in `custom_components/hijri_calendar/brand/source/`, then export PNGs for Home Assistant:

```bash
scripts/build-brand
```

Requires [resvg](https://github.com/Linebender/resvg/releases) on `PATH` (Windows: extract `resvg-win64.zip`). Commit the generated files in `brand/` (`icon.png`, `logo.png`, and dark / `@2x` variants).

### Releasing

Publish a **GitHub release** (not only a tag) so the [Release workflow](.github/workflows/release.yml) attaches `hijri_calendar.zip` for HACS. Bump `version` in `custom_components/hijri_calendar/manifest.json` on `dev`/`main` when preparing the release; the workflow also sets the version inside the zip from the release tag (without the leading `v`).

## License

MIT — see [LICENSE](LICENSE).
