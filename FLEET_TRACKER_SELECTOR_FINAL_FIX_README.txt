AssetTrack 360 Fleet Tracking Selector Final Fix

- Adds a visible GPS-capable tracker selector to Safety Twin.
- Shows asset name, Device UID, state and last-contact age.
- Keeps tenant filtering through gps_tracking_devices().
- Uses /fleet-tracking?device_id=<id> to resolve the correct asset and device.
- Existing Refresh, History, Geofences and Evidence links retain the selected device.
- No database migration or firmware change required.
- Keep DATABASE_URL and Railway variables unchanged.
