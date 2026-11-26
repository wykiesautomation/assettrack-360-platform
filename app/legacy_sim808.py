"""Isolated signed HTTP ingress for legacy SIM808 modem firmware."""
import hashlib, hmac, os, time
from collections import defaultdict, deque
from flask import Blueprint, jsonify, request
from .models import Device
bp=Blueprint("legacy_sim808",__name__);_BUCKETS=defaultdict(deque);_MAX_BODY=32768
def _enabled():return os.getenv("SIM808_LEGACY_INGRESS_ENABLED","false").strip().lower() in {"1","true","yes","on"}
def _rate_ok(device_id):
 now=time.monotonic();bucket=_BUCKETS[int(device_id)]
 while bucket and now-bucket[0]>60:bucket.popleft()
 if len(bucket)>=12:return False
 bucket.append(now);return True
def _signature(token,raw):
 secret=token.encode("utf-8");return hashlib.sha256(secret+b"|"+raw+b"|"+secret).hexdigest()
@bp.post("/api/v1/sim808-legacy-ingest")
def sim808_legacy_ingest():
 if not _enabled():return jsonify(error="legacy_ingress_disabled"),404
 required=os.getenv("SIM808_LEGACY_HOST","").strip().lower()
 if required and request.host.split(":",1)[0].lower()!=required:return jsonify(error="legacy_host_required"),421
 if (request.content_length or 0)<=0 or (request.content_length or 0)>_MAX_BODY:return jsonify(error="invalid_content_length",maximum_bytes=_MAX_BODY),413
 raw=request.get_data(cache=True);payload=request.get_json(silent=True) or {};uid=str(payload.get("device_id") or "").strip().upper();seq=str(payload.get("sequence") or "").strip();supplied=request.headers.get("X-AT360-Signature","").strip().lower()
 if not uid or not seq or len(seq)>80 or len(supplied)!=64:return jsonify(error="signed_device_sequence_required"),400
 device=Device.query.filter_by(device_uid=uid,active=True).first()
 if not device or str(device.device_type or "").upper() not in {"SIM808_GPS_TRACKER","SIM808_SAMD21"}:return jsonify(error="unauthorized_legacy_device"),401
 if not _rate_ok(device.id):return jsonify(error="legacy_rate_limit",retry_after_seconds=60),429
 if not hmac.compare_digest(_signature(device.api_token,raw),supplied):return jsonify(error="invalid_signature"),401
 request.environ["HTTP_AUTHORIZATION"]="Bearer "+device.api_token
 from .routes import ingest
 response=ingest()
 try:(response[0] if isinstance(response,tuple) else response).headers["X-AT360-Legacy-Ingress"]="signed-http-v1"
 except Exception:pass
 return response
