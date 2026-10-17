AssetTrack 360 Predictive Safety Twin Left Navigation Final Fix

This patch was applied directly to assettrack-360-platform-main_PREDICTIVE_SAFETY_TWIN_FINAL.zip.

Root cause: generic Safety Twin CSS classes .side and .brand collided with the production AssetTrack shell. Operational Truth and Evidence Chain replaced the normal left navigation visually.

Fix: internal classes are namespaced as .twin-side and .twin-brand; common panel, metric, action and mode selectors are scoped under .twin-shell; responsive rules are also scoped.

Preserved: the full Predictive Safety Twin conversion, Geofence Zones Save V2, current routes, APIs, database logic, firmware, mobile tracking and all other files from the uploaded FINAL baseline.
