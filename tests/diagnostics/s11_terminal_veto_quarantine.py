"""Input-local terminal-veto diagnostic. Not a promoted production policy."""
from __future__ import annotations
import argparse
from contextlib import contextmanager
from dataclasses import asdict
import gzip
import json
from pathlib import Path
import subprocess
import time
from unittest.mock import patch
from tests.diagnostics import s11_history_phase_amplification as hpa
from tests.diagnostics import s11_single_observation_influence as soi
from tests.diagnostics import s11_single_observation_verify as verify
from tests.diagnostics import s11_role_consumer_intervention as rci
from oil_tracker.adapters.vision.oil_phase_lifecycle import OilMaterialPhaseLifecycleOwner as Owner
from oil_tracker.adapters.vision.oil_phase_lifecycle import OilFillConfirmationProfile as Profile
from oil_tracker.adapters.reporting.graph_renderer import GraphRenderer


@contextmanager
def quarantine():
    """Veto current-frame output; never promote another completion by pruning a rival."""
    original_profile=Owner._fill_confirmation_profile
    original_transition=Owner._transition_open
    active={}; operations=[]
    def profile(self,chain):
        result=original_profile(self,chain)
        context=active.get(id(self))
        if context is None: return result
        if context['blocked'] is None:
            qualified=[(c,original_profile(self,c)) for c in context['state'].chains.values()]
            vetoes=[(c,p) for c,p in qualified if p is not Profile.NONE and c.last.material_veto]
            context['blocked']=bool(vetoes)
            context['vetoes']=[dict(chain=asdict(c),profile=p.value) for c,p in vetoes]
            context['qualified_owners']=[c.owner for c,p in qualified if p is not Profile.NONE]
        return Profile.NONE if context['blocked'] else result
    def transition(self,state,records,rows_by_frame,first_frame,frame,ambiguous_frames):
        key=id(self); rci.require(key not in active,'reentrant quarantine context')
        context=dict(state=state,blocked=None,vetoes=[],qualified_owners=[])
        active[key]=context
        try:
            result=original_transition(self,state,records,rows_by_frame,first_frame,frame,ambiguous_frames)
        finally: active.pop(key)
        if context['blocked']:
            record=records[frame]
            operations.append(rci.normalize(dict(frame_offset=frame,
                vetoes=context['vetoes'],qualified_owners=context['qualified_owners'],
                ordinary_reason=record.reason,ordinary_phase=state.phase,
                ordinary_allowed=record.allowed_tracklet_ids)))
            record.allowed_tracklet_ids=frozenset()
            record.reason='HPA_TERMINAL_VETO_NOT_FULL'
        return result
    with patch.object(Owner,'_fill_confirmation_profile',profile),patch.object(Owner,'_transition_open',transition):
        yield operations
    rci.require(Owner._fill_confirmation_profile is original_profile and
        Owner._transition_open is original_transition,'quarantine patch leak')


def execute(raw,recipe,case):
    with quarantine() as operations:
        result=soi.execute(raw,recipe,case)
    record=result[0]
    for operation in operations:
        row=record['rows'][operation['frame_offset']]
        rci.require(row['oil_y'] is None,'quarantined frame publishes Oil')
    return (*result,operations)


def run(root,parent,output):
    rci.require(output.is_dir() and not any(output.iterdir()),'empty managed work required')
    prior=json.loads((parent/'comparison.json').read_text())
    raw=json.loads((root/rci.SAVED/'raw.json').read_text())
    recipe=rci.JsonRecipeRepository().load(root/rci.BUNDLE/'recipe_snapshot.oilrecipe')
    saved=[]
    with gzip.open(parent/'population.jsonl.gz','rt',encoding='utf-8') as f:
        for line in f: saved.append(json.loads(line))
    rci.require(len(saved)==246,'original denominator mismatch')
    source_paths=list((root/'src').rglob('*.py'))+[Path(__file__),Path(soi.__file__),Path(rci.__file__),Path(hpa.__file__)]
    sources={str(p.relative_to(root)):rci.digest(p) for p in source_paths}
    inputs={**prior['preflight']['inputs'],str(parent.relative_to(root)/'population.jsonl.gz'):rci.digest(parent/'population.jsonl.gz')}
    rci.require(all(rci.digest(root/p)==v for p,v in inputs.items()),'input drift')
    pre=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),sources=sources,inputs=inputs,
        protocol_sha256=rci.digest(root/'docs/50-diagnostics/s11/2026-10-17-history-phase-amplification.md'),
        cases=[r['case'] for r in saved],controls=prior['preflight']['controls'],scope='generic diagnostic quarantine; not production adoption')
    rci.write_json(output/'preflight.json',pre)
    summaries=[]; checks=0; event_checks=0; ops_count=0; began=time.perf_counter()
    with gzip.open(output/'population.jsonl.gz','xt',encoding='utf-8') as stream:
        for ordinal,original in enumerate(saved):
            record,_,_,_,operations=execute(raw,recipe,original['case'])
            if ordinal==0: rci.require(record==original,'trial changes original baseline')
            for row,source in zip(record['rows'],raw,strict=True): verify.check_row(row,source); checks+=1
            samples={r['frame_index']:r['sample'] for r in record['rows']}
            for event in record['events']:
                verify.check_event_levels(event,samples[event['representative_frame_index']]); event_checks+=1
            summary=soi.summarize(record,saved[0]); paired=soi.summarize(record,original)
            summary.update(quarantined_frames=[o['frame_offset'] for o in operations],
                paired_oil_changed_frames=paired['oil_changed_frames'],paired_foam_changed_frames=paired['foam_changed_frames'],
                paired_public_equal=hpa.public_signature(record)==hpa.public_signature(original))
            summaries.append(summary); ops_count+=len(operations)
            stream.write(json.dumps(dict(record=record,operations=operations),ensure_ascii=False,allow_nan=False)+'\n')
            if ordinal%20==0 or ordinal==245: print(ordinal,len(operations),summary['oil_numeric'],f'{time.perf_counter()-began:.1f}s',flush=True)
    representatives=list(dict.fromkeys(prior['representatives']+soi.representatives(summaries)))
    targets={}
    with gzip.open(output/'population.jsonl.gz','rt',encoding='utf-8') as stream:
        for line in stream:
            payload=json.loads(line)
            if payload['record']['id'] in representatives: targets[payload['record']['id']]=payload
    for name in representatives:
        expected=targets[name]; record,complete,public,presentation,operations=execute(raw,recipe,expected['record']['case'])
        rci.require(record==expected['record'] and operations==expected['operations'],'representative non-determinism')
        directory=output/name; directory.mkdir()
        rci.CsvExporter().export(public,directory/'tracking.csv',directory/'events.csv')
        GraphRenderer().render(public,directory/'graphs',recipe,presentation=presentation)
        witnesses=[dict(frame=d.frame_index,witness=d.debug_metrics['sequence_decision_witness']) for d in complete.detections]
        (directory/'witnesses.json.gz').write_bytes(gzip.compress(json.dumps(rci.normalize(witnesses),ensure_ascii=False,
            sort_keys=True,allow_nan=False).encode(),mtime=0))
    rci.require(all(rci.digest(root/p)==v for p,v in {**sources,**inputs}.items()),'source/input mutation')
    summary=dict(schema='s11-terminal-veto-quarantine-v1',preflight=pre,cases=summaries,representatives=representatives,
        population_cases=len(saved),population_rows=checks,events_verified=event_checks,quarantine_operations=ops_count,
        production_unchanged=True,physical_accuracy='NOT_EVALUATED',report_comprehension='NOT_HUMAN_EVALUATED',seconds=time.perf_counter()-began)
    rci.write_json(output/'comparison.json',summary)
    print('COMPLETE',len(saved),checks,ops_count,flush=True)
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--root',type=Path,default=hpa.ROOT)
    p.add_argument('--parent',type=Path,required=True); p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(); run(a.root.resolve(),a.parent.resolve(),a.output.resolve())


if __name__=='__main__': main()
