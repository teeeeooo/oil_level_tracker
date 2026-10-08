#!/usr/bin/env python3
"""Recheck the stored Mac A/B sequences with pinned, unchanged repository code.

This is a portable helper delivered with the work specification, not a detector
patch. It neither decodes video nor changes recipes, truth, or production files.
Run using the repository virtual environment; provide a NEW output directory.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

PINNED_HEAD = "18885d226a7a7745bc2d062fd750ec263b9c78f6"
PAIR_DIRECTORY = Path("sample/output/s11-d2-recipe-artifact-20261008-001")
VARIANTS = (
    ("unregistered", "baseline.oilrecipe"),
    ("registered_pink822", "registered-pink822.oilrecipe"),
)


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def head_at(repo: Path) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repo, text=True
    ).strip()


def save_json(path: Path, value: Any) -> None:
    # Exclusive creation prevents an audit from overwriting earlier evidence.
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    repo, out = args.repo.resolve(), args.output.resolve()
    if not (repo / ".git").exists():
        raise ValueError(f"Not a repository checkout: {repo}")
    if out.exists():
        raise ValueError(f"Use a new output directory: {out}")
    if head_at(repo) != PINNED_HEAD:
        raise ValueError("HEAD differs from the specification. Refresh the audit explicitly.")
    dirty = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=no"], cwd=repo, text=True
    )
    if dirty.strip():
        raise ValueError("Tracked changes are present; a clean pinned checkout is required.")

    prior = repo / PAIR_DIRECTORY
    receipt_path = prior / "pipeline-receipt.json"
    previous_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    inputs = list(sorted((repo / "src").rglob("*.py")))
    inputs += list(sorted((repo / "sample").glob("*.oiltruth")))
    inputs.append(receipt_path)
    for variant, recipe_name in VARIANTS:
        for suffix in ("raw", "completed"):
            name = f"{variant}-{suffix}.json"
            path = prior / name
            expected_digest = previous_receipt["outputs"][name]
            if digest(path) != expected_digest:
                raise ValueError(f"Stored receipt mismatch: {name}")
            inputs.append(path)
        inputs.append(prior / recipe_name)
    pins = {str(path.relative_to(repo)): digest(path) for path in inputs}
    out.mkdir(parents=True, exist_ok=False)
    save_json(out / "preflight.json", {
        "head": PINNED_HEAD,
        "runner_sha256": digest(Path(__file__).resolve()),
        "inputs": pins,
        "scope": "Stored raw detections -> current completed resolver. No image detector.",
    })

    sys.path.insert(0, str(repo / "src"))
    from oil_tracker.domain.detection import BoundaryCandidate, PhaseDetection
    from oil_tracker.domain.enums import BoundaryKind, FillState
    from oil_tracker.domain.recipe import InspectionRecipe
    from oil_tracker.adapters.vision.observation_sequence_resolver import ObservationSequenceResolver

    def decode(saved: dict[str, Any]) -> PhaseDetection:
        value = deepcopy(saved)
        value["fill_state"] = FillState(value["fill_state"])
        value["candidates"] = [
            BoundaryCandidate(**{**candidate, "kind": BoundaryKind(candidate["kind"])})
            for candidate in value["candidates"]
        ]
        return PhaseDetection(**value)

    checks: dict[str, Any] = {}
    for variant, recipe_name in VARIANTS:
        raw = json.loads((prior / f"{variant}-raw.json").read_text(encoding="utf-8"))
        expected = json.loads((prior / f"{variant}-completed.json").read_text(encoding="utf-8"))
        recipe = InspectionRecipe.from_dict(
            json.loads((prior / recipe_name).read_text(encoding="utf-8"))
        )
        glass = recipe.glasses[0]
        start = time.monotonic()
        result = ObservationSequenceResolver().resolve(
            [decode(row) for row in raw], glass, glass.initial_state
        )
        # Normalize tuple/list representation only; do not drop any output field.
        actual = json.loads(json.dumps([asdict(row) for row in result.detections]))
        equal = len(actual) == 113 and actual == expected
        checks[variant] = {
            "complete_detection_count": len(actual),
            "entire_output_equal": equal,
            "elapsed_sec": time.monotonic() - start,
            "anchors": [
                {"frame_index": row["frame_index"], "raw_oil_y": row["raw_oil_air_level_y"]}
                for row in actual if row["frame_index"] in (1320, 1485, 1560)
            ],
        }
        if not equal:
            save_json(out / "mismatch.json", {
                "variant": variant, "actual_count": len(actual),
                "expected_count": len(expected),
                "different_positions": [
                    index for index, (left, right) in enumerate(zip(actual, expected))
                    if left != right
                ],
            })
            raise AssertionError(f"Full-output equality failed: {variant}")
        print(f"{variant}: {len(actual)} complete detections equal", flush=True)

    for name, expected_digest in pins.items():
        if digest(repo / name) != expected_digest:
            raise AssertionError(f"Input changed during audit: {name}")
    if head_at(repo) != PINNED_HEAD:
        raise AssertionError("HEAD changed during audit")
    save_json(out / "receipt.json", {
        "head": PINNED_HEAD, "checks": checks,
        "inputs_preserved": True, "input_pin_count": len(pins),
        "production_changed": False, "labels_changed": False,
        "video_read": False, "frame_detector_rerun": False,
        "completed_resolver_rerun": True, "field_qualification": False,
        "preflight_sha256": digest(out / "preflight.json"),
    })
    print("COMPLETE: 226 unchanged completed detections; no efficacy claim.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, AssertionError, subprocess.SubprocessError) as exc:
        print(f"AUDIT FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1)
