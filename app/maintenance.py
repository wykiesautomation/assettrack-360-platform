"""Run retention in an independent application context, never in page/ingest requests."""
import os,threading,time
_lock=threading.Lock()
_next_check=0.0
_running=False
def schedule_cleanup(app):
    global _next_check,_running
    if os.getenv('TREND_CLEANUP_BACKGROUND','true').lower() not in ('1','true','yes'):return
    with _lock:
        if _running or time.monotonic()<_next_check:return
        _running=True;_next_check=time.monotonic()+3600
    def run():
        global _running
        try:
            with app.app_context():
                from .trend_cleanup import cleanup_due
                cleanup_due(force=False)
        except Exception:app.logger.exception('Background retention failed; will retry later')
        finally:
            with _lock:_running=False
    threading.Thread(target=run,name='at360-retention',daemon=True).start()
