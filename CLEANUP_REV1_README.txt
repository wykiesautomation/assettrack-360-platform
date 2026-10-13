AssetTrack REV1 - Cleanup safety repair
Based on the complete user-uploaded assettracktest.zip.txt project.
Only app/__init__.py and app/trend_cleanup.py changed.
Destructive retention cleanup disabled, including force=True callers.
Cleanup removed from startup and HTTP request hooks.
No database migrations, credentials, DNS or subscription rules changed.
Does not recover previously deleted rows or resolve all mobile upload issues.
Upload the extracted project contents to the existing GitHub main branch.
Do not upload the ZIP itself as an application file; keep app/ and Dockerfile
at the repository root, not inside an extra nested folder.
Deploy the latest commit on Railway; verify the source commit matches GitHub.
Expected log: Retention cleanup disabled: history preservation repair REV1
Python syntax and cleanup no-op behavior checked. Live integration not tested.
