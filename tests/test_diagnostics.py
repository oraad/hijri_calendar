"""Test Hijri Calendar diagnostics."""

from __future__ import annotations

from custom_components.hijri_calendar.diagnostics import (
    async_get_config_entry_diagnostics,
)


async def test_config_entry_diagnostics(hass, setup_integration) -> None:
    """Test diagnostics returns config and computed dates."""
    result = await async_get_config_entry_diagnostics(hass, setup_integration)
    assert result["config"]["language"] == "en"
    assert "hijri_date" in result
    assert "gregorian_date" in result
    assert result["offset_days"] == 0
