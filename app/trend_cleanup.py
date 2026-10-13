"""History-preservation repair. Destructive retention is disabled.

Compatibility entry point retained for callers. No SQL queries, commits,
deletes or advisory locks are performed, including when force=True.
This does not restore previously deleted data.
"""
JOB_NAME = "trend-retention-daily-v1"

def cleanup_due(force=False):
    return {
        "ran": False,
        "readings": 0,
        "locations": 0,
        "reason": "history_preservation_cleanup_disabled_REV1",
    }
