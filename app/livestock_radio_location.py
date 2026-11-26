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

def _to_xy(lat,lon,lat0,lon0):
    y=(lat-lat0)*111320.0
    x=(lon-lon0)*111320.0*math.cos(math.radians(lat0))
    return x,y

def _to_latlon(x,y,lat0,lon0):
    lat=lat0+y/111320.0
    lon=lon0+x/(111320.0*math.cos(math.radians(lat0)))
    return lat,lon

def _solve_multilateration(fixes):
    """Coarse-to-fine least-squares circle fit without an external numeric package."""
    lat0=sum(g.latitude for g,_,_ in fixes)/len(fixes);lon0=sum(g.longitude for g,_,_ in fixes)/len(fixes)
    anchors=[]
    for gateway,distance,rssi in fixes:
        x,y=_to_xy(gateway.latitude,gateway.longitude,lat0,lon0);anchors.append((x,y,float(distance),rssi,gateway))
    xs=[a[0] for a in anchors];ys=[a[1] for a in anchors];max_d=max(a[2] for a in anchors)
    minx,maxx=min(xs)-max_d,max(xs)+max_d;miny,maxy=min(ys)-max_d,max(ys)+max_d
    best=None
    for resolution in (35,31,25,21):
        stepx=(maxx-minx)/max(1,resolution-1);stepy=(maxy-miny)/max(1,resolution-1)
        for ix in range(resolution):
            x=minx+ix*stepx
            for iy in range(resolution):
                y=miny+iy*stepy
                residuals=[math.hypot(x-ax,y-ay)-distance for ax,ay,distance,_,_ in anchors]
                # Huber-like cost reduces the effect of one reflected/blocked radio path.
                cost=sum((r*r if abs(r)<=500 else 1000*abs(r)-250000) for r in residuals)
                if best is None or cost<best[0]:best=(cost,x,y,residuals)
        _,bx,by,_=best
        spanx=max(stepx*4,80);spany=max(stepy*4,80);minx,maxx=bx-spanx,bx+spanx;miny,maxy=by-spany,by+spany
    _,x,y,residuals=best
    lat,lon=_to_latlon(x,y,lat0,lon0)
    rms=math.sqrt(sum(r*r for r in residuals)/len(residuals))
    geometry=max(max(xs)-min(xs),max(ys)-min(ys))
    return lat,lon,rms,geometry,anchors

def estimate_animal(animal,current,window_seconds=900):
    recent=LivestockTagReception.query.filter(LivestockTagReception.animal_id==animal.id,LivestockTagReception.received_at>=current-timedelta(seconds=window_seconds)).order_by(LivestockTagReception.received_at.desc()).all()
    latest={}
    for row in recent:
        if row.gateway_id not in latest:latest[row.gateway_id]=row
    fixes=[]
    for gateway_id,row in latest.items():
        gateway=LivestockGateway.query.filter_by(id=gateway_id,customer_id=animal.customer_id,farm_id=animal.farm_id,active=True).first()
        distance=calibrated_distance(gateway_id,row.rssi)
        if gateway and distance is not None:fixes.append((gateway,distance,row.rssi))
    # A single gateway gives only a radius and two gateways give ambiguous intersections.
    # Do not fabricate a centre until at least three calibrated gateways heard the tag.
    if len(fixes)<3:
        animal.estimated_lat=None;animal.estimated_lon=None;animal.estimated_radius_m=None
        animal.location_confidence='INSUFFICIENT';animal.location_gateway_count=len(fixes);animal.location_estimated_at=current
        return None
    lat,lon,rms,geometry,anchors=_solve_multilateration(fixes)
    geometry_penalty=300 if geometry<250 else 150 if geometry<500 else 0
    radius=int(max(80,min(3000,rms+geometry_penalty)))
    count=len(fixes)
    confidence='HIGH' if count>=4 and radius<=250 and geometry>=500 else 'MEDIUM' if count>=3 and radius<=800 else 'LOW'
    animal.estimated_lat=lat;animal.estimated_lon=lon;animal.estimated_radius_m=radius
    animal.location_confidence=confidence;animal.location_gateway_count=count;animal.location_estimated_at=current
    return {'lat':lat,'lon':lon,'radius_m':radius,'confidence':confidence,'gateway_count':count,'geometry_m':round(geometry),'rms_error_m':round(rms),'fixes':[{'gateway_id':g.id,'distance_m':round(d),'rssi':r} for g,d,r in fixes]}
