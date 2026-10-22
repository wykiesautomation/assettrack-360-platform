"""Explicit owner-reviewed SIM800L profile repair. No UID/token rotation."""
import hashlib,hmac,re,secrets
from datetime import datetime,timezone
from flask import Blueprint,abort,request,session,render_template,flash,redirect,url_for
from flask_login import login_required,current_user
from . import db
from .models import Device,DeviceChannelAssignment,HardwareDeviceRegistration,MobileTrackerRegistration
from .device_profiles import get_profile,profile_for_device
from .admin import log
bp=Blueprint('profile_repair',__name__)
TARGET='AT360_LILYGO_TCALL_SIM800L'
OLD='AT360_LILYGO_TSIM7000G'
def physical_candidates(uid):
    match=re.fullmatch(r'AT360-LILYGO-([0-9A-F]{12})',str(uid).upper())
    if not match:raise ValueError('Use the physical HARDWARE_UID from READ_ALL, not IMEI or stored Device UID.')
    suffix=match.group(1)
    return ('AT360-LILYGO-'+suffix,'AT360-LILYGO-AT360LILYGO'+suffix)
def repair_device(device,physical_uid,firmware):
    candidates=physical_candidates(physical_uid)
    if device.device_uid not in candidates:raise ValueError('Physical UID does not match the selected device.')
    if Device.query.filter(Device.device_uid.in_(candidates),Device.id!=device.id).first():raise ValueError('Another device has the same physical identity. Review duplicates first.')
    if not re.fullmatch(r'AT360_LILYGO_TCALL_IO_REV[0-9]+',firmware):raise ValueError('Exact T-Call firmware identity from READ_ALL required.')
    old=(profile_for_device(device) or {}).get('code')
    if old not in (OLD,TARGET):raise ValueError('Only SIM7000G/SIM800L profile correction is allowed here.')
    if not device.active:raise ValueError('Device must be active.')
    if device.asset and device.asset.customer_id!=device.customer_id:raise ValueError('Asset tenant mismatch.')
    profile=get_profile(TARGET);allowed={x['key'] for x in profile['channels']}
    rows=DeviceChannelAssignment.query.filter_by(device_id=device.id).all()
    if any(x.customer_id!=device.customer_id for x in rows):raise ValueError('Assignment tenant mismatch.')
    if any(x.enabled and x.channel_key not in allowed for x in rows):raise ValueError('Enabled incompatible assignments require review before profile repair.')
    # Preserve UID, token, asset, readings and all assignment rows.
    device.device_type=profile['device_type'];device.firmware=firmware
    device.capabilities=list(dict.fromkeys(profile['capabilities']+['PROFILE:'+TARGET]))
    for spec in profile['channels']:
        row=next((x for x in rows if x.channel_key==spec['key']),None)
        if not row:
            row=DeviceChannelAssignment(customer_id=device.customer_id,device_id=device.id,channel_key=spec['key'],direction=spec.get('direction','HEALTH'),purpose='UNUSED',enabled=False,customer_label=spec['label'],config_json={});db.session.add(row)
        cfg=dict(row.config_json or {});cfg.update(profile_code=TARGET,physical_pin=spec.get('pin'),pin_notes=spec.get('pin_notes'));row.config_json=cfg
    return old
@bp.route('/platform-admin/sim800l-profile-repair',methods=['GET','POST'])
@login_required
def page():
    if current_user.role!='platform_admin':abort(403)
    if 'profile_repair_csrf' not in session:session['profile_repair_csrf']=secrets.token_urlsafe(32)
    if request.method=='POST':
        if not hmac.compare_digest(str(request.form.get('csrf','')),session['profile_repair_csrf']):abort(403)
        if request.form.get('confirm')!='SIM800L':abort(400)
        try:
            if request.form.get('action')=='device':
                device=Device.query.filter_by(id=request.form.get('device_id',type=int)).with_for_update().first_or_404()
                old=repair_device(device,request.form.get('hardware_uid','').strip().upper(),request.form.get('firmware','').strip())
                log('SIM800L_DEVICE_PROFILE_REPAIRED',device.customer_id,f'device={device.id}; old={old}; UID/token/history preserved')
                db.session.commit();flash('Device profile repaired. Existing UID and token preserved. Do NOT claim this device again. Test its existing upload.','ok')
            elif request.form.get('action')=='claim':
                code=request.form.get('claim_code','').strip().upper()
                if not re.fullmatch(r'[0-9A-F]{4}-[0-9A-F]{4}',code):raise ValueError('Valid one-time code required.')
                digest=hashlib.sha256(code.encode()).hexdigest()
                regs=[]
                for model in (HardwareDeviceRegistration,MobileTrackerRegistration):
                    regs+=model.query.filter_by(code_hash=digest).with_for_update().all()
                if len(regs)!=1:raise ValueError('Code missing or ambiguous. Generate a fresh SIM800L code.')
                reg=regs[0]
                if reg.customer_id!=request.form.get('customer_id',type=int):raise ValueError('Customer mismatch.')
                if reg.provisioning_state!='WAITING' or getattr(reg,'used_at',None) or getattr(reg,'claimed_at',None):raise ValueError('Only unused WAITING codes can be repaired.')
                expires=reg.expires_at.replace(tzinfo=reg.expires_at.tzinfo or timezone.utc)
                if datetime.now(timezone.utc)>expires:raise ValueError('Code expired. Generate a fresh SIM800L code; expiry is not extended.')
                if reg.profile_code!=OLD:raise ValueError('Only a SIM7000G code can be explicitly corrected here.')
                reg.profile_code=TARGET
                log('SIM800L_UNUSED_CLAIM_PROFILE_REPAIRED',reg.customer_id,f'registration={reg.id}; expiry unchanged; no device created')
                db.session.commit();flash('Unused code corrected to SIM800L. This did not register a device. Do not use it to re-claim an existing device.','ok')
            else:abort(400)
        except ValueError as exc:db.session.rollback();flash(str(exc),'error')
        except Exception:db.session.rollback();flash('Repair rolled back safely. Review server logs.','error')
        return redirect(url_for('profile_repair.page'))
    devices=Device.query.filter(Device.device_type.in_(['LILYGO_T_SIM7000G_TRACKER','LILYGO_TCALL_SIM800L_IO'])).order_by(Device.id).all()
    prefill_uid=request.args.get('hardware_uid','').strip().upper()
    prefill_fw=request.args.get('firmware','').strip()
    selected_id=None
    if prefill_uid or prefill_fw:
        try:
            candidates=physical_candidates(prefill_uid)
            if not re.fullmatch(r'AT360_LILYGO_TCALL_IO_REV[0-9]+',prefill_fw):raise ValueError('Invalid firmware readback.')
            matches=[d for d in devices if d.device_uid in candidates]
            if len(matches)!=1:raise ValueError('Physical readback must match exactly one existing device. Review missing/duplicate records.')
            selected_id=matches[0].id
        except ValueError as exc:
            flash(str(exc),'error');prefill_uid='';prefill_fw=''
    return render_template('sim800l_profile_repair.html',devices=devices,csrf=session['profile_repair_csrf'],prefill_uid=prefill_uid,prefill_fw=prefill_fw,selected_id=selected_id)
