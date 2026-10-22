"""Frozen local inputs for initial-FULL and individual candidate comparisons.

Use a managed experiment's work directory. Original Recipes are never changed.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import time
from uuid import NAMESPACE_URL, uuid5

import cv2
import numpy as np

from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.adapters.vision.geometry_masks import build_mask_bundle
from oil_tracker.domain.geometry import EllipseGeometry, GlassGeometry
from oil_tracker.domain.recipe import GlassInspectionConfig, InspectionRecipe

ROOT = Path(__file__).resolve().parents[2]
SOURCE_VIEWS = ROOT / "sample/output/s11-truth-audit-20261010-002/sample4"
ROI_FRAMES = (0, 450, 900, 1470, 1680)
INTAKE_VIEWS = ROOT / "sample/output/s11-public-video-intake-20261009-001"
EMPTY_FILL_FROZEN_AT = "2026-10-22T00:00:00+00:00"
# Never-full negatives for the top-exit promotion criteria. Each ellipse is the
# vessel interior, from the inner rim to the top of the solid base, measured on
# the empty first frame before any detector run; it is not fitted to the level.
EMPTY_FILL_CONTROLS = {
    # The nominal 54.855 s end lies past the last decodable frame (about
    # 54.82 s), where seeking near EOF fails, so the window ends at 54.8 s.
    "sample5": {"label": "water", "views": "public_water_fill_pexels_6381722",
                "frames": (0, 822, 1643), "ellipse": (960.5, 593.0, 142.5, 257.0),
                "window": (0.0, 54.8)},
    "sample7": {"label": "milk", "views": "public_milk_fill_pexels_11158788",
                "frames": (0, 532, 1063), "ellipse": (1130.0, 600.0, 287.0, 303.0),
                "window": (0.0, 44.378)},
}


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


def prepare_empty_fill(output: Path) -> None:
    """Freeze the never-full Recipes and a review sheet before any detector run."""
    from oil_tracker.adapters.vision.oil_observation_resolver import OilObservationResolverConfig

    output.mkdir(parents=True, exist_ok=False)
    band = OilObservationResolverConfig().entrance_band_ratio
    repository = JsonRecipeRepository()
    records, source_hashes, sheets = {}, {}, []
    for sample, control in EMPTY_FILL_CONTROLS.items():
        views = INTAKE_VIEWS / control["views"]
        first = cv2.imread(str(views / "f000000.png"))
        if first is None:
            raise ValueError(f"Missing empty frame for {sample}")
        height, width = first.shape[:2]
        cx, cy, rx, ry = control["ellipse"]
        note = (f"Never-full negative for the top-exit promotion criteria ({control['label']} fill). "
                "Ellipse: vessel interior from the inner rim to the top of the solid base, "
                "measured on the empty first frame before any detector run; not canonical truth.")
        glass = GlassInspectionConfig(
            id=str(uuid5(NAMESPACE_URL, f"oil-level-tracker/s11-empty-fill/{sample}/glass")),
            name=f"{sample} glass",
            geometry=GlassGeometry(ellipse=EllipseGeometry(cx, cy, rx, ry), zero_line_y=cy, margin_ratio=0.08),
            description=note,
        )
        recipe = InspectionRecipe(
            name=f"S11 empty-fill negative {sample}", reference_frame_width=width,
            reference_frame_height=height, glasses=[glass], description=note,
            recipe_id=str(uuid5(NAMESPACE_URL, f"oil-level-tracker/s11-empty-fill/{sample}")),
            created_at=EMPTY_FILL_FROZEN_AT, updated_at=EMPTY_FILL_FROZEN_AT,
        )
        target = output / f"{sample}.oilrecipe"
        repository.save(target, recipe)
        records[sample] = {
            "comparison_recipe_sha256": _sha(target),
            "geometry": recipe.to_dict()["glasses"][0]["geometry"],
            "band_end_y": _band_end(glass, band),
        }
        panels = []
        for frame in control["frames"]:
            path = views / f"f{frame:06d}.png"
            source_hashes[str(path.relative_to(ROOT))] = _sha(path)
            image = cv2.imread(str(path))
            if image is None:
                raise ValueError(f"Missing source view: {path}")
            panels.append(_roi_panel(image, glass, band, f"{sample} f{frame}"))
        sheets.append(np.concatenate(panels, axis=1))
    _write_sheet(output / "roi-review.png", sheets)
    manifest = {
        "status": "ROI_PREPARED_BEFORE_DETECTOR_COMPARISON",
        "source_views": source_hashes,
        "recipes": records,
        "selection_basis": ("Vessel interior from the inner rim to the top of the solid base, measured on the "
                            "empty first frame; no detector output and not fitted to the settled level"),
        "review_legend": {"green": "Recipe ellipse", "yellow": "effective mask (margin 0.08)",
                          "red": f"end of the top {band:.0%} band"},
        "truth": "USER_CONFIRMATION_REQUIRED: each glass starts EMPTY and never becomes full",
    }
    (output / "roi-inputs.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def roi_overlay(video: Path, recipe_path: Path, times: list[float], output: Path, *, grid: bool = False) -> None:
    """Show a Recipe's ellipses and top-band ends on source frames before any detector run.

    With ``grid`` the panels keep source scale and carry a source-Y grid, five
    frames per row, for reading a visible surface position off the frame.
    """
    from oil_tracker.adapters.vision.oil_observation_resolver import OilObservationResolverConfig
    from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader

    output.mkdir(parents=True, exist_ok=False)
    band = OilObservationResolverConfig().entrance_band_ratio
    recipe = JsonRecipeRepository().load(recipe_path)
    glasses = [glass for glass in recipe.glasses if glass.enabled]
    panels: dict[str, list[np.ndarray]] = {glass.id: [] for glass in glasses}
    frames = []
    with OpenCvVideoReader(video) as reader:
        metadata = reader.metadata
        for requested in times:
            image, index, actual = reader.read_at(requested)
            frames.append({"requested_sec": requested, "frame_index": index, "timestamp_sec": actual})
            for glass in glasses:
                panels[glass.id].append(_roi_panel(image, glass, band, f"{glass.name} f{index} {actual:.2f}s", grid=grid))
    per_row = 5 if grid else len(times)
    _write_sheet(output / "roi-overlay.png", [
        np.concatenate(panels[glass.id][start:start + per_row], axis=1)
        for glass in glasses for start in range(0, len(times), per_row)
    ])
    manifest = {
        "status": "ROI_OVERLAY_WITH_Y_GRID" if grid else "ROI_OVERLAY_BEFORE_DETECTOR_RUN",
        **({"grid": {"minor_px": _GRID_MINOR_PX, "labelled_px": _GRID_LABEL_PX, "scale": 1.0}} if grid else {}),
        "video": {"path": str(video), "sha256": _sha(video), "size_bytes": video.stat().st_size,
                  "fps": metadata.fps, "frame_count": metadata.frame_count,
                  "duration_sec": metadata.duration_sec, "width": metadata.width, "height": metadata.height},
        "recipe": {"path": str(recipe_path), "sha256": _sha(recipe_path), "name": recipe.name},
        "frames": frames,
        "glasses": [
            {"id": glass.id, "name": glass.name, "ellipse": asdict(glass.geometry.ellipse),
             "margin_ratio": glass.geometry.margin_ratio, "exclusions": len(glass.geometry.exclusions),
             "artifact_templates": len(glass.geometry.artifact_templates),
             "band_end_y": _band_end(glass, band)}
            for glass in glasses
        ],
        "legend": {"green": "Recipe ellipse", "yellow": "effective mask",
                   "red": f"end of the top {band:.0%} band"},
        "check": "USER_CONFIRMATION_REQUIRED: each ellipse is the vessel interior (OTR-1 D1)",
    }
    (output / "roi-overlay.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False), flush=True)


def _band_end(glass: GlassInspectionConfig, band: float) -> float:
    ellipse = glass.geometry.ellipse
    return ellipse.center_y - ellipse.radius_y + band * 2.0 * ellipse.radius_y


_GRID_MINOR_PX = 20
_GRID_LABEL_PX = 40


def _roi_panel(image: np.ndarray, glass: GlassInspectionConfig, band: float, title: str, *,
               grid: bool = False) -> np.ndarray:
    """Ellipse (green), effective mask (yellow) and top-band end (red), cropped around the Glass."""
    ellipse = glass.geometry.ellipse
    cx, cy, rx, ry = ellipse.center_x, ellipse.center_y, ellipse.radius_x, ellipse.radius_y
    band_end = _band_end(glass, band)
    left, right = int(cx - rx) - 40, int(cx + rx) + 40
    top, bottom = max(int(cy - ry) - 30, 0), min(int(cy + ry) + 30, image.shape[0])
    canvas = image.copy()
    if grid:
        # Source-Y rows under the overlays: thin every 20 px, labelled every 40 px.
        for y in range(top - top % _GRID_MINOR_PX + _GRID_MINOR_PX, bottom, _GRID_MINOR_PX):
            labelled = y % _GRID_LABEL_PX == 0
            cv2.line(canvas, (max(left, 0), y), (right, y), (255, 0, 255) if labelled else (160, 60, 160), 1)
            if labelled:
                cv2.putText(canvas, str(y), (max(left, 0) + 2, y - 3), cv2.FONT_HERSHEY_SIMPLEX, .45,
                            (255, 255, 255), 1)
    cv2.ellipse(canvas, (round(cx), round(cy)), (round(rx), round(ry)), 0, 0, 360, (0, 255, 0), 2)
    mask = build_mask_bundle(image, glass)
    contours, _ = cv2.findContours(mask.effective_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(canvas, [c + np.array(mask.crop_origin) for c in contours], -1, (0, 215, 255), 1)
    cv2.line(canvas, (left, round(band_end)), (right, round(band_end)), (0, 0, 255), 1)
    crop = canvas[top:bottom, max(left, 0):right]
    scale = 1.0 if grid else 520 / crop.shape[0]
    panel = cv2.resize(crop, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    panel = cv2.copyMakeBorder(panel, 30, 0, 0, 4, cv2.BORDER_CONSTANT, value=(24, 24, 24))
    cv2.putText(panel, title, (6, 21), cv2.FONT_HERSHEY_SIMPLEX, .6, (255, 255, 255), 1)
    return panel


def _write_sheet(path: Path, sheets: list[np.ndarray]) -> None:
    width = max(sheet.shape[1] for sheet in sheets)
    padded = [cv2.copyMakeBorder(sheet, 0, 4, 0, width - sheet.shape[1], cv2.BORDER_CONSTANT, value=(24, 24, 24))
              for sheet in sheets]
    if not cv2.imwrite(str(path), np.concatenate(padded, axis=0)):
        raise OSError(f"Cannot save {path.name}")


# Per-candidate tracklet fields the resolver already writes; the readout copies them only.
OWNER_READOUT_FEATURES = (
    "sequence_tracklet_id", "sequence_tracklet_lifecycle", "sequence_tracklet_admitted",
    "sequence_tracklet_direction", "sequence_tracklet_net_progress_px", "sequence_tracklet_failure_reason",
    "sequence_tracklet_confirmation_observation_count", "sequence_identity_contradiction",
    "sequence_authority_reason",
)


def _owner_readout(detection: dict) -> dict:
    """One frame's fill owners and Oil candidates, read from a completed detection."""
    metrics = detection["debug_metrics"]
    lifecycle = metrics.get("sequence_material_phase_diagnostics") or {}
    return {
        "frame_index": detection["frame_index"],
        "phase": metrics.get("sequence_material_phase"),
        "reason": metrics.get("sequence_material_phase_reason"),
        "owner_chain": metrics.get("sequence_material_phase_owner_chain"),
        **{key: lifecycle.get(key) for key in (
            "allowed_mode", "allowed_tracklet_ids", "dynamic_fill_owner_ids",
            "established_fill_owner", "established_fill_last_y",
        )},
        "published_oil_y": detection["raw_oil_air_level_y"],
        "oil_candidates": [
            {"y": candidate["y"], "selected": candidate["selected"],
             **{key: candidate["features"].get(key) for key in OWNER_READOUT_FEATURES}}
            for candidate in detection["candidates"] if candidate["kind"] == "oil_air"
        ],
    }


def compare(
    output: Path, roi_inputs: Path, sample: str, *, debug_full: bool = False,
    cost_first_comparison: bool = False,
    candidate_rgb_comparison: bool = False,
    top_exit_comparison: bool = False,
    original_recipe: bool = False,
    initial_state: str = "full",
    owner_readout: bool = False,
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
    if initial_state not in {"full", "unknown", "empty"}:
        raise ValueError("Initial state must be full, unknown or empty.")
    output.mkdir(parents=True, exist_ok=False)
    video = ROOT / "sample" / f"{sample}.mp4"
    original = ROOT / "sample" / f"{sample}.oilrecipe"
    empty_fill = sample in EMPTY_FILL_CONTROLS
    recipe_path = (roi_inputs / f"{sample}.oilrecipe" if empty_fill
                   else roi_inputs / "sample4.oilrecipe" if sample == "sample4" and not original_recipe
                   else original)
    window = EMPTY_FILL_CONTROLS[sample]["window"] if empty_fill else QUALIFICATION_WINDOWS[sample]
    frozen = json.loads((roi_inputs / "roi-inputs.json").read_text(encoding="utf-8"))
    if sample in frozen["recipes"]:
        hash_key = "original_recipe_sha256" if recipe_path == original else "comparison_recipe_sha256"
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
            _, session = _session(sample, video, scratch_path, *window,
                                  run_label="Initial FULL comparison", run_note=mode,
                                  recipe_path=recipe_path)
            if debug_full:
                session.debug_trace_level = DebugTraceLevel.FULL
            recipe = JsonRecipeRepository().load(recipe_path)
            initial = {"full": InitialObservationState.FULL_NO_INTERFACE,
                       "empty": InitialObservationState.EMPTY_NO_INTERFACE,
                       "unknown": InitialObservationState.UNKNOWN_REVIEW}[initial_state]
            for glass in recipe.glasses:
                glass.initial_state = initial
                session.initial_state_confirmations[glass.id] = InitialStateConfirmation(
                    initial, str(video), session.analysis_start_sec,
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
                assert ("+top-exit-full-v3" in detection["debug_metrics"]["sequence_resolver_version"]) == (top_exit_comparison and enabled)
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
                "retrospective": stable([asdict(g.retrospective) if g.retrospective else None
                                         for g in result.glass_results]),
                "report": asdict(report),
                "csv_and_selected_candidate_equality": "PASS",
            }
            if owner_readout:
                variants[mode]["owner_readout"] = [_owner_readout(d) for d in detector.completed]
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
              "initial_state": {"full": "FULL mechanism stress condition; not physical truth",
                                "empty": "EMPTY at the start; never-full negative (truth confirmed in the run plan)",
                                "unknown": "UNKNOWN qualification state"}[initial_state],
              "recipe": str(recipe_path.relative_to(ROOT)) if recipe_path.is_relative_to(ROOT) else str(recipe_path),
              "debug_trace_level": "FULL" if debug_full else "NONE",
              "recipe_sha256": _sha(recipe_path), "runtime": capture_runtime_provenance(video),
              "raw_inputs_equal": raw_inputs[0] == raw_inputs[1],
              "raw_inputs_equal_without_rgb_annotations": True, "variants": variants}
    (output / "comparison.json").write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False, default=str) + "\n", encoding="utf-8")


def summarize_top_exit(work: Path) -> None:
    """Score every top-exit control under ``work`` against N1/N2 of the promotion criteria."""
    from tests.diagnostics.s11_local_xy_replay import stable

    full_states = {"FULL_NO_INTERFACE", "FULL_WITH_FOAM"}
    controls = {}
    for path in sorted(work.glob("*/comparison.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data["comparison"] != "top_exit":
            raise ValueError(f"Not a top-exit comparison: {path}")
        off, on = data["variants"]["observation"], data["variants"]["top_exit"]
        top_exit = [p.get("top_exit") or {} for p in on["phase"]]
        record = {
            "sample": data["sample"], "recipe": data["recipe"], "recipe_sha256": data["recipe_sha256"],
            "initial_state": data["initial_state"], "rows": len(on["rows"]),
            "numeric_oil": sum(r["raw_oil_air_level_y"] is not None for r in on["rows"]),
            "numeric_foam": sum(r["raw_foam_front_y"] is not None for r in on["rows"]),
            "full_rows_off": sum(r["fill_state"] in full_states for r in off["rows"]),
            "full_rows_on": sum(r["fill_state"] in full_states for r in on["rows"]),
            "top_exit_full_rows": sum("OIL_TOP_EXIT_FULL" in r["flags"] for r in on["rows"]),
            "raw_inputs_equal": data["raw_inputs_equal"],
            "rows_equal": off["rows"] == on["rows"],
            "events_equal": off["events"] == on["events"],
            "report_equal_without_run_id": stable(off["report"]) == stable(on["report"]),
            "versions": [off["detector_version"], on["detector_version"]],
            "top_exit_reasons": dict(Counter(t.get("reason") for t in top_exit)),
            "confirmation_states": dict(Counter(t["confirmation"] for t in top_exit if t.get("confirmation"))),
            "phase_reasons_on": dict(Counter(p["reason"] for p in on["phase"])),
            "retrospective_on": [
                None if r is None else {k: r.get(k) for k in ("status", "barriers", "start_time_sec",
                                                             "end_time_sec", "provenance", "reason")}
                for r in on.get("retrospective", [])
            ],
        }
        record["pass"] = (record["top_exit_full_rows"] == 0 and record["raw_inputs_equal"]
                          and record["rows_equal"] and record["events_equal"]
                          and record["report_equal_without_run_id"])
        controls[path.parent.name] = record
    if not controls:
        raise ValueError(f"No comparison.json under {work}")
    failed = sorted(name for name, record in controls.items() if not record["pass"])
    summary = {
        "criteria": "N1 zero top-exit FULL rows; N2 raw inputs, rows, events and report equal between arms",
        "verdict": (f"PASS: all {len(controls)} controls" if not failed else f"FAIL: {', '.join(failed)}"),
        "controls": controls,
    }
    (work / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
                                       encoding="utf-8")
    print(summary["verdict"])


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
    modes.add_argument("--prepare-empty-fill", type=Path,
                       help="Freeze the sample5/sample7 never-full Recipes and their review sheet")
    modes.add_argument("--roi-overlay", type=Path,
                       help="Write roi-overlay.png/json for --video and --recipe at --times, before any run")
    modes.add_argument("--compare", type=Path)
    modes.add_argument("--summarize-top-exit", type=Path,
                       help="Write summary.json for every */comparison.json top-exit control in this directory")
    modes.add_argument("--verify-rgb", type=Path)
    parser.add_argument("--roi-inputs", type=Path)
    parser.add_argument("--video", type=Path)
    parser.add_argument("--recipe", type=Path)
    parser.add_argument("--times", default="0,40", help="Comma-separated seconds for --roi-overlay")
    parser.add_argument("--sample", choices=("base_sample_1", "sample2", "sample4", *EMPTY_FILL_CONTROLS))
    parser.add_argument("--original-recipe", action="store_true",
                        help="Use sample/<sample>.oilrecipe instead of the frozen sample4 interior Recipe")
    parser.add_argument("--initial-state", choices=("full", "unknown", "empty"), default="full")
    parser.add_argument("--debug-full", action="store_true")
    parser.add_argument("--owner-readout", action="store_true",
                        help="With --compare, also record each frame's fill owners and Oil candidate tracklet fields")
    parser.add_argument("--grid", action="store_true", help="With --roi-overlay, source-scale panels with a Y grid")
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
    elif args.prepare_empty_fill:
        prepare_empty_fill(args.prepare_empty_fill)
    elif args.roi_overlay:
        if args.video is None or args.recipe is None:
            parser.error("--roi-overlay requires --video and --recipe")
        roi_overlay(args.video, args.recipe, [float(value) for value in args.times.split(",")], args.roi_overlay,
                    grid=args.grid)
    elif args.summarize_top_exit:
        summarize_top_exit(args.summarize_top_exit)
    elif args.verify_rgb:
        verify_candidate_rgb(args.verify_rgb)
    else:
        if args.roi_inputs is None or args.sample is None:
            parser.error("--compare requires --roi-inputs and --sample")
        compare(args.compare, args.roi_inputs, args.sample, debug_full=args.debug_full,
                cost_first_comparison=args.cost_first_comparison,
                candidate_rgb_comparison=args.candidate_rgb_comparison,
                top_exit_comparison=args.top_exit_comparison,
                original_recipe=args.original_recipe, initial_state=args.initial_state,
                owner_readout=args.owner_readout)
