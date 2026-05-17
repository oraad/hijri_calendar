"""Test the Hijri Calendar config flow."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.const import CONF_LANGUAGE
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

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
    ],
)
async def test_user_flow(hass: HomeAssistant, language: str, day_boundary: str) -> None:
    """Test the user config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM

    with patch(
        "homeassistant.config_entries.ConfigEntries.async_forward_entry_setups",
        return_value=True,
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
