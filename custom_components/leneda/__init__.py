"""The Leneda Energy integration."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from leneda import LenedaClient
from leneda.obis_codes import (
    ElectricityConsumption,
    ElectricityProduction,
    GasConsumption,
)

from .const import (
    DOMAIN,
    CONF_API_TOKEN,
    CONF_ENERGY_ID,
    CONF_METERING_POINTS,
    SCAN_INTERVAL,
)
from .config_flow import LenedaOptionsFlow

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Leneda Energy component."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Leneda Energy from a config entry."""
    # Parse metering points from comma-separated string
    metering_points = [mp.strip() for mp in entry.data[CONF_METERING_POINTS].split(",")]
    
    client = LenedaClient(
        api_key=entry.data[CONF_API_TOKEN],
        energy_id=entry.data[CONF_ENERGY_ID],
    )

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=lambda: update_data(hass, client, metering_points),
        update_interval=SCAN_INTERVAL,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def update_data(hass: HomeAssistant, client: LenedaClient, metering_points: list) -> dict:
    """Fetch data from Leneda API."""
    current_year = datetime.now().year
    start_date = datetime(current_year, 1, 1)
    end_date = datetime(current_year, 12, 31)

    data = {}
    for metering_point in metering_points:
        meter_data = {
            "consumption": None,
            "production": None,
            "gas_consumption": None,
        }
        
        try:
            # Get electricity consumption data
            electricity_consumption = await hass.async_add_executor_job(
                client.get_aggregated_metering_data,
                metering_point,
                ElectricityConsumption.ACTIVE,
                start_date,
                end_date,
                "Month",
                "Accumulation"
            )
            
            # Calculate yearly total for electricity consumption
            if electricity_consumption and electricity_consumption.aggregated_time_series:
                meter_data["consumption"] = sum(
                    float(point.value) for point in electricity_consumption.aggregated_time_series
                )
            else:
                _LOGGER.debug("No electricity consumption data available for %s", metering_point)
            
            # Get electricity production data (if available)
            try:
                electricity_production = await hass.async_add_executor_job(
                    client.get_aggregated_metering_data,
                    metering_point,
                    ElectricityProduction.ACTIVE,
                    start_date,
                    end_date,
                    "Month",
                    "Accumulation"
                )
                
                # Calculate yearly total for electricity production
                if electricity_production and electricity_production.aggregated_time_series:
                    meter_data["production"] = sum(
                        float(point.value) for point in electricity_production.aggregated_time_series
                    )
                else:
                    _LOGGER.debug("No electricity production data available for %s", metering_point)
                    
            except Exception as err:
                _LOGGER.debug("Could not fetch electricity production data for %s: %s", metering_point, err)
                
            # Get gas consumption data (if available)
            try:
                gas_consumption = await hass.async_add_executor_job(
                    client.get_aggregated_metering_data,
                    metering_point,
                    GasConsumption.VOLUME,
                    start_date,
                    end_date,
                    "Month",
                    "Accumulation"
                )
                
                # Calculate yearly total for gas consumption
                if gas_consumption and gas_consumption.aggregated_time_series:
                    meter_data["gas_consumption"] = sum(
                        float(point.value) for point in gas_consumption.aggregated_time_series
                    )
                else:
                    _LOGGER.debug("No gas consumption data available for %s", metering_point)
                    
            except Exception as err:
                _LOGGER.debug("Could not fetch gas consumption data for %s: %s", metering_point, err)
                
        except Exception as err:
            _LOGGER.error("Error fetching data for metering point %s: %s", metering_point, err)
            # Don't set default values, keep them as None to indicate unavailability
            
        data[metering_point] = meter_data

    return data

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

# Register the options flow
config_entries.register_options_flow = lambda domain, flow_class: None 