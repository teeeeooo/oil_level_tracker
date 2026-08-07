from __future__ import annotations

import pytest

from oil_tracker import cli
from oil_tracker.application.ports.progress import AnalysisStage, build_progress_update
from oil_tracker.domain.enums import InitialObservationState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.session import AnalysisSession


def test_lifecycle_progress_formats_without_frame_only_values() -> None:
    update = build_progress_update(
        AnalysisStage.EVENTS_AND_JUDGMENT,
        0.0,
        message="Glass별 이벤트와 판정을 계산하고 있습니다.",
        total=1,
    )

    rendered = cli._format_analysis_progress(update)

    assert "[2/6] 이벤트와 판정 계산" in rendered
    assert "Glass별 이벤트와 판정을 계산하고 있습니다." in rendered
    assert "0/1" in rendered
    assert "None" not in rendered


def test_frame_progress_keeps_timestamp_glass_and_rate() -> None:
    update = build_progress_update(
        AnalysisStage.VIDEO_ANALYSIS,
        0.5,
        message="Glass A 검출 중",
        completed=3,
        total=5,
        timestamp_sec=1.23456,
        glass_name="Glass A",
        rate_fps=7.891,
    )

    rendered = cli._format_analysis_progress(update)

    assert "[1/6] 영상 분석" in rendered
    assert "3/5" in rendered
    assert "1.235s" in rendered
    assert "Glass A" in rendered
    assert "7.89 fps" in rendered


def test_analyze_parser_accepts_optional_run_name_without_changing_default():
    parser = cli.build_parser()
    default_args = parser.parse_args(["analyze", "--recipe", "a.oilrecipe", "--video", "a.mp4"])
    named_args = parser.parse_args(
        ["analyze", "--recipe", "a.oilrecipe", "--video", "a.mp4", "--run-name", "시험 03"]
    )

    assert default_args.run_name == ""
    assert named_args.run_name == "시험 03"


def test_analyze_parser_accepts_explicit_repeated_initial_state_confirmations():
    parser = cli.build_parser()
    args = parser.parse_args(
        [
            "analyze",
            "--recipe",
            "a.oilrecipe",
            "--video",
            "a.mp4",
            "--initial-state-confirmation",
            "g1=FULL_NO_INTERFACE",
            "--initial-state-confirmation",
            "g2=UNKNOWN_REVIEW",
        ]
    )
    assert args.initial_state_confirmation == [
        "g1=FULL_NO_INTERFACE",
        "g2=UNKNOWN_REVIEW",
    ]


def test_cli_confirmation_is_explicit_and_bound_to_current_video_start_context():
    recipe = InspectionRecipe.empty(320, 240)
    glass = InspectionRecipe.default_glass(320, 240)
    glass.initial_state = InitialObservationState.FULL_NO_INTERFACE
    recipe.glasses.append(glass)
    session = AnalysisSession(input_video_path="current.mp4", analysis_start_sec=1.25)

    cli._apply_initial_state_confirmations(
        recipe,
        session,
        [f"{glass.id}=FULL_NO_INTERFACE"],
    )
    confirmation = session.initial_state_confirmations[glass.id]
    assert confirmation.state is InitialObservationState.FULL_NO_INTERFACE
    assert confirmation.input_video_path == "current.mp4"
    assert confirmation.analysis_start_sec == 1.25


def test_cli_confirmation_rejects_auto_and_recipe_mismatch():
    recipe = InspectionRecipe.empty(320, 240)
    glass = InspectionRecipe.default_glass(320, 240)
    recipe.glasses.append(glass)
    session = AnalysisSession(input_video_path="current.mp4")

    with pytest.raises(ValueError, match="AUTO cannot be confirmed"):
        cli._apply_initial_state_confirmations(
            recipe,
            session,
            [f"{glass.id}=AUTO"],
        )

    glass.initial_state = InitialObservationState.FULL_NO_INTERFACE
    with pytest.raises(ValueError, match="does not match"):
        cli._apply_initial_state_confirmations(
            recipe,
            session,
            [f"{glass.id}=EMPTY_NO_INTERFACE"],
        )
