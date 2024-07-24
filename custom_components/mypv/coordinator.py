"""Provides the MYPV DataUpdateCoordinator."""
from datetime import timedelta
import logging
import requests
import json
import aiohttp

from async_timeout import timeout
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, WIFI_METER_NAME

_LOGGER = logging.getLogger(__name__)


class MYPVDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching MYPV data."""

    def __init__(self, hass: HomeAssistant, *, config: dict, options: dict):
        """Initialize global NZBGet data updater."""
        self._host = config[CONF_HOST]
        self._info = None
        self._setup = None
        self._next_update = 0
        # self._data = await self.get_datasource(self._host)
        update_interval = timedelta(seconds=10)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> dict:
        """Fetch data from NZBGet."""

        def _update_data() -> dict:
            """Fetch data from NZBGet via sync functions."""
            data = self.data_update()
            if self._info is None:
                self._info = self.info_update()

            self._setup = self.setup_update()

            return {
                "data": data,
                "info": self._info,
                "setup": self._setup,
            }

        try:
            async with timeout(4):
                return await self.hass.async_add_executor_job(_update_data)
        except Exception as error:
            raise UpdateFailed(f"Invalid response from API: {error}") from error

    def data_update(self):
        """Update inverter data."""
        try:
            response = requests.get(f"http://{self._host}/data.jsn")
            data = json.loads(response.text)
            _LOGGER.debug(data)
            return data
        except:
            pass

    def info_update(self):
        """Update inverter info."""
        try:
            response = requests.get(f"http://{self._host}/mypv_dev.jsn")
            info = json.loads(response.text)
            _LOGGER.debug(info)
            return info
        except:
            pass

    def setup_update(self):
        """Update inverter info."""
        try:
            response = requests.get(f"http://{self._host}/setup.jsn")
            info = json.loads(response.text)
            _LOGGER.debug(info)
            return info
        except:
            pass
    
    async def get_datasource(self, host):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{host}/mypv_dev.jsn") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("device") == WIFI_METER_NAME:
                        return "monitorjson"
                    else:
                        return "data.jsn"
                else:
                    _LOGGER.error("Failed to connect to your device")