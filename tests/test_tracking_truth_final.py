from datetime import datetime,timedelta,timezone
from types import SimpleNamespace
from app.routes import analyse_tracking_points,build_validated_trips
BASE=datetime(2026,9,27,6,0,tzinfo=timezone.utc)
def p(i,lat,lon,sec,speed=0,acc=8,trip="trip-table"):
 return SimpleNamespace(id=i,latitude=lat,longitude=lon,speed_kmh=speed,accuracy_m=acc,sampled_at=BASE+timedelta(seconds=sec),sequence=f"{trip}|p-{i}")
def table_rows():
 offsets=[(0,0),(.00003,-.00002),(-.00004,.00003),(.00002,.00004),(-.00003,-.00003)]
 return [p(i,-26.73622+offsets[i%5][0],27.84626+offsets[i%5][1],i*60,9 if i==17 else 0) for i in range(82)]
def test_both_views_return_stationary_truth():
 for fn in (analyse_tracking_points,build_validated_trips):
  r=fn(table_rows());assert r["distance_km"]==0.0;assert r["max_speed"]==0;assert r["moving_minutes"]==0;assert r["stopped_minutes"]>=81;assert r["rejection_counts"]["STATIONARY_DRIFT"]>0
def test_real_sustained_movement_survives():
 rows=[p(i,-26.73622+i*.00045,27.84626,i*30,6,8,"trip-drive") for i in range(6)]
 for fn in (analyse_tracking_points,build_validated_trips):
  r=fn(rows);assert r["distance_km"]>.2;assert r["max_speed"]>0;assert len(r["trips"])==1
