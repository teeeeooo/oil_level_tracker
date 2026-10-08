"""Paired saved-input selector experiment; no source video or production edits.

Run as ``python -m tests.diagnostics.s11_cellular_selector_permutation``.
The patch is scoped to this diagnostic process and restored even on failure.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, replace
import hashlib
import json
import math
from pathlib import Path
from unittest.mock import patch

from tests.diagnostics.s11_saved_detection_replay import digest, encode, restore


SPEC = {
    "id": "cellular-selector-emission-permutation-v1",
    "initial_state": "UNKNOWN_REVIEW",
    "minimum_eligible": 2,
    "tie_tolerance": 1e-12,
    "new_authority": False,
    "new_coordinates": False,
    "production_promotion": False,
}


def permute_emissions(layer, scores):
    eligible=[]
    for index,node in enumerate(layer):
        if node.kind!='oil' or node.candidate_ref is None:continue
        value=scores.get(node.candidate_ref.candidate_offset)
        if value is not None and math.isfinite(value):
            eligible.append((index,value))
    if len(eligible)<2:return layer
    values=sorted(value for _,value in eligible)
    if any(abs(a-b)<=1e-12 for a,b in zip(values,values[1:])):return layer
    emissions=sorted(layer[index].emission for index,_ in eligible)
    output=list(layer)
    for (index,_),emission in zip(sorted(eligible,key=lambda pair:pair[1]),emissions,strict=True):
        output[index]=replace(layer[index],emission=emission)
    assert sorted(n.emission for n in output)==sorted(n.emission for n in layer)
    assert all(a.kind==b.kind and a.candidate_ref is b.candidate_ref for a,b in zip(layer,output,strict=True))
    return tuple(output)


def normalized(value):
    return json.loads(json.dumps(value, default=encode, allow_nan=False))


def fingerprint(value):
    return hashlib.sha256(json.dumps(normalized(value), sort_keys=True).encode()).hexdigest()


def bind_scores(detections, measurements):
    """Join by exact source identity, never nearest coordinate or row position."""
    if len(detections) != len(measurements):
        raise ValueError("Detection/measurement row count differs")
    bound = {}
    for detection, measurement in zip(detections, measurements, strict=True):
        key = (detection.glass_id, detection.frame_index, detection.time_sec)
        if key != tuple(measurement[k] for k in ("glass_id", "frame_index", "time_sec")):
            raise ValueError("Measurement source identity differs")
        scores = {}
        for row in measurement["rows"]:
            index = row["candidate_input_index"]
            if type(index) is not int or not 0 <= index < len(detection.candidates) or index in scores:
                raise ValueError("Invalid or duplicate candidate offset")
            candidate = detection.candidates[index]
            if row["canonical_y"] != candidate.y or row["source"] != candidate.source:
                raise ValueError("Measurement candidate identity differs")
            value = row["score"]
            if value is not None and (type(value) not in (int, float) or not math.isfinite(value)):
                raise ValueError("Score must be finite or unavailable")
            scores[index] = value
        bound[key] = scores
    return bound


def replay(saved, measurements, glass, *, intervene):
    from oil_tracker.adapters.vision import oil_observation_resolver as owner
    from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
    from oil_tracker.domain.enums import InitialObservationState

    detections = restore(saved)
    scores = bind_scores(detections, measurements)
    layers, phases = [], []
    build = owner.build_interface_layers
    phase_resolve = owner.OilMaterialPhaseLifecycleOwner.resolve

    def wrapped_build(detection, *args, **kwargs):
        phase, layer = build(detection, *args, **kwargs)
        key = (detection.glass_id, detection.frame_index, detection.time_sec)
        changed = permute_emissions(layer, scores[key]) if intervene else layer
        # Verify the intervention's boundary independently of its implementation.
        assert len(changed) == len(layer)
        assert sorted(n.emission for n in layer) == sorted(n.emission for n in changed)
        assert all(replace(a, emission=b.emission) == b and a.candidate_ref is b.candidate_ref
                   for a, b in zip(layer, changed, strict=True))
        layers.append({
            "frame_index": detection.frame_index,
            "phase_input_sha256": fingerprint([asdict(n) for n in phase]),
            "nodes": [{"kind": a.kind, "identity": a.identity, "y": a.y,
                       "candidate_offset": None if a.candidate_ref is None else a.candidate_ref.candidate_offset,
                       "score": None if a.candidate_ref is None else scores[key].get(a.candidate_ref.candidate_offset),
                       "before": a.emission, "after": b.emission}
                      for a, b in zip(layer, changed, strict=True)],
        })
        return phase, changed

    def wrapped_phase(instance, *args, **kwargs):
        result = phase_resolve(instance, *args, **kwargs)
        phases.append(normalized(asdict(result)))
        return result

    with patch.object(owner, "build_interface_layers", wrapped_build), patch.object(
        owner.OilMaterialPhaseLifecycleOwner, "resolve", wrapped_phase
    ):
        result = OpenCvPhaseDetector().resolve_sequence(
            detections, glass, InitialObservationState.UNKNOWN_REVIEW
        )
    assert len(layers) == len(detections) and len(phases) == 1, "Diagnostic seam did not execute"
    assert normalized([asdict(d) for d in detections]) == saved, "Saved inputs mutated"
    return normalized(asdict(result)), layers, phases


def paired_replay(saved, measurements, glass):
    from oil_tracker.domain.enums import BoundaryKind

    baseline, baseline_layers, baseline_phases = replay(saved, measurements, glass, intervene=False)
    alternate, layers, phases = replay(saved, measurements, glass, intervene=True)
    assert baseline_phases == phases, "Material lifecycle or allowed owners changed"
    assert [r["phase_input_sha256"] for r in layers] == [r["phase_input_sha256"] for r in baseline_layers]
    rows = []
    for raw, original, changed, layer in zip(saved, baseline["detections"], alternate["detections"], layers, strict=True):
        for result in (original, changed):
            for field, kind in (("oil_air_level_y", BoundaryKind.OIL_AIR.value), ("foam_front_y", BoundaryKind.FOAM_FRONT.value)):
                assert result[field] is None or any(c["kind"] == kind and c["y"] == result[field] for c in raw["candidates"]), "Lost numeric provenance"
        rows.append({
            "frame_index": raw["frame_index"], "time_sec": raw["time_sec"],
            "baseline_oil_y": original["oil_air_level_y"], "experimental_oil_y": changed["oil_air_level_y"],
            "baseline_foam_y": original["foam_front_y"], "experimental_foam_y": changed["foam_front_y"],
            "state_changed": original["fill_state"] != changed["fill_state"],
            "changed_emissions": sum(n["before"] != n["after"] for n in layer["nodes"]),
        })
    summary = {
        "rows": len(rows), "permuted_frames": sum(r["changed_emissions"] > 0 for r in rows),
        "oil_coordinate_changes": sum(r["baseline_oil_y"] != r["experimental_oil_y"] for r in rows),
        "foam_coordinate_changes": sum(r["baseline_foam_y"] != r["experimental_foam_y"] for r in rows),
        "state_changes": sum(r["state_changed"] for r in rows),
        "phase_inputs_equal": True, "lifecycle_and_allowed_owners_equal": True,
        "raw_detections_equal": True, "numeric_provenance_failures": [],
        "baseline_diagnostics": baseline["diagnostics"], "experimental_diagnostics": alternate["diagnostics"],
        "field_disposition": "NOT_EVALUATED", "auto_acceptance": False,
    }
    return {"summary": summary, "rows": rows, "layers": layers,
            "baseline": baseline, "experimental": alternate, "lifecycle": phases}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--measurements", type=Path, required=True)
    parser.add_argument("--recipe", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository

    repo = Path(__file__).resolve().parents[2]
    paths = [args.input, args.measurements, args.recipe, Path(__file__),
             Path(__file__).with_name("s11_saved_detection_replay.py"),
             *sorted((repo / "src").rglob("*.py"))]
    pins = {str(p.resolve()): digest(p) for p in paths}
    saved = json.loads(args.input.read_text(encoding="utf-8"))
    detections = restore(saved)
    measurements = json.loads(args.measurements.read_text(encoding="utf-8"))
    bind_scores(detections, measurements)
    recipe = JsonRecipeRepository().load(args.recipe)
    glass = next((g for g in recipe.glasses if g.id == detections[0].glass_id), None)
    if glass is None:
        raise ValueError("Saved Glass is not bound to recipe")
    args.output.mkdir(parents=True, exist_ok=False)

    def save(name, data):
        with (args.output / name).open("x", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write("\n")

    save("freeze.json", {"spec": SPEC, "pins": pins})
    result = paired_replay(saved, measurements, glass)
    for name, data in result.items():
        save(name + ".json", data)
    assert all(digest(Path(p)) == pin for p, pin in pins.items()), "Input/source mutation"
    save("receipt.json", {"status": "COMPLETE", "spec": SPEC, "input_bytes_preserved": True,
                          "video_read": False, "files": {p.name: digest(p) for p in args.output.glob("*.json")}})
    print(json.dumps(result["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
