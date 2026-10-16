"""Independent source, intervention, population and publication verifier for SOI-1."""
from __future__ import annotations
from collections import Counter
import csv
import gzip
import hashlib
import json
from pathlib import Path


def require(value, message):
    if not value:
        raise ValueError(message)


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def runs(rows, key, present):
    groups = []; start = None
    for i in range(len(rows)+1):
        active = i < len(rows) and (rows[i][key] is not None) == present
        if active and start is None: start = i
        if not active and start is not None:
            a,b = rows[start],rows[i-1]
            groups.append(dict(start_sec=a['time_sec'],last_sample_sec=b['time_sec'],
                sample_count=i-start,sampled_span_sec=b['time_sec']-a['time_sec']))
            start = None
    return groups


def check_row(row, original):
    require((row['frame_index'],row['time_sec']) == (original['frame_index'],original['time_sec']), 'frame/time mismatch')
    require(row['sample']['frame_index'] == row['frame_index'] and row['sample']['timestamp_sec'] == row['time_sec'], 'sample identity mismatch')
    require(row['sample']['raw_oil_air_level_y'] == row['oil_y'] and row['sample']['raw_foam_front_y'] == row['foam_y'], 'projection mismatch')
    selected = row['selected']
    if selected is None:
        require(row['oil_y'] is None, 'numeric without selected Oil')
    else:
        index = selected['candidate_offset']
        require(isinstance(index,int) and 0 <= index < len(original['candidates']), 'candidate offset')
        c = original['candidates'][index]
        require((c['kind'],c['source'],c['y']) == ('oil_air',selected['source'],selected['y']), 'selected provenance mismatch')
        require(c['y'] == row['oil_y'], 'selected Oil coordinate mismatch')
    if row['foam_y'] is not None:
        require(any(c['kind']=='foam_front' and c['y']==row['foam_y'] for c in original['candidates']), 'Foam membership mismatch')


def check_edits(record, originals):
    case = record['case']
    if case is None:
        require(record['edits'] == [], 'baseline intervention'); return
    raw = originals[case['frame']]
    kind,field = ('foam_front','sequence_foam_eligible') if case['mode']=='all_foam' else ('oil_air','sequence_eligible')
    indices = [i for i,c in enumerate(raw['candidates']) if c['kind']==kind and (case['mode']!='selected_oil' or i==case['index'])]
    require(indices == [e['index'] for e in record['edits']], 'intervention denominator mismatch')
    for e in record['edits']:
        c = raw['candidates'][e['index']]
        require(e == dict(frame=case['frame'],index=e['index'],source=c['source'],y=c['y'],field=field,
            before=c['features'].get(field),before_present=field in c['features']), 'intervention provenance mismatch')


def check_event_levels(event, sample):
    """Lifecycle events intentionally omit coordinates; numeric events bind smoothed samples."""
    for event_key, sample_key in [('oil_level_px','smoothed_oil_air_level_px_from_zero'),
                                  ('foam_front_px','smoothed_foam_front_px_from_zero')]:
        if event['event_type'] in ('ANALYSIS_START', 'ANALYSIS_END'):
            require(event[event_key] is None, 'lifecycle event fabricated a coordinate')
        else:
            require(sample[sample_key] == event[event_key], 'event representative level join')


def verify(root, output):
    comparison = json.loads((output/'comparison.json').read_text())
    pre = comparison['preflight']
    for p,h in {**pre['inputs'],**pre['source_hashes']}.items():
        require(digest(root/p)==h, 'input/source hash mismatch: '+p)
    rawpath = next(p for p in pre['inputs'] if p.endswith('/raw.json'))
    raw = json.loads((root/rawpath).read_text())
    originals = {r['frame_index']:r for r in raw}
    require(len(raw)==len(originals)==113, 'input population')
    summaries = {c['id']:c for c in comparison['cases']}
    counts = Counter(); seen = set(); records = {}; baseline = None
    with gzip.open(output/'population.jsonl.gz','rt',encoding='utf-8') as stream:
        for line in stream:
            record = json.loads(line); name = record['id']; case = record['case']
            require(name not in seen and name in summaries, 'duplicate/unknown run')
            seen.add(name); counts['runs'] += 1
            if name == 'baseline': baseline = record
            require(baseline is not None, 'baseline must precede cases')
            require(len(record['rows'])==113, 'output population')
            require([r['frame_index'] for r in record['rows']]==list(originals), 'ordered frame identity')
            check_edits(record,originals)
            for row in record['rows']:
                check_row(row,originals[row['frame_index']]); counts['rows'] += 1
                counts['oil_joins'] += row['oil_y'] is not None
                counts['foam_memberships'] += row['foam_y'] is not None
            byframe = {r['frame_index']:r for r in record['rows']}
            if case:
                at = byframe[case['frame']]
                if case['mode']=='selected_oil':
                    require(at['selected'] is None or at['selected']['candidate_offset']!=case['index'],'suppressed member published')
                else:
                    require(at['foam_y' if case['mode']=='all_foam' else 'oil_y'] is None,'suppressed series published')
            summary = summaries[name]
            for series in ('oil','foam'):
                key=series+'_y'
                changed=[b['frame_index'] for a,b in zip(baseline['rows'],record['rows'],strict=True) if a[key]!=b[key]]
                frame = None if case is None else case['frame']
                require(summary[series+'_changed_frames']==changed, 'changed-frame accounting')
                require(summary[series+'_changed_elsewhere']==sum(f!=frame for f in changed), 'influence accounting')
                require(summary[series+'_numeric']==sum(r[key] is not None for r in record['rows']), 'numeric accounting')
                require(summary[series+'_valid']==sum(r['sample'][series+'_is_valid'] for r in record['rows']), 'validity accounting')
                require(summary[series+'_missing_runs']==runs(record['rows'],key,False), 'missing-run accounting')
                require(summary[series+'_numeric_runs']==runs(record['rows'],key,True), 'numeric-run accounting')
            for event in record['events']:
                row = byframe[event['representative_frame_index']]
                require(row['time_sec']==event['start_time_sec'], 'event time join')
                check_event_levels(event, row['sample'])
                counts['events'] += 1
            if name in comparison['representatives']: records[name]=record
    require(seen==set(summaries), 'missing population cases')
    require(counts['runs']==comparison['population_cases'] and counts['rows']==comparison['population_rows'], 'population accounting')
    require([s['case'] for s in comparison['cases'][1:]] == pre['cases'], 'predeclared case list drift')
    expected_cases = []
    for mode in ('selected_oil', 'all_oil', 'all_foam'):
        for original, row in zip(raw, baseline['rows'], strict=True):
            eligible = (row['selected'] is not None if mode=='selected_oil' else
                any(c['kind']=='oil_air' for c in original['candidates']) if mode=='all_oil' else
                any(c['kind']=='foam_front' and c['features'].get('sequence_foam_eligible',0)>=.5 for c in original['candidates']))
            if eligible:
                expected_cases.append(dict(mode=mode,frame=original['frame_index'],
                    index=row['selected']['candidate_offset'] if mode=='selected_oil' else None))
    require(pre['cases']==expected_cases, 'independent population enumeration')
    for name,record in records.items():
        with (output/name/'tracking.csv').open(encoding='utf-8-sig',newline='') as stream:
            rows=list(csv.DictReader(stream))
        require(len(rows)==113, 'CSV cardinality')
        for actual,row in zip(rows,record['rows'],strict=True):
            for key,expected in row['sample'].items():
                value=actual[key]
                if expected is None: require(value=='','CSV None')
                elif isinstance(expected,bool): require(value==str(expected),'CSV validity')
                elif isinstance(expected,(float,int)): require(float(value)==expected,'CSV numeric')
                elif key=='flags': require(value.split(';')==expected if value else expected==[], 'CSV flags')
                else: require(value==expected,'CSV text')
            counts['csv_rows'] += 1
    return dict(schema='s11-single-observation-verification-v2', **counts,
        input_and_source_hashes=len(pre['inputs'])+len(pre['source_hashes']),
        verifier_sha256=digest(Path(__file__)), mismatches=0,
        physical_accuracy='NOT_EVALUATED',report_comprehension='NOT_HUMAN_EVALUATED')
