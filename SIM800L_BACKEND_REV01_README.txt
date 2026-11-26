AssetTrack 360 SIM800L backend profile repair REV01
Build date: 2026-10-21. Based on the user's complete uploaded web repository.

ADDED
Separate AT360_LILYGO_TCALL_SIM800L profile and public Connect Device card.
Six GPIO14/32/33/34/35/39 points aligned with TCALL_IO_REV14.
No GNSS/LTE claims; no remote cloud output commands (firmware has no command polling).
Modem, PMU, boot, flash and PSRAM pins reserved.
Both v2 and v1 claim paths recognize the new profile and normalize physical
AT360-LILYGO-<12 hex> to one prefix. Existing SIM7000G module unchanged.
Waiting page uses generic Board Builder wording, not SIM808-only instructions.

DEPLOY
Back up the existing Git repository before overlaying this full cumulative source.
Commit/push normally and redeploy the existing service. No force push or repo deletion.
Keep DATABASE_URL, secrets and existing database unchanged.
No schema migration or automatic device/profile/token updates were added.
This pack has NOT been deployed to the live service.

CLAIM
Old SIM7000G claim codes remain SIM7000G and still return profile_mismatch.
For an unregistered board, select LILYGO T-Call SIM800L I/O in Connect Device
and generate a fresh one-time code after deployment. Use Board Builder REV13.
If a board already exists under the wrong SIM7000G profile, the server returns
existing_device_profile_repair_required rather than silently rotating its token,
renaming its UID, changing assignments or creating a duplicate.
Do NOT delete/reclaim an existing device to bypass that guard. An explicit
administrator-reviewed repair of that existing record is still required.

LIMITS
This source change does not supply the firmware root CA or enable cellular HTTPS.
A successful desktop claim does not prove autonomous board cloud telemetry.
Do not disable TLS verification or send public production tokens over plain HTTP.

TESTS
Local isolated Flask/SQLite v2 API tests passed: five profiles, six GPIO,
no GNSS/remote outputs, old-code 409, new SIM800L 201, canonical UID,
eight placeholder assignments, existing wrong-profile UID/token preservation.
Changed Python source compiled and changed Jinja templates parsed.
v1 source syntax checked; v1 endpoint not integration-tested.
Full app startup, live PostgreSQL, deployment and physical board not tested.
Synthetic test identities were used only in an isolated in-memory test database.
Copyright: (c) 2026 JP Van Wyk. All rights reserved.
