"""Independent saved-stage accounting for SOI-1; no detector execution."""
from __future__ import annotations
from collections import Counter
import csv
import gzip
import json
from pathlib import Path
from tests.diagnostics.s11_single_observation_verify import require, digest, check_row, check_event_levels, runs
from tests.diagnostics.s11_profile_role_verify import artifact_file


def members(frames):
    result={}
    for offset,refs in enumerate(frames):
        for ref in refs:
            key=(offset,ref['candidate_offset'])
            require(ref['frame_offset']==offset and key not in result,'stage membership key')
            result[key]=ref
    return result


def stage_difference(before,after,raw):
    a,b=members(before),members(after); changes=[]; fields=Counter()
    for key in sorted(a.keys() & b.keys()):
        differing=[k for k in a[key] if a[key][k]!=b[key][k]]
        if differing:
            fields.update(differing)
            changes.append(dict(frame=raw[key[0]]['frame_index'],time_sec=raw[key[0]]['time_sec'],
                candidate_index=key[1],fields=differing))
    return dict(removed=[list(k) for k in sorted(a.keys()-b.keys())],
        added=[list(k) for k in sorted(b.keys()-a.keys())],field_counts=dict(fields),changes=changes)


def verify(root,directory,parent):
    data=json.loads(gzip.decompress((directory/'readout.json.gz').read_bytes()))
    summary=json.loads((directory/'comparison.json').read_text()); pre=data['preflight']
    require(pre==summary['preflight'],'preflight mismatch')
    for p,h in {**pre['sources'],**pre['inputs']}.items():
        require(digest(root/p)==h,'source/input hash mismatch: '+p)
    original=json.loads((parent/'comparison.json').read_text())
    raw=json.loads((root/next(p for p in pre['inputs'] if p.endswith('/raw.json'))).read_text())
    expected={}
    with gzip.open(parent/'population.jsonl.gz','rt',encoding='utf-8') as stream:
        for line in stream:
            r=json.loads(line)
            if r['id'] in original['representatives']: expected[r['id']]=r
    require(len(data['records'])==len(summary['cases'])==len(pre['cases'])==37,'causal population')
    baseline=expected['baseline']; counts=Counter(); seen=set()
    for record,case_summary,spec in zip(data['records'],summary['cases'],pre['cases'],strict=True):
        stage,case=spec; name=record['id']; require(name not in seen,'duplicate causal case'); seen.add(name)
        require(record['case']==case and case_summary['case']==case and case_summary['id']==name,'case binding')
        if stage=='early': require(record==expected[name],'instrumented replay inequality')
        require(len(record['rows'])==len(raw)==113,'frame denominator')
        byframe={}
        for row,source in zip(record['rows'],raw,strict=True):
            check_row(row,source); byframe[row['frame_index']]=row; counts['rows']+=1
        for event in record['events']:
            sample=byframe[event['representative_frame_index']]['sample']
            require(sample['timestamp_sec']==event['start_time_sec'],'event frame/time')
            check_event_levels(event,sample); counts['events']+=1
        for series in ('oil','foam'):
            key=series+'_y'; rows=record['rows']
            changed=[r['frame_index'] for r,b in zip(rows,baseline['rows'],strict=True) if r[key]!=b[key]]
            require(case_summary[series+'_changed_frames']==changed,'changed numeric accounting')
            require(case_summary[series+'_numeric']==sum(r[key] is not None for r in rows),'numeric count')
            require(case_summary[series+'_missing_runs']==runs(rows,key,False),'missing run accounting')
            require(case_summary[series+'_numeric_runs']==runs(rows,key,True),'numeric run accounting')
        if stage=='late_foam':
            require(not case_summary['oil_changed_frames'],'late Foam changed Oil')
            require(byframe[case['frame']]['foam_y'] is None,'late Foam member republished')
        if stage=='late_track':
            at=byframe[case['frame']]
            require(at['oil_y'] is None if case['index'] is None else at['selected'] is None or
                at['selected']['candidate_offset']!=case['index'],'late tracked member republished')
        if name.startswith('late_') and name in data['captures']:
            csvpath=artifact_file(root,directory,name+'/tracking.csv')
            with csvpath.open(encoding='utf-8-sig',newline='') as stream: csvrows=list(csv.DictReader(stream))
            require(len(csvrows)==113,'CSV denominator')
            for csvrow,row in zip(csvrows,record['rows'],strict=True):
                for key,expected_value in row['sample'].items():
                    value=csvrow[key]
                    if expected_value is None: require(value=='','CSV absent value')
                    elif isinstance(expected_value,bool): require(value==str(expected_value),'CSV validity')
                    elif isinstance(expected_value,(float,int)): require(float(value)==expected_value,'CSV numeric')
                    elif key=='flags': require(value.split(';')==expected_value if value else expected_value==[],'CSV flags')
                    else: require(value==expected_value,'CSV text')
                counts['csv_rows']+=1
        counts[stage]+=1
    differences={}; basecap=data['captures']['baseline']
    for name,capture in data['captures'].items():
        differences[name]={stage:stage_difference(basecap[stage],capture[stage],raw)
            for stage in ('admission','recurrence','tracked')}
        for stage in ('admission','recurrence','tracked'):
            for key,ref in members(capture[stage]).items():
                c=raw[key[0]]['candidates'][key[1]]
                require((c['source'],c['y'])==(ref['source'],ref['y']),'stage candidate provenance')
                counts['stage_member_joins']+=1
        if name.startswith('late_'):
            require(all(capture[s]==basecap[s] for s in ('admission','recurrence','tracked')),
                'late intervention changed upstream history')
        if name.startswith('late_track__'):
            record=next(r for r in data['records'] if r['id']==name); case=record['case']
            offset=next(i for i,d in enumerate(raw) if d['frame_index']==case['frame'])
            before=members(basecap['tracked']); after=members(capture['after_late_withdrawal'])
            wanted={k:v for k,v in before.items() if not (k[0]==offset and (case['index'] is None or k[1]==case['index']))}
            require(after==wanted,'late-track withdrawal scope/history mismatch')
            expected_ops=[dict(frame_offset=k[0],candidate_offset=k[1],source=v['source'],y=v['y'])
                for k,v in before.items() if k not in wanted]
            require(record['stage_interventions']==expected_ops,'late-track operation log')
    for record in data['records']:
        if not record['id'].startswith('late_foam__'): continue
        case=record['case']; source=next(r for r in raw if r['frame_index']==case['frame'])
        expected_ops=[dict(frame=case['frame'],candidate_offset=i,source=c['source'],y=c['y'])
            for i,c in enumerate(source['candidates']) if c['kind']=='foam_front']
        require(record['stage_interventions']==expected_ops,'late-Foam operation scope')
    require((counts['early'],counts['late_track'],counts['late_foam'],counts['csv_rows'])==(4,2,31,339),'stage/CSV denominator')
    for per_case in differences.values():
        for entry in per_case.values():
            changes=entry.pop('changes')
            entry.update(changed_member_count=len(changes),first_changes=changes[:3])
    return dict(schema='s11-single-observation-causal-verification-v1',**counts,
        verifier_sha256=digest(Path(__file__)),stage_differences=differences,mismatches=0,
        scope='Computational attribution and provenance, NOT physical accuracy or production-safe policy')


def verify_backfill(root,directory,parent):
    data=json.loads(gzip.decompress((directory/'readout.json.gz').read_bytes()))
    summary=json.loads((directory/'comparison.json').read_text()); pre=data['preflight']
    require(pre==summary['preflight'],'H6 preflight')
    for p,h in {**pre['sources'],**pre['inputs']}.items(): require(digest(root/p)==h,'H6 input/source hash')
    raw=json.loads((root/next(p for p in pre['inputs'] if p.endswith('/raw.json'))).read_text())
    require(len(data['records'])==len(summary['cases'])==4,'H6 case denominator')
    original={}
    with gzip.open(parent/'population.jsonl.gz','rt',encoding='utf-8') as stream:
        for line in stream:
            r=json.loads(line)
            if r['case'] is None or r['case'] in [s[1] for s in pre['cases']]: original[json.dumps(r['case'],sort_keys=True)]=r
    base=members(data['snapshots']['baseline']['after']); count=Counter()
    for record,case_summary,spec in zip(data['records'],summary['cases'],pre['cases'],strict=True):
        name,case,filtered=spec
        require(record['id']==name and record['case']==case,'H6 case binding')
        before=members(data['snapshots'][name]['before']); after=members(data['snapshots'][name]['after'])
        offset=None if case is None else next(i for i,r in enumerate(raw) if r['frame_index']==case['frame'])
        wanted={k:v for k,v in before.items() if not (filtered and k[0]==offset and k not in base)}
        require(wanted==after,'H6 changed surviving refs or restored members')
        ops=[dict(frame_offset=k[0],candidate_offset=k[1],source=v['source'],y=v['y']) for k,v in before.items() if k not in wanted]
        require(record['admission_withdrawals']==ops,'H6 operation log')
        reference=original[json.dumps(case,sort_keys=True)]
        require(record['edits']==reference['edits'],'H6 changed raw intervention')
        if name!='no_backfill_selected_loss':
            normalized={k:v for k,v in record.items() if k!='admission_withdrawals'}
            normalized['id']=reference['id']; require(normalized==reference,'H6 original/control inequality')
        byframe={r['frame_index']:r['sample'] for r in record['rows']}
        require(len(record['rows'])==113,'H6 frame denominator')
        for row,source in zip(record['rows'],raw,strict=True): check_row(row,source); count['rows']+=1
        for event in record['events']:
            sample=byframe[event['representative_frame_index']]
            require(sample['timestamp_sec']==event['start_time_sec'],'H6 event frame/time')
            check_event_levels(event,sample); count['events']+=1
        require(case_summary['oil_missing_runs']==runs(record['rows'],'oil_y',False),'H6 gap accounting')
        for key,ref in {**before,**after}.items():
            candidate=raw[key[0]]['candidates'][key[1]]
            require((candidate['source'],candidate['y'])==(ref['source'],ref['y']),'H6 ref provenance')
            count['ref_joins']+=1
    target=next(r for r in data['records'] if r['id']=='no_backfill_selected_loss')
    with artifact_file(root,directory,'tracking.csv').open(encoding='utf-8-sig',newline='') as f: csvrows=list(csv.DictReader(f))
    require(len(csvrows)==113,'H6 CSV denominator')
    for row,saved in zip(target['rows'],csvrows,strict=True):
        require(row['frame_index']==int(saved['frame_index']) and row['time_sec']==float(saved['timestamp_sec']),'H6 CSV identity')
        for key,field in [('oil_y','raw_oil_air_level_y'),('foam_y','raw_foam_front_y')]:
            require(row[key]==(None if saved[field]=='' else float(saved[field])),'H6 CSV coordinate')
    return dict(schema='s11-single-observation-backfill-verification-v1',**count,csv_rows=113,
        mismatches=0,verifier_sha256=digest(Path(__file__)),scope='H6 intervention scope and saved outputs only')
