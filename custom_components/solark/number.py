"""Number platform for SolArk Modbus."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.helpers.device_registry import DeviceInfo

from .const import ATTR_MANUFACTURER, DOMAIN
from .entity import SolArkBaseEntity
from .entity_description import SolArkModbusEntityDescription
from .hub import SolArkModbusHub

from dataclasses import dataclass

@dataclass(kw_only=True, frozen=True)
class SolArkModbusNumberEntityDescription(NumberEntityDescription, SolArkModbusEntityDescription):
    """A class that describes SolArk number entities."""

async def async_setup_entry(hass, entry, async_add_entities):
    hub_name = entry.data[CONF_NAME]
    hub: SolArkModbusHub = hass.data[DOMAIN][hub_name]["hub"]

    device_info = DeviceInfo(
        identifiers={(DOMAIN, hub_name)},
        name=hub_name,
        manufacturer=ATTR_MANUFACTURER,
    )

    entities = []

    for description in hub.register_map.number_types().values():
        entities.append(
            SolArkNumber(
                hub_name,
                hub,
                device_info,
                description,
            )
        )

    async_add_entities(entities)
    return True

class SolArkNumber(SolArkBaseEntity, NumberEntity):
    """Representation of a SolArk Modbus number."""

    entity_description: SolArkModbusNumberEntityDescription

    def __init__(
        self,
        hub_name: str,
        hub: SolArkModbusHub,
        device_info: DeviceInfo,
        description: SolArkModbusNumberEntityDescription,
    ) -> None:
        """Initialize the number."""
        super().__init__(hub_name, hub, device_info)
        self.entity_description = description
        self._attr_unique_id = f"{hub_name}_{description.key}"
        self._attr_name = f"{hub_name} {description.name}"
        self._attr_mode = "slider"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get(self.entity_description.key)

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        # User defined scaling (e.g. 0.01 for Voltage)
        scale = getattr(self.entity_description, "scale", 1.0)
        raw_value = int(value / scale)
        
        if await self.coordinator.async_write_register(self.entity_description.address, raw_value):
            self.coordinator.data[self.entity_description.key] = value
            self.async_write_ha_state()
