"""Frozen, offline P1 comparison. No video decode or production selection."""
from __future__ import annotations
import argparse, ast, dataclasses, gzip, hashlib, importlib.util, json, platform, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
from tests.diagnostics.s11_corpus_access import require_corpus_access
import cv2
import numpy as np
from oil_tracker.adapters.vision import oil_material_path as owner
from oil_tracker.adapters.vision.preprocessing import preprocess
from oil_tracker.adapters.vision.foam_front_detector import detect_bottom_connected_foam
from oil_tracker.domain.recipe import DetectorSettings

BASE = "8fea93f2cfa27c455114d0921bbeacb9f697ad13"
SOURCE = "src/oil_tracker/adapters/vision/oil_material_path.py"
PUBLIC = "docs/50-diagnostics/s11/2026-10-09-public-path-representation.json"
B_RECORD = "docs/50-diagnostics/s11/2026-10-10-b-material-path-interval.json"
ABC = "docs/50-diagnostics/s11/2026-10-10-abc-source-interval-comparison.json"
S4 = "docs/50-diagnostics/s11/2026-10-10-sample4-center-interval-comparison.json"
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path): return json.loads(path.read_text())
def save(path, data): path.write_text(json.dumps(data, indent=2, allow_nan=False)+"\n")


def prepare(evidence, out):
    public, b, abc, s4 = [load(evidence/p) for p in (PUBLIC,B_RECORD,ABC,S4)]
    samples=tuple(sorted({Path(c["video"]).stem for c in public["preflight"]["cases"]} | {"sample4","sample5"}))
    admission=require_corpus_access(samples)
    if samples != ("sample4","sample5","sample6","sample7"):
        raise ValueError("The frozen P1 matrix must not be expanded or repurposed.")
    pins = {p:sha(evidence/p) for p in (PUBLIC,B_RECORD,ABC,S4,SOURCE)}
    cases = []
    for r in public["readout"]["results"]:
        cases.append({"id":r["case_id"], "scale":r["scale"], "arrays":r["arrays_path"],
                      "origin":r["crop_xyxy"][:2], "scale_xy":r["source_per_working_pixel_xy"]})
        pins[r["arrays_path"]] = r["arrays_sha256"]
    for r in b["readout"]["results"]:
        cases.append({"id":"water-B", "scale":r["scale"], "arrays":r["arrays_path"],
                      "origin":[740,250], "scale_xy":r["source_per_working_pixel_xy"]})
        pins[r["arrays_path"]] = r["arrays_sha256"]
    a = abc["preflight"]["references"][0]["source_raster"]
    pins[a["path"]] = a["sha256"]
    for scale in ("native", "height_200"):
        cases.append({"id":"water-A", "scale":scale, "image":a["path"],
                      "crop":[740,250,1160,1080], "origin":[740,250]})
    s = s4["readout"]["reference"]["source_raster"]
    mask = "sample/output/s11-a1-lineage-20261007-001/frames-final/f1275-effective_mask.png"
    recipe = "sample/sample4.oilrecipe"
    for p in (s["path"],mask,recipe): pins[p] = s4["preflight"]["inputs"][p]
    cases.append({"id":"sample4-f1275","scale":"native","image":s["path"],
                  "mask":mask,"recipe":recipe,"origin":[543,798]})
    for p, digest in pins.items():
        assert sha(evidence/p) == digest, p
    out.mkdir(parents=True,exist_ok=False)
    preflight = {"schema":"s11-center-path-preflight-v1", "base_head":BASE,
                 "cases":cases,"samples":samples,"corpus_access":admission,
                 "inputs":pins,"candidate_source_sha256":sha(ROOT/SOURCE),
                 "runner_sha256":sha(Path(__file__)),"max_records":16384,"max_transitions":50_000_000,
                 "rule":"Original seed graph; best sector-count then sum per central row and polarity. Median checks separately. No physical selector.",
                 "stop":"No after-result thresholds, crop, scale, seed or budget changes. No production promotion.",
                 "partition":"exposed development; sample3 not executed; Windows not executed"}
    save(out/"preflight.json",preflight)
    print("FROZEN",len(cases),"cases",len(pins),"input pins",sha(out/"preflight.json"))


def read_case(evidence, case, settings):
    if "arrays" in case:
        with np.load(evidence/case["arrays"],allow_pickle=False) as z:
            arrays = {k:z[k].copy() for k in z.files}
        crop = arrays["crop"]
        mask = np.full(crop.shape[:2],255,np.uint8)
    else:
        crop = cv2.imread(str(evidence/case["image"]))
        if crop is None: raise ValueError("Missing source raster")
        if "crop" in case:
            x0,y0,x1,y1=case["crop"]; crop=crop[y0:y1,x0:x1].copy()
        native_h,native_w=crop.shape[:2]
        if case["scale"] == "height_200":
            crop=cv2.resize(crop,(round(native_w*200/native_h),200),interpolation=cv2.INTER_AREA)
        mask=cv2.imread(str(evidence/case["mask"]),0) if "mask" in case else np.full(crop.shape[:2],255,np.uint8)
        if "recipe" in case:
            settings=DetectorSettings(**load(evidence/case["recipe"])["glasses"][0]["detector_settings"])
        arrays={}
        case = {**case,"scale_xy":[native_w/crop.shape[1],native_h/crop.shape[0]]}
    pre=preprocess(crop,mask,settings)
    material=arrays.get("material")
    if material is None:
        material=detect_bottom_connected_foam(crop,pre.gray,pre.canny,pre.glare_mask,mask,settings).combined_evidence_map
    visible=(mask>0)&~(pre.glare_mask>0)
    _,xx=np.where(mask>0); x0,x1=int(xx.min()),int(xx.max())+1
    ps=[]
    for i in range(5):
        start=x0+round((x1-x0)*i/5); stop=x0+round((x1-x0)*(i+1)/5)
        fresh=owner._sector_profile(pre.blurred,visible,start,stop,material_evidence_map=material,
                                   sector_index=i,capture_diagnostics=True)
        if f"s{i}_score" in arrays:
            p=owner._SectorProfile(start,stop,*(arrays[f"s{i}_{k}"] for k in
                 ("score","signed","support")),i,arrays[f"s{i}_contrast_channel"],arrays[f"s{i}_contrast_scale"])
            assert fresh is not None
            for k in ("score","signed","support","contrast_channel","contrast_scale"):
                assert np.array_equal(getattr(p,k),getattr(fresh,k)),(case["id"],case["scale"],i,k)
        else: p=fresh
        if p is not None: ps.append(p)
    return case,pre,mask,material,ps


def verify_paths(result, ps):
    checked=0
    for r in result.alternatives:
        if r.status != "PATH": continue
        score=0.
        assert len(r.rows)>=3 and r.rows[r.profile_indices.index(
            next(i for i,p in enumerate(ps) if p.sector_index==result.center_sector_index))]==r.center_row
        assert list(r.profile_indices)==list(range(r.profile_indices[0],r.profile_indices[-1]+1))
        for index,y,s in zip(r.profile_indices,r.rows,r.samples):
            p=ps[index]
            assert abs(y-r.seed)<=result.maximum_jump and float(p.score[y])>=.09
            assert p.support[y]>=.42 and r.polarity*float(p.signed[y])>=.025
            assert s.local_y==y and s.sector_index==p.sector_index
            assert (s.start_x,s.stop_x)==(p.start_x,p.stop_x)
            assert s.strength==float(p.score[y]) and s.signed_contrast==float(p.signed[y])
            score+=float(p.score[y])+.08*min(1.,abs(float(p.signed[y]))/.20)
        assert abs(score-r.objective_score)<1e-12
        assert all(abs(a-b)<=result.maximum_jump for a,b in zip(r.rows,r.rows[1:]))
        checked+=1
    return checked


def run(evidence,out):
    if (out/"readout.json").exists():
        raise FileExistsError("Use a new output directory; completed evidence is immutable.")
    frozen=load(out/"preflight.json")
    if tuple(frozen["samples"]) != ("sample4","sample5","sample6","sample7"):
        raise ValueError("Unexpected source set in frozen P1 matrix.")
    require_corpus_access(tuple(frozen["samples"]))
    assert sha(ROOT/SOURCE)==frozen["candidate_source_sha256"]
    assert sha(Path(__file__))==frozen["runner_sha256"]
    for p,digest in frozen["inputs"].items(): assert sha(evidence/p)==digest,p
    original=(evidence/SOURCE).read_bytes(); current=(ROOT/SOURCE).read_bytes()
    assert current.startswith(original), "Existing production source changed"
    prior=ast.parse(original).body; now=ast.parse(current).body
    assert [ast.dump(x) for x in prior]==[ast.dump(x) for x in now[:len(prior)]]
    refs={"water-A":(475.5,481.5),"water-B":(483.5,489.5),
          "s5-settled":(488.5,494.5),"sample4-f1275":(832.5,841.5)}
    summaries=[]
    for index, case in enumerate(frozen["cases"]):
        case,pre,mask,material,ps=read_case(evidence,case,DetectorSettings())
        base_paths={}
        before=[dataclasses.asdict(c) for c in owner.generate_material_path_candidates(
            pre,mask,None,crop_origin_y=0.,top_k=6,material_evidence_map=material,diagnostic_paths=base_paths)]
        retained_centers=[s.local_y for p in base_paths.values() for s in p.diagnostic_samples if s.sector_index==2]
        snapshots=[(p.score.tobytes(),p.signed.tobytes(),p.support.tobytes()) for p in ps]
        start=time.perf_counter()
        result=owner.diagnose_center_path_alternatives(ps,max_records=frozen["max_records"],
                                                      max_transitions=frozen["max_transitions"])
        seconds=time.perf_counter()-start
        checked=verify_paths(result,ps)
        after=[dataclasses.asdict(c) for c in owner.generate_material_path_candidates(
            pre,mask,None,crop_origin_y=0.,top_k=6,material_evidence_map=material)]
        assert before==after
        assert snapshots==[(p.score.tobytes(),p.signed.tobytes(),p.support.tobytes()) for p in ps]
        old_centers=[]
        for seed in result.seeds:
            path=owner._path_for_seed(seed,ps,(mask>0)&~(pre.glare_mask>0),pre.glare_mask,None,
                material_row_profile=owner._material_row_profile(material,(mask>0)&~(pre.glare_mask>0)),
                maximum_jump=result.maximum_jump,capture_diagnostics=True)
            if path is not None:
                old_centers.extend(s.local_y for s in path.diagnostic_samples if s.sector_index==2)
        paths=[r for r in result.alternatives if r.status=="PATH"]
        passed=[r for r in paths if r.passes_path_median_checks]
        ys=sorted({r.center_row for r in passed})
        origin_y=case["origin"][1]; sy=case["scale_xy"][1]
        source=lambda y: origin_y+(y+.5)*sy-.5
        ref=refs.get(case["id"])
        compatible=lambda values: sorted({source(y) for y in values if ref and ref[0]<=source(y)<=ref[1]})
        name=f'{index:02d}-{case["id"]}-{case["scale"]}'
        details=json.dumps(dataclasses.asdict(result),allow_nan=False,separators=(",",":")).encode()
        detail_path=out/f"{name}.json.gz"
        detail_path.write_bytes(gzip.compress(details,mtime=0))
        item={"id":case["id"],"scale":case["scale"],"status":result.status,"reason":result.reason,
              "shape":list(pre.gray.shape),"seeds":len(result.seeds),"records":len(result.alternatives),
              "paths_verified":checked,"median_pass_paths":len(passed),"unique_center_rows":len(ys),
              "original_all_seed_center_rows":sorted(set(old_centers)),
              "position_comparison_status":"QUALIFIED_INTERVAL_ONLY" if ref else "NOT_EVALUATED",
              "reviewed_interval":ref,"old_seed_compatible_source_rows":compatible(old_centers),
              "old_retained_compatible_source_rows":compatible(retained_centers),
              "new_compatible_source_rows":compatible(ys),"source_mapping":case,
              "seconds":seconds,"transition_bound":result.transition_bound,"peak_live_states":result.peak_live_states,
              "default_candidates_unchanged":True,"profile_arrays_unchanged":True,
              "detail_file":detail_path.name,"detail_sha256":sha(detail_path),
              "physical_identity":"NOT_EVALUATED","production_selection_changed":False}
        summaries.append(item)
        print(case["id"],case["scale"],result.status,checked,"paths",compatible(old_centers),"->",compatible(ys),
              round(seconds,3),"sec",flush=True)
    for p,digest in frozen["inputs"].items(): assert sha(evidence/p)==digest,p
    data={"schema":"s11-center-path-trial-v1","base_head":BASE,
          "preflight_sha256":sha(out/"preflight.json"),"candidate_source_sha256":sha(ROOT/SOURCE),
          "runtime":{"python":platform.python_version(),"numpy":np.__version__,"opencv":cv2.__version__},
          "original_source_prefix_and_AST_unchanged":True,"input_pins_preserved":len(frozen["inputs"]),
          "cases":summaries,"windows_execution":False,"video_decode":False,
          "report_efficacy":"NOT_TESTED","promotion":"NONE"}
    save(out/"readout.json",data)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action",choices=("prepare","run"))
    parser.add_argument("--evidence-root",required=True,type=Path)
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    (prepare if args.action=="prepare" else run)(args.evidence_root.resolve(),args.out.resolve())
