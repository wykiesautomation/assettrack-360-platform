"""Evidence-grade GPS movement validation for AssetTrack 360.

The validator never road-snaps and never invents travel between observations.
It returns only separately supported movement runs. All distances are metres.
"""
import math
from datetime import datetime

MAX_ACCURACY_M=100.0
MAX_EDGE_SECONDS=180.0
MIN_DERIVED_SPEED_KMH=2.0
MAX_DERIVED_SPEED_KMH=140.0
MIN_REPORTED_SPEED_KMH=2.5
MIN_SPEED_SUPPORTED_POINTS=2
MIN_GEOMETRY_EDGES=4
MIN_NET_PATH_RATIO=0.55
MAX_MEDIAN_TURN_DEG=65.0

def _distance_m(a,b):
    r=6371008.8
    p1=math.radians(float(a['latitude']));p2=math.radians(float(b['latitude']))
    dp=p2-p1;dl=math.radians(float(b['longitude'])-float(a['longitude']))
    value=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*r*math.asin(min(1.0,math.sqrt(value)))

def _bearing(a,b):
    p1=math.radians(float(a['latitude']));p2=math.radians(float(b['latitude']))
    dl=math.radians(float(b['longitude'])-float(a['longitude']))
    y=math.sin(dl)*math.cos(p2)
    x=math.cos(p1)*math.sin(p2)-math.sin(p1)*math.cos(p2)*math.cos(dl)
    return (math.degrees(math.atan2(y,x))+360.0)%360.0

def _turn_delta(a,b):
    return abs((a-b+180.0)%360.0-180.0)

def _median(values):
    values=sorted(float(x) for x in values)
    if not values:return 0.0
    middle=len(values)//2
    return values[middle] if len(values)%2 else (values[middle-1]+values[middle])/2.0

def validate_movement_segments(points):
    """Return supported route segments, accepted edges and rejection evidence.

    A run is accepted when it contains at least two consecutive accuracy-cleared
    edges and it has real speed support. If reported speed is unavailable, a longer
    four-edge run may be accepted only when its geometry is coherent and progressive.
    """
    edges=[];rejected=[]
    for index,(a,b) in enumerate(zip(points,points[1:])):
        start=datetime.fromisoformat(a['timestamp']);end=datetime.fromisoformat(b['timestamp'])
        seconds=(end-start).total_seconds();metres=_distance_m(a,b)
        derived=metres/seconds*3.6 if seconds>0 else 9999.0
        envelope=max(30.0,min(120.0,(float(a.get('accuracy') or 0)+float(b.get('accuracy') or 0))*1.5))
        reported=max(float(a.get('reported_speed') or 0),float(b.get('reported_speed') or 0))
        plausible_time=0<seconds<=MAX_EDGE_SECONDS
        plausible_speed=MIN_DERIVED_SPEED_KMH<=derived<=MAX_DERIVED_SPEED_KMH
        clears_accuracy=metres>envelope
        candidate=plausible_time and plausible_speed and clears_accuracy
        reason=None
        if not plausible_time:reason='TRACKING_GAP'
        elif not clears_accuracy:reason='STATIONARY_ACCURACY_ENVELOPE'
        elif derived>MAX_DERIVED_SPEED_KMH:reason='IMPOSSIBLE_JUMP'
        elif derived<MIN_DERIVED_SPEED_KMH:reason='NO_MEANINGFUL_MOVEMENT'
        edge={'i':index,'candidate':candidate,'km':metres/1000.0,'metres':metres,'seconds':seconds,
              'speed':derived,'reported':reported,'bearing':_bearing(a,b),'envelope':envelope}
        edges.append(edge)
        if reason and reason!='STATIONARY_ACCURACY_ENVELOPE':
            rejected.append({'reason':reason,'timestamp':b['timestamp'],'edge_index':index})

    candidate_runs=[];run=[]
    for edge in edges:
        if edge['candidate']:
            if run and edge['i']!=run[-1]['i']+1:
                candidate_runs.append(run);run=[]
            run.append(edge)
        elif run:
            candidate_runs.append(run);run=[]
    if run:candidate_runs.append(run)

    accepted_runs=[]
    for run in candidate_runs:
        if len(run)<2:
            rejected.append({'reason':'ISOLATED_MOVEMENT','timestamp':points[run[-1]['i']+1]['timestamp'],'edge_index':run[-1]['i']})
            continue
        run_points=points[run[0]['i']:run[-1]['i']+2]
        reported_support=sum(float(point.get('reported_speed') or 0)>=MIN_REPORTED_SPEED_KMH for point in run_points)
        speed_supported=reported_support>=MIN_SPEED_SUPPORTED_POINTS
        path=sum(edge['metres'] for edge in run)
        net=_distance_m(run_points[0],run_points[-1])
        net_ratio=net/path if path else 0.0
        turns=[_turn_delta(a['bearing'],b['bearing']) for a,b in zip(run,run[1:])]
        median_turn=_median(turns)
        geometry_supported=(len(run)>=MIN_GEOMETRY_EDGES and _median(edge['speed'] for edge in run)>=5.0
                            and net_ratio>=MIN_NET_PATH_RATIO and median_turn<=MAX_MEDIAN_TURN_DEG)
        if speed_supported or geometry_supported:
            accepted_runs.append(run)
        else:
            for edge in run:
                rejected.append({'reason':'ZERO_SPEED_DRIFT_RUN','timestamp':points[edge['i']+1]['timestamp'],'edge_index':edge['i']})

    segments=[];accepted_edges=[]
    for run in accepted_runs:
        segment=points[run[0]['i']:run[-1]['i']+2]
        if len(segment)>=3:
            segments.append(segment);accepted_edges.extend(run)
    return {'segments':segments,'accepted_edges':accepted_edges,'rejected':rejected,'all_edges':edges}
