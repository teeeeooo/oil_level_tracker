from __future__ import annotations

from copy import deepcopy
from uuid import uuid4

import pytest

from oil_tracker.application.preflight import preflight_context_key
from oil_tracker.domain.enums import InitialObservationState
from oil_tracker.domain.geometry import ExclusionZone, Rect
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.session import AnalysisSession, VideoMetadata


def _context():
    recipe = InspectionRecipe.empty(640, 480)
    recipe.glasses = [InspectionRecipe.default_glass(640, 480)]
    metadata = VideoMetadata("video.mp4", 640, 480, 30.0, 10.0, 300)
    session = AnalysisSession(
        input_video_path=metadata.path,
        video_metadata=metadata,
        analysis_start_sec=0.0,
        analysis_end_sec=10.0,
        compressor_start_sec=1.0,
        sampling_fps=2.0,
    )
    return recipe, session


def test_non_detection_metadata_and_sampling_rate_do_not_make_result_stale():
    recipe, session = _context()
    original = preflight_context_key(recipe, session)

    recipe.name = "renamed recipe"
    recipe.description = "documentation only"
    recipe.touch()
    session.sampling_fps = 5.0

    assert preflight_context_key(recipe, session) == original


@pytest.mark.parametrize(
    "mutate",
    [
        lambda recipe, session: setattr(session, "input_video_path", "other.mp4"),
        lambda recipe, session: setattr(session, "analysis_start_sec", 0.5),
        lambda recipe, session: setattr(session, "analysis_end_sec", 9.5),
        lambda recipe, session: setattr(session, "compressor_start_sec", 1.5),
        lambda recipe, session: setattr(recipe.glasses[0], "enabled", False),
        lambda recipe, session: setattr(recipe.glasses[0], "name", "관찰창 변경"),
        lambda recipe, session: setattr(recipe.glasses[0].geometry.ellipse, "center_x", 321.0),
        lambda recipe, session: setattr(recipe.glasses[0].geometry, "zero_line_y", 250.0),
        lambda recipe, session: recipe.glasses[0].geometry.exclusions.append(
            ExclusionZone(str(uuid4()), Rect(1.0, 2.0, 3.0, 4.0), "제외")
        ),
        lambda recipe, session: setattr(
            recipe.glasses[0].detector_settings,
            "minimum_final_confidence",
            0.75,
        ),
        lambda recipe, session: setattr(
            recipe.glasses[0],
            "initial_state",
            InitialObservationState.FULL_NO_INTERFACE,
        ),
        lambda recipe, session: setattr(recipe.glasses[0], "mm_per_pixel", 0.2),
    ],
)
def test_all_preflight_relevant_changes_invalidate_context(mutate):
    recipe, session = _context()
    original = preflight_context_key(recipe, session)
    changed_recipe = deepcopy(recipe)
    changed_session = deepcopy(session)

    mutate(changed_recipe, changed_session)

    assert preflight_context_key(changed_recipe, changed_session) != original
