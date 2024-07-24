"""Provides the MYPV DataUpdateCoordinator."""
from datetime import timedelta
import logging
import aiohttp
import asyncio
from aiohttp import ClientTimeout

from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, WIFI_METER_NAME

_LOGGER = logging.getLogger(__name__)


class MYPVDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching MYPV data."""

    def __init__(self, hass: HomeAssistant, *, config: dict):
        """Initialize global NZBGet data updater."""
        self._host = config[CONF_HOST]
        self._info = None
        self._setup = None
        self._next_update = 0
        self._data = "data.jsn"
        update_interval = timedelta(seconds=10)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> dict:
        """Fetch data"""
        try:
            async with aiohttp.ClientSession() as session:
                if self._info is None:
                    self._info = await self.async_update_info(session)
                    if self._info is None:
                        raise Exception("Could not connect to your my-PV device")
                if self._data != "monitorjson":
                    self._setup = await self.async_update_setup(session)
                    if self._setup is None:
                        raise Exception("Could not connect to your my-PV device")
                data = await self.async_update_data(session)
                if data is None:
                    raise Exception("Could not connect to your my-PV device")
                
                return {
                    "data" : data,
                    "info" : self._info,
                    "setup" : self._setup,
                }
        except Exception as e:
            _LOGGER.error(f"Error fetching data from the API: {e}")
        
    async def async_update_info(self, session):
        try:
            timeout = ClientTimeout(total=5)
            async with session.get(f"http://{self._host}/mypv_dev.jsn", timeout=timeout) as response:
                if response.status == 200:
                    info = await response.json()
                    if info.get("device") == WIFI_METER_NAME:
                        self._data = "monitorjson"
                    return info
                else:
                    _LOGGER.error("Failed to connect to your my-PV device")
                    return None
        except aiohttp.ClientError:
            return None
        except asyncio.TimeoutError:
            return None
    
    async def async_update_setup(self, session):
        try:
            timeout = ClientTimeout(total=5)
            async with session.get(f"http://{self._host}/setup.jsn", timeout=timeout) as response:
                if response.status == 200:
                    setup = await response.json()
                    return setup
                else:
                    _LOGGER.error("Failed to connect to your my-PV device")
                    return None
        except aiohttp.ClientError:
            return None
        except asyncio.TimeoutError:
            return None
        
    async def async_update_data(self, session):
        try:
            timeout = ClientTimeout(total=5)
            async with session.get(f"http://{self._host}/{self._data}", timeout=timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    _LOGGER.error("Failed to connect to your my-PV device")
                    return None
        except aiohttp.ClientError:
            return None
        except asyncio.TimeoutError:
            return None