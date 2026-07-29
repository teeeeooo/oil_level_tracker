from __future__ import annotations

from dataclasses import asdict
import math

import numpy as np
import pytest

from foam_benchmark_fixtures import controlled_scenes as controlled_foam_scenes
from oil_benchmark_fixtures import controlled_oil_scenes
from oil_observability_fixtures import single_frame_observability_collisions
from oil_tracker.adapters.vision.geometry_masks import build_mask_bundle
import oil_tracker.adapters.vision.oil_shadow_observations as observations
from oil_tracker.adapters.vision.oil_shadow_pipeline import OilHypothesisPipeline
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.adapters.vision.preprocessing import preprocess
from oil_tracker.domain.geometry import EllipseGeometry
from oil_tracker.domain.recipe import InspectionRecipe


def _scalar_row_plateau_support(values: np.ndarray) -> float:
    """Exact test-only copy of the ce1656df parent implementation."""

    row = values.astype(np.float64)
    if row.size < 5:
        return 0.0
    differences = np.diff(row)
    magnitudes = np.abs(differences)
    total_variation = float(np.sum(magnitudes))
    if total_variation <= 1e-12:
        return 0.0

    edge_indices = np.argsort(magnitudes)[-min(6, magnitudes.size) :]
    localized = 0.0
    for edge_index in edge_indices:
        split = int(edge_index) + 1
        localized = max(
            localized,
            observations._localized_component_support(
                abs(float(np.mean(row[:split]) - np.mean(row[split:]))),
                float(magnitudes[edge_index]),
                float(magnitudes[edge_index]) / total_variation,
            ),
        )

    for left_index, first_edge in enumerate(edge_indices):
        for second_edge in edge_indices[left_index + 1 :]:
            left, right = sorted((int(first_edge), int(second_edge)))
            if differences[left] * differences[right] >= 0.0:
                continue
            center_mean = float(np.mean(row[left + 1 : right + 1]))
            left_delta = center_mean - float(np.mean(row[: left + 1]))
            right_delta = center_mean - float(np.mean(row[right + 1 :]))
            if left_delta * right_delta <= 0.0:
                continue
            localized = max(
                localized,
                observations._localized_component_support(
                    min(abs(left_delta), abs(right_delta)),
                    min(float(magnitudes[left]), float(magnitudes[right])),
                    (float(magnitudes[left]) + float(magnitudes[right]))
                    / total_variation,
                ),
            )

    strongest_two = float(
        np.sum(np.sort(magnitudes)[-min(2, magnitudes.size) :])
    )
    distributed_fraction = max(0.0, 1.0 - strongest_two / total_variation)
    mean_variation = total_variation / max(1, row.size - 1)
    fine_texture = (
        min(1.0, (mean_variation / 4.5) ** 6)
        * distributed_fraction
    )
    return observations._unit(max(localized, fine_texture))


def _scalar_plateau_artifact(
    gray: np.ndarray,
    effective_mask: np.ndarray,
    center_y: float,
) -> float:
    effective = effective_mask > 0
    valid_rows = np.flatnonzero(np.any(effective, axis=1))
    if valid_rows.size == 0:
        return 0.0
    first_row = int(valid_rows[0])
    last_row = int(valid_rows[-1])
    roi_height = last_row - first_row + 1
    window_height = max(3, int(round(0.45 * roi_height)))
    center_gap = max(1, int(round(0.015 * roi_height)))
    center = min(last_row, max(first_row, int(round(center_y))))
    reference_width = max(
        int(np.count_nonzero(effective[row])) for row in valid_rows
    )
    if reference_width < 4:
        return 0.0

    minimum_run = max(3, int(math.ceil(0.25 * reference_width)))
    side_scores: list[float] = []
    for start, stop in (
        (
            max(first_row, center - center_gap - window_height),
            max(first_row, center - center_gap),
        ),
        (
            min(last_row + 1, center + center_gap),
            min(last_row + 1, center + center_gap + window_height),
        ),
    ):
        row_scores: list[float] = []
        for row in range(start, stop):
            columns = np.flatnonzero(effective[row])
            runs = (
                np.split(columns, np.flatnonzero(np.diff(columns) > 1) + 1)
                if columns.size
                else ()
            )
            run = max(runs, key=len) if runs else np.empty(0, dtype=np.int64)
            if run.size < minimum_run:
                row_scores.append(0.0)
                continue
            row_scores.append(
                _scalar_row_plateau_support(gray[row, run])
                * (run.size / reference_width)
            )
        side_scores.append(
            0.0 if not row_scores else float(np.mean(row_scores))
        )
    return observations._unit(max(side_scores, default=0.0))


def _prepared(frame: np.ndarray, ellipse: EllipseGeometry | None = None):
    glass = InspectionRecipe.default_glass(frame.shape[1], frame.shape[0])
    glass.id = "plateau-performance"
    if ellipse is not None:
        glass.geometry.ellipse = ellipse
    bundle = build_mask_bundle(frame, glass)
    prepared = preprocess(
        bundle.crop,
        bundle.effective_mask,
        glass.detector_settings,
    )
    return glass, bundle, prepared, OilHypothesisPipeline().bounds


def _semantic_hypotheses_with_scalar_plateau(
    proposals,
    raw,
    prepared,
    bundle,
    bounds,
):
    observation_by_id = {item.identity: item for item in raw}
    broad_profiles = observations._broad_profiles(
        prepared,
        bundle.effective_mask,
        bundle.exclusion_mask,
        bounds,
    )
    narrow_context = observations._narrow_context(
        prepared,
        bundle.effective_mask,
        bundle.ellipse_mask,
        bundle.exclusion_mask,
        None,
        bounds,
    )
    hypotheses = []
    for proposal in proposals:
        members = tuple(observation_by_id[item] for item in proposal.member_ids)
        broad = observations._broad_summary(proposal, broad_profiles, bounds)
        narrow = observations._narrow_summary(proposal, narrow_context, bounds)
        static_prior = observations._static_prior(narrow, broad, None, bounds)
        plateau = _scalar_plateau_artifact(
            prepared.gray,
            bundle.effective_mask,
            broad.transition_local_y,
        )
        hypotheses.append(
            observations._semantic_hypothesis(
                proposal,
                members,
                broad,
                narrow,
                static_prior,
                plateau,
                float(bundle.crop_origin[1]),
            )
        )
    return observations.semantic_deduplicate(tuple(hypotheses), bounds)


def _raw_and_proposals(frame: np.ndarray, ellipse: EllipseGeometry | None = None):
    _glass, bundle, prepared, bounds = _prepared(frame, ellipse)
    raw = observations.extract_raw_observations(
        prepared,
        bundle.effective_mask,
        crop_origin_y=float(bundle.crop_origin[1]),
        bounds=bounds,
    )
    proposals = observations.build_bounded_proposals(raw, bounds)
    return bundle, prepared, bounds, raw, proposals


def _coverage_frames() -> list[tuple[str, np.ndarray, EllipseGeometry | None]]:
    oil = {scene.case_id: scene for scene in controlled_oil_scenes()}
    foam = {scene.case_id: scene for scene in controlled_foam_scenes()}
    names = (
        "clear-upper",
        "rapid-filling-0",
        "full-no-interface",
        "reflection-only",
        "shimmer-only",
        "structural-plus-real",
        "glare-plus-real",
        "rim-line",
    )
    rows = [(name, oil[name].frame, None) for name in names]
    for name in (
        "white-foam",
        "variance-shimmer",
        "clipped-glare",
        "thin-line",
    ):
        rows.append((name, foam[name].frame, None))
    rows.append(("learned-static-overlap", foam["thin-line"].frame, None))
    rows.extend(
        (scene.case_id, scene.frame, scene.ellipse)
        for scene in single_frame_observability_collisions()
    )
    return rows


def _row_cases() -> tuple[np.ndarray, ...]:
    rng = np.random.default_rng(20260729)
    return (
        np.full(32, 90, dtype=np.uint8),
        np.array([50] * 12 + [220] * 12, dtype=np.uint8),
        np.array([50] * 8 + [220] * 8 + [50] * 8, dtype=np.uint8),
        np.tile(np.array([20, 220, 40, 200], dtype=np.uint8), 10),
        np.tile(np.array([0, 64], dtype=np.uint8), 24),
        np.array([30, 30, 180, 180, 30], dtype=np.uint8),
        rng.integers(0, 256, size=79, dtype=np.uint8),
        rng.integers(0, 256, size=160, dtype=np.uint8),
    )


@pytest.mark.parametrize("row", _row_cases())
def test_row_support_matches_parent_scalar_oracle_exactly(row: np.ndarray) -> None:
    assert observations._row_plateau_support(row) == _scalar_row_plateau_support(row)


def test_plateau_context_matches_scalar_oracle_across_controlled_matrix() -> None:
    for case_id, frame, ellipse in _coverage_frames():
        _glass, bundle, prepared, _bounds = _prepared(frame, ellipse)
        context = observations._build_plateau_evidence_context(
            prepared.gray,
            bundle.effective_mask,
        )
        for center in np.linspace(-4.0, prepared.gray.shape[0] + 4.0, 19):
            actual = observations._plateau_artifact_from_context(context, center)
            expected = _scalar_plateau_artifact(
                prepared.gray,
                bundle.effective_mask,
                center,
            )
            assert actual == expected, (case_id, center, expected, actual)


def test_plateau_context_handles_mask_geometry_matrix_exactly() -> None:
    rng = np.random.default_rng(735328)
    gray = rng.integers(0, 256, size=(96, 144), dtype=np.uint8)
    masks = []
    full = np.full(gray.shape, 255, dtype=np.uint8)
    masks.append(("wide", full))
    narrow = np.zeros_like(full)
    narrow[:, 58:86] = 255
    masks.append(("narrow", narrow))
    shifted = np.zeros_like(full)
    shifted[8:88, 20:112] = 255
    masks.append(("shifted", shifted))
    disconnected = shifted.copy()
    disconnected[:, 46:52] = 0
    disconnected[::3, 70:88] = 0
    masks.append(("disconnected", disconnected))
    sparse = np.zeros_like(full)
    sparse[10:86:2, 20:55] = 255
    sparse[11:86:4, 90:104] = 255
    masks.append(("sparse", sparse))
    short = np.zeros_like(full)
    short[:, 20:55] = 255
    short[25:60, 28:35] = 0
    masks.append(("near-minimum-run", short))

    for name, mask in masks:
        context = observations._build_plateau_evidence_context(gray, mask)
        for center in range(-5, gray.shape[0] + 6, 5):
            assert observations._plateau_artifact_from_context(
                context, float(center)
            ) == _scalar_plateau_artifact(gray, mask, float(center)), name


def test_semantic_hypotheses_match_parent_scalar_oracle_exactly() -> None:
    for case_id, frame, ellipse in _coverage_frames():
        bundle, prepared, bounds, raw, proposals = _raw_and_proposals(
            frame, ellipse
        )
        actual = observations.evaluate_semantic_hypotheses(
            proposals,
            raw,
            prepared,
            bundle.effective_mask,
            bundle.ellipse_mask,
            bundle.exclusion_mask,
            None,
            crop_origin_y=float(bundle.crop_origin[1]),
            bounds=bounds,
        )
        expected = _semantic_hypotheses_with_scalar_plateau(
            proposals,
            raw,
            prepared,
            bundle,
            bounds,
        )
        assert actual == expected, case_id


def test_candidate_rich_frame_builds_once_and_scans_each_row_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    scene = next(
        item for item in controlled_foam_scenes() if item.case_id == "white-foam"
    )
    bundle, prepared, bounds, raw, proposals = _raw_and_proposals(scene.frame)
    assert len(proposals) > 1
    original_build = observations._build_plateau_evidence_context
    original_support = observations._row_plateau_support
    build_calls = 0
    row_addresses: list[int] = []

    def counted_build(gray, mask):
        nonlocal build_calls
        build_calls += 1
        return original_build(gray, mask)

    def counted_support(values):
        row_addresses.append(int(values.__array_interface__["data"][0]))
        return original_support(values)

    monkeypatch.setattr(
        observations,
        "_build_plateau_evidence_context",
        counted_build,
    )
    monkeypatch.setattr(observations, "_row_plateau_support", counted_support)
    observations.evaluate_semantic_hypotheses(
        proposals,
        raw,
        prepared,
        bundle.effective_mask,
        bundle.ellipse_mask,
        bundle.exclusion_mask,
        None,
        crop_origin_y=float(bundle.crop_origin[1]),
        bounds=bounds,
    )

    assert build_calls == 1
    assert len(row_addresses) == len(set(row_addresses))
    assert len(row_addresses) <= prepared.gray.shape[0]


def test_no_proposals_skip_plateau_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    frame = np.full((240, 320, 3), 90, dtype=np.uint8)
    _glass, bundle, prepared, bounds = _prepared(frame)

    def fail_build(_gray, _mask):
        raise AssertionError("plateau context must not be built without proposals")

    monkeypatch.setattr(
        observations,
        "_build_plateau_evidence_context",
        fail_build,
    )
    assert observations.evaluate_semantic_hypotheses(
        (),
        (),
        prepared,
        bundle.effective_mask,
        bundle.ellipse_mask,
        bundle.exclusion_mask,
        None,
        crop_origin_y=float(bundle.crop_origin[1]),
        bounds=bounds,
    ) == ()


def test_context_is_read_only_input_independent_and_does_not_mutate() -> None:
    scene = next(
        item for item in controlled_oil_scenes() if item.case_id == "clear-upper"
    )
    _glass, bundle, prepared, _bounds = _prepared(scene.frame)
    gray_before = prepared.gray.copy()
    mask_before = bundle.effective_mask.copy()
    context = observations._build_plateau_evidence_context(
        prepared.gray,
        bundle.effective_mask,
    )
    assert context is not None
    assert not context.row_scores.flags.writeable
    assert not np.shares_memory(context.row_scores, prepared.gray)
    assert not np.shares_memory(context.row_scores, bundle.effective_mask)
    assert np.array_equal(prepared.gray, gray_before)
    assert np.array_equal(bundle.effective_mask, mask_before)


def test_debug_toggle_preserves_detection_semantics() -> None:
    scene = next(
        item for item in controlled_oil_scenes()
        if item.case_id == "structural-plus-real"
    )
    glass = InspectionRecipe.default_glass(320, 240)
    glass.id = "plateau-debug-parity"
    fast, fast_artifacts = OpenCvPhaseDetector().detect(
        scene.frame.copy(), glass, 0, scene.timestamp, debug=False
    )
    glass = InspectionRecipe.default_glass(320, 240)
    glass.id = "plateau-debug-parity"
    debugged, debug_artifacts = OpenCvPhaseDetector().detect(
        scene.frame.copy(), glass, 0, scene.timestamp, debug=True
    )
    assert fast_artifacts is None
    assert debug_artifacts is not None
    assert asdict(fast) == asdict(debugged)


def test_identical_rows_reuse_support_only_within_each_frame(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gray = np.tile(
        np.array([30] * 24 + [210] * 24, dtype=np.uint8),
        (40, 1),
    )
    mask = np.full(gray.shape, 255, dtype=np.uint8)
    original = observations._row_plateau_support
    calls = 0

    def counted(values):
        nonlocal calls
        calls += 1
        return original(values)

    monkeypatch.setattr(observations, "_row_plateau_support", counted)
    first = observations._build_plateau_evidence_context(gray, mask)
    assert first is not None
    assert calls == 1
    second = observations._build_plateau_evidence_context(gray, mask)
    assert second is not None
    assert calls == 2
    assert first is not second
    assert not np.shares_memory(first.row_scores, second.row_scores)
