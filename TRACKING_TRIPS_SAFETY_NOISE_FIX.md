# AssetTrack 360 Trips, Map and Safety Noise Fix

- Satellite map is default; street map remains selectable.
- Speed monitoring defaults to and is capped at 60 km/h.
- One overspeed event per continuous episode.
- Harsh events require stronger GPS evidence and use a five-minute cooldown.
- Abnormal tilt requires ten seconds sustained evidence, 90 percent confidence and a fifteen-minute cooldown.
- Customer history shows RECORDED and CONFIRMED events only.
- Visible events are grouped into ten-minute episodes.
- Existing APIs, PostgreSQL data, identity, GPS ingestion, route metrics and geofences are preserved.
