AssetTrack 360 Geofence Zones Save Fix V2

Root cause:
The form had two separate actions. Use Last Position only added a zone to the browser-side list, while Save only stored zones already present in that list. Pressing Save with the draft fields visible but no listed zone submitted an empty array, so the page correctly returned with no stored zones but the workflow looked broken.

Correction:
- The button now says Add Zone at Last Position.
- Blank names automatically become Zone 1, Zone 2, etc.
- Pressing Save automatically adds a pending draft before submitting.
- If JavaScript fails, server-side draft fields safely create the zone from the last accepted GPS position.
- Existing zones remain preserved and duplicates are blocked.
- Save remains transactional and retains the selected tracker.
