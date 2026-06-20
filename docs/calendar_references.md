# Calendar reference links

Maintainer inventory of reference URLs used in calendar event descriptions. Each event has distinct URLs in `strings.json`, `en.json`, `ar.json`, and `tr.json` under `calendar_content`.

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

Arabic and Turkish files use Wikipedia (or equivalent) articles in those languages.

## Islamic history (`calendar.islamic_history`)

| Event id | English source (example) |
|----------|--------------------------|
| `hijra` | Britannica — Hijrah |
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

Regenerate translation JSON from [`scripts/build_calendar_translations.py`](../scripts/build_calendar_translations.py) after editing URL or description source data in that script.
