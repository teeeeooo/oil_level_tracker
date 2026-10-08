"""Reproduce the stored pair with current, unchanged sequence owners."""
from pathlib import Path
from dataclasses import asdict
from copy import deepcopy
import hashlib, json, subprocess, sys, time
ROOT = Path('/Users/sunjaekim/Developer/oil_level_tracker')
OUT = Path(__file__).resolve().parent
HEAD = '18885d226a7a7745bc2d062fd750ec263b9c78f6'
PRIOR = ROOT/'sample/output/s11-d2-recipe-artifact-20261008-001'
sys.path.insert(0,str(ROOT/'src'))
from oil_tracker.domain.detection import PhaseDetection, BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind, FillState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.adapters.vision.observation_sequence_resolver import ObservationSequenceResolver
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==HEAD
paths=[*sorted((ROOT/'src').rglob('*.py')), *sorted((ROOT/'sample').glob('*.oiltruth')), Path(__file__)]
for variant,recipe in [('unregistered','baseline.oilrecipe'),('registered_pink822','registered-pink822.oilrecipe')]:
 paths.extend([PRIOR/f'{variant}-raw.json',PRIOR/f'{variant}-completed.json',PRIOR/recipe])
pins={str(p.relative_to(ROOT)):sha(p) for p in paths}
pre=OUT/'sequence-verification-preflight.json'; assert not pre.exists()
pre.write_text(json.dumps({'head':HEAD,'inputs':pins,'mode':'saved raw inputs, current completed resolver, no frame detector or video'},indent=2)+'\n')
def decode(d):
 d=deepcopy(d); d['fill_state']=FillState(d['fill_state'])
 d['candidates']=[BoundaryCandidate(**dict(c,kind=BoundaryKind(c['kind']))) for c in d['candidates']]
 return PhaseDetection(**d)
checks={}
for variant,recipe in [('unregistered','baseline.oilrecipe'),('registered_pink822','registered-pink822.oilrecipe')]:
 raw=json.loads((PRIOR/f'{variant}-raw.json').read_text())
 glass=InspectionRecipe.from_dict(json.loads((PRIOR/recipe).read_text())).glasses[0]
 started=time.monotonic()
 result=ObservationSequenceResolver().resolve([decode(d) for d in raw],glass,glass.initial_state)
 actual=json.loads(json.dumps([asdict(d) for d in result.detections]))
 expected=json.loads((PRIOR/f'{variant}-completed.json').read_text())
 assert len(actual)==113 and actual==expected,variant
 checks[variant]={'complete_detection_count':len(actual),'entire_output_equal':True,'elapsed_sec':time.monotonic()-started,
  'anchors':[{'frame_index':d['frame_index'],'raw_oil_y':d['raw_oil_air_level_y']} for d in actual if d['frame_index'] in (1320,1485,1560)]}
 print(variant,checks[variant],flush=True)
for name,h in pins.items(): assert sha(ROOT/name)==h,name
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==HEAD
receipt={'head':HEAD,'preflight_sha256':sha(pre),'inputs_preserved':True,'input_pin_count':len(pins),'checks':checks,
 'video_read':False,'frame_detector_rerun':False,'completed_resolver_rerun':True,'production_changed':False,'labels_changed':False,
 'field_qualification':False,'scope':'Current-source reproducibility of exposed Mac saved sequences; no challenger efficacy claim.'}
path=OUT/'sequence-verification-receipt.json'; assert not path.exists()
path.write_text(json.dumps(receipt,indent=2)+'\n')
print('COMPLETE',sum(c['complete_detection_count'] for c in checks.values()))
