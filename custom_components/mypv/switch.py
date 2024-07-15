"""Switch entity"""

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST

import logging
import aiohttp

from .const import DOMAIN, DATA_COORDINATOR
from .coordinator import MYPVDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the toggle switch."""
    coordinator: MYPVDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        DATA_COORDINATOR
    ]

    host = entry.data[CONF_HOST]
    async_add_entities([ToggleSwitch(coordinator, host)], True)

class ToggleSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, host):
        """Initialize the switch"""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._name = "Device state"
        self._host = host
    
    @property
    def is_on(self):
        return self.coordinator.data["setup"].get("devmode", False)

    @property
    def name(self):
        return self._name
    
    async def async_turn_on(self):
        await self.async_toggle_switch(1)
        self.async_write_ha_state()

    async def async_turn_off(self):
        await self.async_toggle_switch(0)
        self.async_write_ha_state()
    
    async def async_toggle_switch(self, mode):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{self._host}/data.jsn?devmode={mode}") as response:
                if response.status != 200:
                    _LOGGER.error(f"Failed to turn on/off the device {self._entity_id}")
                else:
                    await self.coordinator.async_request_refresh()