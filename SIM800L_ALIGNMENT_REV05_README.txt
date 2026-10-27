AssetTrack 360 SIM800L Alignment REV05
Build: 2026-10-23
This is a source alignment/test pack, NOT a certified production release.

CONTENTS
backend/: complete uploaded backend with targeted customer-facing cleanup.
board_builder/: REV17, based on supplied REV16.
firmware/: REV19, based on supplied REV18.

CHANGES
Builder installation now includes APN/user/password. Wi-Fi setup uses the
SIM800L command sequence. Separate link/reason/TLS/network storage fields.
Firmware saves network/API settings independently of complete credentials.
Physical readings cannot be uploaded as GOOD while in Simulation.
TLS verification is enabled by default. No public plaintext downgrade.
Unsupported OTA commands explicitly report USB-only.
Backend removes stale SIM7000G customer card branches and solution references.
SIM800L is added only to firmware-compatible monitoring solution lists.
Historical SIM7000G identity/repair guards remain deliberately: these protect
existing records and enable explicit admin repair without UID/token deletion.
No automatic database migration, device conversion, token rotation or deletion.

IMPORTANT HTTPS BLOCKER
The supplied REV18 has a placeholder root CA and insecure TLS enabled.
REV19 retains the placeholder but disables insecure TLS. Before flashing for
cloud use, replace REPLACE_WITH_ASSETTRACK360_SERVER_ROOT_CA with the verified
PEM root CA for your actual API server. Otherwise HTTPS fails closed with -101.
This pack does NOT pretend that a valid CA or physical GSM test was supplied.
Install Arduino libraries: TinyGSM, ArduinoHttpClient, ArduinoJson 7,
GovoroxSSLClient (not the unrelated OPEnSLab SSLClient).
https://github.com/govorox/SSLClient

DEPLOY
Use only backend/assettrack-360-platform-main contents for GitHub/Railway.
Do not upload the whole engineering pack as the app root.
Keep DATABASE_URL, secrets and existing records unchanged. No force push.
For an already registered wrong-profile device, use the existing admin profile
repair page, confirm physical SIM800L identity, retain UID/token/history.
Do not re-claim or delete an existing device.

COMMISSIONING
1. Run REV17; select T-CALL SIM800L and connect USB; READ ALL.
2. Configure actual Wi-Fi credentials and/or actual SIM APN; save.
3. Install existing matching UID/token on board; verify persistence.
4. Read Connection Diagnostics; CONNECT + TEST; inspect actual HTTP result.
5. Power-cycle; confirm saved settings and accepted upload without PC relay.
USB connection is not proof of internet/cloud connection.
Firmware pulse polling is not validated for high-speed pulse measurement.
No electrical drawings were generated or hardware-certified in this pack.
