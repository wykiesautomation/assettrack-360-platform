import os,tempfile,json,time
from pathlib import Path
os.environ['DATABASE_URL']='sqlite:///'+str(Path(tempfile.mkdtemp())/'test.db')
os.environ['SITE_MAINTENANCE_BACKGROUND']='false'
from app import app,db
from app.models import Customer,User,Subscription,SubscriptionPlan,WorkspaceProfile,FleetFeatureDefaults,TrendCleanupState
from app import routes
from sqlalchemy import event
from werkzeug.security import generate_password_hash
from datetime import datetime,timezone
routes._calibration_schema_ready=True
with app.app_context():
 c=Customer(name='Fixture',slug='fixture');db.session.add(c);db.session.flush()
 u=User(customer_id=c.id,name='Test',email='test@example.invalid',password_hash=generate_password_hash('test-only-password'),role='customer_admin',email_verified=True);db.session.add(u)
 plan=SubscriptionPlan.query.first();db.session.add(Subscription(customer_id=c.id,plan_id=plan.id,state='ACTIVE',access_source='COMPLIMENTARY'))
 db.session.add(WorkspaceProfile(customer_id=c.id));db.session.add(FleetFeatureDefaults(customer_id=c.id));db.session.commit();uid=u.id
 engine=db.engine
queries=[]
@event.listens_for(engine,'before_cursor_execute')
def record(conn,cursor,statement,*args):queries.append(statement);time.sleep(.025)
client=app.test_client()
with client.session_transaction() as session:session['_user_id']=str(uid);session['_fresh']=True
out={}
for path in ['/notifications/email','/static/rev28_full.css?v=45']:
 queries.clear();t=time.perf_counter();response=client.get(path);elapsed=time.perf_counter()-t
 out[path]={'status':response.status_code,'queries':len(queries),'elapsed_ms':round(elapsed*1000),'server_timing':response.headers.get('Server-Timing'),'cache_control':response.headers.get('Cache-Control')}
 assert response.status_code==200
print(json.dumps(out,indent=2))

assert out['/notifications/email']['queries']==4
assert out['/static/rev28_full.css?v=45']['queries']==0
assert 'no-store' in out['/notifications/email']['cache_control']
assert out['/notifications/email']['server_timing']
assert client.get('/notifications/email').headers['X-AssetTrack-Build']=='SiteResponse-REV02'
assert client.post('/notifications/email',data={'contact_email':'updated@example.invalid','enabled':'on'}).status_code==302
with app.app_context():
 assert WorkspaceProfile.query.filter_by(customer_id=1).first().contact_email=='updated@example.invalid'
 c2=Customer(name='OTHER_TENANT_SECRET',slug='other');db.session.add(c2);db.session.flush()
 u2=User(customer_id=c2.id,name='Other',email='other@example.invalid',password_hash='test',role='customer_admin',email_verified=True);db.session.add(u2)
 db.session.add(Subscription(customer_id=c2.id,plan_id=SubscriptionPlan.query.first().id,state='PAYMENT_REQUIRED',access_source='PAYMENT_REQUIRED'));db.session.commit();other_uid=u2.id
assert 'OTHER_TENANT_SECRET' not in client.get('/notifications/email').get_data(as_text=True)
other=app.test_client()
with other.session_transaction() as session:session['_user_id']=str(other_uid);session['_fresh']=True
response=other.get('/notifications/email');assert response.status_code==302 and 'subscription-required' in response.location
assert app.test_client().get('/notifications/email').status_code==302
client.get('/logout');assert client.get('/notifications/email').status_code==302
# Maintenance must return immediately even if its job is blocked.
import threading
from app import site_performance,trend_cleanup
started=threading.Event();release=threading.Event()
def blocked_cleanup(force=False):started.set();release.wait(5)
trend_cleanup.cleanup_due=blocked_cleanup
os.environ['SITE_MAINTENANCE_BACKGROUND']='true'
t=time.perf_counter();site_performance.schedule_retention(app);assert time.perf_counter()-t<.5
assert started.wait(2);release.set()
print('PASS: query budgets, settings save, tenant isolation, subscription gate, anonymous access, logout, background isolation')
