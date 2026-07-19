# Calendar reference links

Maintainer inventory of reference URLs used in calendar event descriptions. Each supported language has its own `calendar_content/{lang}.json` file with localized descriptions and reference links.

Source data lives in `scripts/translation_data/{lang}.yaml` under the `calendar` section. Regenerate JSON with:

```bash
python scripts/build_calendar_translations.py
```

English (`en`) generally uses Britannica articles where no localized equivalent is listed below. Other languages use Wikipedia (or equivalent) articles in that language when available.

## Observances (`calendar.hijri_events`)

| Event id | English source (example) |
|----------|--------------------------|
| `ramadan` | Britannica — Ramadan |
| `hajj_season` | Britannica — Hajj |
| `hijri_new_year` | Britannica — Islamic calendar |
| `first_day_of_ramadan` | Britannica — Ramadan |
| `laylat_al_qadr` | Britannica — Laylat al-Qadr |
| `isra_and_miraj` | Britannica — Isra and Mi'raj |
| `last_day_of_ramadan` | Britannica — Ramadan |
| `eid_al_fitr_eve` | Britannica — Eid al-Fitr |
| `eid_al_fitr` | Britannica — Eid al-Fitr |
| `eid_al_fitr_day_2` | Britannica — Eid al-Fitr |
| `eid_al_fitr_day_3` | Britannica — Eid al-Fitr |
| `day_of_arafah` | Britannica — Hajj |
| `eid_al_adha` | Britannica — Eid al-Adha |
| `eid_al_adha_day_2` | Britannica — Eid al-Adha |
| `eid_al_adha_day_3` | Britannica — Eid al-Adha |
| `eid_al_adha_day_4` | Britannica — Eid al-Adha |
| `ashura` | Britannica — Ashura |

Localized files (`ar`, `tr`, `de`, `fr`, and the other supported languages) use language-appropriate Wikipedia or equivalent articles. Review URL choices when adding or editing a locale YAML file.

## Islamic history (`calendar.islamic_history`)

| Event id | English source (example) |
|----------|--------------------------|
| `battle_of_badr` | Britannica — Battle of Badr |
| `battle_of_uhud` | Britannica — Battle of Uhud |
| `battle_of_khandaq` | Britannica — Battle of the Ditch |
| `treaty_of_hudaybiyyah` | Britannica — Treaty of al-Hudaybiyah |
| `conquest_of_khaybar` | Britannica — Khaybar |
| `conquest_of_mecca` | Britannica — Conquest of Mecca |
| `battle_of_hunayn` | Britannica — Battle of Hunayn |
| `expedition_to_tabuk` | Britannica — Tabuk |
| `battle_of_yarmouk` | Britannica — Battle of Yarmuk |
| `battle_of_qadisiyyah` | Britannica — Battle of al-Qadisiyyah |
| `conquest_of_jerusalem` | Britannica — Jerusalem |
| `conquest_of_egypt` | Britannica — Egypt |
| `fall_of_constantinople` | Britannica — Fall of Constantinople |

All 20 supported languages include name, description, and reference URL entries for every observance and history event. CI tests assert key parity across `calendar_content/*.json` files.
