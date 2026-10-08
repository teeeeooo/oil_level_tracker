"""No-exclusion control isolates the paired-aperture numerical guard."""
from pathlib import Path
from dataclasses import asdict
from copy import deepcopy
from unittest.mock import patch
import hashlib,json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from tests.diagnostics.s11_report_observability_replay import _session,_tracking_fingerprint
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.application.services.report_presentation import build_report_presentation
from oil_tracker.adapters.vision import oil_supplemental_path as supplemental
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def stable(v):
 if isinstance(v,dict):return {k:stable(x) for k,x in v.items() if k!='run_id'}
 if isinstance(v,(tuple,list)):return [stable(x) for x in v]
 return v
def save(p,v):
 assert not p.exists(),p
 p.write_text(json.dumps(v,indent=2,allow_nan=False,default=lambda v:v.value)+'\n')
pre=json.loads((OUT/'preflight.json').read_text())
save(OUT/'pair-control-preflight.json',{'source_head':pre['source_head'],'runner_sha256':sha(Path(__file__)),'purpose':'paired phase means also affect existing ellipse/glare support without the XY mask; this no-mask ablation is required to avoid attributing all changes to exclusion','variant':'paired_phase_no_exclusion','paired_rule':'same complete common-X and same existing 25-percent minimum area as oil_measurement_paired_phase','window':[0,56],'role':'exposed regression, not holdout','promotion':False})
class Recorder(OpenCvPhaseDetector):
 def __init__(self):super().__init__();self.raw=[];self.completed=[]
 def detect(self,*a,**kw):
  d,art=super().detect(*a,**kw);self.raw.append(deepcopy(asdict(d)));return d,art
 def resolve_sequence(self,*a,**kw):
  r=super().resolve_sequence(*a,**kw);self.completed.extend(deepcopy(asdict(d)) for d in r.detections);return r

def paired(u,l,uv,lv,r,w):
 good=np.all(uv,axis=0)&np.all(lv,axis=0)
 if r*int(good.sum())<max(2,int(r*max(1,w)*.25)):return None
 return float(u[:,good].mean()),float(l[:,good].mean())
variant='paired_phase_no_exclusion';directory=OUT/('sample4-'+variant);directory.mkdir(exist_ok=False)
recipe,session=_session('sample4',ROOT/'sample/sample4.mp4',directory,0,56,run_label='D2 paired aperture no mask',run_note=variant)
original=recipe.to_dict();det=Recorder();t=time.monotonic()
with patch.object(supplemental,'_phase_band_means',paired):result=AnalysisPipeline(OpenCvVideoReader,det,RecipeValidationService()).run(recipe,session)
assert not result.errors and original==recipe.to_dict()
rows=stable([asdict(s) for g in result.glass_results for s in g.samples]);assert len(rows)==len(det.raw)==len(det.completed)==113
for n,v in [('raw',det.raw),('completed',det.completed),('tracking',rows),('report',stable(asdict(build_report_presentation(result,recipe))))]:save(directory/(n+'.json'),v)
info={'variant':variant,'results':len(rows),'numeric_oil':sum(r['raw_oil_air_level_y'] is not None for r in rows),'numeric_foam':sum(r['raw_foam_front_y'] is not None for r in rows),'fingerprint':_tracking_fingerprint(result),'elapsed_sec':time.monotonic()-t}
for n,h in {**pre['inputs'],**pre['source_files']}.items():assert sha(ROOT/n)==h,n
save(directory/'summary.json',info);print(json.dumps(info),flush=True)
