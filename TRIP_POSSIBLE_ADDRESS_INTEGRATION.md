# AssetTrack 360 Trip Possible Address Integration

- Trip cards show shortened From and To possible addresses.
- Detailed View shows full possible start and end addresses.
- Exact six-decimal GPS coordinates remain visible as authoritative evidence.
- Reverse geocoding is lazy, fail-safe and uses the existing authenticated internal endpoint.
- Browser results are cached for 30 days; the server provider cache remains active.
- Address-provider failure displays `Possible address unavailable` and never breaks Trips.
- Addresses do not alter distance, route, stop, speed or Start/Stop calculations.
- Stationary trips may correctly display the same start and end address.
