# AssetTrack 360 Tracking KPI and Route Alignment Fix

## Root cause
The blue map route used `display_segments`, but distance, movement time, journey rows and maximum speed still used the older strict analytical segments. This caused a visually long route to report only 0.62 km, 3 minutes and 46 km/h.

## Correction
- Distance, movement time, trip maximum speed, journey distance and journey duration now use the exact same `display_segments` drawn on the map.
- Distance uses the Haversine formula between consecutive measured points.
- Movement time sums the same valid point intervals.
- Trip maximum uses the highest plausible value from reported GPS speed or time/distance-derived speed.
- Current speed remains the latest reported GPS speed and is not confused with trip maximum.
- Gaps over 10 minutes, jumps over 5 km and implied speeds over 180 km/h remain excluded.
- Accuracy-radius jitter remains excluded from distance and movement time.
- No API, database, device registration, ONLINE logic or map rendering behavior was changed.
