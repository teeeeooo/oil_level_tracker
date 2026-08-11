from __future__ import annotations

"""Production safety checks retained from the retired S11 Spatial probes.

R6 no longer gives Spatial or Foam an independent publication authority.  This
module therefore keeps only black-box safeguards that remain part of the
production contract; historical D2-D5 implementation probes live in the
diagnostic record instead of constraining the current detector.
"""

from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

from oil_observability_fixtures import (
    historical_glare_negatives,
    single_frame_observability_collisions,
)
from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.adapters.vision.geometry_masks import build_mask_bundle
from oil_tracker.adapters.vision.oil_shadow_observations import extract_raw_observations
from oil_tracker.adapters.vision.oil_shadow_types import OilShadowBounds, ShadowSourceFamily
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.adapters.vision.preprocessing import preprocess
from oil_tracker.domain.recipe import InspectionRecipe
from tests.diagnostics.s11_evidence_probe import (
    ProbeCase,
    TRANSFORMS,
    decode_frame,
    load_cases,
    run_variant,
    transform_frame,
)
from tests.s11_local_corpus import require_s11_local_corpus


def _production_raw_oil(frame: np.ndarray, glass, *, frame_index: int = 0) -> float | None:
    detection, _artifacts = OpenCvPhaseDetector().detect(
        frame,
        glass,
        frame_index=frame_index,
        time_sec=0.0,
        debug=False,
    )
    return detection.raw_oil_air_level_y


def _resolved_repeated_oil(frame: np.ndarray, glass) -> list[float | None]:
    detector = OpenCvPhaseDetector()
    detections = [
        detector.detect(
            frame.copy(),
            glass,
            frame_index=index,
            time_sec=index * 0.5,
            debug=False,
        )[0]
        for index in range(5)
    ]
    return [
        detection.raw_oil_air_level_y
        for detection in detector.resolve_sequence(detections, glass).detections
    ]


def _diagnostic_case(frame, glass, case_id: str) -> ProbeCase:
    return ProbeCase(
        sample=case_id,
        frame_index=0,
        time_sec=0.0,
        truth_oil_y=0.0,
        truth_foam_present=False,
        truth_foam_y=None,
        glass=glass,
        video_path=Path("."),
    )


def _decode_local_video_frame(root: Path, sample: str, frame_index: int) -> np.ndarray:
    capture = cv2.VideoCapture(str(root / "sample" / f"{sample}.mp4"))
    capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ok, frame = capture.read()
    capture.release()
    if not ok or frame is None:
        raise RuntimeError(f"Could not decode {sample}:{frame_index}")
    return frame


def test_slice_a_removes_distributed_supplemental_authority_without_forced_promotion() -> None:
    root = require_s11_local_corpus()
    glass = JsonRecipeRepository().load(root / "sample" / "sample3.oilrecipe").glasses[0]
    frame = _decode_local_video_frame(root, "sample3", 2697)

    detection, _artifacts = OpenCvPhaseDetector().detect(
        frame,
        glass,
        frame_index=2697,
        time_sec=89.9899,
        debug=False,
    )
    assert detection.raw_oil_air_level_y is None
    assert detection.debug_metrics["oil_decision_status"] == "ambiguous"

    bundle = build_mask_bundle(frame, glass)
    pre = preprocess(bundle.crop, bundle.effective_mask, glass.detector_settings)
    raw = extract_raw_observations(
        pre,
        bundle.effective_mask,
        crop_origin_y=float(bundle.crop_origin[1]),
        bounds=OilShadowBounds(),
    )
    assert raw
    assert ShadowSourceFamily.REGION_STEP in {item.source_family for item in raw}
    assert not any(
        item.source_family is ShadowSourceFamily.SOBEL_DISTRIBUTED for item in raw
    )


def test_scalar_relative_collision_candidates_cannot_publish_numeric_oil() -> None:
    grouped = defaultdict(list)
    relative_numeric = 0
    production_numeric = 0
    for scene in single_frame_observability_collisions():
        glass = InspectionRecipe.default_glass(320, 240)
        glass.id = f"s11-production-collision-{scene.case_id}"
        case = _diagnostic_case(scene.frame, glass, scene.case_id)
        relative = run_variant(scene.frame.copy(), case, "P1")
        resolved = _resolved_repeated_oil(scene.frame, glass)
        relative_numeric += relative.oil_y is not None
        production_numeric += sum(value is not None for value in resolved)
        grouped[scene.collision_id].append(resolved)

    # The historical relative scorer is stimulus generation, not production
    # authority. Its exact count may change as diagnostics are simplified.
    assert relative_numeric > 0
    assert production_numeric == 0
    assert all(
        pair == [[None] * 5, [None] * 5]
        for pair in grouped.values()
    )


def test_retained_glare_negatives_remain_non_numeric_in_production() -> None:
    for scene in historical_glare_negatives():
        glass = InspectionRecipe.default_glass(320, 240)
        glass.id = f"s11-production-glare-{scene.case_id}"
        assert _production_raw_oil(scene.frame.copy(), glass) is None, scene.case_id


def test_p2_semantic_rescues_do_not_gain_spatial_numeric_oil() -> None:
    root = require_s11_local_corpus()
    cases = {case.case_id: case for case in load_cases(root)}
    transforms = {item.name: item for item in TRANSFORMS}
    expected = (
        ("brightness_0.60", "sample3:900"),
        ("brightness_0.45", "base_sample_1:144"),
        ("brightness_0.45", "sample3:900"),
        ("brightness_0.45", "sample3:1035"),
    )
    for transform_id, case_id in expected:
        case = cases[case_id]
        frame = transform_frame(decode_frame(case), transforms[transform_id])
        detection, _artifacts = OpenCvPhaseDetector().detect(
            frame,
            case.glass,
            frame_index=case.frame_index,
            time_sec=case.time_sec,
            debug=False,
        )
        assert detection.raw_oil_air_level_y is None
        assert "OIL_EVIDENCE_AMBIGUOUS" in detection.flags


def test_low_exposure_known_false_boundary_warning_stays_fail_closed() -> None:
    root = require_s11_local_corpus()
    cases = {case.case_id: case for case in load_cases(root)}
    transforms = {item.name: item for item in TRANSFORMS}
    case = cases["sample4:450"]
    for transform_id in ("brightness_0.60", "brightness_0.45"):
        frame = transform_frame(decode_frame(case), transforms[transform_id])
        assert _production_raw_oil(frame, case.glass, frame_index=case.frame_index) is None
