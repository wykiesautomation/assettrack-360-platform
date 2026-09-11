AssetTrack 360 Hardware Claim API Fix

Fixed routes:
- POST /api/v2/devices/claim is authoritative for Device Studio and Device Centre hardware codes.
- POST /api/v1/device/claim remains compatible with existing clients.
- POST /api/v1/android/register is Android/mobile only.

SIM808 profile:
AT360_SIM808_TRACKER_2AI_2DO

After deployment, generate a NEW SIM808 hardware claim code. Old mobile registration codes remain mobile-only by design.
