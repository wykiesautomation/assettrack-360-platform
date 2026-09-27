AssetTrack 360 Final Device and Orphan Asset Delete Fix

Workflow:
1. Disable Device.
2. Delete Device Permanently.

Result:
- Device identity and token removed.
- Device assignments, commands and dependent rows removed.
- Linked asset, telemetry, GPS history, alarms, signals and configuration removed only when no other device uses that asset.
- Shared assets remain protected.
- Parent site always remains.
- Other devices and assets at the site remain.
- Any failure rolls back the complete transaction.
