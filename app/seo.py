from flask import render_template, url_for

SITE_NAME = "AssetTrack 360 by Wykies Automation"
SITE_URL = "https://assettrack360.wykiesautomation.co.za"
DEFAULT_IMAGE = SITE_URL + "/static/assettrack360-social-card.png"

SEO_PAGES = {
    "fleet-tracking-south-africa": {
        "path": "/fleet-tracking-south-africa",
        "title": "Fleet Tracking Software South Africa | AssetTrack 360",
        "description": "Track vehicles and mobile assets in South Africa with live GPS, journey history, stops, mobile phone tracking, device health and secure customer workspaces.",
        "eyebrow": "SOUTH AFRICAN FLEET TRACKING",
        "heading": "Fleet tracking built for South African operations.",
        "intro": "AssetTrack 360 combines live GPS visibility, journey history, stops, device health and secure mobile tracking in one customer workspace.",
        "primary_keyword": "fleet tracking software South Africa",
        "features": [
            ["Live vehicle visibility", "See current and last-known positions, speed, heading and GPS accuracy."],
            ["Journey intelligence", "Review distance, driving time, stops, communication gaps and route quality."],
            ["Mobile and dedicated devices", "Start with an Android phone and expand to GPS or industrial hardware later."],
            ["Local operational context", "Customer-isolated workspaces, South African support and POPIA-aligned controls."],
        ],
        "faq": [
            ["Can a phone be used as a fleet tracker?", "Yes. The Android tracker uses a visible foreground location service, secure registration and an offline queue."],
            ["Does AssetTrack 360 show route history?", "Yes. The platform provides accepted GPS routes, rejected outlier diagnostics, journeys, stops and last-known position."],
            ["Can existing GPS devices be connected?", "The platform has a universal gateway foundation for supported third-party protocols and APIs."],
        ],
    },
    "mobile-phone-tracking": {
        "path": "/mobile-phone-tracking",
        "title": "Android Mobile Phone Tracking for Fleets | AssetTrack 360",
        "description": "Use an Android phone for visible background fleet tracking with GPS, battery, charging, offline queue, consent controls and secure API telemetry.",
        "eyebrow": "ANDROID MOBILE TRACKER",
        "heading": "Turn an Android phone into a secure mobile tracker.",
        "intro": "Register a phone with a one-time code, keep tracking visible through Android, queue locations when the network is unavailable and recover automatically.",
        "primary_keyword": "Android phone fleet tracking South Africa",
        "features": [
            ["Visible background tracking", "An ongoing Android notification confirms when the tracking service is active."],
            ["Offline queue", "Locations wait safely on the phone and upload oldest-first when connectivity returns."],
            ["Device health", "Monitor phone battery, charging, GPS accuracy, app version and last API contact."],
            ["Privacy controls", "Consent, stop tracking, unregister, token revocation and deletion requests are built in."],
        ],
        "faq": [
            ["Does tracking continue with the screen locked?", "The native Android app is designed to use a visible foreground location service for screen-off tracking."],
            ["Can the user stop tracking?", "Yes. Tracking remains user-visible and can be stopped. Consent can also be withdrawn."],
            ["What happens without mobile data?", "GPS points are queued locally and uploaded automatically after network recovery."],
        ],
    },
    "vehicle-gps-tracking": {
        "path": "/vehicle-gps-tracking",
        "title": "Vehicle GPS Tracking, Routes and Stops | AssetTrack 360",
        "description": "Monitor vehicle position, speed, stops, distance, route quality, possible addresses and tracking history from one secure platform.",
        "eyebrow": "VEHICLE GPS INTELLIGENCE",
        "heading": "See where the vehicle was, how it moved and when it stopped.",
        "intro": "Operational GPS tracking with outlier protection, journey separation, accepted routes, raw diagnostics and possible-address lookup.",
        "primary_keyword": "vehicle GPS tracking South Africa",
        "features": [
            ["Accepted route", "Impossible jumps and weak GPS outliers are excluded from the operational route."],
            ["Tracking history", "Filter today, 24 hours, seven days or a custom period."],
            ["Stops and journeys", "Separate journeys after communication gaps and review confirmed stops."],
            ["Possible address", "Convert coordinates into a possible street or area while keeping accuracy visible."],
        ],
        "faq": [
            ["Why can a GPS route jump?", "Weak accuracy, cached positions or network-derived locations can create outliers. AssetTrack 360 retains diagnostics but excludes suspect points from operational routes."],
            ["Does the platform support road matching?", "Yes. Matched-route and raw-GPS views are supported when a route provider is configured."],
        ],
    },
    "asset-monitoring": {
        "path": "/asset-monitoring",
        "title": "Universal Asset Monitoring Platform | AssetTrack 360",
        "description": "Monitor mobile and fixed assets with GPS, device health, alarms, tank levels, machine condition and universal industrial signals.",
        "eyebrow": "UNIVERSAL ASSET MONITORING",
        "heading": "One operational view for moving and fixed assets.",
        "intro": "AssetTrack 360 is designed around the asset and business outcome, not a single hardware brand or protocol.",
        "primary_keyword": "asset monitoring software South Africa",
        "features": [
            ["Mobile assets", "Phones, vehicles, trailers and supported third-party GPS devices."],
            ["Fixed equipment", "Tanks, pumps, motors and remote infrastructure without mandatory GPS."],
            ["Universal signals", "4–20 mA, digital, pulse, MQTT, Modbus, OPC and external APIs."],
            ["Configurable experience", "Show only the dashboards, alarms and controls supported by each device profile."],
        ],
        "faq": [
            ["Is GPS required for every asset?", "No. Fixed sensor devices can report analogue or digital values without any tracking capability."],
            ["Can one customer monitor different asset types?", "Yes. A customer workspace can contain trackers, tanks, machines and custom signals."],
        ],
    },
    "industrial-sensor-monitoring": {
        "path": "/industrial-sensor-monitoring",
        "title": "Industrial Sensor Monitoring and Remote Signals | AssetTrack 360",
        "description": "Connect 4–20 mA, 0–10 V, digital, pulse, vibration, temperature, MQTT, Modbus and OPC data to customer-friendly dashboards.",
        "eyebrow": "INDUSTRIAL SIGNAL VISIBILITY",
        "heading": "Turn industrial signals into understandable operational information.",
        "intro": "Scale raw signals into engineering units, label every channel, choose a suitable display and apply warning, critical and stale-data alarms.",
        "primary_keyword": "industrial sensor monitoring South Africa",
        "features": [
            ["Engineering-unit scaling", "Convert 4–20 mA or voltage inputs into litres, bar, degrees, amps or custom units."],
            ["Configurable displays", "Use numeric cards, tank levels, bars, trends, status tiles, counters or runtime displays."],
            ["Signal quality", "Expose raw and engineering values to distinguish process changes from sensor faults."],
            ["Industrial connectivity", "Use managed gateways for MQTT, Modbus, OPC, SQL/ODBC and API sources."],
        ],
        "faq": [
            ["Can a fixed ESP32 work without GPS?", "Yes. A fixed sensor profile can report analogue, digital and device-health values with a manually assigned site location."],
            ["Can each input have its own label and unit?", "Yes. Channel name, unit, scaling, decimals, display type and alarm limits are configurable."],
        ],
    },
    "fleet-tracking-api": {
        "path": "/fleet-tracking-api",
        "title": "Fleet Tracking API and Device Integration | AssetTrack 360",
        "description": "Securely register phones and tracking devices, ingest GPS and telemetry, manage tokens, consent, subscriptions and customer-isolated data.",
        "eyebrow": "SECURE TRACKING API",
        "heading": "Connect devices without exposing customers to raw tokens.",
        "intro": "A customer-friendly onboarding flow issues one-time registration codes while the API creates and protects the permanent device identity behind the scenes.",
        "primary_keyword": "fleet tracking API South Africa",
        "features": [
            ["Secure onboarding", "One-time codes connect a device to the correct customer and asset."],
            ["Token lifecycle", "Issue, revoke, replace and disable device identities without losing asset history."],
            ["Telemetry validation", "Validate identity, timestamps, sequences, ranges, consent and subscription status."],
            ["Tenant isolation", "Every asset, device, location, alarm and reading remains scoped to the customer workspace."],
        ],
        "faq": [
            ["Does the customer type in the API token?", "No. The API issues the token after one-time code registration and the native app stores it securely."],
            ["Can a phone be replaced without deleting history?", "Yes. Replace Phone revokes the old identity, preserves the asset history and generates a new registration code."],
        ],
    },
    "security-privacy": {
        "path": "/security-privacy",
        "title": "Tracking Security, Consent and Privacy | AssetTrack 360",
        "description": "Learn how AssetTrack 360 uses visible tracking, explicit consent, customer isolation, revocable tokens, audit trails and deletion requests.",
        "eyebrow": "SECURITY AND PRIVACY",
        "heading": "Visible tracking, explicit consent and customer-isolated data.",
        "intro": "Security controls remain mandatory while customers can configure optional monitoring and notification features.",
        "primary_keyword": "POPIA fleet tracking privacy South Africa",
        "features": [
            ["Explicit consent", "Mobile registration requires the current location-tracking notice."],
            ["Visible operation", "Native Android tracking remains visible through an ongoing notification."],
            ["Revocable identity", "Disable, unregister, replace or revoke a device without exposing its token."],
            ["Data-subject controls", "Stop tracking, withdraw consent and submit a tracking-data deletion request."],
        ],
        "faq": [
            ["Does AssetTrack 360 secretly record audio or video?", "No. The normal mobile tracking scope excludes microphone, camera, contacts, messages, call history and personal files."],
            ["Can customers see other customer data?", "No. Normal customer queries are scoped to the authenticated customer workspace."],
        ],
    },
}

def page_for(slug):
    return SEO_PAGES.get(slug)

def render_seo_page(slug):
    page = page_for(slug)
    if not page:
        return None
    schema = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": SITE_NAME,
        "alternateName": "AssetTrack 360",
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "Web, Android",
        "url": SITE_URL + page["path"],
        "description": page["description"],
        "offers": {"@type": "Offer", "priceCurrency": "ZAR", "availability": "https://schema.org/OnlineOnly"},
        "provider": {"@type": "Organization", "name": "Wykies Automation", "url": SITE_URL},
    }
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in page.get("faq", [])
        ],
    }
    return render_template("public_landing.html", page=page, schema=schema, faq_schema=faq_schema, site_url=SITE_URL)


# AssetTrack 360 public positioning guard. Dedicated fleet/truck marketing belongs
# to the separate FleetTrack 360 platform and is deliberately excluded here.
for _assettrack_excluded_slug in (
    "fleet-tracking-south-africa",
    "vehicle-gps-tracking",
    "fleet-tracking-api",
    "fleet-tracking",
):
    SEO_PAGES.pop(_assettrack_excluded_slug, None)


# Product-specific AssetTrack 360 public pages.
SEO_PAGES.update({
 "industrial-asset-monitoring":{"path":"/industrial-asset-monitoring","title":"Industrial Asset Monitoring South Africa | AssetTrack 360","description":"Monitor industrial assets, verified signals, alarms and device health with capability-aware hardware profiles and secure customer workspaces.","eyebrow":"INDUSTRIAL ASSET MONITORING","heading":"Connect verified asset signals to clear operational evidence.","intro":"AssetTrack 360 links sites, assets, devices and supported signals while keeping measured, scaled and advisory information clearly distinguished.","primary_keyword":"industrial asset monitoring South Africa","features":[["Capability-aware monitoring","Offer only signals supported by the selected board, wiring and protocol profile."],["Engineering units","Scale supported inputs into litres, pressure, temperature, current, runtime and other operational values."],["Alarm evidence","Retain severity, state, acknowledgement and measurement context."],["Customer isolation","Keep every site, asset, device and reading tenant-scoped."]],"faq":[["Can unsupported inputs be configured?","No. Public and customer workflows should expose only verified capabilities for the selected device profile."]]},
 "tank-level-monitoring":{"path":"/tank-level-monitoring","title":"Tank Level Monitoring and Diesel Evidence | AssetTrack 360","description":"Monitor supported tank level signals with calibration, litres and percentage context, filtering, quality indicators and evidence-aware diesel alerts.","eyebrow":"TANK AND DIESEL VISIBILITY","heading":"Turn verified level signals into useful tank and diesel evidence.","intro":"Configure supported level inputs, calibration, filtering and alarm thresholds while preserving signal quality and uncertainty.","primary_keyword":"tank level monitoring South Africa","features":[["Verified sensor path","Use only supported board, interface and sensor combinations."],["Calibration context","Map raw measurements to litres, percentage or other approved engineering units."],["Signal quality","Keep raw, scaled, quality and timestamp context visible."],["Evidence-aware alerts","Treat possible loss as an event for investigation, not as proven theft."]],"faq":[["Does every board support tank monitoring?","No. Tank monitoring is available only where the board, interface, wiring and sensor profile support the signal."]]},
 "device-engineering-studio":{"path":"/device-engineering-studio","title":"Capability-Aware Device Engineering Studio | AssetTrack 360","description":"Engineer verified ESP32, SIM808/SAMD21, LILYGO and mobile tracker profiles with safe I/O assignment, revision context and firmware compatibility controls.","eyebrow":"DEVICE ENGINEERING STUDIO","heading":"Build only what the selected device can physically support.","intro":"Link registered hardware, verified profiles, assets and signals without offering reserved pins, unsafe outputs or unsupported capabilities.","primary_keyword":"device engineering platform South Africa","features":[["Verified board profiles","Record board family, revision, capabilities and restrictions."],["Safe I/O assignment","Protect reserved, boot-sensitive, input-only and unsupported points."],["Firmware context","Validate device identity and firmware-family compatibility."],["Mobile virtual points","Keep phone GPS and battery data separate from physical GPIO."]],"faq":[["Are all ESP32 boards treated as identical?","No. Different physical boards and module revisions require separate verified profiles where capabilities or pin maps differ."]]},
 "diesel-security":{"path":"/diesel-security","title":"Diesel Monitoring and Security Evidence | AssetTrack 360","description":"Correlate supported fuel telemetry with stationary state, movement context, quality and review workflows without overstating uncertain evidence.","eyebrow":"DIESEL MONITORING","heading":"Investigate possible diesel loss with measured context.","intro":"AssetTrack 360 retains accepted fuel observations, operational context and review history so possible loss remains evidence-aware.","primary_keyword":"diesel monitoring South Africa","features":[["Accepted observations","Retain litres, percentage, quality and timestamp context."],["Operational correlation","Use movement and state context to reduce nuisance events."],["Review workflow","Acknowledge, investigate and resolve without deleting history."],["Evidence exports","Produce customer-scoped fuel and event records."]],"faq":[["Does AssetTrack prove theft?","No. AssetTrack records possible loss evidence for investigation and does not independently prove theft or liability."]]},
 "opc-ua-monitoring":{"path":"/opc-ua-monitoring","title":"Read-Only OPC UA Monitoring | AssetTrack 360","description":"Bring approved OPC UA values into AssetTrack 360 through registered read-only edge gateways, explicit mappings, source timestamps and quality context.","eyebrow":"READ-ONLY OPC UA","heading":"Monitor approved OPC UA data without creating a PLC write path.","intro":"Use registered gateways and explicit mappings to bring approved industrial values into customer-isolated AssetTrack workspaces.","primary_keyword":"OPC UA monitoring gateway South Africa","features":[["Read-only controls","Disable writes, methods and alarm acknowledgement through the monitoring path."],["Explicit mappings","Map approved nodes to customer assets and signals."],["Gateway identity","Use rotatable tokens, heartbeats and audit evidence."],["Quality context","Preserve source timestamps and quality with mapped readings."]],"faq":[["Can AssetTrack write directly to a PLC?","The AssetTrack public monitoring position is read-only. Direct PLC writes are not part of this gateway workflow."]]},
 "modbus-monitoring":{"path":"/modbus-monitoring","title":"Modbus TCP and RTU Monitoring | AssetTrack 360","description":"Configure approved Modbus TCP and RTU monitoring with explicit register addresses, data types, byte order, word order, scaling and diagnostics.","eyebrow":"MODBUS MONITORING","heading":"Decode approved Modbus data with visible engineering context.","intro":"Build controlled mappings while preserving register, type, byte order, word order, scaling, quality and commissioning evidence.","primary_keyword":"Modbus monitoring software South Africa","features":[["TCP and RTU context","Keep transport and device settings explicit."],["Register decoding","Record address, type, byte order, word order, scale and offset."],["Read-only operation","Use monitoring-safe requests and controlled polling."],["Diagnostics","Retain last success, quality and mapping errors."]],"faq":[["Can unknown registers be trusted automatically?","No. Final register meaning requires verified device documentation or commissioning evidence."]]},
 "about":{"path":"/about","title":"About AssetTrack 360 | Wykies Automation","description":"AssetTrack 360 is a South African industrial asset monitoring, tank monitoring, device engineering and secure edge integration platform by Wykies Automation.","eyebrow":"ABOUT ASSETTRACK 360","heading":"A practical platform for connected assets and operational evidence.","intro":"AssetTrack 360 combines supported devices, industrial signals, tank monitoring and secure integrations in customer-isolated workspaces.","primary_keyword":"AssetTrack 360 Wykies Automation","features":[["Operational truth","Measured, validated, derived and advisory information remain distinct."],["Capability awareness","Workflows respect real board, wiring and protocol limitations."],["Customer isolation","Assets, devices and data remain tenant-scoped."],["Controlled expansion","Pilots expand only after commissioning and acceptance evidence."]],"faq":[]},
 "contact":{"path":"/contact","title":"Contact AssetTrack 360 | Wykies Automation","description":"Contact Wykies Automation about an AssetTrack 360 industrial asset, tank, device engineering or integration pilot.","eyebrow":"CONTACT AND PILOT ENQUIRY","heading":"Plan a controlled AssetTrack 360 pilot.","intro":"Confirm the asset, hardware, signals, connectivity and acceptance evidence before committing to a deployment.","primary_keyword":"AssetTrack 360 contact","features":[["Pilot scope","Select the first machine, tank, equipment item or signal group."],["Hardware fit","Confirm device, power, wiring and communications constraints."],["Data path","Confirm Wi-Fi, cellular, MQTT, OPC UA, Modbus, REST or edge requirements."],["Acceptance criteria","Define evidence required before expansion."]],"faq":[]}
})
