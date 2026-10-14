AssetTrack 360 FULL Mobile Request Logging REV03
Based on the deployed SiteResponse-REV02 full source. Site performance settings
and authentication rules are preserved. No database schema changes, token resets,
registration changes, GPS algorithm changes or dashboard query changes.
This is diagnostic instrumentation, not a fix for the unknown 401 cause.

DEPLOY
Put this ZIP beside Upload_AssetTrack_FULL_REV05.ps1 and run that uploader.
Target: wykiesautomation/assettrack-360-platform main.
Full source overlay, no clearing repository or force-push.
Keep Amsterdam, DATABASE_URL, secrets and current start command unchanged.
Wait for the new deployment to be Active.

READ LOGS
Railway > current Active deployment > Deploy Logs > filter MOBILE_REQUEST.
Every mobile response is logged, including fast 202 and 401 responses.
Reasons include authorization_missing, token_empty, authorization_format_invalid,
token_not_found_in_current_database, device_inactive, device_type_not_mobile,
consent_inactive, subscription_inactive, device_identity_mismatch and accepted.
Unknown response errors are not printed verbatim. Authentication diagnosis adds
one read-only lookup only on 401 responses. It does not accept rejected requests.
Authenticated numeric device/asset IDs are included where available.
An unknown token cannot be attributed to device 75 from these logs alone.
If no mobile requests arrive, no mobile log appears. The phone may require
inspection later; this build does not remotely wake or reconnect it.

PRIVACY
No raw token, token fingerprint, Authorization header, cookie, request body,
query string, GPS coordinates, IP address or arbitrary exception text is logged
by this module. Endpoint names are server-defined. Logs include status, reason,
request ID, elapsed time and authenticated numeric IDs.
Existing unrelated application logs are unchanged.
MOBILE_REQUEST_LOGGING=false disables this diagnostic logging after investigation.
Logs use WARNING level so successful requests appear in current deployment logs;
a WARNING MOBILE_REQUEST line is not itself an application failure.

VALIDATION
10 synthetic local SQLite logging checks PASS, including secret non-disclosure,
accepted status, missing/invalid token cases, inactive device, motion rejection,
non-mobile exclusion and disable switch. Existing site-response regression PASS.
Python syntax PASS; full ZIP manifest/integrity verified.
No live phone, production PostgreSQL or Windows PowerShell execution tested here.
