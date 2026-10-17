from ..schema import health_channel
PROFILE={
 "code":"AT360_LILYGO_TSIM7000G","display_name":"LILYGO T-SIM7000G GNSS Tracker","device_type":"LILYGO_T_SIM7000G_TRACKER","asset_type":"TRACKER","transport":"CELLULAR_WIFI","firmware_family":"AT360_LILYGO_TSIM7000G",
 "capabilities":["WIFI","LTE_CAT_M1","NB_IOT","GNSS","SERIAL_PROVISIONING","NO_CUSTOMER_GPIO_OUTPUTS"],
 "channels":[health_channel("gps_fix","GNSS Fix","STATE","TSIM7000G"),health_channel("speed_kmh","Speed","SPEED","TSIM7000G","km/h","numeric"),health_channel("satellites_used","Satellites Used","COUNT","TSIM7000G","sat","numeric"),health_channel("gps_accuracy_m","GNSS Accuracy","DISTANCE","TSIM7000G","m","numeric"),health_channel("wifi_rssi","Wi-Fi Signal","SIGNAL","TSIM7000G","dBm","numeric")],
 "output_channels":[],"profile_notice":"Dedicated T-SIM7000G profile, separate from T-SIM7600E V1.3."
}
