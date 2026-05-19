"""Test holiday detection."""

from hijridate import Hijri

from custom_components.hijri_calendar.holidays import (
    EVENT_EID_AL_FITR,
    EVENT_RAMADAN,
    HOLIDAY_EID_AL_FITR,
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


def test_eid_al_fitr() -> None:
    """Test Eid al-Fitr is detected."""
    hijri = Hijri(1445, 10, 1)
    holidays = get_holidays(hijri)
    assert any(h.id == HOLIDAY_EID_AL_FITR for h in holidays)
    assert EVENT_EID_AL_FITR in get_active_events(hijri)


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
