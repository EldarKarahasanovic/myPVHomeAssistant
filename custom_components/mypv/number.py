import logging
import aiohttp
from homeassistant.components.number import NumberEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, DATA_COORDINATOR

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Setup myPV numbers from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    # Wir nutzen entry.title, genau wie in der sensor.py
    device_name = entry.title
    
    async_add_entities([
        MyPVMaxPwr(coordinator, device_name),
        MyPVWWBoost(coordinator, device_name)
    ])

class MyPVNumberEntity(CoordinatorEntity, NumberEntity):
    """Gemeinsame Basis für myPV Slider mit korrekter Device Info."""
    def __init__(self, coordinator, device_name):
        super().__init__(coordinator)
        self._device_name = device_name
        # Wir holen die Hardware-Infos exakt wie in der sensor.py
        self.serial_number = self.coordinator.data["info"]["sn"]
        self.model = self.coordinator.data["info"]["device"]
        self._host = self.coordinator._host # Zugriff auf den Host im Coordinator

    @property
    def device_info(self):
        """Verknüpft die Entität exakt mit dem Hauptgerät."""
        return {
            "identifiers": {(DOMAIN, self.serial_number)},
            "name": self._device_name,
            "manufacturer": "my-PV",
            "model": self.model,
        }

class MyPVMaxPwr(MyPVNumberEntity):
    """Slider für die maximale Leistung."""
    @property
    def name(self):
        return f"{self._device_name} Maximum Power"

    @property
    def unique_id(self):
        return f"{self.serial_number} Maximum Power"

    @property
    def native_value(self):
        val = self.coordinator.data.get("setup", {}).get("maxpwr")
        return float(val) if val is not None else None

    @property
    def native_unit_of_measurement(self):
        return "%"

    @property
    def native_min_value(self):
        return 0
    
    @property
    def native_max_value(self):
        return 100

    async def async_set_native_value(self, value):
        url = f"http://{self._host}/setup.jsn?maxpwr={int(value)}"
        async with aiohttp.ClientSession() as session:
            await session.get(url, timeout=5)
            await self.coordinator.async_request_refresh()

class MyPVWWBoost(MyPVNumberEntity):
    """Slider für die Warmwasser-Sicherstellung."""
    @property
    def name(self):
        return f"{self._device_name} Hot Water Boost"

    @property
    def unique_id(self):
        return f"{self.serial_number} Hot Water Boost"

    @property
    def native_value(self):
        val = self.coordinator.data.get("setup", {}).get("ww1boost")
        # Skalierung: Gerät liefert 500 für 50.0°C
        return float(val) / 10.0 if val is not None else None

    @property
    def native_unit_of_measurement(self):
        return "°C"

    @property
    def native_min_value(self):
        return 20
    
    @property
    def native_max_value(self):
        return 90

    async def async_set_native_value(self, value):
        # Skalierung zurück: HA liefert 45.5 -> 455 für das Gerät
        target_val = int(value * 10)
        url = f"http://{self._host}/setup.jsn?ww1boost={target_val}"
        async with aiohttp.ClientSession() as session:
            await session.get(url, timeout=5)
            await self.coordinator.async_request_refresh()
