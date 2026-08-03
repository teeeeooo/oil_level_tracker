from __future__ import annotations

from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.session import AnalysisSession


def test_run_name_round_trips_as_session_state():
    session = AnalysisSession(run_name="냉방 반복 시험 03")
    restored = AnalysisSession.from_dict(session.to_dict())

    assert restored.run_name == "냉방 반복 시험 03"


def test_old_session_without_run_name_remains_readable():
    payload = AnalysisSession(input_video_path="old.mp4").to_dict()
    payload.pop("run_name")

    restored = AnalysisSession.from_dict(payload)

    assert restored.input_video_path == "old.mp4"
    assert restored.run_name == ""


def test_run_name_is_not_recipe_owned_state():
    recipe = InspectionRecipe.empty(name="재사용 프로필")
    session = AnalysisSession(run_name="시험 A")

    assert "run_name" not in recipe.to_dict()
    assert session.to_dict()["run_name"] == "시험 A"
