from datetime import datetime, timedelta, timezone


def test_dashboard_connectivity_thresholds_are_single_source():
    source=open("app/routes.py",encoding="utf-8").read()
    assert "def device_connectivity_state" in source
    assert "age_seconds<=90" in source
    assert "age_seconds<=300" in source
    assert "return 'OFFLINE'" in source
    assert "else 'HEALTHY'" not in source[source.index("def asset_status"):source.index("BOARD_TELEMETRY_SPECS")]

def test_asset_template_separates_live_last_reported_and_simulation():
    html=open("app/templates/asset.html",encoding="utf-8").read()
    assert "LAST SIMULATED TEST" in html
    assert "CURRENT LIVE VALUE" in html
    assert "LAST REPORTED VALUE" in html
    assert "WAITING FOR BOARD TELEMETRY" in html
    assert "asset_connectivity.state" in html
