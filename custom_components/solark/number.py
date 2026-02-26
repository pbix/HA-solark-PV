from __future__ import annotations

import logging
from typing import Optional

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import CONF_NAME, UnitOfElectricCurrent
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_MANUFACTURER,
    DOMAIN,
    GRID_CHARGE_CURRENT_KEY,
)
from .hub import SolArkModbusHub

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up SolArk number entities (grid charge current)."""
    hub_name = entry.data[CONF_NAME]
    hub: SolArkModbusHub = hass.data[DOMAIN][hub_name]["hub"]["hub"]

    device_info = {
        "identifiers": {(DOMAIN, hub_name)},
        "name": hub_name,
        "manufacturer": ATTR_MANUFACTURER,
    }

    entities: list[SolArkGridChargeCurrentNumber] = [
        SolArkGridChargeCurrentNumber(
            platform_name=hub_name,
            hub=hub,
            device_info=device_info,
        )
    ]

    async_add_entities(entities)
    return True


class SolArkGridChargeCurrentNumber(CoordinatorEntity, NumberEntity):
    """Number entity for grid charge current (register 128)."""

    _attr_has_entity_name = True
    _attr_mode = NumberMode.SLIDER
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_native_min_value = 0
    _attr_native_max_value = 105
    _attr_native_step = 1

    def __init__(
        self,
        platform_name: str,
        hub: SolArkModbusHub,
        device_info: dict,
    ) -> None:
        super().__init__(coordinator=hub)
        self._platform_name = platform_name
        self._hub = hub
        self._attr_device_info = device_info
        self._attr_name = f"{platform_name} Grid Charge Current"
        self._key = GRID_CHARGE_CURRENT_KEY
        self._attr_icon = "mdi:current-dc"

    @property
    def unique_id(self) -> Optional[str]:
        return f"{self._platform_name}_{self._key}"

    @property
    def native_value(self) -> float | None:
        """Return the current grid charge current in amps."""
        val = self.coordinator.data.get(self._key)
        if val is None:
            return None
        return float(val)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the hub."""
        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Set new grid charge current in amps."""
        # Clamp in case someone bypasses HA's slider bounds.
        if value < self._attr_native_min_value:
            value = self._attr_native_min_value
        if value > self._attr_native_max_value:
            value = self._attr_native_max_value

        amps_int = int(round(value))
        _LOGGER.debug("Setting grid charge current to %s A", amps_int)

        success = await self.coordinator.hass.async_add_executor_job(
            self._hub.set_grid_charge_current, amps_int
        )
        if success:
            await self.coordinator.async_request_refresh()
