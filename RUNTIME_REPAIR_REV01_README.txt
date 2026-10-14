ASSETTRACK 360 - RUNTIME REPAIR REV01
Build: 2026-10-14

Hierdie is die volledige source-baseline met geteikende herstelwerk.
Geen PlantLink/Studio/UDT-werk is ingesluit nie.

ONTplooi
1. Maak eers 'n backup van jou huidige repository en databasis.
2. Pak hierdie ZIP uit. Kopieer die inhoud van assettrack-360-platform-main
   na die bestaande AssetTrack repository, nie as 'n ekstra subfolder nie.
3. Commit en push; redeploy die bestaande hosting service.
4. Hou DATABASE_URL, SECRET_KEY, domein en alle bestaande secrets onveranderd.
5. Indien die host 'n custom Start Command gebruik, stel dit op:
   gunicorn -w 1 --threads 4 -b 0.0.0.0:$PORT app:app
   Dockerfile en render.yaml is reeds aangepas.
6. PostgreSQL reading.sequence word by startup van 80 na 160 verbreed indien
   nodig. Die database user moet ALTER-regte he. Geen tabel/data word deur
   hierdie schema-verandering uitgevee nie. Bestaande retention bly aktief.
7. Hard refresh die laptop. Heropen die bestaande trackerblad op die foon.
   Moenie die device uitvee of nuwe claim/registration skep as eerste stap nie.

HERSTEL
- Dashboard gebruik tenant-filtered, request-local batched data eerder as
  herhaalde per-asset/per-signal queries.
- Dashboard, asset detail en history page rendering gebruik cached addresses
  sonder om vir die eksterne adresdiens te wag. Bestaande address API bly werk.
- Static CSS/JS requests laai nie meer die authenticated user uit SQL nie.
- Retention-cleanup loop in 'n aparte background application context, nie
  sinchronies in login/dashboard/telemetry requests nie. PostgreSQL advisory
  lock bly op een toegewyde connection tot die cleanup klaar is.
- Ontbrekende mobile GPS retention-policy beteken nie meer 'delete history'
  nie: mobile default bly 31 dae. Reeds verwyderde history kan nie herstel word nie.
- Mobile auto-profile lees signals en assignments in twee queries.
- Mobile batch sequences van 80 karakters plus point suffix pas nou in SQL.
- Mobile status gebruik dieselfde connectivity-policy as dashboard.
- Healthy Assets tel ONLINE assets korrek; last contact kom van die device.
- Assetblad refresh elke 15 sekondes, nie elke sekonde nie. Geen onmiddellike
  dubbele page-load nie. Tracker Summary en Device Health word ook vervang.
- Refresh badge lees die nuwe response se connectivity, nie ou Jinja state nie.
- Browser storage JSON is fail-safe; fallbackCanvas is voor gebruik verklaar.
- Mobile fetch het 'n 15-second timeout; asset refresh 'n 12-second timeout.
- Server-Timing header en slow-request logs help met live diagnose.
- Vaste, vervaardigde telemetry bars is deur werklike recorded events vervang.

TOETS NA DEPLOY
- Login en dashboard: kyk dashboard request se Time en Server-Timing.
- Start Tracking op die bestaande foon; kyk Activity Log vir Heartbeat accepted.
- Kontroleer nuwe last_contact en last_position, nie net die ONLINE kleur nie.
- Maak asset detail oop; Tracker Summary moet na volgende refresh bywerk.
- Ou/offline devices moet steeds Offline bly. Geen vals ONLINE status nie.
- Indien 401/403/402: ondersoek token/consent/subscription; moenie data namaak nie.
- Indien nuwe data steeds nie inkom nie: stuur die presiese phone Activity Log
  en hosting log. Hierdie pack kan nie 'n verkeerde live DATABASE_URL, ou
  browser identity of verkeerde deployment-branch op afstand regstel nie.

MAINTENANCE
TREND_CLEANUP_BACKGROUND=false kan tydelik gebruik word om background retention
vir diagnose te stop. Dan moet 'n aparte retention worker/schedule onderhou word.
Die bestaande retention-regels bly geld; maak backups voor deployment.

VALIDASIE EN BEPERKINGS
22 runtime checks PASS met sintetiese, plaaslike SQLite fixtures.
Malformed localStorage runtime check PASS; mobile JS en rendered inline scripts
syntax PASS; Python compile PASS.
GPS regression suite: 12 PASS, 1 FAIL. Dieselfde FAIL is bevestig op die
onveranderde oorspronklike baseline: test_continuous_measured_route (distance 0).
GPS-validator en route-calculation code is nie verander nie. Hierdie bestaande
low-speed distance mismatch bly oop; moenie hierdie pack as 100% GPS-certified
beskou nie. Volledige logs is in docs/.
Geen live PostgreSQL, hosting deployment of fisiese phone upload is hier getoets
nie. Die 25-second live wagtyd moet na deployment weer gemeet word.

Copyright: (c) 2026 JP Van Wyk. All rights reserved.
