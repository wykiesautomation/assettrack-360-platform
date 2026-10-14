"""Site response instrumentation and independent retention scheduling.
No authenticated HTML cache; no shared user or tenant cache.
"""
import os,threading,time
from flask import g,request,has_request_context
from sqlalchemy import event
_lock=threading.Lock()
_running=False
_next_check=0.0

def schedule_retention(app):
    global _running,_next_check
    if os.getenv('SITE_MAINTENANCE_BACKGROUND','true').lower() not in ('1','true','yes'):return
    with _lock:
        if _running or time.monotonic()<_next_check:return
        _running=True;_next_check=time.monotonic()+3600
    def run():
        global _running
        try:
            with app.app_context():
                from .trend_cleanup import cleanup_due
                cleanup_due(force=False)
        except Exception:app.logger.exception('Background retention failed; web requests remain independent')
        finally:
            with _lock:_running=False
    threading.Thread(target=run,name='at360-site-maintenance',daemon=True).start()

def install_performance_hooks(app,db):
    @app.before_request
    def begin():
        g.site_started=time.perf_counter();g.site_sql_count=0;g.site_sql_ms=0.0
    # Measure the whole request, including earlier registered access hooks.
    app.before_request_funcs[None].remove(begin)
    app.before_request_funcs[None].insert(0,begin)
    with app.app_context():engine=db.engine
    @event.listens_for(engine,'before_cursor_execute')
    def before_sql(conn,cursor,statement,parameters,context,executemany):
        if has_request_context():context.at360_started=time.perf_counter()
    @event.listens_for(engine,'after_cursor_execute')
    def after_sql(conn,cursor,statement,parameters,context,executemany):
        if has_request_context():
            started=getattr(context,'at360_started',None)
            if started is not None:
                g.site_sql_count=getattr(g,'site_sql_count',0)+1
                g.site_sql_ms=getattr(g,'site_sql_ms',0.0)+(time.perf_counter()-started)*1000
    @app.before_request
    def maintenance():
        if not request.path.startswith('/static/') and request.endpoint!='main.health':schedule_retention(app)
    @app.after_request
    def report(response):
        started=getattr(g,'site_started',None)
        if started is not None:
            elapsed=(time.perf_counter()-started)*1000
            response.headers['Server-Timing']=f'app;dur={elapsed:.1f}, sql;dur={getattr(g,"site_sql_ms",0):.1f}'
            response.headers['X-AssetTrack-Build']='SiteResponse-REV02'
            response.headers['X-AssetTrack-SQL-Count']=str(getattr(g,'site_sql_count',0))
            if elapsed>=1000:app.logger.warning('Slow page method=%s path=%s status=%s ms=%.0f sql_count=%s sql_ms=%.0f',request.method,request.path,response.status_code,elapsed,getattr(g,'site_sql_count',0),getattr(g,'site_sql_ms',0))
        if request.path.startswith('/static/') and response.status_code in (200,304):
            # Versioned CSS/JS may be reused; HTML remains private/no-store.
            if request.args.get('v') and request.path.endswith(('.css','.js')):
                response.headers['Cache-Control']='public, max-age=86400'
            else:response.headers['Cache-Control']='public, max-age=300'
        return response
