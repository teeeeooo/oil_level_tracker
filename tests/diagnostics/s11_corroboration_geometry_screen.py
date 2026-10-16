"""Join saved peer support to native geometry; never grant detector authority."""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import gzip
from hashlib import sha256
import json
import math
from pathlib import Path

import cv2
import numpy as np

PREFIX = "docs/50-diagnostics/s11/"
PEERS = PREFIX + "2026-10-16-corroboration-peer-screen/readout.json.gz"
PREPARED = PREFIX + "2026-10-14-candidate-rgb-trial/prepared.json"
PUBLIC = PREFIX + "2026-10-12-public-compressor-source/current-frame/"
SCHEMA = "s11-corroboration-geometry-screen-v1"
MOMENT_ATOL = 1e-7  # arithmetic equivalence, not a classifier threshold


def require(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def fingerprint(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def bind_packet(raw: dict, packet: dict) -> dict[int, dict]:
    require(packet["source_frame_index"] == raw["frame_index"], "wrong frame")
    require(packet["coordinate_space"] == "source_frame_y", "wrong coordinates")
    require(packet["candidate_index_space"] ==
            "detection.candidates_before_trace_score_sort", "wrong index space")
    result = {}
    for row in packet["candidates"]:
        i = row["candidate_input_index"]
        require(type(i) is int and 0 <= i < len(raw["candidates"]), "invalid index")
        require(i not in result, "duplicate candidate")
        candidate = raw["candidates"][i]
        require(candidate["kind"] == "oil_air", "non-Oil witness")
        require((row["source"], row["canonical_y"]) ==
                (candidate["source"], candidate["y"]), "source/Y mismatch")
        result[i] = row
    expected = {i for i, c in enumerate(raw["candidates"]) if c["kind"] == "oil_air"}
    require(set(result) == expected, "incomplete Oil population")
    return result


def native_sectors(row: dict) -> list[dict]:
    path = row["path_aligned"]
    if path.get("reason") != "native_generator_path":
        require(not path.get("sectors"), "uncertified path has sectors")
        return []
    sectors = path["sectors"]
    require(len(sectors) <= 5, "native path exceeds sector budget")
    require(len({s["sector"] for s in sectors}) == len(sectors), "duplicate sector")
    for s in sectors:
        x0, x1 = s["source_x_range"]
        require(0 <= s["sector"] < 5 and x0 < x1 and
                math.isfinite(s["path_source_y"]), "invalid native geometry")
    return sectors


def compare_native(a: dict, b: dict) -> dict:
    left, right = native_sectors(a), native_sectors(b)
    cells = []
    for sa in left:
        for sb in right:
            lo = max(sa["source_x_range"][0], sb["source_x_range"][0])
            hi = min(sa["source_x_range"][1], sb["source_x_range"][1])
            if lo >= hi:
                continue
            cells.append({"source_x_range": [lo, hi],
                "left_sector": sa["sector"], "right_sector": sb["sector"],
                "left_y": sa["path_source_y"], "right_y": sb["path_source_y"],
                "absolute_delta_y": abs(sa["path_source_y"]-sb["path_source_y"]),
                "left_near_contrast": sa["near_signed_contrast"],
                "right_near_contrast": sb["near_signed_contrast"]})
    return {"status": "BOTH_NATIVE" if left and right else "NATIVE_UNAVAILABLE",
        "left_native": bool(left), "right_native": bool(right), "cells": cells,
        "shared_derivation": sorted(set(a["path_aligned"].get("shared_derivation", []))
                                    & set(b["path_aligned"].get("shared_derivation", []))),
        "measurement_independence": "NOT_ESTABLISHED",
        "physical_same_interface": "NOT_EVALUATED"}


def verify_band(gray: np.ndarray, visible: np.ndarray, origin: list[int],
                sector: dict, band: dict) -> dict:
    """Direct pixel indexing, independent of production row-prefix sums."""
    require(gray.shape == visible.shape and gray.ndim == 2, "raster shape mismatch")
    x0, x1 = [x-origin[0] for x in sector["source_x_range"]]
    a, b = band["local_y_range"]
    height, width = gray.shape
    require(0 <= x0 < x1 <= width and a < b, "invalid band geometry")
    lo, hi = max(0, min(height, a)), max(0, min(height, b))
    mask = visible[lo:hi, x0:x1]
    values = gray[lo:hi, x0:x1][mask].astype(np.float64) / 255.0
    count = values.size
    fraction = count / ((b-a)*(x1-x0))
    available = 0 <= a < b <= height and count >= 8 and fraction >= 0.5
    differences = []
    for key, value in (("valid_pixel_count", count), ("available", available)):
        if band[key] != value:
            differences.append(key)
    errors = {"valid_fraction": abs(fraction-band["valid_fraction"])}
    if available:
        for key, value in (("gray_mean", float(values.mean())),
                           ("gray_std", float(values.std()))):
            if band[key] is None or not math.isfinite(band[key]):
                differences.append(key+"_missing_or_nonfinite")
            else:
                errors[key] = abs(value-band[key])
    elif band["gray_mean"] is not None or band["gray_std"] is not None:
        differences.append("unavailable_moments_not_null")
    differences.extend(k for k, v in errors.items() if v > MOMENT_ATOL)
    return {"mismatches": differences, "max_moment_error": max(errors.values())}


def run(root: Path) -> dict:
    pins: dict[str, str] = {}

    def pin(relative: str, expected: str | None = None) -> Path:
        path = root / relative
        digest = fingerprint(path)
        require(expected is None or digest == expected, f"input hash mismatch: {relative}")
        pins[relative] = digest
        return path

    def load(relative: str, expected: str | None = None) -> dict:
        path = pin(relative, expected)
        data = path.read_bytes()
        return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)

    previous = load(PEERS)
    for relative, expected in previous["inputs"].items():
        pin(relative, expected)
    prepared = load(PREPARED, previous["inputs"][PREPARED])
    frames = {}
    for fid, spec in prepared["frames"].items():
        rgb = pin(**{"relative": spec["rgb"]["path"], "expected": spec["rgb"]["sha256"]})
        visibility = pin(spec["visibility"]["path"], spec["visibility"]["sha256"])
        if fid.startswith("sample4-f"):
            frame = int(fid.split("-f")[1])
            relative = f"sample/output/s11-a1-lineage-20261007-001/frames-final/f{frame}.json"
            capture = load(relative, previous["inputs"][relative])
            raw, state = capture["current"], capture["state"]
            bgr = cv2.imread(str(rgb), cv2.IMREAD_COLOR)
            require(bgr is not None, "missing source raster")
            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
            with np.load(visibility, allow_pickle=False) as archive:
                visible = archive[spec["mask_key"]].copy()
        else:
            require(fid == "public-f1499", "unexpected source")
            raw = load(PUBLIC + "native-none.json")
            state = load(PUBLIC + "native-diagnostics.json.gz")["state"]
            with np.load(rgb, allow_pickle=False) as archive:
                gray = cv2.cvtColor(archive["original_roi"], cv2.COLOR_BGR2GRAY)
                require(np.array_equal(gray, archive["grayscale"]), "gray conversion mismatch")
                visible = (archive["effective_mask"] > 0) & (archive["glare_mask"] == 0)
        packet = state["oil_interface_diagnostics"]
        require(packet["crop_origin"] == spec["origin"], "crop origin mismatch")
        require(list(gray.shape) == spec["shape"] == list(visible.shape), "crop shape mismatch")
        rows = bind_packet(raw, packet)
        for row in rows.values():
            for s in native_sectors(row):
                require(s["path_source_y"] == s["path_local_y"]+spec["origin"][1],
                        "native source/local mismatch")
        frames[fid] = {"rows": rows, "raw": raw, "packet": packet,
                       "gray": gray, "visible": visible, "origin": spec["origin"]}
    units, band_errors, unique_windows = [], [], set()
    band_count, max_error = 0, 0.0
    by_key = {(u["raw_frame_id"], u["query"]["candidate_index"]): u
              for u in previous["units"] if "measurement" in u}
    require(len(by_key) == previous["summary"]["oil_candidates"], "duplicate Oil unit")
    for unit in previous["units"]:
        out = deepcopy({k: v for k, v in unit.items() if k != "measurement"})
        if "measurement" not in unit:
            units.append(out)
            continue
        fid, i = unit["raw_frame_id"], unit["query"]["candidate_index"]
        f = frames[fid]
        row = f["rows"][i]
        require((row["source"], row["canonical_y"]) ==
                (unit["measurement"]["source"], unit["measurement"]["source_y"]),
                "peer readout identity mismatch")
        native = native_sectors(row)
        out["geometry"] = {"native_available": bool(native),
            "native_reason": row["path_aligned"]["reason"],
            "native_sector_count": len(native), "peers": []}
        for mode, sectors in (("candidate_center", row["sectors"]), ("native", native)):
            for s in sectors:
                for name, band in s["bands"].items():
                    check = verify_band(f["gray"], f["visible"], f["origin"], s, band)
                    band_count += 1
                    unique_windows.add((fid, *s["source_x_range"], *band["local_y_range"]))
                    max_error = max(max_error, check["max_moment_error"])
                    if check["mismatches"]:
                        band_errors.append({"unit": unit["id"], "mode": mode,
                            "sector": s["sector"], "band": name, **check})
        for peer in unit["measurement"]["contributors"]:
            j = peer["candidate_input_index"]
            peer_unit = by_key[(fid, j)]
            peer_row = f["rows"][j]
            require((peer_row["source"], peer_row["canonical_y"]) ==
                    (peer["source"], peer["source_y"]), "peer source/Y mismatch")
            relation = compare_native(row, peer_row)
            out["geometry"]["peers"].append({"id": peer_unit["id"],
                "candidate_input_index": j, "review_label": peer_unit["review_label"],
                "legacy_support": peer["support"],
                "legacy_winner": j in unit["measurement"]["winning_peer_indexes"],
                **relation})
        out["legacy_support"] = unit["measurement"]["legacy_support"]
        out["material_consumer"] = unit["measurement"]["proposed_gate_consumer"]
        units.append(out)
    oil = [u for u in units if "geometry" in u]
    edges = [p for u in oil for p in u["geometry"]["peers"]]
    summary = {"total_units": len(units), "frames": len(frames),
        "kinds": dict(Counter(u["source_kind"] for u in units)),
        "oil_native_available": sum(u["geometry"]["native_available"] for u in oil),
        "positive_contribution_pairs": len(edges),
        "pair_geometry": dict(Counter(e["status"] for e in edges)),
        "band_references_checked": band_count, "unique_band_windows": len(unique_windows),
        "band_mismatch_references": len(band_errors), "max_moment_error": max_error,
        "by_review": {label: {"units": sum(u["review_label"] == label for u in oil),
            "native_available": [u["id"] for u in oil if u["review_label"] == label
                                 and u["geometry"]["native_available"]],
            "has_two_native_peer": [u["id"] for u in oil if u["review_label"] == label
                 and any(p["status"] == "BOTH_NATIVE" for p in u["geometry"]["peers"])]}
                       for label in ("ACCEPTED", "OPPOSED", "UNASSESSED")}}
    for rel, digest in pins.items():
        require(fingerprint(root/rel) == digest, f"input mutated: {rel}")
    require(set(by_key) == {(fid, i) for fid, f in frames.items() for i in f["rows"]},
            "unit/frame population mismatch")
    return {"schema": SCHEMA, "summary": summary, "inputs": pins, "units": units,
        "band_errors": band_errors, "moment_arithmetic_tolerance": MOMENT_ATOL,
        "G1": "AVAILABILITY_AUDIT_COMPLETE", "G2": "GEOMETRY_NOT_PHYSICAL_IDENTITY",
        "G3": "RASTER_MOMENTS_EQUAL" if not band_errors else "RASTER_MISMATCH",
        "production_changed": False, "classifier_or_gate_adopted": False,
        "physical_accuracy": "NOT_EVALUATED", "report_comprehension": "NOT_EVALUATED",
        "windows_replay": "NOT_RUN", "source_inputs_unchanged": True}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+"\n").encode()
    args.output.write_bytes(gzip.compress(payload, mtime=0)
                            if args.output.suffix == ".gz" else payload)
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
    return int(bool(result["band_errors"]))


if __name__ == "__main__":
    raise SystemExit(main())
