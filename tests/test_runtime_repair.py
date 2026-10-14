import os,sys,re,subprocess,tempfile,json,time
from pathlib import Path
os.environ['DATABASE_URL']='sqlite:///'+str(Path(tempfile.mkdtemp())/'regression.db')
os.environ['TREND_CLEANUP_BACKGROUND']='false'
os.environ['GEOCODING_DISABLED']='false'
from app import app,db
from app.models import *
from app import route_intelligence as geo
from sqlalchemy import event
from sqlalchemy.orm import Session
from datetime import datetime,timezone,timedelta
from werkzeug.security import generate_password_hash
checks=[]
def check(name,value):
 assert value,name
 checks.append(name);print('PASS',name)
# SQLite test adapter only: production uses PostgreSQL BIGSERIAL.
ids={}
@event.listens_for(Session,'before_flush')
def sqlite_ids(session,*args):
 for obj in session.new:
  table=getattr(obj,'__table__',None)
  if table is not None and 'id' in table.c and isinstance(table.c.id.type,db.BigInteger) and obj.id is None:
   key=table.name;ids[key]=ids.get(key,10000)+1;obj.id=ids[key]
with app.app_context():
 c=Customer(name='Regression',slug='regression');db.session.add(c);db.session.flush()
 u=User(customer_id=c.id,email='test@example.invalid',name='Test',role='customer_admin',password_hash=generate_password_hash('test-only-password'),email_verified=True);db.session.add(u)
 site=Site(customer_id=c.id,name='Test');db.session.add(site);db.session.flush()
 a=Asset(customer_id=c.id,site_id=site.id,name='Test tracker',asset_type='TRACKER');db.session.add(a);db.session.flush()
 d=Device(customer_id=c.id,asset_id=a.id,device_uid='TEST-TRACKER',device_type='MOBILE_WEB_TRACKER',api_token='test-only-token',capabilities=['GPS'],last_seen=datetime.now(timezone.utc)-timedelta(days=40));db.session.add(d);db.session.flush()
 plan=SubscriptionPlan.query.first();db.session.add(Subscription(customer_id=c.id,plan_id=plan.id,state='ACTIVE',access_source='COMPLIMENTARY'))
 db.session.add(MobileConsent(customer_id=c.id,asset_id=a.id,device_id=d.id,device_uid=d.device_uid,active=True))
 db.session.add(Location(customer_id=c.id,asset_id=a.id,sampled_at=datetime.now(timezone.utc),latitude=-26.6,longitude=27.8,accuracy_m=10,speed_kmh=0));db.session.commit();uid=u.id;aid=a.id;did=d.id;cid=c.id
client=app.test_client()
with client.session_transaction() as s:s['_user_id']=str(uid);s['_fresh']=True
geo._json_get=lambda *args,**kwargs: (_ for _ in ()).throw(AssertionError('Page must not contact geocoder'))
for path in ['/dashboard',f'/asset/{aid}']:
 resp=client.get(path);check(path+' renders',resp.status_code==200);check(path+' timing header','Server-Timing' in resp.headers)
 for i,js in enumerate(re.findall(r'<script[^>]*>(.*?)</script>',resp.get_data(as_text=True),re.S)):
  f=Path(tempfile.gettempdir())/f'at360_script_{i}.js';f.write_text(js)
  result=subprocess.run(['node','--check',str(f)],capture_output=True,text=True)
  check(path+f' script {i} syntax',result.returncode==0)
  if 'adaptive per-user' in js:
   pass
headers={'Authorization':'Bearer test-only-token'}
resp=client.post('/api/v1/mobile/heartbeat',headers=headers,json={'device_id':'TEST-TRACKER','battery_percent':75,'charging':False,'sequence':'test-heartbeat'})
check('heartbeat accepted',resp.status_code==202)
resp=client.get('/api/v1/mobile/status',headers=headers);check('heartbeat makes device ONLINE',resp.json['tracking_state']=='ONLINE')
sequence='x'*80
point={'device_id':'TEST-TRACKER','sequence':sequence,'timestamp':datetime.now(timezone.utc).isoformat(),'latitude':-26.6001,'longitude':27.8001,'accuracy_m':10,'speed_kmh':0,'battery_percent':74}
resp=client.post('/api/v1/mobile/location/batch',headers=headers,json={'device_id':'TEST-TRACKER','points':[point]})
print('batch response',resp.status_code,resp.json)
check('location batch accepted',resp.status_code in (202,207) and sequence in resp.json['accepted'])
resp=client.post('/api/v1/mobile/location/batch',headers=headers,json={'device_id':'TEST-TRACKER','points':[point]})
check('duplicate batch idempotent',sequence in resp.json['duplicates'])
check('invalid token rejected',client.post('/api/v1/mobile/heartbeat',headers={'Authorization':'Bearer wrong'},json={}).status_code==401)
check('wrong device identity rejected',client.post('/api/v1/mobile/heartbeat',headers=headers,json={'device_id':'WRONG'}).status_code==403)
with app.app_context():
 check('reading sequence accommodates suffix',Reading.__table__.c.sequence.type.length==160)
 check('location actually persisted',Location.query.filter_by(sequence=sequence,asset_id=aid).count()==1)
 d=db.session.get(Device,did);d.last_seen=datetime.now(timezone.utc)-timedelta(minutes=6);db.session.commit()
resp=client.get('/api/v1/mobile/status',headers=headers);check('stale contact remains OFFLINE',resp.json['tracking_state']=='OFFLINE')
# Static requests must not load the authenticated user from the database.
queries=[]
with app.app_context():
 engine=db.engine
 @event.listens_for(engine,'before_cursor_execute')
 def record(conn,cursor,statement,*args):queries.append(statement)
resp=client.get('/static/mobile_tracker.js');check('static response',resp.status_code==200);check('static no database queries',not queries)
# Confirm tenant boundary.
with app.app_context():
 c2=Customer(name='Other',slug='other');db.session.add(c2);db.session.flush()
 s2=Site(customer_id=c2.id,name='Other');db.session.add(s2);db.session.flush()
 a2=Asset(customer_id=c2.id,site_id=s2.id,name='SECRET_OTHER_TENANT',asset_type='TRACKER');db.session.add(a2);db.session.commit();other=a2.id
resp=client.get('/dashboard');check('dashboard tenant isolation','SECRET_OTHER_TENANT' not in resp.get_data(as_text=True))
check('asset tenant isolation',client.get(f'/asset/{other}').status_code==404)
print(json.dumps({'passed':len(checks),'checks':checks,'limits':'Synthetic SQLite fixtures; production PostgreSQL and real phone delivery not tested.'},indent=2))
