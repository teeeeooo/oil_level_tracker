"""Source-owned locality and measurement-dependency controls, not a classifier."""
from pathlib import Path
from dataclasses import replace
import hashlib,json,sys
import cv2,numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.geometry import ExclusionZone,Rect
from oil_tracker.adapters.vision.geometry_masks import build_mask_bundle
from oil_tracker.adapters.vision.preprocessing import preprocess
from oil_tracker.adapters.vision.oil_supplemental_path import _phase_band_means,phase_transition_support
from oil_tracker.adapters.vision.oil_material_path import _sector_profile

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,v):
    p=OUT/name; assert not p.exists(),p
    p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')

def paired_means(u,l,uv,lv,r,w):
    # Proposed safety control only: not wired to any candidate/sequence owner.
    xs=np.all(uv,axis=0)&np.all(lv,axis=0)
    if r*int(xs.sum())<max(2,int(r*max(1,w)*.25)): return None
    return float(u[:,xs].mean()),float(l[:,xs].mean())

save('probe-preflight.json',{'runner_sha256':sha(Path(__file__)),'frozen_primary_preflight_sha256':sha(OUT/'preflight.json'),'controls':['rectangular locality','same X below excluded Y','raw pixels unchanged','no-template-rejection','all-masked native abstention','horizontal-ramp unequal-aperture counterexample','paired common-X null contrast','true-step preservation','no common-X abstention','zero-fill artificial Sobel edge','preprocessing noninterference counterexample'],'real_points':[[1140,844],[1200,841],[1260,839],[1275,835],[1320,844],[1320,822],[1485,836],[1560,833]],'meaning':'sampling facts and synthetic guard requirements; no new physical or scalar labels'})
recipe=InspectionRecipe.from_dict(json.loads((ROOT/'sample/sample4.oilrecipe').read_text()))
glass=recipe.glasses[0]
zone=ExclusionZone('d2-local-xy-experiment',Rect(563,816,35,12))
masked=replace(glass,geometry=replace(glass.geometry,exclusions=(*glass.geometry.exclusions,zone)))
cap=cv2.VideoCapture(str(ROOT/'sample/sample4.mp4'))
cap.set(cv2.CAP_PROP_POS_FRAMES,1320);ok,frame=cap.read();assert ok
b=build_mask_bundle(frame,glass);m=build_mask_bundle(frame,masked)
x,y=b.crop_origin
rect=np.zeros_like(b.effective_mask,bool);rect[816-y:828-y,563-x:598-x]=True
changed=b.effective_mask!=m.effective_mask
checks=[]
def check(n,c):
    assert bool(c),n;checks.append({'name':n,'status':'PASS'})
check('changes_only_inside_xy',not np.any(changed&~rect))
check('all_previously_usable_scope_pixels_excluded',np.array_equal(changed,rect&(b.effective_mask>0)))
check('same_x_other_y_unchanged',np.array_equal(b.effective_mask[844-y,563-x:598-x],m.effective_mask[844-y,563-x:598-x]))
check('raw_crop_not_modified',np.array_equal(b.crop,m.crop))
check('no_template_rejection',not masked.geometry.artifact_templates)
check('all_masked_native_profile_unavailable',_sector_profile(np.zeros((40,20),np.uint8),np.zeros((40,20),bool),0,20,material_evidence_map=None) is None)
r,w=3,12
u=np.tile(np.arange(w,dtype=np.float32)*12,(r,1));l=u.copy()
uv=np.ones((r,w),bool);lv=uv.copy();uv[:,:4]=False
old=_phase_band_means(u,l,uv,lv,r,w);pair=paired_means(u,l,uv,lv,r,w)
check('unequal_aperture_makes_false_contrast',old[1]-old[0]==-24.)
check('paired_aperture_has_zero_false_contrast',pair[1]-pair[0]==0.)
step=paired_means(u,l+40,uv,lv,r,w)
check('paired_aperture_preserves_real_step',step[1]-step[0]==40.)
a=np.zeros((r,w),bool);a[:,:4]=True;z=np.zeros_like(a);z[:,8:]=True
check('disjoint_column_support_is_unavailable',paired_means(u,l,a,z,r,w) is None)
raw=np.full((64,64),128,np.uint8);filled=raw.copy();filled[20:28,20:40]=0
check('zero_fill_creates_nonexistent_gradient',not np.any(cv2.Sobel(raw,cv2.CV_32F,0,1)) and np.any(cv2.Sobel(filled,cv2.CV_32F,0,1)))
raw2=np.full((64,64,3),64,np.uint8);changed2=raw2.copy();changed2[20:28,20:40]=180
emask=np.full((64,64),255,np.uint8);emask[20:28,20:40]=0
p1=preprocess(raw2,emask,glass.detector_settings);p2=preprocess(changed2,emask,glass.detector_settings)
leak={name:int(np.count_nonzero((getattr(p1,name)!=getattr(p2,name))&(emask>0))) for name in ('gray','normalized','blurred','sobel_y_abs','canny','horizontal_mask')}
check('upstream_dependencies_can_survive_sampling_exclusion',leak['gray']==0 and leak['blurred']>0)
points=json.loads((OUT/'probe-preflight.json').read_text())['real_points']
records=[];tiles=[];seen=set()
for f,cy in points:
    cap.set(cv2.CAP_PROP_POS_FRAMES,f);ok,fr=cap.read();assert ok
    b=build_mask_bundle(fr,glass);m=build_mask_bundle(fr,masked)
    pb=preprocess(b.crop,b.effective_mask,glass.detector_settings);pm=preprocess(m.crop,m.effective_mask,glass.detector_settings)
    oldrows=phase_transition_support(pb.normalized,(b.effective_mask>0)&(pb.glare_mask==0),local_y=cy-y,crop_origin=b.crop_origin)
    newrows=phase_transition_support(pm.normalized,(m.effective_mask>0)&(pm.glare_mask==0),local_y=cy-y,crop_origin=m.crop_origin)
    records.append({'frame_index':f,'source_y':cy,'baseline':oldrows,'masked':newrows,'scope':'measurement readout only; not candidate correspondence'})
    if f not in seen:
        seen.add(f);img=Image.fromarray(cv2.cvtColor(b.crop,cv2.COLOR_BGR2RGB)).resize((312,312),Image.Resampling.NEAREST)
        tile=Image.new('RGB',(328,350),'white');tile.paste(img,(8,30));ImageDraw.Draw(tile).text((8,8),f'f{f} / {f/30:g} s - original ROI',fill='black');tiles.append(tile)
cap.release()
montage=Image.new('RGB',(328*4,350*2),'white')
for i,tile in enumerate(tiles):montage.paste(tile,((i%4)*328,(i//4)*350))
montage.save(OUT/'sample4-original-controls.jpg',quality=90)
save('real-support-readout.json',records)
save('contract-results.json',{'checks':checks,'check_count':len(checks),'rect_nominal_area':420,'effective_pixels_removed_at_f1320':int(changed.sum()),'frame_shape':list(frame.shape),'crop_origin':list(b.crop_origin),'crop_shape':list(b.crop.shape),'same_x_reusable_at_source_y':844,'synthetic_false_contrast':old[1]-old[0],'synthetic_paired_contrast':pair[1]-pair[0],'synthetic_true_step_contrast':step[1]-step[0],'outside_mask_changed_values_when_only_excluded_pixels_change':leak,'interpretation':'Existing exclusion is spatial sampling exclusion, not full preprocessing dependency removal. Paired aperture is a numerical guard, not physical identity.'})
print(json.dumps(json.loads((OUT/'contract-results.json').read_text()),indent=2),flush=True)
