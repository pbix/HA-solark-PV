"""Time platform for SolArk Modbus."""
from __future__ import annotations

from datetime import time as dt_time
from homeassistant.components.time import TimeEntity, TimeEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.helpers.device_registry import DeviceInfo

from .const import ATTR_MANUFACTURER, DOMAIN
from .entity import SolArkBaseEntity
from .entity_description import SolArkModbusEntityDescription
from .hub import SolArkModbusHub

from dataclasses import dataclass

@dataclass(kw_only=True, frozen=True)
class SolArkModbusTimeEntityDescription(TimeEntityDescription, SolArkModbusEntityDescription):
    """A class that describes SolArk time entities."""

async def async_setup_entry(hass, entry, async_add_entities):
    hub_name = entry.data[CONF_NAME]
    hub: SolArkModbusHub = hass.data[DOMAIN][hub_name]["hub"]

    device_info = DeviceInfo(
        identifiers={(DOMAIN, hub_name)},
        name=hub_name,
        manufacturer=ATTR_MANUFACTURER,
    )

    entities = []

    for description in hub.register_map.time_types().values():
        entities.append(
            SolArkTime(
                hub_name,
                hub,
                device_info,
                description,
            )
        )

    async_add_entities(entities)
    return True

class SolArkTime(SolArkBaseEntity, TimeEntity):
    """Representation of a SolArk Modbus time."""

    entity_description: SolArkModbusTimeEntityDescription

    def __init__(
        self,
        hub_name: str,
        hub: SolArkModbusHub,
        device_info: DeviceInfo,
        description: SolArkModbusTimeEntityDescription,
    ) -> None:
        """Initialize the time."""
        super().__init__(hub_name, hub, device_info)
        self.entity_description = description
        self._attr_unique_id = f"{hub_name}_{description.key}"
        self._attr_name = f"{hub_name} {description.name}"

    @property
    def native_value(self) -> dt_time | None:
        """Return the state of the sensor."""
        value = self.coordinator.data.get(self.entity_description.key)
        if value is None:
            return None
            
        hour = int(value // 100)
        minute = int(value % 100)
        
        try:
            return dt_time(hour=hour, minute=minute)
        except ValueError:
            return None

    async def async_set_value(self, value: dt_time) -> None:
        """Update the current value."""
        raw_value = value.hour * 100 + value.minute
        
        if await self.coordinator.async_write_register(self.entity_description.address, raw_value):
            self.coordinator.data[self.entity_description.key] = raw_value
            self.async_write_ha_state()