ASSETTRACK 360 - FULL SITE RESPONSE REV02
Based on the user-uploaded assettrack-3600.zip.txt baseline.
Scope: site response only. Mobile client, telemetry ingestion, tracking algorithms,
models and firmware are unchanged from that upload.

CHANGES
- Email Notifications fixture: 8 SQL queries reduced to 4.
- Static CSS/JS: no authenticated-user database query; versioned resources cached.
- User/customer/subscription loaded together; entitlement reused within one request.
  No cross-request user cache. Existing payment and subscription rules preserved.
- Retention runs in a separate background app context, not every page request.
  Existing retention rules remain active. Advisory lock stays on one connection.
- Four Gunicorn threads instead of a single synchronous request worker.
- Asset page refresh reduced from every second to every 15 seconds.
- Dashboard/detail/history page address lookups are cache-only. The existing
  authenticated address endpoint still performs provider lookups when requested.
- Server-Timing includes app and SQL durations; SQL count and build headers added.
  Slow request logs contain paths/timings, not tokens or query parameters.
- Authenticated HTML remains private/no-store. No unsafe HTML caching.

DEPLOY
Keep this full ZIP and Upload_AssetTrack_FULL_REV04.ps1 together in Downloads.
Run the new uploader. It overlays ALL packaged source into
wykiesautomation/assettrack-360-platform main, not a changed-file patch.
It does not clear the repo, force-push, upload .env or upload databases.
Keep DATABASE_URL and all hosting secrets unchanged.
If hosting has a custom Start Command, use:
gunicorn -w 1 --threads 4 -b 0.0.0.0:$PORT app:app
Dockerfile/render.yaml already use four threads.

VALIDATION
Local synthetic SQLite fixture, with an artificial 25ms delay per SQL statement:
query budgets, settings save, tenant isolation, subscription gate, anonymous
access, logout and blocked-background-job isolation PASS. Python syntax PASS.
This is not a live Railway/Neon/PostgreSQL performance benchmark. No promise
that the measured live 2.63 seconds is eliminated until deployment is tested.
PowerShell uploader is statically checked, not executed on Windows here.

AFTER DEPLOY
Uncheck Disable cache in DevTools for normal navigation measurement.
Email page response headers must show X-AssetTrack-Build: SiteResponse-REV02.
Compare request Time, Server-Timing app/sql and X-AssetTrack-SQL-Count.
If Time remains high while app is low, investigate network/proxy/hosting delay.
If app/sql remain high, use slow-page logs to investigate database latency.
Do not change the phone registration or tracking configuration for this build.

MAINTENANCE
SITE_MAINTENANCE_BACKGROUND=false disables background retention for diagnosis;
only use this with an alternative retention schedule. Default remains true.
Backup the database before deployment because existing retention remains active.

COMPLETE SOURCE
All uploaded source files retained, excluding generated caches and local DBs.
This build does not incorporate unrelated prior phone fixes from another ZIP.
