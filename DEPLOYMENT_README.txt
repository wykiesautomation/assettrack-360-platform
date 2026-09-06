AssetTrack 360 production deployment pack
Dashboard Status Logic Fixed

Includes only the web application, templates/static assets, required worker scripts,
Render/Docker configuration, dependencies and database migration SQL files.
Old build notes, manifests, tests, caches, firmware and development helpers are excluded.

Dashboard connectivity truth:
ONLINE <= 90 seconds
DELAYED 91 seconds to 5 minutes
OFFLINE > 5 minutes
NEVER SEEN when no contact exists

Visual status alignment:
ONLINE is bright green; DELAYED is amber; OFFLINE is red; NEVER SEEN is muted grey.

Trends & Limits device selection:
Selected Device is now a real dropdown listing every active registered customer device, UID, type and linked asset. Selecting a device reloads only that device's assigned, capability-aware pins or mobile points.
