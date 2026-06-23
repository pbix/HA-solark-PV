"""Select platform for SolArk Modbus."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.helpers.device_registry import DeviceInfo

from .const import ATTR_MANUFACTURER, DOMAIN
from .entity import SolArkBaseEntity
from .entity_description import SolArkModbusEntityDescription
from .hub import SolArkModbusHub

from dataclasses import dataclass

@dataclass(kw_only=True, frozen=True)
class SolArkModbusSelectEntityDescription(SelectEntityDescription, SolArkModbusEntityDescription):
    """A class that describes SolArk select entities."""

async def async_setup_entry(hass, entry, async_add_entities):
    hub_name = entry.data[CONF_NAME]
    hub: SolArkModbusHub = hass.data[DOMAIN][hub_name]["hub"]

    device_info = DeviceInfo(
        identifiers={(DOMAIN, hub_name)},
        name=hub_name,
        manufacturer=ATTR_MANUFACTURER,
    )

    entities = []

    for description in hub.register_map.select_types().values():
        entities.append(
            SolArkSelect(
                hub_name,
                hub,
                device_info,
                description,
            )
        )

    async_add_entities(entities)
    return True

class SolArkSelect(SolArkBaseEntity, SelectEntity):
    """Representation of a SolArk Modbus select."""

    entity_description: SolArkModbusSelectEntityDescription

    def __init__(
        self,
        hub_name: str,
        hub: SolArkModbusHub,
        device_info: DeviceInfo,
        description: SolArkModbusSelectEntityDescription,
    ) -> None:
        """Initialize the select."""
        super().__init__(hub_name, hub, device_info)
        self.entity_description = description
        self._attr_unique_id = f"{hub_name}_{description.key}"
        self._attr_name = f"{hub_name} {description.name}"
        self._attr_options = description.options

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""
        val = self.coordinator.data.get(self.entity_description.key)
        if val is None or val >= len(self._attr_options):
            return None
        return self._attr_options[val]

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        try:
            val = self._attr_options.index(option)
        except ValueError:
            return

        if await self.coordinator.async_write_register(self.entity_description.address, val):
            self.coordinator.data[self.entity_description.key] = val
            self.async_write_ha_state()
