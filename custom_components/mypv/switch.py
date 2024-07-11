"""Switch entity"""

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST

import logging
import requests

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the SwitchBoost switch."""
    host = entry.data[CONF_HOST]
    async_add_entities([BoostSwitch(host)], True)
    return True

class BoostSwitch(SwitchEntity):
    def __init__(self, host):
        """Initialize the switch"""
        self._name = "ww1boost switch"
        self._is_on = False
        self._host = host
    
    @property
    def is_on(self):
        return self._is_on

    @property
    def name(self):
        return self._name
    
    async def async_turn_on(self, **kwargs):
        self._is_on = True
        try:
            response = requests.get(f"http://{self._host}/data.jsn?devmode=1")
            response.raise_for_status()
        except requests.RequestException as e:
            _LOGGER.error(f"Failed to turn on the device: {e}")
        self.async_write_ha_state()

    
    async def async_turn_off(self, **kwargs):
        self._is_on = False
        try:
            response = requests.get(f"http://{self._host}/data.jsn?devmode=0")
            response.raise_for_status()
        except requests.RequestException as e:
            _LOGGER.error(f"Failed to turn off the device: {e}")
        self.async_write_ha_state()