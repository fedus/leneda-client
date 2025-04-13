"""Config flow for Leneda Energy integration."""
from __future__ import annotations

import logging
from typing import Any, Dict, List

import voluptuous as vol
from leneda import LenedaClient
from leneda.obis_codes import ElectricityConsumption

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    CONF_API_TOKEN,
    CONF_ENERGY_ID,
    CONF_METERING_POINTS,
)

_LOGGER = logging.getLogger(__name__)

class InvalidMeteringPoints(HomeAssistantError):
    """Error to indicate no metering points are available."""

class LenedaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Leneda Energy."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._existing_entries: List[Dict[str, Any]] = []
        self._use_existing: bool = False
        self._selected_energy_id: str = ""
        self._api_token: str = ""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        # Get existing entries
        self._existing_entries = []
        for entry in self.hass.config_entries.async_entries(DOMAIN):
            self._existing_entries.append({
                "entry_id": entry.entry_id,
                "energy_id": entry.data.get(CONF_ENERGY_ID, ""),
                "api_token": entry.data.get(CONF_API_TOKEN, ""),
                "title": entry.title,
            })

        # If there are no existing entries, go directly to new credentials
        if not self._existing_entries:
            return await self.async_step_new_credentials()

        # Show menu with options
        return self.async_show_menu(
            step_id="user",
            menu_options={
                "new_credentials": "Add with new energy ID",
                "select_existing": "Add using existing energy ID",
            },
        )

    async def async_step_select_existing(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle selecting an existing configuration."""
        errors = {}

        if user_input is not None:
            self._selected_energy_id = user_input["existing_energy_id"]
            # Get the API token from the existing entry
            for entry in self._existing_entries:
                if entry["energy_id"] == self._selected_energy_id:
                    self._api_token = entry["api_token"]
                    break
            return await self.async_step_metering_points()

        # Create options for existing energy IDs
        energy_id_options = {
            entry["energy_id"]: f"{entry['energy_id']}" 
            for entry in self._existing_entries
        }

        return self.async_show_form(
            step_id="select_existing",
            data_schema=vol.Schema({
                vol.Required("existing_energy_id"): vol.In(energy_id_options)
            }),
            errors=errors,
        )

    async def async_step_new_credentials(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle entering new credentials."""
        errors = {}

        if user_input is not None:
            try:
                # Validate API token and energy ID by making a test request
                client = LenedaClient(
                    api_key=user_input[CONF_API_TOKEN],
                    energy_id=user_input[CONF_ENERGY_ID],
                )
                
                # Try to make a simple request to validate credentials
                from datetime import datetime, timedelta
                test_date = datetime.now() - timedelta(days=7)
                test_end_date = datetime.now()
                
                # Just try to get data for any metering point to validate credentials
                await self.hass.async_add_executor_job(
                    client.get_aggregated_metering_data,
                    "TEST",
                    ElectricityConsumption.ACTIVE,
                    test_date,
                    test_end_date,
                    "Month",
                    "Accumulation"
                )
                
                # Create unique ID for the config entry
                await self.async_set_unique_id(user_input[CONF_ENERGY_ID])
                self._selected_energy_id = user_input[CONF_ENERGY_ID]
                self._api_token = user_input[CONF_API_TOKEN]
                
                return await self.async_step_metering_points()
            except Exception as err:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="new_credentials",
            data_schema=vol.Schema({
                vol.Required(CONF_API_TOKEN): str,
                vol.Required(CONF_ENERGY_ID): str,
            }),
            errors=errors,
        )

    async def async_step_metering_points(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle entering metering points."""
        errors = {}

        if user_input is not None:
            try:
                # Parse metering points from comma-separated string
                metering_points = [mp.strip() for mp in user_input[CONF_METERING_POINTS].split(",")]
                
                if not metering_points:
                    raise InvalidMeteringPoints()
                
                if self._use_existing:
                    # Get the existing entry
                    existing_entry = None
                    for entry in self.hass.config_entries.async_entries(DOMAIN):
                        if entry.data.get(CONF_ENERGY_ID) == self._selected_energy_id:
                            existing_entry = entry
                            break
                    
                    if not existing_entry:
                        errors["base"] = "existing_config_not_found"
                        return self.async_show_form(
                            step_id="metering_points",
                            data_schema=vol.Schema({
                                vol.Required(CONF_METERING_POINTS): str,
                            }),
                            description_placeholders={
                                "metering_points_help": "Enter your metering point IDs separated by commas (e.g., MP001,MP002)"
                            },
                            errors=errors,
                        )
                    
                    # Merge the new metering points with existing ones
                    existing_points = set(existing_entry.data.get(CONF_METERING_POINTS, "").split(","))
                    new_points = set(metering_points)
                    all_points = ",".join(sorted(existing_points | new_points))
                    
                    # Update the existing entry
                    self.hass.config_entries.async_update_entry(
                        existing_entry,
                        data={
                            **existing_entry.data,
                            CONF_METERING_POINTS: all_points,
                        },
                    )
                    
                    # Trigger a reload of the config entry
                    await self.hass.config_entries.async_reload(existing_entry.entry_id)
                    
                    return self.async_abort(reason="updated_existing")
                else:
                    # Create new entry
                    return self.async_create_entry(
                        title=f"{self._selected_energy_id}",
                        data={
                            CONF_API_TOKEN: self._api_token,
                            CONF_ENERGY_ID: self._selected_energy_id,
                            CONF_METERING_POINTS: ",".join(metering_points),
                        },
                    )

            except InvalidMeteringPoints:
                errors["base"] = "invalid_metering_points"
            except Exception as err:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="metering_points",
            data_schema=vol.Schema({
                vol.Required(CONF_METERING_POINTS): str,
            }),
            description_placeholders={
                "metering_points_help": "Enter your metering point IDs separated by commas (e.g., MP001,MP002)"
            },
            errors=errors,
        )

    async def async_step_import(self, import_data: dict[str, Any]) -> FlowResult:
        """Import a config entry."""
        return await self.async_step_user(import_data)

class LenedaOptionsFlow(config_entries.OptionsFlow):
    """Handle Leneda options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors = {}

        if user_input is not None:
            try:
                # Parse metering points from comma-separated string
                metering_points = [mp.strip() for mp in user_input[CONF_METERING_POINTS].split(",")]
                
                if not metering_points:
                    raise InvalidMeteringPoints()
                
                # Validate the metering points by making a test request
                client = LenedaClient(
                    api_key=self.config_entry.data[CONF_API_TOKEN],
                    energy_id=self.config_entry.data[CONF_ENERGY_ID],
                )
                
                # Try to make a simple request to validate credentials
                from datetime import datetime, timedelta
                test_date = datetime.now() - timedelta(days=7)
                test_end_date = datetime.now()
                
                # Just try to get data for the first metering point to validate credentials
                test_metering_point = metering_points[0]
                await self.hass.async_add_executor_job(
                    client.get_aggregated_metering_data,
                    test_metering_point,
                    ElectricityConsumption.ACTIVE,
                    test_date,
                    test_end_date,
                    "Month",
                    "Accumulation"
                )
                
                return self.async_create_entry(
                    title=self.config_entry.title,
                    data={
                        **self.config_entry.data,
                        CONF_METERING_POINTS: ",".join(metering_points),
                    },
                )

            except InvalidMeteringPoints:
                errors["base"] = "invalid_metering_points"
            except Exception as err:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_METERING_POINTS,
                        default=self.config_entry.options.get(
                            CONF_METERING_POINTS,
                            self.config_entry.data.get(CONF_METERING_POINTS, ""),
                        ),
                    ): str,
                }
            ),
            description_placeholders={
                "metering_points_help": "Enter your metering point IDs separated by commas (e.g., MP001,MP002)"
            },
            errors=errors,
        ) 