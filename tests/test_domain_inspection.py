from dataclasses import replace

import pytest

from oil_tracker.domain.enums import JudgmentMode, SampleOrigin
from oil_tracker.domain.geometry import Ellipse
from oil_tracker.domain.inspection import (
    Analysis,
    AnalysisSettings,
    GlassDraft,
    SourceVideo,
    needs_compressor_start,
    setup_problems,
)
from oil_tracker.domain.line import Line
from oil_tracker.domain.recipe import Glass, JudgmentRule, Recipe, ReferenceFrame

VIDEO = SourceVideo("C:/videos/SPL#1.mp4", "SPL#1.mp4", 683_165_477, 1920, 1080, 23.976, 98_413)
HOLD = JudgmentRule(mode=JudgmentMode.HOLD_BELOW_ZERO)


def make_recipe(*rules: JudgmentRule) -> Recipe:
    glasses = tuple(
        Glass(f"g{i}", f"Glass {i}", Ellipse(400 + 300 * i, 500, 80, 200), 520, rule)
        for i, rule in enumerate(rules or (JudgmentRule(),))
    )
    return Recipe("r1", "SPL#1 가열", ReferenceFrame(1920, 1080, "SPL#1.mp4", 0.0, b"jpeg"), glasses, "c", "u")


def fields(problems) -> list[str]:
    return [problem.field for problem in problems]


def test_sample_count_matches_the_analysis_rate():
    assert AnalysisSettings(0, 2.5).sample_count == 6
    assert AnalysisSettings(0, VIDEO.duration_sec).sample_count == 8210  # SPL#1, as built on Windows


def test_a_complete_setup_has_no_problems():
    assert setup_problems(VIDEO, make_recipe(), AnalysisSettings(0, VIDEO.duration_sec, 532.0)) == []


def test_a_recipe_of_another_frame_size_is_refused():
    small = replace(VIDEO, width=1280, height=720)
    problems = setup_problems(small, make_recipe(), AnalysisSettings(0, 60, 10))
    assert [(p.field, p.message) for p in problems] == [
        ("recipe", "영상 해상도 1280×720가 이 Recipe의 1920×1080와 다릅니다.")
    ]


@pytest.mark.parametrize(
    ("start", "end", "field"),
    [(-1, 60, "start_sec"), (0, 99_999, "end_sec"), (30, 30.5, "end_sec"), (60, 30, "end_sec"), (float("nan"), 60, "start_sec")],
)
def test_the_range_lies_inside_the_video_and_lasts_a_second(start, end, field):
    assert fields(setup_problems(VIDEO, make_recipe(HOLD), AnalysisSettings(start, end))) == [field]


def test_the_compressor_start_is_required_only_with_a_recovery_glass():
    assert needs_compressor_start(make_recipe(HOLD, JudgmentRule()))
    assert not needs_compressor_start(make_recipe(HOLD))
    assert fields(setup_problems(VIDEO, make_recipe(HOLD, JudgmentRule()), AnalysisSettings(0, 60))) == [
        "compressor_start_sec"
    ]
    assert setup_problems(VIDEO, make_recipe(HOLD), AnalysisSettings(0, 60)) == []


@pytest.mark.parametrize("compressor", [5.0, 70.0, float("inf")])
def test_the_compressor_start_lies_inside_the_range(compressor):
    problems = setup_problems(VIDEO, make_recipe(HOLD), AnalysisSettings(10, 60, compressor))
    assert [(p.field, p.message) for p in problems] == [("compressor_start_sec", "압축기 기동 시각이 분석 범위 밖입니다.")]


def test_a_glass_corrected_outside_the_frame_is_a_problem_of_that_glass():
    recipe = make_recipe()
    moved = replace(recipe.glasses[0], ellipse=Ellipse(1900, 500, 80, 200))
    problems = setup_problems(VIDEO, replace(recipe, glasses=(moved,)), AnalysisSettings(0, 60, 10))
    assert {(p.field, p.glass_id) for p in problems} == {("ellipse", "g0")}


def test_a_line_has_one_origin_per_finite_or_empty_sample():
    line = Line((400.0, None, 402.5), (SampleOrigin.DRAFT,) * 3)
    assert line.empty_count == 1
    with pytest.raises(ValueError):
        Line((400.0,), ())
    with pytest.raises(ValueError):
        Line((float("nan"),), (SampleOrigin.DRAFT,))


def test_an_analysis_has_one_sample_per_time_in_every_draft():
    oil = Line((400.0, None), (SampleOrigin.DRAFT,) * 2)
    Analysis((0.0, 0.5), (GlassDraft("g0", oil),), "2026-10-29T15:00:00+09:00")
    with pytest.raises(ValueError):
        Analysis((0.0, 0.5, 1.0), (GlassDraft("g0", oil),), "2026-10-29T15:00:00+09:00")
