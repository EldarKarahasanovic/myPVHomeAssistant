"""Button entity"""

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import CONF_HOST

from .const import DOMAIN, DATA_COORDINATOR
from .coordinator import MYPVDataUpdateCoordinator

import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the boost button"""
    _LOGGER.warning("Set up button")
    coordinator: MYPVDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    host = entry.data[CONF_HOST]
    
    existing_entities = hass.data.get(DOMAIN, {}).get(entry.entry_id, {}).get("entities", [])
    _LOGGER.warning(f"Existing Entities button: {existing_entities}")
    _LOGGER.warning(f"Entry ID button: {entry.entry_id}")
    _LOGGER.warning(f"Entry UNIQUE ID button: {entry.unique_id}")
    if any(entity.unique_id == entry.entry_id for entity in existing_entities):
        _LOGGER.warning("Boost button already exists")
        return True 

    _LOGGER.warning("Adding boost button")
    async_add_entities([BoostButton(coordinator, host, entry.title)], True)

    return True

class BoostButton(CoordinatorEntity, ButtonEntity):
    def __init__(self, coordinator, host, name) -> None:
        """Initialize the button"""
        super().__init__(coordinator)
        self._icon = "mdi:heat-wave"
        self._host = host
        self._name = f"Boost button {self._host}"
        self._device_name = name
        self._model = self.coordinator.data["info"]["device"]
        self.serial_number = self.coordinator.data["info"]["sn"]
        self._button = f"boost_button_{self._host}"

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
        return "{} {}".format(self.serial_number, self._button)

    async def async_press(self) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{self._host}/data.jsn") as response:
                if response.status == 200:
                    data = await response.json()
                    boostActive = data.get("boostactive")
                    newBoost = not boostActive
                    async with session.get(f"http://{self._host}/data.jsn?bststrt={int(newBoost)}") as response2:
                        if response2.status != 200:
                            _LOGGER.error("Failed to (de-)activate boost")
                else:
                    _LOGGER.error("Failed to (de-)activate boost")