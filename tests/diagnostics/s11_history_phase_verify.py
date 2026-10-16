"""Saved-output verifier independent of HPA intervention/reducer implementation."""
from __future__ import annotations
import argparse
from collections import Counter
import csv
import gzip
import hashlib
import json
from pathlib import Path
from tests.diagnostics import s11_single_observation_verify as joins


def require(value,message):
    if not value: raise ValueError(message)


def digest(path):
    with path.open('rb') as stream: return hashlib.file_digest(stream,'sha256').hexdigest()


def locate(root,path):
    exact=root/path
    if exact.exists(): return exact
    moved=root/str(path).replace('/work/','/evidence/')
    require(moved.exists(),'missing retained input '+str(path))
    return moved


def payload_path(root,directory,relative):
    exact=directory/relative
    if exact.exists(): return exact
    index=json.loads((directory/'publication-index.json').read_text())
    item=index[str(relative)]; target=locate(root,item['path'])
    require(digest(target)==item['sha256'],'publication alias hash mismatch')
    return target


def ref_map(frames):
    out={}
    for offset,row in enumerate(frames):
        for ref in row:
            key=(ref['frame_offset'],ref['candidate_offset'])
            require(key[0]==offset and key not in out,'duplicate/misframed ref')
            out[key]=ref
    return out


def check_scalar_capture(capture,donor=None):
    before=ref_map(capture['recurrence_native']); after=ref_map(capture['recurrence_used'])
    require(before.keys()==after.keys(),'scalar transplant changed membership')
    donor=before if donor is None else ref_map(donor)
    edits=[]
    for key,a in before.items():
        b=after[key]; expected=dict(a)
        if key in donor:
            d=donor[key]
            require((a['source'],a['y'])==(d['source'],d['y']),'scalar donor identity')
            expected['track_opposition']=d['track_opposition']
        require(b==expected,'non-scalar field mutation or wrong scalar')
        if b['track_opposition']!=a['track_opposition']:
            edits.append(dict(frame_offset=key[0],candidate_offset=key[1],source=a['source'],y=a['y'],
                              before=a['track_opposition'],after=b['track_opposition']))
    require(edits==capture['scalar_edits'],'scalar edit ledger mismatch')
    return len(edits)


def check_group_capture(capture,zero,pre,mask):
    offset=pre['offset']; donor=pre['donor']; fields=[]
    if mask&1: fields+=['y']
    if mask&2: fields+=['local_quality']
    if mask&4: fields+=['motion_support','motion_coverage']
    before=zero['row_groups']; after=capture['row_groups']
    expected=json.loads(json.dumps(before))
    matches=[r for r in expected[offset] if r['members']==pre['current']['members']]
    require(len(matches)==1,'ambiguous group binding')
    for field in fields: matches[0][field]=donor[field]
    require(after==expected,'group mutation outside factorial fields')
    require(len(capture['group_edits'])==1,'group edit cardinality')
    edit=capture['group_edits'][0]
    require(edit['mask']==mask and edit['before']==pre['current'] and edit['after']==matches[0], 'group edit ledger')


def check_record(record,raw,baseline,summary,counts):
    originals={r['frame_index']:r for r in raw}; rows=record['rows']
    require(len(rows)==len(raw)==113,'window cardinality')
    joins.check_edits(record,originals)
    for row,source in zip(rows,raw,strict=True):
        joins.check_row(row,source); counts['rows']+=1
        counts['oil_joins']+=row['oil_y'] is not None; counts['foam_joins']+=row['foam_y'] is not None
    case=record['case']
    if case:
        at=next(r for r in rows if r['frame_index']==case['frame'])
        if case['mode']=='selected_oil':
            require(at['selected'] is None or at['selected']['candidate_offset']!=case['index'],'withdrawn Oil republished')
        else: require(at['foam_y' if case['mode']=='all_foam' else 'oil_y'] is None,'withdrawn series republished')
    for series in ('oil','foam'):
        key=series+'_y'; frame=None if not case else case['frame']
        changed=[r['frame_index'] for a,r in zip(baseline['rows'],rows,strict=True) if a[key]!=r[key]]
        require(summary[series+'_changed_frames']==changed,'change-accounting mismatch')
        require(summary[series+'_changed_elsewhere']==sum(f!=frame for f in changed),'elsewhere mismatch')
        require(summary[series+'_numeric']==sum(r[key] is not None for r in rows),'numeric accounting')
        require(summary[series+'_valid']==sum(r['sample'][series+'_is_valid'] for r in rows),'validity accounting')
        require(summary[series+'_missing_runs']==joins.runs(rows,key,False),'gap accounting')
        require(summary[series+'_numeric_runs']==joins.runs(rows,key,True),'run accounting')
    byframe={r['frame_index']:r for r in rows}
    for event in record['events']:
        row=byframe[event['representative_frame_index']]
        require(event['start_time_sec']==row['time_sec'],'event frame/time join')
        joins.check_event_levels(event,row['sample']); counts['events']+=1
    counts['windows']+=1


def check_csv(root,directory,name,record,counts):
    path=payload_path(root,directory,Path(name)/'tracking.csv')
    with path.open(encoding='utf-8-sig',newline='') as f: actual=list(csv.DictReader(f))
    require(len(actual)==len(record['rows']),'CSV cardinality')
    for row,observed in zip(record['rows'],actual,strict=True):
        for field,value in row['sample'].items():
            csv_value=observed[field]
            if value is None: require(csv_value=='','CSV null')
            elif isinstance(value,bool): require(csv_value==str(value),'CSV validity')
            elif isinstance(value,(int,float)): require(float(csv_value)==value,'CSV numeric')
            elif field=='flags': require((csv_value.split(';') if csv_value else [])==value,'CSV flags')
            else: require(csv_value==value,'CSV text')
        counts['csv_rows']+=1


def public(record):
    return dict(samples=[r['sample'] for r in record['rows']],events=record['events'],presentation=record['presentation'])


def verify(root,first,second,third):
    one=json.loads(gzip.decompress((first/'readout.json.gz').read_bytes()))
    two=json.loads(gzip.decompress((second/'readout.json.gz').read_bytes()))
    comparisons=[json.loads((p/'comparison.json').read_text()) for p in (first,second,third)]
    seen_pins={}; counts=Counter()
    for directory,comparison in zip((first,second,third),comparisons,strict=True):
        pre=comparison['preflight']
        for p,h in {**pre['inputs'],**pre['sources']}.items():
            key=(p,h)
            if key not in seen_pins:
                require(digest(locate(root,p))==h,'input/source hash mismatch '+p);seen_pins[key]=True
        snapshot=json.loads((directory/'protocol-snapshot.json').read_text())
        require(hashlib.sha256(snapshot['text'].encode()).hexdigest()==snapshot['sha256']==pre['protocol_sha256'],'protocol snapshot hash')
    pre=one['preflight']; rawpath=next(p for p in pre['inputs'] if p.endswith('/raw.json'))
    raw=json.loads(locate(root,rawpath).read_text()); baseline=one['records']['baseline']
    for data,comparison in zip((one,two),comparisons[:2],strict=True):
        summaries={s['id']:s for s in comparison['cases']}
        require(data['records'].keys()==summaries.keys(),'missing recorded arm')
        for name,record in data['records'].items(): check_record(record,raw,baseline,summaries[name],counts)
    for name,c in one['captures'].items():
        donor=None
        if '__' in name:
            arm,case=name.split('__'); donor=one['captures']['baseline' if arm=='baseline_weights' else case]['recurrence_native']
        counts['scalar_edits']+=check_scalar_capture(c,donor)
    for outcome in comparisons[0]['outcomes']:
        require(outcome['public_equal']==(public(one['records'][outcome['id']])==public(one['records'][outcome['compared_to']])),'public equality claim')
    require({s['mask'] for s in comparisons[1]['cases']}==set(range(8)),'factorial denominator')
    for mask in range(8):
        name=f'group_mask_{mask}'; c=two['captures'][name]
        check_scalar_capture(c);check_group_capture(c,two['captures']['group_mask_0'],two['preflight'],mask)
        check_csv(root,second,name,two['records'][name],counts)
    for name in ('baseline_weights__all_oil-f001320','loss_weights__all_oil-f001320'):
        check_csv(root,second,name,one['records'][name],counts)
    third_summary=comparisons[2]; summaries={s['id']:s for s in third_summary['cases']}; names=[]; originals={}; triggered={}
    original_population=next(p for p in third_summary['preflight']['inputs'] if p.endswith('/population.jsonl.gz'))
    with gzip.open(locate(root,original_population),'rt',encoding='utf-8') as stream:
        for line in stream:
            r=json.loads(line); originals[r['id']]=r
    with gzip.open(third/'population.jsonl.gz','rt',encoding='utf-8') as stream:
        for line in stream:
            payload=json.loads(line); r=payload['record']; name=r['id']; names.append(name); summary=summaries[name]
            check_record(r,raw,baseline,summary,counts)
            if payload['operations']: triggered[name]=r
            require(summary['quarantined_frames']==[o['frame_offset'] for o in payload['operations']],'quarantine accounting')
            for operation in payload['operations']:
                require(r['rows'][operation['frame_offset']]['oil_y'] is None,'quarantine published Oil')
                require(operation['vetoes'] and all(v['chain']['observations'][-1]['material_veto'] and v['profile']!='none'
                    for v in operation['vetoes']),'unbound veto')
                counts['quarantines']+=1
            original=originals[name]
            require(summary['paired_public_equal']==(public(original)==public(r)),'paired public claim')
            for series in ('oil','foam'):
                key=series+'_y'; changed=[a['frame_index'] for a,b in zip(original['rows'],r['rows'],strict=True) if a[key]!=b[key]]
                require(summary['paired_'+series+'_changed_frames']==changed,'paired changes')
            if name in third_summary['representatives']: check_csv(root,third,name,r,counts)
    require(names==list(originals)==list(summaries) and len(names)==246,'full original population not preserved')
    require(third_summary['preflight']['cases']==[r['case'] for r in originals.values()],'case list drift')
    require(counts['quarantines']==third_summary['quarantine_operations'],'quarantine count')
    publication=json.loads((third/'paired-publication.json').read_text())
    require(publication['population_sha256']==digest(third/'population.jsonl.gz'),'publication population binding')
    for p,h in publication['sources'].items():
        require(digest(locate(root,p))==h,'publication source hash')
        seen_pins[(p,h)]=True
    expected={(name,policy) for name in triggered for policy in ('default','trial')}
    actual={(entry['case'],entry['policy']) for entry in publication['entries']}
    require(actual==expected and len(actual)==len(publication['entries'])==publication['windows'],'publication paired denominator')
    for entry in publication['entries']:
        r=(originals if entry['policy']=='default' else triggered)[entry['case']]
        require(entry['rows']==len(r['rows']) and entry['movement_summary']==r['presentation']['movement_summary'],'publication narrative binding')
        check_csv(root,third,entry['path'],r,counts)
    scope=json.loads((third/'source-scope.json').read_text())
    for item in scope['videos']+scope['inspected_source_assets']+scope['review_constraints']:
        require(digest(locate(root,item['path']))==item['sha256'],'source-scope hash')
        seen_pins[(item['path'],item['sha256'])]=True
    counts['source_video_inventories']=len(scope['videos'])
    counts['paired_publication_windows']=len(publication['entries'])
    return dict(schema='s11-history-phase-verification-v2',**counts,unique_pins=len(seen_pins),mismatches=0,
                verifier_sha256=digest(Path(__file__)),physical_accuracy='NOT_EVALUATED',report_comprehension='NOT_HUMAN_EVALUATED')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    for name in ('first','second','third','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();result=verify(a.root.resolve(),a.first.resolve(),a.second.resolve(),a.third.resolve())
    with a.output.open('x',encoding='utf-8') as stream:json.dump(result,stream,indent=2)
    print(json.dumps(result))


if __name__=='__main__':main()
