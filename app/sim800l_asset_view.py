"""Read-only SIM800L presentation; no assignments or telemetry are created."""
from datetime import timezone

def io_rows(profile, assignments, cards, now, online):
    by_signal={c['signal'].id:c for c in cards}
    result=[]
    for spec in profile.get('channels',[]):
        if not spec.get('pin') or spec.get('direction') not in ('INPUT','OUTPUT'):
            continue
        assignment=assignments.get(spec['key'])
        enabled=bool(assignment and assignment.enabled and assignment.signal_id)
        card=by_signal.get(assignment.signal_id) if enabled else None
        reading=card.get('latest') if card else None
        quality=str(reading.quality or '').upper() if reading else ''
        sampled=reading.sampled_at if reading else None
        if sampled and not sampled.tzinfo:sampled=sampled.replace(tzinfo=timezone.utc)
        age=(now-sampled).total_seconds() if sampled else None
        live=bool(online and age is not None and 0<=age<=90 and quality=='GOOD')
        state='UNASSIGNED' if not enabled else 'WAITING FOR TELEMETRY' if not reading else 'SIMULATED' if quality=='SIMULATED' else 'LIVE' if live else 'LAST REPORTED'
        result.append({'pin':spec['pin'],'key':spec['key'],'label':assignment.customer_label if enabled else spec['label'],
                       'purpose':assignment.purpose if enabled else 'UNUSED','state':state,
                       'value':reading.value if reading else None,'unit':card['signal'].unit if card else '',
                       'quality':quality or 'WAITING','sampled_at':sampled,'functions':spec.get('supported_functions',[]),
                       'input_only':spec.get('input_only',False)})
    return result
