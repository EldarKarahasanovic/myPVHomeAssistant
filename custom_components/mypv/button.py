"""Button entity"""

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST

import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the boost button"""
    host = entry.data[CONF_HOST]
    async_add_entities([BoostButton(host)], True)

class BoostButton(ButtonEntity):
    def __init__(self, host) -> None:
        """Initialize the button"""
        self._icon = ""
        self._name = "Boost button"
        self._host = host

    @property
    def name(self):
        return self._name
    
    @property 
    def icon(self):
        return self._icon

    async def async_press(self) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{self._host}/data.jsn") as response:
                if response.status == 200:
                    data = await response.json()
                    boostActive = data.get("bststrt")
                    newBoost = not boostActive
                    async with session.get(f"http://{self._host}/data.jsn?bststrt={int(newBoost)}") as response2:
                        if response2.status != 200:
                            _LOGGER.error("Failed to (de-)activate boost")
                else:
                    _LOGGER.error("Faile to (de-)activate boost")