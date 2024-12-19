"""The SolArk Modbus Integration."""
import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_SCAN_INTERVAL, Platform
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .const import DEFAULT_NAME, DEFAULT_SCAN_INTERVAL, DOMAIN
from .hub import SolArkModbusHub

_LOGGER = logging.getLogger(__name__)

SOLARK_MODBUS_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(
            CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
        ): cv.positive_int,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.Schema({cv.slug: SOLARK_MODBUS_SCHEMA})}, extra=vol.ALLOW_EXTRA
)

PLATFORMS = [Platform.SENSOR]

async def async_setup(hass, config):
    """Set up the SolArk modbus component."""
    hass.data[DOMAIN] = {}
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up a SolArk modbus."""
    name = entry.data[CONF_NAME]
    scan_interval = entry.data[CONF_SCAN_INTERVAL]
    host = entry.data[CONF_HOST]

    _LOGGER.debug("Setup %s.%s", DOMAIN, name)

    hub = SolArkModbusHub(hass, name, host, scan_interval)
    """Register the hub."""
    hass.data[DOMAIN][name] = {"hub": hub}

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass, entry):
    """Unload SolArk mobus entry."""
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

    hass.data[DOMAIN].pop(entry.data["name"])
    return True
