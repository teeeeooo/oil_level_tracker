import argparse, json, hashlib, zipfile, sys, subprocess
from pathlib import Path
from types import SimpleNamespace
from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind
from oil_tracker.adapters.vision.oil_candidate_evidence import OilCandidateEvidenceIndex, candidate_is_eligible
from oil_tracker.adapters.vision.oil_observation_resolver import _cross_representation_support, _candidate_representation_family
ap=argparse.ArgumentParser(description='Read-only saved-candidate peer-support audit; no detector repair.')
ap.add_argument('--output',type=Path,required=True)
args=ap.parse_args()
R=Path.cwd(); out=args.output.resolve(); out.mkdir(parents=True,exist_ok=False)
sha=lambda b:hashlib.sha256(b).hexdigest()
s4p=R/'docs/70-reference/s11-program-audit-2026-10-11/native-evidence/sample4-current-default.json'
s4=json.loads(s4p.read_text()); pins=s4['source_files']
assert all(sha((R/k).read_bytes())==v for k,v in pins.items())
p=R/'docs/50-diagnostics/s11/2026-10-12-public-compressor-source/pipeline-linkage'
s=json.loads((p/'storage.json').read_text()); z=zipfile.ZipFile(p/'captures.zip')
assert sha((p/'captures.zip').read_bytes())==s['archive_sha256']
for k,v in s['files'].items():
 b=z.read(v['member']); assert len(b)==v['bytes'] and sha(b)==v['sha256'],k
load=lambda n:json.loads(z.read(s['files']['FULL/'+n+'.json']['member']))
s4run=R/'sample/output/s11-p5-default-linkage-20261011-001/none'
s4summary=json.loads((s4run/'summary.json').read_text())
for n in ['raw.json','completed.json']:
 assert sha((s4run/n).read_bytes())==s4summary['outputs'][n]
sources=[('sample4',json.loads((s4run/'raw.json').read_text()),json.loads((s4run/'completed.json').read_text()),json.loads((R/'sample/sample4.oilrecipe').read_text())),('public',load('raw'),load('completed'),load('recipe'))]
result={'schema':'s11-authority-peer-probe-v1','head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'script_sha256':sha(Path(__file__).read_bytes()),'source_receipt_sha256':sha(s4p.read_bytes()),'public_archive_sha256':sha((p/'captures.zip').read_bytes()),'sample4_inputs':{n:sha((s4run/n).read_bytes()) for n in ['raw.json','completed.json','summary.json']},'production_pins_verified':len(pins),'archive_files_verified':len(s['files']),'sources':{}}
for name,raws,finals,recipe in sources:
 glass=SimpleNamespace(detector_settings=SimpleNamespace(**recipe['glasses'][0]['detector_settings']))
 rows=[]; matches=0; mismatch=[]; joins=0
 for raw,final in zip(raws,finals,strict=True):
  cs=[BoundaryCandidate(**{**c,'kind':BoundaryKind(c['kind'])}) for c in raw['candidates']]
  oils=tuple(c for c in cs if c.kind is BoundaryKind.OIL_AIR); ei=OilCandidateEvidenceIndex()
  for ci,c in enumerate(cs):
   if c.kind is not BoundaryKind.OIL_AIR:continue
   fc=final['candidates'][ci]; assert (fc['source'],fc['y'])==(c.source,c.y);joins+=1
   ev=ei.evidence(c);family=_candidate_representation_family(c,ev)
   support=_cross_representation_support(c,oils,glass,evidence_index=ei)
   saved=fc['features'].get('sequence_cross_representation_support')
   if saved is not None:
    if abs(saved-support)<=1e-12:matches+=1
    else:mismatch.append([raw['frame_index'],ci,saved,support])
   peers=[]
   for pi,q in enumerate(cs):
    if q is c or q.kind is not BoundaryKind.OIL_AIR:continue
    qe=ei.evidence(q);qf=_candidate_representation_family(q,qe)
    value=_cross_representation_support(c,(q,),glass,evidence_index=ei)
    if qf!=family and abs(q.y-c.y)<=12:
     peers.append({'index':pi,'source':q.source,'y':q.y,'family':qf,'contribution':value,'eligible':candidate_is_eligible(q,qe),'texture_conflict':qe.material_texture_conflict,'artifact_signature':qe.artifact_signature,'optics':qe.optics_opposition})
   assert abs(max((a['contribution'] for a in peers),default=0)-support)<1e-12
   if name=='public' or raw['frame_index'] in [1140,1200,1260,1275,1305,1320,1485,1560,1620,1665,1680]:
    rows.append({'frame':raw['frame_index'],'candidate':ci,'source':c.source,'y':c.y,'family':family,'support':support,'saved_support':saved,'selected':fc['selected'],'authority':fc['features'].get('sequence_authority_reason'),'own_texture_conflict':ev.material_texture_conflict,'peers':peers})
 result['sources'][name]={'frames':len(raws),'candidate_joins':joins,'support_matches':matches,'support_mismatches':mismatch,'rows':rows}
assert all(sha((R/k).read_bytes())==v for k,v in pins.items())
result['production_unchanged']=True;result['physical_acceptance']='NOT_EVALUATED'
with (out/'peer-probe.json').open('x') as f:json.dump(result,f,indent=2,allow_nan=False)
print(json.dumps({**{k:v for k,v in result.items() if k!='sources'},'sources':{k:{a:b for a,b in v.items() if a!='rows'} for k,v in result['sources'].items()}},indent=2))
print('SELECTED/FIXED PUBLIC ANCHOR ROWS')
for a in result['sources']['public']['rows']:
 if a['frame']==1499 and (a['selected'] or a['y'] in [424,425,427,430]):print(json.dumps(a))
