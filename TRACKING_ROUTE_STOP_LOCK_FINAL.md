# Tracking Route and Stop Lock Final

- Keeps current Possible address and reverse-geocoding code unchanged.
- Breaks map lines at gaps over 180 seconds, trip identity changes and impossible jumps.
- Requires neighbouring movement evidence or a decisive speed-supported displacement.
- Uses a larger combined GPS-accuracy envelope near stops.
- Locks the final stop to the best-accuracy point in a compact stationary cluster.
- Rejected points never add distance and are never bridged by a cyan polyline.
