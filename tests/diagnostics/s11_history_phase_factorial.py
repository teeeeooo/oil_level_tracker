"""HPA-1 row-hypothesis factorial: diagnostic donor data, not production policy."""
from __future__ import annotations
import argparse
from dataclasses import replace
import gzip
import json
from pathlib import Path
import subprocess
from unittest.mock import patch
from tests.diagnostics import s11_history_phase_amplification as hpa
from tests.diagnostics import s11_single_observation_influence as soi
from tests.diagnostics import s11_role_consumer_intervention as rci
from oil_tracker.adapters.vision.oil_interface_tracklets import DirectedInterfaceTrackletBuilder as Builder
from oil_tracker.adapters.reporting.graph_renderer import GraphRenderer

BLOCKS=((1,('y',)),(2,('local_quality',)),(4,('motion_support','motion_coverage')))


def fields_for_mask(mask):
    rci.require(isinstance(mask,int) and 0<=mask<8,'invalid factorial mask')
    return tuple(field for bit,fields in BLOCKS if mask&bit for field in fields)


def transplant_group(hypothesis, donor, mask):
    changes={field:donor[field] for field in fields_for_mask(mask)}
    result=replace(hypothesis,**changes)
    rci.require(result.members is hypothesis.members,'membership copied')
    return result


def correspondence(base,loss):
    changed=[i for i,(a,b) in enumerate(zip(base,loss,strict=True)) if a!=b]
    rci.require(len(changed)==1,'not a one-frame group change')
    offset=changed[0]
    changed_groups=[row for row in loss[offset] if row not in base[offset]]
    rci.require(len(changed_groups)==1,'ambiguous changed group')
    current=changed_groups[0]; members=set(current['members'])
    donors=[row for row in base[offset] if members<=set(row['members'])]
    rci.require(len(donors)==1,'ambiguous donor correspondence')
    donor=donors[0]
    fixed=('anchor_signal','has_physical_proposal','representation_classes','material_conflict')
    rci.require(all(current[f]==donor[f] for f in fixed),'non-factorial field changed')
    return offset,current,donor


def render(output,name,recipe,public,presentation):
    directory=output/name; directory.mkdir()
    rci.CsvExporter().export(public,directory/'tracking.csv',directory/'events.csv')
    GraphRenderer().render(public,directory/'graphs',recipe,presentation=presentation)


def run(root,parent,output):
    rci.require(output.is_dir() and not any(output.iterdir()),'empty managed work required')
    prior=json.loads(gzip.decompress((parent/'readout.json.gz').read_bytes()))
    base=prior['records']['baseline']; case=prior['records']['selected_oil-f001275']['case']
    offset,current,donor=correspondence(prior['captures']['baseline']['row_groups'],
        prior['captures']['selected_oil-f001275']['row_groups'])
    raw=json.loads((root/rci.SAVED/'raw.json').read_text())
    recipe=rci.JsonRecipeRepository().load(root/rci.BUNDLE/'recipe_snapshot.oilrecipe')
    sources=dict(prior['preflight']['sources']); sources[str(Path(__file__).relative_to(root))]=rci.digest(Path(__file__))
    inputs=dict(prior['preflight']['inputs']); inputs[str(parent.relative_to(root)/'readout.json.gz')]=rci.digest(parent/'readout.json.gz')
    rci.require(all(rci.digest(root/p)==v for p,v in {**sources,**inputs}.items()),'source/input drift')
    pre=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),sources=sources,inputs=inputs,
        offset=offset,current=current,donor=donor,blocks=BLOCKS,masks=list(range(8)),
        protocol_sha256=rci.digest(root/'docs/50-diagnostics/s11/2026-10-17-history-phase-amplification.md'))
    rci.write_json(output/'preflight.json',pre)
    records,captures,outcomes={},{},[]
    groups=Builder._row_hypotheses
    for mask in range(8):
        calls=[]
        def wrapper(self,frame_offset,refs):
            hypotheses=groups(self,frame_offset,refs)
            if frame_offset!=offset: return hypotheses
            result=[]
            for h in hypotheses:
                if tuple(r.candidate_offset for r in h.members)==tuple(current['members']):
                    before=hpa.hypothesis_snapshot(h); h=transplant_group(h,donor,mask)
                    calls.append(dict(before=before,after=hpa.hypothesis_snapshot(h),mask=mask))
                result.append(h)
            return tuple(result)
        with patch.object(Builder,'_row_hypotheses',wrapper):
            record,capture,_,_,public,presentation=hpa.execute(raw,recipe,case,capture_details=True)
        rci.require(Builder._row_hypotheses is groups and len(calls)==1,'patch scope')
        if mask==0: rci.require(record==prior['records']['selected_oil-f001275'],'zero mask changed baseline')
        name=f'group_mask_{mask}'; record['id']=name; capture['group_edits']=calls
        records[name]=record; captures[name]=capture
        summary=soi.summarize(record,base); summary['mask']=mask
        summary['qualified_fill_count']=len(capture['qualified_fills'])
        summary['selected_loss_public_equal']=hpa.public_signature(record)==hpa.public_signature(prior['records']['selected_oil-f001275'])
        outcomes.append(summary); render(output,name,recipe,public,presentation)
        print(name,summary['oil_numeric'],summary['foam_numeric'],summary['qualified_fill_count'],summary['oil_changed_elsewhere'],flush=True)
    for arm,target in [('baseline_weights','all_oil-f001320'),('loss_weights','all_oil-f001320')]:
        name=arm+'__'+target
        donor_name='baseline' if arm=='baseline_weights' else target
        mapping={(r['frame_offset'],r['candidate_offset']):(r['source'],r['y'],r['track_opposition'])
            for row in prior['captures'][donor_name]['recurrence_native'] for r in row}
        case=prior['records'][name]['case']
        record,_,_,_,public,presentation=hpa.execute(raw,recipe,case,mapping,capture_details=False)
        record['id']=name
        rci.require(record==prior['records'][name],'publication replay inequality')
        render(output,name,recipe,public,presentation)
    rci.require(all(rci.digest(root/p)==v for p,v in {**sources,**inputs}.items()),'source/input mutation')
    payload=dict(schema='s11-history-phase-factorial-v1',preflight=pre,records=records,captures=captures)
    (output/'readout.json.gz').write_bytes(gzip.compress(json.dumps(payload,ensure_ascii=False,sort_keys=True,allow_nan=False).encode(),mtime=0))
    summary=dict(schema=payload['schema'],preflight=pre,cases=outcomes,windows=8,publication_replays=2,
                 sampled_rows=1130,production_unchanged=True,physical_accuracy='NOT_EVALUATED')
    rci.write_json(output/'comparison.json',summary)
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--root',type=Path,default=hpa.ROOT)
    p.add_argument('--parent',type=Path,required=True); p.add_argument('--output',type=Path,required=True)
    args=p.parse_args(); run(args.root.resolve(),args.parent.resolve(),args.output.resolve())


if __name__=='__main__': main()
