AssetTrack 360 Tracking Route Repair

Corrected root causes:
- Removed the fixed 250 metre rejection that discarded normal highway travel.
- Increased short mobile reporting-gap continuity from 3 to 15 minutes.
- Stops remain recorded after 2 minutes but close a journey only after 20 minutes.
- Final journey distance no longer discards valid sparse highway observations.
- Impossible jumps are rejected by implied speed above 180 km/h.

No database migration or new phone registration is required.
Historical results will be recalculated from existing stored GPS points after deployment.
No road snapping or invented route is used.

Browser limitation:
Android can pause browser GPS when the screen is locked. Keep the tracker page visible during web tracking. Guaranteed screen-off collection requires a native Android foreground location service.

Copyright: © 2026 JP Van Wyk. All rights reserved.

Explicit tracking control:
- Pressing Start Tracking creates a unique trip identifier.
- Pressing Stop Tracking closes that trip identifier immediately.
- Pressing Start Tracking again creates a new trip even if the stop was shorter than 20 minutes.
- Browser reload restores only an already-active trip. It does not create a false new trip.
