# AssetTrack 360 Measured Route Finalisation

- Mobile batch receipt remains authoritative for ONLINE and last_seen.
- Historical map uses stored GPS observations only. No road snapping or predicted path.
- Consecutive route-grade fixes connect only when time, displacement and implied speed are plausible.
- Gaps over 180 seconds and impossible jumps always break route continuity.
- Accuracy-radius jitter does not add distance or create a route.
- Stops require a prior measured journey and at least 120 seconds stationary.
- Rejected observations never add distance, movement time or stop time.
- Map includes a switchable measured-GPS evidence point layer.
- Segment start/end markers appear only when more than one continuous segment exists.
- Journey history keys and point counts are aligned with backend output.
