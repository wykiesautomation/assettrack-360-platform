AssetTrack 360 SIM808 REV16 Firmware Identity Database Fix

Root cause:
The REV16 firmware identity is 49 characters, but PostgreSQL device.firmware was VARCHAR(40). Every telemetry transaction rolled back during commit and returned HTTP 500.

Fix:
- Device.firmware expanded to 100 characters.
- Production startup alters PostgreSQL device.firmware to VARCHAR(100).
- Claim and telemetry paths retain up to 100 characters.

No firmware reflash, new claim, Cloudflare change or Railway variable change is required. REV16 autonomous retry will upload again automatically.
