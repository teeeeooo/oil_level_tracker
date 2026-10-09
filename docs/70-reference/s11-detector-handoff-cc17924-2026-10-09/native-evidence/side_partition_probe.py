"""Frozen offline proposal test. No production, truth, Recipe, or report writes.
Reference roles are disclosed boundary-vicinity inputs, not dense material truth.
Native seed transport is reused; this script does not run or retune tracking.
"""
from __future__ import annotations
import argparse, hashlib, heapq, json, math, time
from pathlib import Path
import numpy as np

VERSION = 'reference-paired-minimax-partition-v1'
OFFSET = 2  # Reuse the previous reference stencil; not fitted to returned outcomes.
MAX_PIXELS = 65536

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def minimax(image: np.ndarray, visible: np.ndarray, seeds: list[tuple[int,int]]) -> np.ndarray:
    h,w = visible.shape
    if image.shape != (h,w,3) or image.dtype != np.uint8 or h*w > MAX_PIXELS:
        raise ValueError('invalid or oversized raster')
    dist = np.full((h,w), 256, np.uint16)
    heap: list[tuple[int,int,int]] = []
    for y,x in sorted(set(seeds)):
        if 0 <= y < h and 0 <= x < w and visible[y,x]:
            dist[y,x] = 0
            heapq.heappush(heap,(0,y,x))
    pix = image.astype(np.int16)
    horizontal = np.abs(pix[:,1:]-pix[:,:-1]).max(2)
    vertical = np.abs(pix[1:]-pix[:-1]).max(2)
    while heap:
        d,y,x = heapq.heappop(heap)
        if d != dist[y,x]:
            continue
        for yy,xx,cost in ((y,x-1,int(horizontal[y,x-1]) if x>0 else 0),
                           (y,x+1,int(horizontal[y,x]) if x+1<w else 0),
                           (y-1,x,int(vertical[y-1,x]) if y>0 else 0),
                           (y+1,x,int(vertical[y,x]) if y+1<h else 0)):
            if not (0<=yy<h and 0<=xx<w and visible[yy,xx]):
                continue
            nd = max(d,cost)
            if nd < dist[yy,xx]:
                dist[yy,xx] = nd
                heapq.heappush(heap,(nd,yy,xx))
    return dist

def pair_pixels(image: np.ndarray, visible: np.ndarray, points: np.ndarray):
    h,w = visible.shape
    pairs=[]
    for p in points:
        if not np.isfinite(p).all():
            pairs.append(None); continue
        x,y = np.floor(p+.5).astype(int)
        a,b = (int(y-OFFSET),int(x)),(int(y+OFFSET),int(x))
        if all(0<=yy<h and 0<=xx<w and visible[yy,xx] for yy,xx in [a,b]):
            pairs.append((a,b,image[a].astype(np.int32),image[b].astype(np.int32)))
        else:
            pairs.append(None)
    return pairs

def choose_seeds(current, reference):
    aa=[];bb=[];reasons={'missing_pair':0,'not_ordered_closer':0,'accepted_pairs':0}
    for now,ref in zip(current,reference,strict=True):
        if now is None or ref is None:
            reasons['missing_pair']+=1; continue
        a,b,ca,cb=now;_,_,ra,rb=ref
        # BOTH sides must favor their own frozen reference over the other side.
        own_a=int(np.abs(ca-ra).sum());opp_a=int(np.abs(ca-rb).sum())
        own_b=int(np.abs(cb-rb).sum());opp_b=int(np.abs(cb-ra).sum())
        if own_a<opp_a and own_b<opp_b:
            aa.append(a);bb.append(b);reasons['accepted_pairs']+=1
        else:
            reasons['not_ordered_closer']+=1
    conflicts=set(aa)&set(bb)
    aa=sorted(set(aa)-conflicts);bb=sorted(set(bb)-conflicts)
    reasons['conflicting_seed_pixels']=len(conflicts)
    return aa,bb,reasons

def partition(image,visible,aa,bb):
    da=minimax(image,visible,aa);db=minimax(image,visible,bb)
    labels=np.zeros(visible.shape,np.uint8)
    if aa and bb:
        labels[visible&(da<db)]=1
        labels[visible&(db<da)]=2
    return labels,da,db

def run(root: Path,out: Path):
    out.mkdir(exist_ok=False)
    src=root/'sample/output/s11-reference-current-perimeters-20261009-001'
    prior=json.loads((src/'readout.json').read_text())
    pins={str(p.relative_to(root)):sha(p) for p in (src/'readout.json',src/'preflight.json')}
    cases=[]
    for plan in prior['results']:
        if plan['plan_id'] not in ('oil-positive','foam-positive','rim-opposition'):
            continue
        cases.append(plan)
        for r in plan['rows']:
            for key in ('support','query'):
                pins[r[key+'_path']]=r[key+'_sha256']
    pre={'schema':VERSION,'base_head':'cc179244c89ea59bd097fa165ea493942629e23e',
         'hypothesis':'Explicit ordered side examples plus current-frame seeded region competition may reobserve boundary geometry better than transported points alone. This is conditional appearance evidence, not a physical identity theorem.',
         'difference':'No rigid pattern translation, raw-edge-closure test or brightness-component selection. Minimax paths on the visible current RGB graph retain wider spatial arrangement and two declared side references.',
         'inputs':'Reuse all original paired side stencils at +/-2 rows and all live LK positions. Reference pairs are hypotheses derived from approximate boundary vicinity, NOT certified material pixels. Initial frames excluded from continuation counts.',
         'seed_rule':'Both current side pixels must be strictly closer in BGR L1 to their own initial pair pixel than the opposite initial pixel. Missing or conflicting seeds removed. No after-result subset selection, gains, adaptive reference, thresholds, mask expansion or snapping.',
         'region_rule':'4-connected visible graph, edge cost max(abs(BGR neighbour difference)); minimum bottleneck path cost per side. Equal costs, absent either seed class or unreachable support remains unknown. No distance/smoothness secondary tie break.',
         'center_rule':'Reuse ALL saved visible support faces at native Recipe X595. Candidate face qualifies only when its immediately upper pixel is label 1 and lower pixel label 2. Exact half-pixel Y retained. More than one=>AMBIGUOUS; none=>NO_SUPPORTED_CENTER. A unique face is PROVISIONAL_APPEARANCE_ONLY, never physical/published truth.',
         'controls':['integer minimax oracle on small graphs','mask barriers do not leak','no seed class cannot imply material absence','constant same-observable image is unresolved','role swap symmetry','determinism'],
         'falsification':'Reject as a physical selector if it produces wrong-region continuation, cannot retain useful non-initial boundary contexts, or requires manually corrected side seeds. Do not retune this variant. Identical-appearance replacement remains an explicit unresolved physical alternative.',
         'scope':'offline 198 plan/frame queries; no video decode or detector/resolver execution; no UI/schema or production changes; no ML, new dependencies or Windows work',
         'all_seed_pairs':True,'offset':OFFSET,'max_pixels':MAX_PIXELS,'inputs':pins,'script_sha256':sha(Path(__file__))}
    for p,h in pins.items():
        if sha(root/p)!=h: raise ValueError('input changed: '+p)
    (out/'preflight.json').write_text(json.dumps(pre,indent=2)+'\n')
    results=[]
    for plan in cases:
        first=plan['rows'][0]
        init=np.load(root/first['support_path'],allow_pickle=False)
        iq=np.load(root/first['query_path'],allow_pickle=False)
        refs=pair_pixels(init['crop'],init['visible'],iq['pos'])
        rows=[]
        for nr,r in enumerate(plan['rows']):
            a=np.load(root/r['support_path'],allow_pickle=False)
            q=np.load(root/r['query_path'],allow_pickle=False)
            crop,vis=a['crop'],a['visible']
            aa,bb,counts=choose_seeds(pair_pixels(crop,vis,q['pos']),refs)
            start=time.perf_counter();labels,da,db=partition(crop,vis,aa,bb)
            elapsed=time.perf_counter()-start
            crossings=[]
            for i,(xy,normal,status) in enumerate(zip(a['owner_pixel_xy'],a['outward_normal_xy'],a['status'],strict=True)):
                if xy[0]!=595 or normal[0]!=0 or status>1: continue
                ys=float(xy[1]+normal[1]/2);upper=math.floor(ys)-798;lower=upper+1
                if 0<=upper<104 and 0<=lower<104 and labels[upper,52]==1 and labels[lower,52]==2:
                    crossings.append({'face_id':i,'source_y':ys})
            crossings=sorted(crossings,key=lambda v:(v['source_y'],v['face_id']))
            state='PROVISIONAL_APPEARANCE_ONLY' if len(crossings)==1 else ('AMBIGUOUS_CENTER' if crossings else 'NO_SUPPORTED_CENTER')
            row={'frame':r['frame'],'initialized':nr==0,'seed_a':len(aa),'seed_b':len(bb),'seed_filter':counts,'center_candidates':crossings,'state':state,'provisional_y':crossings[0]['source_y'] if len(crossings)==1 else None,'visible_pixels':int(vis.sum()),'classified_pixels':int(np.count_nonzero(labels)),'elapsed_s':elapsed,'physical_decision':'NOT_EVALUATED'}
            rows.append(row)
            np.savez_compressed(out/f'{plan["plan_id"]}-f{r["frame"]}.npz',labels=labels,crop=crop,visible=vis,seeds_a=np.asarray(aa,dtype=int).reshape(-1,2),seeds_b=np.asarray(bb,dtype=int).reshape(-1,2),distance_a=da,distance_b=db)
        results.append({'plan':plan['plan_id'],'rows':rows})
        print(plan['plan_id'],{k:sum(r['state']==k for r in rows[1:]) for k in ('PROVISIONAL_APPEARANCE_ONLY','AMBIGUOUS_CENTER','NO_SUPPORTED_CENTER')},flush=True)
    for p,h in pins.items():
        if sha(root/p)!=h: raise ValueError('input changed: '+p)
    report={'schema':VERSION,'results':results,'inputs_unchanged':True,'production_changed':False,'field_efficacy':'NOT_EVALUATED','script_sha256':sha(Path(__file__))}
    (out/'readout.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print('COMPLETE',str(out),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();run(args.root.resolve(),args.out.resolve())
