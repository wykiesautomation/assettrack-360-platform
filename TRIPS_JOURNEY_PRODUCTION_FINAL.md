# AssetTrack 360 Trips and Journey Production Final

- Authoritative trip reconstruction from chronological route-grade GPS points.
- Separate trips on new day, gaps over 180 seconds, impossible jumps, or at least 120 seconds stationary.
- Minimum trip: three points, 100 m and 20 seconds movement evidence.
- Selected-trip satellite map with street-layer option, start/end markers and direction arrows.
- Detailed and list views, daily summary, trip duration, distance, point count, route quality and maximum speed.
- Trip maximum rejects isolated speed spikes unless neighbouring samples confirm at least 80 percent.
- Existing mobile API, tokens, PostgreSQL data, Safety Twin, geofences and Railway settings are preserved.
