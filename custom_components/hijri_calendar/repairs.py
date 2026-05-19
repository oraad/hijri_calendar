"""Repair issues for Hijri Calendar."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers import issue_registry as ir

from .const import CONF_DAY_BOUNDARY, DAY_BOUNDARY_SUNSET, DOMAIN
from .data import HijriCalendarConfigEntry
from .helpers import next_sunset

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

ISSUE_SUNSET_UNAVAILABLE = "sunset_unavailable"


def _issue_id(entry_id: str) -> str:
    return f"{ISSUE_SUNSET_UNAVAILABLE}_{entry_id}"


async def async_update_sunset_repairs(
    hass: HomeAssistant, config_entry: HijriCalendarConfigEntry
) -> None:
    """Create or clear the sunset-unavailable repair issue."""
    issue_id = _issue_id(config_entry.entry_id)
    day_boundary = config_entry.data.get(CONF_DAY_BOUNDARY, "midnight")

    if day_boundary != DAY_BOUNDARY_SUNSET:
        ir.async_delete_issue(hass, DOMAIN, issue_id)
        return

    if next_sunset(hass) is None:
        ir.async_create_issue(
            hass,
            DOMAIN,
            issue_id,
            is_fixable=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key=ISSUE_SUNSET_UNAVAILABLE,
        )
        return

    ir.async_delete_issue(hass, DOMAIN, issue_id)


def async_clear_sunset_repairs(
    hass: HomeAssistant, config_entry: HijriCalendarConfigEntry
) -> None:
    """Remove sunset repair issues when the integration unloads."""
    ir.async_delete_issue(hass, DOMAIN, _issue_id(config_entry.entry_id))
