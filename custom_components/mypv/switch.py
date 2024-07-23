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
    """Set up the toggle switch."""
    coordinator: MYPVDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    host = entry.data[CONF_HOST]
    
    # Retrieve existing entities
    existing_entities = hass.data.get(DOMAIN, {}).get(entry.entry_id, {}).get("entities", [])
    
    # Log details for debugging
    _LOGGER.warning(f"Existing Entities: {existing_entities}")
    _LOGGER.warning(f"Entry ID: {entry.entry_id}")
    
    # Check for existing entity with same unique_id
    if any(entity.unique_id == entry.unique_id for entity in existing_entities):
        _LOGGER.warning("Entity already set up, skipping.")
        return False  # Indicate setup did not add any new entities

    _LOGGER.warning("Adding toggle switch")
    new_entity = ToggleSwitch(coordinator, host, entry.title)
    async_add_entities([new_entity], True)
    
    # Store the new entity in hass.data for future reference
    hass.data.setdefault(DOMAIN, {}).setdefault(entry.entry_id, {}).setdefault("entities", []).append(new_entity)
    
    return True


class ToggleSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, host, name):
        """Initialize the switch"""
        super().__init__(coordinator)
        self._device_name = name
        self._name = "Device state"
        self._host = host
        self._switch = f"device_state_{self._host}"
        self._icon = "mdi:power"
        self._is_on = self.coordinator.data["setup"]["devmode"] if self.coordinator.data else False
        self._model = self.coordinator.data["info"]["device"]
        self.serial_number = self.coordinator.data["info"]["sn"]
    
    @property
    def is_on(self):
        if self.coordinator.data:
            self._is_on = self.coordinator.data["setup"]["devmode"]
        return self._is_on

    @property
    def name(self):
        return self._name
    
    @property
    def icon(self):
        return self._icon
    
    @property
    def device_info(self):
        """Return information about the device."""
        return {
            "identifiers": {(DOMAIN, self.serial_number)},
            "name": self._device_name,
            "manufacturer": "my-PV",
            "model": self._model,
        }
    
    @property
    def unique_id(self):
        """Return unique id based on device serial and variable."""
        return "{}_{}".format(self.serial_number, self._switch)
    
    async def async_turn_on(self):
        await self.async_toggle_switch(1)
        self._is_on = True
        await self.coordinator.async_refresh()
        self.async_write_ha_state()

    async def async_turn_off(self):
        await self.async_toggle_switch(0)
        self._is_on = False
        await self.coordinator.async_refresh()
        self.async_write_ha_state()
    
    async def async_toggle_switch(self, mode):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{self._host}/data.jsn?devmode={mode}") as response:
                if response.status != 200:
                    _LOGGER.error(f"Failed to turn on/off the device {self.unique_id}")