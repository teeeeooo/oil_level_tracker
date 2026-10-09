"""Saved-output ablation: current partition faces versus legacy bright-support faces.
No fitting, new tracking, segmentation rerun, interpolation, or public scalar change.
"""
from pathlib import Path
import json,hashlib,sys
from collections import Counter
import numpy as np
ROOT=Path('/Users/sunjaekim/Developer/oil_level_tracker');sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from tests.diagnostics.s11_foam_support_geometry import measure_boundary_faces
OUT=ROOT/'sample/output/s11-design-audit-cc17924-20261009-001';TRIAL=OUT/'partition-trial'
readout=json.loads((TRIAL/'readout.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins={str(p.relative_to(ROOT)):sha(p) for p in [TRIAL/'readout.json',ROOT/'tests/diagnostics/s11_foam_support_geometry.py',*sorted(TRIAL.glob('*.npz'))]}
pre={'id':'reference-partition-center-projection-ablation-v1','base_head':'cc179244c89ea59bd097fa165ea493942629e23e','motivation':'Oil partitions in original/overlay review retain broad upper/lower separation at initial and f1320, yet the legacy support-face query has no output. Test the separately named geometry bottleneck rather than adjusting seed or color rules.', 'rule':'Reconstruct every 4-connected partition-label perimeter with the EXISTING measure_boundary_faces owner. Select only fully visible label1 above label2 shared unit faces at fixed source column X595. Keep exact half-pixel source Y, no ties/gaps filled and no alternative column. This uses CURRENT partition geometry rather than demanding alignment with the old Foam brightness-support boundary.', 'comparison':'Identical stored partition arrays, seeds, masks, frames, source pixels, arithmetic and reference inputs. ONLY candidate geometry provenance changes. Real physical output remains NOT_EVALUATED. R0/R1 numbers are proposal availability, not identity accuracy or successful abstention.', 'stop_rule':'No after-result threshold, mask, role, seed, gap, fit, median, strongest-edge or nearest-point changes. An added face is an appearance proposal, never automatic Oil/Foam authority.', 'inputs':pins}
(OUT/'center-projection-ablation-preflight.json').write_text(json.dumps(pre,indent=2)+'\n')
results=[]
for plan in readout['results']:
 rows=[]
 for r in plan['rows']:
  a=np.load(TRIAL/f'{plan["plan"]}-f{r["frame"]}.npz',allow_pickle=False);l=a['labels'];v=a['visible']
  b=measure_boundary_faces(l.astype(np.uint16),v,origin=(543,798))
  ids=np.flatnonzero((b['owner_pixel_xy'][:,0]==595)&(b['outward_normal_xy'][:,0]==0)&(b['outward_normal_xy'][:,1]==1)&(b['inside_label']==1)&(b['outside_label']==2)&(b['status']==1))
  ys=sorted((b['owner_pixel_xy'][ids,1]+.5).tolist())
  direct=(np.flatnonzero((l[:-1,52]==1)&(l[1:,52]==2)&v[:-1,52]&v[1:,52])+798.5).tolist()
  assert ys==direct
  rows.append({'frame':r['frame'],'initialized':r['initialized'],'r0_legacy_support_candidates':[x['source_y'] for x in r['center_candidates']],'r1_current_partition_candidates':ys,'r1_provisional_y':ys[0] if len(ys)==1 else None,'physical_decision':'NOT_EVALUATED'})
 later=rows[1:];states=Counter('unique' if len(r['r1_current_partition_candidates'])==1 else ('multiple' if r['r1_current_partition_candidates'] else 'none') for r in later);runs=[];run=[]
 for r in rows:
  if r['r1_provisional_y'] is not None:run.append(r)
  elif run:runs.append(run);run=[]
 if run:runs.append(run)
 summary={'plan':plan['plan'],'continuation_frames':len(later),'r1_states':dict(states),'longest_provisional_run_frames':max(map(len,runs),default=0),'runs':[{'first_frame':rs[0]['frame'],'last_frame':rs[-1]['frame'],'frames':len(rs),'y_min':min(x['r1_provisional_y'] for x in rs),'y_max':max(x['r1_provisional_y'] for x in rs)} for rs in runs]}
 results.append({'summary':summary,'rows':rows});print(json.dumps(summary))
for n,h in pins.items():assert sha(ROOT/n)==h
(OUT/'center-projection-ablation.json').write_text(json.dumps({'id':pre['id'],'results':results,'independent_face_projection_checks':sum(len(r['rows']) for r in results),'inputs_unchanged':True,'physical_efficacy':'NOT_EVALUATED','production_change':False},indent=2)+'\n')
