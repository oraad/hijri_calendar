"""Tests for the Hijri alternate calendar provider."""

import datetime as dt
import sys
from typing import TYPE_CHECKING

import pytest
from hijridate import Hijri
from homeassistant.components.calendar import CalendarEntity
from homeassistant.components.calendar.alternate_calendar import (
    AlternateCalendarProvider,
    AlternateCalendarRegistry,
    AlternateDate,
)
from homeassistant.const import CONF_LANGUAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.hijri_calendar.alternate_calendar import (
    HijriAlternateCalendarProvider,
)
from custom_components.hijri_calendar.const import (
    CALENDAR_TYPE_HIJRI,
    CONF_DAY_BOUNDARY,
    DAY_BOUNDARY_MIDNIGHT,
    DOMAIN,
)
from custom_components.hijri_calendar.helpers import gregorian_to_hijri

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

CALENDAR_KEYS = ["hijri_events", "islamic_history", "hijri_month_starts"]
OUT_OF_RANGE = dt.date(1800, 1, 1)
RAMADAN_START = dt.datetime.combine(
    Hijri(1447, 9, 1).to_gregorian(), dt.time.min, tzinfo=dt.UTC
)


def _calendar_entity(hass: HomeAssistant, entry_id: str, key: str) -> CalendarEntity:
    """Return a Hijri calendar entity."""
    entity_id = er.async_get(hass).async_get_entity_id(
        "calendar", DOMAIN, f"{entry_id}-{key}"
    )
    assert entity_id is not None
    entity = hass.data["entity_components"]["calendar"].get_entity(entity_id)
    assert isinstance(entity, CalendarEntity)
    return entity


@pytest.fixture
def provider() -> HijriAlternateCalendarProvider:
    """Return a provider using the default display language."""
    return HijriAlternateCalendarProvider()


@pytest.fixture
async def setup_arabic_integration(
    hass: HomeAssistant,
) -> AsyncIterator[MockConfigEntry]:
    """Set up the integration using Arabic display language."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_LANGUAGE: "ar", CONF_DAY_BOUNDARY: DAY_BOUNDARY_MIDNIGHT},
        options={},
        version=2,
        unique_id=DOMAIN,
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    yield entry
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()


def test_provider_registered() -> None:
    """Test the provider is registered with the core registry."""
    provider_class = AlternateCalendarRegistry.get_provider(CALENDAR_TYPE_HIJRI)

    assert issubclass(provider_class, AlternateCalendarProvider)


async def test_provider_registered_on_integration_setup(
    hass: HomeAssistant, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test setting up the integration registers the Hijri provider."""
    monkeypatch.delitem(
        AlternateCalendarRegistry._providers,  # noqa: SLF001
        CALENDAR_TYPE_HIJRI,
        raising=False,
    )
    monkeypatch.delitem(
        sys.modules, HijriAlternateCalendarProvider.__module__, raising=False
    )

    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()

    provider_class = AlternateCalendarRegistry.get_provider(CALENDAR_TYPE_HIJRI)
    assert issubclass(provider_class, AlternateCalendarProvider)


def test_provider_is_alternate_calendar_provider(
    provider: HijriAlternateCalendarProvider,
) -> None:
    """Test the provider implements the core ABC."""
    assert isinstance(provider, AlternateCalendarProvider)


def test_calendar_type(provider: HijriAlternateCalendarProvider) -> None:
    """Test the calendar type identifier."""
    assert provider.calendar_type == CALENDAR_TYPE_HIJRI == "hijri"


def test_display_name(provider: HijriAlternateCalendarProvider) -> None:
    """Test the display name shown in the frontend."""
    assert provider.display_name == "Hijri"


def test_convert_date_known_date(provider: HijriAlternateCalendarProvider) -> None:
    """Test conversion for a known date."""
    assert provider.convert_date(dt.date(2024, 3, 11)) == AlternateDate(
        calendar_type=CALENDAR_TYPE_HIJRI,
        display_name="1 Ramadan 1445 AH",
        date_str="1445-09-01",
        metadata={
            "hijri_year": 1445,
            "hijri_month": 9,
            "hijri_day": 1,
            "month_name": "Ramadan",
            "notation": "AH",
        },
    )


def test_convert_date_out_of_range(provider: HijriAlternateCalendarProvider) -> None:
    """Test dates outside the Umm al-Qura range fall back instead of raising."""
    assert provider.convert_date(OUT_OF_RANGE) == AlternateDate(
        calendar_type=CALENDAR_TYPE_HIJRI, display_name="", date_str=""
    )


def test_convert_date_language_is_respected() -> None:
    """Test display names use the provider language."""
    result = HijriAlternateCalendarProvider("ar").convert_date(dt.date(2024, 3, 11))

    assert result.display_name == "1 رمضان 1445 هـ"


@pytest.mark.parametrize("key", CALENDAR_KEYS)
async def test_calendar_entities_support_alternate_dates(
    hass: HomeAssistant, setup_integration: MockConfigEntry, key: str
) -> None:
    """Test every calendar entity declares Hijri alternate calendar support."""
    entity = _calendar_entity(hass, setup_integration.entry_id, key)

    assert entity.supported_alternate_calendars == [CALENDAR_TYPE_HIJRI]


@pytest.mark.parametrize("key", CALENDAR_KEYS)
async def test_calendar_entities_attach_alternate_dates(
    hass: HomeAssistant, setup_integration: MockConfigEntry, key: str
) -> None:
    """Test every event carries the Hijri date of its start day."""
    entity = _calendar_entity(hass, setup_integration.entry_id, key)
    events = await entity.async_get_events(
        hass, RAMADAN_START, RAMADAN_START + dt.timedelta(days=40)
    )

    assert events
    for event in events:
        assert event.alternate_dates
        alternate = event.alternate_dates[0]
        assert alternate.calendar_type == CALENDAR_TYPE_HIJRI
        day = event.start_datetime_local.date()
        assert alternate.date_str == gregorian_to_hijri(day).isoformat()


async def test_alternate_dates_use_configured_language(
    hass: HomeAssistant, setup_arabic_integration: MockConfigEntry
) -> None:
    """Test alternate date display names follow the configured language."""
    entity = _calendar_entity(hass, setup_arabic_integration.entry_id, "hijri_events")
    events = await entity.async_get_events(
        hass, RAMADAN_START, RAMADAN_START + dt.timedelta(days=40)
    )

    assert all(event.alternate_dates for event in events)
    assert all("هـ" in event.alternate_dates[0].display_name for event in events)
