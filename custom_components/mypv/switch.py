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

class BoostSwitch(SwitchEntity):
    def __init__(self, host):
        """Initialize the switch"""
        self._name = "Toggle switch"
        self._host = host
        self._is_on = False
    
    @property
    def is_on(self):
        return self._is_on

    @property
    def name(self):
        return self._name
    
    async def async_turn_on(self):
        self._is_on = True
        await self.switch_state_update(1)
        self.async_write_ha_state()

    async def async_turn_off(self):
        self._is_on = False
        await self.async_toggle_switch(0)
        self.async_write_ha_state()
    
    async def async_toggle_switch(self, mode):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{self._host}/data.jsn?devmode={mode}") as response:
                if response.status != 200:
                    _LOGGER.error(f"Failed to turn on/off the device {self._entity_id}")