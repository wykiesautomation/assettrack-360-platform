AssetTrack 360 SIM800L Signed HTTP Bridge REV32

Fixes HTTP 421 sim800l_host_required after the Cloudflare Worker correctly removes the Railway HTTP 301.
Backend accepts the original SIM800L host only through an authenticated bridge header and then validates device UID, exact raw body signature, sequence, active SIM800L profile and rate limit before invoking existing /api/v2/telemetry logic.
No device token is sent by the modem. No claim, token rotation, firmware flash, database reset or migration.

DEPLOY BACKEND
Overlay assettrack-360-platform-main on the current repository and redeploy.
Railway variables:
 SIM800L_LEGACY_INGRESS_ENABLED=true
 SIM800L_LEGACY_HOST=sim800-ingest.wykiesautomation.co.za
 SIM800L_BRIDGE_SECRET=<new long random secret>
Keep AT360_OPENCELLID_API_KEY and all existing variables unchanged.

DEPLOY WORKER
Replace Worker code with CLOUDFLARE_SIM800L_WORKER.js.
Worker Settings -> Variables and Secrets: add encrypted secret SIM800L_BRIDGE_SECRET with exactly the same value as Railway.
Keep route exactly: sim800-ingest.wykiesautomation.co.za/api/v1/sim800l-legacy-ingest*
Deploy Worker.

TEST
curl.exe -I --max-redirs 0 http://sim800-ingest.wykiesautomation.co.za/api/v1/sim800l-legacy-ingest
Expected 404 for HEAD, not 301. Then SEND NOW once. Expected HTTP 202 / UPLOAD_STATUS=SUCCESS if signature and profile match.
401 invalid_signature means firmware signature format/body differs. 401 unauthorized_sim800l_device means live profile mismatch. 421 means bridge secret/original-host mismatch. 503 bridge_secret_not_configured means Worker secret missing.
