from datetime import datetime,timezone,timedelta
from zoneinfo import ZoneInfo
from . import db
from .models import LivestockAnimal,LivestockAlert,LivestockDailyRollCall

SAST=ZoneInfo('Africa/Johannesburg')
def utcnow():return datetime.now(timezone.utc)
def local_now(current=None):return (current or utcnow()).astimezone(SAST)
def parse_hhmm(value,default):
    try:h,m=[int(x) for x in str(value).split(':',1)];return h*60+m
    except Exception:return default
def in_quiet_hours(farm,current=None):
    minute=local_now(current).hour*60+local_now(current).minute;start=parse_hhmm(farm.quiet_start,1200);end=parse_hhmm(farm.quiet_end,300)
    return start<=minute<end if start<end else minute>=start or minute<end
def open_once(farm,animal,gateway,kind,severity,title,detail,current=None,cooldown_minutes=30):
    current=current or utcnow();cutoff=current-timedelta(minutes=cooldown_minutes)
    exists=LivestockAlert.query.filter(LivestockAlert.farm_id==farm.id,LivestockAlert.animal_id==animal.id,LivestockAlert.alert_type==kind,LivestockAlert.state=='OPEN',LivestockAlert.opened_at>=cutoff).first()
    if not exists:db.session.add(LivestockAlert(customer_id=farm.customer_id,farm_id=farm.id,animal_id=animal.id,gateway_id=getattr(gateway,'id',None),alert_type=kind,severity=severity,title=title,detail=detail,opened_at=current))
def evaluate_night_observation(farm,animal,gateway,current=None):
    current=current or utcnow()
    if not farm.night_monitoring_enabled or not in_quiet_hours(farm,current):return
    moving=str(animal.movement_state or '').upper() in ('ACTIVE','MOVING')
    unexpected=bool(animal.expected_night_gateway_id and gateway and animal.expected_night_gateway_id!=gateway.id)
    if moving:open_once(farm,animal,gateway,'UNEXPECTED_NIGHT_MOVEMENT','WARNING','Unexpected night movement',f'{animal.display_name or animal.animal_uid} reported {animal.movement_state} during quiet hours near {gateway.name if gateway else "an unknown gateway"}.',current,20)
    if unexpected:open_once(farm,animal,gateway,'OUTSIDE_EXPECTED_NIGHT_AREA','HIGH','Outside expected night area',f'{animal.display_name or animal.animal_uid} was expected near gateway {animal.expected_night_gateway_id} but was strongest near {gateway.name}.',current,20)
def roll_call_snapshot(farm,current=None,persist=False):
    current=current or utcnow();local=local_now(current);animals=LivestockAnimal.query.filter_by(customer_id=farm.customer_id,farm_id=farm.id,active=True).all()
    present=[];late=[];missing=[];low=[]
    late_cut=current-timedelta(minutes=max(1,farm.late_minutes));missing_cut=current-timedelta(minutes=max(farm.late_minutes+1,farm.missing_minutes))
    for a in animals:
        if a.battery_pct is not None and a.battery_pct<20:low.append(a.id)
        if a.last_seen_at and a.last_seen_at>=late_cut:present.append(a.id)
        elif a.last_seen_at and a.last_seen_at>=missing_cut:late.append(a.id)
        else:missing.append(a.id)
    data={'date':local.date().isoformat(),'expected':len(animals),'present':len(present),'late':len(late),'missing':len(missing),'low_battery':len(low),'present_ids':present,'late_ids':late,'missing_ids':missing,'low_battery_ids':low}
    if persist:
        row=LivestockDailyRollCall.query.filter_by(farm_id=farm.id,roll_call_date=local.date()).first()
        if not row:row=LivestockDailyRollCall(customer_id=farm.customer_id,farm_id=farm.id,roll_call_date=local.date());db.session.add(row)
        row.expected_count=data['expected'];row.present_count=data['present'];row.late_count=data['late'];row.missing_count=data['missing'];row.low_battery_count=data['low_battery'];row.detail_json=data;row.completed_at=current
    return data
def roll_call_due(farm,current=None):return local_now(current).hour*60+local_now(current).minute>=parse_hhmm(farm.roll_call_time,1080)
