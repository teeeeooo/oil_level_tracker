"""SOI-1 stage interventions: frozen-history diagnostics, NOT deployable policies."""
from __future__ import annotations
import argparse
from contextlib import ExitStack
from dataclasses import fields, replace
import gzip
import json
from pathlib import Path
import subprocess
from unittest.mock import patch
from tests.diagnostics import s11_single_observation_influence as soi
from tests.diagnostics import s11_single_observation_verify as verify
from tests.diagnostics import s11_role_consumer_intervention as rci
from oil_tracker.adapters.vision import oil_observation_resolver as oil
from oil_tracker.adapters.vision.foam_episode_resolver import FoamEpisodeResolver
from oil_tracker.domain.enums import BoundaryKind


def ref_snapshot(frames):
    return [[rci.normalize({**{f.name:getattr(ref,f.name) for f in fields(ref)
        if f.name not in {'candidate','evidence'}},
        'source':ref.candidate.source,'y':ref.candidate.y}) for ref in refs] for refs in frames]


def late_foam_input(detections, frame):
    return tuple(replace(d, candidates=[replace(c, features={**c.features,'sequence_foam_eligible':0.0})
        if c.kind is BoundaryKind.FOAM_FRONT else c for c in d.candidates])
        if d.frame_index==frame else d for d in detections)


def filtered_tracklets(result, frame_offset, candidate_index):
    rows=[]; removed=[]
    for offset, refs in enumerate(result.refs_by_frame):
        row=[]
        for ref in refs:
            if offset==frame_offset and (candidate_index is None or ref.candidate_offset==candidate_index):
                removed.append(dict(frame_offset=offset,candidate_offset=ref.candidate_offset,
                    source=ref.candidate.source,y=ref.candidate.y))
            else: row.append(ref)
        rows.append(tuple(row))
    rci.require(bool(removed), 'late withdrawal removed no tracked member')
    return replace(result,refs_by_frame=tuple(rows)), removed


def execute(raw, recipe, case, stage):
    rci.require(stage in ('early','late_foam','late_track'), 'unknown intervention stage')
    captured={}; operations=[]
    prepare=oil.OilAdmissionEvidenceOwner.prepare
    oppose=oil.OilTrackletOppositionOwner._apply_track_opposition
    track=oil.DirectedInterfaceTrackletBuilder.resolve
    foam=FoamEpisodeResolver.resolve
    def prepare_wrapper(self,*args,**kwargs):
        result=prepare(self,*args,**kwargs)
        captured['admission']=ref_snapshot(result[0]); return result
    def oppose_wrapper(self,*args,**kwargs):
        result=oppose(self,*args,**kwargs)
        captured['recurrence']=ref_snapshot(result[0]); return result
    def track_wrapper(self,*args,**kwargs):
        result=track(self,*args,**kwargs)
        captured['tracked']=ref_snapshot(result.refs_by_frame)
        if stage=='late_track':
            offset=next(i for i,d in enumerate(raw) if d['frame_index']==case['frame'])
            result, removed=filtered_tracklets(result,offset,case['index'])
            operations.extend(removed)
            captured['after_late_withdrawal']=ref_snapshot(result.refs_by_frame)
        return result
    def foam_wrapper(self,detections,glass):
        if stage=='late_foam':
            operations.extend(dict(frame=case['frame'],candidate_offset=i,source=c.source,y=c.y)
                for d in detections if d.frame_index==case['frame']
                for i,c in enumerate(d.candidates) if c.kind is BoundaryKind.FOAM_FRONT)
            detections=late_foam_input(detections,case['frame'])
        return foam(self,detections,glass)
    with ExitStack() as stack:
        for target,name,wrapper in [(oil.OilAdmissionEvidenceOwner,'prepare',prepare_wrapper),
            (oil.OilTrackletOppositionOwner,'_apply_track_opposition',oppose_wrapper),
            (oil.DirectedInterfaceTrackletBuilder,'resolve',track_wrapper),
            (FoamEpisodeResolver,'resolve',foam_wrapper)]:
            stack.enter_context(patch.object(target,name,wrapper))
        record, complete, public, presentation=soi.execute(raw,recipe,case if stage=='early' else None)
    rci.require(oil.OilAdmissionEvidenceOwner.prepare is prepare and
        oil.OilTrackletOppositionOwner._apply_track_opposition is oppose and
        oil.DirectedInterfaceTrackletBuilder.resolve is track and FoamEpisodeResolver.resolve is foam,
        'temporary observer not restored')
    if stage!='early':
        record.update(case=case,id=stage+'__'+soi.case_id(case),stage_interventions=operations)
    return record,captured,complete,public,presentation


def run(root, parent, output):
    rci.require(output.is_dir() and not any(output.iterdir()), 'empty managed work directory required')
    original=json.loads((parent/'comparison.json').read_text())
    raw=json.loads((root/rci.SAVED/'raw.json').read_text())
    recipe=rci.JsonRecipeRepository().load(root/rci.BUNDLE/'recipe_snapshot.oilrecipe')
    saved={}
    with gzip.open(parent/'population.jsonl.gz','rt',encoding='utf-8') as stream:
        for line in stream:
            record=json.loads(line)
            if record['id'] in original['representatives']: saved[record['id']]=record
    cases=[('early',saved[name]['case']) for name in original['representatives']]
    cases += [('late_track',saved[name]['case']) for name in original['representatives'][1:3]]
    cases += [('late_foam',c) for c in original['preflight']['cases'] if c['mode']=='all_foam']
    sources={str(p.relative_to(root)):rci.digest(p) for p in (root/'src').rglob('*.py')}
    pins={str(parent.relative_to(root)/p):rci.digest(parent/p) for p in ['comparison.json','population.jsonl.gz']}
    pins.update(original['preflight']['inputs'])
    pre=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
        sources=sources,inputs=pins,cases=cases,script_sha256=rci.digest(Path(__file__)),
        scope='Frozen-history causal interventions; not valid automatic missing-observation policies')
    rci.write_json(output/'preflight.json',pre)
    records=[]; summaries=[]; captures={}; checked=0; events=0
    draw_names={'late_track__'+n for n in original['representatives'][1:3]}
    draw_names.add('late_foam__'+original['representatives'][3])
    for ordinal,(stage,case) in enumerate(cases,1):
        record,capture,complete,public,presentation=execute(raw,recipe,case,stage)
        if stage=='early':
            rci.require(record==saved[record['id']], 'instrumented replay changed original result')
        baseline=saved['baseline']
        if stage=='late_track':
            at=next(r for r in record['rows'] if r['frame_index']==case['frame'])
            rci.require(at['oil_y'] is None if case['index'] is None else
                at['selected'] is None or at['selected']['candidate_offset']!=case['index'],
                'withdrawn tracked member was republished')
        if stage=='late_foam':
            rci.require([r['oil_y'] for r in record['rows']]==[r['oil_y'] for r in baseline['rows']],
                'late Foam unexpectedly rewrote Oil coordinates')
            rci.require(record['rows'][next(i for i,r in enumerate(raw) if r['frame_index']==case['frame'])]['foam_y'] is None,
                'late Foam withdrawal still published a coordinate')
        byframe={r['frame_index']:r['sample'] for r in record['rows']}
        for row,source in zip(record['rows'],raw,strict=True):
            verify.check_row(row,source); checked+=1
        for event in record['events']:
            sample=byframe[event['representative_frame_index']]
            rci.require(sample['timestamp_sec']==event['start_time_sec'],'event identity')
            verify.check_event_levels(event,sample); events+=1
        records.append(record); summaries.append(soi.summarize(record,baseline))
        if stage=='early' or record['id'] in draw_names: captures[record['id']]=capture
        if record['id'] in draw_names:
            from oil_tracker.adapters.reporting.graph_renderer import GraphRenderer
            directory=output/record['id']; directory.mkdir()
            rci.CsvExporter().export(public,directory/'tracking.csv',directory/'events.csv')
            GraphRenderer().render(public,directory/'graphs',recipe,presentation=presentation)
        print(f'{ordinal}/{len(cases)} {record["id"]}',flush=True)
    rci.require(all(rci.digest(root/p)==h for p,h in {**sources,**pins}.items()), 'source/input mutation')
    payload=dict(schema='s11-single-observation-causality-v1',preflight=pre,records=records,captures=captures)
    (output/'readout.json.gz').write_bytes(gzip.compress(json.dumps(payload,ensure_ascii=False,
        sort_keys=True,allow_nan=False).encode(),mtime=0))
    summary=dict(schema=payload['schema'],preflight=pre,cases=summaries,
        retained_capture_cases=list(captures),instrumented_original_replays=4,
        verified_rows=checked,verified_events=events,production_unchanged=True,
        automatic_repair=False,physical_accuracy='NOT_EVALUATED')
    rci.write_json(output/'comparison.json',summary)
    print(json.dumps(dict(runs=len(records),rows=checked,events=events)),flush=True)
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    parser.add_argument('--parent',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    run(args.root.resolve(),args.parent.resolve(),args.output.resolve())


if __name__=='__main__':
    main()
