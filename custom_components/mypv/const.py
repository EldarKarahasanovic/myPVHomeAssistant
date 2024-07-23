"""Constants for the MYPV Piko integration."""
from datetime import timedelta

from homeassistant.const import (
    UnitOfPower,
    UnitOfElectricPotential,
    UnitOfElectricCurrent,
    UnitOfFrequency,
    UnitOfTemperature,
    Platform
)

DOMAIN = "mypv"

PLATFORMS = [Platform.SENSOR]

DATA_COORDINATOR = "coordinator"

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=10)

DEFAULT_MENU_OPTIONS = {
        "ip_known": "IP Address",
        "ip_unknown": "IP Subnet Scan",
        "automatic_scan": "Automatic Scan in Your Network"
    }

ENTITIES_NOT_TO_BE_REMOVED = ["Boost button", "Device state"]

DEVICE_STATUS = {
    "de": {
        0: "Standby",
        1: "Heizen",
        2: "Heizen Sicherstellung",
        3: "Heizen beendet",
        4: "Keine Verbindung / Deaktiviert",
        5: "Fehler",
        6: "Sperrzeit aktiv"
    },
    "en": {
        0: "Standby",
        1: "Heating",
        2: "Heating Assurance",
        3: "Heating Ended",
        4: "No Connection / Disabled",
        5: "Error",
        6: "Blocking Time Active"
    }
}

# 1. Spalte Sensorname
# 2. Spalte Einheit
# 3. Spalte Icon
# 4. Spalte Datenquelle

SENSOR_TYPES = {
    "device": ["Device", None, "", "data"],
    "acthor9s": ["Acthor 9s", None, "", "data"],
    "fwversion": ["Firmware Version", None, "mdi:numeric", "data"],
    "psversion": ["Power Supply Version", None, "mdi:numeric", "data"],
    "p9sversion": ["Power Supply Version Acthor 9", None, "mdi:numeric", "data"],
    "screen_mode_flag": ["Screen Mode", None, "", "data"],
    "status": ["Status", None, "", "data"],
    "power": ["Power", UnitOfPower.WATT, "mdi:lightning-bolt", "data"],
    "boostpower": ["Boost Power", UnitOfPower.WATT, "mdi:thermometer-lines", "data"],
    "power_act": ["Power", UnitOfPower.WATT, "mdi:lightning-bolt", "data"],
    "power_solar_act": ["Power from solar", UnitOfPower.WATT, "mdi:solar-power-variant", "data"],
    "power_grid_act": ["Power from grid", UnitOfPower.WATT, "mdi:transmission-tower-export", "data"],
    "power_ac9": ["Power Acthor 9", UnitOfPower.WATT, "mdi:lightning-bolt", "data"],
    "power_solar_ac9": ["Power from solar Acthor 9", UnitOfPower.WATT, "mdi:solar-power-variant", "data"],
    "power_grid_ac9": ["Power from grid Acthor 9", UnitOfPower.WATT, "mdi:transmission-tower-export", "data"],
    "power1_solar": ["power1_solar", UnitOfPower.WATT, "mdi:solar-power-variant", "data"],
    "power1_grid": ["power1_grid", UnitOfPower.WATT, "mdi:transmission-tower-export", "data"],
    "power2_solar": ["power2_solar", UnitOfPower.WATT, "mdi:solar-power-variant", "data"],
    "power2_grid": ["power2_grid", UnitOfPower.WATT, "mdi:transmission-tower-export", "data"],
    "power3_solar": ["power3_solar", UnitOfPower.WATT, "mdi:solar-power-variant", "data"],
    "power3_grid": ["power3_grid", UnitOfPower.WATT, "mdi:transmission-tower-export", "data"],
    "load_state": ["load_state", None, "", "data"],
    "load_nom": ["load_nom", UnitOfPower.WATT, "", "data"],
    "rel1_out": ["rel1_out", None, "mdi:electric-switch", "data"],
    "ww1target": ["target_temperature", UnitOfTemperature.CELSIUS, "mdi:thermometer-auto", "data"],
    "temp1": ["Temperatur 1", UnitOfTemperature.CELSIUS, "mdi:thermometer-water", "data"],
    "temp2": ["Temperatur 2", UnitOfTemperature.CELSIUS, "mdi:thermometer", "data"],
    "temp3": ["Temperatur 3", UnitOfTemperature.CELSIUS, "mdi:thermometer", "data"],
    "temp4": ["Temperatur 4", UnitOfTemperature.CELSIUS, "mdi:thermometer", "data"],
    "boostactive": ["Boost active", None, "mdi:thermometer-chevron-up", "data"],
    "legboostnext": ["legboostnext", None, "mdi:bacteria", "data"],
    "date": ["Date", None, "mdi:calendar-today", "data"],
    "loctime": ["Loctime", None, "mdi:home-clock", "data"],
    "unixtime": ["Unix time", None, "mdi:web-clock", "data"],
    "wp_flag": ["wp_flag", None, "", "data"],
    "wp_time1_ctr": ["wp_time1_ctr", None, "", "data"],
    "wp_time2_ctr": ["wp_time2_ctr", None, "", "data"],
    "wp_time3_ctr": ["wp_time3_ctr", None, "", "data"],
    "pump_pwm": ["Pump PWM", None, "mdi:pump", "data"],
    "schicht_flag": ["Schicht", None, "", "data"],
    "act_night_flag": ["Night flag", None, "", "data"],
    "ctrlstate": ["ctrlstate", None, "", "data"],
    "blockactive": ["Block active", None, "", "data"],
    "error_state": ["Error state", None, "mdi:alert-circle", "data"],
    "meter1_id": ["meter1_id", None, "mdi:identifier", "data"],
    "meter1_ip": ["meter1_ip", None, "mdi:ip-network", "data"],
    "meter2_id": ["meter2_id", None, "mdi:identifier", "data"],
    "meter2_ip": ["meter2_ip", None, "mdi:ip-network", "data"],
    "meter3_id": ["meter3_id", None, "mdi:identifier", "data"],
    "meter3_ip": ["meter3_ip", None, "mdi:ip-network", "data"],
    "meter4_id": ["meter4_id", None, "mdi:identifier", "data"],
    "meter4_ip": ["meter4_ip", None, "mdi:ip-network", "data"],
    "meter5_id": ["meter5_id", None, "mdi:identifier", "data"],
    "meter5_ip": ["meter5_ip", None, "mdi:ip-network", "data"],
    "meter6_id": ["meter6_id", None, "mdi:identifier", "data"],
    "meter6_ip": ["meter6_ip", None, "mdi:ip-network", "data"],
    "surplus": ["surplus", None, "", "data"],
    "m0sum": ["m0sum", None, "", "data"],
    "m0l1": ["m0l1", None, "", "data"],
    "m0l2": ["m0l2", None, "", "data"],
    "m0l3": ["m0l3", None, "", "data"],
    "m0bat": ["m0bat", None, "", "data"],
    "m1sum": ["m1sum", None, "mdi:solar-power", "data"],
    "m1l1": ["m1l1", None, "mdi:solar-power", "data"],
    "m1l2": ["m1l2", None, "mdi:solar-power", "data"],
    "m1l3": ["m1l3", None, "mdi:solar-power", "data"],
    "m1devstate": ["m1devstate", None, "mdi:link", "data"],
    "m2sum": ["m2sum", None, "mdi:home-battery", "data"],
    "m2l1": ["m2l1", None, "mdi:home-battery", "data"],
    "m2l2": ["m2l2", None, "mdi:home-battery", "data"],
    "m2l3": ["m2l3", None, "mdi:home-battery", "data"],
    "m2soc": ["m2soc", None, "mdi:battery-charging-50", "data"],
    "m2state": ["m2state", None, "mdi:battery-heart-variant", "data"],
    "m2devstate": ["m2devstate", None, "mdi:link", "data"],
    "m3sum": ["m3sum", None, "mdi:ev-station", "data"],
    "m3l1": ["m3l1", None, "mdi:ev-station", "data"],
    "m3l2": ["m3l2", None, "mdi:ev-station", "data"],
    "m3l3": ["m3l3", None, "mdi:ev-station", "data"],
    "m3soc": ["m3soc", None, "mdi:battery-charging-50", "data"],
    "m3devstate": ["m3devstate", None, "mdi:link", "data"],
    "m4sum": ["m4sum", None, "mdi:heat-pump", "data"],
    "m4l1": ["m4l1", None, "mdi:heat-pump", "data"],
    "m4l2": ["m4l2", None, "mdi:heat-pump", "data"],
    "m4l3": ["m4l3", None, "mdi:heat-pump", "data"],
    "m4devstate": ["m4devstate", None, "mdi:link", "data"],
    "ecarstate": ["ecarstate", None, "mdi:car-electric", "data"],
    "ecarboostctr": ["ecarboostctr", None, "", "data"],
    "mss2": ["mss2", None, "", "data"],
    "mss3": ["mss3", None, "", "data"],
    "mss4": ["mss4", None, "", "data"],
    "mss5": ["mss5", None, "", "data"],
    "mss6": ["mss6", None, "", "data"],
    "mss7": ["mss7", None, "", "data"],
    "mss8": ["mss8", None, "", "data"],
    "mss9": ["mss9", None, "", "data"],
    "mss10": ["mss10", None, "", "data"],
    "mss11": ["mss11", None, "", "data"],
    "volt_mains": ["Volt L1", UnitOfElectricPotential.VOLT, "mdi:flash-triangle", "data"],
    "curr_mains": ["Current L1", UnitOfElectricCurrent.AMPERE, "mdi:current-ac", "data"],
    "volt_L2": ["Volt L2", UnitOfElectricPotential.VOLT, "mdi:current-ac", "data"],
    "curr_L2": ["Current L2", UnitOfElectricCurrent.AMPERE, "mdi:current-ac", "data"],
    "volt_L3": ["Volt L3", UnitOfElectricPotential.VOLT, "mdi:current-ac", "data"],
    "curr_L3": ["Current L3", UnitOfElectricCurrent.AMPERE, "mdi:current_ac", "data"],
    "volt_out": ["Volt out", UnitOfElectricPotential.VOLT, "mdi:flash-triangle", "data"],
    "freq": ["Frequency", UnitOfFrequency.HERTZ, "mdi:sine-wave", "data"],
    "temp_ps": ["Temp power supply", UnitOfTemperature.CELSIUS, "mdi:thermometer", "data"],
    "fan_speed": ["Fan speed", None, "mdi:fan", "data"],
    "ps_state": ["Power supply state", None, "", "data"],
    "cur_ip": ["IP", None, "mdi:ip-network", "data"],
    "cur_sn": ["Serial number", None, "mdi:numeric", "data"],
    "cur_gw": ["Gateway", None, "mdi:router-network", "data"],
    "cur_dns": ["DNS", None, "", "data"],
    "fwversionlatest": ["latest Firmware version", None, "mdi:numeric", "data"],
    "psversionlatest": ["latest Power supply version", None, "mdi:numeric", "data"],
    "p9sversionlatest": ["latest Power supply version Acthor 9", None, "mdi:numeric", "data"],
    "upd_state": ["Update state", None, "mdi:update", "data"],
    "upd_files_left": ["Update files left", None, "mdi:update", "data"],
    "ps_upd_state": ["Power supply update state", None, "mdi:update", "data"],
    "p9s_upd_state": ["Acthor 9 Power supply update state", None, "mdi:update", "data"],
    "mainmode": ["Operating Mode", None, "", "setup"],
    "mode9s": ["Operating Mode Acthor 9", None, "", "setup"],
}
