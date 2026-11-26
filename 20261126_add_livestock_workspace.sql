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
