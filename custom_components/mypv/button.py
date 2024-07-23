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
    coordinator: MYPVDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    host = entry.data[CONF_HOST]

    entities = []
    boostButton = MYPVButton(coordinator, host, "mdi:heat-wave", "Boost button", entry.title)
    ww1boostButton = MYPVButton(coordinator, host, "mdi:content-save", "Save warmwater boost", entry.title)
    entities.extend([boostButton, ww1boostButton])
    async_add_entities([MYPVButton(coordinator, host, entry.title)], True)

    return True

class MYPVButton(CoordinatorEntity, ButtonEntity):
    def __init__(self, coordinator, host, icon, name, deviceName) -> None:
        """Initialize the button"""
        super().__init__(coordinator)
        self._icon = icon
        self._name = name
        self._device_name = deviceName
        self._host = host
        self._model = self.coordinator.data["info"]["device"]
        self.serial_number = self.coordinator.data["info"]["sn"]
        self._button = f"{self.name}_{self._host}"

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
            if self._name == "Boost button":
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
            #else:
                #async with session.get(f"http://{self._host}/data.jsn?ww1boost=")