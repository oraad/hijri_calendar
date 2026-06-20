"""Test holiday detection."""

from hijridate import Hijri

from custom_components.hijri_calendar.holidays import (
    EVENT_EID_AL_FITR,
    EVENT_RAMADAN,
    HOLIDAY_EID_AL_FITR,
    HOLIDAY_EID_AL_FITR_DAY_2,
    HOLIDAY_HIJRI_NEW_YEAR,
    HOLIDAY_LAYLAT_AL_QADR,
    HOLIDAY_RAMADAN,
    get_active_events,
    get_holidays,
)


def test_ramadan_holiday() -> None:
    """Test Ramadan is detected."""
    hijri = Hijri(1445, 9, 15)
    holidays = get_holidays(hijri)
    assert any(h.id == HOLIDAY_RAMADAN for h in holidays)
    assert EVENT_RAMADAN in get_active_events(hijri)


def test_laylat_al_qadr_before_ramadan_in_list() -> None:
    """Test Laylat al-Qadr is listed before generic Ramadan on 27 Ramadan."""
    hijri = Hijri(1445, 9, 27)
    holidays = get_holidays(hijri)
    ids = [holiday.id for holiday in holidays]
    assert HOLIDAY_LAYLAT_AL_QADR in ids
    assert ids.index(HOLIDAY_LAYLAT_AL_QADR) < ids.index(HOLIDAY_RAMADAN)


def test_hijri_new_year() -> None:
    """Test Islamic New Year on 1 Muharram."""
    hijri = Hijri(1445, 1, 1)
    holidays = get_holidays(hijri)
    assert any(h.id == HOLIDAY_HIJRI_NEW_YEAR for h in holidays)


def test_eid_al_fitr() -> None:
    """Test Eid al-Fitr is detected."""
    hijri = Hijri(1445, 10, 1)
    holidays = get_holidays(hijri)
    assert any(h.id == HOLIDAY_EID_AL_FITR for h in holidays)
    assert EVENT_EID_AL_FITR in get_active_events(hijri)


def test_eid_al_fitr_day_2() -> None:
    """Test Eid al-Fitr day 2 is detected."""
    hijri = Hijri(1445, 10, 2)
    holidays = get_holidays(hijri)
    assert any(h.id == HOLIDAY_EID_AL_FITR_DAY_2 for h in holidays)


def test_days_until_ramadan() -> None:
    """Test days until Ramadan from a known date."""
    from custom_components.hijri_calendar.holidays import days_until_ramadan

    assert days_until_ramadan(Hijri(1445, 8, 1)) == 29
    assert days_until_ramadan(Hijri(1445, 9, 1)) == 0


def test_days_until_eid_al_fitr() -> None:
    """Test days until Eid al-Fitr from Ramadan."""
    from custom_components.hijri_calendar.holidays import days_until_eid_al_fitr

    assert days_until_eid_al_fitr(Hijri(1445, 9, 1)) == 30


def test_no_holiday_on_regular_day() -> None:
    """Test an ordinary day has no active events."""
    hijri = Hijri(1446, 2, 15)
    assert get_active_events(hijri) == set()
    assert get_holidays(hijri) == []


def test_mawlid_not_detected() -> None:
    """Test Mawlid is no longer a holiday."""
    hijri = Hijri(1445, 3, 12)
    assert not any(h.id == "mawlid" for h in get_holidays(hijri))
