"""T-Call 20190610 profile aligned to TCALL_IO_REV14; no onboard GNSS."""
from ..schema import health_channel

def gpio(pin):
    functions=["DIGITAL_INPUT","PULSE_INPUT"]
    if pin != 14: functions.append("ANALOGUE_INPUT")
    if pin in (14,32,33): functions.append("DIGITAL_OUTPUT")
    return {"key":f"gpio_{pin}","label":f"GPIO{pin}","signal_type":"CUSTOM",
            "source_type":"TCALL_SIM800L","unit":"","widget":"numeric",
            "direction":"INPUT","calibratable":pin!=14,"pin":f"GPIO{pin}",
            "gpio":pin,"supported_functions":functions,"input_only":pin in (34,35,39),
            "pin_notes":"3.3 V GPIO only; configure actual mode locally. " +
            ("Input-only; external bias required." if pin in (34,35,39) else "Outputs boot OFF; local configuration only.")}

PROFILE={
 "code":"AT360_LILYGO_TCALL_SIM800L","display_name":"LILYGO T-Call SIM800L I/O",
 "device_type":"LILYGO_TCALL_SIM800L_IO","asset_type":"GENERIC",
 "transport":"CELLULAR_WIFI","firmware_family":"AT360_LILYGO_TCALL_IO",
 "minimum_firmware":"AT360_LILYGO_TCALL_IO_REV14","recommended_firmware":"AT360_LILYGO_TCALL_IO_REV14",
 "capabilities":["WIFI","GPRS","GSM_SIGNAL","IMEI_IDENTITY","SERIAL_PROVISIONING",
                 "CAPABILITY_AWARE_GPIO","SAFE_OUTPUT_BOOT_OFF","SIMULATION"],
 "channels":[gpio(p) for p in (14,32,33,34,35,39)]+[
   health_channel("gsm_csq","GSM Signal Quality","SIGNAL","TCALL_SIM800L","CSQ","numeric"),
   health_channel("wifi_rssi","Wi-Fi Signal","SIGNAL","TCALL_SIM800L","dBm","numeric")],
 # REV14 has no cloud command polling. Never offer remote physical output commands.
 "output_channels":[],
 "reserved_pins":[{"pin":f"GPIO{p}","customer_output":False,"reason":reason} for p,reason in
   ((4,"SIM800L PWRKEY"),(5,"SIM800L reset"),(23,"SIM800L power enable"),
    (26,"Modem UART RX"),(27,"Modem UART TX"),(21,"IP5306 I2C SDA"),
    (22,"IP5306 I2C SCL"),(13,"Onboard LED"),(0,"Boot strap"),(2,"Boot strap"),
    (12,"Boot-sensitive"),(15,"Boot strap"),(16,"PSRAM"),(17,"PSRAM"))]+
    [{"pin":"GPIO6-11","customer_output":False,"reason":"Flash bus"}],
 "io_rules":{"one_assignment_per_physical_pin":True,"outputs_safe_off":True,"simulation_output_lockout":True},
 "profile_notice":"SIM800L 2G/Wi-Fi I/O gateway; no GPS/GNSS or LTE. Six firmware-supported GPIO points. Local outputs only; cellular HTTPS is not validated in REV14."
}
