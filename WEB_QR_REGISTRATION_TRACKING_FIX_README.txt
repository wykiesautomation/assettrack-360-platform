AssetTrack 360 Web QR Registration and Tracking Fix

Root cause:
Phone camera QR links can open in a restricted in-app browser. The server registration succeeded, but localStorage could throw an exception. The page then looked unregistered even though the device record already existed, and Start Tracking was unavailable.

Fix:
- Safe storage fallback order: localStorage, sessionStorage, then in-page memory.
- A successful server registration always shows the registered tracker controls.
- Tracking starts automatically after successful consent and registration.
- The device token is no longer erased on a transient 401/403 response.
- The activity log tells the user to open the page in Chrome when camera-browser storage is restricted.
- Existing web GPS watch, heartbeat, offline queue and location upload remain intact.
