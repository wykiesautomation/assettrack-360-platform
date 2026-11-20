AssetTrack 360 ESP32-D and ESP32-WROOM Claim Alignment

This is a cumulative patch applied directly to assettrack-360-platform-main_WEB_MOBILE_AUTH_MAP_FIXED.zip. Nothing was removed from that baseline.

Canonical hardware identities:
- AT360_ESP32_WROOM32 -> AT360-WROOM32-<BOARD_ID>
- AT360_ESP32D_EXPANDED -> AT360-ESP32D-<BOARD_ID>

Both POST /api/v2/devices/claim and POST /api/v1/device/claim now use the same profile-specific UID rules. Existing same-customer legacy records using AT360-<BOARD_ID> or AT360-BOARD-<BOARD_ID> are safely reused and renamed to the canonical UID instead of creating duplicate devices. Token and Device UID continue to be issued as one claim pair.

No mobile web, map, QR, safety, SIM808, billing, templates, migrations, firmware or other platform files were removed.
