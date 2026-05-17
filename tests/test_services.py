"""Test Hijri Calendar services."""

import datetime as dt

from homeassistant.core import HomeAssistant

from custom_components.hijri_calendar.const import (
    ATTR_DATE,
    ATTR_OFFSET,
    DOMAIN,
    SERVICE_CALIBRATE_DATE,
    SERVICE_CONVERT_TO_GREGORIAN,
    SERVICE_CONVERT_TO_HIJRI,
)
from custom_components.hijri_calendar.services import async_setup_services


async def test_convert_to_hijri_service(hass: HomeAssistant) -> None:
    """Test convert_to_hijri service."""
    async_setup_services(hass)
    response = await hass.services.async_call(
        DOMAIN,
        SERVICE_CONVERT_TO_HIJRI,
        {ATTR_DATE: dt.date(2024, 4, 9)},
        blocking=True,
        return_response=True,
    )
    assert response["hijri"] == "1445-09-30"
    assert response["year"] == 1445


async def test_convert_to_gregorian_service(hass: HomeAssistant) -> None:
    """Test convert_to_gregorian service."""
    async_setup_services(hass)
    response = await hass.services.async_call(
        DOMAIN,
        SERVICE_CONVERT_TO_GREGORIAN,
        {ATTR_DATE: "1445-09-30"},
        blocking=True,
        return_response=True,
    )
    assert response["gregorian"] == "2024-04-09"


async def test_calibrate_date_service(hass: HomeAssistant) -> None:
    """Test calibrate_date service with offset."""
    async_setup_services(hass)
    response = await hass.services.async_call(
        DOMAIN,
        SERVICE_CALIBRATE_DATE,
        {
            ATTR_DATE: dt.date(2024, 4, 9),
            ATTR_OFFSET: 1,
        },
        blocking=True,
        return_response=True,
    )
    assert response["input_gregorian"] == "2024-04-09"
    assert response["adjusted_gregorian"] == "2024-04-10"
    assert response["offset"] == 1
    assert "hijri" in response
