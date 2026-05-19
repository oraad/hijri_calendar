"""Test Hijri Calendar services."""

import datetime as dt
from unittest.mock import AsyncMock, patch

import pytest
import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from custom_components.hijri_calendar.const import (
    ATTR_DATE,
    ATTR_HIJRI,
    ATTR_OFFSET,
    CONF_OFFSET_DAYS,
    DOMAIN,
    SERVICE_CALIBRATE_DATE,
    SERVICE_CONVERT_TO_GREGORIAN,
    SERVICE_CONVERT_TO_HIJRI,
    SERVICE_SET_DAY_OFFSET,
)
from custom_components.hijri_calendar.helpers import (
    compute_offset_for_hijri_today,
    gregorian_to_hijri,
    parse_hijri_date,
    resolve_effective_gregorian_date,
)
from custom_components.hijri_calendar.services import (
    CALIBRATE_SCHEMA,
    SET_DAY_OFFSET_SCHEMA,
    async_setup_services,
)


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


async def test_calibrate_date_relative_offset(
    hass: HomeAssistant, mock_config_entry
) -> None:
    """Test calibrate_date applies a relative offset and persists it."""
    mock_config_entry.add_to_hass(hass)
    async_setup_services(hass)

    frozen = dt.datetime(2024, 4, 9, 12, 0, 0, tzinfo=dt.UTC)
    with (
        patch(
            "custom_components.hijri_calendar.helpers.dt_util.now",
            return_value=frozen,
        ),
        patch.object(
            hass.config_entries,
            "async_reload",
            new=AsyncMock(return_value=True),
        ),
    ):
        response = await hass.services.async_call(
            DOMAIN,
            SERVICE_CALIBRATE_DATE,
            {ATTR_OFFSET: 1},
            blocking=True,
            return_response=True,
        )

    assert response["previous_offset"] == 0
    assert response["offset"] == 1
    assert mock_config_entry.options[CONF_OFFSET_DAYS] == 1
    assert response["hijri"] == "1445-10-01"
    assert response["effective_gregorian"] == "2024-04-10"


async def test_calibrate_date_hijri_mode(
    hass: HomeAssistant, mock_config_entry
) -> None:
    """Test calibrate_date computes offset from announced Hijri date."""
    mock_config_entry.add_to_hass(hass)
    async_setup_services(hass)

    frozen = dt.datetime(2024, 4, 9, 12, 0, 0, tzinfo=dt.UTC)
    with (
        patch(
            "custom_components.hijri_calendar.helpers.dt_util.now",
            return_value=frozen,
        ),
        patch.object(
            hass.config_entries,
            "async_reload",
            new=AsyncMock(return_value=True),
        ),
    ):
        response = await hass.services.async_call(
            DOMAIN,
            SERVICE_CALIBRATE_DATE,
            {ATTR_HIJRI: "1445-10-01"},
            blocking=True,
            return_response=True,
        )

    assert response["offset"] == 1
    assert response["hijri"] == "1445-10-01"
    assert mock_config_entry.options[CONF_OFFSET_DAYS] == 1


async def test_calibrate_date_no_config_entry(hass: HomeAssistant) -> None:
    """Test calibrate_date requires a configured integration."""
    async_setup_services(hass)
    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_CALIBRATE_DATE,
            {ATTR_OFFSET: 1},
            blocking=True,
            return_response=True,
        )


def test_calibrate_schema_rejects_both_modes() -> None:
    """Test calibrate schema rejects offset and hijri together."""
    with pytest.raises(vol.MultipleInvalid):
        CALIBRATE_SCHEMA({ATTR_OFFSET: 1, ATTR_HIJRI: "1445-09-30"})


def test_calibrate_schema_rejects_large_relative_offset() -> None:
    """Test calibrate schema limits relative offset to ±2."""
    with pytest.raises(vol.MultipleInvalid):
        CALIBRATE_SCHEMA({ATTR_OFFSET: 3})


def test_set_day_offset_schema_rejects_out_of_range() -> None:
    """Test set_day_offset schema limits offset to ±2."""
    with pytest.raises(vol.MultipleInvalid):
        SET_DAY_OFFSET_SCHEMA({ATTR_OFFSET: 3})


def test_compute_offset_for_hijri_today(hass: HomeAssistant) -> None:
    """Test offset computation for a fixed reference day."""
    frozen = dt.datetime(2024, 4, 9, 12, 0, 0, tzinfo=dt.UTC)
    with patch(
        "custom_components.hijri_calendar.helpers.dt_util.now", return_value=frozen
    ):
        target = parse_hijri_date("1445-10-01")
        offset = compute_offset_for_hijri_today(hass, "midnight", target)
    assert offset == 1
    with patch(
        "custom_components.hijri_calendar.helpers.dt_util.now", return_value=frozen
    ):
        base = resolve_effective_gregorian_date(hass, "midnight", offset)
        assert gregorian_to_hijri(base).isoformat() == "1445-10-01"


async def test_convert_to_gregorian_invalid_date(hass: HomeAssistant) -> None:
    """Test convert_to_gregorian raises for an invalid Hijri date."""
    async_setup_services(hass)
    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_CONVERT_TO_GREGORIAN,
            {ATTR_DATE: "not-a-date"},
            blocking=True,
            return_response=True,
        )


async def test_set_day_offset_service(hass: HomeAssistant, mock_config_entry) -> None:
    """Test set_day_offset updates config entry options."""
    mock_config_entry.add_to_hass(hass)
    async_setup_services(hass)

    with patch.object(
        hass.config_entries,
        "async_reload",
        new=AsyncMock(return_value=True),
    ):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SET_DAY_OFFSET,
            {ATTR_OFFSET: 2},
            blocking=True,
        )

    assert mock_config_entry.options["offset_days"] == 2
