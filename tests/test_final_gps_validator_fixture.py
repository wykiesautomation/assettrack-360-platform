import csv, importlib.util
from datetime import datetime, timezone
from pathlib import Path
MODULE=Path(__file__).parents[1]/'app'/'tracking_validator.py'
spec=importlib.util.spec_from_file_location('tracking_validator',MODULE);validator=importlib.util.module_from_spec(spec);spec.loader.exec_module(validator)
def parsed(value):
    return datetime.fromisoformat(value.replace(' ','T')).astimezone(timezone.utc).isoformat()
def test_asset130_stationary_drift_does_not_form_route():
    fixture=Path(__file__).parent/'fixtures'/'asset130_stationary_drift.csv'
    points=[]
    with fixture.open(newline='',encoding='utf-8-sig') as handle:
        for row in csv.DictReader(handle):
            accuracy=float(row['accuracy_m'] or 0)
            if accuracy>100:continue
            points.append({'latitude':float(row['latitude']),'longitude':float(row['longitude']),
                'accuracy':max(3.0,accuracy),'reported_speed':max(0.0,float(row['speed_kmh'] or 0)),
                'heading':float(row['heading'] or 0),'timestamp':parsed(row['sampled_at']),'trip_id':None})
    result=validator.validate_movement_segments(points)
    assert len(points)==1027
    assert len(result['segments'])==0
    assert len(result['accepted_edges'])==0
    assert sum(1 for item in result['rejected'] if item['reason']=='ZERO_SPEED_DRIFT_RUN')>=1
