AssetTrack 360 SIM808 GPS Stationary Web Fix

Fixes:
- Speed below 5 km/h is stored and displayed as 0 km/h.
- Low-speed GPS drift cannot create MOVING state, route distance or movement minutes.
- Movement displacement must exceed the combined GPS uncertainty envelope.
- Live Safety Twin cards use only the current 30-minute session.
- Three latest stationary observations close/reset current movement metrics.
- Very poor GPS accuracy above 100 m is rejected at ingest.

Deployment:
Replace the repository with this cumulative pack, or replace only app/routes.py.
Keep DATABASE_URL and all Railway variables unchanged.
No new claim is required.
After deploy, run USB RELAY NOW three times about 20-30 seconds apart while the board remains stationary.
Expected: STATIONARY, 0 km/h, 0.00 km, 0 min.
