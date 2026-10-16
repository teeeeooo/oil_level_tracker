"""SOI-1 H6: admission-backfill ablation with all history rebuilt, not a policy."""
from __future__ import annotations
import argparse
import gzip
import json
from pathlib import Path
import subprocess
from unittest.mock import patch
from tests.diagnostics import s11_single_observation_influence as soi
from tests.diagnostics import s11_role_consumer_intervention as rci
from tests.diagnostics.s11_single_observation_causality import ref_snapshot
from tests.diagnostics.s11_single_observation_verify import check_row, check_event_levels
from oil_tracker.adapters.vision.oil_observation_resolver import OilAdmissionEvidenceOwner


def without_backfill(refs, baseline_keys, offset):
    rows=[]; removed=[]
    for frame,items in enumerate(refs):
        keep=[]
        for ref in items:
            if frame==offset and ref.candidate_offset not in baseline_keys[frame]:
                removed.append(dict(frame_offset=frame,candidate_offset=ref.candidate_offset,
                    source=ref.candidate.source,y=ref.candidate.y))
            else: keep.append(ref)
        rows.append(tuple(keep))
    return tuple(rows),removed


def run(root,parent,output):
    rci.require(output.is_dir() and not any(output.iterdir()),'empty managed directory')
    comp=json.loads((parent/'comparison.json').read_text()); expected={}
    with gzip.open(parent/'population.jsonl.gz','rt',encoding='utf-8') as f:
        for line in f:
            item=json.loads(line)
            if item['id'] in comp['representatives'][:3]: expected[item['id']]=item
    raw=json.loads((root/rci.SAVED/'raw.json').read_text())
    recipe=rci.JsonRecipeRepository().load(root/rci.BUNDLE/'recipe_snapshot.oilrecipe')
    selected=expected[comp['representatives'][1]]['case']; whole=expected[comp['representatives'][2]]['case']
    cases=[('baseline',None,False),('original_selected_loss',selected,False),
        ('no_backfill_selected_loss',selected,True),('no_backfill_whole_oil_control',whole,True)]
    hashes={str(p.relative_to(root)):rci.digest(p) for p in (root/'src').rglob('*.py')}
    inputs={str(parent.relative_to(root)/n):rci.digest(parent/n) for n in ['comparison.json','population.jsonl.gz']}
    inputs.update(comp['preflight']['inputs'])
    pre=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
        sources=hashes,inputs=inputs,cases=cases,script_sha256=rci.digest(Path(__file__)))
    rci.write_json(output/'preflight.json',pre)
    records=[]; snapshots={}; summaries=[]; baseline_keys=None
    prepare=OilAdmissionEvidenceOwner.prepare
    for name,case,remove_backfill in cases:
        captured={}; operations=[]
        offset=None if case is None else next(i for i,r in enumerate(raw) if r['frame_index']==case['frame'])
        def observe(owner,*args,**kwargs):
            result=prepare(owner,*args,**kwargs); refs=result[0]
            captured['before']=ref_snapshot(refs)
            if remove_backfill:
                refs,removed=without_backfill(refs,baseline_keys,offset); operations.extend(removed)
            captured['after']=ref_snapshot(refs)
            return refs,result[1],result[2]
        with patch.object(OilAdmissionEvidenceOwner,'prepare',observe):
            record,complete,public,presentation=soi.execute(raw,recipe,case)
        rci.require(OilAdmissionEvidenceOwner.prepare is prepare,'admission observer not restored')
        if name=='baseline': baseline_keys=[{r['candidate_offset'] for r in frame} for frame in captured['after']]
        if name!='no_backfill_selected_loss':
            rci.require(record==expected[soi.case_id(case)],'baseline/negative control replay mismatch')
        byframe={r['frame_index']:r for r in record['rows']}
        for row,source in zip(record['rows'],raw,strict=True): check_row(row,source)
        for event in record['events']:
            sample=byframe[event['representative_frame_index']]['sample']
            rci.require(sample['timestamp_sec']==event['start_time_sec'],'event time')
            check_event_levels(event,sample)
        record.update(id=name,admission_withdrawals=operations)
        records.append(record); snapshots[name]=captured
        summaries.append(soi.summarize(record,expected['baseline']))
        if name=='no_backfill_selected_loss':
            from oil_tracker.adapters.reporting.graph_renderer import GraphRenderer
            rci.CsvExporter().export(public,output/'tracking.csv',output/'events.csv')
            GraphRenderer().render(public,output/'graphs',recipe,presentation=presentation)
        print(name,json.dumps(summaries[-1]['oil_missing_runs']),flush=True)
    rci.require(all(rci.digest(root/p)==h for p,h in {**hashes,**inputs}.items()),'input/source mutation')
    payload=dict(schema='s11-single-observation-backfill-v1',preflight=pre,records=records,snapshots=snapshots)
    (output/'readout.json.gz').write_bytes(gzip.compress(json.dumps(payload,ensure_ascii=False,
        sort_keys=True,allow_nan=False).encode(),mtime=0))
    rci.write_json(output/'comparison.json',dict(schema=payload['schema'],preflight=pre,cases=summaries,
        baseline_and_control_equal=True,production_unchanged=True,automatic_policy=False))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    parser.add_argument('--parent',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    run(args.root.resolve(),args.parent.resolve(),args.output.resolve())


if __name__=='__main__': main()
