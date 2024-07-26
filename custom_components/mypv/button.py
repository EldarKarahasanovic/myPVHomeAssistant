import aiohttp
import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import CONF_HOST, CONF_DEVICE

from .const import DOMAIN, DATA_COORDINATOR, WIFI_METER_NAME, BOOST_BUTTON_NAME

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the boost button"""
    device_name = entry.data[CONF_DEVICE]
    if device_name != WIFI_METER_NAME:
        coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
        host = entry.data[CONF_HOST]
        entities = [
            MYPVButton(hass, coordinator, host, "mdi:heat-wave", BOOST_BUTTON_NAME, entry.title),
            MYPVButton(hass, coordinator, host, "mdi:thermometer", "Single Boost", entry.title)
        ]
        async_add_entities(entities)

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
        """Handle button press."""
        async with aiohttp.ClientSession() as session:
            if self._name == BOOST_BUTTON_NAME:
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
                number_entity_id = None

                for entity in self._hass.states.async_all():
                    ip_address = f"{self._host}"
                    ip_address_w_underscore = ip_address.replace(".", "_")
                    if entity.domain == "number" and f"hot_water_assurance_{ip_address_w_underscore}" in entity.entity_id:
                        number_entity_id = entity.entity_id
                        break

                if not number_entity_id:
                    _LOGGER.error("No matching number entity found")
                    return

                number_state = self._hass.states.get(number_entity_id)
                if number_state:
                    try:
                        number_value = float(number_state.state)
                        async with session.get(f"http://{self._host}/data.jsn?ww1boost={number_value*10}") as response3:
                            if response3.status != 200:
                                _LOGGER.error("Failed to save ww1boost settings")
                    except ValueError:
                        _LOGGER.error(f"Failed to convert number state to float: {number_state.state}")
                else:
                    _LOGGER.error(f"Failed to retrieve number state for entity_id: {number_entity_id}")