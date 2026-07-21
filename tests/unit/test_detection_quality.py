from __future__ import annotations

from oil_tracker.application.detection_quality import DetectionQuality, assess_detection_quality
from oil_tracker.domain.detection import PhaseDetection
from oil_tracker.domain.enums import FillState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.ui.readiness import PreviewQuality, build_detection_summary


def _detection(glass_id: str, *, state=FillState.PARTIAL_VISIBLE, confidence=0.9, y=200.0, flags=None):
    return PhaseDetection(
        glass_id,
        1,
        0.1,
        state,
        oil_air_level_y=y,
        overall_confidence=confidence,
        flags=list(flags or []),
    )


def test_shared_quality_helper_matches_current_frame_preview_card_semantics():
    glass = InspectionRecipe.default_glass(640, 480)
    cases = [
        (_detection(glass.id), DetectionQuality.NORMAL),
        (_detection(glass.id, confidence=0.1), DetectionQuality.REVIEW),
        (_detection(glass.id, flags=["FOGGED_OR_GLARE"]), DetectionQuality.REVIEW),
        (_detection(glass.id, state=FillState.FOAMING_VISIBLE, flags=["FOAM_REACH_TOP"]), DetectionQuality.REVIEW),
        (_detection(glass.id, y=None, flags=["DETECTION_LOST"]), DetectionQuality.FAILURE),
    ]

    for detection, expected in cases:
        assessment = assess_detection_quality(
            detection,
            glass.detector_settings.minimum_final_confidence,
        )
        preview = build_detection_summary(detection, glass)
        assert assessment.quality == expected
        assert preview.quality == PreviewQuality(expected.value)
        if detection.fill_state == FillState.FOAMING_VISIBLE:
            assert preview.interpretation == "거품 가능성이 감지됨"
            assert preview.recommendation == "영상에서 실제 거품인지 확인하세요."
            assert preview.action_key == "initial_state"
        else:
            assert preview.interpretation == assessment.reason
            assert preview.recommendation


def test_explicit_full_or_empty_state_without_visible_boundary_remains_usable():
    glass = InspectionRecipe.default_glass(640, 480)
    detection = _detection(
        glass.id,
        state=FillState.FULL_NO_INTERFACE,
        confidence=0.8,
        y=None,
    )

    assessment = assess_detection_quality(detection, glass.detector_settings.minimum_final_confidence)

    assert assessment.quality == DetectionQuality.NORMAL
    assert build_detection_summary(detection, glass).quality == PreviewQuality.NORMAL
