"""Provides the my-PV DataUpdateCoordinator."""

from datetime import timedelta
import logging
import aiohttp
import asyncio
from aiohttp import ClientTimeout

from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, WIFI_METER_NAME

_LOGGER = logging.getLogger(__name__)


class MYPVDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching my-PV data."""

    def __init__(self, hass: HomeAssistant, *, config: dict, options: dict):
        """Initialize my-PV coordinator."""
        self._host = config[CONF_HOST]
        self._info = None
        self._setup = None
        self._data = "data.jsn"
        update_interval = timedelta(seconds=10)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> dict:
        """Fetch data."""
        # Re-use Home Assistant's shared aiohttp session instead of opening a
        # new ClientSession on every refresh. A new session cannot re-use any
        # connection, so at the default 10 second interval this opened a fresh
        # TCP connection for every request against a small embedded web server.
        session = async_get_clientsession(self.hass)

        if self._info is None:
            self._info = await self.async_update_info(session)
            if self._info is None:
                raise UpdateFailed("Could not connect to your my-PV device")

        if self._data != "monitorjson":
            self._setup = await self.async_update_setup(session)
            if self._setup is None:
                raise UpdateFailed("Could not connect to your my-PV device")

        data = await self.async_update_data(session)
        if data is None:
            raise UpdateFailed("Could not connect to your my-PV device")

        return {
            "data": data,
            "info": self._info,
            "setup": self._setup,
        }

    async def async_update_info(self, session):
        try:
            timeout = ClientTimeout(total=10)
            async with session.get(
                f"http://{self._host}/mypv_dev.jsn", timeout=timeout
            ) as response:
                if response.status == 200:
                    info = await response.json()
                    if info.get("device") == WIFI_METER_NAME:
                        self._data = "monitorjson"
                    return info
                else:
                    _LOGGER.error(
                        f"Failed to connect to your my-PV device (status code: {response.status})"
                    )
                    return None
        except aiohttp.ClientConnectionError as e:
            _LOGGER.error(f"ClientConnectionError in async_update_info: {e}")
            return None
        except aiohttp.ClientPayloadError as e:
            _LOGGER.error(f"ClientPayloadError in async_update_info: {e}")
            return None
        except aiohttp.ClientResponseError as e:
            _LOGGER.error(f"ClientResponseError in async_update_info: {e}")
            return None
        except aiohttp.ClientTimeout as e:
            _LOGGER.error(f"ClientTimeout error in async_update_info: {e}")
            return None
        except asyncio.TimeoutError as e:
            _LOGGER.error(f"TimeoutError in async_update_info: {e}")
            return None

    async def async_update_setup(self, session):
        try:
            timeout = ClientTimeout(total=5)
            async with session.get(
                f"http://{self._host}/setup.jsn", timeout=timeout
            ) as response:
                if response.status == 200:
                    setup = await response.json()
                    return setup
                else:
                    _LOGGER.error(
                        f"Failed to connect to your my-PV device (status code: {response.status})"
                    )
                    return None
        except aiohttp.ClientError as e:
            _LOGGER.error(f"ClientError in async_update_setup: {e}")
            return None
        except asyncio.TimeoutError as e:
            _LOGGER.error(f"TimeoutError in async_update_setup: {e}")
            return None

    async def async_update_data(self, session):
        try:
            timeout = ClientTimeout(total=5)
            async with session.get(
                f"http://{self._host}/{self._data}", timeout=timeout
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    _LOGGER.error(
                        f"Failed to connect to your my-PV device (status code: {response.status})"
                    )
                    return None
        except aiohttp.ClientError as e:
            _LOGGER.error(f"ClientError in async_update_data: {e}")
            return None
        except asyncio.TimeoutError as e:
            _LOGGER.error(f"TimeoutError in async_update_data: {e}")
            return None
