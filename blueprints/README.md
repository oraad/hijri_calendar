# Hijri Calendar blueprints

Ready-made automations for the [Hijri Calendar](https://github.com/oraad/hijri_calendar) integration.

## Prerequisites

- Home Assistant **2026.3.0** or newer
- [Hijri Calendar](https://github.com/oraad/hijri_calendar) installed and configured

## Import a blueprint

1. Copy the YAML file URL from this repository (for example `blueprints/automation/hijri_calendar/ramadan_mode.yaml` on the `main` branch).
2. In Home Assistant go to **Settings → Automations & scenes → Blueprints**.
3. Select **Import blueprint** and paste the URL, or upload the file from disk.
4. Create an automation from the blueprint and pick your entities when prompted.

Blueprints use entity selectors so you can choose the correct Hijri Calendar entities on your instance (names may differ from the defaults in the README).

The **Calibrate offset helper** blueprint expects an `input_button` helper; create one under **Settings → Devices & services → Helpers**, then select it when configuring the automation.

For **Iftar reminder**, set **Time before sunset** to a negative offset such as `-00:15:00` for fifteen minutes before maghrib.
