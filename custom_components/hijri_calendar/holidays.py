"""Islamic holiday detection based on Hijri calendar dates."""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Final

from hijridate import Hijri

from .helpers import gregorian_to_date, gregorian_to_hijri

HIJRI_MONTH_RAMADAN: Final = 9
HIJRI_MONTH_SHAWWAL: Final = 10
HIJRI_MONTH_DHUL_HIJJAH: Final = 12

EVENT_RAMADAN: Final = "ramadan"
EVENT_EID_AL_FITR: Final = "eid_al_fitr"
EVENT_EID_AL_ADHA: Final = "eid_al_adha"
EVENT_HAJJ_SEASON: Final = "hajj_season"

HOLIDAY_NONE: Final = "none"

HOLIDAY_RAMADAN: Final = "ramadan"
HOLIDAY_LAST_RAMADAN: Final = "last_day_of_ramadan"
HOLIDAY_EID_AL_FITR: Final = "eid_al_fitr"
HOLIDAY_EID_AL_FITR_EVE: Final = "eid_al_fitr_eve"
HOLIDAY_DAY_OF_ARAFAH: Final = "day_of_arafah"
HOLIDAY_EID_AL_ADHA: Final = "eid_al_adha"
HOLIDAY_HAJJ: Final = "hajj"
HOLIDAY_ASHURA: Final = "ashura"
HOLIDAY_HIJRI_NEW_YEAR: Final = "hijri_new_year"
HOLIDAY_FIRST_DAY_OF_RAMADAN: Final = "first_day_of_ramadan"
HOLIDAY_LAYLAT_AL_QADR: Final = "laylat_al_qadr"
HOLIDAY_ISRA_AND_MIRAJ: Final = "isra_and_miraj"
HOLIDAY_EID_AL_FITR_DAY_2: Final = "eid_al_fitr_day_2"
HOLIDAY_EID_AL_FITR_DAY_3: Final = "eid_al_fitr_day_3"
HOLIDAY_EID_AL_ADHA_DAY_2: Final = "eid_al_adha_day_2"
HOLIDAY_EID_AL_ADHA_DAY_3: Final = "eid_al_adha_day_3"
HOLIDAY_EID_AL_ADHA_DAY_4: Final = "eid_al_adha_day_4"

SPAN_RAMADAN: Final = "ramadan"
SPAN_HAJJ_SEASON: Final = "hajj_season"

TYPE_RAMADAN: Final = "ramadan"
TYPE_EID: Final = "eid"
TYPE_HAJJ: Final = "hajj"
TYPE_OTHER: Final = "other"

ALL_HOLIDAY_IDS: Final[frozenset[str]] = frozenset(
    {
        HOLIDAY_RAMADAN,
        HOLIDAY_LAST_RAMADAN,
        HOLIDAY_EID_AL_FITR_EVE,
        HOLIDAY_EID_AL_FITR,
        HOLIDAY_EID_AL_FITR_DAY_2,
        HOLIDAY_EID_AL_FITR_DAY_3,
        HOLIDAY_DAY_OF_ARAFAH,
        HOLIDAY_EID_AL_ADHA,
        HOLIDAY_EID_AL_ADHA_DAY_2,
        HOLIDAY_EID_AL_ADHA_DAY_3,
        HOLIDAY_EID_AL_ADHA_DAY_4,
        HOLIDAY_HAJJ,
        HOLIDAY_ASHURA,
        HOLIDAY_HIJRI_NEW_YEAR,
        HOLIDAY_FIRST_DAY_OF_RAMADAN,
        HOLIDAY_LAYLAT_AL_QADR,
        HOLIDAY_ISRA_AND_MIRAJ,
        HOLIDAY_NONE,
    }
)

ALL_HOLIDAY_TYPES: Final[frozenset[str]] = frozenset(
    {TYPE_RAMADAN, TYPE_EID, TYPE_HAJJ, TYPE_OTHER}
)

ALL_OBSERVANCE_CALENDAR_EVENT_IDS: Final[frozenset[str]] = frozenset(
    {
        SPAN_RAMADAN,
        SPAN_HAJJ_SEASON,
        HOLIDAY_HIJRI_NEW_YEAR,
        HOLIDAY_FIRST_DAY_OF_RAMADAN,
        HOLIDAY_LAYLAT_AL_QADR,
        HOLIDAY_ISRA_AND_MIRAJ,
        HOLIDAY_LAST_RAMADAN,
        HOLIDAY_EID_AL_FITR_EVE,
        HOLIDAY_EID_AL_FITR,
        HOLIDAY_EID_AL_FITR_DAY_2,
        HOLIDAY_EID_AL_FITR_DAY_3,
        HOLIDAY_DAY_OF_ARAFAH,
        HOLIDAY_EID_AL_ADHA,
        HOLIDAY_EID_AL_ADHA_DAY_2,
        HOLIDAY_EID_AL_ADHA_DAY_3,
        HOLIDAY_EID_AL_ADHA_DAY_4,
        HOLIDAY_ASHURA,
    }
)


@dataclass(frozen=True)
class HijriHoliday:
    """A detected Islamic holiday or observance."""

    id: str
    type: str


def get_holidays(hijri: Hijri) -> list[HijriHoliday]:  # noqa: PLR0912
    """Return holidays active on the given Hijri date."""
    holidays: list[HijriHoliday] = []
    month, day = hijri.month, hijri.day

    if month == 1 and day == 1:
        holidays.append(HijriHoliday(id=HOLIDAY_HIJRI_NEW_YEAR, type=TYPE_OTHER))

    if month == 1 and day == 10:
        holidays.append(HijriHoliday(id=HOLIDAY_ASHURA, type=TYPE_OTHER))

    if month == 7 and day == 27:
        holidays.append(HijriHoliday(id=HOLIDAY_ISRA_AND_MIRAJ, type=TYPE_OTHER))

    if month == HIJRI_MONTH_RAMADAN:
        if day == 1:
            holidays.append(
                HijriHoliday(id=HOLIDAY_FIRST_DAY_OF_RAMADAN, type=TYPE_RAMADAN)
            )
        if day == 27:
            holidays.append(HijriHoliday(id=HOLIDAY_LAYLAT_AL_QADR, type=TYPE_RAMADAN))
        holidays.append(HijriHoliday(id=HOLIDAY_RAMADAN, type=TYPE_RAMADAN))
        if day == hijri.month_length():
            holidays.append(HijriHoliday(id=HOLIDAY_LAST_RAMADAN, type=TYPE_RAMADAN))
            holidays.append(HijriHoliday(id=HOLIDAY_EID_AL_FITR_EVE, type=TYPE_EID))

    if month == HIJRI_MONTH_SHAWWAL:
        if day == 1:
            holidays.append(HijriHoliday(id=HOLIDAY_EID_AL_FITR, type=TYPE_EID))
        if day == 2:
            holidays.append(HijriHoliday(id=HOLIDAY_EID_AL_FITR_DAY_2, type=TYPE_EID))
        if day == 3:
            holidays.append(HijriHoliday(id=HOLIDAY_EID_AL_FITR_DAY_3, type=TYPE_EID))

    if month == HIJRI_MONTH_DHUL_HIJJAH:
        if day in (8, 9, 10, 11, 12, 13):
            holidays.append(HijriHoliday(id=HOLIDAY_HAJJ, type=TYPE_HAJJ))
        if day == 9:
            holidays.append(HijriHoliday(id=HOLIDAY_DAY_OF_ARAFAH, type=TYPE_HAJJ))
        if day == 10:
            holidays.append(HijriHoliday(id=HOLIDAY_EID_AL_ADHA, type=TYPE_EID))
        if day == 11:
            holidays.append(HijriHoliday(id=HOLIDAY_EID_AL_ADHA_DAY_2, type=TYPE_EID))
        if day == 12:
            holidays.append(HijriHoliday(id=HOLIDAY_EID_AL_ADHA_DAY_3, type=TYPE_EID))
        if day == 13:
            holidays.append(HijriHoliday(id=HOLIDAY_EID_AL_ADHA_DAY_4, type=TYPE_EID))

    return holidays


def get_active_events(hijri: Hijri) -> set[str]:
    """Return active event keys for binary sensors."""
    events: set[str] = set()
    month, day = hijri.month, hijri.day

    if month == HIJRI_MONTH_RAMADAN:
        events.add(EVENT_RAMADAN)

    if month == HIJRI_MONTH_SHAWWAL and day == 1:
        events.add(EVENT_EID_AL_FITR)

    if month == HIJRI_MONTH_DHUL_HIJJAH:
        if day == 10:
            events.add(EVENT_EID_AL_ADHA)
        if 8 <= day <= 13:
            events.add(EVENT_HAJJ_SEASON)

    return events


def days_until_hijri_date(
    hijri: Hijri, target_month: int, target_day: int, *, max_days: int = 400
) -> int | None:
    """Return days until the next occurrence of a Hijri month/day."""
    try:
        gregorian = gregorian_to_date(hijri.to_gregorian())
    except OverflowError, ValueError:
        return None

    for delta in range(max_days):
        candidate = gregorian_to_hijri(gregorian + dt.timedelta(days=delta))
        if candidate.month == target_month and candidate.day == target_day:
            return delta
    return None


def days_until_ramadan(hijri: Hijri) -> int | None:
    """Return days until 1 Ramadan."""
    return days_until_hijri_date(hijri, HIJRI_MONTH_RAMADAN, 1)


def days_until_eid_al_fitr(hijri: Hijri) -> int | None:
    """Return days until 1 Shawwal (Eid al-Fitr)."""
    return days_until_hijri_date(hijri, HIJRI_MONTH_SHAWWAL, 1)
