"""Merge calendar translation content into integration JSON files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components" / "hijri_calendar"
CALENDAR_CONTENT = COMPONENT / "calendar_content"

NEW_HOLIDAY_STATES = {
    "en": {
        "hijri_new_year": "Islamic New Year",
        "first_day_of_ramadan": "First day of Ramadan",
        "laylat_al_qadr": "Laylat al-Qadr",
        "isra_and_miraj": "Isra and Mi'raj",
        "eid_al_fitr_day_2": "Eid al-Fitr (day 2)",
        "eid_al_fitr_day_3": "Eid al-Fitr (day 3)",
        "eid_al_adha_day_2": "Eid al-Adha (day 2)",
        "eid_al_adha_day_3": "Eid al-Adha (day 3)",
        "eid_al_adha_day_4": "Eid al-Adha (day 4)",
    },
    "ar": {
        "hijri_new_year": "رأس السنة الهجرية",
        "first_day_of_ramadan": "أول يوم من رمضان",
        "laylat_al_qadr": "ليلة القدر",
        "isra_and_miraj": "الإسراء والمعراج",
        "eid_al_fitr_day_2": "عيد الفطر (اليوم الثاني)",
        "eid_al_fitr_day_3": "عيد الفطر (اليوم الثالث)",
        "eid_al_adha_day_2": "عيد الأضحى (اليوم الثاني)",
        "eid_al_adha_day_3": "عيد الأضحى (اليوم الثالث)",
        "eid_al_adha_day_4": "عيد الأضحى (اليوم الرابع)",
    },
    "tr": {
        "hijri_new_year": "Hicri yılbaşı",
        "first_day_of_ramadan": "Ramazan'ın ilk günü",
        "laylat_al_qadr": "Kadir Gecesi",
        "isra_and_miraj": "İsra ve Miraç",
        "eid_al_fitr_day_2": "Ramazan Bayramı (2. gün)",
        "eid_al_fitr_day_3": "Ramazan Bayramı (3. gün)",
        "eid_al_adha_day_2": "Kurban Bayramı (2. gün)",
        "eid_al_adha_day_3": "Kurban Bayramı (3. gün)",
        "eid_al_adha_day_4": "Kurban Bayramı (4. gün)",
    },
}

REFERENCE_LABEL = {"en": "Learn more", "ar": "المزيد", "tr": "Daha fazla bilgi"}

YEAR_SUFFIX = {"en": "{year} AH", "ar": "{year} هـ", "tr": "{year} H"}

OBSERVANCES: dict[str, dict[str, dict[str, str]]] = {
    "ramadan": {
        "en": {
            "description": "The ninth Hijri month of fasting, prayer, and reflection for Muslims.",
            "reference_url": "https://www.britannica.com/topic/Ramadan",
        },
        "ar": {
            "description": "الشهر الهجري التاسع للصيام والعبادة عند المسلمين.",
            "reference_url": "https://ar.wikipedia.org/wiki/رمضان",
        },
        "tr": {
            "description": "Müslümanlar için oruç, ibadet ve tefekkür ayı olan Hicri dokuzuncu ay.",
            "reference_url": "https://tr.wikipedia.org/wiki/Ramazan",
        },
    },
    "hajj_season": {
        "en": {
            "description": "The annual pilgrimage season in Dhul Hijjah, including the days of Hajj rites.",
            "reference_url": "https://www.britannica.com/topic/hajj",
        },
        "ar": {
            "description": "موسم الحج السنوي في ذي الحجة ويشمل أيام مناسك الحج.",
            "reference_url": "https://ar.wikipedia.org/wiki/الحج",
        },
        "tr": {
            "description": "Zilhicce ayında yıllık hac ibadeti ve hac menasik günleri.",
            "reference_url": "https://tr.wikipedia.org/wiki/Hac",
        },
    },
    "hijri_new_year": {
        "en": {
            "description": "The first day of Muharram marks the beginning of the Islamic Hijri year.",
            "reference_url": "https://www.britannica.com/topic/Islamic-calendar",
        },
        "ar": {
            "description": "أول محرم يمثل بداية السنة الهجرية.",
            "reference_url": "https://ar.wikipedia.org/wiki/التقويم_الهجري",
        },
        "tr": {
            "description": "Muharrem'in birinci günü Hicri yılın başlangıcıdır.",
            "reference_url": "https://tr.wikipedia.org/wiki/Hicri_takvim",
        },
    },
    "first_day_of_ramadan": {
        "en": {
            "description": "The first day of Ramadan when the month of fasting begins.",
            "reference_url": "https://www.britannica.com/topic/Ramadan",
        },
        "ar": {
            "description": "أول أيام شهر رمضان وبدء الصيام.",
            "reference_url": "https://ar.wikipedia.org/wiki/رمضان",
        },
        "tr": {
            "description": "Ramazan orucunun başladığı ilk gün.",
            "reference_url": "https://tr.wikipedia.org/wiki/Ramazan",
        },
    },
    "laylat_al_qadr": {
        "en": {
            "description": "The Night of Decree, widely observed on the 27th of Ramadan.",
            "reference_url": "https://www.britannica.com/topic/Laylat-al-Qadr",
        },
        "ar": {
            "description": "ليلة القدر، ويُحتفل بها غالبًا في 27 رمضان.",
            "reference_url": "https://ar.wikipedia.org/wiki/ليلة_القدر",
        },
        "tr": {
            "description": "Kadir Gecesi; genellikle Ramazan'ın 27. gecesi anılır.",
            "reference_url": "https://tr.wikipedia.org/wiki/Kadir_Gecesi",
        },
    },
    "isra_and_miraj": {
        "en": {
            "description": "Commemorates the night journey and ascension, observed on 27 Rajab.",
            "reference_url": "https://www.britannica.com/topic/Isra-and-Miraj",
        },
        "ar": {
            "description": "ذكرى الإسراء بالنبي والمعراج في 27 رجب.",
            "reference_url": "https://ar.wikipedia.org/wiki/الإسراء_والمعراج",
        },
        "tr": {
            "description": "Receb'in 27'sinde anılan İsra ve Miraç miracı.",
            "reference_url": "https://tr.wikipedia.org/wiki/İsra_ve_Miraç",
        },
    },
    "last_day_of_ramadan": {
        "en": {
            "description": "The final day of Ramadan before Eid al-Fitr.",
            "reference_url": "https://www.britannica.com/topic/Ramadan",
        },
        "ar": {
            "description": "آخر يوم من شهر رمضان قبل عيد الفطر.",
            "reference_url": "https://ar.wikipedia.org/wiki/رمضان",
        },
        "tr": {
            "description": "Ramazan Bayramı'ndan önceki Ramazan'ın son günü.",
            "reference_url": "https://tr.wikipedia.org/wiki/Ramazan",
        },
    },
    "eid_al_fitr_eve": {
        "en": {
            "description": "The eve of Eid al-Fitr at the end of Ramadan.",
            "reference_url": "https://www.britannica.com/topic/Eid-al-Fitr",
        },
        "ar": {
            "description": "ليلة عيد الفطر في آخر أيام رمضان.",
            "reference_url": "https://ar.wikipedia.org/wiki/عيد_الفطر",
        },
        "tr": {
            "description": "Ramazan Bayramı'nın arefesi.",
            "reference_url": "https://tr.wikipedia.org/wiki/Ramazan_Bayramı",
        },
    },
    "eid_al_fitr": {
        "en": {
            "description": "Festival marking the end of Ramadan on 1 Shawwal.",
            "reference_url": "https://www.britannica.com/topic/Eid-al-Fitr",
        },
        "ar": {
            "description": "عيد الفطر في أول شوال يختم رمضان.",
            "reference_url": "https://ar.wikipedia.org/wiki/عيد_الفطر",
        },
        "tr": {
            "description": "Şevval'in birinde kutlanan Ramazan Bayramı.",
            "reference_url": "https://tr.wikipedia.org/wiki/Ramazan_Bayramı",
        },
    },
    "eid_al_fitr_day_2": {
        "en": {
            "description": "The second day of Eid al-Fitr celebrations.",
            "reference_url": "https://www.britannica.com/topic/Eid-al-Fitr",
        },
        "ar": {
            "description": "اليوم الثاني من عيد الفطر.",
            "reference_url": "https://ar.wikipedia.org/wiki/عيد_الفطر",
        },
        "tr": {
            "description": "Ramazan Bayramı'nın ikinci günü.",
            "reference_url": "https://tr.wikipedia.org/wiki/Ramazan_Bayramı",
        },
    },
    "eid_al_fitr_day_3": {
        "en": {
            "description": "The third day of Eid al-Fitr celebrations.",
            "reference_url": "https://www.britannica.com/topic/Eid-al-Fitr",
        },
        "ar": {
            "description": "اليوم الثالث من عيد الفطر.",
            "reference_url": "https://ar.wikipedia.org/wiki/عيد_الفطر",
        },
        "tr": {
            "description": "Ramazan Bayramı'nın üçüncü günü.",
            "reference_url": "https://tr.wikipedia.org/wiki/Ramazan_Bayramı",
        },
    },
    "day_of_arafah": {
        "en": {
            "description": "The day of standing at Arafah during Hajj on 9 Dhul Hijjah.",
            "reference_url": "https://www.britannica.com/topic/hajj",
        },
        "ar": {
            "description": "يوم الوقوف بعرفة في الحج في 9 ذي الحجة.",
            "reference_url": "https://ar.wikipedia.org/wiki/يوم_عرفة",
        },
        "tr": {
            "description": "Hac'da Arafat vakfesi günü (9 Zilhicce).",
            "reference_url": "https://tr.wikipedia.org/wiki/Arafat",
        },
    },
    "eid_al_adha": {
        "en": {
            "description": "Festival of Sacrifice on 10 Dhul Hijjah.",
            "reference_url": "https://www.britannica.com/topic/Eid-al-Adha",
        },
        "ar": {
            "description": "عيد الأضحى في 10 ذي الحجة.",
            "reference_url": "https://ar.wikipedia.org/wiki/عيد_الأضحى",
        },
        "tr": {
            "description": "10 Zilhicce'de kutlanan Kurban Bayramı.",
            "reference_url": "https://tr.wikipedia.org/wiki/Kurban_Bayramı",
        },
    },
    "eid_al_adha_day_2": {
        "en": {
            "description": "The second day of Eid al-Adha.",
            "reference_url": "https://www.britannica.com/topic/Eid-al-Adha",
        },
        "ar": {
            "description": "اليوم الثاني من عيد الأضحى.",
            "reference_url": "https://ar.wikipedia.org/wiki/عيد_الأضحى",
        },
        "tr": {
            "description": "Kurban Bayramı'nın ikinci günü.",
            "reference_url": "https://tr.wikipedia.org/wiki/Kurban_Bayramı",
        },
    },
    "eid_al_adha_day_3": {
        "en": {
            "description": "The third day of Eid al-Adha.",
            "reference_url": "https://www.britannica.com/topic/Eid-al-Adha",
        },
        "ar": {
            "description": "اليوم الثالث من عيد الأضحى.",
            "reference_url": "https://ar.wikipedia.org/wiki/عيد_الأضحى",
        },
        "tr": {
            "description": "Kurban Bayramı'nın üçüncü günü.",
            "reference_url": "https://tr.wikipedia.org/wiki/Kurban_Bayramı",
        },
    },
    "eid_al_adha_day_4": {
        "en": {
            "description": "The fourth day of Eid al-Adha and the end of the Hajj season rites.",
            "reference_url": "https://www.britannica.com/topic/Eid-al-Adha",
        },
        "ar": {
            "description": "اليوم الرابع من عيد الأضحى وختام أيام مناسك الحج.",
            "reference_url": "https://ar.wikipedia.org/wiki/عيد_الأضحى",
        },
        "tr": {
            "description": "Kurban Bayramı'nın dördüncü günü ve hac menasik sonu.",
            "reference_url": "https://tr.wikipedia.org/wiki/Kurban_Bayramı",
        },
    },
    "ashura": {
        "en": {
            "description": "Observed on 10 Muharram, especially significant for fasting and remembrance.",
            "reference_url": "https://www.britannica.com/topic/Ashura",
        },
        "ar": {
            "description": "يُحتفل به في 10 محرم وله صيام وذكرى تاريخية.",
            "reference_url": "https://ar.wikipedia.org/wiki/عاشوراء",
        },
        "tr": {
            "description": "Muharrem'in 10'unda anılan Aşure günü.",
            "reference_url": "https://tr.wikipedia.org/wiki/Aşure_Günü",
        },
    },
}

HISTORY: dict[str, dict[str, dict[str, str]]] = {
    "hijra": {
        "en": {
            "name": "Hijra",
            "description": "The migration from Mecca to Medina that marks year 1 AH.",
            "reference_url": "https://www.britannica.com/event/Hijrah",
        },
        "ar": {
            "name": "الهجرة",
            "description": "هجرة النبي من مكة إلى المدينة وبداية التقويم الهجري.",
            "reference_url": "https://ar.wikipedia.org/wiki/الهجرة_النبوية",
        },
        "tr": {
            "name": "Hicret",
            "description": "1. Hicri yılın başlangıcı sayılan Mekke'den Medine'ye hicret.",
            "reference_url": "https://tr.wikipedia.org/wiki/Hicret",
        },
    },
    "battle_of_badr": {
        "en": {
            "name": "Battle of Badr",
            "description": "The first major battle between Muslims and Quraysh in 2 AH.",
            "reference_url": "https://www.britannica.com/event/Battle-of-Badr",
        },
        "ar": {
            "name": "غزوة بدر",
            "description": "أول معركة فاصلة بين المسلمين وقريش في 2 هـ.",
            "reference_url": "https://ar.wikipedia.org/wiki/غزوة_بدر",
        },
        "tr": {
            "name": "Bedir Savaşı",
            "description": "2. yılda Müslümanlar ile Kureyş arasındaki ilk büyük savaş.",
            "reference_url": "https://tr.wikipedia.org/wiki/Bedir_Savaşı",
        },
    },
    "battle_of_uhud": {
        "en": {
            "name": "Battle of Uhud",
            "description": "A battle fought near Mount Uhud in 3 AH.",
            "reference_url": "https://www.britannica.com/event/Battle-of-Uhud",
        },
        "ar": {
            "name": "غزوة أحد",
            "description": "معركة وقعت عند جبل أحد في 3 هـ.",
            "reference_url": "https://ar.wikipedia.org/wiki/غزوة_أحد",
        },
        "tr": {
            "name": "Uhud Savaşı",
            "description": "3. yılda Uhud Dağı yakınında yapılan savaş.",
            "reference_url": "https://tr.wikipedia.org/wiki/Uhud_Savaşı",
        },
    },
    "battle_of_khandaq": {
        "en": {
            "name": "Battle of the Trench",
            "description": "The confederates' siege of Medina in 5 AH.",
            "reference_url": "https://www.britannica.com/event/Battle-of-the-Ditch",
        },
        "ar": {
            "name": "غزوة الخندق",
            "description": "حصار الأحزاب للمدينة في 5 هـ.",
            "reference_url": "https://ar.wikipedia.org/wiki/غزوة_الخندق",
        },
        "tr": {
            "name": "Hendek Savaşı",
            "description": "5. yılda Medine kuşatması (Hendek).",
            "reference_url": "https://tr.wikipedia.org/wiki/Hendek_Savaşı",
        },
    },
    "treaty_of_hudaybiyyah": {
        "en": {
            "name": "Treaty of Hudaybiyyah",
            "description": "A peace agreement between Muslims and Quraysh in 6 AH.",
            "reference_url": "https://www.britannica.com/topic/Treaty-of-al-Hudaybiyah",
        },
        "ar": {
            "name": "صلح الحديبية",
            "description": "اتفاق سلام بين المسلمين وقريش في 6 هـ.",
            "reference_url": "https://ar.wikipedia.org/wiki/صلح_الحديبية",
        },
        "tr": {
            "name": "Hudeybiye Antlaşması",
            "description": "6. yılda Müslümanlar ile Kureyş arasındaki barış antlaşması.",
            "reference_url": "https://tr.wikipedia.org/wiki/Hudeybiye_Antlaşması",
        },
    },
    "conquest_of_khaybar": {
        "en": {
            "name": "Conquest of Khaybar",
            "description": "Muslim campaign against Khaybar fortresses in 7 AH.",
            "reference_url": "https://www.britannica.com/place/Khaybar",
        },
        "ar": {
            "name": "فتح خيبر",
            "description": "فتح حصون خيبر في 7 هـ.",
            "reference_url": "https://ar.wikipedia.org/wiki/غزوة_خيبر",
        },
        "tr": {
            "name": "Hayber'in Fethi",
            "description": "7. yılda Hayber kalelerinin fethi.",
            "reference_url": "https://tr.wikipedia.org/wiki/Hayber",
        },
    },
    "conquest_of_mecca": {
        "en": {
            "name": "Conquest of Mecca",
            "description": "The peaceful opening of Mecca in 8 AH.",
            "reference_url": "https://www.britannica.com/event/Conquest-of-Mecca",
        },
        "ar": {
            "name": "فتح مكة",
            "description": "فتح مكة في 8 هـ.",
            "reference_url": "https://ar.wikipedia.org/wiki/فتح_مكة",
        },
        "tr": {
            "name": "Mekke'nin Fethi",
            "description": "8. yılda Mekke'nin fethedilmesi.",
            "reference_url": "https://tr.wikipedia.org/wiki/Mekke%27nin_Fethi",
        },
    },
    "battle_of_hunayn": {
        "en": {
            "name": "Battle of Hunayn",
            "description": "A battle fought after the conquest of Mecca in 8 AH.",
            "reference_url": "https://www.britannica.com/event/Battle-of-Hunayn",
        },
        "ar": {
            "name": "غزوة حنين",
            "description": "معركة حنين بعد فتح مكة في 8 هـ.",
            "reference_url": "https://ar.wikipedia.org/wiki/غزوة_حنين",
        },
        "tr": {
            "name": "Huneyn Savaşı",
            "description": "Mekke fethinden sonra 8. yılda Huneyn Savaşı.",
            "reference_url": "https://tr.wikipedia.org/wiki/Huneyn_Savaşı",
        },
    },
    "expedition_to_tabuk": {
        "en": {
            "name": "Expedition to Tabuk",
            "description": "The Tabuk campaign in 9 AH.",
            "reference_url": "https://www.britannica.com/place/Tabuk-Saudi-Arabia",
        },
        "ar": {
            "name": "غزوة تبوك",
            "description": "غزوة تبوك في 9 هـ.",
            "reference_url": "https://ar.wikipedia.org/wiki/غزوة_تبوك",
        },
        "tr": {
            "name": "Tebük Seferi",
            "description": "9. yıldaki Tebük seferi.",
            "reference_url": "https://tr.wikipedia.org/wiki/Tebük_Seferi",
        },
    },
    "battle_of_yarmouk": {
        "en": {
            "name": "Battle of Yarmouk",
            "description": "A decisive battle against Byzantine forces in 15 AH.",
            "reference_url": "https://www.britannica.com/event/Battle-of-Yarmuk",
        },
        "ar": {
            "name": "معركة اليرموك",
            "description": "معركة فاصلة ضد البيزنطيين في 15 هـ.",
            "reference_url": "https://ar.wikipedia.org/wiki/معركة_اليرموك",
        },
        "tr": {
            "name": "Yermük Savaşı",
            "description": "15. yılda Bizans'a karşı Yermük Savaşı.",
            "reference_url": "https://tr.wikipedia.org/wiki/Yermük_Savaşı",
        },
    },
    "battle_of_qadisiyyah": {
        "en": {
            "name": "Battle of al-Qadisiyyah",
            "description": "A major battle opening Iraq to Muslim forces in 15 AH.",
            "reference_url": "https://www.britannica.com/event/Battle-of-Al-Qadisiyyah",
        },
        "ar": {
            "name": "معركة القادسية",
            "description": "معركة فتح العراق في 15 هـ.",
            "reference_url": "https://ar.wikipedia.org/wiki/معركة_القادسية",
        },
        "tr": {
            "name": "Kadisiye Savaşı",
            "description": "15. yılda Kadisiye Savaşı.",
            "reference_url": "https://tr.wikipedia.org/wiki/Kadisiye_Savaşı",
        },
    },
    "conquest_of_jerusalem": {
        "en": {
            "name": "Conquest of Jerusalem",
            "description": "The Muslim entry into Jerusalem in 17 AH.",
            "reference_url": "https://www.britannica.com/place/Jerusalem",
        },
        "ar": {
            "name": "فتح القدس",
            "description": "دخول المسلمين القدس في 17 هـ.",
            "reference_url": "https://ar.wikipedia.org/wiki/فتح_بيت_المقدس",
        },
        "tr": {
            "name": "Kudüs'ün Fethi",
            "description": "17. yılda Kudüs'ün fethi.",
            "reference_url": "https://tr.wikipedia.org/wiki/Kudüs",
        },
    },
    "conquest_of_egypt": {
        "en": {
            "name": "Conquest of Egypt",
            "description": "The Muslim expansion into Egypt in 21 AH.",
            "reference_url": "https://www.britannica.com/place/Egypt",
        },
        "ar": {
            "name": "فتح مصر",
            "description": "الفتح الإسلامي لمصر في 21 هـ.",
            "reference_url": "https://ar.wikipedia.org/wiki/الفتح_الإسلامي_لمصر",
        },
        "tr": {
            "name": "Mısır'ın Fethi",
            "description": "21. yılda Mısır'ın fethi.",
            "reference_url": "https://tr.wikipedia.org/wiki/Mısır",
        },
    },
    "fall_of_constantinople": {
        "en": {
            "name": "Fall of Constantinople",
            "description": "The Ottoman conquest of Constantinople in 857 AH.",
            "reference_url": "https://www.britannica.com/event/Fall-of-Constantinople-1453",
        },
        "ar": {
            "name": "فتح القسطنطينية",
            "description": "فتح القسطنطينية في 857 هـ.",
            "reference_url": "https://ar.wikipedia.org/wiki/فتح_القسطنطينية",
        },
        "tr": {
            "name": "İstanbul'un Fethi",
            "description": "857. yılda İstanbul'un fethi.",
            "reference_url": "https://tr.wikipedia.org/wiki/İstanbul%27un_Fethi",
        },
    },
}


def _observance_sections(lang: str) -> dict[str, dict[str, str]]:
    descriptions: dict[str, str] = {}
    urls: dict[str, str] = {}
    for event_id, locales in OBSERVANCES.items():
        descriptions[event_id] = locales[lang]["description"]
        urls[event_id] = locales[lang]["reference_url"]
    return {"description": descriptions, "reference_url": urls}


def _history_sections(lang: str) -> dict[str, Any]:
    names: dict[str, str] = {}
    descriptions: dict[str, str] = {}
    urls: dict[str, str] = {}
    for event_id, locales in HISTORY.items():
        names[event_id] = locales[lang]["name"]
        descriptions[event_id] = locales[lang]["description"]
        urls[event_id] = locales[lang]["reference_url"]
    return {
        "name": "Islamic history"
        if lang == "en"
        else ("التاريخ الإسلامي" if lang == "ar" else "İslam tarihi"),
        "event_name": names,
        "description": descriptions,
        "reference_url": urls,
        "year_suffix": YEAR_SUFFIX[lang],
    }


def _patch_file(path: Path, lang: str) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    holiday_state = data["entity"]["sensor"]["holiday"]["state"]
    holiday_state.pop("mawlid", None)
    holiday_state.update(NEW_HOLIDAY_STATES[lang])

    calendar = data.setdefault("entity", {}).setdefault("calendar", {})
    calendar.pop("reference_label", None)
    calendar["hijri_events"] = {
        "name": calendar.get("hijri_events", {}).get("name", "Hijri observances"),
    }
    history = _history_sections(lang)
    calendar["islamic_history"] = {"name": history.pop("name")}
    data.pop("calendar_content", None)
    CALENDAR_CONTENT.mkdir(exist_ok=True)
    (CALENDAR_CONTENT / f"{lang}.json").write_text(
        json.dumps(
            {
                "reference_label": REFERENCE_LABEL[lang],
                "hijri_events": _observance_sections(lang),
                "islamic_history": history,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    options_data = (
        data.setdefault("options", {})
        .setdefault("step", {})
        .setdefault("init", {})
        .setdefault("data", {})
    )
    options_data["observances_calendar_language"] = (
        "Observances calendar language"
        if lang == "en"
        else "لغة تقويم المناسبات"
        if lang == "ar"
        else "Gözlem takvimi dili"
    )
    options_data["islamic_history_calendar_language"] = (
        "Islamic history calendar language"
        if lang == "en"
        else "لغة تقويم التاريخ الإسلامي"
        if lang == "ar"
        else "İslam tarihi takvimi dili"
    )

    selector = data.setdefault("selector", {})
    selector["observances_calendar_language"] = {
        "options": {
            "default": (
                "Integration language"
                if lang == "en"
                else "لغة التكامل"
                if lang == "ar"
                else "Entegrasyon dili"
            ),
            "ar": "العربية" if lang != "tr" else "Arapça",
        }
    }
    selector["islamic_history_calendar_language"] = selector[
        "observances_calendar_language"
    ]

    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    _patch_file(COMPONENT / "strings.json", "en")
    _patch_file(COMPONENT / "translations" / "en.json", "en")
    _patch_file(COMPONENT / "translations" / "ar.json", "ar")
    _patch_file(COMPONENT / "translations" / "tr.json", "tr")


if __name__ == "__main__":
    main()
