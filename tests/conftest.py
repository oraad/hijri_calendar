"""Fixtures for hijri_calendar tests."""

from unittest.mock import patch

import pytest
from homeassistant.const import CONF_LANGUAGE
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.hijri_calendar.const import (
    CONF_DAY_BOUNDARY,
    DAY_BOUNDARY_MIDNIGHT,
    DOMAIN,
)

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations) -> None:
    """Enable loading custom integrations from custom_components."""
    return enable_custom_integrations


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a default mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_LANGUAGE: "en",
            CONF_DAY_BOUNDARY: DAY_BOUNDARY_MIDNIGHT,
        },
        options={},
        unique_id=DOMAIN,
    )


@pytest.fixture
async def setup_integration(hass, mock_config_entry):
    """Set up the hijri_calendar integration."""
    mock_config_entry.add_to_hass(hass)
    with patch(
        "homeassistant.config_entries.ConfigEntries.async_forward_entry_setups",
        return_value=True,
    ):
        from custom_components.hijri_calendar import async_setup_entry

        await async_setup_entry(hass, mock_config_entry)
    await hass.async_block_till_done()
    return mock_config_entry
