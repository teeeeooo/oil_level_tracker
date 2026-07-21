from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from oil_tracker.adapters.storage.json_truth_repository import build_truth_bundle_identity
from oil_tracker.application.services.user_truth import TruthFrameContext, UserTruthService
from oil_tracker.domain.enums import FillState, ResultState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.review import ReviewBundle, ReviewGlass, ReviewTrackingSample
from oil_tracker.domain.session import AnalysisSession, VideoMetadata
from oil_tracker.domain.user_truth import TruthDisposition, TruthErrorType


def make_truth_bundle(tmp_path: Path, *, mm_per_pixel: float | None = 0.25) -> ReviewBundle:
    root = tmp_path / "공식 결과 bundle"
    root.mkdir(parents=True, exist_ok=True)
    recipe = InspectionRecipe.empty(320, 240, "truth fixture")
    recipe.recipe_id = "recipe-truth-1"
    glass = InspectionRecipe.default_glass(320, 240)
    glass.id = "glass-1"
    glass.name = "관찰창 1"
    glass.geometry.zero_line_y = 150.0
    glass.mm_per_pixel = mm_per_pixel
    recipe.glasses = [glass]
    source = tmp_path / "원본 영상.mp4"
    source.touch()
    metadata = VideoMetadata(str(source), 320, 240, 30.0, 8.0, 240, "fake")
    session = AnalysisSession(
        input_video_path=str(source),
        video_metadata=metadata,
        analysis_start_sec=1.0,
        analysis_end_sec=7.0,
        compressor_start_sec=1.5,
        sampling_fps=2.0,
    )
    sample = ReviewTrackingSample(
        run_id="run-truth-1",
        glass_id="glass-1",
        frame_index=60,
        timestamp_sec=2.0,
        fill_state=FillState.PARTIAL_VISIBLE,
        raw_oil_air_level_y=130.0,
        raw_oil_air_level_px_from_zero=20.0,
        raw_oil_air_level_mm_from_zero=5.0 if mm_per_pixel is not None else None,
        smoothed_oil_air_level_px_from_zero=20.0,
        smoothed_oil_air_level_mm_from_zero=5.0 if mm_per_pixel is not None else None,
        oil_air_confidence=0.8,
        raw_foam_front_y=120.0,
        raw_foam_front_px_from_zero=30.0,
        raw_foam_front_mm_from_zero=7.5 if mm_per_pixel is not None else None,
        smoothed_foam_front_px_from_zero=30.0,
        smoothed_foam_front_mm_from_zero=7.5 if mm_per_pixel is not None else None,
        foam_confidence=0.6,
        visibility_confidence=0.9,
        overall_confidence=0.8,
        is_valid=True,
        flags=("LOW_CONFIDENCE",),
        input_order=1,
    )
    files = {
        "manifest": root / "analysis_manifest.json",
        "session": root / "session.json",
        "recipe_snapshot": root / "recipe_snapshot.oilrecipe",
        "tracking_data": root / "tracking_data.csv",
        "events": root / "events.csv",
    }
    files["manifest"].write_text(json.dumps({"run_id": "run-truth-1"}), encoding="utf-8")
    files["session"].write_text(json.dumps(session.to_dict(), ensure_ascii=False), encoding="utf-8")
    files["recipe_snapshot"].write_text(json.dumps(recipe.to_dict(), ensure_ascii=False), encoding="utf-8")
    files["tracking_data"].write_text("official tracking\n", encoding="utf-8")
    files["events"].write_text("official events\n", encoding="utf-8")
    (root / "review_index.json").write_text("{}", encoding="utf-8")
    return ReviewBundle(
        root=root,
        run_id="run-truth-1",
        recipe=recipe,
        session=session,
        manifest={"run_id": "run-truth-1"},
        source_video_path=str(source),
        source_video_candidates=(str(source),),
        source_metadata=metadata,
        analysis_start_sec=1.0,
        analysis_end_sec=7.0,
        compressor_start_sec=1.5,
        glasses=(ReviewGlass("glass-1", "관찰창 1", ResultState.PASS),),
        samples=(sample,),
        events=(),
        files=files,
    )


def make_truth_set_and_annotation(
    bundle: ReviewBundle,
    *,
    disposition: TruthDisposition = TruthDisposition.CORRECTED,
    fill_state: FillState | None = FillState.PARTIAL_VISIBLE,
    oil_y: float | None = 128.0,
    foam_present: bool = True,
    foam_y: float | None = 118.0,
    error_types=(TruthErrorType.WRONG_CANDIDATE,),
    note: str = "사용자 확인",
):
    service = UserTruthService()
    identity = build_truth_bundle_identity(bundle)
    truth_set = service.create_set(identity)
    glass = bundle.recipe.glasses[0]
    context = TruthFrameContext("glass-1", "관찰창 1", 2.0, 2.0, 60)
    official = service.official_reference(bundle, glass, 2.0)
    annotation = service.make_annotation(
        truth_set,
        identity,
        glass,
        context,
        disposition,
        truth_fill_state=fill_state,
        oil_source_y=oil_y,
        foam_present=foam_present,
        foam_source_y=foam_y,
        error_types=error_types,
        note=note,
        official_reference=official,
    )
    return truth_set, truth_set.upsert(annotation), service


class FakeVideoReader:
    def __init__(
        self,
        path,
        *,
        frame_index: int = 60,
        timestamp: float = 2.0,
        width: int = 320,
        height: int = 240,
        fps: float = 30.0,
    ) -> None:
        self.path = str(path)
        self.frame_index = frame_index
        self.timestamp = timestamp
        self.metadata = VideoMetadata(self.path, width, height, fps, 8.0, int(8.0 * fps), "fake")
        self.closed = False
        self.requests: list[float] = []

    def read_at(self, timestamp: float):
        self.requests.append(float(timestamp))
        frame = np.zeros((self.metadata.height, self.metadata.width, 3), dtype=np.uint8)
        frame[:, :, 0] = 12
        frame[:, :, 1] = 34
        frame[:, :, 2] = 56
        return frame, self.frame_index, self.timestamp

    def close(self) -> None:
        self.closed = True


def snapshot_tree(root: Path) -> dict[str, tuple[str, bytes]]:
    return {
        path.relative_to(root).as_posix(): (
            "directory",
            b"",
        )
        if path.is_dir()
        else ("file", path.read_bytes())
        for path in sorted(root.rglob("*"), key=lambda value: value.relative_to(root).as_posix())
    }
