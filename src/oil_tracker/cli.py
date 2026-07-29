from __future__ import annotations

import argparse
from pathlib import Path
import sys

from oil_tracker.adapters.storage.benchmark_result_writer import AtomicBenchmarkResultWriter
from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.adapters.storage.output_bundle_store import OutputBundleStore
from oil_tracker.adapters.storage.regression_dataset_reader import FilesystemRegressionDatasetReader
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
from oil_tracker.application.ports.progress import ProgressUpdate
from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline
from oil_tracker.application.services.detector_benchmark_service import DetectorBenchmarkService
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.domain.session import AnalysisSession


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="oil-tracker-cli")
    sub = parser.add_subparsers(dest="command", required=True)
    analyze = sub.add_parser("analyze", help="Analyze a video with an .oilrecipe file")
    analyze.add_argument("--recipe", required=True)
    analyze.add_argument("--video", required=True)
    analyze.add_argument("--output", default=".")
    analyze.add_argument("--start", type=float, default=0.0)
    analyze.add_argument("--end", type=float)
    analyze.add_argument("--compressor-start", type=float)
    analyze.add_argument("--sampling-fps", type=float, default=2.0)
    benchmark = sub.add_parser(
        "benchmark",
        help="Run the current detector against a Phase 2C-3 regression dataset",
    )
    benchmark.add_argument("--dataset", required=True)
    benchmark.add_argument("--output", default=".")
    benchmark.add_argument("--baseline")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "analyze":
            return _run_analyze(args)
        if args.command == "benchmark":
            return _run_benchmark(args)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 2


def _format_analysis_progress(progress: ProgressUpdate) -> str:
    parts = [f"[{progress.stage_index}/{progress.stage_count}] {progress.stage_label}"]
    if progress.message:
        parts.append(progress.message)
    if progress.total > 0:
        parts.append(f"{progress.completed}/{progress.total}")
    if progress.timestamp_sec is not None:
        parts.append(f"{progress.timestamp_sec:.3f}s")
    if progress.glass_name:
        parts.append(progress.glass_name)
    if progress.rate_fps is not None:
        parts.append(f"{progress.rate_fps:.2f} fps")
    return " | ".join(parts)


def _print_analysis_progress(progress: ProgressUpdate) -> None:
    print(_format_analysis_progress(progress), end="\r", flush=True)


def _run_analyze(args) -> int:
    repository = JsonRecipeRepository()
    recipe = repository.load(Path(args.recipe))
    metadata_reader = OpenCvVideoReader(args.video)
    try:
        metadata = metadata_reader.metadata
    finally:
        metadata_reader.close()
    session = AnalysisSession(
        input_video_path=args.video,
        video_metadata=metadata,
        analysis_start_sec=args.start,
        analysis_end_sec=args.end if args.end is not None else metadata.duration_sec,
        compressor_start_sec=args.compressor_start,
        sampling_fps=args.sampling_fps,
        output_directory=args.output,
        resolution_confirmed=(metadata.width, metadata.height)
        == (recipe.reference_frame_width, recipe.reference_frame_height),
    )
    pipeline = AnalysisPipeline(
        lambda path: OpenCvVideoReader(path),
        OpenCvPhaseDetector(),
        RecipeValidationService(),
    )
    result = pipeline.run(
        recipe,
        session,
        progress=_print_analysis_progress,
    )
    output = OutputBundleStore().write_bundle(
        result,
        recipe,
        session,
        Path(args.output),
        progress=_print_analysis_progress,
    )
    print(f"\n{result.overall_state.value}: {output}")
    return 0


def _run_benchmark(args) -> int:
    service = DetectorBenchmarkService(
        FilesystemRegressionDatasetReader(),
        AtomicBenchmarkResultWriter(),
        OpenCvPhaseDetector,
    )
    run = service.run(args.dataset, args.output, baseline_path=args.baseline)
    payload = run.payload
    print(f"benchmark output: {run.output_path}")
    print(
        f"fixtures: total={payload['case_count']} usable={payload['usable_count']} "
        f"unusable={payload['unusable_count']} categories={payload['category_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
