"""Switch platform for SolArk Modbus."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.helpers.device_registry import DeviceInfo

from .const import ATTR_MANUFACTURER, DOMAIN
from .entity import SolArkBaseEntity
from .entity_description import SolArkModbusEntityDescription
from .hub import SolArkModbusHub

from dataclasses import dataclass

@dataclass(kw_only=True, frozen=True)
class SolArkModbusSwitchEntityDescription(SwitchEntityDescription, SolArkModbusEntityDescription):
    """A class that describes SolArk switch entities."""

async def async_setup_entry(hass, entry, async_add_entities):
    hub_name = entry.data[CONF_NAME]
    hub: SolArkModbusHub = hass.data[DOMAIN][hub_name]["hub"]

    device_info = DeviceInfo(
        identifiers={(DOMAIN, hub_name)},
        name=hub_name,
        manufacturer=ATTR_MANUFACTURER,
    )

    entities = []

    for description in hub.register_map.switch_types().values():
        entities.append(
            SolArkSwitch(
                hub_name,
                hub,
                device_info,
                description,
            )
        )

    async_add_entities(entities)
    return True

class SolArkSwitch(SolArkBaseEntity, SwitchEntity):
    """Representation of a SolArk Modbus switch."""

    entity_description: SolArkModbusSwitchEntityDescription

    def __init__(
        self,
        hub_name: str,
        hub: SolArkModbusHub,
        device_info: DeviceInfo,
        description: SolArkModbusSwitchEntityDescription,
    ) -> None:
        """Initialize the switch."""
        super().__init__(hub_name, hub, device_info)
        self.entity_description = description
        self._attr_unique_id = f"{hub_name}_{description.key}"
        self._attr_name = f"{hub_name} {description.name}"

    @property
    def is_on(self) -> bool | None:
        """Return True if entity is on."""
        value = self.coordinator.data.get(self.entity_description.key)
        if value is None:
            return None
        return bool(value)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the entity on."""
        if await self.coordinator.async_write_register(self.entity_description.address, 1):
            self.coordinator.data[self.entity_description.key] = 1
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the entity off."""
        if await self.coordinator.async_write_register(self.entity_description.address, 0):
            self.coordinator.data[self.entity_description.key] = 0
            self.async_write_ha_state()
