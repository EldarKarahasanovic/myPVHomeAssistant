"""Switch entity"""

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST

import logging
import aiohttp

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the SwitchBoost switch."""
    host = entry.data[CONF_HOST]
    async_add_entities([BoostSwitch(host)], True)
    return True

class BoostSwitch(SwitchEntity):
    def __init__(self, host):
        """Initialize the switch"""
        self._name = "Toggle switch"
        self._is_on = True
        self._host = host
    
    @property
    def is_on(self):
        return self._is_on

    @property
    def name(self):
        return self._name
    
    async def async_turn_on(self, **kwargs):
        self._is_on = True
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{self._host}/data.jsn?devmode=1") as response:
                if response.status != 200:
                    _LOGGER.error(f"Failed to turn on the device: {self._name}")

        self.async_write_ha_state()

    
    async def async_turn_off(self, **kwargs):
        self._is_on = False
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{self._host}/data.jsn?devmode=0") as response:
                if response.status != 200:
                    _LOGGER.error(f"Failed to turn off the device: {self._name}")

        self.async_write_ha_state()
