from __future__ import annotations

import logging
from typing import Optional

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_MANUFACTURER,
    DOMAIN,
    GEN_CHARGE_ENABLE_KEY,
    GRID_CHARGE_ENABLE_KEY,
)
from .hub import SolArkModbusHub

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up SolArk switches (grid/gen charge enable)."""
    hub_name = entry.data[CONF_NAME]
    hub: SolArkModbusHub = hass.data[DOMAIN][hub_name]["hub"]["hub"]

    device_info = {
        "identifiers": {(DOMAIN, hub_name)},
        "name": hub_name,
        "manufacturer": ATTR_MANUFACTURER,
    }

    entities: list[SolArkBaseSwitch] = []

    entities.append(
        SolArkGridChargeEnableSwitch(
            platform_name=hub_name,
            hub=hub,
            device_info=device_info,
        )
    )

    entities.append(
        SolArkGenChargeEnableSwitch(
            platform_name=hub_name,
            hub=hub,
            device_info=device_info,
        )
    )

    async_add_entities(entities)
    return True


class SolArkBaseSwitch(CoordinatorEntity, SwitchEntity):
    """Base class for SolArk writable boolean registers."""

    _attr_has_entity_name = True

    def __init__(
        self,
        platform_name: str,
        hub: SolArkModbusHub,
        device_info: dict,
        key: str,
        name_suffix: str,
        icon: str | None = None,
    ) -> None:
        super().__init__(coordinator=hub)
        self._platform_name = platform_name
        self._hub = hub
        self._attr_device_info = device_info
        self._key = key
        self._attr_name = f"{platform_name} {name_suffix}"
        if icon:
            self._attr_icon = icon

    @property
    def unique_id(self) -> Optional[str]:
        return f"{self._platform_name}_{self._key}"

    @property
    def is_on(self) -> bool | None:
        val = self.coordinator.data.get(self._key)
        if val is None:
            return None
        # Treat any non-zero as "on"
        return bool(val)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the hub."""
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the feature on (implemented in subclass)."""
        raise NotImplementedError

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the feature off (implemented in subclass)."""
        raise NotImplementedError


class SolArkGridChargeEnableSwitch(SolArkBaseSwitch):
    """Switch for enabling/disabling grid charge (register 130)."""

    def __init__(
        self,
        platform_name: str,
        hub: SolArkModbusHub,
        device_info: dict,
    ) -> None:
        super().__init__(
            platform_name=platform_name,
            hub=hub,
            device_info=device_info,
            key=GRID_CHARGE_ENABLE_KEY,
            name_suffix="Grid Charge Enable",
            icon="mdi:transmission-tower-export",
        )

    async def async_turn_on(self, **kwargs) -> None:
        """Enable grid charge."""
        success = await self.coordinator.hass.async_add_executor_job(
            self._hub.set_grid_charge_enable, True
        )
        if success:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Disable grid charge."""
        success = await self.coordinator.hass.async_add_executor_job(
            self._hub.set_grid_charge_enable, False
        )
        if success:
            await self.coordinator.async_request_refresh()


class SolArkGenChargeEnableSwitch(SolArkBaseSwitch):
    """Switch for enabling/disabling generator charge (register 129)."""

    def __init__(
        self,
        platform_name: str,
        hub: SolArkModbusHub,
        device_info: dict,
    ) -> None:
        super().__init__(
            platform_name=platform_name,
            hub=hub,
            device_info=device_info,
            key=GEN_CHARGE_ENABLE_KEY,
            name_suffix="Generator Charge Enable",
            icon="mdi:engine",
        )

    async def async_turn_on(self, **kwargs) -> None:
        """Enable generator charge."""
        success = await self.coordinator.hass.async_add_executor_job(
            self._hub.set_gen_charge_enable, True
        )
        if success:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Disable generator charge."""
        success = await self.coordinator.hass.async_add_executor_job(
            self._hub.set_gen_charge_enable, False
        )
        if success:
            await self.coordinator.async_request_refresh()
