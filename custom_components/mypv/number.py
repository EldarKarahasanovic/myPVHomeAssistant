from homeassistant.components.number import NumberEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import UnitOfTemperature, CONF_HOST

from .const import DOMAIN, DATA_COORDINATOR
from .coordinator import MYPVDataUpdateCoordinator
import logging

_LOGGER = logging.getLogger(__name__)

DEFAULT_MIN_VALUE = 30
DEFAULT_MAX_VALUE = 70
DEFAULT_STEP = 0.1
DEFAULT_MODE = "slider"

async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Set up the WWBoost number entity."""
    coordinator: MYPVDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    host = entry.data[CONF_HOST]
    async_add_entities([WWBoost(coordinator, host, entry.title)], True)

class WWBoost(CoordinatorEntity, NumberEntity):
    """Representation of the WWBoost number entity"""

    def __init__(self, coordinator, host, name):
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._name = "Warmwassersicherstellung"
        self._device_name = name
        self._host = host
        self._min_value = DEFAULT_MIN_VALUE
        self._max_value = DEFAULT_MAX_VALUE
        self._value = 50
        self._step = DEFAULT_STEP
        self._unit_of_measurement = UnitOfTemperature.CELSIUS
        self._mode = DEFAULT_MODE
        self.serial_number = self.coordinator.data["info"]["sn"]
        self._model = self.coordinator.data["info"]["device"]
        self._number = f"ww1boost_{self._host}"
    
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
        """Return a unique id based on device serial and variable."""
        return f"{self.serial_number}_{self._number}"
    
    @property
    def entity_id(self):
        """Return the entity id for this number."""
        return f"number.warmwassersicherstellung_{self.serial_number}"
    
    @property
    def name(self):
        """Return the display name of this entity."""
        return self._name

    @property
    def native_min_value(self):
        """Return the minimum value of this number."""
        return self._min_value

    @property
    def native_max_value(self):
        """Return the maximum value of this number."""
        return self._max_value

    @property
    def native_value(self):
        """Return the current value of this number."""
        return self._value
    
    @property
    def native_step(self):
        """Return the step size for this number."""
        return self._step
    
    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement for this number."""
        return self._unit_of_measurement
    
    @property
    def mode(self):
        return self._mode

    async def async_set_value(self, value: float):
        """Set a new value for this number."""
        if self._min_value <= value <= self._max_value:
            self._value = value
            self.async_write_ha_state()
        else:
            _LOGGER.error("Value %s is out of range [%s, %s]", value, self._min_value, self._max_value)