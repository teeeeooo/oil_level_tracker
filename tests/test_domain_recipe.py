import math
from dataclasses import replace

import pytest

from oil_tracker.domain.enums import JudgmentMode
from oil_tracker.domain.geometry import Ellipse
from oil_tracker.domain.recipe import (
    Glass,
    JudgmentRule,
    Recipe,
    ReferenceFrame,
    recipe_problems,
)


def make_recipe(**changes) -> Recipe:
    glass = Glass(
        id="g1",
        name="BASE",
        ellipse=Ellipse(center_x=640, center_y=360, radius_x=80, radius_y=200),
        zero_line_y=380,
    )
    recipe = Recipe(
        id="r1",
        name="2호기 냉각",
        reference_frame=ReferenceFrame(1280, 720, "SPL#4.mp4", 12.5, b"\xff\xd8jpeg"),
        glasses=(glass,),
        created_at="2026-10-29T00:00:00+00:00",
        updated_at="2026-10-29T00:00:00+00:00",
    )
    return replace(recipe, **changes)


def fields_of(recipe: Recipe) -> list[str]:
    return [problem.field for problem in recipe_problems(recipe)]


def test_judgment_rule_defaults_follow_product_ssot():
    rule = JudgmentRule()
    assert rule.mode is JudgmentMode.RECOVERY
    assert rule.recovery_limit_sec == 120
    assert rule.stable_hold_sec == 5
    assert rule.minimum_valid_coverage_ratio == 0.70
    assert rule.allowed_sec == 5
    assert rule.allowed_px == 0


def test_valid_recipe_has_no_problems():
    assert recipe_problems(make_recipe()) == []


@pytest.mark.parametrize("name", ["", "   ", "x" * 101])
def test_recipe_name_is_required_and_bounded(name):
    assert fields_of(make_recipe(name=name)) == ["name"]


def test_reference_frame_needs_size_and_image():
    frame = make_recipe().reference_frame
    assert fields_of(make_recipe(reference_frame=replace(frame, width=0))) == ["reference_frame"]
    assert fields_of(make_recipe(reference_frame=replace(frame, jpeg=b""))) == ["reference_frame"]


def test_recipe_needs_a_glass():
    assert fields_of(make_recipe(glasses=())) == ["glasses"]


def test_glass_names_are_unique_ignoring_case():
    glass = make_recipe().glasses[0]
    twin = replace(glass, id="g2", name=" base ")
    problems = recipe_problems(make_recipe(glasses=(glass, twin)))
    assert [(p.field, p.glass_id) for p in problems] == [("name", "g2")]


def test_glass_ids_are_unique():
    glass = make_recipe().glasses[0]
    twin = replace(glass, name="Accum")
    assert fields_of(make_recipe(glasses=(glass, twin))) == ["id"]


@pytest.mark.parametrize(
    "ellipse",
    [
        Ellipse(640, 360, 80, 400),  # taller than the frame
        Ellipse(20, 360, 80, 200),  # off the left edge
        Ellipse(640, 360, 4, 200),  # radius below the minimum
        Ellipse(math.nan, 360, 80, 200),
    ],
)
def test_ellipse_must_be_finite_large_enough_and_inside_the_frame(ellipse):
    glass = replace(make_recipe().glasses[0], ellipse=ellipse)
    assert set(fields_of(make_recipe(glasses=(glass,)))) == {"ellipse"}


@pytest.mark.parametrize("zero", [159.0, 561.0, math.inf])
def test_zero_line_lies_within_the_ellipse_height(zero):
    glass = replace(make_recipe().glasses[0], zero_line_y=zero)
    assert fields_of(make_recipe(glasses=(glass,))) == ["zero_line_y"]


@pytest.mark.parametrize("zero", [160.0, 560.0])
def test_zero_line_may_touch_the_ellipse_ends(zero):
    glass = replace(make_recipe().glasses[0], zero_line_y=zero)
    assert recipe_problems(make_recipe(glasses=(glass,))) == []


@pytest.mark.parametrize(
    ("change", "field"),
    [
        ({"recovery_limit_sec": 0.0}, "recovery_limit_sec"),
        ({"stable_hold_sec": -1.0}, "stable_hold_sec"),
        ({"allowed_sec": -0.5}, "allowed_sec"),
        ({"allowed_px": math.nan}, "allowed_px"),
        ({"minimum_valid_coverage_ratio": 1.5}, "minimum_valid_coverage_ratio"),
    ],
)
def test_judgment_rule_values_are_checked(change, field):
    glass = make_recipe().glasses[0]
    glass = replace(glass, judgment_rule=replace(glass.judgment_rule, **change))
    assert fields_of(make_recipe(glasses=(glass,))) == [f"judgment_rule.{field}"]


def test_zero_allowances_are_valid():
    glass = make_recipe().glasses[0]
    rule = JudgmentRule(mode=JudgmentMode.HOLD_ABOVE_ZERO, allowed_sec=0.0, allowed_px=0.0)
    assert recipe_problems(make_recipe(glasses=(replace(glass, judgment_rule=rule),))) == []


def test_frame_size_match():
    recipe = make_recipe()
    assert recipe.matches_frame_size(1280, 720)
    assert not recipe.matches_frame_size(1920, 1080)
    assert recipe.frame_size_message(1280, 720) is None
    assert recipe.frame_size_message(1920, 1080) == "영상 해상도 1920×1080가 이 Recipe의 1280×720와 다릅니다."
