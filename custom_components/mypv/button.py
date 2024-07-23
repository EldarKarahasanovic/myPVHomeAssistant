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
    boostButton = MYPVButton(hass, coordinator, host, "mdi:heat-wave", "Boost button", entry.title)
    ww1boostButton = MYPVButton(hass, coordinator, host, "mdi:content-save", "Save warmwater boost", entry.title)
    entities.extend([boostButton, ww1boostButton])
    async_add_entities(entities)

    return True

class MYPVButton(CoordinatorEntity, ButtonEntity):
    def __init__(self, hass, coordinator, host, icon, name, deviceName) -> None:
        """Initialize the button"""
        super().__init__(coordinator)
        self._hass = hass
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
            else:
                _LOGGER.error("ww1boost incoming")
                number_entity_id = None
                for entity in self._hass.states.async_all():
                    if entity.domain == "number":
                        number_entity_id = entity.entity_id
                        break
                _LOGGER.warning(f"Number entity ID: {number_entity_id}")
                if number_entity_id:
                    number_state = self._hass.states.get(number_entity_id)
                    _LOGGER.warning(f"Number state: {number_state}")
                    if number_state:
                        number_value = number_state.state
                        _LOGGER.warning(f"Number value: {number_value}")
                        async with session.get(f"http://{self._host}/data.jsn?ww1boost={number_value*10}") as response3:
                            if response3.status != 200:
                                _LOGGER.error("Failed to save ww1boost settings")