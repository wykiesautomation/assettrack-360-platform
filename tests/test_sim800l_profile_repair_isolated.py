import sys,types,importlib
from pathlib import Path
from datetime import datetime,timezone,timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
root=Path(__file__).resolve().parents[1]
pkg=types.ModuleType('app');pkg.__path__=[str(root/'app')];pkg.db=SQLAlchemy();sys.modules['app']=pkg
m=importlib.import_module('app.models');admin=types.ModuleType('app.admin');admin.log=lambda *a:None;sys.modules['app.admin']=admin
repair=importlib.import_module('app.sim800l_profile_repair');api=importlib.import_module('app.device_api')
app=Flask('test',template_folder=str(root/'app/templates'));app.config.update(SECRET_KEY='test',SQLALCHEMY_DATABASE_URI='sqlite://',TESTING=True);pkg.db.init_app(app);lm=LoginManager(app);lm.login_view='login'
@lm.user_loader
def user(uid):return pkg.db.session.get(m.User,int(uid))
app.register_blueprint(repair.bp);app.register_blueprint(api.bp)
with app.app_context():
 db=pkg.db;db.create_all();c=m.Customer(name='Test',slug='test');db.session.add(c);db.session.flush();u=m.User(customer_id=c.id,email='test@example.invalid',name='Test',password_hash='unused',role='platform_admin');db.session.add(u);db.session.flush()
 d=m.Device(customer_id=c.id,device_uid='AT360-LILYGO-AT360LILYGOABCDEF123456',api_token='keep-test-token',device_type='LILYGO_T_SIM7000G_TRACKER',capabilities=['PROFILE:'+repair.OLD]);db.session.add(d);db.session.commit()
 client=app.test_client()
 with client.session_transaction() as ss:ss['_user_id']=str(u.id);ss['_fresh']=True;ss['profile_repair_csrf']='test-csrf'
 form={'csrf':'test-csrf','confirm':'SIM800L','action':'device','device_id':d.id,'hardware_uid':'AT360-LILYGO-ABCDEF123456','firmware':'AT360_LILYGO_TCALL_IO_REV17'}
 assert client.post('/platform-admin/sim800l-profile-repair',data={**form,'csrf':'bad'}).status_code==403
 assert client.post('/platform-admin/sim800l-profile-repair',data=form).status_code==302
 db.session.refresh(d);assert d.api_token=='keep-test-token' and d.device_uid=='AT360-LILYGO-AT360LILYGOABCDEF123456';assert d.device_type=='LILYGO_TCALL_SIM800L_IO';assert m.DeviceChannelAssignment.query.count()==8
 try:repair.repair_device(d,'AT360-LILYGO-000000000000','AT360_LILYGO_TCALL_IO_REV17');raise AssertionError('wrong board accepted')
 except ValueError:pass
 reg=m.HardwareDeviceRegistration(customer_id=c.id,created_by=u.id,profile_code=repair.OLD,code_hash=api.h('ABCD-1234'),expires_at=datetime.now(timezone.utc)+timedelta(minutes=5));db.session.add(reg);db.session.commit()
 cf={'csrf':'test-csrf','confirm':'SIM800L','action':'claim','customer_id':c.id,'claim_code':'ABCD-1234'}
 assert client.post('/platform-admin/sim800l-profile-repair',data=cf).status_code==302
 db.session.refresh(reg);assert reg.profile_code==repair.TARGET and reg.provisioning_state=='WAITING';assert m.Device.query.count()==1
 payload={'claim_code':'ABCD-1234','profile_code':repair.OLD,'board_id':'AABBCCDDEEFF'}
 r=client.post('/api/v2/devices/claim',json=payload);assert r.status_code==409 and r.json['error']=='profile_mismatch'
 u.role='customer_admin';db.session.commit();assert client.get('/platform-admin/sim800l-profile-repair').status_code==403
 from jinja2 import Environment
 for f in ['sim800l_profile_repair.html','platform_admin_devices.html']:Environment().parse((root/'app/templates'/f).read_text())
 print('PASS: owner guard, CSRF, wrong board rejected, profile repair, UID/token preserved, 8 placeholders, unused code repair, no device creation, strict mismatch retained, templates parsed. Audit integration stubbed; no live database.')
