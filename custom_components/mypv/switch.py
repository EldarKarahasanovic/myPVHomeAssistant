"""Switch entity"""

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import CONF_HOST

from .const import DOMAIN, DATA_COORDINATOR
from .coordinator import MYPVDataUpdateCoordinator


import logging
import aiohttp

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the SwitchBoost switch."""
    host = entry.data[CONF_HOST]
    coordinator: MYPVDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        DATA_COORDINATOR
    ]
    async_add_entities([BoostSwitch(host, coordinator)], True)
    return True

def switch_state_update(coordinator):
    switchState = coordinator.data["setup"]["devmode"]
    return switchState == 1

class BoostSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, host, coordinator):
        """Initialize the switch"""
        super().__init__(coordinator)
        self._name = "Toggle switch"
        self._host = host
        self._is_on = switch_state_update(self.coordinator)
    
    @property
    def is_on(self):
        return self._is_on

    @property
    def name(self):
        return self._name
    
    async def async_turn_on(self):
        self._is_on = True
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{self._host}/data.jsn?devmode=1") as response:
                if response.status != 200:
                    _LOGGER.error(f"Failed to turn on the device: {self._name}")
        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()

    
    async def async_turn_off(self):
        self._is_on = False
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{self._host}/data.jsn?devmode=0") as response:
                if response.status != 200:
                    _LOGGER.error(f"Failed to turn off the device: {self._name}")

        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()
    
    async def async_update(self) -> None:
        await super().async_update()
        self._is_on = switch_state_update(self.coordinator)
        self.async_write_ha_state()