"""CRW-1: bounded current-raster peak/partition hypotheses, never authority."""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import gzip
from hashlib import sha256
import json
import math
from pathlib import Path
import time

import cv2
import numpy as np

from tests.diagnostics.s11_corroboration_geometry_screen import (
    PEERS, PREPARED, PUBLIC, bind_packet, native_sectors, require,
)

SCHEMA = "s11-current-raster-partition-screen-v1"


def paired_gradient(gray: np.ndarray, visible: np.ndarray, x0: int, x1: int,
                    y: int) -> dict:
    """Use identical columns on the two edge rows; never contrast disjoint masks."""
    if not 1 <= y < gray.shape[0]-1:
        return {"available": False, "value": None, "paired_columns": []}
    columns = np.flatnonzero(visible[y-1, x0:x1] & visible[y+1, x0:x1])+x0
    available = len(columns) >= 2 and len(columns)/(x1-x0) >= 0.5
    value = (float((gray[y+1, columns].astype(float)-gray[y-1, columns]).mean())
             / 510.0 if available else None)
    return {"available": available, "value": value, "paired_columns": columns.tolist()}


def paired_partition(gray: np.ndarray, visible: np.ndarray, x0: int, x1: int,
                     y: int, band: int) -> dict:
    """Four O1-sized bands, common (offset,column) support; no material label."""
    offsets = np.arange(band)
    rows = [y-2-offsets, y+2+offsets,
            y-2-2*band-offsets, y+2+2*band+offsets]
    windows = [r.tolist() for r in rows]
    if min(int(r.min()) for r in rows) < 0 or max(int(r.max()) for r in rows) >= gray.shape[0]:
        return {"status": "UNAVAILABLE_CROP", "rows": windows,
                "paired_pixel_count": 0, "margin": None}
    support = np.logical_and.reduce([visible[r, x0:x1] for r in rows])
    count = int(support.sum())
    result = {"status": "UNAVAILABLE_SUPPORT", "rows": windows,
              "paired_pixel_count": count, "paired_fraction": count/(band*(x1-x0)),
              "support_sha256": sha256(support.tobytes()).hexdigest(), "margin": None}
    if count < 8 or result["paired_fraction"] < 0.5:
        return result
    sums = [int(gray[r, x0:x1][support].sum()) for r in rows]
    a, b, fa, fb = sums
    near, far = b-a, fb-fa
    drift = max(abs(a-fa), abs(b-fb))
    compatible_sign = near*far > 0
    margin = (min(abs(near), abs(far)) if compatible_sign else
              -min(abs(near), abs(far))) - drift
    scale = 255.0*count
    result.update(status="MEASURED", means=[s/scale for s in sums],
                  near_contrast=near/scale, far_contrast=far/scale,
                  same_side_drift=drift/scale, integer_margin=margin,
                  compatible_sign=compatible_sign, margin=margin/scale)
    return result


def peak_groups(profile: list[dict]) -> list[dict]:
    """Keep every nonzero local maximum and every exact tied row; no peak hull."""
    groups = []
    i = 0
    while i < len(profile):
        row = profile[i]
        if not row["available"] or row["value"] == 0:
            i += 1
            continue
        strength = abs(row["value"])
        j = i+1
        while (j < len(profile) and profile[j]["available"]
               and abs(profile[j]["value"]) == strength):
            j += 1
        before = profile[i-1] if i else None
        after = profile[j] if j < len(profile) else None
        neighbors = [p for p in (before, after) if p is not None and p["available"]]
        if all(abs(p["value"]) < strength for p in neighbors):
            groups.append({"local_rows": [p["local_y"] for p in profile[i:j]],
                           "search_censored": len(neighbors) != 2})
        i = j
    return groups


def observe(gray: np.ndarray, visible: np.ndarray, origin: list[int], row: dict,
            band: int, *, frame_key: str) -> dict:
    require(bool(frame_key), "missing frame identity")
    require(gray.ndim == 2 and gray.dtype == np.uint8, "gray must be uint8 raster")
    require(visible.shape == gray.shape and visible.dtype == bool, "invalid visibility")
    require(type(band) is int and 1 <= band <= 64, "invalid band width")
    require([s["sector"] for s in row["sectors"]] == list(range(5)), "expected ordered five sectors")
    native = {s["sector"]: s for s in native_sectors(row)}
    sectors = []
    for s in row["sectors"]:
        sid = s["sector"]
        x0,x1 = [x-origin[0] for x in s["source_x_range"]]
        require(0 <= x0 < x1 <= gray.shape[1], "invalid sector bounds")
        seed = native[sid]["path_source_y"] if sid in native else row["canonical_y"]
        require(math.isfinite(seed), "nonfinite seed")
        seed_local = seed-origin[1]
        lo,hi = math.floor(seed_local)-band, math.ceil(seed_local)+band
        require(hi-lo <= 2*band+1, "unbounded search")
        profile = [{"local_y": y, **paired_gradient(gray,visible,x0,x1,y)}
                   for y in range(lo,hi+1)]
        groups = peak_groups(profile)
        for group in groups:
            group["source_rows"] = [y+origin[1] for y in group["local_rows"]]
            group["partitions"] = [paired_partition(gray,visible,x0,x1,y,band)
                                   for y in group["local_rows"]]
        supported = [y for g in groups if not g["search_censored"]
                     for y,p in zip(g["source_rows"],g["partitions"],strict=True)
                     if p["margin"] is not None and p["margin"] > 0]
        sectors.append({"sector": sid, "source_x_range": s["source_x_range"],
            "seed_kind": "NATIVE_GENERATOR_HINT" if sid in native else "SCALAR_CENTER_HINT",
            "seed_source_y": seed, "search_source_rows": [lo+origin[1],hi+origin[1]],
            "profile": profile, "peak_groups": groups,
            "partition_supported_source_rows": supported})
    return {"schema": SCHEMA,
        "raster_binding": {"frame_key": frame_key, "origin": origin,
            "shape": list(gray.shape), "gray_sha256": sha256(gray.tobytes()).hexdigest(),
            "visible_sha256": sha256(visible.tobytes()).hexdigest(), "band": band},
        "canonical_y_unchanged": row["canonical_y"],
        "input_candidate_index": row["candidate_input_index"], "input_source": row["source"],
        "derivation": "paired-current-gray-edge-and-four-band-v1",
        "sectors": sectors,
        "localized_sector_count": sum(any(not g["search_censored"] for g in s["peak_groups"])
                                      for s in sectors),
        "partition_sector_count": sum(bool(s["partition_supported_source_rows"]) for s in sectors),
        "physical_role": "NOT_EVALUATED", "native_path_created": False,
        "continuous_contour_qualified": False, "authority": "NONE"}


def shared_measurements(left: dict, right: dict) -> list[dict]:
    """Exact aliases of one extraction, NOT independent votes or complete geometry."""
    require(left["raster_binding"] == right["raster_binding"], "different raster identity")
    output = []
    for a,b in zip(left["sectors"],right["sectors"],strict=True):
        require((a["sector"],a["source_x_range"]) ==
                (b["sector"],b["source_x_range"]), "different sector grid")
        common = sorted(set(a["partition_supported_source_rows"])
                        & set(b["partition_supported_source_rows"]))
        if common:
            output.append({"sector": a["sector"],"source_rows":common,
                           "relationship":"SAME_MEASUREMENT_NOT_INDEPENDENT"})
    return output


def run(root: Path) -> dict:
    started = time.monotonic()
    pins = {}
    def pin(relative, expected=None):
        path = root/relative
        digest = sha256(path.read_bytes()).hexdigest()
        require(expected is None or digest == expected, f"hash mismatch: {relative}")
        pins[relative] = digest
        return path
    def load(relative, expected=None):
        p = pin(relative,expected)
        data = p.read_bytes()
        return json.loads(gzip.decompress(data) if p.suffix==".gz" else data)
    previous = load(PEERS)
    for p,h in previous["inputs"].items():
        pin(p,h)
    prepared = load(PREPARED,previous["inputs"][PREPARED])
    frames = {}
    for fid,spec in prepared["frames"].items():
        image = pin(spec["rgb"]["path"],spec["rgb"]["sha256"])
        mask = pin(spec["visibility"]["path"],spec["visibility"]["sha256"])
        if fid.startswith("sample4-f"):
            number = int(fid.split("-f")[1])
            p = f"sample/output/s11-a1-lineage-20261007-001/frames-final/f{number}.json"
            capture = load(p,previous["inputs"][p])
            raw,state = capture["current"],capture["state"]
            bgr = cv2.imread(str(image),cv2.IMREAD_COLOR)
            require(bgr is not None,"missing raster")
            gray = cv2.cvtColor(bgr,cv2.COLOR_BGR2GRAY)
            with np.load(mask,allow_pickle=False) as z:
                visible = z[spec["mask_key"]].copy()
        else:
            require(fid=="public-f1499","unexpected source")
            raw = load(PUBLIC+"native-none.json")
            state = load(PUBLIC+"native-diagnostics.json.gz")["state"]
            with np.load(image,allow_pickle=False) as z:
                gray = cv2.cvtColor(z["original_roi"],cv2.COLOR_BGR2GRAY)
                require(np.array_equal(gray,z["grayscale"]),"gray mismatch")
                visible = (z["effective_mask"]>0)&(z["glare_mask"]==0)
        packet = state["oil_interface_diagnostics"]
        require(packet["crop_origin"]==spec["origin"],"origin mismatch")
        require(list(gray.shape)==spec["shape"]==list(visible.shape),"shape mismatch")
        frames[fid] = (gray,visible,spec["origin"],packet,bind_packet(raw,packet))
    units = []
    for u in previous["units"]:
        out = deepcopy({k:v for k,v in u.items() if k!="measurement"})
        if "measurement" in u:
            gray,visible,origin,packet,rows = frames[u["raw_frame_id"]]
            row = rows[u["query"]["candidate_index"]]
            require((row["source"],row["canonical_y"]) ==
                    (u["measurement"]["source"],u["measurement"]["source_y"]),"wrong binding")
            out["raster_witness"] = observe(gray,visible,origin,row,packet["band_width_px"],
                                            frame_key=u["raw_frame_id"])
            out["legacy_input_eligible"] = u["measurement"]["input_eligible"]
        units.append(out)
    oil = [u for u in units if "raster_witness" in u]
    by_id = {u["id"]:u for u in oil}
    by_key = {(u["raw_frame_id"],u["query"]["candidate_index"]):u for u in oil}
    require(len(by_key)==175 and len(units)==187,"population changed")
    pairs = []
    for old in previous["units"]:
        if "measurement" not in old:
            continue
        for contributor in old["measurement"]["contributors"]:
            peer = by_key[(old["raw_frame_id"],contributor["candidate_input_index"])]
            shared = shared_measurements(by_id[old["id"]]["raster_witness"],peer["raster_witness"])
            pairs.append({"left":old["id"],"right":peer["id"],"shared":shared,
                          "independent_support_granted":False})
    summary = {"total_units":len(units),"frames":len(frames),
        "source_kind_counts":dict(Counter(u["source_kind"] for u in units)),
        "positive_contribution_pairs":len(pairs),
        "pairs_with_any_shared_partition":sum(bool(p["shared"]) for p in pairs),
        "pairs_with_three_shared_partition_sectors":sum(len(p["shared"])>=3 for p in pairs),
        "physical_discriminator_adopted":False,"by_review":{}}
    for label in ("ACCEPTED","OPPOSED","UNASSESSED"):
        group = [u for u in oil if u["review_label"]==label]
        summary["by_review"][label] = {"units":len(group),
            "three_localized_sectors":[u["id"] for u in group if u["raster_witness"]["localized_sector_count"]>=3],
            "three_partition_sectors":[u["id"] for u in group if u["raster_witness"]["partition_sector_count"]>=3],
            "frame_partition_presence": {fid:any(u["raster_witness"]["partition_sector_count"]>=3 for u in group if u["raw_frame_id"]==fid)
                                        for fid in sorted({u["raw_frame_id"] for u in group})}}
    for p,h in pins.items():
        require(sha256((root/p).read_bytes()).hexdigest()==h,f"input mutated: {p}")
    return {"schema":SCHEMA,"inputs":pins,"summary":summary,"units":units,"pairs":pairs,
        "runtime_seconds":time.monotonic()-started,"production_changed":False,
        "report_comprehension":"NOT_EVALUATED","windows_replay":"NOT_RUN",
        "physical_accuracy":"NOT_EVALUATED","source_inputs_unchanged":True}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    result = run(args.root.resolve())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    payload = (json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+"\n").encode()
    args.output.write_bytes(gzip.compress(payload,mtime=0) if args.output.suffix==".gz" else payload)
    print(json.dumps(result["summary"],ensure_ascii=False,indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
