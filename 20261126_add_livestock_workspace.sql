CREATE TABLE IF NOT EXISTS livestock_farm (
 id SERIAL PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customer(id), name VARCHAR(120) NOT NULL,
 centre_lat DOUBLE PRECISION, centre_lon DOUBLE PRECISION, zoom INTEGER NOT NULL DEFAULT 15,
 boundary_json JSON NOT NULL DEFAULT '[]', camps_json JSON NOT NULL DEFAULT '[]',
 created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX IF NOT EXISTS ix_livestock_farm_customer_id ON livestock_farm(customer_id);
CREATE TABLE IF NOT EXISTS livestock_gateway (
 id SERIAL PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customer(id), farm_id INTEGER NOT NULL REFERENCES livestock_farm(id),
 name VARCHAR(120) NOT NULL, gateway_uid VARCHAR(100) NOT NULL, latitude DOUBLE PRECISION NOT NULL, longitude DOUBLE PRECISION NOT NULL,
 backhaul VARCHAR(30) NOT NULL DEFAULT 'WIFI', last_seen_at TIMESTAMPTZ, active BOOLEAN NOT NULL DEFAULT TRUE,
 created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX IF NOT EXISTS ix_livestock_gateway_customer_id ON livestock_gateway(customer_id);
CREATE INDEX IF NOT EXISTS ix_livestock_gateway_farm_id ON livestock_gateway(farm_id);
CREATE INDEX IF NOT EXISTS ix_livestock_gateway_gateway_uid ON livestock_gateway(gateway_uid);
CREATE TABLE IF NOT EXISTS livestock_animal (
 id SERIAL PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customer(id), farm_id INTEGER NOT NULL REFERENCES livestock_farm(id),
 gateway_id INTEGER REFERENCES livestock_gateway(id), animal_uid VARCHAR(100) NOT NULL, tag_uid VARCHAR(100) NOT NULL,
 species VARCHAR(30) NOT NULL DEFAULT 'SHEEP', tracker_type VARCHAR(30) NOT NULL DEFAULT 'LORA_EAR_TAG', linked_device_id INTEGER REFERENCES device(id), herd_name VARCHAR(100), camp_name VARCHAR(100), display_name VARCHAR(120),
 movement_state VARCHAR(30) NOT NULL DEFAULT 'WAITING', battery_pct INTEGER, rssi INTEGER, snr DOUBLE PRECISION,
 last_seen_at TIMESTAMPTZ, active BOOLEAN NOT NULL DEFAULT TRUE, created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX IF NOT EXISTS ix_livestock_animal_customer_id ON livestock_animal(customer_id);
CREATE INDEX IF NOT EXISTS ix_livestock_animal_farm_id ON livestock_animal(farm_id);
CREATE INDEX IF NOT EXISTS ix_livestock_animal_gateway_id ON livestock_animal(gateway_id);
CREATE UNIQUE INDEX IF NOT EXISTS uq_livestock_animal_tag_customer ON livestock_animal(customer_id,tag_uid);

CREATE INDEX IF NOT EXISTS ix_livestock_animal_linked_device_id ON livestock_animal(linked_device_id);
ALTER TABLE livestock_gateway ADD COLUMN IF NOT EXISTS api_token VARCHAR(96);
CREATE UNIQUE INDEX IF NOT EXISTS uq_livestock_gateway_api_token ON livestock_gateway(api_token);
CREATE TABLE IF NOT EXISTS livestock_tag_reception (
 id SERIAL PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customer(id), farm_id INTEGER NOT NULL REFERENCES livestock_farm(id),
 gateway_id INTEGER NOT NULL REFERENCES livestock_gateway(id), animal_id INTEGER NOT NULL REFERENCES livestock_animal(id),
 tag_uid VARCHAR(100) NOT NULL, sequence VARCHAR(100) NOT NULL, rssi INTEGER, snr DOUBLE PRECISION, battery_pct INTEGER,
 movement_state VARCHAR(30) NOT NULL DEFAULT 'UNKNOWN', received_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
 CONSTRAINT uq_livestock_reception_gateway_tag_sequence UNIQUE(gateway_id,tag_uid,sequence));
CREATE INDEX IF NOT EXISTS ix_livestock_reception_customer_id ON livestock_tag_reception(customer_id);
CREATE INDEX IF NOT EXISTS ix_livestock_reception_farm_id ON livestock_tag_reception(farm_id);
CREATE INDEX IF NOT EXISTS ix_livestock_reception_gateway_id ON livestock_tag_reception(gateway_id);
CREATE INDEX IF NOT EXISTS ix_livestock_reception_animal_id ON livestock_tag_reception(animal_id);
CREATE INDEX IF NOT EXISTS ix_livestock_reception_tag_uid ON livestock_tag_reception(tag_uid);
CREATE INDEX IF NOT EXISTS ix_livestock_reception_received_at ON livestock_tag_reception(received_at);
ALTER TABLE livestock_farm ADD COLUMN IF NOT EXISTS roll_call_time VARCHAR(5) NOT NULL DEFAULT '18:00';
ALTER TABLE livestock_farm ADD COLUMN IF NOT EXISTS late_minutes INTEGER NOT NULL DEFAULT 30;
ALTER TABLE livestock_farm ADD COLUMN IF NOT EXISTS missing_minutes INTEGER NOT NULL DEFAULT 120;
ALTER TABLE livestock_farm ADD COLUMN IF NOT EXISTS quiet_start VARCHAR(5) NOT NULL DEFAULT '20:00';
ALTER TABLE livestock_farm ADD COLUMN IF NOT EXISTS quiet_end VARCHAR(5) NOT NULL DEFAULT '05:00';
ALTER TABLE livestock_farm ADD COLUMN IF NOT EXISTS night_monitoring_enabled BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE livestock_farm ADD COLUMN IF NOT EXISTS night_movement_threshold INTEGER NOT NULL DEFAULT 3;
ALTER TABLE livestock_animal ADD COLUMN IF NOT EXISTS expected_night_gateway_id INTEGER REFERENCES livestock_gateway(id);
CREATE TABLE IF NOT EXISTS livestock_alert (id SERIAL PRIMARY KEY,customer_id INTEGER NOT NULL REFERENCES customer(id),farm_id INTEGER NOT NULL REFERENCES livestock_farm(id),animal_id INTEGER REFERENCES livestock_animal(id),gateway_id INTEGER REFERENCES livestock_gateway(id),alert_type VARCHAR(50) NOT NULL,severity VARCHAR(20) NOT NULL DEFAULT 'WARNING',title VARCHAR(160) NOT NULL,detail VARCHAR(500) NOT NULL,state VARCHAR(20) NOT NULL DEFAULT 'OPEN',opened_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,acknowledged_at TIMESTAMPTZ,closed_at TIMESTAMPTZ);
CREATE TABLE IF NOT EXISTS livestock_daily_roll_call (id SERIAL PRIMARY KEY,customer_id INTEGER NOT NULL REFERENCES customer(id),farm_id INTEGER NOT NULL REFERENCES livestock_farm(id),roll_call_date DATE NOT NULL,expected_count INTEGER NOT NULL DEFAULT 0,present_count INTEGER NOT NULL DEFAULT 0,late_count INTEGER NOT NULL DEFAULT 0,missing_count INTEGER NOT NULL DEFAULT 0,low_battery_count INTEGER NOT NULL DEFAULT 0,detail_json JSON NOT NULL DEFAULT '{}',completed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,CONSTRAINT uq_livestock_daily_roll_call_farm_date UNIQUE(farm_id,roll_call_date));
ALTER TABLE livestock_animal ADD COLUMN IF NOT EXISTS estimated_lat DOUBLE PRECISION;
ALTER TABLE livestock_animal ADD COLUMN IF NOT EXISTS estimated_lon DOUBLE PRECISION;
ALTER TABLE livestock_animal ADD COLUMN IF NOT EXISTS estimated_radius_m INTEGER;
ALTER TABLE livestock_animal ADD COLUMN IF NOT EXISTS location_confidence VARCHAR(20);
ALTER TABLE livestock_animal ADD COLUMN IF NOT EXISTS location_gateway_count INTEGER NOT NULL DEFAULT 0;
ALTER TABLE livestock_animal ADD COLUMN IF NOT EXISTS location_estimated_at TIMESTAMPTZ;
CREATE TABLE IF NOT EXISTS livestock_radio_calibration (id SERIAL PRIMARY KEY,customer_id INTEGER NOT NULL REFERENCES customer(id),farm_id INTEGER NOT NULL REFERENCES livestock_farm(id),gateway_id INTEGER NOT NULL REFERENCES livestock_gateway(id),distance_m INTEGER NOT NULL,direction VARCHAR(20) NOT NULL DEFAULT 'UNKNOWN',terrain VARCHAR(30) NOT NULL DEFAULT 'OPEN_FIELD',median_rssi DOUBLE PRECISION NOT NULL,min_rssi DOUBLE PRECISION,max_rssi DOUBLE PRECISION,median_snr DOUBLE PRECISION,sample_count INTEGER NOT NULL DEFAULT 1,tx_power_dbm INTEGER NOT NULL DEFAULT 22,spreading_factor INTEGER NOT NULL DEFAULT 9,notes VARCHAR(300),created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,CONSTRAINT uq_livestock_calibration_point UNIQUE(gateway_id,distance_m,direction,terrain));
