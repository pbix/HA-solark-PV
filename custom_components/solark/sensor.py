from __future__ import annotations

from datetime import datetime
import logging
from typing import Optional

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import homeassistant.util.dt as dt_util

from .const import (
    ATTR_MANUFACTURER,
    DOMAIN,
    SENSOR_TYPES,
    SolArkModbusSensorEntityDescription,
)
from .hub import SolArkModbusHub

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    hub_name = entry.data[CONF_NAME]
    hub = hass.data[DOMAIN][hub_name]["hub"]

    device_info = {
        "identifiers": {(DOMAIN, hub_name)},
        "name": hub_name,
        "manufacturer": ATTR_MANUFACTURER,
    }

    entities = []
    for sensor_description in SENSOR_TYPES.values():
        sensor = SolArkSensor(
            hub_name,
            hub,
            device_info,
            sensor_description,
        )
        entities.append(sensor)

    async_add_entities(entities)
    return True


class SolArkSensor(CoordinatorEntity, SensorEntity):
    """Representation of a SolArk Modbus sensor."""

    def __init__(
        self,
        platform_name: str,
        hub: SolArkModbusHub,
        device_info,
        description: SolArkModbusSensorEntityDescription,
    ):
        """Initialize the sensor."""
        self._platform_name = platform_name
        self._attr_device_info = device_info
        self.entity_description: SolArkModbusSensorEntityDescription = description

        super().__init__(coordinator=hub)

    @property
    def name(self):
        """Return the name."""
        return f"{self._platform_name} {self.entity_description.name}"

    @property
    def unique_id(self) -> Optional[str]:
        return f"{self._platform_name}_{self.entity_description.key}"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return (
            self.coordinator.data[self.entity_description.key]
            if self.entity_description.key in self.coordinator.data
            else None
        )
