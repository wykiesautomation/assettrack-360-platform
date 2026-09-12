AssetTrack 360 Mobile API Stability Fix

Root cause corrected:
- The before-request mobile rate limiter performed a database row lock and commit for every heartbeat, GPS batch and Motion Safety upload.
- Motion Safety sample storage performed one duplicate query for every sample.
- These operations competed with telemetry commits and could stall the single Gunicorn worker.

Fixes:
- Mobile rate limiting is now bounded in process memory and performs no database write.
- Motion Safety is limited to 12 batches per minute per device.
- GPS remains at 120 batches per minute and other mobile endpoints at 90.
- Motion duplicate detection is one query per batch.
- Motion batches accept 1 to 100 samples, return accepted/duplicate/rejected sequences and update device heartbeat.
- Database failures rollback and return retryable HTTP 503 instead of hanging.
- Existing registration, heartbeat, GPS queue, tracking start/stop, consent and Android asset-name fixes are retained.
