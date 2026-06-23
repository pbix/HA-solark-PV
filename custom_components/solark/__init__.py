"""The SolArk Modbus Integration."""

import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_SCAN_INTERVAL, Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .hub import SolArkModbusHub

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.NUMBER, Platform.SWITCH, Platform.TIME, Platform.SELECT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up a SolArk modbus."""
    # Use entry.options as overrides for entry.data
    config = {**entry.data, **entry.options}
    name = config[CONF_NAME]
    scan_interval = config[CONF_SCAN_INTERVAL]
    host = config[CONF_HOST]

    _LOGGER.debug("Setup %s.%s", DOMAIN, name)

    hub = SolArkModbusHub(hass, name, host, scan_interval)
    # Register the hub.
    hass.data.setdefault(DOMAIN, {})
    # TODO - This can fail if the name is changed in reconfigure. Use guaranteed unique id. Replace with:
    #  hub_entry_id = entry.entry_id
    #  hass.data[DOMAIN][entry_id] = {"hub": hub}
    hass.data[DOMAIN][name] = {"hub": hub}

    # Make sure the first data read completes before adding entities. This prevents empty/None data
    await hub.async_config_entry_first_refresh()

    # Forward to the normal sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register the options update listener
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry):
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload SolArk Modbus entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if not unload_ok:
        return False

    # Stop the coordinator safely and close the Modbus client
    name = entry.data[CONF_NAME]
    # TODO - This can fail if the name is changed in reconfigure. Use guaranteed unique id. Replace with:
    #  hub_entry_id = entry.entry_id
    #  hub: SolArkModbusHub = hass.data[DOMAIN][entry_id]["hub"]
    hub_data = hass.data.get(DOMAIN, {}).get(name)
    if hub_data is None:
        _LOGGER.warning(
            "Tried to unload hub '%s', but it was never loaded or already removed", name
        )
        return True  # HA expects True even if nothing to unload

    hub: SolArkModbusHub = hub_data["hub"]
    try:
        await hub.async_stop()  # cancels updates
        _LOGGER.info("Stopped SolArk hub '%s'", name)
    except Exception as exc:
        _LOGGER.error("Error stopping SolArk hub '%s': %s", name, exc, exc_info=True)

    # Remove hub reference safely
    hass.data[DOMAIN].pop(name, None)
    _LOGGER.debug("Removed hub reference for '%s'", name)

    return True
