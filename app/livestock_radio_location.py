import math
import statistics
from datetime import timedelta
from .models import LivestockGateway,LivestockTagReception,LivestockRadioCalibration

MAX_GATEWAYS=12
MIN_GATEWAYS=3
LIVE_WINDOW_SECONDS=120

def haversine(lat1,lon1,lat2,lon2):
    radius=6371000.0;p1=math.radians(lat1);p2=math.radians(lat2)
    dp=math.radians(lat2-lat1);dl=math.radians(lon2-lon1)
    value=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*radius*math.asin(math.sqrt(value))

def _median(values):
    clean=[float(value) for value in values if value is not None]
    return statistics.median(clean) if clean else None

def _calibration_curve(gateway_id,terrain=None):
    query=LivestockRadioCalibration.query.filter_by(gateway_id=gateway_id)
    points=query.filter_by(terrain=terrain).all() if terrain else query.all()
    if not points:return []
    grouped={}
    for point in points:grouped.setdefault(int(point.distance_m),[]).append(point)
    curve=[]
    for distance,group in grouped.items():
        rssi=_median([point.median_rssi for point in group])
        snr=_median([point.median_snr for point in group])
        minimum=_median([point.min_rssi for point in group])
        maximum=_median([point.max_rssi for point in group])
        samples=sum(max(1,int(point.sample_count or 1)) for point in group)
        spread=max(2.0,abs((maximum if maximum is not None else rssi)-(minimum if minimum is not None else rssi))/2.0)
        curve.append({'distance':float(distance),'rssi':float(rssi),'snr':snr,'spread':spread,'samples':samples})
    curve.sort(key=lambda row:row['distance'])
    return curve

def calibrated_distance_band(gateway_id,rssi,snr=None,terrain=None):
    curve=_calibration_curve(gateway_id,terrain)
    if len(curve)<2:return None
    reading=float(rssi)
    segments=list(zip(curve[:-1],curve[1:]));segment=None
    for first,second in segments:
        low=min(first['rssi'],second['rssi']);high=max(first['rssi'],second['rssi'])
        if low<=reading<=high:segment=(first,second);break
    if segment is None:segment=segments[0] if reading>=curve[0]['rssi'] else segments[-1]
    first,second=segment;delta=second['rssi']-first['rssi']
    ratio=0.5 if abs(delta)<0.1 else (reading-first['rssi'])/delta
    distance=max(10.0,min(10000.0,first['distance']+ratio*(second['distance']-first['distance'])))
    metres_per_db=abs((second['distance']-first['distance'])/delta) if abs(delta)>=0.1 else max(first['distance'],second['distance'])*0.25
    rssi_spread=max(first['spread'],second['spread'])
    sigma=max(35.0,min(2500.0,metres_per_db*rssi_spread))
    sample_quality=min(1.0,math.sqrt(max(1,min(first['samples'],second['samples']))/30.0))
    snr_quality=1.0 if snr is None else max(0.15,min(1.0,(float(snr)+12.0)/22.0))
    quality=max(0.05,min(1.0,sample_quality*snr_quality*(120.0/(120.0+sigma))))
    return {'distance_m':distance,'sigma_m':sigma,'quality':quality,'curve_points':len(curve)}

def _to_xy(lat,lon,lat0,lon0):
    return ((lon-lon0)*111320.0*math.cos(math.radians(lat0)),(lat-lat0)*111320.0)

def _to_latlon(x,y,lat0,lon0):
    return (lat0+y/111320.0,lon0+x/(111320.0*math.cos(math.radians(lat0))))

def _huber(value,delta=1.5):
    absolute=abs(value)
    return 0.5*value*value if absolute<=delta else delta*(absolute-0.5*delta)

def _geometry_score(anchors):
    if len(anchors)<3:return 0.0
    xs=[row['x'] for row in anchors];ys=[row['y'] for row in anchors]
    span=max(max(xs)-min(xs),max(ys)-min(ys),1.0)
    cx=sum(xs)/len(xs);cy=sum(ys)/len(ys)
    angles=sorted(math.atan2(row['y']-cy,row['x']-cx)%(2*math.pi) for row in anchors)
    gaps=[angles[index+1]-angles[index] for index in range(len(angles)-1)]+[(angles[0]+2*math.pi)-angles[-1]]
    angular=max(0.0,1.0-max(gaps)/(2*math.pi))
    area=0.0
    ordered=sorted(((row['x'],row['y']) for row in anchors),key=lambda point:math.atan2(point[1]-cy,point[0]-cx))
    for index,(x1,y1) in enumerate(ordered):
        x2,y2=ordered[(index+1)%len(ordered)];area+=x1*y2-x2*y1
    area_score=min(1.0,abs(area)/2.0/(span*span*0.45))
    return max(0.0,min(1.0,0.55*angular+0.45*area_score))

def _solve(anchors):
    xs=[row['x'] for row in anchors];ys=[row['y'] for row in anchors];maximum=max(row['distance'] for row in anchors)
    minx,maxx=min(xs)-maximum,max(xs)+maximum;miny,maxy=min(ys)-maximum,max(ys)+maximum;best=None
    for resolution in (33,29,25,21):
        stepx=(maxx-minx)/max(1,resolution-1);stepy=(maxy-miny)/max(1,resolution-1)
        for ix in range(resolution):
            x=minx+ix*stepx
            for iy in range(resolution):
                y=miny+iy*stepy;cost=0.0;residuals=[]
                for row in anchors:
                    error=math.hypot(x-row['x'],y-row['y'])-row['distance']
                    normalised=error/max(35.0,row['sigma']);cost+=row['weight']*_huber(normalised);residuals.append(error)
                if best is None or cost<best[0]:best=(cost,x,y,residuals)
        _,bx,by,_=best;spanx=max(stepx*3.5,50.0);spany=max(stepy*3.5,50.0);minx,maxx=bx-spanx,bx+spanx;miny,maxy=by-spany,by+spany
    return best

def _recent_gateway_medians(animal,current,window_seconds):
    start=current-timedelta(seconds=window_seconds)
    rows=LivestockTagReception.query.filter(LivestockTagReception.animal_id==animal.id,LivestockTagReception.received_at>=start).order_by(LivestockTagReception.received_at.desc()).all()
    grouped={}
    for row in rows:grouped.setdefault(row.gateway_id,[]).append(row)
    result=[]
    for gateway_id,samples in grouped.items():
        result.append({'gateway_id':gateway_id,'rssi':_median([row.rssi for row in samples]),'snr':_median([row.snr for row in samples]),'sample_count':len(samples),'latest':max(row.received_at for row in samples)})
    return result

def estimate_animal(animal,current,window_seconds=LIVE_WINDOW_SECONDS):
    readings=_recent_gateway_medians(animal,current,window_seconds);fixes=[]
    for reading in readings:
        gateway=LivestockGateway.query.filter_by(id=reading['gateway_id'],customer_id=animal.customer_id,farm_id=animal.farm_id,active=True).first()
        band=calibrated_distance_band(reading['gateway_id'],reading['rssi'],reading['snr'])
        if not gateway or not band:continue
        age=max(0.0,(current-reading['latest']).total_seconds());age_quality=max(0.15,1.0-age/max(window_seconds,1))
        repeat_quality=min(1.0,math.sqrt(reading['sample_count']/5.0));quality=band['quality']*age_quality*repeat_quality
        fixes.append({'gateway':gateway,'distance':band['distance_m'],'sigma':band['sigma_m'],'quality':quality,'rssi':reading['rssi'],'snr':reading['snr'],'samples':reading['sample_count']})
    fixes=sorted(fixes,key=lambda row:row['quality'],reverse=True)[:MAX_GATEWAYS]
    if len(fixes)<MIN_GATEWAYS:
        animal.estimated_lat=None;animal.estimated_lon=None;animal.estimated_radius_m=None;animal.location_confidence='INSUFFICIENT';animal.location_gateway_count=len(fixes);animal.location_estimated_at=current
        return None
    lat0=sum(row['gateway'].latitude for row in fixes)/len(fixes);lon0=sum(row['gateway'].longitude for row in fixes)/len(fixes);anchors=[]
    for row in fixes:
        x,y=_to_xy(row['gateway'].latitude,row['gateway'].longitude,lat0,lon0);anchors.append({**row,'x':x,'y':y,'weight':max(0.05,row['quality'])})
    best=_solve(anchors)
    # Robust outlier rejection: remove at most two contradictory gateways while retaining >=3.
    removed=[]
    while len(anchors)>3 and len(removed)<2:
        _,_,_,residuals=best;normalised=[abs(error)/max(35.0,row['sigma']) for error,row in zip(residuals,anchors)];worst=max(range(len(normalised)),key=normalised.__getitem__)
        if normalised[worst]<=3.0:break
        removed.append(anchors.pop(worst));best=_solve(anchors)
    _,x,y,residuals=best;lat,lon=_to_latlon(x,y,lat0,lon0);geometry=_geometry_score(anchors)
    weighted=sum(row['weight']*(error**2) for row,error in zip(anchors,residuals))/max(0.001,sum(row['weight'] for row in anchors));rms=math.sqrt(weighted)
    sigma_floor=statistics.median(row['sigma'] for row in anchors);geometry_penalty=(1.0-geometry)*max(150.0,sigma_floor)
    radius=int(max(75.0,min(3000.0,rms+0.6*sigma_floor+geometry_penalty)))
    count=len(anchors);confidence='HIGH' if count>=4 and radius<=250 and geometry>=0.55 else 'MEDIUM' if count>=3 and radius<=800 and geometry>=0.25 else 'LOW'
    animal.estimated_lat=lat;animal.estimated_lon=lon;animal.estimated_radius_m=radius;animal.location_confidence=confidence;animal.location_gateway_count=count;animal.location_estimated_at=current
    return {'lat':lat,'lon':lon,'radius_m':radius,'confidence':confidence,'gateway_count':count,'geometry_score':round(geometry,3),'rms_error_m':round(rms),'outliers_removed':[row['gateway'].id for row in removed],'fixes':[{'gateway_id':row['gateway'].id,'distance_m':round(row['distance']),'sigma_m':round(row['sigma']),'rssi':round(row['rssi'],1),'snr':None if row['snr'] is None else round(row['snr'],1),'samples':row['samples'],'quality':round(row['quality'],3)} for row in anchors]}
