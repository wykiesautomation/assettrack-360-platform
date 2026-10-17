# AssetTrack 360 Trips Command Centre Production Conversion

- New authenticated `/asset/<asset_id>/trips` workflow using real PostgreSQL Location rows.
- One authoritative trip dataset drives map, distance, duration, maximum speed, speed profile and overspeed episodes.
- Trips split on gaps over 180 seconds, poor accuracy, impossible speed/jumps and stationary uncertainty.
- Trips under 0.3 km or 60 seconds are excluded from customer totals.
- Maximum speed requires adjacent reported-speed support; isolated spikes are rejected.
- Satellite map defaults on, street map remains selectable.
- Selected-trip map, start/end markers, direction markers, optional GPS evidence, date range, trip cards and speed profile included.
- Existing Tracking History has an Open Trips Command Centre button.
- No schema migration, mobile re-registration, firmware change or Railway variable change required.
