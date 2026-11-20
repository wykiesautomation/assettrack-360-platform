import os,time,threading,json
from flask import g,request,has_request_context
from sqlalchemy import event,func
from .models import SignalDefinition,Reading,Location,Alarm
_lock=threading.Lock()
_due=0.0
_running=False

def preload_dashboard(customer_id,devices):
    from . import db
    g.dashboard_devices={}
    for device in devices:g.dashboard_devices.setdefault(device.asset_id,device)
    signals=SignalDefinition.query.filter_by(customer_id=customer_id,enabled=True).all()
    g.dashboard_signals={}
    for sig in signals:g.dashboard_signals.setdefault(sig.asset_id,[]).append(sig)
    ranked=db.session.query(Reading.id.label('id'),func.row_number().over(partition_by=Reading.signal_id,order_by=(Reading.sampled_at.desc(),Reading.id.desc())).label('rn')).filter(Reading.customer_id==customer_id).subquery()
    g.dashboard_readings={row.signal_id:row for row in Reading.query.join(ranked,Reading.id==ranked.c.id).filter(ranked.c.rn==1).all()}
    ranked=db.session.query(Location.id.label('id'),func.row_number().over(partition_by=Location.asset_id,order_by=(Location.sampled_at.desc(),Location.id.desc())).label('rn')).filter(Location.customer_id==customer_id).subquery()
    g.dashboard_locations={row.asset_id:row for row in Location.query.join(ranked,Location.id==ranked.c.id).filter(ranked.c.rn==1).all()}
    g.dashboard_alarms={}
    for alarm in Alarm.query.filter_by(customer_id=customer_id,state='OPEN').order_by(Alarm.severity.desc()).all():g.dashboard_alarms.setdefault(alarm.asset_id,alarm)

def install(app,db):
    @app.before_request
    def start():g.review_started=time.perf_counter();g.review_count=0;g.review_sql=0.0
    app.before_request_funcs[None].remove(start);app.before_request_funcs[None].insert(0,start)
    with app.app_context():engine=db.engine
    @event.listens_for(engine,'before_cursor_execute')
    def before(conn,cursor,statement,parameters,context,many):
        if has_request_context():context.review_start=time.perf_counter()
    @event.listens_for(engine,'after_cursor_execute')
    def after(conn,cursor,statement,parameters,context,many):
        if has_request_context() and hasattr(context,'review_start'):
            g.review_count=getattr(g,'review_count',0)+1;g.review_sql=getattr(g,'review_sql',0)+(time.perf_counter()-context.review_start)*1000
    @app.after_request
    def report(response):
        duration=(time.perf_counter()-getattr(g,'review_started',time.perf_counter()))*1000
        response.headers['X-AssetTrack-Build']='Reviewed-REV05'
        response.headers['X-AssetTrack-SQL-Count']=str(getattr(g,'review_count',0))
        response.headers['Server-Timing']=f'app;dur={duration:.1f}, sql;dur={getattr(g,"review_sql",0):.1f}'
        if request.path.startswith('/static/') and response.status_code in (200,304):response.headers['Cache-Control']='public, max-age=86400' if request.args.get('v') else 'public, max-age=300'
        if request.path.startswith('/api/v1/mobile/'):
            body=response.get_json(silent=True) if response.is_json else None
            known={'invalid_mobile_tracker_token','consent_inactive','subscription_inactive','device_identity_mismatch','sequence_required','invalid_location_payload','location_out_of_range','points_required','batch_too_large','rate_limit_exceeded'}
            error=body.get('error') if isinstance(body,dict) else None
            reason=error if isinstance(error,str) and error in known else 'accepted' if 200<=response.status_code<300 else 'http_rejected'
            if response.status_code==401:
                header=request.headers.get('Authorization','')
                if not header:reason='authorization_missing'
                elif not header.startswith('Bearer '):reason='authorization_format_invalid'
                else:
                    from .models import Device
                    try:
                        row=db.session.query(Device.active,Device.device_type).filter(Device.api_token==header[7:].strip()).first()
                        reason='token_not_found_in_current_database' if row is None else 'device_inactive' if not row.active else 'authentication_rejected'
                    except Exception:reason='diagnostic_lookup_unavailable'
            record={'endpoint':request.endpoint or 'unmatched_mobile','status':response.status_code,'reason':reason,'ms':round(duration,1)}
            if isinstance(body,dict):
                for key in ('accepted_count','duplicate_count','rejected_count'):
                    if isinstance(body.get(key),int):record[key]=body[key]
                rejected=body.get('rejected',[])
                if isinstance(rejected,list):record['point_reasons']=sorted({x.get('error') for x in rejected if isinstance(x,dict) and x.get('error') in {'invalid_point','device_identity_mismatch','sequence_required','invalid_location_payload','location_out_of_range','invalid_timestamp'}})
            app.logger.warning('MOBILE_REQUEST %s',json.dumps(record,separators=(',',':')))
        return response

def schedule(app):
    global _due,_running
    if os.getenv('SITE_MAINTENANCE_BACKGROUND','true').lower() not in ('true','1','yes'):return
    with _lock:
        if _running or time.monotonic()<_due:return
        _running=True;_due=time.monotonic()+3600
    def run():
        global _running
        try:
            with app.app_context():
                from .trend_cleanup import cleanup_due
                cleanup_due(force=False)
        except Exception:app.logger.warning('Background retention failed; inspect maintenance separately')
        finally:
            with _lock:_running=False
    threading.Thread(target=run,daemon=True).start()
