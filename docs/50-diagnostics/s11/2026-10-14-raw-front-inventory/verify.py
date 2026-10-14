"""Independent integer plateau/graph audit; no call to the inventory or peak owner."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT), str(ROOT/"src")]
import cv2
import numpy as np
from tests.diagnostics import s11_overlay_mask_comparison as comparison

o2, g0 = comparison.reuse.o2, comparison.reuse.g0


def digest(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def verify(readout):
    saved = o2.read_json(readout)
    prep = o2.read_json(ROOT/"docs/50-diagnostics/s11/2026-10-14-native-contact-trial/sample3-contact-plan.json")
    inputs = {k:o2.read_json(g0.pinned_path(ROOT,v)) for k,v in prep["inputs"].items()}
    recipe = comparison.InspectionRecipe.from_dict(o2.read_json(g0.pinned_path(ROOT,
        inputs["qualification_plan"]["inputs"]["recipe"])))
    frame = cv2.imread(str(g0.pinned_path(ROOT,saved["source_image"])))
    glass = recipe.glasses[0]
    bundle = comparison.build_mask_bundle(frame,glass)
    pre = comparison.baseline(inputs["comparison_plan"]).preprocess(bundle.crop,
        bundle.effective_mask,glass.detector_settings)
    ox,oy = bundle.crop_origin
    h,w = pre.gray.shape
    assert saved["origin"] == [ox,oy] and saved["shape"] == [h,w]
    gray = cv2.cvtColor(frame[oy:oy+h,ox:ox+w],cv2.COLOR_BGR2GRAY)
    assert np.array_equal(gray,pre.gray) and digest(gray) == saved["gray_sha256"]
    visible = (bundle.effective_mask>0)&(pre.glare_mask==0)
    assert digest(visible) == saved["visible_sha256"]
    valid = np.zeros((h,w),bool)
    valid[1:-1,1:-1] = (visible[1:-1,1:-1]&visible[:-2,1:-1]&visible[2:,1:-1]
                       &visible[1:-1,:-2]&visible[1:-1,2:])
    assert digest(valid) == saved["valid_stencil_sha256"] and valid.sum() == saved["valid_stencils"]
    derivative = np.zeros((h,w),np.int16)
    derivative[1:-1] = gray[2:].astype(np.int16)-gray[:-2].astype(np.int16)
    checks = {}
    for name,sign in (("falling",-1),("rising",1)):
        original = saved["signs"][name]
        values = np.maximum(sign*derivative,0)
        expected = []
        raster = np.zeros((h,w),bool)
        for x in range(w):
            # Segment all equal-value runs independently using vectorized breakpoints.
            starts = np.r_[0,np.flatnonzero(values[1:,x]!=values[:-1,x])+1]
            stops = np.r_[starts[1:],h]
            for a,b in zip(starts,stops,strict=True):
                if (a>0 and b<h and values[a,x]>0 and valid[a-1:b+1,x].all()
                        and values[a-1,x]<values[a,x] and values[b,x]<values[a,x]):
                    expected.append([x+ox,int(a)+oy,int(b)+oy,int(values[a,x])])
                    raster[a:b,x] = True
        assert expected == original["plateaus"] and digest(raster) == original["raster_sha256"]
        yx = np.argwhere(raster)
        xy = yx[:,::-1]+[ox,oy]
        lookup = {tuple(p):i for i,p in enumerate(xy.tolist())}
        links = []
        neighbours = [[] for _ in lookup]
        for (x,y),i in lookup.items():
            for dx,dy in ((1,0),(-1,1),(0,1),(1,1)):
                if (x+dx,y+dy) in lookup:
                    j=lookup[x+dx,y+dy]
                    links.append((i,j)); neighbours[i].append(j); neighbours[j].append(i)
        links.sort()
        graph = original["graph"]
        assert len(xy) == graph["vertices"] and len(links) == graph["links"]
        assert digest(np.array(xy,dtype=np.int64).reshape(-1,2)) == graph["vertices_sha256"]
        assert digest(np.array(links,dtype=np.int32).reshape(-1,2)) == graph["links_sha256"]
        # Enumerate whole graph via unordered link walks, independently of fragment IDs/order.
        remaining = {tuple(sorted(link)) for link in links}
        paths = []
        for i,peers in enumerate(neighbours):
            if not peers: paths.append([i])
            if len(peers)==2: continue
            for j in peers:
                edge=tuple(sorted((i,j)))
                if edge not in remaining: continue
                chain=[i,j]; remaining.remove(edge)
                while len(neighbours[chain[-1]])==2:
                    previous,current=chain[-2:]
                    nxt=next(k for k in neighbours[current] if k!=previous)
                    edge=tuple(sorted((current,nxt)))
                    if edge not in remaining: break
                    remaining.remove(edge); chain.append(nxt)
                paths.append(chain)
        while remaining:
            i,j=min(remaining); remaining.remove((i,j)); chain=[i,j]
            while chain[-1]!=i:
                previous,current=chain[-2:]
                nxt=next(k for k in neighbours[current] if k!=previous)
                remaining.remove(tuple(sorted((current,nxt)))); chain.append(nxt)
            paths.append(chain)
        assert len(paths)==graph["fragments"]
        def canonical(points):
            p=tuple(tuple(x) for x in points)
            if len(p)>1 and p[0]==p[-1]:
                ring=p[:-1]
                return min(q[k:]+q[:k] for q in (ring,ring[::-1]) for k in range(len(q)))
            return min(p,p[::-1])
        centered = [xy[p].tolist() for p in paths if (xy[p,0]==saved["fixed_source_x"]).any()]
        reported=original["fixed_column_fragments"]
        assert sorted(map(canonical,centered)) == sorted(canonical(p["source_path_xy"]) for p in reported)
        for p in reported:
            assert p["path_sha256"]==o2.fingerprint_json(p["source_path_xy"])
            assert p["fixed_column_rows"]==sorted(set(y for x,y in p["source_path_xy"] if x==saved["fixed_source_x"]))
            assert p["physical_role"]=="UNREVIEWED" and not p["native_canny_label"]
        checks[name]=dict(plateaus=len(expected),vertices=len(xy),links=len(links),
                          fragments=len(paths),center_fragments=len(centered))
    before=cv2.Canny(pre.blurred,glass.detector_settings.canny_low,glass.detector_settings.canny_high)
    assert digest(before)==saved["baseline"]["before_mask_sha256"]
    assert saved["baseline"]["canny_before_effective_mask"]==np.count_nonzero(before)
    assert saved["baseline"]["canny_after_effective_mask"]==np.count_nonzero(pre.canny)
    assert saved["baseline"]["canny_after_glare"]==np.count_nonzero((pre.canny>0)&visible)
    assert saved["contact"]["native_labels_created"]==saved["qualified_paths"]==0
    assert saved["selected_front"] is None and not saved["candidate_y_used_for_geometry"]
    return dict(schema="s11-raw-front-independent-verification-v1",readout_sha256=o2.sha256_file(readout),
                status="PASS",checks=checks,complete_original_gray_equal=True,
                complete_stencil_equal=True,complete_plateaus_equal=True,complete_graph_counts_equal=True,
                complete_fixed_column_paths_equal=True,baseline_stages_equal=True,native_labels_created=0)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--readout",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    o2.require(not args.output.exists(),"refuse overwrite")
    result=verify(args.readout)
    o2.write_new(args.output,result)
    print(json.dumps(result))
