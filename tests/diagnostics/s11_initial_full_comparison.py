"""Frozen local inputs for initial-FULL and individual candidate comparisons.

Use a managed experiment's work directory. Original Recipes are never changed.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import time

import cv2
import numpy as np

from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.adapters.vision.geometry_masks import build_mask_bundle
from oil_tracker.domain.geometry import EllipseGeometry

ROOT = Path(__file__).resolve().parents[2]
SOURCE_VIEWS = ROOT / "sample/output/s11-truth-audit-20261010-002/sample4"
ROI_FRAMES = (0, 450, 900, 1470, 1680)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=False)
    repository = JsonRecipeRepository()
    records = {}
    for sample in ("base_sample_1", "sample4"):
        original = ROOT / "sample" / f"{sample}.oilrecipe"
        recipe = repository.load(original)
        if sample == "sample4":
            recipe.glasses[0].geometry.ellipse = EllipseGeometry(595, 842, 37, 34)
        target = output / f"{sample}.oilrecipe"
        repository.save(target, recipe)
        records[sample] = {
            "original_recipe_sha256": _sha(original),
            "comparison_recipe_sha256": _sha(target),
            "geometry": recipe.to_dict()["glasses"][0]["geometry"],
        }

    original = repository.load(ROOT / "sample/sample4.oilrecipe").glasses[0]
    interior = repository.load(output / "sample4.oilrecipe").glasses[0]
    panels = []
    source_hashes = {}
    for frame in ROI_FRAMES:
        path = SOURCE_VIEWS / f"f{frame:06d}.png"
        source_hashes[str(path.relative_to(ROOT))] = _sha(path)
        image = cv2.imread(str(path))
        if image is None:
            raise ValueError(f"Missing source view: {path}")
        canvas = image[785:910, 530:660].copy()
        for glass, color in ((original, (0, 165, 255)), (interior, (0, 255, 0))):
            mask = build_mask_bundle(image, glass)
            contours, _ = cv2.findContours(mask.effective_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            offset = np.array([mask.crop_origin[0] - 530, mask.crop_origin[1] - 785])
            cv2.drawContours(canvas, [c + offset for c in contours], -1, color, 1)
        panel = cv2.resize(canvas, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST)
        panel = cv2.copyMakeBorder(panel, 32, 0, 0, 0, cv2.BORDER_CONSTANT, value=(24, 24, 24))
        cv2.putText(panel, f"sample4 f{frame} | green: interior", (8, 22), cv2.FONT_HERSHEY_SIMPLEX, .52, (255, 255, 255), 1)
        panels.append(panel)
    if not cv2.imwrite(str(output / "roi-review.png"), np.concatenate(panels, axis=1)):
        raise OSError("Cannot save ROI review")
    manifest = {
        "status": "ROI_PREPARED_BEFORE_DETECTOR_COMPARISON",
        "source_views": source_hashes,
        "recipes": records,
        "selection_basis": "Vessel interior in retained source views; no detector output optimization or physical target relabeling",
        "windows_roi": "OPERATOR_CHECK_REQUIRED_ON_WINDOWS",
    }
    (output / "roi-inputs.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def compare(
    output: Path, roi_inputs: Path, sample: str, *, debug_full: bool = False,
    cost_first_comparison: bool = False,
    candidate_rgb_comparison: bool = False,
    top_exit_comparison: bool = False,
) -> None:
    from oil_tracker.adapters.storage.jsonl_debug_trace_writer import JsonlDebugTraceWriterFactory
    from oil_tracker.adapters.storage.output_bundle_store import OutputBundleStore
    from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
    from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline
    from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
    from oil_tracker.application.services.report_presentation import build_report_presentation
    from oil_tracker.domain.enums import BoundaryKind, InitialObservationState
    from oil_tracker.domain.session import DebugTraceLevel, InitialStateConfirmation
    from tests.diagnostics.s11_local_xy_replay import Recorder, stable
    from tests.diagnostics.s11_report_observability_replay import _session, QUALIFICATION_WINDOWS
    from tests.diagnostics.s11_replay_provenance import capture_runtime_provenance
    import csv

    if sum((cost_first_comparison, candidate_rgb_comparison, top_exit_comparison)) > 1:
        raise ValueError("Compare one mechanism at a time.")
    output.mkdir(parents=True, exist_ok=False)
    video = ROOT / "sample" / f"{sample}.mp4"
    recipe_path = (roi_inputs / "sample4.oilrecipe" if sample == "sample4"
                   else ROOT / "sample/base_sample_1.oilrecipe")
    frozen = json.loads((roi_inputs / "roi-inputs.json").read_text(encoding="utf-8"))
    hash_key = "comparison_recipe_sha256" if sample == "sample4" else "original_recipe_sha256"
    assert _sha(recipe_path) == frozen["recipes"][sample][hash_key]
    variants = {}
    raw_inputs = []
    for enabled in (False, True):
        mode = (("top_exit" if enabled else "observation") if top_exit_comparison
                else ("candidate_rgb" if enabled else "observation") if candidate_rgb_comparison
                else ("cost_first" if enabled else "observation") if cost_first_comparison
                else ("observation" if enabled else "baseline"))
        with TemporaryDirectory(prefix=f"{sample}-{mode}-", dir=output) as scratch:
            scratch_path = Path(scratch)
            _, session = _session(sample, video, scratch_path, *QUALIFICATION_WINDOWS[sample],
                                  run_label="Initial FULL comparison", run_note=mode)
            if debug_full:
                session.debug_trace_level = DebugTraceLevel.FULL
            recipe = JsonRecipeRepository().load(recipe_path)
            for glass in recipe.glasses:
                glass.initial_state = InitialObservationState.FULL_NO_INTERFACE
                session.initial_state_confirmations[glass.id] = InitialStateConfirmation(
                    InitialObservationState.FULL_NO_INTERFACE, str(video), session.analysis_start_sec,
                )
            detector = Recorder(
                initial_full_observation=cost_first_comparison or candidate_rgb_comparison or top_exit_comparison or enabled,
                cost_first_assignment=cost_first_comparison and enabled,
                candidate_rgb=candidate_rgb_comparison and enabled,
                top_exit_full=top_exit_comparison and enabled,
            )
            started = time.monotonic()
            result = AnalysisPipeline(
                OpenCvVideoReader, detector, RecipeValidationService(),
                JsonlDebugTraceWriterFactory(scratch_path) if debug_full else None,
            ).run(recipe, session)
            analysis_seconds = time.monotonic() - started
            assert not result.errors, result.errors
            raw_inputs.append(detector.raw)
            rows = stable([asdict(s) for g in result.glass_results for s in g.samples])
            assert len(rows) == len(detector.raw) == len(detector.completed)
            bundle = OutputBundleStore().write_bundle(result, recipe, session, scratch_path)
            with (bundle / "tracking_data.csv").open(encoding="utf-8-sig", newline="") as stream:
                csv_rows = list(csv.DictReader(stream))
            for sample_row, detection, csv_row in zip(rows, detector.completed, csv_rows, strict=True):
                assert ("+cost-first-assignment-v1" in detection["debug_metrics"]["sequence_resolver_version"]) == (cost_first_comparison and enabled)
                assert ("+candidate-rgb-v1" in detection["debug_metrics"]["sequence_resolver_version"]) == (candidate_rgb_comparison and enabled)
                assert ("+top-exit-full-v1" in detection["debug_metrics"]["sequence_resolver_version"]) == (top_exit_comparison and enabled)
                y = sample_row["raw_oil_air_level_y"]
                assert y == detection["raw_oil_air_level_y"]
                assert (None if not csv_row["raw_oil_air_level_y"] else float(csv_row["raw_oil_air_level_y"])) == y
                if y is not None:
                    selected = [c for c in detection["candidates"] if c["kind"] == BoundaryKind.OIL_AIR and c["selected"]]
                    assert len(selected) == 1 and selected[0]["y"] == y
                    if candidate_rgb_comparison and enabled:
                        assert selected[0]["features"]["oil_candidate_rgb_decision"] == "OIL_CANDIDATE_COMPATIBLE"
            report = build_report_presentation(result, recipe).glasses[0]
            if any("OIL_DIRECTION_UNCONFIRMED" in row["flags"] for row in rows):
                assert "이동 방향이 미확정" in report.observation_note
                assert "이동 방향이 미확정" in (bundle / "report.html").read_text(encoding="utf-8")
            variants[mode] = {
                "detector_version": detector.version,
                "analysis_seconds": analysis_seconds,
                "raw_input_sha256": hashlib.sha256(json.dumps(detector.raw, sort_keys=True, allow_nan=False).encode()).hexdigest(),
                "rows": rows,
                "phase": [{"frame_index": d["frame_index"], "phase": d["debug_metrics"]["sequence_material_phase"],
                           "reason": d["debug_metrics"]["sequence_material_phase_reason"],
                           "observation": d["debug_metrics"]["sequence_material_phase_diagnostics"].get("initial_full_observation"),
                           **({"top_exit": d["debug_metrics"]["sequence_material_phase_diagnostics"].get("top_exit_full")} if top_exit_comparison else {})}
                          for d in detector.completed],
                "events": stable([asdict(e) for g in result.glass_results for e in g.events]),
                "report": asdict(report),
                "csv_and_selected_candidate_equality": "PASS",
            }
            if candidate_rgb_comparison and enabled:
                variants[mode]["rgb_annotations"] = [
                    {"frame_index": d["frame_index"], **d["debug_metrics"]["oil_candidate_rgb"]}
                    for d in detector.raw
                ]
            print(json.dumps({"sample": sample, "mode": mode, "rows": len(rows),
                              "numeric_oil": sum(row["raw_oil_air_level_y"] is not None for row in rows),
                              "numeric_foam": sum(row["raw_foam_front_y"] is not None for row in rows)}, ensure_ascii=False), flush=True)
    compared_raw = deepcopy(raw_inputs[1])
    if candidate_rgb_comparison:
        for detection in compared_raw:
            detection["debug_metrics"].pop("oil_candidate_rgb")
            for candidate in detection["candidates"]:
                candidate["features"] = {k: v for k, v in candidate["features"].items()
                                         if not k.startswith("oil_candidate_rgb_")}
    assert raw_inputs[0] == compared_raw, "Comparison changed unannotated current-frame detector inputs"
    result = {"sample": sample, "comparison": ("top_exit" if top_exit_comparison
                                               else "candidate_rgb" if candidate_rgb_comparison
                                               else "cost_first" if cost_first_comparison else "initial_full"),
              "initial_state": "FULL mechanism stress condition; not physical truth",
              "debug_trace_level": "FULL" if debug_full else "NONE",
              "recipe_sha256": _sha(recipe_path), "runtime": capture_runtime_provenance(video),
              "raw_inputs_equal": raw_inputs[0] == raw_inputs[1],
              "raw_inputs_equal_without_rgb_annotations": True, "variants": variants}
    (output / "comparison.json").write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False, default=str) + "\n", encoding="utf-8")


def verify_candidate_rgb(output: Path) -> None:
    """Reproduce the frozen candidate readout without fitting or a Torch runtime."""
    from oil_tracker.adapters.vision.oil_candidate_rgb import OilCandidateRgb, COMPATIBLE, WEIGHTS_SHA256
    from oil_tracker.domain.detection import BoundaryCandidate
    from oil_tracker.domain.enums import BoundaryKind
    from tests.diagnostics import s11_candidate_rgb_trial as frozen

    source = ROOT / "docs/50-diagnostics/s11/2026-10-14-candidate-rgb-trial"
    prepared = json.loads((source / "prepared.json").read_text(encoding="utf-8"))
    old = json.loads((source / "readout.json").read_text(encoding="utf-8"))
    assert old["weights_sha256"] == WEIGHTS_SHA256 == _sha(source / "final-weights.npz")
    expected = {row["id"]: row for row in old["rows"]}
    model, rows = OilCandidateRgb(), []
    for frame_id, frame in prepared["frames"].items():
        rgb, visible = frozen.load_frame(ROOT, frame)
        units = [u for u in prepared["units"] if u["frame_id"] == frame_id and u["is_oil_candidate"]]
        for center_x in sorted({u["query"]["source_xy"][0] for u in units}):
            group = [u for u in units if u["query"]["source_xy"][0] == center_x]
            candidates = [BoundaryCandidate(u["query"]["source"], BoundaryKind.OIL_AIR, u["query"]["source_xy"][1]) for u in group]
            annotated, _ = model.annotate(
                candidates, crop_bgr=rgb[:, :, ::-1], effective_mask=visible,
                glare_mask=np.zeros_like(visible), crop_origin=tuple(frame["origin"]), source_center_x=center_x,
            )
            for unit, candidate in zip(group, annotated, strict=True):
                prior = expected[unit["id"]]
                features = candidate.features
                decision = features["oil_candidate_rgb_decision"]
                assert decision == prior["decision"], unit["id"]
                error = None
                variants = features["oil_candidate_rgb_variants"]
                for actual, stored in zip(variants, unit["variants"], strict=True):
                    assert actual["source_y"] == stored["source_xy"][1]
                    assert actual["status"] == stored["status"], unit["id"]
                    for side in ("upper", "lower"):
                        if side in stored["sides"]:
                            assert actual[f"{side}_patch_count"] == stored["sides"][side]["patches"]
                            assert actual[f"{side}_input_sha256"] == stored["sides"][side]["uint8_sha256"]
                if decision != "UNAVAILABLE":
                    logits = np.asarray([v["logits"] for v in variants])
                    error = float(np.max(np.abs(logits - np.asarray(prior["logits"]))))
                    assert error <= 1e-4, (unit["id"], error)
                rows.append({"id": unit["id"], "decision": decision, "maximum_logit_error": error})
    assert len(rows) == 182 and sum(r["decision"] != "UNAVAILABLE" for r in rows) == 165
    assert all(next(r for r in rows if r["id"] == f"s4-f1140-idx{i}")["decision"] == COMPATIBLE for i in (7, 10, 22))
    result = {"model_sha256": WEIGHTS_SHA256, "oil_candidates": len(rows),
              "available": 165, "unavailable": 17, "all_decisions_and_inputs_equal": True,
              "known_rim_false_accepts_preserved": 3,
              "maximum_logit_error": max(r["maximum_logit_error"] or 0 for r in rows), "rows": rows}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({k: v for k, v in result.items() if k != "rows"}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--prepare-roi", type=Path)
    modes.add_argument("--compare", type=Path)
    modes.add_argument("--verify-rgb", type=Path)
    parser.add_argument("--roi-inputs", type=Path)
    parser.add_argument("--sample", choices=("base_sample_1", "sample4"))
    parser.add_argument("--debug-full", action="store_true")
    candidates = parser.add_mutually_exclusive_group()
    candidates.add_argument("--cost-first-comparison", action="store_true",
                        help="Compare FULL+observation v2 with/without cost-first assignment")
    candidates.add_argument("--candidate-rgb-comparison", action="store_true",
                            help="Compare FULL+observation v2 with/without frozen candidate RGB eligibility")
    candidates.add_argument("--top-exit-comparison", action="store_true",
                            help="Compare FULL+observation v2 with/without top-exit FULL closure")
    args = parser.parse_args()
    if args.prepare_roi:
        prepare(args.prepare_roi)
    elif args.verify_rgb:
        verify_candidate_rgb(args.verify_rgb)
    else:
        if args.roi_inputs is None or args.sample is None:
            parser.error("--compare requires --roi-inputs and --sample")
        compare(args.compare, args.roi_inputs, args.sample, debug_full=args.debug_full,
                cost_first_comparison=args.cost_first_comparison,
                candidate_rgb_comparison=args.candidate_rgb_comparison,
                top_exit_comparison=args.top_exit_comparison)
