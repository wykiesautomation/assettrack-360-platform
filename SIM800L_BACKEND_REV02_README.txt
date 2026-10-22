SIM800L BACKEND REV02 - explicit profile repair, cumulative REV01 baseline
No automatic production database changes performed here. Not deployed.

DEPLOY: back up repository and production database. Overlay source and normally
commit/push to the repository actually used by the live AssetTrack service.
Do not clear GitHub, force push, delete devices or change DATABASE_URL/secrets.
After hosting deployment is ACTIVE, log in as platform_admin.
Platform Admin > Devices > SIM800L Profile Repair.
Route: /platform-admin/sim800l-profile-repair
Response header X-AT360-Profile-Repair-Build: SIM800L-REV02 verifies new code is live.

EXISTING DEVICE (use this for the registered board in your screenshot)
Select the existing Device UID, including its stored double prefix.
Physical HARDWARE_UID: AT360-LILYGO-DC396DAE114C
Firmware: exact current READ_ALL value, e.g. AT360_LILYGO_TCALL_IO_REV17.
Type SIM800L to explicitly confirm physical board verification and submit.
Repair changes device_type/capabilities/profile and creates missing disabled
SIM800L placeholders. UID/token/asset/history are preserved. Existing assignment
rows remain; enabled incompatible assignments block repair for manual review.
No duplicate identity allowed. UID is deliberately NOT renamed in this repair.
Do NOT claim again. Use existing installed UID/token and test SEND_NOW.
If credentials differ from the server, this pack does not reconcile/rotate them.

UNUSED CODE: optional separate owner action, unregistered boards only.
Only unexpired WAITING SIM7000G codes may be corrected after exact customer match.
Expired codes are NOT extended. The old screenshot code may now be expired;
for a genuinely unregistered board generate a fresh SIM800L code instead.
Repairing a code does not register a device or change an existing device.
Strict claim mismatch checks remain. No bypass based on submitted firmware alone.

DIAGNOSIS LIMIT: source already has SIM800L public profile and correct profile
storage. We cannot establish why your live code was originally generated for
SIM7000G or whether this uploaded ZIP matches the running deployment/database.
The new page provides the missing explicit repair workflow, not a proven
correction of an unidentified live deployment or original selection error.

TESTS: isolated synthetic Flask/SQLite tests for owner/CSRF guards, wrong-board
rejection, profile repair, UID/token preservation, 8 disabled placeholders,
unused code correction, no device creation and strict mismatch retained.
Audit logging was stubbed in isolated tests; full startup/audit/PostgreSQL/live
hardware not integration-tested. Python syntax and Jinja parsing passed.
Existing firmware/GSM TLS issues are outside this backend change.
