"""Observe the reviewed saved PNG through the unchanged baseline frame entry."""
import argparse
from contextlib import ExitStack
from dataclasses import asdict
import gzip
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]

import cv2
import numpy as np
from oil_tracker.adapters.storage.jsonl_debug_trace_writer import _json_safe
from tests.diagnostics import s11_overlay_mask_comparison as comparison

o2, old = comparison.reuse.o2, comparison.rgb.native


def probe(plan):
    for pin in plan["sources"] + list(plan["inputs"].values()):
        comparison.reuse.g0.pinned_path(ROOT, pin)
    inputs = plan["inputs"]
    source = comparison.reuse.read_pin(ROOT, inputs["source_plan"])
    for pin in source["inputs"].values():
        comparison.reuse.g0.pinned_path(ROOT, pin)
    frame = cv2.imread(str(ROOT / source["inputs"]["image"]["path"]))
    recipe = comparison.InspectionRecipe.from_dict(
        comparison.reuse.read_pin(ROOT, source["inputs"]["recipe"]))
    glass = recipe.glasses[0]
    original = comparison.baseline(comparison.reuse.read_pin(ROOT, source["inputs"]["comparison_plan"]))
    begin = time.perf_counter()
    with ExitStack() as stack:
        comparison.activate(original, stack)
        detector = comparison.OpenCvPhaseDetector()
        detection, artifacts = detector.detect(frame, glass, source["frame"], plan["time_sec"], debug=True)
    elapsed = time.perf_counter() - begin
    with np.load(ROOT / inputs["raster"]["path"], allow_pickle=False) as saved:
        equality = {key: np.array_equal(saved[key], artifacts.images[key]) for key in saved.files}
    o2.require(all(equality.values()), "real frame entry differs from reviewed baseline rasters")
    source_files = {p.relative_to(ROOT).as_posix(): o2.sha256_file(p)
                    for p in sorted((ROOT / "src").rglob("*.py"))}
    baseline_plan = comparison.reuse.read_pin(ROOT, source["inputs"]["comparison_plan"])
    source_files[baseline_plan["preprocessor"]] = baseline_plan["baseline_preprocessor_sha256"]
    return _json_safe(dict(schema="s11-reviewed-native-frame-entry-v1",
        plan_sha256=o2.fingerprint_json(plan), source_files=source_files,
        source_sha256=comparison.witness._digest(source_files), baseline_substitution=True,
        image=source["inputs"]["image"], frame=source["frame"], time_sec=plan["time_sec"],
        real_entry_raster_equality=equality, detection=asdict(detection),
        candidate_rows=artifacts.candidate_rows, state=artifacts.state,
        images={key: dict(shape=list(value.shape), dtype=str(value.dtype),
                         nonzero=int(np.count_nonzero(value)), sha256=old.array_hash(value))
                for key, value in artifacts.images.items()},
        detect_seconds=elapsed, fresh_detector=True, static_learning=False,
        session_initial_confirmation=False, sequence_resolved=False, report_run=False,
        video_decodes=0, model_calls=0, production_changed=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    o2.require(not args.output.exists(), "refuse overwrite")
    result = probe(o2.read_json(args.plan))
    payload = gzip.compress(json.dumps(result, ensure_ascii=False, allow_nan=False,
        separators=(",", ":")).encode("utf-8"), mtime=0)
    o2.require(len(payload) < 500_000, "frame receipt budget exceeded")
    with args.output.open("xb") as handle:
        handle.write(payload)
    print(json.dumps(dict(candidates=len(result["detection"]["candidates"]),
        raster_equality=result["real_entry_raster_equality"], bytes=len(payload))))
