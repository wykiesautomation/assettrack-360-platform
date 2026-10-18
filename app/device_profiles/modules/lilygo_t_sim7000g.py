from ..schema import health_channel
PROFILE={
 "code":"AT360_LILYGO_TSIM7000G",
 "display_name":"LILYGO T-SIM7000G GNSS",
 "device_type":"LILYGO_T_SIM7000G_TRACKER",
 "asset_type":"TRACKER",
 "transport":"CELLULAR_WIFI",
 "firmware_family":"AT360_LILYGO_GNSS",
 "minimum_firmware":"AT360_LILYGO_GNSS_REV7",
 "recommended_firmware":"AT360_LILYGO_GNSS_REV7",
 "capabilities":["WIFI","LTE_CAT_M1","NB_IOT","GPRS","GNSS","IMEI_IDENTITY","CLAIM_TOKEN_REGISTRATION","SERIAL_PROVISIONING","SIMULATION","NO_CUSTOMER_GPIO_OUTPUTS"],
 "channels":[
  health_channel("gps_fix","GNSS Fix","STATE","TSIM7000G"),
  health_channel("latitude","Latitude","LOCATION","TSIM7000G","degrees","numeric"),
  health_channel("longitude","Longitude","LOCATION","TSIM7000G","degrees","numeric"),
  health_channel("speed_kph","Speed","SPEED","TSIM7000G","km/h","numeric"),
  health_channel("altitude_m","Altitude","DISTANCE","TSIM7000G","m","numeric"),
  health_channel("satellites_used","Satellites Used","COUNT","TSIM7000G","sat","numeric"),
  health_channel("gps_accuracy_m","GNSS Accuracy","DISTANCE","TSIM7000G","m","numeric"),
  health_channel("gsm_csq","GSM Signal Quality","SIGNAL","TSIM7000G","CSQ","numeric"),
  health_channel("wifi_rssi","Wi-Fi Signal","SIGNAL","TSIM7000G","dBm","numeric")
 ],
 "output_channels":[],
 "reserved_pins":[
  {"pin":4,"purpose":"SIM7000G PWRKEY","customer_output":False},
  {"pin":25,"purpose":"SIM7000G power enable","customer_output":False},
  {"pin":26,"purpose":"SIM7000G UART RX","customer_output":False},
  {"pin":27,"purpose":"SIM7000G UART TX","customer_output":False}
 ],
 "registration":{"required":True,"method":"CLAIM_TOKEN","store_claim_token":False,"mask_device_token":True},
 "profile_notice":"The single supported LILYGO cellular tracker profile. T-SIM7600E is not published or selectable."
}
