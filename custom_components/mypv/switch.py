"""Switch entity"""

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import CONF_HOST

import logging
import aiohttp

from .const import DOMAIN, DATA_COORDINATOR
from .coordinator import MYPVDataUpdateCoordinator

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
        self._name = "Device state"
        self._host = host
        self.coordinator = coordinator
        self._is_on = self.coordinator.data["setup"]["devmode"] == 1
    
    @property
    def is_on(self):
        return self._is_on

    @property
    def name(self):
        return self._name
    
    async def async_turn_on(self):
        self._is_on = True
        await self.async_toggle_switch(1)
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

    async def async_update(self):
        """Update the state of the switch based on the coordinator data."""
        await self.coordinator.async_request_refresh()
        self._is_on = self.coordinator.data["setup"]["devmode"] == 1
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
        await super().async_added_to_hass()