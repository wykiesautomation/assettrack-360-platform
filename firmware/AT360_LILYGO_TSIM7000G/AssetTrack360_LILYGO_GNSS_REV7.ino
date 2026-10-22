/*
  AssetTrack 360 - LILYGO T-SIM7000G GNSS Firmware REV7
  Wi-Fi + cellular commissioning, Board Builder protocol, GNSS,
  secure claim-token device registration and telemetry upload.

  Target: LILYGO T-SIM7000G / ESP32-WROVER-B
  Copyright: © 2026 JP Van Wyk. All rights reserved.
*/

#define TINY_GSM_MODEM_SIM7000
#define TINY_GSM_RX_BUFFER 1024

#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <Preferences.h>
#include <TinyGsmClient.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>

// T-SIM7000G modem pins. These pins are reserved for the onboard modem.
static const int MODEM_RX = 26;
static const int MODEM_TX = 27;
static const int MODEM_PWRKEY = 4;
static const int MODEM_POWER = 25;
static const uint32_t MODEM_BAUD = 9600;

static const char *BOARD_PROFILE = "AT360_LILYGO_TSIM7000G";
static const char *FIRMWARE_VERSION = "AT360_LILYGO_GNSS_REV7";
static const char *SETUP_AP_SSID = "AssetTrack360-Setup";
static const char *SETUP_AP_PASSWORD = "ChangeMe360!";
static const char *DEFAULT_REGISTER_PATH = "/api/devices/register";
static const char *DEFAULT_TELEMETRY_PATH = "/api/devices/telemetry";

// Set to 1 only for controlled commissioning against a test HTTPS server.
// Production should use a valid CA certificate below and leave this at 0.
#define AT360_ALLOW_INSECURE_TLS 0
static const char AT360_ROOT_CA[] PROGMEM = R"CA(
-----BEGIN CERTIFICATE-----
REPLACE_WITH_ASSETTRACK360_SERVER_ROOT_CA
-----END CERTIFICATE-----
)CA";

HardwareSerial SerialAT(1);
TinyGsm modem(SerialAT);
TinyGsmClient cellularClient(modem);
TinyGsmClientSecure cellularSecureClient(modem);
WebServer web(80);
Preferences prefs;

String serialLine;
String stationSsid, stationPassword;
String cellularApn, cellularUser, cellularPassword;
String apiBaseUrl, registerPath, telemetryPath, deviceName;
String pendingClaimToken;
String assignedDeviceUid, deviceApiToken;
String registrationStatus = "NOT_REGISTERED";
String registrationMessage;
String lastUploadStatus = "NEVER";
String operatingMode = "LIVE";

bool wifiScanActive = false;
bool modemReady = false;
bool gnssEnabled = false;
uint32_t wifiScanStartedAt = 0;
uint32_t lastModemAttemptAt = 0;
uint32_t lastUploadAt = 0;

struct GnssData {
  bool valid = false;
  float latitude = 0;
  float longitude = 0;
  float speedKph = 0;
  float altitudeM = 0;
  float accuracyM = 0;
  int satellitesVisible = 0;
  int satellitesUsed = 0;
  int year = 0, month = 0, day = 0;
  int hour = 0, minute = 0, second = 0;
};

void kv(const String &key, const String &value) {
  Serial.println(key + "=" + value);
}

String safeField(String value) {
  value.replace("|", " ");
  value.replace("\r", " ");
  value.replace("\n", " ");
  return value;
}

String hardwareUid() {
  uint64_t id = ESP.getEfuseMac();
  char buffer[32];
  snprintf(buffer, sizeof(buffer), "AT360-LILYGO-%04X%08X",
           (uint16_t)(id >> 32), (uint32_t)id);
  return String(buffer);
}

String maskedToken(const String &token) {
  if (token.length() < 9) return token.length() ? "********" : "";
  return token.substring(0, 4) + "..." + token.substring(token.length() - 4);
}

String joinUrl(String base, String path) {
  base.trim();
  path.trim();
  while (base.endsWith("/")) base.remove(base.length() - 1);
  if (!path.startsWith("/")) path = "/" + path;
  return base + path;
}

bool validApiBaseUrl(const String &url) {
  return url.startsWith("https://") || url.startsWith("http://192.168.") ||
         url.startsWith("http://10.") || url.startsWith("http://172.16.");
}

void loadSettings() {
  prefs.begin("at360", true);
  stationSsid = prefs.getString("ssid", "");
  stationPassword = prefs.getString("wifiPass", "");
  cellularApn = prefs.getString("apn", "");
  cellularUser = prefs.getString("apnUser", "");
  cellularPassword = prefs.getString("apnPass", "");
  apiBaseUrl = prefs.getString("apiUrl", "");
  registerPath = prefs.getString("regPath", DEFAULT_REGISTER_PATH);
  telemetryPath = prefs.getString("telPath", DEFAULT_TELEMETRY_PATH);
  deviceName = prefs.getString("devName", "LILYGO GNSS Tracker");
  assignedDeviceUid = prefs.getString("assignedUid", "");
  deviceApiToken = prefs.getString("deviceToken", "");
  prefs.end();
  registrationStatus = (assignedDeviceUid.length() && deviceApiToken.length())
                         ? "REGISTERED" : "NOT_REGISTERED";
}

void saveNetworkSettings() {
  prefs.begin("at360", false);
  prefs.putString("ssid", stationSsid);
  prefs.putString("wifiPass", stationPassword);
  prefs.putString("apn", cellularApn);
  prefs.putString("apnUser", cellularUser);
  prefs.putString("apnPass", cellularPassword);
  prefs.end();
}

void saveRegistrationConfig() {
  prefs.begin("at360", false);
  prefs.putString("apiUrl", apiBaseUrl);
  prefs.putString("regPath", registerPath);
  prefs.putString("telPath", telemetryPath);
  prefs.putString("devName", deviceName);
  prefs.end();
}

void saveDeviceCredentials(const String &uid, const String &token) {
  prefs.begin("at360", false);
  prefs.putString("assignedUid", uid);
  prefs.putString("deviceToken", token);
  prefs.end();
  assignedDeviceUid = uid;
  deviceApiToken = token;
  registrationStatus = "REGISTERED";
}

void clearDeviceCredentials() {
  prefs.begin("at360", false);
  prefs.remove("assignedUid");
  prefs.remove("deviceToken");
  prefs.end();
  assignedDeviceUid = "";
  deviceApiToken = "";
  pendingClaimToken = "";
  registrationStatus = "NOT_REGISTERED";
  registrationMessage = "Registration cleared locally";
}

String modemImei() {
  if (!modemReady) return "";
  String value = modem.getIMEI();
  value.trim();
  return value;
}

String simStatusText() {
  if (!modemReady) return "MODEM_NOT_READY";
  SimStatus status = modem.getSimStatus();
  if (status == SIM_READY) return "READY";
  if (status == SIM_LOCKED) return "LOCKED";
  return "ERROR";
}

String networkStatusText() {
  if (!modemReady) return "MODEM_NOT_READY";
  return modem.isNetworkConnected() ? "REGISTERED" : "NOT_REGISTERED";
}

String gprsStatusText() {
  if (!modemReady) return "MODEM_NOT_READY";
  return modem.isGprsConnected() ? "CONNECTED" : "DISCONNECTED";
}

GnssData acquireGnss() {
  GnssData data;
  if (!modemReady || !gnssEnabled) return data;
  bool ok = modem.getGPS(&data.latitude, &data.longitude, &data.speedKph,
                         &data.altitudeM, &data.satellitesVisible,
                         &data.satellitesUsed, &data.accuracyM,
                         &data.year, &data.month, &data.day,
                         &data.hour, &data.minute, &data.second);
  bool coordinatesValid = data.latitude >= -90 && data.latitude <= 90 &&
                          data.longitude >= -180 && data.longitude <= 180 &&
                          !(data.latitude == 0 && data.longitude == 0);
  data.valid = ok && coordinatesValid;
  return data;
}

String gnssTimestamp(const GnssData &data) {
  if (!data.valid || data.year < 2000) return "";
  char timestamp[25];
  snprintf(timestamp, sizeof(timestamp), "%04d-%02d-%02dT%02d:%02d:%02dZ",
           data.year, data.month, data.day,
           data.hour, data.minute, data.second);
  return String(timestamp);
}

void reportIdentity() {
  kv("BOARD_PROFILE", BOARD_PROFILE);
  kv("FIRMWARE", FIRMWARE_VERSION);
  kv("FIRMWARE_VERSION", FIRMWARE_VERSION);
  kv("HARDWARE_UID", hardwareUid());
  kv("BOARD_ID", hardwareUid());
  kv("DEVICE_UID", assignedDeviceUid.length() ? assignedDeviceUid : hardwareUid());
  kv("IMEI", modemImei());
  kv("MODE", operatingMode);
}

void reportWifi() {
  bool online = WiFi.status() == WL_CONNECTED;
  kv("WIFI_STATUS", online ? "ONLINE" : "OFFLINE");
  kv("IP_ADDRESS", online ? WiFi.localIP().toString() : "-");
  kv("WIFI_IP", online ? WiFi.localIP().toString() : "-");
  kv("RSSI", online ? String(WiFi.RSSI()) : "0");
  kv("WIFI_RSSI", online ? String(WiFi.RSSI()) : "0");
  kv("WIFI_SSID", online ? safeField(WiFi.SSID()) : safeField(stationSsid));
  kv("SETUP_AP_IP", WiFi.softAPIP().toString());
}

void reportModem() {
  kv("MODEM_STATUS", modemReady ? "READY" : "STARTING");
  kv("IMEI", modemImei());
  kv("SIM_STATUS", simStatusText());
  String network = networkStatusText();
  String gprs = gprsStatusText();
  kv("NETWORK", network);
  kv("NETWORK_STATUS", network);
  kv("GPRS", gprs);
  kv("GPRS_STATUS", gprs);
  kv("GSM_CSQ", String(modemReady ? modem.getSignalQuality() : -1));
  kv("NETWORK_OPERATOR", modemReady ? safeField(modem.getOperator()) : "");
  kv("APN_CONFIGURED", cellularApn.length() ? "YES" : "NO");
}

void reportGnss() {
  GnssData data = acquireGnss();
  kv("GPS_FIX", data.valid ? "VALID" : "NO_FIX");
  kv("GNSS_FIX", data.valid ? "1" : "0");
  kv("LATITUDE", String(data.latitude, 6));
  kv("LONGITUDE", String(data.longitude, 6));
  kv("SPEED", String(data.speedKph, 1));
  kv("SPEED_KPH", String(data.speedKph, 1));
  kv("ALTITUDE_M", String(data.altitudeM, 1));
  kv("GPS_ACCURACY_M", String(data.accuracyM, 1));
  kv("GNSS_ACCURACY_M", String(data.accuracyM, 1));
  kv("SATELLITES_VISIBLE", String(data.satellitesVisible));
  kv("SATELLITES_USED", String(data.satellitesUsed));
  kv("GPS_TIME", gnssTimestamp(data));
}

void reportRegistration() {
  kv("REGISTRATION_STATUS", registrationStatus);
  kv("API_CONFIGURED", apiBaseUrl.length() ? "YES" : "NO");
  kv("API_URL", apiBaseUrl);
  kv("DEVICE_NAME", safeField(deviceName));
  kv("ASSIGNED_DEVICE_UID", assignedDeviceUid);
  kv("DEVICE_TOKEN_PRESENT", deviceApiToken.length() ? "YES" : "NO");
  kv("DEVICE_TOKEN_MASKED", maskedToken(deviceApiToken));
  kv("CLAIM_TOKEN_STAGED", pendingClaimToken.length() ? "YES" : "NO");
  kv("REGISTRATION_MESSAGE", safeField(registrationMessage));
  kv("LAST_UPLOAD_STATUS", lastUploadStatus);
  kv("LAST_UPLOAD_UPTIME", lastUploadAt ? String(lastUploadAt / 1000UL) : "0");
}

void reportAll() {
  kv("READ_ALL_BEGIN", "1");
  reportIdentity();
  reportWifi();
  reportModem();
  reportGnss();
  reportRegistration();
  kv("UPTIME_SECONDS", String(millis() / 1000UL));
  kv("FREE_HEAP", String(ESP.getFreeHeap()));
  kv("READ_ALL_END", "1");
}

bool prepareHttpClient(const String &url, HTTPClient &http,
                       WiFiClient &plainClient, WiFiClientSecure &secureClient) {
  if (url.startsWith("https://")) {
#if AT360_ALLOW_INSECURE_TLS
    secureClient.setInsecure();
#else
    String ca = String(AT360_ROOT_CA);
    if (ca.indexOf("REPLACE_WITH_") >= 0) {
      registrationMessage = "HTTPS blocked: production root CA not installed";
      return false;
    }
    secureClient.setCACert(AT360_ROOT_CA);
#endif
    if (WiFi.status() == WL_CONNECTED) return http.begin(secureClient, url);
    if (modemReady && modem.isGprsConnected()) return http.begin(cellularSecureClient, url);
    registrationMessage = "No active client for HTTPS";
    return false;
  }
  if (url.startsWith("http://")) {
    if (WiFi.status() == WL_CONNECTED) return http.begin(plainClient, url);
    if (modemReady && modem.isGprsConnected()) return http.begin(cellularClient, url);
    registrationMessage = "No active client for HTTP";
    return false;
  }
  registrationMessage = "Unsupported API URL scheme";
  return false;
}

bool parseRegistrationResponse(const String &body, String &uid, String &token,
                               String &message) {
  JsonDocument document;
  DeserializationError error = deserializeJson(document, body);
  if (error) {
    message = "Invalid registration JSON response";
    return false;
  }
  bool success = document["success"] | false;
  const char *uidValue = document["device_uid"] | "";
  if (!strlen(uidValue)) uidValue = document["deviceUid"] | "";
  const char *tokenValue = document["device_token"] | "";
  if (!strlen(tokenValue)) tokenValue = document["deviceToken"] | "";
  const char *messageValue = document["message"] | "";
  uid = String(uidValue);
  token = String(tokenValue);
  message = String(messageValue);
  return success && uid.length() && token.length();
}

bool internetAvailable() {
  return WiFi.status() == WL_CONNECTED ||
         (modemReady && modem.isGprsConnected());
}

void registerDevice() {
  if (registrationStatus == "REGISTERED") {
    registrationMessage = "Already registered; clear registration before reclaiming";
    kv("REGISTRATION_STATUS", registrationStatus);
    kv("REGISTRATION_MESSAGE", registrationMessage);
    return;
  }
  if (!internetAvailable()) {
    registrationStatus = "FAILED";
    registrationMessage = "No Wi-Fi or cellular data connection";
    reportRegistration();
    return;
  }
  if (!validApiBaseUrl(apiBaseUrl)) {
    registrationStatus = "FAILED";
    registrationMessage = "Valid HTTPS API URL required";
    reportRegistration();
    return;
  }
  if (pendingClaimToken.length() < 8) {
    registrationStatus = "FAILED";
    registrationMessage = "Claim token missing or too short";
    reportRegistration();
    return;
  }

  registrationStatus = "REGISTERING";
  registrationMessage = "Registration request started";
  reportRegistration();

  JsonDocument document;
  document["claim_token"] = pendingClaimToken;
  document["hardware_uid"] = hardwareUid();
  document["imei"] = modemImei();
  document["board_profile"] = BOARD_PROFILE;
  document["firmware_version"] = FIRMWARE_VERSION;
  document["device_name"] = deviceName;
  document["capabilities"][0] = "GNSS";
  document["capabilities"][1] = "WIFI";
  document["capabilities"][2] = "CELLULAR";
  String payload;
  serializeJson(document, payload);

  HTTPClient http;
  WiFiClient plainClient;
  WiFiClientSecure secureClient;
  String url = joinUrl(apiBaseUrl, registerPath);
  if (!prepareHttpClient(url, http, plainClient, secureClient)) {
    registrationStatus = "FAILED";
    reportRegistration();
    return;
  }
  http.setTimeout(20000);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("Accept", "application/json");
  int statusCode = http.POST(payload);
  String responseBody = statusCode > 0 ? http.getString() : "";
  http.end();

  String uid, token, message;
  if (statusCode >= 200 && statusCode < 300 &&
      parseRegistrationResponse(responseBody, uid, token, message)) {
    saveDeviceCredentials(uid, token);
    pendingClaimToken = "";
    registrationMessage = message.length() ? message : "Device registered successfully";
  } else {
    registrationStatus = "FAILED";
    registrationMessage = "HTTP " + String(statusCode) + ": " +
                          (message.length() ? message : "Registration rejected");
  }
  reportRegistration();
}

void uploadTelemetry() {
  if (registrationStatus != "REGISTERED" || !deviceApiToken.length()) {
    lastUploadStatus = "BLOCKED_NOT_REGISTERED";
    kv("UPLOAD_STATUS", lastUploadStatus);
    return;
  }
  if (!internetAvailable()) {
    lastUploadStatus = "FAILED_NO_CONNECTION";
    kv("UPLOAD_STATUS", lastUploadStatus);
    return;
  }

  GnssData data = acquireGnss();
  JsonDocument document;
  document["device_uid"] = assignedDeviceUid;
  document["hardware_uid"] = hardwareUid();
  document["firmware_version"] = FIRMWARE_VERSION;
  document["mode"] = operatingMode;
  document["uptime_seconds"] = millis() / 1000UL;
  document["gnss"]["fix"] = data.valid;
  document["gnss"]["latitude"] = data.latitude;
  document["gnss"]["longitude"] = data.longitude;
  document["gnss"]["speed_kph"] = data.speedKph;
  document["gnss"]["altitude_m"] = data.altitudeM;
  document["gnss"]["accuracy_m"] = data.accuracyM;
  document["gnss"]["satellites"] = data.satellitesUsed;
  document["gnss"]["timestamp"] = gnssTimestamp(data);
  document["wifi"]["connected"] = WiFi.status() == WL_CONNECTED;
  document["wifi"]["rssi"] = WiFi.status() == WL_CONNECTED ? WiFi.RSSI() : 0;
  document["cellular"]["csq"] = modemReady ? modem.getSignalQuality() : -1;
  document["cellular"]["network"] = networkStatusText();
  String payload;
  serializeJson(document, payload);

  HTTPClient http;
  WiFiClient plainClient;
  WiFiClientSecure secureClient;
  String url = joinUrl(apiBaseUrl, telemetryPath);
  if (!prepareHttpClient(url, http, plainClient, secureClient)) {
    lastUploadStatus = "FAILED_TLS_CONFIGURATION";
    kv("UPLOAD_STATUS", lastUploadStatus);
    return;
  }
  http.setTimeout(20000);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("Accept", "application/json");
  http.addHeader("Authorization", "Bearer " + deviceApiToken);
  int statusCode = http.POST(payload);
  http.end();
  lastUploadAt = millis();
  lastUploadStatus = (statusCode >= 200 && statusCode < 300)
                       ? "SUCCESS" : "FAILED_HTTP_" + String(statusCode);
  kv("UPLOAD_STATUS", lastUploadStatus);
}

void startWifiScan() {
  if (wifiScanActive) { kv("WIFI_SCAN_FAILED", "ALREADY_RUNNING"); return; }
  WiFi.mode(WIFI_AP_STA);
  WiFi.scanDelete();
  kv("WIFI_SCAN_BEGIN", "1");
  int result = WiFi.scanNetworks(true, true);
  if (result == WIFI_SCAN_FAILED) { kv("WIFI_SCAN_FAILED", "START_FAILED"); return; }
  wifiScanActive = true;
  wifiScanStartedAt = millis();
}

void pollWifiScan() {
  if (!wifiScanActive) return;
  int count = WiFi.scanComplete();
  if (count == WIFI_SCAN_RUNNING) {
    if (millis() - wifiScanStartedAt > 35000UL) {
      WiFi.scanDelete(); wifiScanActive = false;
      kv("WIFI_SCAN_FAILED", "FIRMWARE_TIMEOUT");
    }
    return;
  }
  if (count == WIFI_SCAN_FAILED) {
    WiFi.scanDelete(); wifiScanActive = false;
    kv("WIFI_SCAN_FAILED", "SCAN_FAILED"); return;
  }
  for (int i = 0; i < count; ++i) {
    String security = WiFi.encryptionType(i) == WIFI_AUTH_OPEN ? "OPEN" : "SECURED";
    Serial.println("WIFI_RESULT=" + safeField(WiFi.SSID(i)) + "|" +
                   String(WiFi.RSSI(i)) + "|" + security + "|" +
                   String(WiFi.channel(i)));
    delay(1);
  }
  kv("WIFI_SCAN_END", String(count));
  WiFi.scanDelete();
  wifiScanActive = false;
}

void connectWifi() {
  if (!stationSsid.length()) { kv("WIFI_FAILED", "SSID_NOT_SET"); return; }
  saveNetworkSettings();
  WiFi.mode(WIFI_AP_STA);
  WiFi.disconnect(false, false);
  delay(100);
  WiFi.begin(stationSsid.c_str(), stationPassword.c_str());
  kv("WIFI_CONNECTING", safeField(stationSsid));
}

void connectGprs() {
  if (!modemReady) { kv("GPRS_STATUS", "MODEM_NOT_READY"); return; }
  if (!cellularApn.length()) { kv("GPRS_STATUS", "APN_CONFIG_REQUIRED"); return; }
  if (!modem.isNetworkConnected() && !modem.waitForNetwork(60000L, true)) {
    kv("GPRS_STATUS", "NETWORK_TIMEOUT"); return;
  }
  bool ok = modem.gprsConnect(cellularApn.c_str(),
                              cellularUser.c_str(), cellularPassword.c_str());
  kv("GPRS", ok ? "CONNECTED" : "FAILED");
  kv("GPRS_STATUS", ok ? "CONNECTED" : "FAILED");
}

void powerOnModem() {
  pinMode(MODEM_POWER, OUTPUT);
  digitalWrite(MODEM_POWER, HIGH);
  delay(100);
  pinMode(MODEM_PWRKEY, OUTPUT);
  digitalWrite(MODEM_PWRKEY, HIGH);
  delay(100);
  digitalWrite(MODEM_PWRKEY, LOW);
  delay(1200);
  digitalWrite(MODEM_PWRKEY, HIGH);
}

void attemptModemInit() {
  if (modemReady || millis() - lastModemAttemptAt < 5000UL) return;
  lastModemAttemptAt = millis();
  if (modem.testAT(800)) {
    modemReady = true;
    kv("MODEM_STATUS", "READY");
    gnssEnabled = modem.enableGPS();
    kv("GNSS_ENABLED", gnssEnabled ? "YES" : "NO");
  } else kv("MODEM_STATUS", "STARTING");
}

void handleCommand(String command) {
  command.trim();
  if (!command.length()) return;

  if (command == "HELLO" || command == "SHOW_CONFIG" || command == "READ_IDENTITY") reportIdentity();
  else if (command == "READ_ALL") reportAll();
  else if (command == "SCAN_WIFI") startWifiScan();
  else if (command.startsWith("SET_SSID=")) { stationSsid = command.substring(9); kv("OK", "SSID_STAGED"); }
  else if (command.startsWith("SET_WIFI_PASSWORD=")) { stationPassword = command.substring(18); kv("OK", "PASSWORD_STAGED"); }
  else if (command == "CONNECT_WIFI" || command == "SAVE_CONNECT_WIFI") connectWifi();
  else if (command == "READ_WIFI_STATUS") reportWifi();
  else if (command.startsWith("SET_APN=")) { cellularApn = command.substring(8); saveNetworkSettings(); kv("OK", "APN_SAVED"); }
  else if (command.startsWith("SET_APN_USER=")) { cellularUser = command.substring(13); saveNetworkSettings(); kv("OK", "APN_USER_SAVED"); }
  else if (command.startsWith("SET_APN_PASSWORD=")) { cellularPassword = command.substring(17); saveNetworkSettings(); kv("OK", "APN_PASSWORD_SAVED"); }
  else if (command.startsWith("SET_API_URL=")) { apiBaseUrl = command.substring(12); saveRegistrationConfig(); kv("OK", "API_URL_SAVED"); }
  else if (command.startsWith("SET_REGISTER_PATH=")) { registerPath = command.substring(18); saveRegistrationConfig(); kv("OK", "REGISTER_PATH_SAVED"); }
  else if (command.startsWith("SET_TELEMETRY_PATH=")) { telemetryPath = command.substring(19); saveRegistrationConfig(); kv("OK", "TELEMETRY_PATH_SAVED"); }
  else if (command.startsWith("SET_DEVICE_NAME=")) { deviceName = command.substring(16); saveRegistrationConfig(); kv("OK", "DEVICE_NAME_SAVED"); }
  else if (command.startsWith("SET_CLAIM_TOKEN=")) { pendingClaimToken = command.substring(16); kv("OK", "CLAIM_TOKEN_STAGED"); }
  else if (command == "REGISTER_DEVICE") registerDevice();
  else if (command == "READ_REGISTRATION_STATUS") reportRegistration();
  else if (command == "CLEAR_REGISTRATION=CONFIRM") { clearDeviceCredentials(); reportRegistration(); }
  else if (command == "CLEAR_REGISTRATION") kv("ERROR", "CONFIRMATION_REQUIRED");
  else if (command == "READ_STATUS") { reportIdentity(); reportWifi(); reportModem(); reportRegistration(); }
  else if (command == "READ_TRACKING") reportGnss();
  else if (command == "CHECK_NETWORK") reportModem();
  else if (command == "CONNECT_GPRS") connectGprs();
  else if (command == "DISCONNECT_GPRS") { if (modemReady) modem.gprsDisconnect(); reportModem(); }
  else if (command == "ENABLE_GNSS") { gnssEnabled = modemReady && modem.enableGPS(); kv("GNSS_ENABLED", gnssEnabled ? "YES" : "NO"); }
  else if (command == "SEND_NOW") uploadTelemetry();
  else if (command == "MODE_LIVE") { operatingMode = "LIVE"; kv("MODE", operatingMode); }
  else if (command == "MODE_SIMULATION") { operatingMode = "SIMULATION"; kv("MODE", operatingMode); }
  else kv("ERROR", "UNKNOWN_COMMAND:" + command);
}

void pollSerial() {
  while (Serial.available()) {
    char character = (char)Serial.read();
    if (character == '\n' || character == '\r') {
      if (serialLine.length()) { handleCommand(serialLine); serialLine = ""; }
    } else if (serialLine.length() < 768) serialLine += character;
  }
}

String htmlEscape(String value) {
  value.replace("&", "&amp;"); value.replace("<", "&lt;");
  value.replace(">", "&gt;"); value.replace("\"", "&quot;");
  return value;
}

String page(const String &message = "") {
  String html;
  html.reserve(9000);
  html += F("<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>AssetTrack 360 Setup</title><style>");
  html += F("body{font-family:Arial;background:#071f2d;color:#eef7fa;margin:0;padding:18px}main{max-width:820px;margin:auto}h1,h2{color:#12cbe5}.card{background:#0d3850;padding:18px;margin:14px 0;border-radius:9px}label{display:block;margin-top:10px}input{width:100%;box-sizing:border-box;padding:10px;margin-top:4px}button{padding:11px 16px;margin:12px 8px 0 0;background:#12cbe5;border:0;font-weight:bold}.danger{background:#ff725e}.ok{color:#9eea63}.warn{color:#ffd166}.small{font-size:12px;color:#aac4d0}</style></head><body><main>");
  html += F("<h1>AssetTrack 360 LILYGO GNSS</h1><p>Firmware: "); html += FIRMWARE_VERSION; html += F("</p>");
  if (message.length()) html += "<p class='ok'>" + htmlEscape(message) + "</p>";
  html += F("<div class='card'><h2>1. Wi-Fi</h2><form method='post' action='/wifi'><label>SSID</label><input name='ssid' value='");
  html += htmlEscape(stationSsid); html += F("'><label>Password</label><input type='password' name='pass'><button>Save and Connect</button></form></div>");
  html += F("<div class='card'><h2>2. Cellular APN</h2><form method='post' action='/apn'><label>APN</label><input name='apn' value='");
  html += htmlEscape(cellularApn); html += F("'><label>Username</label><input name='user' value='"); html += htmlEscape(cellularUser);
  html += F("'><label>Password</label><input type='password' name='pass'><button>Save APN</button></form></div>");
  html += F("<div class='card'><h2>3. AssetTrack 360 Registration</h2><form method='post' action='/register'><label>API base URL</label><input name='api' placeholder='https://server.example' value='");
  html += htmlEscape(apiBaseUrl); html += F("'><label>Device name</label><input name='name' value='"); html += htmlEscape(deviceName);
  html += F("'><label>Claim / registration token</label><input type='password' name='claim' autocomplete='off'><button>Save and Register Device</button></form>");
  html += "<p>Status: <b>" + htmlEscape(registrationStatus) + "</b></p>";
  html += "<p>Assigned Device UID: " + htmlEscape(assignedDeviceUid.length() ? assignedDeviceUid : "Not assigned") + "</p>";
  html += "<p>Device token: " + htmlEscape(maskedToken(deviceApiToken).length() ? maskedToken(deviceApiToken) : "Not assigned") + "</p>";
  html += "<p>Message: " + htmlEscape(registrationMessage) + "</p>";
  html += F("<form method='post' action='/clear'><label><input style='width:auto' type='checkbox' name='confirm' value='YES'> Confirm local registration removal</label><button class='danger'>Clear Registration</button></form></div>");
  html += F("<div class='card'><h2>Live Status</h2>");
  html += "<p>Hardware UID: " + hardwareUid() + "</p>";
  html += "<p>Wi-Fi: " + String(WiFi.status() == WL_CONNECTED ? "ONLINE" : "OFFLINE") + "</p>";
  html += "<p>IP: " + String(WiFi.status() == WL_CONNECTED ? WiFi.localIP().toString() : "-") + "</p>";
  html += "<p>Modem: " + String(modemReady ? "READY" : "STARTING") + "</p>";
  html += "<p>SIM: " + simStatusText() + " | Network: " + networkStatusText() + " | GPRS: " + gprsStatusText() + "</p>";
  html += F("<form method='post' action='/send'><button>Send Telemetry Now</button></form><p>Last upload: "); html += lastUploadStatus;
  html += F("</p><p class='small'>The full claim token and permanent device token are never shown on this page or returned by diagnostics.</p></div></main></body></html>");
  return html;
}

void setupWeb() {
  WiFi.mode(WIFI_AP_STA);
  WiFi.softAP(SETUP_AP_SSID, SETUP_AP_PASSWORD);
  web.on("/", HTTP_GET, []() { web.send(200, "text/html", page()); });
  web.on("/wifi", HTTP_POST, []() {
    stationSsid = web.arg("ssid"); stationPassword = web.arg("pass");
    connectWifi(); web.send(200, "text/html", page("Wi-Fi settings saved; connection started."));
  });
  web.on("/apn", HTTP_POST, []() {
    cellularApn = web.arg("apn"); cellularUser = web.arg("user"); cellularPassword = web.arg("pass");
    saveNetworkSettings(); web.send(200, "text/html", page("Cellular APN settings saved."));
  });
  web.on("/register", HTTP_POST, []() {
    apiBaseUrl = web.arg("api"); deviceName = web.arg("name"); pendingClaimToken = web.arg("claim");
    saveRegistrationConfig(); registerDevice(); web.send(200, "text/html", page());
  });
  web.on("/clear", HTTP_POST, []() {
    if (web.arg("confirm") == "YES") clearDeviceCredentials();
    else registrationMessage = "Clear registration was not confirmed";
    web.send(200, "text/html", page());
  });
  web.on("/send", HTTP_POST, []() { uploadTelemetry(); web.send(200, "text/html", page()); });
  web.on("/status", HTTP_GET, []() {
    JsonDocument document;
    document["board_profile"] = BOARD_PROFILE;
    document["firmware"] = FIRMWARE_VERSION;
    document["hardware_uid"] = hardwareUid();
    document["registration_status"] = registrationStatus;
    document["assigned_device_uid"] = assignedDeviceUid;
    document["device_token_present"] = deviceApiToken.length() > 0;
    document["wifi_status"] = WiFi.status() == WL_CONNECTED ? "ONLINE" : "OFFLINE";
    document["modem_status"] = modemReady ? "READY" : "STARTING";
    String json; serializeJson(document, json);
    web.send(200, "application/json", json);
  });
  web.onNotFound([]() { web.send(404, "text/plain", "Not found"); });
  web.begin();
}

void setup() {
  Serial.begin(115200);
  delay(250);
  loadSettings();
  setupWeb();
  powerOnModem();
  SerialAT.begin(MODEM_BAUD, SERIAL_8N1, MODEM_RX, MODEM_TX);
  delay(100);
  reportIdentity();
  reportWifi();
  reportRegistration();
  kv("MODEM_STATUS", "STARTING");
  kv("READY", "1");
}

void loop() {
  pollSerial();
  pollWifiScan();
  web.handleClient();
  attemptModemInit();

  static wl_status_t previousWifiStatus = WL_IDLE_STATUS;
  wl_status_t currentWifiStatus = WiFi.status();
  if (currentWifiStatus != previousWifiStatus) {
    previousWifiStatus = currentWifiStatus;
    reportWifi();
  }
  delay(2);
}
