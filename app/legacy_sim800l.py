"""Signed HTTP-to-HTTPS bridge ingress for LILYGO T-Call SIM800L."""
import hashlib, hmac, os, time
from collections import defaultdict, deque
from flask import Blueprint, jsonify, request
from .models import Device
from .device_profiles import profile_for_device

bp=Blueprint("legacy_sim800l",__name__)
_BUCKETS=defaultdict(deque)
_MAX_BODY=32768
_EXPECTED_HOST="sim800-ingest.wykiesautomation.co.za"

def _enabled():
    return os.getenv("SIM800L_LEGACY_INGRESS_ENABLED","true").strip().lower() in {"1","true","yes","on"}

def _rate_ok(device_id):
    now=time.monotonic();bucket=_BUCKETS[int(device_id)]
    while bucket and now-bucket[0]>60:bucket.popleft()
    if len(bucket)>=12:return False
    bucket.append(now);return True

def _digests(token,raw):
    secret=token.encode("utf-8")
    return (
        hashlib.sha256(secret+b"|"+raw+b"|"+secret).hexdigest(),
        hashlib.sha256(secret+raw+secret).hexdigest(),
    )

def _trusted_bridge():
    expected=os.getenv("SIM800L_BRIDGE_SECRET","").strip()
    supplied=(request.headers.get("X-AT360-Bridge-Secret") or "").strip()
    marker=(request.headers.get("X-AT360-Bridge") or "").strip().lower()
    return bool(expected and marker=="cloudflare-sim800l-v1" and hmac.compare_digest(expected,supplied))

@bp.post("/api/v1/sim800l-legacy-ingest")
def sim800l_legacy_ingest():
    if not _enabled():return jsonify(error="sim800l_ingress_disabled"),404
    required=os.getenv("SIM800L_LEGACY_HOST",_EXPECTED_HOST).strip().lower()
    direct_host=request.host.split(":",1)[0].lower()
    original=(request.headers.get("X-AT360-Original-Host") or "").split(":",1)[0].strip().lower()
    if direct_host!=required and not (_trusted_bridge() and original==required):
        return jsonify(error="sim800l_host_required"),421
    length=request.content_length or 0
    if length<=0 or length>_MAX_BODY:return jsonify(error="invalid_content_length",maximum_bytes=_MAX_BODY),413
    raw=request.get_data(cache=True);payload=request.get_json(silent=True) or {}
    uid=str(payload.get("device_uid") or payload.get("device_id") or request.headers.get("X-Device-UID") or "").strip().upper()
    seq=str(payload.get("sequence") or "").strip()
    supplied=(request.headers.get("X-AT360-Signature") or "").strip().lower()
    if not uid or not seq or len(seq)>80 or len(supplied)!=64:return jsonify(error="signed_device_sequence_required"),400
    device=Device.query.filter_by(device_uid=uid,active=True).first()
    profile=profile_for_device(device) if device else None
    if not device or not profile or profile.get("code")!="AT360_LILYGO_TCALL_SIM800L":return jsonify(error="unauthorized_sim800l_device"),401
    if not _rate_ok(device.id):return jsonify(error="sim800l_rate_limit",retry_after_seconds=60),429
    if not any(hmac.compare_digest(candidate,supplied) for candidate in _digests(device.api_token,raw)):
        return jsonify(error="invalid_signature"),401
    request.environ["HTTP_AUTHORIZATION"]="Bearer "+device.api_token
    request.environ["HTTP_X_DEVICE_TOKEN"]=device.api_token
    from .device_api import telemetry
    response=telemetry()
    try:
        target=response[0] if isinstance(response,tuple) else response
        target.headers["X-AT360-Legacy-Ingress"]="sim800l-signed-http-v2"
    except Exception:pass
    return response
