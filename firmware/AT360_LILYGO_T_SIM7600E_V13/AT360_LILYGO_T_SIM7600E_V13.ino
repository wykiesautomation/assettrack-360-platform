/*
  AssetTrack 360 - LILYGO T-SIM7600E V1.3 (PCB 20200310)
  Production baseline firmware. Safe defaults: no physical customer outputs.
  Copyright: (c) 2026 JP Van Wyk. All rights reserved.
*/
#define TINY_GSM_MODEM_SIM7600
#define TINY_GSM_RX_BUFFER 1024
#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Preferences.h>
#include <TinyGsmClient.h>

static const char *FW = "AT360_LILYGO_T_SIM7600E_V13_1.0.0";
static const char *PROFILE = "AT360_LILYGO_T_SIM7600E_V13";
static const char *API_BASE = "https://assettrack360.wykiesautomation.co.za";
static const char *WIFI_SSID = "";
static const char *WIFI_PASSWORD = "";
static const char *CELLULAR_APN = "";       // Set for the installed SIM
static const char *CELLULAR_USER = "";
static const char *CELLULAR_PASSWORD = "";

static const int MODEM_TX = 27;  // ESP32 TX -> SIM7600E RX
static const int MODEM_RX = 26;  // ESP32 RX <- SIM7600E TX
static const int MODEM_PWRKEY = 4;
static const int MODEM_RING = 33;
static const int MODEM_DTR = 32;
static const int MODEM_FLIGHT = 25;
static const int MODEM_STATUS = 34;
static const int BATTERY_ADC = 35;
static const int SOLAR_ADC = 36;
static const int BOARD_LED = 12;

HardwareSerial ModemSerial(1);
TinyGsm modem(ModemSerial);
TinyGsmClientSecure cellularClient(modem);
WiFiClientSecure wifiClient;
Preferences prefs;
String deviceUid, deviceToken, pendingClaim;
uint32_t sequenceNo = 0;
unsigned long previousUpload = 0;
const unsigned long UPLOAD_MS = 30000;

String boardId() {
  uint64_t mac = ESP.getEfuseMac();
  char out[17]; snprintf(out, sizeof(out), "%04X%08X", (uint16_t)(mac >> 32), (uint32_t)mac);
  return String(out);
}

void pulsePowerKey() {
  pinMode(MODEM_PWRKEY, OUTPUT);
  digitalWrite(MODEM_PWRKEY, LOW); delay(100);
  digitalWrite(MODEM_PWRKEY, HIGH); delay(1000);
  digitalWrite(MODEM_PWRKEY, LOW); delay(5000);
}

bool startModem() {
  ModemSerial.begin(115200, SERIAL_8N1, MODEM_RX, MODEM_TX);
  pinMode(MODEM_FLIGHT, OUTPUT); digitalWrite(MODEM_FLIGHT, HIGH);
  pinMode(MODEM_DTR, OUTPUT); digitalWrite(MODEM_DTR, LOW);
  if (!modem.testAT(1500)) pulsePowerKey();
  if (!modem.restart()) return false;
  modem.sendAT("+CGPS=1"); modem.waitResponse(2000);
  return true;
}

bool connectNetwork() {
  if (strlen(WIFI_SSID)) {
    WiFi.mode(WIFI_STA); WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    for (int i=0; i<30 && WiFi.status()!=WL_CONNECTED; ++i) delay(500);
    if (WiFi.status()==WL_CONNECTED) return true;
  }
  if (!modem.isNetworkConnected() && !modem.waitForNetwork(60000L, true)) return false;
  if (!modem.isGprsConnected() && !modem.gprsConnect(CELLULAR_APN, CELLULAR_USER, CELLULAR_PASSWORD)) return false;
  return true;
}

int postJson(const String &path, const String &body, const String &token, String &reply) {
  HTTPClient http; int status=-1;
  if (WiFi.status()==WL_CONNECTED) {
    wifiClient.setInsecure();
    if (!http.begin(wifiClient, String(API_BASE)+path)) return -1;
  } else {
    if (!http.begin(cellularClient, String(API_BASE)+path)) return -1;
  }
  http.addHeader("Content-Type", "application/json");
  if (token.length()) http.addHeader("Authorization", "Bearer "+token);
  status=http.POST((uint8_t*)body.c_str(), body.length());
  reply=http.getString(); http.end(); return status;
}

bool claimDevice(const String &code) {
  JsonDocument doc; doc["claim_code"]=code; doc["board_id"]=boardId(); doc["profile_code"]=PROFILE; doc["firmware"]=FW;
  String body, reply; serializeJson(doc,body);
  int status=postJson("/api/v2/devices/claim",body,"",reply);
  if (status!=201) { Serial.printf("CLAIM FAILED HTTP %d: %s\n",status,reply.c_str()); return false; }
  JsonDocument result; if (deserializeJson(result,reply)) return false;
  deviceUid=result["device_uid"].as<String>(); deviceToken=result["device_token"].as<String>();
  if (!deviceUid.length() || !deviceToken.length()) return false;
  prefs.putString("uid",deviceUid); prefs.putString("token",deviceToken); prefs.remove("claim");
  Serial.printf("CLAIMED %s\n",deviceUid.c_str()); return true;
}

void serialProvisioning() {
  if (!Serial.available()) return;
  String line=Serial.readStringUntil('\n'); line.trim();
  if (line.startsWith("CLAIM ")) { pendingClaim=line.substring(6); pendingClaim.trim(); pendingClaim.toUpperCase(); prefs.putString("claim",pendingClaim); }
  else if (line=="STATUS") Serial.printf("UID=%s TOKEN=%s NET=%s CSQ=%d\n",deviceUid.c_str(),deviceToken.length()?"STORED":"MISSING",WiFi.status()==WL_CONNECTED?"WIFI":"CELLULAR",modem.getSignalQuality());
  else if (line=="CLEAR") { prefs.clear(); deviceUid=""; deviceToken=""; pendingClaim=""; Serial.println("PROVISIONING CLEARED"); }
  else Serial.println("Commands: CLAIM XXXX-XXXX | STATUS | CLEAR");
}

float adcVolts(int pin, float divider) {
  uint32_t mv=analogReadMilliVolts(pin); return (mv/1000.0f)*divider;
}

bool readGnss(float &lat,float &lon,float &speed,float &alt,int &vsat) {
  float accuracy=0; int usat=0,year=0,month=0,day=0,hour=0,minute=0,second=0;
  return modem.getGPS(&lat,&lon,&speed,&alt,&vsat,&usat,&accuracy,&year,&month,&day,&hour,&minute,&second);
}

void uploadTelemetry() {
  if (!deviceToken.length() || !connectNetwork()) return;
  float lat=0,lon=0,speed=0,alt=0; int sats=0; bool fix=readGnss(lat,lon,speed,alt,sats);
  float batteryV=adcVolts(BATTERY_ADC,2.0f); float solarV=adcVolts(SOLAR_ADC,2.0f);
  int csq=modem.getSignalQuality();
  JsonDocument doc; doc["firmware"]=FW; doc["sequence"]=deviceUid+":"+String(millis())+":"+String(++sequenceNo);
  JsonArray m=doc["measurements"].to<JsonArray>();
  auto add=[&](const char *point,float value,const char *quality="GOOD"){JsonObject x=m.add<JsonObject>();x["point"]=point;x["value"]=value;x["quality"]=quality;};
  add("gps_fix",fix?1:0,fix?"GOOD":"BAD"); add("speed_kmh",fix?speed:0,fix?"GOOD":"BAD"); add("heading",0,fix?"UNCERTAIN":"BAD");
  add("satellites",sats,fix?"GOOD":"BAD"); add("altitude_m",alt,fix?"GOOD":"BAD"); add("battery_v",batteryV); add("battery_percent",constrain((batteryV-3.2f)*100.0f,0.0f,100.0f));
  add("solar_v",solarV); add("cellular_signal",csq,csq==99?"BAD":"GOOD"); add("network_registered",modem.isNetworkConnected()?1:0); add("wifi_rssi",WiFi.status()==WL_CONNECTED?WiFi.RSSI():-127);
  add("queue_depth",0); add("sd_status",0,"UNCERTAIN");
  if (fix) { JsonObject loc=doc["location"].to<JsonObject>(); loc["latitude"]=lat; loc["longitude"]=lon; loc["speed_kmh"]=speed; loc["heading"]=0; loc["accuracy_m"]=25; }
  String body,reply; serializeJson(doc,body); int status=postJson("/api/v1/ingest",body,deviceToken,reply);
  Serial.printf("UPLOAD HTTP %d: %s\n",status,reply.c_str());
}

void setup() {
  Serial.begin(115200); delay(500); Serial.println("\nAssetTrack 360 T-SIM7600E V1.3");
  pinMode(BOARD_LED,OUTPUT); digitalWrite(BOARD_LED,LOW);
  pinMode(MODEM_RING,INPUT); pinMode(MODEM_STATUS,INPUT);
  analogReadResolution(12); analogSetPinAttenuation(BATTERY_ADC,ADC_11db); analogSetPinAttenuation(SOLAR_ADC,ADC_11db);
  prefs.begin("at360",false); deviceUid=prefs.getString("uid",""); deviceToken=prefs.getString("token",""); pendingClaim=prefs.getString("claim",""); sequenceNo=prefs.getUInt("seq",0);
  startModem(); connectNetwork();
  if (!deviceToken.length() && pendingClaim.length()) claimDevice(pendingClaim);
  Serial.println("Use Serial command CLAIM XXXX-XXXX to provision this board.");
}

void loop() {
  serialProvisioning();
  if (!deviceToken.length() && pendingClaim.length() && millis()-previousUpload>10000) { previousUpload=millis(); if(connectNetwork()) claimDevice(pendingClaim); }
  if (deviceToken.length() && millis()-previousUpload>=UPLOAD_MS) { previousUpload=millis(); uploadTelemetry(); prefs.putUInt("seq",sequenceNo); }
  delay(20);
}
