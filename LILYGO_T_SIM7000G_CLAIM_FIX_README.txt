AssetTrack 360 LILYGO T-SIM7000G Claim Fix

Root cause:
The registry aliased AT360_LILYGO_T_SIM7000G to the separate T-SIM7600E V1.3 profile, causing HTTP 409 profile_mismatch.

Fix:
- Added a dedicated canonical AT360_LILYGO_TSIM7000G profile.
- Kept AT360_LILYGO_T_SIM7600E_V13 separate and unchanged.
- Legacy AT360_LILYGO_T_SIM7000G spelling resolves only to the new SIM7000G profile.
- Claim UID prefix is AT360-LILYGO- for SIM7000G.
- Claim page wording is board-aware rather than SIM808-only.
- REV8 first GNSS telemetry is accepted when valid, accuracy is 0-100 m, coordinates are non-zero, and the claimed device is linked to an asset.
- Existing ESP32-D, WROOM, SIM808 and SIM7600E support is preserved.

Deployment:
Replace repository contents with this cumulative pack, commit/push, and redeploy the existing service. Keep DATABASE_URL and all production secrets unchanged. Generate a new T-SIM7000G claim code after deployment.
