#!/usr/bin/env python3
"""Reproduce a read-only, fixed native-feature footprint canary.

Run with the audited repository's existing virtual environment. No encoder,
video decode, tracker, training, full replay, or production file writes occur.
This tests dependency support, not material identity or detection accuracy.

The original core calculation was executed during the review. This CLI wrapper
adds input guards and exclusive output handling; it is not a new detector.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

HEAD = "badf7caddebc7e75013ef02c888d2b72f13feb92"
PLAN = "docs/50-diagnostics/s11/2026-10-13-foam-material-sides/preflight.json"
PLAN_SHA = "d414111b9afc891c0e290b4bd0d73a4702fc1abbde26c242a27082e09352730f"
OWNER = "src/oil_tracker/adapters/vision/foam_front_detector.py"
OWNER_SHA = "b1b19e3384925c44344ebaa8010ff75569885448f314f8531fec94294cfde947"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def inside(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Input escapes repository root: {relative}")
    return path


def run(root: Path) -> dict[str, Any]:
    root = root.resolve(strict=True)
    head = subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()
    if head != HEAD:
        raise ValueError("HEAD changed. Review the new baseline instead of silently replaying this pin.")
    for name, expected in ((PLAN, PLAN_SHA), (OWNER, OWNER_SHA)):
        if digest(inside(root, name)) != expected:
            raise ValueError(f"Changed pinned input: {name}")
    saved = inside(root, "docs/50-diagnostics/s11/2026-10-11-p5-default-linkage/readout.json")
    if digest(saved) != "e90b1d5d90af2c561c6357b9fa86e3a10074ff6252947398ff9300e9c4513e51":
        raise ValueError("Changed saved default-run readout")
    source_pins = json.loads(saved.read_text(encoding="utf-8"))["inputs"]
    for name, expected in source_pins.items():
        if name.startswith("src/") and digest(inside(root, name)) != expected:
            raise ValueError(f"Changed production source: {name}")
    plan = json.loads(inside(root, PLAN).read_text(encoding="utf-8"))
    case = next(c for c in plan["cases"] if c["id"] == "s4-f1620")
    for name in case["images"].values():
        if digest(inside(root, name)) != plan["pins"][name]:
            raise ValueError(f"Changed image: {name}")

    # Resolve only the audited local code; do not install or download anything.
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(root / "src"))
    import numpy as np
    from PIL import Image
    from oil_tracker.adapters.vision.foam_front_detector import _texture_evidence
    from oil_tracker.domain.recipe import DetectorSettings

    start = time.monotonic()
    images = {k: np.array(Image.open(inside(root, p))) for k, p in case["images"].items()}
    original = {k: a.copy() for k, a in images.items()}
    valid = (images["effective_mask"] > 0) & (images["glare_mask"] == 0)
    settings = DetectorSettings()  # Default settings, not a claimed Recipe replay.
    baseline = _texture_evidence(images["grayscale"], images["canny"], valid, settings)
    y, x = 813 - case["origin"][1], case["column"]
    results = []
    for fill in (0, 255):  # Frozen interventions: do not optimize these values.
        gray, canny = images["grayscale"].copy(), images["canny"].copy()
        gray[~valid], canny[~valid] = fill, fill
        changed = _texture_evidence(gray, canny, valid, settings)
        row: dict[str, Any] = {
            "masked_fill": fill,
            "inside_input_bytes_equal": bool(
                np.array_equal(gray[valid], images["grayscale"][valid])
                and np.array_equal(canny[valid], images["canny"][valid])
            ),
            "features": {},
        }
        for name, a, b in zip(("variance", "edge_density", "texture"), baseline, changed):
            delta = np.abs(a - b)
            row["features"][name] = {
                "changed_visible_pixels": int(np.count_nonzero(delta[valid] > 1e-6)),
                "max_visible_abs_delta": float(delta[valid].max()),
                "anchor_baseline": float(a[y, x]),
                "anchor_counterfactual": float(b[y, x]),
                "anchor_abs_delta": float(delta[y, x]),
            }
        results.append(row)
    return {
        "schema": "s11-native-feature-support-canary-v1",
        "kind": "CONSTRUCTED_MASKED_PIXEL_INTERVENTION_NOT_SCENE_TRUTH",
        "head": head, "case_id": case["id"], "native_anchor": [595, 813],
        "anchor_visible": bool(valid[y, x]),
        "visible_pixels": int(valid.sum()), "masked_pixels": int((~valid).sum()),
        "settings_scope": "DetectorSettings() defaults; not a full Recipe replay",
        "results": results,
        "source_arrays_unchanged": all(np.array_equal(original[k], images[k]) for k in original),
        "elapsed_sec_excluding_imports": time.monotonic() - start,
        "new_model_calls": 0, "video_decodes": 0, "production_replays": 0,
        "physical_identity": "NOT_EVALUATED", "detector_improvement": "NOT_EVALUATED",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True, help="Audited local repository root")
    parser.add_argument("--output", type=Path, help="New output JSON; an existing file is never overwritten")
    args = parser.parse_args()
    try:
        output = json.dumps(run(args.repo), ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        if args.output:
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(output)
        else:
            print(output, end="")
    except (OSError, ValueError, KeyError, StopIteration, ImportError, subprocess.SubprocessError) as exc:
        print(f"Canary stopped: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
