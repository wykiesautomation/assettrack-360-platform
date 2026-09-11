AssetTrack 360 Device Delete Ghost Asset Fix

After a disabled device is permanently deleted:
- the device identity and API token are removed;
- all device-owned operational rows are removed;
- if no other device uses the linked asset, the linked asset and its history/configuration are removed so it disappears from Monitored Assets, Asset detail, Fleet Tracking, Asset & Device Setup, search and selectors;
- if another device still uses the asset, the shared asset is retained;
- the parent site is always retained;
- other assets and devices at the same site are untouched.

Confirmation requires the exact Device UID and DELETE.
