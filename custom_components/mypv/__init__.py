""" Integration for MYPV AC-Thor"""
import voluptuous as vol
import logging

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_MONITORED_CONDITIONS,
)
import homeassistant.helpers.config_validation as cv

from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.core import HomeAssistant

from .const import DOMAIN, SENSOR_TYPES, DATA_COORDINATOR, PLATFORMS
from .coordinator import MYPVDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
                vol.Required(CONF_MONITORED_CONDITIONS): vol.All(
                    cv.ensure_list, [vol.In(list(SENSOR_TYPES))]
                ),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    """Platform setup, do nothing."""
    hass.data.setdefault(DOMAIN, {})

    if DOMAIN not in config:
        return True

    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_IMPORT}, data=dict(config[DOMAIN])
        )
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Load the saved entities."""
    coordinator = MYPVDataUpdateCoordinator(
        hass,
        config=entry.data,
        options=entry.options,
    )

    await coordinator.async_refresh()

    # Reload entry when its updated.
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = {
        DATA_COORDINATOR: coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "switch", "button"])

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)