from __future__ import annotations

import argparse
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path

from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.adapters.storage.output_bundle_store import OutputBundleStore
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.application.services.report_presentation import build_report_presentation
from oil_tracker.domain.enums import EventType, InitialObservationState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.session import (
    AnalysisSession,
    DebugTraceLevel,
    InitialStateConfirmation,
)
from tests.diagnostics.s11_evidence_probe import file_sha256, repository_root


SAMPLING_FPS = 2.0
QUALIFICATION_WINDOWS: dict[str, tuple[float, float]] = {
    "base_sample_1": (0.0, 14.4),
    "sample2": (0.0, 2.0),
    "sample3": (30.03, 105.0),
    "sample4": (0.0, 56.0),
}
ACCEPTED_ROW_COUNTS = {
    "base_sample_1": 30,
    "sample2": 5,
    "sample3": 151,
    "sample4": 113,
}
ACCEPTED_NUMERIC_OIL_COUNTS = {
    "base_sample_1": 2,
    "sample2": 2,
    "sample3": 21,
    "sample4": 64,
}
ACCEPTED_TRACKING_FINGERPRINTS = {
    "base_sample_1": "c50e1e8bb7ff8bda873c1fbd4637586de4798fb950ea9fb17213ec8d3eb9716c",
    "sample2": "912225deb00b1a33504d7541be9a61727049a2a845c29ebd8b7badd7197f06aa",
    "sample3": "30effdc2b523af3d0ba051b3ed0e760d7f88eefb7a59885f1f66bb6887a106ac",
    "sample4": "d37bbd9101fa3f7d3f56524b588c1e22d76eb4849702d12fceeeec3ea2385c37",
}


def _session(
    sample: str,
    video_path: Path,
    output_root: Path,
    start_sec: float,
    end_sec: float,
    *,
    run_label: str,
    run_note: str,
) -> tuple[InspectionRecipe, AnalysisSession]:
    recipe = JsonRecipeRepository().load(video_path.with_suffix(".oilrecipe"))
    reader = OpenCvVideoReader(video_path)
    try:
        metadata = reader.metadata
    finally:
        reader.close()
    session = AnalysisSession(
        input_video_path=str(video_path),
        video_metadata=metadata,
        analysis_start_sec=start_sec,
        analysis_end_sec=min(end_sec, metadata.duration_sec),
        # The established qualification windows begin at the recorded compressor
        # start (sample3 at 30.03 s; the other three at 0.0 s).
        compressor_start_sec=start_sec,
        sampling_fps=SAMPLING_FPS,
        output_directory=str(output_root),
        run_name=f"{run_label} {sample}",
        run_note=run_note,
        resolution_confirmed=True,
        debug_trace_level=DebugTraceLevel.NONE,
    )
    for glass in recipe.glasses:
        if not glass.enabled:
            continue
        # The checked-in qualification Recipes retain AUTO for operator workflow.
        # This replay confirms UNKNOWN explicitly so no retrospective FULL/EMPTY
        # interpretation can create report observations.
        glass.initial_state = InitialObservationState.UNKNOWN_REVIEW
        session.initial_state_confirmations[glass.id] = InitialStateConfirmation(
            InitialObservationState.UNKNOWN_REVIEW,
            session.input_video_path,
            session.analysis_start_sec,
        )
    return recipe, session


def _tracking_fingerprint(result) -> str:
    rows = [
        {
            "glass_id": glass.glass_id,
            "frame_index": sample.frame_index,
            "timestamp_sec": sample.timestamp_sec,
            "fill_state": sample.fill_state.value,
            "raw_oil_y": sample.raw_oil_air_level_y,
            "raw_oil_px": sample.raw_oil_air_level_px_from_zero,
            "smoothed_oil_px": sample.smoothed_oil_air_level_px_from_zero,
            "raw_foam_y": sample.raw_foam_front_y,
            "smoothed_foam_px": sample.smoothed_foam_front_px_from_zero,
            "is_valid": sample.is_valid,
            "flags": list(sample.flags),
        }
        for glass in result.glass_results
        for sample in glass.samples
    ]
    encoded = json.dumps(
        rows,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _sample_summary(sample: str, result, recipe, bundle: Path) -> dict[str, object]:
    presentation = build_report_presentation(result, recipe)
    rows = [sample_row for glass in result.glass_results for sample_row in glass.samples]
    numeric = sum(
        sample_row.smoothed_oil_air_level_px_from_zero is not None
        or sample_row.raw_oil_air_level_px_from_zero is not None
        for sample_row in rows
    )
    capture_paths = sorted((bundle / "captures").glob("*.png"))
    graph_paths = sorted((bundle / "graphs").glob("*.png"))
    return {
        "sample": sample,
        "bundle": str(bundle),
        "tracking_row_count": len(rows),
        "numeric_oil_count": numeric,
        "numeric_oil_ratio": numeric / len(rows) if rows else 0.0,
        "tracking_fingerprint_sha256": _tracking_fingerprint(result),
        "capture_count": len(capture_paths),
        "capture_files": [path.name for path in capture_paths],
        "graph_count": len(graph_paths),
        "report_landmark_count": len(presentation.landmarks),
        "foam_episode_count": sum(
            glass.foam_episode_count for glass in presentation.glasses
        ),
        "glass_reports": [
            {
                "glass_id": glass.glass_id,
                "glass_name": glass.glass_name,
                "finite_oil_count": glass.finite_oil_count,
                "foam_episode_count": glass.foam_episode_count,
                "landmark_count": len(glass.landmarks),
                "landmarks": [
                    {
                        "event_type": landmark.event_type.value,
                        "timestamp_sec": landmark.timestamp_sec,
                    }
                    for landmark in glass.landmarks
                ],
                "unavailable_intervals": [
                    asdict(interval) for interval in glass.unavailable_intervals
                ],
            }
            for glass in presentation.glasses
        ],
        "maximum_event_count": sum(
            event.event_type is EventType.MAXIMUM_OIL_LEVEL
            for glass in result.glass_results
            for event in glass.events
        ),
        "minimum_event_count": sum(
            event.event_type is EventType.MINIMUM_OIL_LEVEL
            for glass in result.glass_results
            for event in glass.events
        ),
    }


def run_replay(
    root: Path | None = None,
    output_root: Path | None = None,
    *,
    verify_accepted_counts: bool = True,
    expected_numeric_oil_counts: dict[str, int] = ACCEPTED_NUMERIC_OIL_COUNTS,
    expected_tracking_fingerprints: dict[str, str] = ACCEPTED_TRACKING_FINGERPRINTS,
    run_label: str = "S11-R1",
    run_note: str = "User observation report qualification replay",
    manifest_schema: str = "s11-user-observation-report-replay-v1",
) -> dict[str, object]:
    root = repository_root() if root is None else Path(root)
    output_root = (
        root / "sample" / "output" / "s11-report-r1"
        if output_root is None
        else Path(output_root)
    )
    output_root.mkdir(parents=True, exist_ok=True)
    summaries = []
    for sample, (start_sec, end_sec) in QUALIFICATION_WINDOWS.items():
        print(f"[{sample}] replay {start_sec:.2f}-{end_sec:.2f}s", flush=True)
        video_path = root / "sample" / f"{sample}.mp4"
        recipe, session = _session(
            sample,
            video_path,
            output_root,
            start_sec,
            end_sec,
            run_label=run_label,
            run_note=run_note,
        )
        result = AnalysisPipeline(
            lambda path: OpenCvVideoReader(path),
            OpenCvPhaseDetector(),
            RecipeValidationService(),
        ).run(recipe, session)
        bundle = OutputBundleStore().write_bundle(
            result,
            recipe,
            session,
            output_root,
        )
        summary = _sample_summary(sample, result, recipe, bundle)
        if verify_accepted_counts:
            expected = (
                ACCEPTED_ROW_COUNTS[sample],
                expected_numeric_oil_counts[sample],
            )
            actual = (
                summary["tracking_row_count"],
                summary["numeric_oil_count"],
            )
            if actual != expected:
                raise AssertionError(
                    f"{sample} detector/tracking baseline changed: expected {expected}, got {actual}"
                )
            fingerprint = str(summary["tracking_fingerprint_sha256"])
            if fingerprint != expected_tracking_fingerprints[sample]:
                raise AssertionError(
                    f"{sample} tracking fingerprint changed: {fingerprint}"
                )
        print(
            f"[{sample}] rows={summary['tracking_row_count']} "
            f"numeric={summary['numeric_oil_count']} "
            f"landmarks={summary['report_landmark_count']} "
            f"captures={summary['capture_count']}",
            flush=True,
        )
        summaries.append(summary)

    inputs = {
        sample: {
            suffix: file_sha256(root / "sample" / f"{sample}.{suffix}")
            for suffix in ("mp4", "oilrecipe", "oiltruth")
        }
        for sample in QUALIFICATION_WINDOWS
    }
    manifest = {
        "schema": manifest_schema,
        "sampling_fps": SAMPLING_FPS,
        "qualification_windows": QUALIFICATION_WINDOWS,
        "accepted_count_check_enabled": verify_accepted_counts,
        "inputs": inputs,
        "samples": summaries,
        "total_tracking_rows": sum(
            int(summary["tracking_row_count"]) for summary in summaries
        ),
        "total_numeric_oil": sum(
            int(summary["numeric_oil_count"]) for summary in summaries
        ),
        "total_captures": sum(int(summary["capture_count"]) for summary in summaries),
        "total_landmarks": sum(
            int(summary["report_landmark_count"]) for summary in summaries
        ),
    }
    manifest_path = output_root / "replay_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replay the four S11 qualification windows and render user reports."
    )
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--skip-accepted-count-check", action="store_true")
    args = parser.parse_args()
    manifest = run_replay(
        output_root=args.output_root,
        verify_accepted_counts=not args.skip_accepted_count_check,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
