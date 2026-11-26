from sqlalchemy import inspect,text

def ensure_livestock_live_schema(db):
    inspector=inspect(db.engine)
    tables=set(inspector.get_table_names())

    if 'livestock_farm' in tables:
        farm_cols={c['name'] for c in inspector.get_columns('livestock_farm')}
        additions={'roll_call_time':"VARCHAR(5) NOT NULL DEFAULT '18:00'",'late_minutes':'INTEGER NOT NULL DEFAULT 30','missing_minutes':'INTEGER NOT NULL DEFAULT 120','quiet_start':"VARCHAR(5) NOT NULL DEFAULT '20:00'",'quiet_end':"VARCHAR(5) NOT NULL DEFAULT '05:00'",'night_monitoring_enabled':'BOOLEAN NOT NULL DEFAULT TRUE','night_movement_threshold':'INTEGER NOT NULL DEFAULT 3'}
        for name,ddl in additions.items():
            if name not in farm_cols:db.session.execute(text(f'ALTER TABLE livestock_farm ADD COLUMN {name} {ddl}'))
        db.session.commit()
    if 'livestock_animal' in tables:
        animal_cols={c['name'] for c in inspector.get_columns('livestock_animal')}
        if 'expected_night_gateway_id' not in animal_cols:
            db.session.execute(text('ALTER TABLE livestock_animal ADD COLUMN expected_night_gateway_id INTEGER REFERENCES livestock_gateway(id)'));db.session.commit()
    if 'livestock_gateway' in tables:
        cols={c['name'] for c in inspector.get_columns('livestock_gateway')}
        if 'api_token' not in cols:
            db.session.execute(text('ALTER TABLE livestock_gateway ADD COLUMN api_token VARCHAR(96)'))
            db.session.commit()
    db.create_all()
    inspector=inspect(db.engine)
    if 'livestock_animal' in set(inspector.get_table_names()):
        cols={c['name'] for c in inspector.get_columns('livestock_animal')}
        additions={'estimated_lat':'DOUBLE PRECISION','estimated_lon':'DOUBLE PRECISION','estimated_radius_m':'INTEGER','location_confidence':'VARCHAR(20)','location_gateway_count':'INTEGER NOT NULL DEFAULT 0','location_estimated_at':'TIMESTAMPTZ'}
        for name,ddl in additions.items():
            if name not in cols:db.session.execute(text(f'ALTER TABLE livestock_animal ADD COLUMN {name} {ddl}'))
        db.session.commit()
    # PostgreSQL and SQLite both accept a unique index here.
    db.session.execute(text('CREATE UNIQUE INDEX IF NOT EXISTS uq_livestock_gateway_api_token ON livestock_gateway(api_token)'))
    from .models import LivestockGateway
    import secrets
    for gateway in LivestockGateway.query.filter(LivestockGateway.api_token.is_(None)).all():gateway.api_token=secrets.token_urlsafe(32)
    db.session.commit()
