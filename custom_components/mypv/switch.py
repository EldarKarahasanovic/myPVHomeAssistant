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

class BoostSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, host, coordinator):
        """Initialize the switch"""
        super().__init__(coordinator)
        self._name = "Toggle switch"
        self._host = host
        self._is_on = self.switch_state_update()
    
    @property
    def is_on(self):
        return self._is_on

    @property
    def name(self):
        return self._name
    
    async def async_turn_on(self):
        await self.switch_state_update(1)
        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()

    
    async def async_turn_off(self):
        await self.async_toggle_switch(0)
        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()
    
    async def async_toggle_switch(self, mode):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{self._host}/data.jsn?devmode={mode}") as response:
                if response.status != 200:
                    _LOGGER.error(f"Failed to turn on/off the device {self._entity_id}")
    
    def switch_state_update(self):
        switchState = self.coordinator.data["setup"]["devmode"]
        return switchState == 1
    
    async def async_update(self) -> None:
        await super().async_update()
        self._is_on = self.switch_state_update()
        self.async_write_ha_state()