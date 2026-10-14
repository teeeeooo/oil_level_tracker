"""Independent integer accumulation and sampling for the frozen DTO-1 readout."""
import argparse
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT/"src")]
import numpy as np
from tests.diagnostics.s11_dense_temporal_role_run import load, decode_window, sha


def independent(grays):
    h, w = grays[0].shape
    counts = np.zeros((h-2, w-2), dtype=np.int32)
    for a, b in zip(grays[:-1], grays[1:]):
        ac, bc = a[1:-1, 1:-1], b[1:-1, 1:-1]
        for dy, dx in ((-1,-1),(-1,0),(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1)):
            an, bn = a[1+dy:h-1+dy, 1+dx:w-1+dx], b[1+dy:h-1+dy, 1+dx:w-1+dx]
            counts += ((an > ac) != (bn > bc)) | ((an < ac) != (bn < bc))
    field = np.full((h, w), np.nan)
    field[1:-1, 1:-1] = counts / (8*(len(grays)-1))
    return field


def side(field, centers):
    vals = []
    for x, y in centers:
        if x-3 < 0 or y-3 < 0 or x+3 >= field.shape[1] or y+3 >= field.shape[0]:
            return None
        patch = field[y-3:y+4, x-3:x+4]
        if not np.isfinite(patch).all():
            return None
        vals.append(float(patch.sum()/49))
    return sum(vals)/len(vals) if vals else None


def verify(path, output):
    data = json.loads(path.read_text()); rows, frames, pins = load(ROOT)
    assert data["corpus_pins"] == pins
    observed = {r["id"]: r for r in data["subjects"]}
    assert len(observed) == len(rows) == 137
    differences, checked, profiles = [], 0, 0
    for key, entry in frames.items():
        grays, hashes, times = decode_window(ROOT, entry)
        saved = next(f for f in data["frames"] if f["frame_key"] == key)
        assert hashes == saved["roi_hashes"] and times == saved["times"]
        field = independent(grays)
        ox, oy = entry["geometry"]["origin"]; ix, iy = entry["image_origin"]
        for row in rows:
            if row["frame_key"] != key:
                continue
            original = observed[row["id"]]
            assert original["allowed_roles"] == row["allowed_boundary_roles"]
            measured = original["measurements"]["turnover"]
            for name in ("upper", "lower"):
                centers = [[x+ix-ox, y+iy-oy] for x,y in
                           row["native_sides"].get(name, {}).get("centers_image_xy", [])]
                value = side(field, centers); reference = measured[name]["mean"]
                assert (value is None) == (reference is None)
                if value is not None:
                    differences.append(abs(value-reference))
            checked += 1
        col = entry["geometry"]["column"]
        for record in saved["center_profile"]:
            y = record["row"]; a = side(field, [[col,y-5]]); b = side(field, [[col,y+5]])
            value = None if a is None or b is None else b-a
            assert (value is None) == (record["score"] is None)
            if value is not None:
                differences.append(abs(value-record["score"]))
            profiles += 1
    assert max(differences, default=0) < 1e-14
    qualified = [r for r in data["subjects"] if r["allowed_roles"]]
    base = next(f for f in data["frames"] if f["source"]["path"] == "sample/base_sample_1.mp4")
    base_rows = [{"source_y":r["row"]+218, "score":r["score"]} for r in base["center_profile"]
                 if 365 <= r["row"]+218 < 381]
    receipt = {"status":"PASS", "readout_sha256":sha(path), "verifier_sha256":sha(Path(__file__)),
               "checked_subjects":checked, "checked_center_rows":profiles,
               "decoded_frames_for_independent_verification":104,
               "maximum_absolute_arithmetic_error":max(differences,default=0),
               "qualified": [{"id":r["id"], "roles":r["allowed_roles"],
                               "score":r["measurements"]["turnover"]["score"]} for r in qualified],
               "available_subjects":sum(r["measurements"]["turnover"]["score"] is not None for r in data["subjects"]),
               "passes":{k:sum(c["checks"][k]["passes"] is True for c in data["comparisons"])
                         for k in ("turnover", "static_complexity")},
               "comparisons":len(data["comparisons"]), "base_regional_availability":base_rows,
               "physical_acceptance":"NOT_EVALUATED", "production_changed":False}
    if output.exists():
        raise ValueError("refuse overwrite")
    output.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(receipt,ensure_ascii=False))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--readout", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    verify(a.readout, a.output)
