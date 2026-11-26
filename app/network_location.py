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

def validated_position(data,cell=None):
    if not isinstance(data,dict) or data.get('error') or data.get('code'):return None
    try:
        lat=float(data['lat']);lon=float(data['lon'])
        if not math.isfinite(lat) or not math.isfinite(lon) or not -90<=lat<=90 or not -180<=lon<=180:return None
        if cell:
            for name,key in [('mcc','mobileCountryCode'),('mnc','mobileNetworkCode'),('lac','locationAreaCode'),('cellid','cellId')]:
                if int(data[name])!=cell[key]:return None
    except (KeyError,ValueError,TypeError,OverflowError):return None
    try:radius=float(data.get('range',0))
    except (ValueError,TypeError):radius=0
    if not math.isfinite(radius) or not 0<radius<=100000:radius=None
    return {'latitude':lat,'longitude':lon,'accuracy_m':radius,'source':'OPENCELLID_CELL_ESTIMATE','provider':'OpenCellID'}

def lookup_cell(cell,key):
    from urllib.parse import urlencode
    params={'key':key,'mcc':cell['mobileCountryCode'],'mnc':cell['mobileNetworkCode'],'lac':cell['locationAreaCode'],'cellid':cell['cellId'],'radio':'GSM','format':'json'}
    req=urllib.request.Request('https://opencellid.org/cell/get?'+urlencode(params),headers={'Accept':'application/json','User-Agent':'AssetTrack360/Network-REV09'})
    try:
        with urllib.request.urlopen(req,timeout=4) as response:data=json.loads(response.read(65536))
        if not isinstance(data,dict):return None,'INVALID_PROVIDER_RESULT'
        try:code=int(data.get('code',0))
        except (ValueError,TypeError):code=-1
        if code or data.get('error'):return None,{1:'CELL_NOT_FOUND',2:'PROVIDER_KEY_INVALID',3:'INVALID_CELL_DATA',7:'PROVIDER_QUOTA_EXCEEDED'}.get(code,'PROVIDER_ERROR')
        position=validated_position(data,cell)
        return position,'ESTIMATED_CELL_LOCATION' if position else 'INVALID_PROVIDER_RESULT'
    except urllib.error.HTTPError as exc:return None,{401:'PROVIDER_KEY_INVALID',403:'PROVIDER_ACCESS_DENIED',429:'PROVIDER_QUOTA_EXCEEDED'}.get(exc.code,'PROVIDER_HTTP_'+str(exc.code))
    except Exception:return None,'PROVIDER_UNAVAILABLE'

def update_estimate(asset,device,payload,current):
    meta=dict(asset.metadata_json or {});states=dict(meta.get('network_location_devices') or {});state=dict(states.get(device.device_uid) or {})
    cells=parse_cells(payload.get('network_observations'))
    if state.get('provider')!='OpenCellID':
        for name in ('position','position_at','lookup_at','fingerprint'):state.pop(name,None)
    state['provider']='OpenCellID'
    enabled=bool((meta.get('network_location_consent') or {}).get(device.device_uid))
    if cells:state.update(cell_count=len(cells),cells=cells,observed_at=current.isoformat())
    key=os.environ.get('AT360_OPENCELLID_API_KEY','').strip()
    if str(payload.get('mode','')).upper()!='LIVE':state['status']='LIVE_MODE_REQUIRED'
    elif not enabled:
        state['status']='CONSENT_REQUIRED';state.pop('position',None);state.pop('position_at',None)
    elif not cells:state['status']='WAITING_FOR_CELL_DATA'
    elif not key:state['status']='PROVIDER_KEY_REQUIRED'
    else:
        cell=cells[0];fingerprint=hashlib.sha256(json.dumps(cell,sort_keys=True).encode()).hexdigest()
        try:last=datetime.fromisoformat(state.get('lookup_at','')).astimezone(timezone.utc)
        except (ValueError,TypeError):last=current-timedelta(days=1)
        age=(current-last).total_seconds()
        if state.get('fingerprint')==fingerprint and state.get('position') and state.get('matched_cell')==cell and age<86400:state['status']='CACHED_CELL_LOCATION'
        elif age>=300:
            state.update(lookup_at=current.isoformat(),fingerprint=fingerprint)
            position,status=lookup_cell(cell,key);state['status']=status
            if position:state.update(position=position,position_at=current.isoformat(),matched_cell=cell)
        else:state['status']='LOOKUP_COOLDOWN'
    states[device.device_uid]=state;meta['network_location_devices']=states;asset.metadata_json=meta
    return state['status']
