"""Base entity for SolArk Modbus integration."""
from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from .hub import SolArkModbusHub
from .const import ATTR_MANUFACTURER, DOMAIN

class SolArkBaseEntity(CoordinatorEntity[SolArkModbusHub]):
    """Common base for all SolArk entities."""

    def __init__(
        self,
        hub_name: str,
        hub: SolArkModbusHub,
        device_info: DeviceInfo,
    ) -> None:
        """Initialize the entity."""
        super().__init__(hub)
        self._hub_name = hub_name
        self._device_info = device_info

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return self._device_info

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        if not super().available:
            return False
            
        data = self.coordinator.data
        if not data:
            return False

        # Keep all sensors enabled as requested
        return True
