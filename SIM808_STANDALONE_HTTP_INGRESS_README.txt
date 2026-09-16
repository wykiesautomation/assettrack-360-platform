AssetTrack 360 SIM808 Standalone Signed HTTP Ingress

Railway variables:
SIM808_LEGACY_INGRESS_ENABLED=true
SIM808_LEGACY_HOST=sim808-ingest.wykiesautomation.co.za

Cloudflare:
1. Create proxied CNAME sim808-ingest.wykiesautomation.co.za to the existing Railway service.
2. Add a hostname-specific rule that does not redirect HTTP to HTTPS for this hostname only.
3. Keep all other AssetTrack hostnames HTTPS-only.
4. Bypass cache and allow POST only on /api/v1/sim808-legacy-ingest.

Security:
The Device Token is never transmitted. The exact JSON body is authenticated with SHA-256(token + '|' + body + '|' + token). The server validates SIM808 device type, signature, sequence, tenant, subscription, body size and rate. Payload contents are not confidential on 2G HTTP, so never place secrets in telemetry. New LTE hardware must use TLS.

Acceptance:
Deploy web ZIP, set variables, configure Cloudflare, flash the included sketch with TinySHA256.h in the same sketch folder, provision once, confirm UPLOAD|ACCEPTED, remove USB while external power remains, wait two intervals, then power-cycle and repeat.
