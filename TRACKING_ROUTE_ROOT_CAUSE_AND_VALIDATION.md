# Tracking Route Root Cause and Validation

## Why tracking was broken

1. The original strict validator treated mobile points below 5 km/h as stationary and required three progressive fixes over at least 20 seconds. Genuine slow phone movement was therefore discarded.
2. A later route patch accepted displacement too broadly. Historical GPS fixes and long inaccuracies were promoted into route segments, creating lines to places not travelled.
3. Stationary time was calculated from the entire selected period and every drift observation was exposed as a stop. This produced impossible values such as 474 minutes and 87 stops with zero accepted route points.
4. One patch included a SQLAlchemy Location object inside route JSON. Jinja `tojson` could not serialize it, causing the Tracking History HTTP 500 error.
5. Segment end markers were orange. Excessive fragmentation produced many orange markers, although they were not actual stops.

## Current production rules

- Stored GPS observations are the only source of route evidence.
- Accuracy worse than 100 m is rejected.
- Gaps longer than 180 seconds break continuity.
- Impossible jumps break continuity and do not add distance.
- Accuracy-radius jitter does not add distance.
- Stops require a prior measured journey and at least 120 seconds stationary.
- Rejected points never add distance, movement time, or stopped time.
- The map exposes a measured GPS evidence layer and never road-snaps or predicts missing travel.

## Regression validation

Six deterministic checks cover continuous movement, stationary jitter, impossible jumps, stale gaps, poor accuracy, and confirmed stops. Run:

`pytest -q tests/test_tracking_route_regression.py`
