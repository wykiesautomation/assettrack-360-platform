AssetTrack 360 Reviewed Source REV05
Source: FleetTrack_AssetTrack_Final_GPS_Validator.zip.txt, not the older 3600 source.
Final tracking_validator.py and original stationary-drift fixture retained byte-for-byte.
New public_home.html copied from user assettracktest.zip.txt.

CONFIRMED FIXES
No GPS observations now means 0 confidence and WAITING evidence, not 95%, MEASURED or VALIDATED.
Long GPS sequences remain intact in Location; derived Reading sequence values are deterministically hashed only if longer than the existing 80-character column. No schema widening or destructive migration.
Dashboard queries batched; local query budget remains 10 with 20 extra assets.
Background retention no longer executes synchronously in page requests.
Static cache headers, four Gunicorn threads, cache-only dashboard reverse geocoding.
MOBILE_REQUEST logs include HTTP status, allowlisted reason, accepted/duplicate/rejected counts. No token, cookie, payload, coordinates or raw exception in this diagnostic module.

TESTS
14 tracking regression tests PASS. One legacy movement fixture used 11 m steps below the final validator's 30 m envelope; changed the positive fixture to 44 m steps and added a negative sub-envelope test. Validator thresholds unchanged.
Local synthetic SQLite API tests PASS: single GPS, batch GPS, 80-character sequence, duplicate, database persistence, rendered Safety Twin, zero confidence, subscription denial, heartbeat, log privacy and dashboard query growth.
SQLite fixture assigns test IDs for PostgreSQL BigInteger identities and explicitly checks reading string lengths. No live PostgreSQL or physical phone tested.
Python syntax and JS syntax PASS. Jinja template parse PASS. ZIP hashes verified.
This is a focused source review, not certification of every product feature.

IMPORTANT
The actual live cause of missing GPS is NOT conclusively proven. An expired subscription still correctly rejects GPS with 402 while heartbeat may be accepted. No entitlement bypass, device reset or token rotation.
Keep current Railway DATABASE_URL and Amsterdam region unchanged. Do not restore or delete database data.
After upload and Active deployment: reload phone tracker, keep existing registration, Start Tracking with location permission, check MOBILE_REQUEST for location. Expect 202 accepted and nonzero GPS points. If 402 subscription_inactive, resolve the customer's actual entitlement through existing admin workflow. If 401, reconcile registration; do not publish tokens.
Header X-AssetTrack-Build must be Reviewed-REV05.

UPLOAD
Place ZIP and Upload_AssetTrack_REV07.ps1 together. Uploader clones main into a fresh work folder, saves a git bundle backup, verifies all payload hashes, overlays source, commits and pushes normally. No force push, no repository deletion, no database changes. Windows uploader not executed in this Linux environment.
