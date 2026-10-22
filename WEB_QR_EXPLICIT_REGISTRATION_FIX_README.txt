AssetTrack 360 Web QR Explicit Registration Fix

Correct flow restored:
1. Scan the QR with the normal phone camera.
2. The mobile tracker page opens with the one-time code prefilled.
3. Registration does NOT happen automatically.
4. The user must review and tick consent.
5. The user must press Register Phone.
6. After successful registration, the registered tracker controls appear.
7. The user may then press Start Tracking.

A newly scanned QR now overrides any old tracker identity in the browser UI for onboarding purposes, without silently registering or reusing the stale identity. Existing local state is not sent or activated until the user explicitly completes registration.
