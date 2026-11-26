AssetTrack 360 REV30 Hardware Authentication Alignment

Root cause addressed:
- Firmware already sent Authorization: Bearer, but HTTP 403 was returned before useful error detail was visible.
- Backend accepted only a case-sensitive Bearer prefix and had no proxy-safe compatibility header.

Changes:
- Firmware trims UID/token after load, save and staging.
- Firmware sends Authorization: Bearer plus X-Device-Token and X-Device-UID.
- Firmware logs safe response body, auth mode and token length, never the full token.
- Backend accepts case-insensitive Bearer scheme or X-Device-Token fallback.
- Backend responses include X-AT360-Hardware-Auth-Build: REV30.
- Existing Device UID, token, database and history remain unchanged. Do not re-claim.

Deploy backend contents normally and flash REV30 firmware.
Expected telemetry result: HTTP 202 and UPLOAD_STATUS=SUCCESS.
If 403 remains, inspect HTTP_RESPONSE_BODY_SAFE. The uploaded backend telemetry route itself returns 401 for invalid tokens, not 403, so a continuing 403 indicates an upstream host/WAF rule or a different live deployment.
