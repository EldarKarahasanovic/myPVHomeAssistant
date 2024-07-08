"""Switch entity"""

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the SwitchBoost switch."""
    async_add_entities([BoostSwitch()], True)
    return True

class BoostSwitch(SwitchEntity):
    def __init__(self):
        """Initialize the switch"""
        self._name = "ww1boost switch"
        self._is_on = False
    
    @property
    def is_on(self):
        return self._is_on

    @property
    def name(self):
        return self._name
    
    async def async_turn_on(self, **kwargs):
        self._is_on = True
        _LOGGER.error("Switch turned on")
        self.async_write_ha_state()

    
    async def async_turn_off(self, **kwargs):
        self._is_on = False
        self.async_write_ha_state()

