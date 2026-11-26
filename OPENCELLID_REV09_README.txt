OpenCellID Network Location REV09 - full cumulative backend from gnss.zip.txt.
Deploy CONTENTS of assettrack-360-platform-main to existing repository/backend service.
Back up repository/database; normal commit/push/redeploy. No force push or database reset.
Railway variable: AT360_OPENCELLID_API_KEY = private OpenCellID token (already entered by user).
Google location key is unused. No Google fallback. No new claim or token rotation.
Keep firmware REV25 and Builder REV23. No schema migration or hardware changes added.
After active deployment: hard refresh Lilly -> OpenCellID key Configured.
READ CELL -> wait -> SEND NOW -> refresh. ESTIMATED_CELL_LOCATION/CACHED_CELL_LOCATION
means provider coordinates returned. CELL_NOT_FOUND means missing cell coverage, not GPS failure.
Provider key/limits/errors are shown without raw provider text or secret.
Serving-cell lookup only, not triangulation. Marker is estimated CELL location, not precise board.
Range shown only if supplied/valid, not verified device accuracy; missing range means no circle.
No GPS rows, speed, trips or geofence calculations from these estimates.
Old Google positions are hidden, not relabelled. Consent text now names OpenCellID.
Same-cell success cache 24h; lookup throttle 5min per device, not a distributed quota guarantee.
HTTPS lookup remains synchronous with 4s timeout. Live provider acceptance still required.
OpenCellID CC BY-SA 4.0 attribution included; observe dataset attribution/share-alike terms.
No guarantee of universal coverage, free commercial scale or precise location.
Rollback: revert four modified web files and redeploy. No device/database rollback needed.
Sources: https://docs.opencellid.org/docs/api/cell-position
https://docs.opencellid.org/docs/api/errors
https://docs.opencellid.org/docs/attribution
