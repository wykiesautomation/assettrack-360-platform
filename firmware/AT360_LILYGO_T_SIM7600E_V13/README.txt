AssetTrack 360 LILYGO T-SIM7600E V1.3 Firmware

Board: photographed LILYGO V1.3 PCB 20200310 with SIM7600E.
Arduino target: ESP32 Dev Module; PSRAM Enabled; 4 MB flash; Huge APP partition recommended.
Libraries: TinyGSM, ArduinoJson. ESP32 core supplies WiFi, HTTPClient and Preferences.

1. Install LTE and GNSS antennas before powering the modem.
2. Set CELLULAR_APN. Wi-Fi fields are optional.
3. Flash the .ino and open Serial Monitor at 115200.
4. In AssetTrack 360 select LILYGO T-SIM7600E V1.3 and create a hardware claim code.
5. Enter: CLAIM XXXX-XXXX
6. The token is stored in ESP32 NVS. Never place a production token in source code.

Safety: no customer output channels are implemented. GPIO4, 25, 26, 27, 32, 33, 34, 35 and 36 are board-reserved. GPIO2, 13, 14 and 15 are reserved for microSD.

Note: battery and solar divider factors must be bench-verified before relying on voltage values. The firmware intentionally marks SD status uncertain until SD support is enabled.
