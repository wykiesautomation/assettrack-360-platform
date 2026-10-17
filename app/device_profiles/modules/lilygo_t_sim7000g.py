from ..schema import health_channel

PROFILE = {
    'code': 'AT360_LILYGO_TSIM7000G',
    'display_name': 'LILYGO T-SIM7000G GNSS Tracker',
    'device_type': 'LILYGO_T_SIM7000G_TRACKER',
    'asset_type': 'TRACKER',
    'transport': 'CELLULAR_WIFI',
    'firmware_family': 'AT360_LILYGO_TSIM7000G',
    'revision_state': 'FIRMWARE_AND_CONNECTED_BOARD_VERIFIED',
    'capabilities': ['WIFI','BLE','LTE_CAT_M1','NB_IOT','GPRS_FALLBACK','GNSS','SMS','SERIAL_PROVISIONING','OFFLINE_QUEUE','ESP32_WROVER_B','PSRAM','NO_CUSTOMER_GPIO_OUTPUTS'],
    'channels': [
        health_channel('gps_fix','GNSS Fix','STATE','TSIM7000G'),
        health_channel('speed_kmh','Speed','SPEED','TSIM7000G','km/h','numeric'),
        health_channel('satellites_used','Satellites Used','COUNT','TSIM7000G','sat','numeric'),
        health_channel('gps_accuracy_m','GNSS Accuracy','DISTANCE','TSIM7000G','m','numeric'),
        health_channel('cellular_signal','Cellular Signal','SIGNAL','TSIM7000G','CSQ','numeric'),
        health_channel('network_registered','Network Registered','STATE','TSIM7000G'),
        health_channel('gprs_connected','Packet Data Connected','STATE','TSIM7000G'),
        health_channel('wifi_rssi','Wi-Fi Signal','SIGNAL','TSIM7000G','dBm','numeric'),
    ],
    'output_channels': [],
    'reserved_pins': [
        {'pin':'GPIO26','purpose':'SIM7000G modem RX','customer_output':False},
        {'pin':'GPIO27','purpose':'SIM7000G modem TX','customer_output':False},
        {'pin':'GPIO4','purpose':'SIM7000G PWRKEY','customer_output':False},
        {'pin':'GPIO25','purpose':'SIM7000G modem power','customer_output':False},
        {'pin':'GPIO36','purpose':'SIM7000G status input','customer_output':False},
        {'pin':'GPIO12','purpose':'Board status LED','customer_output':False},
    ],
    'board_metadata': {'board_family':'LILYGO T-SIM7000G','mcu':'ESP32-WROVER-B','modem':'SIM7000G','arduino_target':'ESP32 Wrover Module','customer_io':'LOCKED; tracker modem and status pins are reserved'},
    'profile_notice': 'Dedicated T-SIM7000G tracker profile. It remains separate from T-SIM7600E V1.3.'
}
