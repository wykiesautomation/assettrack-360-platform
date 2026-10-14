import os,tempfile,logging,io,json
from pathlib import Path
os.environ['DATABASE_URL']='sqlite:///'+str(Path(tempfile.mkdtemp())/'test.db')
os.environ['SITE_MAINTENANCE_BACKGROUND']='false'
from app import app,db
from app.models import Customer,Site,Asset,Device
with app.app_context():
 c=Customer(name='Fixture',slug='fixture');db.session.add(c);db.session.flush()
 site=Site(customer_id=c.id,name='Fixture');db.session.add(site);db.session.flush()
 a=Asset(customer_id=c.id,site_id=site.id,name='Fixture',asset_type='TRACKER');db.session.add(a);db.session.flush()
 for uid,token,active,typ in [('active','SECRET_VALID_TOKEN',True,'MOBILE_WEB_TRACKER'),('inactive','SECRET_INACTIVE_TOKEN',False,'MOBILE_WEB_TRACKER'),('board','SECRET_BOARD_TOKEN',True,'ESP32_REMOTE_IO')]:
  db.session.add(Device(customer_id=c.id,asset_id=a.id,device_uid=uid,api_token=token,active=active,device_type=typ))
 db.session.commit()
stream=io.StringIO();handler=logging.StreamHandler(stream);app.logger.addHandler(handler)
client=app.test_client();count=0
for header,reason in [('', 'authorization_missing'),('Bearer ', 'token_empty'),('Basic SECRET_UNKNOWN_TOKEN','authorization_format_invalid'),('Bearer SECRET_UNKNOWN_TOKEN','token_not_found_in_current_database'),('Bearer SECRET_INACTIVE_TOKEN','device_inactive'),('Bearer SECRET_BOARD_TOKEN','device_type_not_mobile')]:
 stream.seek(0);stream.truncate(0)
 resp=client.post('/api/v1/mobile/heartbeat?token=QUERY_SECRET',headers={'Authorization':header,'Cookie':'COOKIE_SECRET'},json={'latitude':-26.123456,'password':'PAYLOAD_SECRET'})
 assert resp.status_code==401,(resp.status_code,resp.json)
 line=stream.getvalue();assert reason in line,(reason,line)
 for secret in ['SECRET_UNKNOWN_TOKEN','SECRET_INACTIVE_TOKEN','SECRET_BOARD_TOKEN','QUERY_SECRET','COOKIE_SECRET','PAYLOAD_SECRET','-26.123456']:assert secret not in line
 assert resp.headers['X-AssetTrack-Mobile-Logging']=='REV03'
 count+=1;print('PASS',reason)
stream.seek(0);stream.truncate(0)
resp=client.get('/api/v1/mobile/status',headers={'Authorization':'Bearer SECRET_VALID_TOKEN'})
assert resp.status_code==200;assert '"reason":"accepted"' in stream.getvalue();assert '"device_id":' in stream.getvalue();assert 'SECRET_VALID_TOKEN' not in stream.getvalue();count+=1
print('PASS accepted status and authenticated device identity')
stream.seek(0);stream.truncate(0)
resp=client.post('/api/v1/mobile/motion/samples',headers={'Authorization':'Bearer SECRET_UNKNOWN_TOKEN'},json={})
assert resp.status_code==401;assert 'token_not_found_in_current_database' in stream.getvalue();count+=1
print('PASS motion rejection')
stream.seek(0);stream.truncate(0);client.get('/health');assert 'MOBILE_REQUEST' not in stream.getvalue();count+=1
print('PASS non-mobile not logged')
os.environ['MOBILE_REQUEST_LOGGING']='false';stream.seek(0);stream.truncate(0);client.post('/api/v1/mobile/heartbeat',json={});assert 'MOBILE_REQUEST' not in stream.getvalue();count+=1
print('PASS disable logging switch')
print('PASS',count,'checks; synthetic SQLite fixtures; no live phone tested')
