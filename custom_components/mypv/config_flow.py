import logging
import voluptuous as vol
import ipaddress
import aiohttp
import asyncio
import socket
from aiohttp import ClientTimeout

from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv

from homeassistant.const import (
    CONF_HOST,
    CONF_MONITORED_CONDITIONS,
)
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN, SENSOR_TYPES  # pylint:disable=unused-import

_LOGGER = logging.getLogger(__name__)

DEFAULT_MONITORED_CONDITIONS = [
    "temp1"
]

@callback
def mypv_entries(hass: HomeAssistant):
    """Return the hosts for the domain."""
    return set(
        (entry.data[CONF_HOST]) for entry in hass.config_entries.async_entries(DOMAIN)
    )

class MypvConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Mypv config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._errors = {}
        self._info = {}
        self._host = None
        self._filtered_sensor_types = {}
        self._devices = {}

    def _host_in_configuration_exists(self, host) -> bool:
        """Return True if host exists in configuration."""
        return host in mypv_entries(self.hass)

    async def _get_sensor(self, host):
        """Fetch sensor data and update _filtered_sensor_types."""
        async with aiohttp.ClientSession() as session:
            try:
                timeout = ClientTimeout(total=5)
                async with session.get(f"http://{host}/data.jsn", timeout=timeout) as response:
                    if response.status == 200:
                        data = await response.json()
                        json_keys = set(data.keys())
                        self._filtered_sensor_types = {}

                        for key, value in SENSOR_TYPES.items():
                            if key in json_keys:
                                self._filtered_sensor_types[key] = value[0]
                        
                        if not self._filtered_sensor_types:
                            _LOGGER.warning("No matching sensors found on the device.")
                    else:
                        self._filtered_sensor_types = {}
                        _LOGGER.error(f"Can't connect to {host}: Bad HTTP Request status")

            except aiohttp.ClientError as e:
                _LOGGER.error(f"Failed to connect to {host}: {e}")
                self._filtered_sensor_types = {}
            except asyncio.TimeoutError as e:
                _LOGGER.error(f"Timeout error occured on {host}: {e}")
                self._filtered_sensor_types = {}

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        translations = self.hass.data[DOMAIN]["translations"]
        return self.async_show_menu(
            step_id="user",
            menu_options={
                "ip_known": translations.get("menu_options.ip_known", "IP address"),
                "ip_unknown": translations.get("menu_options.ip_unknown", "IP subnet scan"),
                "automatic_scan" : translations.get("menu_options.automatic_scan", "Automatic scan for my-PV devices in your local network")
            },
        )  
    
    async def async_step_ip_known(self, user_input=None):
        if user_input is not None:
            self._host = user_input[CONF_HOST]
            if self.is_valid_ip(self._host):
                device = await self.check_ip_device(self._host)
                if device:
                    if not self._host_in_configuration_exists(self._host):
                        self._devices[self._host] = f"{device} ({self._host})"
                        await self._get_sensor(self._host)
                        return await self.async_step_sensors()
                    else:
                        self._errors[CONF_HOST] = "host_already_configured"
                else:
                    self._errors[CONF_HOST] = "could_not_connect"
            else:
                self._errors[CONF_HOST] = "invalid_ip"

        user_input = user_input or {CONF_HOST: "192.168.0.0"}

        ip_known_schema = vol.Schema(
            {vol.Required(CONF_HOST, default="192.168.0.0"): str}
        )
        return self.async_show_form(
            step_id="ip_known",
            data_schema=ip_known_schema,
            errors=self._errors
        )
    
    async def async_step_ip_unknown(self, user_input=None):
        self._errors = {}
        if user_input is not None:
            subnet = user_input["subnet"]
            if self.is_valid_subnet(subnet):
                self._devices = await self.scan_devices(subnet)
                if self._devices:
                    return await self.async_step_select_device()
                else:
                    self._errors["base"] = "no_devices_found"
            else:
                self._errors["base"] = "invalid_subnet"
            
        ip_unknown_schema = vol.Schema(
            {vol.Required("subnet", default="192.168.0"): str}
        )

        return self.async_show_form(
            step_id="ip_unknown",
            data_schema=ip_unknown_schema,
            errors=self._errors,
        )  
    
    async def async_step_automatic_scan(self, user_input=None):
        self._devices = await self.scan_devices(self.get_subnet(self.get_own_ip()))
        if not self._devices:
            return self.async_abort(reason="no_devices_found")
        return await self.async_step_select_device()
    
    async def async_step_select_device(self, user_input=None):
        self._errors = {}
        if user_input is not None:
            self._host = list(self._devices.keys())[list(self._devices.values()).index(user_input["device"])]
            await self._get_sensor(self._host)
            return await self.async_step_sensors()        
        
        select_device_schema = vol.Schema({
            vol.Required("device"): vol.In(list(self._devices.values()))
        })
        
        return self.async_show_form(
            step_id="select_device",
            data_schema=select_device_schema,
            description_placeholders={"devices": ", ".join(self._devices.values())},
            errors=self._errors
        )  
        
    def is_valid_ip(self, ip):
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            _LOGGER.error("Invalid IP entered")
            return False
    
    def is_valid_subnet(self, subnet):
        cntPeriod = subnet.count('.')
        if cntPeriod != 2:
            _LOGGER.error("Invalid subnet")
            return False
        ip = subnet + ".0"
        return self.is_valid_ip(ip)
    
    def get_own_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = None
            _LOGGER.error("Unable to get IP address")
        finally:
            s.close()
        return ip
    
    def get_subnet(self, ip):
        if self.is_valid_ip(ip):
            octets = ip.split('.')
            subnet = f"{octets[0]}.{octets[1]}.{octets[2]}"
            return subnet
        return None
        
    async def check_ip_device(self, ip):
        async with aiohttp.ClientSession() as session:
            return await self.check_device(session, ip)
    
    async def scan_devices(self, subnet):
        devices = {}
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(1, 255):
                ip = f"{subnet}.{i}"
                tasks.append(self.check_device(session, ip))

            results = await asyncio.gather(*tasks)

            for ip, device_name in zip([f"{subnet}.{i}" for i in range(1, 255)], results):
                if device_name is not None and not self._host_in_configuration_exists(ip):
                    devices[ip] = f"{device_name} ({ip})"

        return devices
    
    async def check_device(self, session, ip):
        try:
            timeout = ClientTimeout(total=15)
            async with session.get(f"http://{ip}/mypv_dev.jsn", timeout=timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("device")
                else:
                    return None
        except aiohttp.ClientError:
            return None
        except asyncio.TimeoutError:
            return None

    async def async_step_sensors(self, user_input=None):
        """Handle the sensor selection step."""
        self._errors = {}
        if user_input is not None:                
            return self.async_create_entry(
                title=f"{self._devices[self._host]}",
                data={
                    CONF_HOST: self._host,
                    CONF_MONITORED_CONDITIONS: user_input[CONF_MONITORED_CONDITIONS],
                },
            )

        setup_schema = vol.Schema(
            {
                vol.Required(
                    CONF_MONITORED_CONDITIONS, default=DEFAULT_MONITORED_CONDITIONS
                ): cv.multi_select(self._filtered_sensor_types),
            }
        )

        return self.async_show_form(
            step_id="sensors", data_schema=setup_schema, errors=self._errors
        )

    async def async_step_import(self, user_input=None):
        """Import a config entry."""
        if self._host_in_configuration_exists(user_input[CONF_HOST]):
            return self.async_abort(reason="host_exists")
        self._host = user_input[CONF_HOST]
        if not await self.check_ip_device(self._host):
            return self.async_abort(reason="invalid_ip_address")
        await self._get_sensor(self._host)
        return await self.async_step_sensors(user_input)