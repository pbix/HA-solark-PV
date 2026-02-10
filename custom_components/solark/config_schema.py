"""Configuration schema."""

import voluptuous as vol

from homeassistant.const import CONF_HOST, CONF_NAME, CONF_SCAN_INTERVAL
import homeassistant.helpers.config_validation as cv


def get_schema(name: str, host: str, scan_interval: int) -> vol.Schema:
    """Get the full data schema."""
    return vol.Schema(_get_schema_entries(name, host, scan_interval))


def get_reconfig_schema(host: str, scan_interval: int) -> vol.Schema:
    """Get the reconfiguration data schema."""
    return vol.Schema(_get_reconfig_schema_entries(host, scan_interval))


def _get_schema_entries(name: str, host: str, scan_interval: int) -> set:
    """Get the full data schema."""
    return {
        vol.Required(CONF_NAME, default=name): cv.string,
    } | _get_reconfig_schema_entries(host, scan_interval)


def _get_reconfig_schema_entries(host: str, scan_interval: int) -> set:
    """Get the reconfiguration data schema."""
    return {
        vol.Required(CONF_HOST, default=host): cv.string,
        vol.Required(CONF_SCAN_INTERVAL, default=scan_interval): cv.positive_int,
    }
