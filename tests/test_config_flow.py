"""Test the Hijri Calendar config flow."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.const import CONF_LANGUAGE
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType, InvalidData
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.hijri_calendar.config_flow import HijriCalendarConfigFlow
from custom_components.hijri_calendar.const import (
    CONF_DAY_BOUNDARY,
    CONF_OFFSET_DAYS,
    DAY_BOUNDARY_MIDNIGHT,
    DAY_BOUNDARY_SUNSET,
    DOMAIN,
)


@pytest.mark.parametrize(
    ("language", "day_boundary"),
    [
        ("en", DAY_BOUNDARY_MIDNIGHT),
        ("ar", DAY_BOUNDARY_SUNSET),
        ("de", DAY_BOUNDARY_MIDNIGHT),
        ("bn", DAY_BOUNDARY_MIDNIGHT),
    ],
)
async def test_user_flow(hass: HomeAssistant, language: str, day_boundary: str) -> None:
    """Test the user config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM

    with (
        patch(
            "homeassistant.config_entries.ConfigEntries.async_forward_entry_setups",
            return_value=True,
        ),
        patch(
            "custom_components.hijri_calendar.async_setup_entry",
            new=AsyncMock(return_value=True),
        ),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                CONF_LANGUAGE: language,
                CONF_DAY_BOUNDARY: day_boundary,
            },
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_LANGUAGE] == language
    assert result["data"][CONF_DAY_BOUNDARY] == day_boundary


async def test_options_flow(hass: HomeAssistant, mock_config_entry) -> None:
    """Test the options flow."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    assert result["type"] is FlowResultType.FORM

    with patch.object(
        hass.config_entries,
        "async_reload",
        new=AsyncMock(return_value=True),
    ):
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={CONF_OFFSET_DAYS: 1},
        )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_OFFSET_DAYS] == 1


async def test_options_flow_rejects_offset_out_of_range(
    hass: HomeAssistant, mock_config_entry
) -> None:
    """Test the options flow rejects day offset outside ±2."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    assert result["type"] is FlowResultType.FORM

    with pytest.raises(InvalidData):
        await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={CONF_OFFSET_DAYS: 5},
        )


async def test_migrate_entry_clamps_offset(hass: HomeAssistant) -> None:
    """Test migration clamps legacy offset values to ±2."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_LANGUAGE: "en", CONF_DAY_BOUNDARY: DAY_BOUNDARY_MIDNIGHT},
        options={CONF_OFFSET_DAYS: 10},
        version=1,
        unique_id=DOMAIN,
    )
    entry.add_to_hass(hass)

    assert await HijriCalendarConfigFlow.async_migrate_entry(hass, entry) is True
    assert entry.version == 2
    assert entry.options[CONF_OFFSET_DAYS] == 2


async def test_reconfigure_flow(hass: HomeAssistant, mock_config_entry) -> None:
    """Test reconfigure updates language and day boundary."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_RECONFIGURE,
            "entry_id": mock_config_entry.entry_id,
        },
    )
    assert result["type"] is FlowResultType.FORM

    with patch.object(
        hass.config_entries,
        "async_reload",
        new=AsyncMock(return_value=True),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                CONF_LANGUAGE: "ar",
                CONF_DAY_BOUNDARY: DAY_BOUNDARY_SUNSET,
            },
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert mock_config_entry.data[CONF_LANGUAGE] == "ar"
    assert mock_config_entry.data[CONF_DAY_BOUNDARY] == DAY_BOUNDARY_SUNSET
