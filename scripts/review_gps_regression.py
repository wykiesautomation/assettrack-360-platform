import os,tempfile,io,logging
from pathlib import Path
os.environ['DATABASE_URL']='sqlite:///'+str(Path(tempfile.mkdtemp())/'test.db')
os.environ['SITE_MAINTENANCE_BACKGROUND']='false'
from app import app,db
from app.models import Customer,Site,Asset,Device,User,Subscription,SubscriptionPlan,MobileConsent,Location,Reading
from app.routes import analyse_safety_twin_points,mobile_reading_sequence
from datetime import datetime,timezone,timedelta
from sqlalchemy import event
from werkzeug.security import generate_password_hash
# SQLite fixture only: PostgreSQL BigInteger identities are not SQLite rowids.
from sqlalchemy.orm import Session
from sqlalchemy import BigInteger
fixture_counters={}
@event.listens_for(Session,'before_flush')
def fixture_ids(session,context,instances):
 for obj in session.new:
  table=obj.__table__
  if 'id' in table.c and isinstance(table.c.id.type,BigInteger) and getattr(obj,'id',None) is None:
   counters=fixture_counters;key=table.name
   counters[key]=counters.get(key,10000)+1;obj.id=counters[key]

with app.app_context():
 c=Customer(name='Test',slug='test');db.session.add(c);db.session.flush()
 site=Site(customer_id=c.id,name='Test');db.session.add(site);db.session.flush()
 a=Asset(customer_id=c.id,site_id=site.id,name='Phone',asset_type='TRACKER');db.session.add(a);db.session.flush()
 d=Device(customer_id=c.id,asset_id=a.id,device_uid='TEST-PHONE',api_token='TEST_SECRET',device_type='MOBILE_WEB_TRACKER',active=True);db.session.add(d);db.session.flush()
 db.session.add(MobileConsent(customer_id=c.id,asset_id=a.id,device_id=d.id,device_uid=d.device_uid,active=True))
 db.session.add(Subscription(customer_id=c.id,plan_id=SubscriptionPlan.query.first().id,state='ACTIVE',access_source='PAID',current_period_end=datetime.now(timezone.utc)+timedelta(days=30)))
 u=User(customer_id=c.id,name='Test',email='test@example.invalid',password_hash=generate_password_hash('test'),role='customer_admin',email_verified=True);db.session.add(u);db.session.commit();uid=u.id;aid=a.id;cid=c.id
 assert analyse_safety_twin_points([])['confidence']==0
 assert len(mobile_reading_sequence('x'*80,'battery_percent'))<=80
 # enforce real varchar limit in SQLite fixture to reproduce Postgres constraint
 engine=db.engine
@event.listens_for(engine,'before_cursor_execute')
def check_width(conn,cursor,statement,params,context,many):
 if statement.lower().startswith('insert into reading'):
  rows=params if many else [params]
  for row in rows:
   if isinstance(row,tuple):
    assert all(not isinstance(v,str) or len(v)<=80 for v in row),row
stream=io.StringIO();app.logger.addHandler(logging.StreamHandler(stream))
client=app.test_client();headers={'Authorization':'Bearer TEST_SECRET'}
point={'device_id':'TEST-PHONE','sequence':'x'*80,'latitude':-26.7,'longitude':27.8,'accuracy_m':5,'speed_kmh':0,'battery_percent':80,'timestamp':datetime.now(timezone.utc).isoformat()}
r=client.post('/api/v1/mobile/location',headers=headers,json=point);print('single',r.status_code,r.json);assert r.status_code==202
point2=dict(point,sequence='y'*80)
r=client.post('/api/v1/mobile/location/batch',headers=headers,json={'device_id':'TEST-PHONE','points':[point2]});print('batch',r.status_code,r.json);assert r.status_code==202 and r.json['accepted_count']==1
r=client.post('/api/v1/mobile/location/batch',headers=headers,json={'points':[point2]});assert r.status_code==202 and r.json['duplicate_count']==1
with app.app_context():assert Location.query.filter_by(asset_id=aid).count()==2
with client.session_transaction() as session:session['_user_id']=str(uid);session['_fresh']=True
r=client.get(f'/asset/{aid}/safety-twin');print('map',r.status_code);assert r.status_code==200;assert 'Waiting for an accepted GPS position.' not in r.get_data(as_text=True)
# expired subscription: heartbeat can be accepted, GPS must be denied
with app.app_context():
 sub=Subscription.query.filter_by(customer_id=cid).first();sub.state='SUSPENDED';sub.access_source='PAYMENT_REQUIRED';sub.current_period_end=None;db.session.commit()
api=app.test_client();r=api.post('/api/v1/mobile/heartbeat',headers=headers,json={'device_id':'TEST-PHONE','sequence':'hb-test'});print('heartbeat',r.status_code);assert r.status_code==202
r=api.post('/api/v1/mobile/location',headers=headers,json=dict(point,sequence='denied'));assert r.status_code==402
assert 'subscription_inactive' in stream.getvalue() and 'TEST_SECRET' not in stream.getvalue()
print('PASS: single and batch GPS -> database -> Safety Twin; long sequences; duplicate; subscription denial; heartbeat; zero-data confidence; safe logs')
# Restore entitlement and compare dashboard query growth with 20 extra assets.
with app.app_context():
 sub=Subscription.query.filter_by(customer_id=cid).first();sub.state='ACTIVE';sub.access_source='PAID';sub.current_period_end=datetime.now(timezone.utc)+timedelta(days=30);db.session.commit()
r=client.get('/dashboard');assert r.status_code==200;r1=int(r.headers['X-AssetTrack-SQL-Count'])
with app.app_context():
 for i in range(20):
  extra=Asset(customer_id=cid,site_id=site.id if False else 1,name=f'Extra {i}',asset_type='TRACKER');db.session.add(extra);db.session.flush()
  db.session.add(Device(customer_id=cid,asset_id=extra.id,device_uid=f'EXTRA-{i}',api_token=f'EXTRA-TOKEN-{i}',device_type='MOBILE_WEB_TRACKER',active=True,last_seen=datetime.now(timezone.utc)))
 db.session.commit()
r=client.get('/dashboard');assert r.status_code==200;r2=int(r.headers['X-AssetTrack-SQL-Count']);assert r2<=r1+2,(r1,r2)
print('PASS dashboard query growth:',r1,'->',r2,'with 20 additional assets')
