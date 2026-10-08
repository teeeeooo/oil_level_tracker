"""Exploratory owner ablation after shared-mask result; not production wiring."""
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
from oil_tracker.adapters.vision import phase_candidate_assembler as assembler
from oil_tracker.adapters.vision import oil_supplemental_path as supplemental

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def stable(v):
    if isinstance(v,dict): return {k:stable(x) for k,x in v.items() if k!='run_id'}
    if isinstance(v,(tuple,list)): return [stable(x) for x in v]
    return v

def save(p,v):
    assert not p.exists(),p
    p.write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False,default=lambda v:v.value)+'\n')

pre=json.loads((OUT/'preflight.json').read_text());old=json.loads((OUT/'results.json').read_text())
contract={'source_head':pre['source_head'],'runner_sha256':sha(Path(__file__)),'primary_result_sha256':sha(OUT/'results.json'),'primary_preflight_sha256':sha(OUT/'preflight.json'),'exposure':'Designed after shared-mask failure; both new variants frozen before their results; exposed regression only','rect':pre['rect_source_xyxy'],'variants':['oil_measurement_only','oil_measurement_paired_phase'],'measurement_owners':['phase_candidate_assembler.generate_material_path_candidates (both material/raster)','phase_candidate_assembler.generate_phase_transition_candidates'],'unchanged':['Oil hypothesis acquisition','Foam pixel/material/motion/temporal owners','shared preprocess','other Oil proposal families','original enrichment and static maps','authority,tracklet,phase,selector','all thresholds and original recipes'],'variant_difference':'second variant only replaces independent upper/lower phase averages with complete-common-X averages; same existing minimum-area rule, no new score or threshold','limits':'measurement-only aperture withdrawal, NOT pixel influence removal or physical classification; no template rejection; metadata/spatial signatures and unmodified context can still sample structure','window':[0,56],'cadence_fps':2,'controls':pre['controls']}
save(OUT/'measurement-scope-preflight.json',contract)

class Recorder(OpenCvPhaseDetector):
    def __init__(self): super().__init__();self.raw=[];self.completed=[]
    def detect(self,*a,**kw):
        d,art=super().detect(*a,**kw);self.raw.append(deepcopy(asdict(d)));return d,art
    def resolve_sequence(self,*a,**kw):
        r=super().resolve_sequence(*a,**kw);self.completed.extend(deepcopy(asdict(d)) for d in r.detections);return r

def paired(u,l,uv,lv,r,w):
    good=np.all(uv,axis=0)&np.all(lv,axis=0)
    if r*int(good.sum())<max(2,int(r*max(1,w)*.25)): return None
    return float(u[:,good].mean()),float(l[:,good].mean())

origmaterial=assembler.generate_material_path_candidates;origphase=assembler.generate_phase_transition_candidates
summary=[]
for variant in contract['variants']:
    directory=OUT/('sample4-'+variant);directory.mkdir(exist_ok=False)
    recipe,session=_session('sample4',ROOT/'sample/sample4.mp4',directory,0,56,run_label='D2 measurement scope',run_note=variant)
    g=recipe.glasses[0];bounds=g.geometry.crop_roi;ox,oy=int(np.floor(bounds.x)),int(np.floor(bounds.y))
    assert not g.geometry.artifact_templates and not g.geometry.exclusions
    operation_records=[]
    def masked_call(fn,pre,mask,*a,**kw):
        x0,y0,x1,y1=contract['rect'];h,w=mask.shape
        aperture=mask.copy();lx0,ly0,lx1,ly1=max(0,x0-ox),max(0,y0-oy),min(w,x1-ox),min(h,y1-oy)
        if lx1>lx0 and ly1>ly0:aperture[ly0:ly1,lx0:lx1]=0
        result=fn(pre,aperture,*a,**kw)
        operation_records.append({'owner':fn.__name__,'removed':int(np.count_nonzero(mask!=aperture)),'candidate_count':len(result)})
        return result
    def material(pre,mask,*a,**kw):return masked_call(origmaterial,pre,mask,*a,**kw)
    def phase(pre,mask,*a,**kw):return masked_call(origphase,pre,mask,*a,**kw)
    original=recipe.to_dict();det=Recorder();t=time.monotonic()
    with patch.object(assembler,'generate_material_path_candidates',material),patch.object(assembler,'generate_phase_transition_candidates',phase):
        if variant=='oil_measurement_paired_phase':
            with patch.object(supplemental,'_phase_band_means',paired):
                result=AnalysisPipeline(OpenCvVideoReader,det,RecipeValidationService()).run(recipe,session)
        else:result=AnalysisPipeline(OpenCvVideoReader,det,RecipeValidationService()).run(recipe,session)
    assert not result.errors,result.errors
    assert original==recipe.to_dict()
    rows=stable([asdict(s) for gr in result.glass_results for s in gr.samples]);assert len(rows)==len(det.raw)==len(det.completed)==113
    for name,value in [('raw',det.raw),('completed',det.completed),('tracking',rows),('report',stable(asdict(build_report_presentation(result,recipe)))),('operations',operation_records)]:save(directory/(name+'.json'),value)
    info={'variant':variant,'results':len(rows),'numeric_oil':sum(r['raw_oil_air_level_y'] is not None for r in rows),'numeric_foam':sum(r['raw_foam_front_y'] is not None for r in rows),'fingerprint':_tracking_fingerprint(result),'elapsed_sec':time.monotonic()-t,'operation_calls':len(operation_records)}
    save(directory/'summary.json',info);summary.append(info);print(json.dumps(info),flush=True)
for n,h in {**pre['inputs'],**pre['source_files']}.items():assert sha(ROOT/n)==h,n
save(OUT/'measurement-scope-results.json',{'status':'COMPLETE_UNPROMOTED','preflight_sha256':sha(OUT/'measurement-scope-preflight.json'),'runs':summary,'source_and_original_inputs_unchanged':True,'field_acceptance':False})
print('COMPLETE owner-scope comparison',flush=True)
