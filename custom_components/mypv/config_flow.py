"""Config flow for Kostal piko integration."""
import logging
import voluptuous as vol
import requests
import ipaddress
import aiohttp
import asyncio
from requests.exceptions import RequestException
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
        """Return True if site_id exists in configuration."""
        return host in mypv_entries(self.hass)
    """
    def _check_host(self, host) -> bool:
        Check if we can connect to the mypv.
        try:
            response = requests.get(f"http://{host}/mypv_dev.jsn", timeout=10)
            response.raise_for_status()
            self._info = response.json()
        except (ConnectTimeout, HTTPError) as e:
            self._errors[CONF_HOST] = "could_not_connect"
            _LOGGER.error(f"Connection error: {e}")
            return False
        except RequestException as e:
            self._errors[CONF_HOST] = "unexpected_error"
            _LOGGER.error(f"Unexpected error: {e}")
            return False
        return True
    """
    def _get_sensor(self, host):
        """Fetch sensor data and update _filtered_sensor_types."""
        try:
            response = requests.get(f"http://{host}/data.jsn", timeout=10)
            response.raise_for_status()
            data = response.json()
            json_keys = set(data.keys())
            self._filtered_sensor_types = {}

            for key, value in SENSOR_TYPES.items():
                if key in json_keys:
                    self._filtered_sensor_types[key] = value[0]  #damit nur das erste element genutzt wird

            if not self._filtered_sensor_types:
                _LOGGER.warning("No matching sensors found on the device.")
        except RequestException as e:
            _LOGGER.error(f"Error fetching sensor data: {e}")
            self._filtered_sensor_types = {}
    """
    async def async_step_user(self, user_input=None):
            Handle the initial step.
        if user_input is not None:
            self._host = user_input[CONF_HOST]
            if self._host_in_configuration_exists(self._host):
                self._errors[CONF_HOST] = "host_exists"
            else:
                can_connect = await self.hass.async_add_executor_job(
                    self._check_host, self._host
                )
                if (can_connect):
                    await self.hass.async_add_executor_job(self._get_sensor, self._host)
                    return await self.async_step_sensors()
        
        user_input = user_input or {CONF_HOST: "192.168.0.0"}

        setup_schema = vol.Schema(
            {vol.Required(CONF_HOST, default=user_input[CONF_HOST]): str}
        )

        return self.async_show_form(
            step_id="user", data_schema=setup_schema, errors=self._errors
        )
"""
    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        return self.async_show_menu(
            step_id="user",
            menu_options={
                "ip_known": "IP address",
                "ip_unknown": "IP subnet scan"
            },
        )  
    
    async def async_step_ip_known(self, user_input=None):
        if user_input is not None:
            self._host = user_input[CONF_HOST]
            if self.is_valid_ip(self._host):
                if await self.check_ip_device(self._host):
                    if not self._host_in_configuration_exists(self._host):
                        await self.hass.async_add_executor_job(self._get_sensor, self._host)
                        return await self.async_step_sensors()
                    else:
                        self._errors[CONF_HOST] = "host_already_configured"
                else:
                    self._errors[CONF_HOST] = "could_not_connect"
            else:
                self._errors[CONF_HOST] = "invalid_ip"

        user_input = user_input or {CONF_HOST: "192.168.0.0"}

        ip_known_schema = vol.Schema(
            {vol.Required(CONF_HOST, default="192.168.0.0"):str}
        )
        return self.async_show_form(
            step_id="ip_known",
            data_schema=ip_known_schema,
            errors=self._errors
        )
    
    async def async_step_ip_unknown(self, user_input=None):
        errors = {}
        if user_input is not None:
            subnet = user_input["subnet"]
            if self.is_valid_subnet(subnet):
                self._devices = await self.scan_devices(subnet)
                if self._devices:    
                    return await self.async_step_select_device()
                else:
                    errors["base"] = "no_devices_found"
            else:
                errors["base"] = "invalid_subnet"
            
        ip_unknown_schema = vol.Schema(
            {vol.Required("subnet", default="192.168.0"):str}
        )

        return self.async_show_form(
            step_id="ip_unknown",
            data_schema=ip_unknown_schema,
            errors=errors
        )  
    
    async def async_step_select_device(self, user_input=None):
        if user_input is not None:
            self._host = user_input["device"]
            await self.hass.async_add_executor_job(self._get_sensor, self._host)
            return await self.async_step_sensors()        
        
        select_device_schema = vol.Schema({
                vol.Required("device"): vol.In(list(self._devices.values()))
            })
        
        return self.async_show_form(
            step_id="select_device",
            data_schema=select_device_schema,
            description_placeholders={"devices": ", ".join(self._devices.values())}
        )  
        
    def is_valid_ip(self, ip):
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            _LOGGER.error("You entered an invalid IP")
            return False
    
    def is_valid_subnet(self, subnet):
        cntPeriod = subnet.count('.')
        if cntPeriod != 2:
            _LOGGER.error("Invalid subnet")
            return False
        ip = subnet + ".0"
        return self.is_valid_ip(ip)
        
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
                if (device_name is not None) and (not self._host_in_configuration_exists(ip)):
                    devices[ip] = f"{device_name} {ip}"

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
        except aiohttp.ClientError as e:
            return None
        except asyncio.TimeoutError as e:
            return None

    async def async_step_sensors(self, user_input=None):
        """Handle the sensor selection step."""
        if user_input is not None:
            return self.async_create_entry(
                title=f"{self._info['device']} - {self._info['number']}",
                data={
                    CONF_HOST: self._host,
                    CONF_MONITORED_CONDITIONS: user_input[CONF_MONITORED_CONDITIONS],
                },
            )

        default_monitored_conditions = (
            [] if self._async_current_entries() else DEFAULT_MONITORED_CONDITIONS
        )

        setup_schema = vol.Schema(
            {
                vol.Required(
                    CONF_MONITORED_CONDITIONS, default=default_monitored_conditions
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
        await self.hass.async_add_executor_job(self._check_host, self._host)
        await self.hass.async_add_executor_job(self._get_sensor, self._host)
        return await self.async_step_sensors(user_input)