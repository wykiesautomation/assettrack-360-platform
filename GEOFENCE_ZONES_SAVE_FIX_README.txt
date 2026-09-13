AssetTrack 360 Geofence Zones Save Fix

- Geofence zones now save transactionally into asset.metadata_json.tracking_safety.zones.
- Existing tracking_safety metadata is preserved instead of overwritten unnecessarily.
- Zone names are trimmed, required and duplicate names are rejected case-insensitively.
- Latitude, longitude and radius are validated server-side.
- Maximum 20 zones; radius is constrained to 50-50000 m.
- Any database failure rolls back fully and shows a useful message.
- The selected tracker device remains selected after save.
- The form synchronises zones_json immediately before submit.
- Customer admin and platform admin role protection remains unchanged.
