AssetTrack 360 SIM800L Web Status & I/O REV06
Source: supplied assettracficlily.zip.txt (valid ZIP archive).

Deploy the CONTENTS of assettrack-360-platform-main to the existing repository/service.
Back up repository first. Normal commit/push and redeploy; no force push or repository clearing.
Keep DATABASE_URL, all secrets and the production database unchanged.
Do NOT flash firmware or re-claim devices. Working REV23 stays on the board.

CHANGES
- Existing SIM800L profile selects a dedicated read-only I/O asset template even if
  its existing asset_type is TRACKER. No database conversion.
- Header, connectivity card and banner use the same asset_connectivity snapshot.
- Six supported GPIO pins show existing enabled assignment values only.
- Unassigned remains UNUSED; assigned without stored readings waits for telemetry.
- Zero is preserved. SIMULATED is explicit; old/non-GOOD readings are not LIVE.
- No GPS/speed/geofence/battery cards or remote physical output commands for SIM800L.
- Existing Device Panel, Signals & Inputs, Alert Settings and alarm acknowledgement retained.
- Original GPS template banner now separates device contact from validated GPS freshness.
- Original connectivity thresholds and telemetry API unchanged.

IMPORTANT
HTTP 202 can acknowledge contact with zero stored measurements when assignments
are disabled/missing. This release does not auto-enable assignments or invent data.
Use Signals & Inputs to assign gpio_14/gpio_32 to the correct asset and configure
actual board modes locally. Check API stored/rejected lists if measurements still wait.
This is not a firmware-mode readback feature: supported functions are profile capabilities,
not proof of the current physical pin mode.

ACCEPTANCE
After deployment, hard refresh Lilly /asset/142. Expect Device & I/O Summary,
no GPS cards, consistent contact state and six pin rows. Verify a configured pin's
stored value and timestamp. Stop uploads and verify delayed/offline state on refresh.
Other board templates/routes retained. Full live acceptance still required.
Rollback: revert the web commit and redeploy; no database rollback needed.
