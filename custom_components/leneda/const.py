"""Constants for the Leneda Energy integration."""
from datetime import timedelta
from leneda.obis_codes import (
    ElectricityConsumption,
    ElectricityProduction,
    GasConsumption,
)

DOMAIN = "leneda"

CONF_API_TOKEN = "api_token"
CONF_ENERGY_ID = "energy_id"
CONF_METERING_POINTS = "metering_points"

SCAN_INTERVAL = timedelta(hours=1)

# Sensor types
SENSOR_TYPE_ELECTRICITY_CONSUMPTION = "electricity_consumption"
SENSOR_TYPE_ELECTRICITY_PRODUCTION = "electricity_production"
SENSOR_TYPE_GAS_CONSUMPTION = "gas_consumption"

# Sensor names
SENSOR_NAMES = {
    SENSOR_TYPE_ELECTRICITY_CONSUMPTION: "Electricity Consumption",
    SENSOR_TYPE_ELECTRICITY_PRODUCTION: "Electricity Production",
    SENSOR_TYPE_GAS_CONSUMPTION: "Gas Consumption",
}

# Device classes
DEVICE_CLASSES = {
    SENSOR_TYPE_ELECTRICITY_CONSUMPTION: "energy",
    SENSOR_TYPE_ELECTRICITY_PRODUCTION: "energy",
    SENSOR_TYPE_GAS_CONSUMPTION: "gas",
}

# State classes
STATE_CLASSES = {
    SENSOR_TYPE_ELECTRICITY_CONSUMPTION: "total_increasing",
    SENSOR_TYPE_ELECTRICITY_PRODUCTION: "total_increasing",
    SENSOR_TYPE_GAS_CONSUMPTION: "total_increasing",
}

# Units
UNITS = {
    SENSOR_TYPE_ELECTRICITY_CONSUMPTION: "kWh",
    SENSOR_TYPE_ELECTRICITY_PRODUCTION: "kWh",
    SENSOR_TYPE_GAS_CONSUMPTION: "m³",
}

# Icons
ICONS = {
    SENSOR_TYPE_ELECTRICITY_CONSUMPTION: "mdi:lightning-bolt",
    SENSOR_TYPE_ELECTRICITY_PRODUCTION: "mdi:solar-power",
    SENSOR_TYPE_GAS_CONSUMPTION: "mdi:fire",
}

# Integration description
INTEGRATION_DESCRIPTION = """
Leneda Energy Integration for Home Assistant

This integration allows you to monitor your energy consumption and production from the Leneda energy platform in Luxembourg.

Features:
- Track electricity consumption and production
- Monitor gas consumption
- Yearly energy tracking (resets on January 1st)
- Compatible with Home Assistant Energy Dashboard

Note: Data is updated hourly and may have a one-day lag as per Leneda's data availability.
""" 