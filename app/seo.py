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

# Public search-visibility expansion. Existing routes and customer workflows remain unchanged.
SEO_PAGES.update({
    "fleet-tracking": {
        "path": "/fleet-tracking",
        "title": "Fleet Tracking Platform South Africa | AssetTrack 360",
        "description": "Fleet tracking for South African operations with accepted GPS positions, journey history, stops, tracker health, safety evidence and customer-isolated workspaces.",
        "eyebrow": "FLEET VISIBILITY AND EVIDENCE",
        "heading": "Fleet tracking that keeps accepted evidence separate from assumptions.",
        "intro": "Monitor vehicles, trackers and mobile GPS sources with clear position quality, communication state, route history and operational context.",
        "primary_keyword": "fleet tracking platform South Africa",
        "features": [["Live fleet context","Review accepted current and last-known positions with speed, accuracy and tracker state."],["Journey and stop evidence","Inspect routes, stops, communication gaps and sustained speed evidence without fabricating missing travel."],["Capability-aware trackers","Connect supported mobile, SIM808/SAMD21, ESP32 and cellular tracker profiles according to verified capabilities."],["Operational reporting","Export route, stop, safety and device-health evidence from customer-isolated workspaces."]],
        "faq": [["Does the platform invent routes when GPS data is missing?","No. Telemetry gaps remain visible and are not presented as factual travel."],["Can a mobile phone be used for an initial pilot?","Yes. A registered mobile tracker can provide consent-based GPS and device-health data without implying physical GPIO capability."]],
    },
    "industrial-asset-monitoring": {
        "path": "/industrial-asset-monitoring",
        "title": "Industrial Asset Monitoring South Africa | AssetTrack 360",
        "description": "Monitor industrial assets, signals, alarms and device health through secure customer workspaces, engineering-unit scaling and read-only integration gateways.",
        "eyebrow": "INDUSTRIAL ASSET MONITORING",
        "heading": "Bring asset condition, signals and alarms into one operational workspace.",
        "intro": "AssetTrack 360 links sites, assets, devices and verified signals while keeping raw, scaled, measured and advisory values clearly distinguished.",
        "primary_keyword": "industrial asset monitoring South Africa",
        "features": [["Universal signal registry","Configure permitted analogue, digital, pulse, health and virtual points against verified device profiles."],["Engineering-unit scaling","Translate supported raw signals into litres, pressure, temperature, current, runtime or other operational units."],["Alarm evidence","Retain alarm state, severity, acknowledgement and relevant measurement context."],["Read-only integration","Connect approved OPC UA, Modbus, MQTT, REST and SQL/ODBC sources through controlled gateways."]],
        "faq": [["Can unsupported device inputs be configured?","No. The engineering workflow should expose only points supported by the selected board, wiring, voltage and protocol profile."],["Can PLC data be monitored without direct PLC writes?","Yes. Read-only gateway patterns can be used for approved industrial integration paths."]],
    },
    "tank-level-monitoring": {
        "path": "/tank-level-monitoring",
        "title": "Tank Level Monitoring and Diesel Security | AssetTrack 360",
        "description": "Tank level monitoring with calibrated signals, litres and percentage context, trend evidence, quality indicators and possible diesel-loss correlation.",
        "eyebrow": "TANK AND DIESEL VISIBILITY",
        "heading": "Turn verified level signals into useful tank and diesel evidence.",
        "intro": "Configure supported level inputs, calibration, filtering and alarm thresholds while preserving signal quality and uncertainty.",
        "primary_keyword": "tank level monitoring South Africa",
        "features": [["Calibration workflows","Map supported raw measurements to engineering units with documented calibration settings."],["Litres and percentage","Present tank level in the units appropriate to the configured asset and sensor."],["Signal quality","Keep raw value, quality, scaling and latest accepted reading visible for fault finding."],["Diesel security context","Correlate verified stationary drops and operational evidence before raising possible-loss events."]],
        "faq": [["Does every board support direct tank sensing?","No. Tank monitoring is offered only when the selected board, interface, wiring and sensor profile support the required signal."],["Is every level drop treated as theft?","No. A possible-loss event requires supporting evidence and must not be presented as proven theft."]],
    },
    "device-engineering-studio": {
        "path": "/device-engineering-studio",
        "title": "Device Engineering Studio | AssetTrack 360",
        "description": "Capability-aware device engineering for verified ESP32, SIM808/SAMD21, LILYGO and mobile tracker profiles with safe I/O assignment and firmware context.",
        "eyebrow": "CAPABILITY-AWARE DEVICE ENGINEERING",
        "heading": "Engineer only the signals and I/O that the selected device can support.",
        "intro": "The Device Engineering Studio links registered hardware, verified profiles, assets and signals without offering unsupported pins or implied capabilities.",
        "primary_keyword": "IoT device engineering platform",
        "features": [["Verified board profiles","Resolve device family, revision, capabilities, reserved pins and safe operating constraints."],["Safe I/O assignment","Prevent reserved, boot-sensitive, input-only and unsupported points from being offered as buildable outputs."],["Firmware context","Record device identity, firmware family and compatibility context for commissioning."],["Mobile virtual points","Keep phone-generated GPS and battery data separate from physical GPIO and analogue scaling."]],
        "faq": [["Are all ESP32 boards treated as identical?","No. Physical board and module revisions require separate verified profiles where pin maps or onboard functions differ."],["Can simulation energise physical outputs?","No. Simulation must remain physically locked out from real outputs."]],
    },
    "diesel-security": {
        "path": "/diesel-security",
        "title": "Diesel Security Monitoring | AssetTrack 360",
        "description": "Evidence-aware diesel monitoring combining calibrated fuel observations, vehicle state, movement context, event workflows and customer review.",
        "eyebrow": "DIESEL SECURITY",
        "heading": "Detect possible diesel risk without overstating uncertain evidence.",
        "intro": "AssetTrack 360 correlates supported fuel telemetry with operational context and keeps possible loss, acknowledgement and resolution evidence visible.",
        "primary_keyword": "diesel security monitoring South Africa",
        "features": [["Verified fuel observations","Store accepted litres, percentage, quality and timestamp context."],["Context-aware correlation","Use movement and operating state to reduce nuisance loss events."],["Review workflow","Acknowledge, investigate and resolve security events without deleting historical evidence."],["Evidence exports","Produce customer-scoped fuel and security records for operational review."]],
        "faq": [["Does the platform make a legal theft determination?","No. It records possible loss evidence for investigation and does not independently prove theft or liability."]],
    },
    "opc-ua-monitoring": {
        "path": "/opc-ua-monitoring",
        "title": "Read-Only OPC UA Monitoring Gateway | AssetTrack 360",
        "description": "Connect approved OPC UA sources through a secure read-only edge gateway with node mapping, engineering context and customer-isolated telemetry.",
        "eyebrow": "READ-ONLY OPC UA GATEWAY",
        "heading": "Monitor approved OPC UA data without turning the platform into a PLC write path.",
        "intro": "Use a registered edge gateway, explicit mappings and read-only controls to bring approved industrial values into AssetTrack 360.",
        "primary_keyword": "OPC UA monitoring gateway",
        "features": [["Read-only contract","Disable writes, method calls and alarm acknowledgement through the monitoring gateway."],["Explicit point mapping","Map approved source nodes to customer assets and signals."],["Gateway identity","Use rotatable tokens, heartbeats and edge audit evidence."],["Quality and timestamps","Preserve source timestamps and quality context with mapped readings."]],
        "faq": [["Can AssetTrack write directly to a PLC?","The public monitoring position is read-only. Direct PLC writes are not part of this gateway workflow."]],
    },
    "modbus-monitoring": {
        "path": "/modbus-monitoring",
        "title": "Modbus TCP and RTU Monitoring | AssetTrack 360",
        "description": "Capability-aware Modbus TCP and RTU monitoring with explicit register mapping, byte and word order, scaling, quality and read-only operating controls.",
        "eyebrow": "MODBUS MONITORING",
        "heading": "Decode approved Modbus data with visible register and scaling context.",
        "intro": "Build controlled TCP or RTU mappings for supported devices while preserving source path, data type, byte order, word order and engineering conversion.",
        "primary_keyword": "Modbus monitoring software South Africa",
        "features": [["TCP and RTU profiles","Separate transport and device-profile settings for supported installations."],["Register decoding","Make address, type, byte order, word order, scale and offset explicit."],["Read-only operation","Use monitoring-safe requests and controlled polling intervals."],["Evidence and diagnostics","Retain last success, quality and mapping errors for commissioning."]],
        "faq": [["Can unknown Modbus devices be decoded automatically?","Discovery can assist, but final register meaning and safe configuration require a verified device document or commissioning evidence."]],
    },
    "about": {
        "path": "/about",
        "title": "About AssetTrack 360 and Wykies Automation",
        "description": "Learn about AssetTrack 360, a South African fleet tracking, industrial asset monitoring and device engineering platform by Wykies Automation.",
        "eyebrow": "ABOUT THE PLATFORM",
        "heading": "A practical South African platform for connected assets and operational evidence.",
        "intro": "AssetTrack 360 is developed by Wykies Automation to combine tracking, industrial asset monitoring, device engineering and evidence-aware operations in one secure platform.",
        "primary_keyword": "AssetTrack 360 Wykies Automation",
        "features": [["Operational truth","Measured, validated, derived and advisory information remain clearly distinguished."],["Capability awareness","Hardware and software workflows should reflect real board, wiring and protocol limits."],["Customer isolation","Customer data, devices, assets and permissions remain tenant-scoped."],["Phased deployment","Pilots can start small and expand after commissioning evidence and production gates pass."]],
        "faq": [],
    },
    "contact": {
        "path": "/contact",
        "title": "Contact AssetTrack 360 | Wykies Automation",
        "description": "Contact Wykies Automation about an AssetTrack 360 pilot, fleet tracking, tank monitoring, industrial asset monitoring or device integration assessment.",
        "eyebrow": "CONTACT AND PILOT ENQUIRY",
        "heading": "Plan a controlled AssetTrack 360 pilot.",
        "intro": "Discuss the asset, tracker, signal, integration and evidence requirements before hardware or subscriptions are committed.",
        "primary_keyword": "AssetTrack 360 contact",
        "features": [["Pilot scope","Identify the first vehicle, tank, machine or signal group to monitor."],["Hardware fit","Confirm device profile, power, wiring, communications and installation constraints."],["Data path","Confirm mobile, cellular, Wi-Fi, MQTT, OPC UA, Modbus, REST or edge requirements."],["Acceptance criteria","Define the evidence required before expanding the deployment."]],
        "faq": [["How do I contact AssetTrack 360?","Use the Contact Sales email link on this page or create a controlled customer workspace when registration is available."]],
    },
})
