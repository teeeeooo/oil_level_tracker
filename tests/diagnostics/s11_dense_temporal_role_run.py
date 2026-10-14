"""Frozen DTO-1 corpus runner: source-bound raw maps, no production consumer."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import resource
import sys
import time
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]
import cv2
import numpy as np
from tests.diagnostics import s11_dense_temporal_role_probe as dto

CORPUS = (
 "docs/50-diagnostics/s11/2026-10-14-semantic-role-readiness/corpus.json",
 "docs/50-diagnostics/s11/2026-10-14-native-contact-trial/sample4-extension.json",
 "docs/50-diagnostics/s11/2026-10-14-raw-front-inventory/base-extension.json")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ahash(array):
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def verified(root, pin):
    path = root / pin["path"]
    if sha(path) != pin["sha256"]:
        raise ValueError(f"input pin mismatch: {pin['path']}")
    return path


def load(root):
    rows, frames, pins = [], {}, []
    for name in CORPUS:
        path = root/name
        data = json.loads(path.read_text())
        pins.append({"path": name, "sha256": sha(path)})
        rows.extend(data.get("rows", data.get("added_rows", [])))
        for key, value in data.get("frames", data.get("added_frames", {})).items():
            if key in frames:
                raise ValueError("duplicate frame")
            frames[key] = value
    if len(rows) != 137 or len({r['id'] for r in rows}) != 137 or len(frames) != 8:
        raise ValueError("frozen population changed")
    return rows, frames, pins


def synthetic():
    rng = np.random.default_rng(20261014)
    texture = rng.integers(20, 90, (80, 80), dtype=np.uint8)
    yy, xx = np.indices(texture.shape, dtype=np.float32)
    constant = np.full_like(texture, 40)
    cases = {"constant": [constant]*13,
             "affine_brightness": [texture*(1+t % 2)+t for t in range(13)]}
    for name in ("static_translation", "static_optical_warp"):
        frames = []
        for t in range(13):
            changed = (np.roll(texture, t, axis=1) if name == "static_translation" else
                       cv2.remap(texture, xx + 2*np.sin(yy/8+t/2), yy,
                                 cv2.INTER_NEAREST, borderMode=cv2.BORDER_REFLECT_101))
            frame = constant.copy()
            frame[40:] = changed[40:]
            frames.append(frame)
        cases[name] = frames
    return {name: dto.paired_score(dto.measure(frames)["turnover"],
                                  [[40, 34]], [[40, 46]])
            for name, frames in cases.items()}


def decode_window(root, entry):
    """Decode the fixed trailing window and enforce saved current-frame identity."""
    path = verified(root, entry["source_recording"])
    saved = cv2.imread(str(verified(root, entry["rgb"])))
    x, y = entry["geometry"]["origin"]
    h, w = entry["geometry"]["shape"]
    ix, iy = entry["image_origin"]
    saved_roi = saved[y-iy:y-iy+h, x-ix:x-ix+w]
    if ahash(saved_roi[:, :, ::-1]) != entry["roi_sha256"]:
        raise ValueError("saved ROI byte identity mismatch")
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError("video unavailable")
    gray_frames, hashes, times = [], [], []
    try:
        start = entry["frame"] - 12
        if start < 0 or not cap.set(cv2.CAP_PROP_POS_FRAMES, start):
            raise ValueError("fixed window unavailable")
        for expected in range(start, entry["frame"]+1):
            ok, frame = cap.read()
            if not ok or int(cap.get(cv2.CAP_PROP_POS_FRAMES)) != expected+1:
                raise ValueError("frame decode or index mismatch")
            crop = frame[y:y+h, x:x+w]
            if crop.shape != saved_roi.shape:
                raise ValueError("ROI shape changed")
            hashes.append(ahash(crop[:, :, ::-1]))
            times.append(float(cap.get(cv2.CAP_PROP_POS_MSEC))/1000)
            gray_frames.append(cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY))
        if not np.array_equal(crop, saved_roi):
            raise ValueError("decoded anchor differs from frozen source pixels")
    finally:
        cap.release()
    return gray_frames, hashes, times


def run(root, work):
    started = time.perf_counter()
    rows, frames, corpus_pins = load(root)
    output, subjects = [], []
    for key, entry in frames.items():
        grays, hashes, times = decode_window(root, entry)
        maps = dto.measure(grays)
        ox, oy = entry["geometry"]["origin"]
        ix, iy = entry["image_origin"]
        for row in rows:
            if row["frame_key"] != key:
                continue
            sides = row["native_sides"]
            centers = {name: [[int(x+ix-ox), int(y+iy-oy)] for x, y in
                             data["centers_image_xy"]] for name, data in sides.items()}
            result = {"id": row["id"], "frame_key": key,
                      "role": row["certain_boundary_role"],
                      "allowed_roles": row["allowed_boundary_roles"],
                      "original_availability": row["availability"], "measurements": {}}
            for channel in ("turnover", "static_complexity"):
                result["measurements"][channel] = dto.paired_score(
                    maps[channel], centers.get("upper", []), centers.get("lower", []))
            subjects.append(result)
        profile = dto.center_profile(maps["turnover"], entry["geometry"]["column"])
        output.append({"frame_key": key, "source": entry["source_recording"],
                       "anchor_frame": entry["frame"], "geometry": entry["geometry"],
                       "rgb_pin": entry["rgb"], "roi_hashes": hashes, "times": times,
                       "anchor_equal": True, "frames_decoded": len(grays),
                       "raw_finite_pixels": int(np.isfinite(maps["turnover"]).sum()),
                       "roi_pixels": int(maps["turnover"].size), "center_profile": profile})
        print(f"verified {Path(entry['source_recording']['path']).name} f{entry['frame']}", flush=True)
        del grays, maps
    comparisons = []
    positives = [r for r in subjects if r["role"] == "FOAM_UPPER"]
    negatives = [r for r in subjects if r["role"] in ("INTERNAL_FOAM_CHANGE", "STRUCTURE_BOUNDARY")]
    for positive in positives:
        for negative in negatives:
            cross_time = (positive["id"], negative["id"]) == ("N3", "N5")
            if positive["frame_key"] != negative["frame_key"] and not cross_time:
                continue
            checks = {}
            for channel in ("turnover", "static_complexity"):
                a = positive["measurements"][channel]["score"]
                b = negative["measurements"][channel]["score"]
                checks[channel] = {"positive": a, "negative": b,
                                   "passes": None if a is None or b is None else a > b}
            comparisons.append({"positive": positive["id"], "negative": negative["id"],
                                "cross_time": cross_time, "checks": checks})
    result = {"schema": "s11-dto1-frozen-readout-v1", "corpus_pins": corpus_pins,
              "source_pins": [{"path": str(p.relative_to(root)), "sha256": sha(p)}
                              for p in (Path(__file__), root/"tests/diagnostics/s11_dense_temporal_role_probe.py")],
              "frames": output, "subjects": subjects, "comparisons": comparisons,
              "synthetic": synthetic(), "elapsed_seconds": time.perf_counter()-started,
              "peak_rss_native_units": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              "platform": sys.platform, "runtime": {"python": sys.version,
              "numpy": np.__version__, "opencv": cv2.__version__},
              "production_changed": False, "physical_acceptance": "NOT_EVALUATED"}
    destination = work/"readout.json"
    if destination.exists():
        raise ValueError("refuse overwrite")
    payload = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+"\n"
    if len(payload.encode()) > 2_000_000:
        raise ValueError("retained budget exceeded")
    destination.write_text(payload, encoding="utf-8")
    print(json.dumps({"subjects": len(subjects), "comparisons": len(comparisons),
                      "turnover_passes": sum(r["checks"]["turnover"]["passes"] is True for r in comparisons),
                      "elapsed_seconds": result["elapsed_seconds"]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--work", type=Path, required=True)
    args = parser.parse_args()
    if not args.work.is_dir():
        raise ValueError("managed work directory must already exist")
    run(args.root.resolve(), args.work.resolve())
