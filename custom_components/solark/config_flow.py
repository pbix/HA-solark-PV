"""Handle the Configuration Flow."""

from urllib.parse import urlparse

from homeassistant.config_entries import (
    CONN_CLASS_LOCAL_POLL,
    ConfigFlow,
    ConfigFlowResult,
)
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant, callback

from . import config_schema
from .const import DEFAULT_HOST, DEFAULT_NAME, DEFAULT_SCAN_INTERVAL, DOMAIN


@callback
def solark_modbus_entries(hass: HomeAssistant):
    """Return the hosts already configured."""
    return {
        entry.data[CONF_HOST] for entry in hass.config_entries.async_entries(DOMAIN)
    }


def host_valid(netloc):
    """Check to see if the user input hostname is valid."""
    parsed = urlparse(f"//{netloc}")

    try:
        # If it not a URL it might be a serial port.
        if (parsed.port is None) and (
            (parsed.hostname is None) or (parsed.hostname[0:3] == "com")
        ):
            return True

    # Hostname made no sense.  Error return
    except:  # noqa: E722
        return False

    return True


class SolArkModbusConfigFlow(ConfigFlow, domain=DOMAIN):
    """SolArk Modbus configflow."""

    VERSION = 1
    CONNECTION_CLASS = CONN_CLASS_LOCAL_POLL

    def _host_in_configuration_exists(self, host) -> bool:
        """Return True if host exists in configuration."""
        if host in solark_modbus_entries(self.hass):
            return True
        return False

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]

            if self._host_in_configuration_exists(host):
                errors[CONF_HOST] = "host_already_configured"
            elif not host_valid(host):
                errors[CONF_HOST] = "invalid_host"
            else:
                # Disallow creation of another device with a host used by an existing device
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="",
                    # title=user_input[CONF_NAME],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=config_schema.get_schema(
                DEFAULT_NAME, DEFAULT_HOST, DEFAULT_SCAN_INTERVAL
            ),
            errors=errors,
        )

    async def async_step_reconfigure(self, user_input=None) -> ConfigFlowResult:
        """Handle the reconfiguration step."""
        errors = {}

        if user_input is not None:
            return self.async_update_reload_and_abort(
                self._get_reconfigure_entry(), data_updates=user_input
            )

        existing_entry = self._get_reconfigure_entry()

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=config_schema.get_reconfig_schema(
                existing_entry.data[CONF_HOST],
                existing_entry.data[CONF_SCAN_INTERVAL],
            ),
            errors=errors,
        )
