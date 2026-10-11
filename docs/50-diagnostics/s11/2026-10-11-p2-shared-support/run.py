"""Frozen, saved-raster P2 regional comparison; no detector/sequence execution.

prepare writes a manifest before outcomes. run checks every pinned byte and
creates a new output directory. Local native rasters must already exist.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT), str(ROOT/'src')]

import cv2
import numpy as np
from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.adapters.vision.preprocessing import preprocess
from tests.diagnostics.s11_boundary_temporal_probe import (
    SHARED_ROLE_SPEC, compare_shared_support_roles,
)

DOC = 'docs/50-diagnostics/s11/'
CAP = 'sample/output/s11-a1-lineage-20261007-001/frames-final/'
RECIPE = 'sample/sample4.oilrecipe'
ORIGIN = np.array([543,798])


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n',
                    encoding='utf-8')


def prepare(path):
    if path.exists():
        raise FileExistsError(path)
    inputs = {}

    def pin(rel, expected=None):
        actual = sha(ROOT/rel)
        if expected is not None and actual != expected:
            raise ValueError('historical pin changed: '+rel)
        inputs[rel] = actual
        return rel

    controls = read(ROOT/(DOC+'2026-10-07-sample4-a2-control-preflight.json'))
    capture = read(ROOT/(CAP+'capture-manifest.json'))
    pin(CAP+'capture-manifest.json')
    pin(DOC+'2026-10-07-sample4-a2-control-preflight.json')
    for name in ['2026-10-07-sample4-candidate-human-reply.json',
                 '2026-10-07-sample4-pink-human-reply.json',
                 '2026-10-09-foam-texture-reply.json',
                 '2026-10-09-foam-gap-upper-side-reply.json',
                 '2026-10-10-later-water-role-reply.json',
                 '2026-10-10-upper-projection-interval-reply.json',
                 '2026-10-10-upper-projection-ac-reply.json',
                 '2026-10-09-reference-correspondence.md',
                 '2026-10-09-public-water-surface-reply.json']:
        pin(DOC+name)
    images = {}
    for frame in sorted({r['frame'] for r in controls['rows']}):
        files = {}
        for key in ['original_roi','effective_mask','canny']:
            name = f'f{frame}-{key}.png'
            files[key] = pin(CAP+name,capture['files'][name])
        meta = f'f{frame}.json'
        files['capture'] = pin(CAP+meta,capture['files'][meta])
        images[str(frame)] = files
    old = read(ROOT/(DOC+'2026-10-09-observed-edge-fragments.json'))
    pin(DOC+'2026-10-09-observed-edge-fragments.json')
    rim = next(c for c in old['preflight']['cases'] if c['case_id']=='s4-f450')
    images['450'] = {k:pin(v,old['preflight']['inputs'].get(v))
                     for k,v in rim['images'].items()}
    texture = read(ROOT/(DOC+'2026-10-09-foam-texture-reply.json'))
    for row in texture['reviewed_guides']:
        f = row['frame_index']; original = pin(row['original_path'],row['original_sha256'])
        folder = (ROOT/original).parent
        files = {'original_roi':original}
        for key in ['effective_mask','canny','glare_mask']:
            matches = list(folder.glob(key+'_*.png'))
            if len(matches) != 1:
                raise ValueError('ambiguous saved image: '+key)
            files[key] = pin(str(matches[0].relative_to(ROOT)))
        images[str(f)] = files
    queries = []
    for row in controls['rows']:
        frame = row['frame']; index = row['candidate_input_index']
        candidate = read(ROOT/images[str(frame)]['capture'])['current']['candidates'][index]
        if candidate['source'] != row['source'] or candidate['y'] != row['source_y']:
            raise ValueError('candidate binding differs from review')
        queries.append(dict(id=f's4-f{frame}-idx{index}',frame=frame,
                            source_xy=[595,row['source_y']],candidate_index=index,
                            source=row['source'],label=row['target_role'],
                            subtype_status=row['physical_subtype_status'],
                            initial_reference=frame==1275))
    for row in texture['reviewed_guides']:
        f = row['frame_index']
        queries.append(dict(id=f's4-texture-f{f}',frame=f,
                            source_xy=[595,row['source_front_y']],
                            label='internal_foam_texture',initial_reference=f==1620))
    queries.append(dict(id='s4-cbr-rim-f450',frame=450,source_xy=[595,880],
                        label='agent_observed_cbr_wrong_region',initial_reference=False))
    refs = {
        'interface':dict(frame=1275,source_xy=[595,835],
                         authority='existing approximate Oil vicinity, not a pure material mask'),
        'structure':dict(frame=450,source_xy=[561,861],
                         authority='existing reviewed rim-seed context, not a dense contour'),
        'texture':dict(frame=1620,source_xy=[595,833],
                       authority='existing user-reviewed internal texture guide, not a whole component label'),
    }
    deferred = [
        dict(id='water-B-f1438',role='water upper surface; no Foam layer',
             reason='no qualified same-scene internal-texture exemplar in this frozen set'),
        dict(id='water-C-f1643',role='water upper surface; no Foam layer',
             reason='no qualified same-scene internal-texture exemplar in this frozen set'),
        dict(id='water-A-f1232',role='Foam upper positive; lower interface unclear',
             reason='Oil-specific sample4 exemplars do not qualify a water Foam classifier'),
        dict(id='water-f822',role='inclined liquid surface, qualitative',
             reason='no qualified same-scene three-role exemplar set; no scalar bound'),
        dict(id='beer',role='one thin layer front/back; cropped upper retained',
             reason='no qualified same-scene three-role exemplar set'),
        dict(id='milk',role='Foam context with independent lower-interface unavailability',
             reason='no qualified same-scene three-role exemplar set'),
    ]
    pin(RECIPE)
    pin(str(Path(__file__).resolve().relative_to(ROOT)))
    pin('tests/diagnostics/s11_boundary_temporal_probe.py')
    pin('tests/unit/test_s11_shared_support_roles.py')
    sources = {str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'src').rglob('*.py'))}
    value = dict(schema='s11-p2-shared-support-preflight-v1',
                 starting_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                 operation=SHARED_ROLE_SPEC,inputs=inputs,production_sources=sources,
                 images=images,queries=queries,references=refs,retained_unavailable=deferred,
                 raster_shape=[104,104],origin=ORIGIN.tolist(),crop_radius=12,
                 query_core_xyxy=[5,10,20,15],parts_x=[[5,10],[10,15],[15,20]],
                 ablation='center part only, with the same translations, role set and cost rule',
                 fractional_y='retain both floor and ceil neighborhoods; require agreeing preferences',
                 support='all existing Canny pixels in core; all three X parts must be nonempty; no snapping or generated contour',
                 normalization='same unique current vertical stencil pixels and same complete translation intersection for every role',
                 geometry='fraction of current edge points missing a reference Canny edge under that same translation',
                 context_limit='Candidate-bound regional neighborhoods, not candidate-owned dense paths, calibrated scalar truth or full-candidate identity.',
                 progression='All six non-initial confirmed Oil contexts must retain interface preference, all three rejected targets must have measured structure/texture preference, and the joint mode must improve a rejected-target decision over center-only without losing any positive. Unresolved/unavailable is not rejection. Public controls remain required even if this pilot passes.',
                 stop='One fixed operation and one ablation. Failure or mostly incomparable closes this variant without retuning. No runtime consumer, sequence/report replay, Windows claim, new labels or repeated closed questions.',
                 partition='previously_exposed_development',video_decode=False,physical_decision='NOT_EVALUATED')
    write(path,value)


def load_images(pre):
    settings = JsonRecipeRepository().load(ROOT/RECIPE).glasses[0].detector_settings
    images = {}
    for key,files in pre['images'].items():
        bgr = cv2.imread(str(ROOT/files['original_roi']))
        mask = cv2.imread(str(ROOT/files['effective_mask']),0)
        edges = cv2.imread(str(ROOT/files['canny']),0)
        if bgr is None or bgr.shape != (104,104,3) or mask is None or edges is None:
            raise ValueError('saved raster shape/read failure')
        pp = preprocess(bgr,mask,settings)
        if not np.array_equal(pp.canny,edges):
            raise ValueError('saved Canny differs from unchanged preprocessing: '+key)
        if 'glare_mask' in files:
            glare = cv2.imread(str(ROOT/files['glare_mask']),0)
            if not np.array_equal(pp.glare_mask,glare):
                raise ValueError('saved glare differs: '+key)
        images[int(key)] = (bgr,(mask>0)&(pp.glare_mask==0),edges>0)
    return images


def region(image, source_xy):
    x,y = (np.asarray(source_xy)-ORIGIN).tolist()
    if type(x) is not int or type(y) is not int or x-12<0 or y-12<0 or x+12>=104 or y+12>=104:
        return None
    return tuple(a[y-12:y+13,x-12:x+13].copy() for a in image)


def run(manifest,out):
    pre = read(manifest)
    for rel,digest in {**pre['inputs'],**pre['production_sources']}.items():
        if sha(ROOT/rel) != digest:
            raise ValueError('frozen input changed: '+rel)
    if pre['operation'] != SHARED_ROLE_SPEC:
        raise ValueError('frozen operation differs')
    if out.exists():
        raise FileExistsError(out)
    images = load_images(pre)
    refs = {role:region(images[r['frame']],r['source_xy']) for role,r in pre['references'].items()}
    results = []
    for query in pre['queries']:
        variants = []
        for y in sorted({math.floor(query['source_xy'][1]),math.ceil(query['source_xy'][1])}):
            patch = region(images[query['frame']],[int(query['source_xy'][0]),int(y)])
            modes = {}
            if patch is None:
                modes = {mode:dict(status='UNAVAILABLE',reason='query_crop_outside',appearance_preference=None)
                         for mode in ['joint','center_only']}
            else:
                bgr,visible,edges = patch
                yy,xx = np.nonzero(edges[10:15,5:20]); points=np.column_stack([xx+5,yy+10])
                complete_parts = all(np.any((points[:,0]>=lo)&(points[:,0]<hi)) for lo,hi in pre['parts_x'])
                for mode in ['joint','center_only']:
                    p = points if mode=='joint' else points[(points[:,0]>=10)&(points[:,0]<15)]
                    if mode=='joint' and not complete_parts:
                        result=dict(status='UNAVAILABLE',reason='missing_current_part',appearance_preference=None)
                    else:
                        result=compare_shared_support_roles(bgr,visible,edges,p,refs)
                    modes[mode]=result
            variants.append(dict(source_center_xy=[query['source_xy'][0],y],modes=modes))
        summary={}
        for mode in ['joint','center_only']:
            values=[v['modes'][mode] for v in variants]
            preferences={v['appearance_preference'] for v in values}
            summary[mode]=dict(measured=all(v['status']=='MEASURED' for v in values),
                               preference=next(iter(preferences)) if len(preferences)==1 else None,
                               fractional_agreement=len(preferences)==1)
        results.append(dict(query=query,variants=variants,summary=summary))
    noninitial=[r for r in results if not r['query']['initial_reference']]
    counts={}
    for mode in ['joint','center_only']:
        pos=[r for r in noninitial if r['query']['label']=='confirmed_target']
        neg=[r for r in noninitial if r['query']['label']=='rejected_target']
        counts[mode]=dict(positive_total=len(pos),
                         positive_interface=sum(r['summary'][mode]['preference']=='interface' for r in pos),
                         rejected_total=len(neg),
                         rejected_interface=sum(r['summary'][mode]['preference']=='interface' for r in neg),
                         rejected_opposition_preference=sum(r['summary'][mode]['measured'] and r['summary'][mode]['preference'] in {'structure','texture'} for r in neg),
                         measured_queries=sum(r['summary'][mode]['measured'] for r in results),
                         total_queries=len(results))
    a,b=counts['joint'],counts['center_only']
    progressed=(a['positive_interface']==a['positive_total'] and a['rejected_opposition_preference']==a['rejected_total']
                and a['rejected_interface']<b['rejected_interface'] and a['positive_interface']>=b['positive_interface'])
    value=dict(schema='s11-p2-shared-support-readout-v1',preflight_sha256=sha(manifest),
               execution_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
               runtime=dict(python=platform.python_version(),numpy=np.__version__,opencv=cv2.__version__),
               results=results,counts=counts,retained_unavailable=pre['retained_unavailable'],
               progression_passed=progressed,physical_decision='NOT_EVALUATED',
               disposition='BOUNDED_PILOT_ONLY' if progressed else 'CLOSED_WITHOUT_PROMOTION',
               source_and_inputs_preserved=True)
    for rel,digest in {**pre['inputs'],**pre['production_sources']}.items():
        if sha(ROOT/rel) != digest:
            raise ValueError('input changed during run: '+rel)
    out.mkdir(parents=True,exist_ok=False)
    write(out/'readout.json',value)
    print(json.dumps(counts,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['prepare','run'])
    parser.add_argument('--manifest',type=Path,required=True)
    parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    if args.command=='prepare':
        prepare(args.manifest)
    elif args.out is None:
        parser.error('run requires --out')
    else:
        run(args.manifest,args.out)
