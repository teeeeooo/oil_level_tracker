"""Frozen local XY measurement-exclusion experiment; no production edits."""
from pathlib import Path
from dataclasses import asdict, replace
from copy import deepcopy
import hashlib, json, sys, time
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from tests.diagnostics.s11_report_observability_replay import _session, QUALIFICATION_WINDOWS, _tracking_fingerprint
from oil_tracker.domain.geometry import ExclusionZone, Rect
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.application.services.report_presentation import build_report_presentation
from oil_tracker.adapters.storage.output_bundle_store import OutputBundleStore

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def stable(v):
    if isinstance(v,dict): return {k:stable(x) for k,x in v.items() if k!='run_id'}
    if isinstance(v,(list,tuple)): return [stable(x) for x in v]
    return v

def save(path,value):
    if path.exists(): raise FileExistsError(path)
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False,default=lambda x:x.value,allow_nan=False)+'\n')

class Recorder(OpenCvPhaseDetector):
    def __init__(self):
        super().__init__(); self.raw=[]; self.completed=[]
    def detect(self,*a,**kw):
        d,art=super().detect(*a,**kw)
        self.raw.append(deepcopy(asdict(d)))
        return d,art
    def resolve_sequence(self,*a,**kw):
        r=super().resolve_sequence(*a,**kw)
        self.completed.extend(deepcopy(asdict(d)) for d in r.detections)
        return r

pre=json.loads((OUT/'preflight.json').read_text())
for n,h in {**pre['inputs'],**pre['source_files']}.items():
    assert sha(ROOT/n)==h,n
save(OUT/'runner-pin.json',{'runner_sha256':sha(Path(__file__)),'preflight_sha256':sha(OUT/'preflight.json')})
summaries=[]
jobs=[(s,'baseline') for s in QUALIFICATION_WINDOWS]+[('sample4','local_xy_rectangle')]
for sample,variant in jobs:
    directory=OUT/(sample+'-'+variant); directory.mkdir(exist_ok=False)
    recipe,session=_session(sample,ROOT/'sample'/f'{sample}.mp4',directory,*QUALIFICATION_WINDOWS[sample],run_label='D2 local XY experiment',run_note=variant)
    if variant=='local_xy_rectangle':
        x0,y0,x1,y1=pre['rect_source_xyxy']
        zone=ExclusionZone('d2-local-xy-experiment',Rect(x0,y0,x1-x0,y1-y0),'D2 local XY','Sampling withdrawal only; not whole-box physical truth')
        for g in recipe.glasses:
            g.geometry=replace(g.geometry,exclusions=(*g.geometry.exclusions,zone))
    assert all(not g.geometry.artifact_templates for g in recipe.glasses)
    save(directory/'recipe.oilrecipe',recipe.to_dict())
    before=recipe.to_dict(); detector=Recorder(); start=time.monotonic()
    result=AnalysisPipeline(OpenCvVideoReader,detector,RecipeValidationService()).run(recipe,session)
    assert not result.errors, result.errors
    assert before==recipe.to_dict()
    rows=stable([asdict(s) for g in result.glass_results for s in g.samples])
    assert len(rows)==len(detector.raw)==len(detector.completed)
    save(directory/'raw.json',detector.raw)
    save(directory/'completed.json',detector.completed)
    save(directory/'tracking.json',rows)
    save(directory/'report.json',stable(asdict(build_report_presentation(result,recipe))))
    summary={'sample':sample,'variant':variant,'results':len(rows),'fingerprint':_tracking_fingerprint(result),'numeric_oil':sum(r['raw_oil_air_level_y'] is not None for r in rows),'numeric_foam':sum(r['raw_foam_front_y'] is not None for r in rows),'elapsed_sec':time.monotonic()-start}
    if sample=='sample4':
        bundle=OutputBundleStore().write_bundle(result,recipe,session,directory)
        summary['report_bundle']=str(bundle)
    save(directory/'summary.json',summary); summaries.append(summary)
    print(json.dumps(summary,default=str),flush=True)

fields=('raw_oil_air_level_y','raw_foam_front_y','oil_is_valid','foam_is_valid','fill_state')
a=json.loads((OUT/'sample4-baseline/tracking.json').read_text())
b=json.loads((OUT/'sample4-local_xy_rectangle/tracking.json').read_text())
changes=[]
for ra,rb in zip(a,b,strict=True):
    assert ra['frame_index']==rb['frame_index']
    delta={k:{'baseline':ra[k],'local_xy':rb[k]} for k in fields if ra[k]!=rb[k]}
    if delta: changes.append({'frame_index':ra['frame_index'],'time_sec':ra['timestamp_sec'],'changes':delta})
checkpoints=[]
for f,i in pre['controls']['targets']:
    ra=next(r for r in a if r['frame_index']==f); rb=next(r for r in b if r['frame_index']==f)
    checkpoints.append({'frame_index':f,'baseline_reviewed_candidate_input_index':i,'baseline_oil':ra['raw_oil_air_level_y'],'local_xy_oil':rb['raw_oil_air_level_y'],'baseline_foam':ra['raw_foam_front_y'],'local_xy_foam':rb['raw_foam_front_y'],'meaning':'numeric output only; changed candidate indices/coordinates do not inherit physical truth'})
for n,h in {**pre['inputs'],**pre['source_files']}.items(): assert sha(ROOT/n)==h,n
save(OUT/'results.json',{'status':'COMPLETE_UNPROMOTED','source_head':pre['source_head'],'preflight_sha256':sha(OUT/'preflight.json'),'runner_sha256':sha(Path(__file__)),'original_inputs_and_source_unchanged':True,'runs':summaries,'public_changes':changes,'reviewed_frame_readout':checkpoints,'source_scope':'Mac original media and existing reviewed evidence; no Windows media/run','limitations':['current pooled support rules unchanged','no mask-aware convolution or balanced upper/lower-column rule added','registered rectangle is sampling-policy counterfactual, not transferred physical label','no independent holdout','no detector or field acceptance']})
print('COMPLETE',len(changes),'public changes',flush=True)
