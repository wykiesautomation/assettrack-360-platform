AssetTrack 360 Dashboard 500 Fix

Root cause fixed:
- base.html called url_for("main.fleet_tracking")
- fleet_tracking() existed but had no @bp route decorator
- Werkzeug therefore raised BuildError on every authenticated page that extended base.html

Correction:
- Added @bp.get("/fleet-tracking") above fleet_tracking()
- The link now resolves and routes GPS-capable customer devices into the existing tracking/safety workflow
- Pinned compatible urllib3 and charset-normalizer versions to eliminate the deployment RequestsDependencyWarning

Deployment:
1. Replace repository contents with this cumulative pack.
2. Commit and push to main.
3. Redeploy the existing AssetTrack service.
4. Keep the existing DATABASE_URL and environment secrets unchanged.
5. Test /login, /dashboard, /fleet-tracking and /health.

Copyright: © 2026 JP Van Wyk. All rights reserved.
