"""Islamic holiday detection based on Hijri calendar dates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from hijridate import Hijri

HIJRI_MONTH_RAMADAN: Final = 9
HIJRI_MONTH_SHAWWAL: Final = 10
HIJRI_MONTH_DHUL_HIJJAH: Final = 12

EVENT_RAMADAN: Final = "ramadan"
EVENT_EID_AL_FITR: Final = "eid_al_fitr"
EVENT_EID_AL_ADHA: Final = "eid_al_adha"
EVENT_HAJJ_SEASON: Final = "hajj_season"

HOLIDAY_RAMADAN: Final = "ramadan"
HOLIDAY_LAST_RAMADAN: Final = "last_day_of_ramadan"
HOLIDAY_EID_AL_FITR: Final = "eid_al_fitr"
HOLIDAY_EID_AL_FITR_EVE: Final = "eid_al_fitr_eve"
HOLIDAY_DAY_OF_ARAFAH: Final = "day_of_arafah"
HOLIDAY_EID_AL_ADHA: Final = "eid_al_adha"
HOLIDAY_HAJJ: Final = "hajj"
HOLIDAY_ASHURA: Final = "ashura"
HOLIDAY_MAWLID: Final = "mawlid"


@dataclass(frozen=True)
class HijriHoliday:
    """A detected Islamic holiday or observance."""

    id: str
    type: str


def get_holidays(hijri: Hijri) -> list[HijriHoliday]:
    """Return holidays active on the given Hijri date."""
    holidays: list[HijriHoliday] = []
    month, day = hijri.month, hijri.day

    if month == HIJRI_MONTH_RAMADAN:
        holidays.append(HijriHoliday(id=HOLIDAY_RAMADAN, type="ramadan"))
        if day == hijri.month_length():
            holidays.append(HijriHoliday(id=HOLIDAY_LAST_RAMADAN, type="ramadan"))
            holidays.append(HijriHoliday(id=HOLIDAY_EID_AL_FITR_EVE, type="eid"))

    if month == HIJRI_MONTH_SHAWWAL and day == 1:
        holidays.append(HijriHoliday(id=HOLIDAY_EID_AL_FITR, type="eid"))

    if month == 1 and day == 10:
        holidays.append(HijriHoliday(id=HOLIDAY_ASHURA, type="other"))

    if month == 3 and day == 12:
        holidays.append(HijriHoliday(id=HOLIDAY_MAWLID, type="other"))

    if month == HIJRI_MONTH_DHUL_HIJJAH:
        if day in (8, 9, 10, 11, 12, 13):
            holidays.append(HijriHoliday(id=HOLIDAY_HAJJ, type="hajj"))
        if day == 9:
            holidays.append(HijriHoliday(id=HOLIDAY_DAY_OF_ARAFAH, type="hajj"))
        if day == 10:
            holidays.append(HijriHoliday(id=HOLIDAY_EID_AL_ADHA, type="eid"))

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
