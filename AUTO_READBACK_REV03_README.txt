AUTO READBACK REPAIR REV03 / BOARD BUILDER REV14
Deploy backend REV03 to existing service, without clearing repository/database.
Run Board Builder REV14, connect T-Call, open T-CALL I/O & GSM tab.
Click READ BOARD & OPEN PROFILE REPAIR. Fresh READ_IDENTITY is requested;
Hardware UID, profile and firmware must all arrive on the same serial connection.
Browser opens your configured HTTPS server with UID/firmware prefilled read-only.
No passwords/tokens/claim codes are put in the browser URL. Identity is not secret
and may appear in browser history/server logs. URL readback is convenience, NOT
cryptographic hardware attestation. Server requires platform_admin login, CSRF,
matching existing physical identity and explicit SIM800L confirmation.
Admin login may redirect away from query parameters: log in first, then click
READ BOARD & OPEN PROFILE REPAIR again. No manual UID/firmware entry needed.
Server selects matching existing device; no/duplicate match blocks prefill.
Confirm device and type SIM800L. UID/token/history retained. Do not re-claim.
No firmware changes required. No automatic production database change/deployment.
Python syntax checked. GUI/physical serial/browser/live service not tested.
