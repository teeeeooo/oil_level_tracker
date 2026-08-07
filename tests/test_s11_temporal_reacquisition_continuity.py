from __future__ import annotations

from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.domain.session import AnalysisSession
from tests.s11_local_corpus import require_s11_local_corpus


_TARGETS = {914, 929, 1004, 1034, 1049, 1064, 1079, 1094, 1109, 1124, 1139}


class _DetectorRegressionValidator:
    def __init__(self) -> None:
        self.inner = RecipeValidationService()

    def validate(self, recipe, session, **_kwargs):
        return self.inner.validate(recipe, session, require_run_confirmation=False)


class _CaptureDetector:
    def __init__(self) -> None:
        self.inner = OpenCvPhaseDetector()
        self.rows: dict[int, dict[str, object]] = {}

    def reset(self, glass_id: str | None = None) -> None:
        self.inner.reset(glass_id)

    def learn_static_artifact(self, frames, glass) -> None:
        self.inner.learn_static_artifact(frames, glass)

    def detect(self, frame, glass, frame_index: int, time_sec: float, debug: bool = False):
        detection, artifacts = self.inner.detect(frame, glass, frame_index, time_sec, debug=debug)
        if frame_index in _TARGETS:
            state = self.inner._oil_pipeline.temporal_snapshot(glass.id).state
            self.rows[frame_index] = {
                "status": detection.debug_metrics["oil_decision_status"],
                "reason": detection.debug_metrics["oil_decision_reason"],
                "raw_y": detection.raw_oil_air_level_y,
                "projected_y": detection.debug_metrics["oil_temporal_projected_source_y"],
                "foam_authoritative": detection.debug_metrics["foam_oil_context_authoritative"],
                "accepted_y": state.accepted_y,
                "accepted_velocity": state.accepted_velocity,
                "pending_y": state.pending_y,
                "pending_velocity": state.pending_velocity,
                "pending_count": state.pending_count,
            }
        return detection, artifacts


def test_sample3_ambiguity_gated_reacquisition_preserves_recovery_and_safety(tmp_path) -> None:
    root = require_s11_local_corpus()
    video_path = root / "sample" / "sample3.mp4"
    recipe = JsonRecipeRepository().load(root / "sample" / "sample3.oilrecipe")
    reader = OpenCvVideoReader(str(video_path))
    try:
        metadata = reader.metadata
    finally:
        reader.close()

    detector = _CaptureDetector()
    session = AnalysisSession(
        input_video_path=str(video_path),
        video_metadata=metadata,
        analysis_start_sec=0.0,
        analysis_end_sec=40.1,
        compressor_start_sec=30.03,
        sampling_fps=2.0,
        output_directory=str(tmp_path),
        run_name="S11 ambiguity-gated temporal reacquisition regression",
        resolution_confirmed=True,
    )
    pipeline = AnalysisPipeline(
        lambda path: OpenCvVideoReader(path),
        detector,
        _DetectorRegressionValidator(),
    )
    pipeline.run(recipe, session)

    rows = detector.rows
    assert set(rows) == _TARGETS
    assert rows[914]["status"] == "reacquisition_pending"
    assert rows[914]["pending_y"] == 301.0 and rows[914]["pending_count"] == 1
    assert rows[929]["status"] == "boundary_accepted"
    assert rows[929]["reason"] == "bounded_shadow_reacquisition"
    assert rows[929]["raw_y"] == 300.0

    assert rows[1004]["status"] == "boundary_accepted"
    assert rows[1004]["reason"] == "continuous_shadow_boundary"
    assert rows[1004]["raw_y"] == 304.0

    assert rows[1034]["status"] == "reacquisition_pending"
    assert rows[1034]["pending_y"] == 245.0 and rows[1034]["pending_count"] == 1
    assert rows[1049]["status"] == "ambiguous" and rows[1049]["raw_y"] is None
    assert rows[1049]["projected_y"] == 240.0
    assert rows[1049]["pending_y"] == 245.0 and rows[1049]["pending_count"] == 1

    assert rows[1064]["status"] == "reacquisition_pending" and rows[1064]["raw_y"] is None
    assert rows[1064]["pending_y"] == 258.0 and rows[1064]["pending_count"] == 1
    assert rows[1079]["status"] == "ambiguous" and rows[1079]["raw_y"] is None
    assert rows[1079]["projected_y"] == 231.0
    assert rows[1079]["foam_authoritative"] is True
    assert rows[1079]["pending_y"] is None and rows[1079]["pending_count"] == 0

    assert rows[1094]["status"] == "reacquisition_pending"
    assert rows[1094]["pending_y"] == 244.0 and rows[1094]["pending_count"] == 1
    assert rows[1109]["status"] == "ambiguous" and rows[1109]["raw_y"] is None
    assert rows[1109]["projected_y"] == 248.0
    assert rows[1109]["foam_authoritative"] is True
    assert rows[1109]["pending_y"] == 244.0 and rows[1109]["pending_count"] == 1

    assert rows[1124]["status"] == "boundary_accepted"
    assert rows[1124]["reason"] == "bounded_shadow_reacquisition"
    assert rows[1124]["raw_y"] == 250.0
    assert rows[1124]["accepted_y"] == 250.0
    assert rows[1124]["accepted_velocity"] is None
    assert rows[1124]["pending_count"] == 0

    assert rows[1139]["status"] == "boundary_accepted"
    assert rows[1139]["reason"] == "continuous_shadow_boundary"
    assert rows[1139]["raw_y"] == 267.0
    assert rows[1139]["accepted_y"] == 267.0
    assert rows[1139]["accepted_velocity"] == 17.0
