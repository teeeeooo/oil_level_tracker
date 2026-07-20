from __future__ import annotations

from pathlib import Path

import pytest

from oil_tracker.application.services.review_query import ReviewQueryModel, review_categories
from oil_tracker.domain.enums import FillState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.review import (
    ReviewBundle,
    ReviewCategory,
    ReviewFilter,
    ReviewGlass,
    ReviewTrackingSample,
)
from oil_tracker.domain.session import AnalysisSession


def _sample(glass_id, timestamp, *, confidence=0.9, valid=True, flags=()):
    return ReviewTrackingSample(
        run_id="run",
        glass_id=glass_id,
        frame_index=int(timestamp * 10),
        timestamp_sec=timestamp,
        fill_state=FillState.PARTIAL_VISIBLE,
        overall_confidence=confidence,
        is_valid=valid,
        flags=tuple(flags),
    )


def _query(samples):
    recipe = InspectionRecipe.empty(320, 240)
    glass = InspectionRecipe.default_glass(320, 240, 1)
    glass.detector_settings.minimum_final_confidence = 0.5
    recipe.glasses.append(glass)
    converted = tuple(
        ReviewTrackingSample(**{**sample.__dict__, "glass_id": glass.id})
        for sample in samples
    )
    bundle = ReviewBundle(
        root=Path("/bundle"),
        run_id="run",
        recipe=recipe,
        session=AnalysisSession(analysis_start_sec=0.0, analysis_end_sec=10.0, sampling_fps=1.0),
        manifest={},
        source_video_path="",
        source_video_candidates=(),
        source_metadata=None,
        analysis_start_sec=0.0,
        analysis_end_sec=10.0,
        compressor_start_sec=None,
        glasses=(ReviewGlass(glass.id, glass.name),),
        samples=converted,
        events=(),
    )
    return ReviewQueryModel(bundle), glass


@pytest.mark.parametrize(
    ("sample", "category"),
    [
        (_sample("x", 1.0, valid=False), ReviewCategory.INVALID),
        (_sample("x", 1.0, confidence=0.2), ReviewCategory.LOW_CONFIDENCE),
        (_sample("x", 1.0, flags=("REVIEW_REQUIRED",)), ReviewCategory.REVIEW_REQUIRED),
        (_sample("x", 1.0, flags=("FOAM_REVIEW",)), ReviewCategory.FOAM),
        (_sample("x", 1.0, flags=("FOGGED_OR_GLARE",)), ReviewCategory.GLARE_OR_FOG),
        (_sample("x", 1.0, flags=("DETECTION_LOST",)), ReviewCategory.DETECTION_LOST),
    ],
)
def test_review_category_classification(sample, category):
    assert category in review_categories(sample, 0.5)


def test_interval_can_have_multiple_categories_and_match_each_filter():
    query, glass = _query([
        _sample("x", 1.0, confidence=0.2, valid=False, flags=("FOAM_REVIEW", "FOGGED_OR_GLARE", "DETECTION_LOST")),
    ])
    interval = query.low_confidence_intervals(glass.id)[0]
    assert {
        ReviewCategory.INVALID,
        ReviewCategory.LOW_CONFIDENCE,
        ReviewCategory.REVIEW_REQUIRED,
        ReviewCategory.FOAM,
        ReviewCategory.GLARE_OR_FOG,
        ReviewCategory.DETECTION_LOST,
    }.issubset(set(interval.categories))
    for review_filter in ReviewFilter:
        assert len(query.filtered_intervals(glass.id, review_filter)) == 1


def test_empty_filter_result_and_filtered_previous_next():
    query, glass = _query([
        _sample("x", 1.0, valid=False),
        _sample("x", 4.0, flags=("DETECTION_LOST",)),
    ])
    assert query.filtered_intervals(glass.id, ReviewFilter.FOAM) == ()
    assert query.next_review(glass.id, 0.0, ReviewFilter.DETECTION_LOST).representative_time_sec == 4.0
    assert query.previous_review(glass.id, 9.0, ReviewFilter.INVALID).representative_time_sec == 1.0
    assert query.next_review(glass.id, 5.0, ReviewFilter.DETECTION_LOST) is None
