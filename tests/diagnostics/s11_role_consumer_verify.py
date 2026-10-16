"""Independent saved-output verifier for the RCI diagnostic, not an evaluator."""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import itertools
import json
from pathlib import Path


def check(condition, message):
    if not condition:
        raise ValueError(message)


def verify_event_sample(event: dict, samples_by_frame: dict) -> None:
    """Verify all motion/Foam/quality events, not only displayed extrema."""
    frame = event['representative_frame_index']
    check(frame in samples_by_frame, 'event representative frame absent')
    sample = samples_by_frame[frame]
    check(float(event['start_time_sec']) == float(sample['timestamp_sec']), 'event time join')
    for event_key, sample_key in [('oil_level_px', 'smoothed_oil_air_level_px_from_zero'),
                                  ('foam_front_px', 'smoothed_foam_front_px_from_zero')]:
        if event[event_key] != '':
            check(sample[sample_key] != '' and float(event[event_key]) == float(sample[sample_key]),
                  'event representative level join')


def verify(root: Path, directory: Path) -> dict:
    summary = json.loads((directory/'comparison.json').read_text())
    trace = json.loads(gzip.decompress((directory/'readout.json.gz').read_bytes()))
    pre = summary['preflight']
    check(trace['preflight'] == pre, 'preflight mismatch')
    for rel, expected in {**pre['inputs'], **pre['source_hashes']}.items():
        with (root/rel).open('rb') as f:
            check(hashlib.file_digest(f,'sha256').hexdigest() == expected, 'source/input hash mismatch: '+rel)
    raw_path = next(p for p in pre['inputs'] if p.endswith('/raw.json'))
    raw = json.loads((root/raw_path).read_text())
    frames = {d['frame_index']: d for d in raw}
    check(len(frames) == len(raw), 'duplicate source frames')
    controls = {(c['frame'],c['index']): c for c in pre['controls']}
    check(len(controls) == len(pre['controls']), 'duplicate controls')
    roster_path = next(p for p in pre['inputs'] if 'raster-partition' in p)
    original_units = json.loads(gzip.decompress((root/roster_path).read_bytes()))['units']
    roles = {}
    for u in original_units:
        if u['group'] != 'sample4' or u['review_label'] not in ('ACCEPTED','OPPOSED'):
            continue
        q=u['query']; key=(q['frame'],q['candidate_index'])
        check(key not in roles, 'duplicate original role')
        roles[key]=u
    check(roles.keys()==controls.keys(), 'original review population mismatch')
    for key,c in controls.items():
        u=roles[key]; q=u['query']; original=frames[key[0]]['candidates'][key[1]]
        check((c['source'],c['y'])==(q['source'],q['source_xy'][1])==(original['source'],original['y']), 'original review identity mismatch')
        check(c['label_basis']==u['label_basis'] and c['review_label']==u['review_label'], 'review scope changed')
        physical=isinstance(u['label_basis'],dict) and u['label_basis'].get('physical')=='TARGET_CORRESPONDENCE'
        check(c['physical_positive']==physical, 'practical truth was promoted')
    baseline=trace['variants'][0]['rows']
    report={}
    check(len(trace['variants'])==len(summary['variants'])==5,'variant denominator')
    for variant,saved in zip(trace['variants'],summary['variants'],strict=True):
        name=variant['variant']; rows=variant['rows']
        check(name==saved['variant'] and name in pre['variants'], 'variant binding')
        check(len(rows)==len(raw)==113, 'row denominator')
        with (directory/name/'tracking.csv').open(encoding='utf-8-sig',newline='') as f:
            csv_rows=list(csv.DictReader(f))
        check(len(csv_rows)==len(rows),'CSV denominator')
        joined, statuses, foam_changed = 0, [], []
        for i,(r,source,csv_row) in enumerate(zip(rows,raw,csv_rows,strict=True)):
            check(r['frame_index']==source['frame_index']==int(csv_row['frame_index']), 'frame join')
            check(r['time_sec']==source['time_sec']==float(csv_row['timestamp_sec']), 'time join')
            selected=r['selected']; csv_y=None if csv_row['raw_oil_air_level_y']=='' else float(csv_row['raw_oil_air_level_y'])
            check(csv_y==r['oil_y'],'CSV/sequence Oil Y mismatch')
            if selected is None:
                check(r['oil_y'] is None, 'unproven numeric observation'); status='NO_NUMERIC_OIL'
            else:
                c=source['candidates'][selected['candidate_offset']]
                check(c['kind']=='oil_air' and c['source']==selected['source'] and c['y']==selected['y']==r['oil_y'], 'selected provenance')
                joined+=1; key=(r['frame_index'],selected['candidate_offset']); role=roles.get(key)
                if role is None: status='UNASSESSED_SELECTION'
                elif role['review_label']=='OPPOSED': status='REVIEWED_OPPOSED'
                elif controls[key]['physical_positive']: status='PHYSICAL_CORRESPONDENCE'
                else: status='PRACTICALLY_ACCEPTED'
            check(status==r['review_status'],'selected role overclaim')
            statuses.append(status)
            check((csv_row['foam_is_valid']=='True')==r['foam_is_valid'], 'Foam validity serialization')
            csv_foam=None if csv_row['raw_foam_front_y']=='' else float(csv_row['raw_foam_front_y'])
            check(csv_foam==r['foam_y'], 'Foam coordinate serialization')
            if r['foam_fields']!=baseline[i]['foam_fields'] or r['foam_is_valid']!=baseline[i]['foam_is_valid']:
                foam_changed.append(r['frame_index'])
        check(foam_changed==saved['foam_changed_frames'],'Foam comparison mismatch')
        check(joined==saved['numeric_oil'],'numeric Oil denominator')
        calculated={s:statuses.count(s) for s in set(statuses)}
        check(calculated==saved['review_status_counts'],'review summary mismatch')
        calls=variant['authority_calls']; keys=[(c['frame'],c['index']) for c in calls]
        expected_keys=[(d['frame_index'],i) for d in raw for i,c in enumerate(d['candidates']) if c['kind']=='oil_air']
        check(keys==expected_keys, 'all-candidate authority call identity/order mismatch')
        injection_count=0
        for c in calls:
            role=controls.get((c['frame'],c['index']),{}); before=c['before']; after=c['after']
            if before!=after:
                injection_count+=1
                demote=(name=='negative_anchor_demotion' and role.get('review_label')=='OPPOSED' and before['tier']==3 and after['tier']==2)
                promote=(name in ('positive_authority_only','negative_veto_positive_authority') and role.get('physical_positive') and before['tier'] in (1,2) and after['tier']==3)
                check(demote or promote, 'unauthorized tier injection')
                check(before['reason']==after['reason'], 'original reason overwritten')
        check(injection_count==len(saved['authority_changes']), 'authority change denominator')
        for missing,label in [(False,'numeric_oil_runs'),(True,'missing_oil_runs')]:
            recomputed=[]
            for state,group in itertools.groupby(rows,key=lambda r:r['oil_y'] is None):
                group=list(group)
                if state==missing:
                    recomputed.append({'start_sec':group[0]['time_sec'],'last_sample_sec':group[-1]['time_sec'],
                        'sample_count':len(group),'sampled_span_sec':group[-1]['time_sec']-group[0]['time_sec']})
            check(recomputed==saved[label], 'sample-run denominator/span')
        with (directory/name/'events.csv').open(encoding='utf-8-sig',newline='') as f:
            events=list(csv.DictReader(f))
        extreme_count=0
        for e in events:
            verify_event_sample(e, {r['frame_index']: r for r in csv_rows})
            if e['event_type'] not in ('MAXIMUM_OIL_LEVEL','MINIMUM_OIL_LEVEL'): continue
            matches=[x for x in saved['extrema'] if x['event']==e['event_type']]
            check(len(matches)==1,'missing/duplicate extrema summary')
            x=matches[0]; check(x['frame_index']==int(e['representative_frame_index']) and x['time_sec']==float(e['start_time_sec']),'extrema binding')
            row=next(r for r in rows if r['frame_index']==x['frame_index'])
            check(x['y']==row['oil_y'] and x['review_status']==row['review_status'], 'extrema role/Y mismatch')
            extreme_count+=1
        check(extreme_count==len(saved['extrema']), 'extrema count')
        report[name]={'rows':len(rows),'same_frame_numeric_joins':joined,'CSV_rows':len(csv_rows),
                      'authority_calls':len(calls),'authority_injections':injection_count,
                      'extrema_verified':extreme_count,'domain_events_verified':len(events),'foam_changed_frames':foam_changed}
    return {'schema':'s11-role-consumer-independent-verification-v2','status':'PASS',
            'variants':report,'review_bindings':len(controls),'mismatches':0,
            'claim':'Arithmetic, provenance and injection scope only; no physical classifier or comprehension acceptance.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,required=True); p.add_argument('--directory',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True); args=p.parse_args()
    result=verify(args.root.resolve(),args.directory.resolve())
    with args.output.open('x',encoding='utf-8') as f: json.dump(result,f,indent=2); f.write('\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
