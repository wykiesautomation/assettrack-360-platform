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
    points=sorted(points,key=lambda p:abs(float(p.median_rssi)-float(rssi)))
    if len(points)==1:return float(points[0].distance_m)
    a,b=points[0],points[1];ra,rb=float(a.median_rssi),float(b.median_rssi)
    if abs(ra-rb)<0.1:return (a.distance_m+b.distance_m)/2
    ratio=(float(rssi)-ra)/(rb-ra);return max(10.0,min(10000.0,a.distance_m+ratio*(b.distance_m-a.distance_m)))

def estimate_animal(animal,current,window_seconds=120):
    recent=LivestockTagReception.query.filter(LivestockTagReception.animal_id==animal.id,LivestockTagReception.received_at>=current-timedelta(seconds=window_seconds)).order_by(LivestockTagReception.received_at.desc()).all()
    latest={}
    for row in recent:
        if row.gateway_id not in latest:latest[row.gateway_id]=row
    fixes=[]
    for gateway_id,row in latest.items():
        gw=LivestockGateway.query.get(gateway_id);distance=calibrated_distance(gateway_id,row.rssi)
        if gw and distance:fixes.append((gw,distance,row.rssi))
    if not fixes:return None
    weights=[1/max(25.0,d*d) for _,d,_ in fixes];total=sum(weights)
    lat=sum(g.latitude*w for (g,_,_),w in zip(fixes,weights))/total;lon=sum(g.longitude*w for (g,_,_),w in zip(fixes,weights))/total
    residuals=[abs(haversine(lat,lon,g.latitude,g.longitude)-d) for g,d,_ in fixes]
    radius=int(max(50,min(3000,(sum(residuals)/len(residuals) if residuals else fixes[0][1]*0.6))))
    count=len(fixes);confidence='HIGH' if count>=5 and radius<=250 else 'MEDIUM' if count>=3 and radius<=600 else 'LOW'
    animal.estimated_lat=lat;animal.estimated_lon=lon;animal.estimated_radius_m=radius;animal.location_confidence=confidence;animal.location_gateway_count=count;animal.location_estimated_at=current
    return {'lat':lat,'lon':lon,'radius_m':radius,'confidence':confidence,'gateway_count':count}
