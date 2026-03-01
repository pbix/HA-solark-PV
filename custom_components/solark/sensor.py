from __future__ import annotations

from typing import Optional

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, EntityCategory
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_MANUFACTURER,
    DOMAIN,
)
from .hub import SolArkModbusHub
from .sensor_entity_description import SolArkModbusSensorEntityDescription


async def async_setup_entry(hass, entry, async_add_entities):
    hub_name = entry.data[CONF_NAME]
    hub: SolArkModbusHub = hass.data[DOMAIN][hub_name]["hub"]

    device_info = DeviceInfo(
        identifiers={(DOMAIN, hub_name)},
        name=hub_name,
        manufacturer=ATTR_MANUFACTURER,
    )

    entities = []

    # Normal Modbus sensors
    for sensor_description in hub.register_map.sensor_types().values():
        sensor = SolArkSensor(
            hub_name,
            hub,
            device_info,
            sensor_description,
        )
        entities.append(sensor)

    # Add ONE configuration info sensor
    entities.append(
        SolArkConfigInfoSensor(
            hub_name,
            entry,
            device_info,
        )
    )

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
        self._platform_name = platform_name
        self._attr_device_info = device_info
        self.entity_description: SolArkModbusSensorEntityDescription = description

        super().__init__(coordinator=hub)

    @property
    def name(self):
        return f"{self._platform_name} {self.entity_description.name}"

    @property
    def unique_id(self) -> Optional[str]:
        return f"{self._platform_name}_{self.entity_description.key}"

    @property
    def native_value(self):
        data = self.coordinator.data
        if not data:
            return None
        return data.get(self.entity_description.key)


class SolArkConfigInfoSensor(SensorEntity):
    """Single diagnostic sensor exposing config values as attributes."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, hub_name: str, entry: ConfigEntry, device_info: DeviceInfo):
        self._hub_name = hub_name
        self._entry = entry
        self._attr_device_info = device_info
        self._attr_unique_id = f"{entry.entry_id}_config_info"
        self._attr_name = f"{hub_name} Configuration"
        self.icon = "mdi:message-alert-outline"

    @property
    def native_value(self):
        return "loaded"

    @property
    def extra_state_attributes(self):
        return {
            "name": self._entry.data.get("name"),
            "host": self._entry.data.get("host"),
            "scan_interval": self._entry.data.get("scan_interval"),
        }
