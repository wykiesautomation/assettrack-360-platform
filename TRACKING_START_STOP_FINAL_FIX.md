# AssetTrack 360 Tracking Start/Stop Final Fix

- Start Tracking opens one explicit trip identity.
- Stop Tracking closes that trip identity.
- A new Start creates a new trip.
- Stops from 180 seconds are confirmed stops.
- Long stops remain inside the same explicit trip.
- Movement after a stop continues inside the same trip.
- Impossible GPS jumps are not treated as measured travel.
