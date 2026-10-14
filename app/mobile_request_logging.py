"""Allowlisted mobile diagnostics. Never logs headers, payloads or token values."""
import json,os,time,uuid
from flask import g,request
ALLOWED_ERRORS=frozenset({
 'invalid_mobile_tracker_token','consent_inactive','subscription_inactive',
 'device_identity_mismatch','rate_limit_exceeded','request_too_large',
 'invalid_battery_percent','points_required','batch_too_large',
 'invalid_location_payload','invalid_motion_samples','samples_required',
 'registration_code_invalid','registration_code_expired'})
MOBILE_TYPES={'MOBILE_WEB_TRACKER','ANDROID_MOBILE_TRACKER','IOS_MOBILE_TRACKER','MOBILE_TRACKER'}
def remember_device(device):
    if device is not None:g.mobile_log_device=(device.id,device.asset_id)
    return device

def rejection_reason(db):
    header=request.headers.get('Authorization','')
    if not header:return 'authorization_missing'
    # Diagnose the existing parser; do not change authentication semantics.
    token=header.removeprefix('Bearer ').strip()
    if not token:return 'token_empty'
    if not header.startswith('Bearer '):return 'authorization_format_invalid'
    from .models import Device
    try:
        row=db.session.query(Device.id,Device.active,Device.device_type).filter(Device.api_token==token).first()
        if not row:return 'token_not_found_in_current_database'
        if not row.active:return 'device_inactive'
        if request.endpoint and request.endpoint.startswith('main.') and row.device_type not in MOBILE_TYPES:return 'device_type_not_mobile'
        return 'authentication_rejected_other'
    except Exception:
        # No exception text: drivers can include parameters or connection details.
        return 'diagnostic_lookup_unavailable'

def install_mobile_logging(app,db):
    @app.before_request
    def begin_mobile_log():
        if request.path.startswith('/api/v1/mobile/'):
            g.mobile_log_started=time.perf_counter();g.mobile_log_id=uuid.uuid4().hex[:16]
    app.before_request_funcs[None].remove(begin_mobile_log)
    app.before_request_funcs[None].insert(0,begin_mobile_log)
    @app.after_request
    def log_mobile_response(response):
        if not request.path.startswith('/api/v1/mobile/'):return response
        if os.getenv('MOBILE_REQUEST_LOGGING','true').lower() not in ('1','true','yes'):return response
        try:
            body=response.get_json(silent=True) if response.is_json else None
            error=body.get('error') if isinstance(body,dict) else None
            reason='accepted' if 200<=response.status_code<300 else 'http_rejected'
            if response.status_code==401:reason=rejection_reason(db)
            elif error in ALLOWED_ERRORS:reason=error
            elif response.status_code>=500:reason='server_error'
            record={'event':'mobile_request','request_id':getattr(g,'mobile_log_id',uuid.uuid4().hex[:16]),
                    'method':request.method,'endpoint':request.endpoint or 'unmatched_mobile_route',
                    'status':response.status_code,'reason':reason,
                    'duration_ms':round((time.perf_counter()-getattr(g,'mobile_log_started',time.perf_counter()))*1000,1)}
            if error in ALLOWED_ERRORS:record['error_code']=error
            identity=getattr(g,'mobile_log_device',None)
            if identity:record['device_id'],record['asset_id']=identity
            response.headers['X-AssetTrack-Request-ID']=record['request_id']
            response.headers['X-AssetTrack-Mobile-Logging']='REV03'
            # WARNING ensures fast successes and fast rejections appear in deploy logs.
            app.logger.warning('MOBILE_REQUEST %s',json.dumps(record,separators=(',',':')))
        except Exception:
            app.logger.warning('MOBILE_REQUEST diagnostic_failed status=%s',response.status_code)
        return response
