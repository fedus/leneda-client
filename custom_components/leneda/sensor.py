"""Support for Leneda Energy sensors."""
from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from leneda.obis_codes import (
    ElectricityConsumption,
    ElectricityProduction,
    GasConsumption,
)

from .const import (
    DOMAIN,
    SENSOR_TYPE_ELECTRICITY_CONSUMPTION,
    SENSOR_TYPE_ELECTRICITY_PRODUCTION,
    SENSOR_TYPE_GAS_CONSUMPTION,
    SENSOR_NAMES,
    DEVICE_CLASSES,
    STATE_CLASSES,
    UNITS,
    ICONS,
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Leneda Energy sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Parse metering points from comma-separated string
    metering_points = [mp.strip() for mp in entry.data["metering_points"].split(",")]

    sensors = []
    for metering_point in metering_points:
        # Add electricity consumption sensor
        sensors.append(
            LenedaEnergySensor(
                coordinator,
                metering_point,
                SENSOR_TYPE_ELECTRICITY_CONSUMPTION,
                entry.data["energy_id"],
                ElectricityConsumption.ACTIVE,
            )
        )
        
        # Add electricity production sensor
        sensors.append(
            LenedaEnergySensor(
                coordinator,
                metering_point,
                SENSOR_TYPE_ELECTRICITY_PRODUCTION,
                entry.data["energy_id"],
                ElectricityProduction.ACTIVE,
            )
        )
        
        # Add gas consumption sensor
        sensors.append(
            LenedaEnergySensor(
                coordinator,
                metering_point,
                SENSOR_TYPE_GAS_CONSUMPTION,
                entry.data["energy_id"],
                GasConsumption.VOLUME,
            )
        )

    async_add_entities(sensors, True)

class LenedaEnergySensor(CoordinatorEntity, SensorEntity):
    """Representation of a Leneda Energy sensor."""

    def __init__(
        self,
        coordinator,
        metering_point: str,
        sensor_type: str,
        energy_id: str,
        obis_code: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._metering_point = metering_point
        self._sensor_type = sensor_type
        self._energy_id = energy_id
        self._obis_code = obis_code
        self._attr_name = f"{SENSOR_NAMES[sensor_type]} {metering_point}"
        self._attr_unique_id = f"{metering_point}_{sensor_type}"
        self._attr_device_class = DEVICE_CLASSES[sensor_type]
        self._attr_state_class = STATE_CLASSES[sensor_type]
        self._attr_native_unit_of_measurement = UNITS[sensor_type]
        self._attr_icon = ICONS[sensor_type]
        
        # Set device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{energy_id}_{metering_point}")},
            "name": f"{energy_id} / {metering_point}",
            "manufacturer": "Leneda",
            "model": "Energy Meter",
            "sw_version": "1.0.0",
        }
        
        # Set additional attributes
        self._attr_extra_state_attributes = {
            "metering_point": metering_point,
            "energy_id": energy_id,
            "sensor_type": sensor_type,
            "obis_code": obis_code,
            "year": datetime.now().year,
        }

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None

        meter_data = self.coordinator.data.get(self._metering_point)
        if not meter_data:
            return None

        # Get the value based on sensor type
        if self._sensor_type == SENSOR_TYPE_ELECTRICITY_CONSUMPTION:
            return meter_data.get("consumption")
        elif self._sensor_type == SENSOR_TYPE_ELECTRICITY_PRODUCTION:
            return meter_data.get("production")
        elif self._sensor_type == SENSOR_TYPE_GAS_CONSUMPTION:
            return meter_data.get("gas_consumption")

        return None
        
    @property
    def available(self) -> bool:
        """Return if the sensor is available."""
        if not self.coordinator.data:
            return False

        meter_data = self.coordinator.data.get(self._metering_point)
        if not meter_data:
            return False

        # Check if the specific sensor type has data
        if self._sensor_type == SENSOR_TYPE_ELECTRICITY_CONSUMPTION:
            return meter_data.get("consumption") is not None
        elif self._sensor_type == SENSOR_TYPE_ELECTRICITY_PRODUCTION:
            return meter_data.get("production") is not None
        elif self._sensor_type == SENSOR_TYPE_GAS_CONSUMPTION:
            return meter_data.get("gas_consumption") is not None

        return False 