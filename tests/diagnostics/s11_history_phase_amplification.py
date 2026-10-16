"""HPA-1: causal diagnostics, never a deployable baseline-history policy."""
from __future__ import annotations
import argparse
from contextlib import ExitStack
from dataclasses import asdict, replace
import gzip
import json
import math
from pathlib import Path
import subprocess
from unittest.mock import patch
from tests.diagnostics import s11_single_observation_influence as soi
from tests.diagnostics import s11_single_observation_causality as causal
from tests.diagnostics import s11_role_consumer_intervention as rci
from oil_tracker.adapters.vision import oil_observation_resolver as oil
from oil_tracker.adapters.vision import oil_phase_lifecycle as phase

ROOT = Path(__file__).resolve().parents[2]


def penalty_map(frames):
    return {(r.frame_offset, r.candidate_offset):
        (r.candidate.source, r.candidate.y, r.track_opposition)
        for row in frames for r in row}


def transplant_penalties(frames, donor):
    """Change only common-ref scalar opposition; never donate membership/authority."""
    output, edits = [], []
    for refs in frames:
        row = []
        for ref in refs:
            key = (ref.frame_offset, ref.candidate_offset)
            if key in donor:
                source, y, value = donor[key]
                rci.require((source, y) == (ref.candidate.source, ref.candidate.y),
                            'donor identity mismatch')
                rci.require(math.isfinite(value) and 0 <= value <= 1, 'invalid donor scalar')
                if value != ref.track_opposition:
                    edits.append(dict(frame_offset=key[0], candidate_offset=key[1],
                                      source=source, y=y, before=ref.track_opposition, after=value))
                    ref = replace(ref, track_opposition=value)
            row.append(ref)
        output.append(tuple(row))
    return tuple(output), edits


def hypothesis_snapshot(hypothesis):
    return dict(identity=hypothesis.identity, frame_offset=hypothesis.frame_offset,
        y=hypothesis.y, members=[r.candidate_offset for r in hypothesis.members],
        member_identity=[(r.candidate_offset, r.candidate.source, r.candidate.y)
                         for r in hypothesis.members],
        anchor_signal=hypothesis.anchor_signal,
        has_physical_proposal=hypothesis.has_physical_proposal,
        representation_classes=sorted(hypothesis.representation_classes),
        motion_support=hypothesis.motion_support, motion_coverage=hypothesis.motion_coverage,
        material_conflict=hypothesis.material_conflict, local_quality=hypothesis.local_quality)


def track_snapshot(track):
    return dict(identity=track.identity, confirmed=track.confirmed,
        termination_reason=track.termination_reason,
        observations=[{**{k:v for k,v in vars_observation(item).items()},
                       'hypothesis':hypothesis_snapshot(item.hypothesis)}
                      for item in track.observations])


def vars_observation(item):
    from dataclasses import fields
    return {f.name:getattr(item,f.name) for f in fields(item) if f.name != 'hypothesis'}


def execute(raw, recipe, case, donor=None, *, capture_details=True):
    captured = dict(row_groups=[], tracklets=[], confirmations=[], assignments=[], qualified_fills=[])
    prepare = oil.OilAdmissionEvidenceOwner.prepare
    oppose = oil.OilTrackletOppositionOwner._apply_track_opposition
    builder = oil.DirectedInterfaceTrackletBuilder
    groups, finalize, refresh = builder._row_hypotheses, builder._finalize_track, builder._refresh_confirmation
    ambiguity, track_resolve = builder._ambiguities, builder.resolve
    fill = phase.OilMaterialPhaseLifecycleOwner._fill_confirmation_profile
    maps = {}
    def prepare_wrapper(self,*args,**kwargs):
        result=prepare(self,*args,**kwargs)
        captured['admission']=causal.ref_snapshot(result[0]); return result
    def oppose_wrapper(self,*args,**kwargs):
        result=oppose(self,*args,**kwargs)
        maps['native']=penalty_map(result[0])
        captured['recurrence_native']=causal.ref_snapshot(result[0])
        used, edits = transplant_penalties(result[0], donor) if donor is not None else (result[0], [])
        captured['recurrence_used']=causal.ref_snapshot(used)
        captured['scalar_edits']=edits
        return used, result[1], result[2]
    def groups_wrapper(self,*args,**kwargs):
        result=groups(self,*args,**kwargs)
        if capture_details: captured['row_groups'].append([hypothesis_snapshot(h) for h in result])
        return result
    def finalize_wrapper(self,track):
        result=finalize(self,track)
        if capture_details: captured['tracklets'].append(track_snapshot(track))
        return result
    def refresh_wrapper(self,track):
        before=track.confirmed
        result=refresh(self,track)
        if capture_details and track.confirmed != before:
            witness=self._cached_confirmation_evidence(track,len(track.observations)-1)
            captured['confirmations'].append(dict(tracklet=track.identity,
                frame_offset=track.last.hypothesis.frame_offset, before=before,
                after=track.confirmed, witness=asdict(witness)))
        return result
    def ambiguity_wrapper(self,pairs):
        result=ambiguity(self,pairs)
        if capture_details and pairs:
            captured['assignments'].append(dict(frame_offset=pairs[0][4].frame_offset,
                pairs=[dict(cost=v[0], tracklet=v[1], row=v[2], confirmed=v[3].confirmed,
                    prior=hypothesis_snapshot(v[3].last.hypothesis),
                    current=hypothesis_snapshot(v[4])) for v in pairs],
                conflicted_tracks=[t.identity for t in result[0]], conflicted_rows=sorted(result[1])))
        return result
    def track_wrapper(self,*args,**kwargs):
        result=track_resolve(self,*args,**kwargs)
        captured['tracked']=causal.ref_snapshot(result.refs_by_frame)
        return result
    def fill_wrapper(self,chain):
        result=fill(self,chain)
        if capture_details and result is not phase.OilFillConfirmationProfile.NONE:
            captured['qualified_fills'].append(dict(chain=asdict(chain), profile=result,
                                                     policy=asdict(self.policy)))
        return result
    methods=[(oil.OilAdmissionEvidenceOwner,'prepare',prepare_wrapper),
        (oil.OilTrackletOppositionOwner,'_apply_track_opposition',oppose_wrapper),
        (builder,'_row_hypotheses',groups_wrapper),(builder,'_finalize_track',finalize_wrapper),
        (builder,'_refresh_confirmation',refresh_wrapper),(builder,'_ambiguities',ambiguity_wrapper),
        (builder,'resolve',track_wrapper),
        (phase.OilMaterialPhaseLifecycleOwner,'_fill_confirmation_profile',fill_wrapper)]
    originals=[getattr(target,name) for target,name,_ in methods]
    with ExitStack() as stack:
        for target,name,wrapper in methods: stack.enter_context(patch.object(target,name,wrapper))
        record,complete,public,presentation=soi.execute(raw,recipe,case)
    rci.require(all(getattr(t,n) is old for (t,n,_),old in zip(methods,originals,strict=True)),
                'diagnostic patch leak')
    return record,rci.normalize(captured),maps['native'],complete,public,presentation


def public_signature(record):
    return {key:record[key] for key in ('events','presentation')} | {
        'samples':[row['sample'] for row in record['rows']],
        'coordinates':[(row['oil_y'],row['foam_y']) for row in record['rows']]}


def run(root, parent, output):
    rci.require(output.is_dir() and not any(output.iterdir()), 'empty managed work required')
    prior=json.loads((parent/'comparison.json').read_text())
    saved={}
    with gzip.open(parent/'population.jsonl.gz','rt',encoding='utf-8') as stream:
        for line in stream:
            row=json.loads(line)
            if row['id'] in prior['representatives']: saved[row['id']]=row
    raw=json.loads((root/rci.SAVED/'raw.json').read_text())
    expected=json.loads((root/rci.SAVED/'completed.json').read_text())
    recipe=rci.JsonRecipeRepository().load(root/rci.BUNDLE/'recipe_snapshot.oilrecipe')
    sources={str(p.relative_to(root)):rci.digest(p) for p in (root/'src').rglob('*.py')}
    sources.update({str(p.relative_to(root)):rci.digest(p) for p in [Path(__file__),Path(soi.__file__),Path(causal.__file__),Path(rci.__file__)]})
    inputs={**prior['preflight']['inputs'],str(parent.relative_to(root)/'comparison.json'):rci.digest(parent/'comparison.json'),
            str(parent.relative_to(root)/'population.jsonl.gz'):rci.digest(parent/'population.jsonl.gz')}
    rci.require(all(rci.digest(root/p)==h for p,h in inputs.items()), 'input drift')
    pre=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
        sources=sources,inputs=inputs,protocol_sha256=rci.digest(root/'docs/50-diagnostics/s11/2026-10-17-history-phase-amplification.md'),
        original_cases=prior['representatives'],scope='scalar transplant diagnostic, no original track history')
    rci.write_json(output/'preflight.json',pre)
    records, captures, maps, summaries = {}, {}, {}, []
    for name in prior['representatives']:
        record,capture,mapping,complete,_,_=execute(raw,recipe,saved[name]['case'])
        rci.require(record==saved[name], 'original replay inequality')
        if name=='baseline': rci.require(rci.normalize([asdict(d) for d in complete.detections])==expected, 'complete baseline inequality')
        records[name]=record; captures[name]=capture; maps[name]=mapping
        summaries.append(soi.summarize(record,saved['baseline']))
        print('reproduced',name,flush=True)
    outcomes=[]
    for name in prior['representatives'][1:]:
        for arm,case,donor,target in [('baseline_weights',saved[name]['case'],maps['baseline'],name),
                                     ('loss_weights',None,maps[name],'baseline')]:
            record,capture,_,_,_,_=execute(raw,recipe,case,donor,capture_details=False)
            record['id']=arm+'__'+name
            records[record['id']]=record; captures[record['id']]=capture
            summary=soi.summarize(record,saved['baseline']); summaries.append(summary)
            outcomes.append(dict(id=record['id'],compared_to=target,
                public_equal=public_signature(record)==public_signature(saved[target]),
                scalar_edits=len(capture['scalar_edits']),
                oil_numeric=summary['oil_numeric'],foam_numeric=summary['foam_numeric'],
                changed_oil_elsewhere=summary['oil_changed_elsewhere']))
            print(outcomes[-1],flush=True)
    rci.require(all(rci.digest(root/p)==h for p,h in {**sources,**inputs}.items()), 'source/input mutation')
    payload=dict(schema='s11-history-phase-amplification-v1',preflight=pre,records=records,captures=captures)
    (output/'readout.json.gz').write_bytes(gzip.compress(json.dumps(payload,ensure_ascii=False,
        sort_keys=True,allow_nan=False).encode(),mtime=0))
    summary=dict(schema=payload['schema'],preflight=pre,outcomes=outcomes,cases=summaries,
        windows=len(records),sampled_rows=len(records)*len(raw),production_unchanged=True,
        physical_accuracy='NOT_EVALUATED',report_comprehension='NOT_HUMAN_EVALUATED')
    rci.write_json(output/'comparison.json',summary)
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--parent',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(); run(args.root.resolve(),args.parent.resolve(),args.output.resolve())


if __name__=='__main__': main()
