# AssetTrack 360 SIM808 Signed HTTP REV14

## Railway variables
```text
SIM808_LEGACY_INGRESS_ENABLED=true
SIM808_LEGACY_HOST=sim808-ingest.wykiesautomation.co.za
```

## Cloudflare
- Proxied CNAME `sim808-ingest` to the current Railway hostname.
- Exclude this hostname from HTTP-to-HTTPS redirect.
- Bypass cache and browser challenges for POST `/api/v1/sim808-legacy-ingest`.
- Keep all other AssetTrack hostnames HTTPS-only.

## Application registration
Confirm `app/__init__.py` imports and registers `legacy_sim808.bp`.

## Security
Payload is authenticated but not encrypted on 2G HTTP. Never include secrets in telemetry. Device Token is never sent.
