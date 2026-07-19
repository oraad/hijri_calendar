"""Config flow for Hijri calendar integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.const import CONF_LANGUAGE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.selector import (
    LanguageSelector,
    LanguageSelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CALENDAR_LANGUAGE_ARABIC,
    CALENDAR_LANGUAGE_DEFAULT,
    CALENDAR_LANGUAGE_OPTIONS,
    CONF_DAY_BOUNDARY,
    CONF_HIJRI_MONTH_STARTS_CALENDAR_LANGUAGE,
    CONF_ISLAMIC_HISTORY_CALENDAR_LANGUAGE,
    CONF_OBSERVANCES_CALENDAR_LANGUAGE,
    CONF_OFFSET_DAYS,
    DAY_BOUNDARY_MIDNIGHT,
    DAY_BOUNDARY_SUNSET,
    DEFAULT_CALENDAR_LANGUAGE,
    DEFAULT_DAY_BOUNDARY,
    DEFAULT_LANGUAGE,
    DEFAULT_NAME,
    DEFAULT_OFFSET_DAYS,
    DOMAIN,
    OFFSET_DAYS_MAX,
    OFFSET_DAYS_MIN,
    SUPPORTED_LANGUAGES,
)
from .data import HijriCalendarConfigEntry

UNIQUE_ID = DOMAIN

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_OFFSET_DAYS, default=DEFAULT_OFFSET_DAYS): NumberSelector(
            NumberSelectorConfig(
                min=OFFSET_DAYS_MIN,
                max=OFFSET_DAYS_MAX,
                step=1,
                mode=NumberSelectorMode.BOX,
            ),
        ),
        vol.Optional(
            CONF_OBSERVANCES_CALENDAR_LANGUAGE, default=DEFAULT_CALENDAR_LANGUAGE
        ): SelectSelector(
            SelectSelectorConfig(
                options=[CALENDAR_LANGUAGE_DEFAULT, CALENDAR_LANGUAGE_ARABIC],
                mode=SelectSelectorMode.DROPDOWN,
                translation_key="observances_calendar_language",
            ),
        ),
        vol.Optional(
            CONF_ISLAMIC_HISTORY_CALENDAR_LANGUAGE, default=DEFAULT_CALENDAR_LANGUAGE
        ): SelectSelector(
            SelectSelectorConfig(
                options=[CALENDAR_LANGUAGE_DEFAULT, CALENDAR_LANGUAGE_ARABIC],
                mode=SelectSelectorMode.DROPDOWN,
                translation_key="islamic_history_calendar_language",
            ),
        ),
        vol.Optional(
            CONF_HIJRI_MONTH_STARTS_CALENDAR_LANGUAGE,
            default=DEFAULT_CALENDAR_LANGUAGE,
        ): SelectSelector(
            SelectSelectorConfig(
                options=list(CALENDAR_LANGUAGE_OPTIONS),
                mode=SelectSelectorMode.DROPDOWN,
                translation_key="hijri_month_starts_calendar_language",
            ),
        ),
    }
)


def _config_schema() -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_LANGUAGE, default=DEFAULT_LANGUAGE): LanguageSelector(
                LanguageSelectorConfig(languages=list(SUPPORTED_LANGUAGES)),
            ),
            vol.Required(
                CONF_DAY_BOUNDARY, default=DEFAULT_DAY_BOUNDARY
            ): SelectSelector(
                SelectSelectorConfig(
                    options=[DAY_BOUNDARY_MIDNIGHT, DAY_BOUNDARY_SUNSET],
                    mode=SelectSelectorMode.DROPDOWN,
                    translation_key="day_boundary",
                ),
            ),
        }
    )


class HijriCalendarConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hijri calendar."""

    VERSION = 2

    @staticmethod
    async def async_migrate_entry(
        hass: HomeAssistant, config_entry: HijriCalendarConfigEntry
    ) -> bool:
        """Migrate config entry; clamp legacy day offset to supported range."""
        if config_entry.version >= 2:
            return True

        offset = int(config_entry.options.get(CONF_OFFSET_DAYS, DEFAULT_OFFSET_DAYS))
        clamped = max(OFFSET_DAYS_MIN, min(OFFSET_DAYS_MAX, offset))
        if clamped != offset:
            hass.config_entries.async_update_entry(
                config_entry,
                options={**config_entry.options, CONF_OFFSET_DAYS: clamped},
                version=2,
            )
        else:
            hass.config_entries.async_update_entry(config_entry, version=2)
        return True

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: HijriCalendarConfigEntry,
    ) -> HijriCalendarOptionsFlowHandler:
        """Return the options flow handler."""
        return HijriCalendarOptionsFlowHandler()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        if user_input is not None:
            await self.async_set_unique_id(UNIQUE_ID)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=DEFAULT_NAME, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(
                _config_schema(), user_input
            ),
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration of the integration."""
        reconfigure_entry = self._get_reconfigure_entry()
        if not user_input:
            return self.async_show_form(
                step_id="reconfigure",
                data_schema=self.add_suggested_values_to_schema(
                    _config_schema(),
                    reconfigure_entry.data,
                ),
            )

        return self.async_update_reload_and_abort(reconfigure_entry, data=user_input)


class HijriCalendarOptionsFlowHandler(OptionsFlowWithReload):
    """Handle Hijri Calendar options."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage Hijri Calendar options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                OPTIONS_SCHEMA,
                self.config_entry.options,
            ),
        )
