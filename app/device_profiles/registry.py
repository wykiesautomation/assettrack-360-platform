"""AssetTrack 360 device-profile registry.

Only verified and currently supported physical boards are published.
SIM7000G and T-Call SIM800L are separate profiles; never aliases.
"""
from importlib import import_module
from .schema import validate_profile

MODULES=("esp32d_38pin","esp32_wroom32","sim808_samd21","lilygo_t_sim7000g","lilygo_tcall_sim800l")
PUBLIC_BOARD_CODES=("AT360_ESP32D_EXPANDED","AT360_ESP32_WROOM32","AT360_SIM808_TRACKER_2AI_2DO","AT360_LILYGO_TSIM7000G","AT360_LILYGO_TCALL_SIM800L")
PROFILE_ALIASES={
    "AT360_ESP32D_38PIN":"AT360_ESP32D_EXPANDED",
    "AT360_ESP32D_PILOT":"AT360_ESP32D_EXPANDED",
    "AT360_LILYGO_T_SIM7000G":"AT360_LILYGO_TSIM7000G",
}
DEVICE_PROFILES={}
for module_name in MODULES:
    module=import_module(f".modules.{module_name}",package=__package__)
    profile=validate_profile(module.PROFILE)
    code=profile["code"]
    if code in DEVICE_PROFILES:raise ValueError(f"Duplicate profile code: {code}")
    DEVICE_PROFILES[code]=profile

def get_profile(code):
    normalized=str(code or "").strip().upper()
    normalized=PROFILE_ALIASES.get(normalized,normalized)
    return DEVICE_PROFILES.get(normalized)

def public_profiles():
    profiles=[];seen=set()
    for code in PUBLIC_BOARD_CODES:
        profile=DEVICE_PROFILES.get(code)
        if profile and profile["code"] not in seen:
            profiles.append(profile);seen.add(profile["code"])
    return profiles

def profile_for_device(device):
    if not device:return None
    for value in device.capabilities or []:
        if str(value).startswith("PROFILE:"):
            profile=get_profile(str(value).split(":",1)[1])
            if profile:return profile
    legacy={
        "LILYGO_TCALL_SIM800L_IO":"AT360_LILYGO_TCALL_SIM800L",
        "ESP32_REMOTE_IO":"AT360_ESP32D_EXPANDED",
        "ESP32D_38PIN_REMOTE_IO":"AT360_ESP32D_EXPANDED",
        "ESP32_WROOM32_REMOTE_IO":"AT360_ESP32_WROOM32",
        "SIM808_GPS_TRACKER":"AT360_SIM808_TRACKER_2AI_2DO",
        "SIM808_SAMD21":"AT360_SIM808_TRACKER_2AI_2DO",
        "LILYGO_T_SIM7000G_TRACKER":"AT360_LILYGO_TSIM7000G",
    }
    return get_profile(legacy.get(str(getattr(device,"device_type","")).upper()))
