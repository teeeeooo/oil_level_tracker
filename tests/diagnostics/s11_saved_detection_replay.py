"""Bounded saved-current-detection replay; never reads source video or labels."""
from __future__ import annotations

import argparse
from dataclasses import asdict
from enum import Enum
import hashlib
import json
import math
from pathlib import Path
import platform
import time


def encode(value):
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (set, frozenset)):
        return sorted(value)
    raise TypeError(type(value).__name__)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def restore(rows):
    from oil_tracker.domain.detection import BoundaryCandidate, PhaseDetection
    from oil_tracker.domain.enums import BoundaryKind, FillState
    if not isinstance(rows, list) or not 1 <= len(rows) <= 10000:
        raise ValueError("Expected 1..10000 saved current detections")
    result = []
    for item in rows:
        row = dict(item)
        row["fill_state"] = FillState(row["fill_state"])
        row["candidates"] = [BoundaryCandidate(**{**c, "kind": BoundaryKind(c["kind"])})
                             for c in row["candidates"]]
        if not math.isfinite(row["time_sec"]) or any(not math.isfinite(c.y) for c in row["candidates"]):
            raise ValueError("Nonfinite source coordinate/time")
        result.append(PhaseDetection(**row))
    if len({d.glass_id for d in result}) != 1:
        raise ValueError("Exactly one Glass must be replayed at a time")
    if any(a.frame_index >= b.frame_index or a.time_sec >= b.time_sec
           for a, b in zip(result, result[1:])):
        raise ValueError("Source frame/time sequence is not strictly increasing")
    if json.loads(json.dumps([asdict(d) for d in result], default=encode)) != rows:
        raise ValueError("Saved observations changed during restoration")
    return tuple(result)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--recipe", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--initial-state", default="UNKNOWN_REVIEW")
    args = parser.parse_args()
    from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
    from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
    from oil_tracker.domain.enums import BoundaryKind, InitialObservationState
    import oil_tracker.adapters.vision.oil_phase_lifecycle as lifecycle

    initial = InitialObservationState(args.initial_state)
    pins = {str(p.resolve()): digest(p) for p in (args.input, args.recipe, Path(lifecycle.__file__))}
    rows = json.loads(args.input.read_text(encoding="utf-8"))
    detections = restore(rows)
    recipe = JsonRecipeRepository().load(args.recipe)
    glass = next((g for g in recipe.glasses if g.id == detections[0].glass_id), None)
    if glass is None:
        raise ValueError("Saved Glass is not bound to supplied recipe")
    args.output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    resolved = OpenCvPhaseDetector().resolve_sequence(detections, glass, initial)
    data = json.loads(json.dumps(asdict(resolved), default=encode, allow_nan=False))
    (args.output / "resolution.json").write_text(json.dumps(data, allow_nan=False), encoding="utf-8")
    provenance_failures = []
    for original, final in zip(detections, resolved.detections, strict=True):
        for value, kind in ((final.oil_air_level_y, BoundaryKind.OIL_AIR), (final.foam_front_y, BoundaryKind.FOAM_FRONT)):
            if value is not None and not any(c.kind is kind and c.y == value for c in original.candidates):
                provenance_failures.append([original.frame_index, kind.value, value])
    if any(digest(Path(p)) != pin for p, pin in pins.items()):
        raise AssertionError("Replay input/source mutation")
    if json.loads(json.dumps([asdict(d) for d in detections], default=encode)) != rows:
        raise AssertionError("Resolver mutated saved-current input")
    summary = {
        "schema": "s11-saved-detection-replay-v1", "input_pins": pins,
        "initial_state": initial.value, "rows": len(detections),
        "python": platform.python_version(), "elapsed_sec": time.monotonic() - started,
        "oil_rows": sum(d.oil_air_level_y is not None for d in resolved.detections),
        "foam_rows": sum(d.foam_front_y is not None for d in resolved.detections),
        "numeric_provenance_failures": provenance_failures,
        "input_bytes_preserved": True, "video_read": False,
        "field_disposition": "NOT_EVALUATED", "auto_acceptance": False,
        "resolution_sha256": digest(args.output / "resolution.json"),
    }
    (args.output / "receipt.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 1 if provenance_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
