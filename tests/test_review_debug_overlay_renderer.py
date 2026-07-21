from __future__ import annotations

from types import SimpleNamespace

import numpy as np

from oil_tracker.adapters.vision.review_debug_overlay_renderer import (
    ReviewDebugOverlayRenderer,
    _dashed_line,
)
from oil_tracker.domain.recipe import InspectionRecipe


def _glass():
    glass = InspectionRecipe.default_glass(320, 240, 1)
    glass.geometry.zero_line_y = 140.0
    return glass


def _record(candidates=None, *, timestamp=2.0):
    return SimpleNamespace(
        timestamp_sec=timestamp,
        candidates=tuple(candidates or ()),
    )


def _candidate(y, *, rank, kind="oil_air", selected=False, rejected=False, score=0.5):
    return {
        "canonical_y": y,
        "rank": rank,
        "kind": kind,
        "selected": selected,
        "rejected": rejected,
        "final_score": score,
    }


def test_debug_renderer_distinguishes_selected_rejected_eligible_and_foam_candidates():
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    record = _record(
        (
            _candidate(100.0, rank=1, selected=True),
            _candidate(110.0, rank=2, rejected=True),
            _candidate(120.0, rank=3),
            _candidate(130.0, rank=4, kind="foam_front"),
        )
    )
    rendered = ReviewDebugOverlayRenderer().render(frame, _glass(), record, 2.012)
    for y in (100, 110, 120, 130):
        assert np.count_nonzero(rendered[y, 100:220]) > 0
    assert not np.array_equal(rendered[100, 100:220], rendered[110, 100:220])
    assert not np.array_equal(rendered[120, 100:220], rendered[130, 100:220])


def test_selected_line_is_solid_and_rejected_and_eligible_lines_are_dashed():
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    renderer = ReviewDebugOverlayRenderer()
    baseline = renderer.render(frame, _glass(), _record(), 2.0)
    selected_render = renderer.render(
        frame,
        _glass(),
        _record((_candidate(100.0, rank=1, selected=True),)),
        2.0,
    )
    selected_delta = np.any(
        selected_render[100, 125:210] != baseline[100, 125:210],
        axis=1,
    )
    assert selected_delta.sum() >= 70

    rejected_image = np.zeros((5, 120, 3), dtype=np.uint8)
    eligible_image = np.zeros((5, 120, 3), dtype=np.uint8)
    _dashed_line(rejected_image, (0, 2), (119, 2), (1, 2, 3), 1, dash=9, gap=6)
    _dashed_line(eligible_image, (0, 2), (119, 2), (1, 2, 3), 1, dash=3, gap=5)
    rejected = np.any(rejected_image[2] != 0, axis=1)
    eligible = np.any(eligible_image[2] != 0, axis=1)
    assert rejected.any() and not rejected.all()
    assert eligible.any() and not eligible.all()
    assert rejected.sum() > eligible.sum()


def test_highlight_changes_only_presentation_and_keeps_source_unchanged():
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    original = frame.copy()
    record = _record((_candidate(115.0, rank=1), _candidate(125.0, rank=2)))
    renderer = ReviewDebugOverlayRenderer()
    normal = renderer.render(frame, _glass(), record, 2.0)
    highlighted = renderer.render(frame, _glass(), record, 2.0, highlighted_candidate=1)
    assert np.array_equal(frame, original)
    assert not np.array_equal(normal, highlighted)
    assert np.count_nonzero(highlighted[125, 100:220]) > np.count_nonzero(normal[125, 100:220])


def test_invalid_and_outside_ellipse_candidate_y_values_are_skipped():
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    baseline = ReviewDebugOverlayRenderer().render(frame, _glass(), _record(), 2.0)
    record = _record(
        (
            _candidate(float("nan"), rank=1),
            _candidate(None, rank=2),
            _candidate(1.0, rank=3),
            _candidate(239.0, rank=4),
        )
    )
    rendered = ReviewDebugOverlayRenderer().render(frame, _glass(), record, 2.0)
    assert np.array_equal(rendered, baseline)


def test_timestamp_and_delta_context_are_rendered_without_official_final_overlay_mix():
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    record = _record((_candidate(115.0, rank=1, selected=True),), timestamp=2.0)
    renderer = ReviewDebugOverlayRenderer()
    first = renderer.render(frame, _glass(), record, 2.012)
    second = renderer.render(frame, _glass(), record, 2.112)
    baseline = renderer.render(frame, _glass(), _record(timestamp=2.0), 2.012)
    assert not np.array_equal(first, second)
    assert np.count_nonzero(first[10:78, 10:310]) > 0
    assert np.array_equal(first[160, 100:220], baseline[160, 100:220])


def test_debug_render_is_deterministic_and_preserves_source_resolution():
    frame = np.zeros((240, 320), dtype=np.uint8)
    record = _record((_candidate(115.0, rank=1, selected=True),))
    renderer = ReviewDebugOverlayRenderer()
    first = renderer.render(frame, _glass(), record, 2.01)
    second = renderer.render(frame, _glass(), record, 2.01)
    assert first.shape == (240, 320, 3)
    assert np.array_equal(first, second)
