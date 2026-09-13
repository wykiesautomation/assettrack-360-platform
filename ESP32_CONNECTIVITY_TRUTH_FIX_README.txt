AssetTrack 360 ESP32 Connectivity Truth Fix

Problem:
Push telemetry only proves that the board contacted the API at the timestamp of the accepted request. The previous 90-second ONLINE window claimed continuous connectivity after the board had already been unplugged. Some dashboard and studio areas also used independent five- or thirty-minute windows.

Corrected truth for ESP32-WROOM-32 and ESP32-D:
- 0-20 seconds since accepted contact: LIVE CONTACT / ONLINE
- 21-90 seconds: RECENT CONTACT, explicitly not online
- 91-300 seconds: DELAYED
- More than 300 seconds: OFFLINE
- No accepted contact: NEVER SEEN

Output control and Device Studio use the same strict live-contact gate. Simulation remains physically locked. Other mobile or cellular tracking policies are unchanged.
