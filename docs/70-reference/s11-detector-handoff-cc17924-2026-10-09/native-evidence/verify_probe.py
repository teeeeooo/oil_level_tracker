"""Independent arithmetic and evidence verification of the frozen offline probe."""
from pathlib import Path
import importlib.util, json, hashlib, sys
from collections import deque, Counter
import numpy as np
ROOT=Path('/Users/sunjaekim/Developer/oil_level_tracker')
OUT=ROOT/'sample/output/s11-design-audit-cc17924-20261009-001'
spec=importlib.util.spec_from_file_location('probe',OUT/'side_partition_probe.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
checks=[]
def check(name,fn):
    fn();checks.append({'name':name,'result':'PASS'})
def same(a,b):
    assert np.array_equal(a,b)
def oracle(im,vis,seeds):
    # Threshold reachability, independently of Dijkstra / priority queues.
    h,w=vis.shape;ans=np.full((h,w),256,np.uint16);pix=im.astype(int)
    levels={0}
    for y,x in np.argwhere(vis):
        for yy,xx in ((y+1,x),(y,x+1)):
            if yy<h and xx<w and vis[yy,xx]: levels.add(int(np.abs(pix[y,x]-pix[yy,xx]).max()))
    for level in sorted(levels):
        seen=set((y,x) for y,x in seeds if 0<=y<h and 0<=x<w and vis[y,x]);todo=deque(seen)
        while todo:
            y,x=todo.popleft()
            for yy,xx in ((y+1,x),(y-1,x),(y,x+1),(y,x-1)):
                if 0<=yy<h and 0<=xx<w and vis[yy,xx] and (yy,xx) not in seen and np.abs(pix[y,x]-pix[yy,xx]).max()<=level:
                    seen.add((yy,xx));todo.append((yy,xx))
        for y,x in seen:ans[y,x]=min(int(ans[y,x]),level)
    return ans
rng=np.random.default_rng(472910)
def random_oracle():
    for _ in range(32):
        im=rng.integers(0,256,(6,7,3),dtype=np.uint8);vis=rng.random((6,7))>.25
        same(p.minimax(im,vis,[(0,0),(4,5)]),oracle(im,vis,[(0,0),(4,5)]))
check('32 small random graphs equal threshold-reachability oracle',random_oracle)
im=np.zeros((9,11,3),np.uint8);im[5:]=180;v=np.ones((9,11),bool)
def split():
    l,_,_=p.partition(im,v,[(2,5)],[(7,5)]);assert np.all(l[:5]==1) and np.all(l[5:]==2)
check('ideal two-side current partition',split)
def constant():
    l,_,_=p.partition(np.zeros_like(im),v,[(2,5)],[(7,5)]);assert not l.any()
check('constant appearance is all unresolved',constant)
def missing():
    l,_,_=p.partition(im,v,[(2,5)],[]);assert not l.any()
check('missing side never yields a material decision',missing)
def mask():
    vv=v.copy();vv[4]=False;d=p.minimax(im,vv,[(2,5)]);assert np.all(d[4:]==256)
check('mask barrier blocks all graph paths',mask)
def swap():
    l,_,_=p.partition(im,v,[(2,5)],[(7,5)]);r,_,_=p.partition(im,v,[(7,5)],[(2,5)]);same(r,np.where(l>0,3-l,0))
check('role swap exchanges labels without changing geometry',swap)
check('deterministic repeated distances',lambda:same(p.minimax(im,v,[(2,5)]),p.minimax(im,v,[(2,5)])))
def translation():
    shifted=np.pad(im,((0,0),(2,0),(0,0)));vv=np.pad(v,((0,0),(2,0)),constant_values=False)
    same(p.minimax(shifted,vv,[(2,7)])[:,2:],p.minimax(im,v,[(2,5)]))
check('coordinate translation with censored padding',translation)
def invalid():
    try:p.minimax(np.zeros((300,300,3),np.uint8),np.ones((300,300),bool),[(0,0)])
    except ValueError:return
    raise AssertionError('oversized raster accepted')
check('resource bound rejects oversized input',invalid)
trial=json.loads((OUT/'partition-trial/readout.json').read_text());stats=[];face_checks=0
for plan in trial['results']:
    rows=plan['rows'];states=Counter(r['state'] for r in rows[1:]);longest=0;run=0;center_causes=Counter()
    for r in rows:
        run=run+1 if r['provisional_y'] is None else 0;longest=max(longest,run)
        a=np.load(OUT/'partition-trial'/f'{plan["plan"]}-f{r["frame"]}.npz',allow_pickle=False)
        original=np.load(ROOT/'sample/output/s11-reference-current-perimeters-20261009-001'/f'f{r["frame"]}-support.npz',allow_pickle=False)
        l=a['labels'];actual=[]
        for i,(xy,n,status) in enumerate(zip(original['owner_pixel_xy'],original['outward_normal_xy'],original['status'],strict=True)):
            if xy[0]!=595 or n[0]!=0 or status>1:continue
            y=float(xy[1]+n[1]/2);u=int(np.floor(y))-798
            pair=(int(l[u,52]),int(l[u+1,52]))
            center_causes[str(pair)]+=1
            if pair==(1,2):actual.append({'face_id':i,'source_y':y})
        actual.sort(key=lambda z:(z['source_y'],z['face_id']));assert actual==r['center_candidates'];face_checks+=1
        assert r['physical_decision']=='NOT_EVALUATED'
    stats.append({'plan':plan['plan'],'total_frames':len(rows),'continuation_frames':len(rows)-1,'provisional_unique':states['PROVISIONAL_APPEARANCE_ONLY'],'ambiguous':states['AMBIGUOUS_CENTER'],'no_supported_center':states['NO_SUPPORTED_CENTER'],'longest_no_center_native_frames_including_initial':longest,'paired_seed_absent_frames':sum(not r['seed_a'] or not r['seed_b'] for r in rows),'center_face_label_pairs':dict(center_causes),'timing_s_total':sum(r['elapsed_s'] for r in rows),'outputs':[(r['frame'],r['provisional_y']) for r in rows if r['provisional_y'] is not None]})
checks.append({'name':'all 198 saved center decisions independently reconstructed','result':'PASS','rows':face_checks})
record=json.loads((ROOT/'docs/50-diagnostics/s11/2026-10-09-fixed-center-readout.json').read_text());pins={**record['preflight']['inputs'],**record['preflight']['source_pins'],**record['local_artifacts'],**{str(Path('docs/50-diagnostics/s11')/k):v['sha256'] for k,v in record['portable_figures'].items()}};mismatches=[]
for rel,h in pins.items():
    if hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()!=h:mismatches.append(rel)
assert not mismatches
result={'base_head':'cc179244c89ea59bd097fa165ea493942629e23e','algorithm_version':p.VERSION,'constructed_check_count':9,'checks':checks,'real_saved_decisions_checked':face_checks,'probe_results':stats,'prior_checkpoint_hashes_checked':len(pins),'prior_checkpoint_hash_mismatches':mismatches,'production_source_pins_checked':len(record['preflight']['source_pins']),'physical_efficacy':'NOT_EVALUATED','classifier_promotion':False,'verification_scope':'arithmetic, saved proposal projection and immutability; not physical accuracy or successful abstention'}
(OUT/'verification.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
print(json.dumps(result,indent=2))
