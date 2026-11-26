import math
from datetime import timedelta
from .models import LivestockGateway,LivestockTagReception,LivestockRadioCalibration

def haversine(lat1,lon1,lat2,lon2):
    r=6371000;p1=math.radians(lat1);p2=math.radians(lat2);dp=math.radians(lat2-lat1);dl=math.radians(lon2-lon1)
    a=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*r*math.asin(math.sqrt(a))

def calibrated_distance(gateway_id,rssi,terrain=None):
    query=LivestockRadioCalibration.query.filter_by(gateway_id=gateway_id)
    points=query.filter_by(terrain=terrain).all() if terrain else query.all()
    if not points:return None
    # Collapse duplicate direction rows at the same distance. Directional calibration
    # is stored for future models, while the current distance engine uses one curve.
    by_distance={}
    for point in points:by_distance.setdefault(point.distance_m,[]).append(point)
    curve=[]
    for distance,group in by_distance.items():
        rssi_values=sorted(float(p.median_rssi) for p in group)
        curve.append((float(distance),rssi_values[len(rssi_values)//2]))
    curve.sort(key=lambda item:item[0])
    if len(curve)==1:return curve[0][0]
    # RSSI normally weakens with distance. Find the adjacent RSSI segment that
    # brackets the reading; otherwise extrapolate from the nearest end segment.
    segments=list(zip(curve[:-1],curve[1:]))
    selected=None
    for a,b in segments:
        high=max(a[1],b[1]);low=min(a[1],b[1])
        if low<=float(rssi)<=high:selected=(a,b);break
    if selected is None:selected=segments[0] if float(rssi)>=curve[0][1] else segments[-1]
    (da,ra),(db,rb)=selected
    if abs(rb-ra)<0.1:return (da+db)/2
    ratio=(float(rssi)-ra)/(rb-ra)
    return max(10.0,min(10000.0,da+ratio*(db-da)))

def estimate_animal(animal,current,window_seconds=900):
    recent=LivestockTagReception.query.filter(LivestockTagReception.animal_id==animal.id,LivestockTagReception.received_at>=current-timedelta(seconds=window_seconds)).order_by(LivestockTagReception.received_at.desc()).all()
    latest={}
    for row in recent:
        if row.gateway_id not in latest:latest[row.gateway_id]=row
    fixes=[]
    for gateway_id,row in latest.items():
        gw=LivestockGateway.query.filter_by(id=gateway_id,customer_id=animal.customer_id,farm_id=animal.farm_id,active=True).first()
        distance=calibrated_distance(gateway_id,row.rssi)
        if gw and distance is not None:fixes.append((gw,distance,row.rssi))
    if not fixes:
        animal.estimated_lat=None;animal.estimated_lon=None;animal.estimated_radius_m=None;animal.location_confidence=None;animal.location_gateway_count=0;animal.location_estimated_at=current
        return None
    # Weighted-centroid radio estimate. This is an approximate search area, not GNSS.
    weights=[1/max(2500.0,d*d) for _,d,_ in fixes];total=sum(weights)
    lat=sum(g.latitude*w for (g,_,_),w in zip(fixes,weights))/total;lon=sum(g.longitude*w for (g,_,_),w in zip(fixes,weights))/total
    residuals=[abs(haversine(lat,lon,g.latitude,g.longitude)-d) for g,d,_ in fixes]
    average_residual=sum(residuals)/len(residuals) if residuals else fixes[0][1]*0.6
    geometry_floor=80 if len(fixes)>=4 else 140 if len(fixes)==3 else 250
    radius=int(max(geometry_floor,min(3000,average_residual)))
    count=len(fixes);confidence='HIGH' if count>=4 and radius<=250 else 'MEDIUM' if count>=3 and radius<=700 else 'LOW'
    animal.estimated_lat=lat;animal.estimated_lon=lon;animal.estimated_radius_m=radius;animal.location_confidence=confidence;animal.location_gateway_count=count;animal.location_estimated_at=current
    return {'lat':lat,'lon':lon,'radius_m':radius,'confidence':confidence,'gateway_count':count,'fixes':[{'gateway_id':g.id,'distance_m':round(d),'rssi':r} for g,d,r in fixes]}
