from __future__ import annotations

import argparse
from pathlib import Path

from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.adapters.storage.output_bundle_store import OutputBundleStore
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline
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
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "analyze":
        repository = JsonRecipeRepository(); recipe = repository.load(Path(args.recipe))
        metadata_reader = OpenCvVideoReader(args.video); metadata = metadata_reader.metadata; metadata_reader.close()
        session = AnalysisSession(
            input_video_path=args.video,
            video_metadata=metadata,
            analysis_start_sec=args.start,
            analysis_end_sec=args.end if args.end is not None else metadata.duration_sec,
            compressor_start_sec=args.compressor_start,
            sampling_fps=args.sampling_fps,
            output_directory=args.output,
            resolution_confirmed=(metadata.width, metadata.height) == (recipe.reference_frame_width, recipe.reference_frame_height),
        )
        pipeline = AnalysisPipeline(lambda path: OpenCvVideoReader(path), OpenCvPhaseDetector(), RecipeValidationService())
        result = pipeline.run(recipe, session, progress=lambda p: print(f"{p.completed}/{p.total} {p.timestamp_sec:.3f}s {p.glass_name}", end="\r"))
        output = OutputBundleStore().write_bundle(result, recipe, session, Path(args.output))
        print(f"\n{result.overall_state.value}: {output}")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
