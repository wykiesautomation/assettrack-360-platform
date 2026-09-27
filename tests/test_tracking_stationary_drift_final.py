from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from app.routes import build_validated_trips

BASE=datetime(2026,9,27,6,0,tzinfo=timezone.utc)
def point(i,lat,lon,seconds,speed=0,accuracy=8,trip="trip-table"):
    return SimpleNamespace(id=i,latitude=lat,longitude=lon,speed_kmh=speed,accuracy_m=accuracy,sampled_at=BASE+timedelta(seconds=seconds),sequence=f"{trip}|p-{i}")

def test_phone_on_table_is_zero_distance_and_speed():
    rows=[]
    offsets=[(0,0),(0.00003,-0.00002),(-0.00004,0.00003),(0.00002,0.00004),(-0.00003,-0.00003)]
    for i in range(82):
        a,b=offsets[i%len(offsets)];rows.append(point(i,-26.73622+a,27.84626+b,i*60,speed=9 if i==17 else 0,accuracy=8))
    result=build_validated_trips(rows)
    assert len(result["trips"])==1
    trip=result["trips"][0]
    assert trip["distance_km"]==0.0
    assert trip["maximum_speed"]==0
    assert trip["moving_minutes"]==0
    assert trip["stopped_minutes"]>=81
    assert len(trip["route"])==1

def test_real_sustained_movement_is_retained():
    rows=[point(i,-26.73622+i*0.00045,27.84626,i*30,speed=6,accuracy=8,trip="trip-drive") for i in range(6)]
    result=build_validated_trips(rows)
    assert len(result["trips"])==1
    assert result["trips"][0]["distance_km"]>0.20
    assert result["trips"][0]["maximum_speed"]>0

def test_new_start_id_creates_second_trip():
    rows=[point(1,-26.7362,27.8462,0,trip="trip-one"),point(2,-26.7357,27.8462,30,speed=6,trip="trip-one"),point(3,-26.7352,27.8462,60,speed=6,trip="trip-one"),point(4,-26.7347,27.8462,90,speed=6,trip="trip-two"),point(5,-26.7342,27.8462,120,speed=6,trip="trip-two"),point(6,-26.7337,27.8462,150,speed=6,trip="trip-two")]
    result=build_validated_trips(rows)
    assert len(result["trips"])==2
