from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import numpy as np

from oil_tracker.adapters.storage.redetection_workspace import RedetectionWorkspace
from oil_tracker.domain.detection import BoundaryCandidate, PhaseDetection
from oil_tracker.domain.enums import BoundaryKind, FillState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.redetection import (
    RedetectionPolicy,
    RedetectionSample,
)
from redetection_fixtures import make_tracking


def _recipe():
    recipe = InspectionRecipe.empty(320, 240, "workspace")
    glass = InspectionRecipe.default_glass(320, 240)
    glass.id = "glass-1"
    recipe.glasses = [glass]
    return recipe, glass


def _detection(glass_id: str, index: int):
    candidate = BoundaryCandidate(
        source="fixture",
        kind=BoundaryKind.OIL_AIR,
        y=100.0 + index,
        feature_score=0.8,
        final_score=0.8,
        selected=True,
    )
    return PhaseDetection(
        glass_id=glass_id,
        frame_index=index,
        time_sec=float(index),
        fill_state=FillState.PARTIAL_VISIBLE,
        oil_air_level_y=100.0 + index,
        oil_air_level_px_from_zero=10.0,
        oil_air_level_mm_from_zero=2.5,
        overall_confidence=0.8,
        candidates=[candidate],
    )


def _sample(index: int, record_id: str):
    tracking = make_tracking(index, float(index))
    return RedetectionSample(
        nominal_timestamp_sec=float(index),
        requested_timestamp_sec=float(index),
        actual_timestamp_sec=float(index),
        frame_index=index,
        tracking_sample=tracking,
        fill_state=tracking.fill_state,
        confidence=tracking.overall_confidence,
        is_valid=tracking.is_valid,
        flags=(),
        selected_candidate=None,
        debug_record_id=record_id,
    )


def _write(workspace, glass, index):
    image = np.full((32, 48, 3), index, dtype=np.uint8)
    artifacts = SimpleNamespace(
        images={"overlay": image, "original_roi": image},
        state={"index": index},
    )
    record_id = workspace.write_detection(
        glass,
        _detection(glass.id, index),
        artifacts,
    )
    workspace.append_sample(_sample(index, record_id))
    return record_id


def test_workspace_roots_are_unique_and_outside_official_bundle(tmp_path):
    bundle = tmp_path / "official-result"
    bundle.mkdir()
    sentinel = bundle / "tracking_data.csv"
    sentinel.write_text("official", encoding="utf-8")
    recipe, _glass = _recipe()
    first = RedetectionWorkspace.create(recipe, temporary_parent=tmp_path)
    second = RedetectionWorkspace.create(recipe, temporary_parent=tmp_path)
    try:
        assert first.root != second.root
        assert bundle not in first.root.parents
        assert sentinel.read_text(encoding="utf-8") == "official"
        assert list(bundle.iterdir()) == [sentinel]
    finally:
        first.cleanup()
        second.cleanup()


def test_workspace_streams_jsonl_and_builds_lazy_index(tmp_path):
    recipe, glass = _recipe()
    workspace = RedetectionWorkspace.create(recipe, temporary_parent=tmp_path)
    record_ids = [_write(workspace, glass, index) for index in range(1, 4)]
    assert workspace.sample_path.read_text(encoding="utf-8").count("\n") == 3
    assert not workspace.index_path.exists()
    repository = workspace.finalize()
    try:
        assert workspace.index_path.is_file()
        assert repository.record_load_count == 0
        assert repository.image_load_count == 0
        assert [item.record_id for item in repository.summaries("glass-1")] == record_ids
        record = repository.load_record(record_ids[0])
        assert repository.record_load_count == 1
        assert repository.load_image(record, "overlay").shape == (32, 48, 3)
        assert repository.image_load_count == 1
    finally:
        root = workspace.root
        workspace.cleanup()
        assert not root.exists()


def test_workspace_record_and_image_caches_are_bounded(tmp_path):
    recipe, glass = _recipe()
    policy = RedetectionPolicy(record_cache_size=2, image_cache_size=1)
    workspace = RedetectionWorkspace.create(
        recipe,
        policy=policy,
        temporary_parent=tmp_path,
    )
    record_ids = [_write(workspace, glass, index) for index in range(1, 5)]
    repository = workspace.finalize()
    try:
        for record_id in record_ids:
            record = repository.load_record(record_id)
            repository.load_image(record, "overlay")
        assert len(repository._record_cache) == 2
        assert len(repository._image_cache) == 1
    finally:
        workspace.cleanup()


def test_cleanup_before_finalize_removes_partial_files(tmp_path):
    recipe, glass = _recipe()
    workspace = RedetectionWorkspace.create(recipe, temporary_parent=tmp_path)
    _write(workspace, glass, 1)
    root = workspace.root
    workspace.cleanup()
    assert not root.exists()
    workspace.cleanup()


def test_new_workspace_does_not_reuse_previous_run_namespace(tmp_path):
    recipe, glass = _recipe()
    first = RedetectionWorkspace.create(recipe, temporary_parent=tmp_path)
    first_id = _write(first, glass, 1)
    first.finalize()
    first_root = first.root
    first.cleanup()
    second = RedetectionWorkspace.create(recipe, temporary_parent=tmp_path)
    try:
        second_id = _write(second, glass, 1)
        second.finalize()
        assert second.root != first_root
        assert second.run_id != first.run_id
        assert second_id == first_id
        assert second.repository.load_record(second_id).run_id == second.run_id
    finally:
        second.cleanup()
