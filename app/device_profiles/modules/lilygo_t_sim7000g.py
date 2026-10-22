from ..schema import health_channel


def gpio_channel(pin, functions, signal_type="DIGITAL", input_only=False, notes=""):
    return {
        "key": f"gpio_{pin}",
        "label": f"GPIO{pin}",
        "signal_type": signal_type,
        "source_type": "TSIM7000G_GPIO",
        "unit": "",
        "widget": "numeric" if "ANALOGUE_INPUT" in functions or "PULSE_INPUT" in functions else "status",
        "direction": "INPUT",
        "calibratable": "ANALOGUE_INPUT" in functions,
        "pin": f"GPIO{pin}",
        "gpio": pin,
        "supported_functions": functions,
        "input_only": input_only,
        "pin_notes": notes,
    }


PROFILE = {
    "code": "AT360_LILYGO_TSIM7000G",
    "display_name": "LILYGO T-SIM7000G GNSS",
    "device_type": "LILYGO_T_SIM7000G_TRACKER",
    "asset_type": "TRACKER",
    "transport": "CELLULAR_WIFI",
    "firmware_family": "AT360_LILYGO_GNSS_IO",
    "minimum_firmware": "AT360_LILYGO_GNSS_IO_REV8",
    "recommended_firmware": "AT360_LILYGO_GNSS_IO_REV8",
    "capabilities": [
        "WIFI", "LTE_CAT_M1", "NB_IOT", "GPRS", "GNSS", "IMEI_IDENTITY",
        "CLAIM_TOKEN_REGISTRATION", "SERIAL_PROVISIONING", "SIMULATION",
        "ANALOGUE_INPUT", "DIGITAL_INPUT", "PULSE_INPUT", "DIGITAL_OUTPUT",
        "I2C", "CAPABILITY_AWARE_GPIO", "SAFE_OUTPUT_BOOT_OFF",
    ],
    "channels": [
        gpio_channel(13, ["DIGITAL_INPUT", "PULSE_INPUT", "DIGITAL_OUTPUT", "CUSTOM"], notes="Header GPIO; output starts OFF"),
        gpio_channel(14, ["DIGITAL_INPUT", "PULSE_INPUT", "DIGITAL_OUTPUT", "CUSTOM"], notes="Header GPIO; shared with microSD clock only if SD is enabled"),
        gpio_channel(21, ["DIGITAL_INPUT", "PULSE_INPUT", "DIGITAL_OUTPUT", "I2C_SDA", "CUSTOM"], notes="Header GPIO / I2C SDA"),
        gpio_channel(22, ["DIGITAL_INPUT", "PULSE_INPUT", "DIGITAL_OUTPUT", "I2C_SCL", "CUSTOM"], notes="Header GPIO / I2C SCL"),
        gpio_channel(23, ["DIGITAL_INPUT", "PULSE_INPUT", "DIGITAL_OUTPUT", "CUSTOM"], notes="Header GPIO"),
        gpio_channel(32, ["ANALOGUE_INPUT", "DIGITAL_INPUT", "PULSE_INPUT", "DIGITAL_OUTPUT", "CUSTOM"], signal_type="ANALOG_DIGITAL_PULSE", notes="ADC1-capable header GPIO; output starts OFF"),
        gpio_channel(33, ["ANALOGUE_INPUT", "DIGITAL_INPUT", "PULSE_INPUT", "DIGITAL_OUTPUT", "CUSTOM"], signal_type="ANALOG_DIGITAL_PULSE", notes="ADC1-capable header GPIO; output starts OFF"),
        gpio_channel(34, ["ANALOGUE_INPUT", "DIGITAL_INPUT", "PULSE_INPUT", "CUSTOM"], signal_type="ANALOG_DIGITAL_PULSE", input_only=True, notes="ADC1 input-only; no output driver; external pull resistor may be required"),
        gpio_channel(35, ["ANALOGUE_INPUT", "DIGITAL_INPUT", "PULSE_INPUT", "CUSTOM"], signal_type="ANALOG_DIGITAL_PULSE", input_only=True, notes="ADC1 input-only; no output driver; external pull resistor may be required"),
        gpio_channel(39, ["ANALOGUE_INPUT", "DIGITAL_INPUT", "PULSE_INPUT", "CUSTOM"], signal_type="ANALOG_DIGITAL_PULSE", input_only=True, notes="SENSOR_VN / GPIO39; ADC1 input-only; external pull resistor may be required"),
        health_channel("gps_fix", "GNSS Fix", "STATE", "TSIM7000G"),
        health_channel("latitude", "Latitude", "LOCATION", "TSIM7000G", "degrees", "numeric"),
        health_channel("longitude", "Longitude", "LOCATION", "TSIM7000G", "degrees", "numeric"),
        health_channel("speed_kph", "Speed", "SPEED", "TSIM7000G", "km/h", "numeric"),
        health_channel("altitude_m", "Altitude", "DISTANCE", "TSIM7000G", "m", "numeric"),
        health_channel("satellites_used", "Satellites Used", "COUNT", "TSIM7000G", "sat", "numeric"),
        health_channel("gps_accuracy_m", "GNSS Accuracy", "DISTANCE", "TSIM7000G", "m", "numeric"),
        health_channel("gsm_csq", "GSM Signal Quality", "SIGNAL", "TSIM7000G", "CSQ", "numeric"),
        health_channel("wifi_rssi", "Wi-Fi Signal", "SIGNAL", "TSIM7000G", "dBm", "numeric"),
    ],
    "output_channels": [
        {"channel": f"GPIO{pin}", "label": f"GPIO{pin} Digital Output", "mode": "LATCHED",
         "supported_actions": ["OUTPUT_ON", "OUTPUT_OFF"], "safe_boot_state": "OFF",
         "simulation_physical_lockout": True, "pin": f"GPIO{pin}"}
        for pin in (13, 14, 21, 22, 23, 32, 33)
    ],
    "reserved_pins": [
        {"pin": "GPIO4", "customer_output": False, "reason": "SIM7000G PWRKEY"},
        {"pin": "GPIO25", "customer_output": False, "reason": "SIM7000G power enable"},
        {"pin": "GPIO26", "customer_output": False, "reason": "SIM7000G UART RX"},
        {"pin": "GPIO27", "customer_output": False, "reason": "SIM7000G UART TX"},
        {"pin": "GPIO0", "customer_output": False, "reason": "Boot-strapping pin"},
        {"pin": "GPIO2", "customer_output": False, "reason": "Boot-strapping / microSD shared pin"},
        {"pin": "GPIO5", "customer_output": False, "reason": "Boot-strapping / board-shared pin"},
        {"pin": "GPIO12", "customer_output": False, "reason": "Boot-sensitive; unsafe external level can prevent startup"},
        {"pin": "GPIO15", "customer_output": False, "reason": "Boot-strapping / microSD shared pin"},
        {"pin": "GPIO6-11", "customer_output": False, "reason": "Internal flash bus"},
        {"pin": "GPIO16-17", "customer_output": False, "reason": "ESP32-WROVER PSRAM/internal use"},
    ],
    "registration": {"required": True, "method": "CLAIM_TOKEN", "store_claim_token": False, "mask_device_token": True},
    "io_rules": {"one_assignment_per_physical_pin": True, "outputs_safe_off": True, "simulation_output_lockout": True},
    "profile_notice": "GNSS/cellular tracker with ten verified header I/O points. Modem, boot-sensitive, flash and PSRAM pins remain protected.",
}
