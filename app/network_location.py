"""Estimated GSM location; never writes GPS Location, speed, trips or geofences."""
import os,re,json,math,hashlib
from datetime import datetime,timezone,timedelta
import urllib.request,urllib.error

def parse_cells(observations):
    if not isinstance(observations,dict):return []
    try:age=int(observations.get('age_ms',999999))
    except (ValueError,TypeError):return []
    if not 0<=age<=300000:return []
    reg=str(observations.get('registration_raw',''))[:6000]
    operator=str(observations.get('operator_raw',''))[:6000]
    m=re.search(r'\+CREG:\s*\d+\s*,\s*([15])\s*,\s*"([0-9a-fA-F]{1,4})"\s*,\s*"([0-9a-fA-F]{1,4})"',reg)
    op=re.search(r'\+COPS:\s*\d+\s*,\s*2\s*,\s*"(\d{5,6})"',operator)
    cells=[]
    if m and op:
        plmn=op.group(1)
        cells.append({'cellId':int(m.group(3),16),'locationAreaCode':int(m.group(2),16),'mobileCountryCode':int(plmn[:3]),'mobileNetworkCode':int(plmn[3:])})
    # Named CNETSCAN fields only; ambiguous/unrecognised formats are not guessed.
    for line in str(observations.get('scan_raw',''))[:6000].splitlines():
        pairs={k.lower():v for k,v in re.findall(r'\b(MCC|MNC|Lac|Cellid):\s*"?([0-9a-fA-F]+)',line,re.I)}
        if len(pairs)!=4:continue
        try:c={'cellId':int(pairs['cellid'],16),'locationAreaCode':int(pairs['lac'],16),'mobileCountryCode':int(pairs['mcc'],10),'mobileNetworkCode':int(pairs['mnc'],10)}
        except ValueError:continue
        if c not in cells:cells.append(c)
    return [c for c in cells if 0<c['cellId']<=65535 and 0<=c['locationAreaCode']<=65535 and 0<c['mobileCountryCode']<=999 and 0<=c['mobileNetworkCode']<=999][:12]

def validated_position(data):
    try:
        lat=float(data['location']['lat']);lon=float(data['location']['lng']);radius=float(data['accuracy'])
    except (KeyError,ValueError,TypeError):return None
    if not all(math.isfinite(x) for x in (lat,lon,radius)) or not -90<=lat<=90 or not -180<=lon<=180 or not 0<radius<=100000:return None
    return {'latitude':lat,'longitude':lon,'accuracy_m':radius,'source':'CELL_NETWORK_ESTIMATE'}

def update_estimate(asset,device,payload,current):
    meta=dict(asset.metadata_json or {});states=dict(meta.get('network_location_devices') or {})
    state=dict(states.get(device.device_uid) or {});cells=parse_cells(payload.get('network_observations'))
    state.update(cell_count=len(cells),cells=cells,observed_at=current.isoformat())
    enabled=bool((meta.get('network_location_consent') or {}).get(device.device_uid))
    if str(payload.get('mode','')).upper()!='LIVE':state['status']='LIVE_MODE_REQUIRED'
    elif not enabled:state['status']='CONSENT_REQUIRED'
    elif not cells:state['status']='WAITING_FOR_CELL_DATA'
    elif not os.environ.get('AT360_GEOLOCATION_API_KEY'):state['status']='PROVIDER_KEY_REQUIRED'
    else:
        fingerprint=hashlib.sha256(json.dumps(cells,sort_keys=True).encode()).hexdigest()
        try:last=datetime.fromisoformat(state.get('lookup_at','')).astimezone(timezone.utc)
        except (ValueError,TypeError):last=current-timedelta(days=1)
        # Persistent throttle: at most one lookup per device per 5 minutes.
        if current-last>=timedelta(minutes=5):
            state.update(lookup_at=current.isoformat(),fingerprint=fingerprint,status='LOOKUP_FAILED')
            body=json.dumps({'radioType':'gsm','considerIp':False,'cellTowers':cells}).encode()
            from urllib.parse import urlencode
            url='https://www.googleapis.com/geolocation/v1/geolocate?'+urlencode({'key':os.environ['AT360_GEOLOCATION_API_KEY']})
            try:
                req=urllib.request.Request(url,data=body,headers={'Content-Type':'application/json'},method='POST')
                with urllib.request.urlopen(req,timeout=4) as response:data=json.loads(response.read(65536))
                position=validated_position(data)
                if position:state.update(position=position,position_at=current.isoformat(),status='ESTIMATED')
                else:state['status']='INVALID_PROVIDER_RESULT'
            except urllib.error.HTTPError as exc:state['status']='PROVIDER_HTTP_'+str(exc.code)
            except Exception:state['status']='PROVIDER_UNAVAILABLE'
    states[device.device_uid]=state;meta['network_location_devices']=states;asset.metadata_json=meta
    return state['status']
