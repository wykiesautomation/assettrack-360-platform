AssetTrack 360 REV31 SIM800L Signed HTTP Ingress

PURPOSE
Allows the legacy SIM800L modem to upload authenticated telemetry over plain HTTP on one isolated hostname/path. The device token is NOT sent on this path; the exact JSON body is signed with SHA-256(token + "|" + body + "|" + token). Payload is authenticated but not encrypted. Never include secrets in telemetry.

RAILWAY VARIABLES
SIM800L_LEGACY_INGRESS_ENABLED=true
SIM800L_LEGACY_HOST=sim800-ingest.wykiesautomation.co.za

CLOUDFLARE
1. Create proxied CNAME sim800-ingest.wykiesautomation.co.za to the existing Railway hostname.
2. Exclude ONLY this hostname from Always Use HTTPS / HTTP redirect.
3. Allow POST without browser challenge for /api/v1/sim800l-legacy-ingest.
4. Keep every other AssetTrack hostname HTTPS-only.

DEPLOY
Deploy the contents of assettrack-360-platform-main to the existing service. Keep DATABASE_URL, database and current device identity/token unchanged. Do not reclaim.

FLASH
Flash AssetTrack360_TCALL_IO_REV31_SIGNED_HTTP.ino.txt. Existing saved UID/token/APN are retained by Preferences. On GPRS the sketch automatically uses the signed HTTP ingress. Wi-Fi still uses the configured HTTPS API.

EXPECTED LOG
CELLULAR_INGRESS_MODE=SIGNED_HTTP_SHA256
AUTH_HEADER_MODE=SIGNED_HTTP_SHA256
HTTP_RESPONSE_STATUS=202
UPLOAD_STATUS=SUCCESS
