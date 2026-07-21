from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import json
from pathlib import Path

import numpy as np
import pytest

from oil_tracker.adapters.storage.json_truth_repository import sha256_file
from oil_tracker.adapters.storage.regression_fixture_exporter import (
    FrameIdentityPolicy,
    RegressionFixtureExportCancelled,
    RegressionFixtureExportError,
    RegressionFixtureExporter,
    ensure_fixture_destination_safe,
)
from oil_tracker.application.services.analysis_pipeline import SimpleCancellationToken
from oil_tracker.domain.debug_trace import DebugTraceRecord
from oil_tracker.domain.user_truth import TruthDisposition, TruthErrorType
from user_truth_fixtures import (
    FakeVideoReader,
    make_truth_bundle,
    make_truth_set_and_annotation,
    snapshot_tree,
)


FIXED_TIME = datetime(2026, 7, 21, 1, 2, 3, tzinfo=timezone.utc)


def _exporter(reader, *, clock=lambda: FIXED_TIME):
    return RegressionFixtureExporter(lambda _path: reader, clock=clock)


def test_fixture_export_writes_machine_readable_atomic_dataset(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    truth_set, annotation, _service = make_truth_set_and_annotation(bundle)
    reader = FakeVideoReader(bundle.source_video_path)
    destination = tmp_path / "Unicode 출력"
    result = _exporter(reader).export(
        bundle,
        truth_set,
        (annotation,),
        destination,
        source_video_path=bundle.source_video_path,
    )
    assert result.fixture_count == 1
    assert result.decoded_frame_count == 1
    assert result.dataset_path.name == "oil_regression_dataset_20260721_010203"
    assert reader.requests == [2.0]
    assert reader.closed
    assert not list(destination.glob(".*.tmp-*"))

    dataset = json.loads((result.dataset_path / "dataset_manifest.json").read_text(encoding="utf-8"))
    assert dataset["dataset_schema_version"] == 1
    assert dataset["status"] == "complete"
    assert dataset["fixture_count"] == 1
    assert dataset["disposition_counts"] == {"corrected": 1}
    assert dataset["error_type_counts"] == {"wrong_candidate": 1}
    assert dataset["numeric_truth_usable_count"] == 1
    assert dataset["unusable_count"] == 0
    assert dataset["decoded_frame_count"] == 1
    fixture_path = result.dataset_path / dataset["fixtures"][0]["path"]
    expected_files = {
        "fixture_manifest.json",
        "frame.png",
        "roi_crop.png",
        "truth.json",
        "official_reference.json",
        "recipe_snapshot.oilrecipe",
        "session_snapshot.json",
    }
    assert expected_files <= {path.name for path in fixture_path.iterdir()}
    fixture = json.loads((fixture_path / "fixture_manifest.json").read_text(encoding="utf-8"))
    assert fixture["fixture_schema_version"] == 1
    assert fixture["decoded_frame_index"] == 60
    assert fixture["decoded_timestamp_sec"] == 2.0
    assert fixture["frame_width"] == 320
    assert fixture["frame_height"] == 240
    assert fixture["annotation_id"] == annotation.annotation_id
    assert fixture["annotation_revision"] == annotation.revision
    assert fixture["relative_files"] == sorted(fixture["relative_files"])
    assert fixture["sha256"]["frame.png"] == sha256_file(fixture_path / "frame.png")
    assert fixture["sha256"]["truth.json"] == sha256_file(fixture_path / "truth.json")
    truth = json.loads((fixture_path / "truth.json").read_text(encoding="utf-8"))
    assert truth["truth_schema_version"] == 1
    assert truth["oil"]["source_frame_y"] == 128.0
    assert truth["oil"]["roi_local_y"] == 128.0 - fixture["roi_crop_origin"]["y"]
    assert truth["usable_numeric_truth"]
    official = json.loads((fixture_path / "official_reference.json").read_text(encoding="utf-8"))
    assert official["official_reference"]["frame_index"] == 60
    assert official["official_reference"]["fill_state"] == "PARTIAL_VISIBLE"


def test_fixture_id_is_deterministic_and_revision_sensitive(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    _truth_set, annotation, _service = make_truth_set_and_annotation(bundle)
    exporter = RegressionFixtureExporter()
    first = exporter.deterministic_fixture_id(bundle, annotation)
    assert first == exporter.deterministic_fixture_id(bundle, annotation)
    assert first.startswith("glass-1-")
    assert first != exporter.deterministic_fixture_id(bundle, replace(annotation, revision=annotation.revision + 1))


def test_export_supports_selected_and_all_annotation_sequences(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    truth_set, annotation, _service = make_truth_set_and_annotation(bundle)
    second = replace(
        annotation,
        annotation_id="annotation-2",
        frame_index=-1,
        requested_timestamp_sec=2.0,
        actual_decoded_timestamp_sec=2.0,
        disposition=TruthDisposition.UNUSABLE,
        truth_fill_state=None,
        oil_boundary=None,
        foam_front=None,
        foam_present=False,
        error_types=(TruthErrorType.VIDEO_UNUSABLE,),
    )
    truth_set.upsert(second)
    selected_reader = FakeVideoReader(bundle.source_video_path)
    selected = _exporter(selected_reader).export(
        bundle,
        truth_set,
        (annotation,),
        tmp_path / "selected",
        source_video_path=bundle.source_video_path,
    )
    assert selected.fixture_count == 1
    all_reader = FakeVideoReader(bundle.source_video_path)
    all_result = RegressionFixtureExporter(
        lambda _path: all_reader,
        clock=lambda: datetime(2026, 7, 21, 1, 2, 4, tzinfo=timezone.utc),
    ).export(
        bundle,
        truth_set,
        truth_set.sorted_annotations(),
        tmp_path / "all",
        source_video_path=bundle.source_video_path,
    )
    dataset = json.loads((all_result.dataset_path / "dataset_manifest.json").read_text(encoding="utf-8"))
    assert all_result.fixture_count == 2
    assert dataset["unusable_count"] == 1
    assert dataset["numeric_truth_usable_count"] == 1


def test_official_reference_null_is_explicit(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    truth_set, annotation, _service = make_truth_set_and_annotation(bundle)
    annotation = replace(
        annotation,
        official_tracking_reference=None,
        official_debug_record_id=None,
    )
    truth_set.annotations[:] = [annotation]
    result = _exporter(FakeVideoReader(bundle.source_video_path)).export(
        bundle,
        truth_set,
        (annotation,),
        tmp_path / "null-official",
        source_video_path=bundle.source_video_path,
    )
    fixture = next((result.dataset_path / "fixtures").iterdir())
    payload = json.loads((fixture / "official_reference.json").read_text(encoding="utf-8"))
    assert payload["official_reference"] is None
    assert payload["reason"]


class _DebugRepository:
    def __init__(self):
        self.record = DebugTraceRecord(
            schema_version=1,
            record_id="debug-1",
            run_id="run-truth-1",
            glass_id="glass-1",
            glass_name="관찰창 1",
            frame_index=60,
            timestamp_sec=2.0,
            capture_reasons=("low_confidence",),
            fill_state="PARTIAL_VISIBLE",
            confidence={"overall": 0.8},
            flags=("LOW_CONFIDENCE",),
            positions={"oil": 130.0},
            state={"selected": 0},
            candidates=({"y": 130.0},),
            images={"overlay": "overlay.png", "normalized": "missing.png"},
        )
        self.loaded = []

    def load_record(self, record_id):
        assert record_id == "debug-1"
        return self.record

    def load_image(self, record, key):
        self.loaded.append(key)
        if key == "normalized":
            raise OSError("missing artifact")
        return np.full((20, 30, 3), 123, dtype=np.uint8)


def test_official_debug_is_lazy_optional_and_missing_artifact_is_warning(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    truth_set, annotation, _service = make_truth_set_and_annotation(bundle)
    annotation = replace(annotation, official_debug_record_id="debug-1")
    truth_set.annotations[:] = [annotation]
    debug = _DebugRepository()
    assert debug.loaded == []
    result = _exporter(FakeVideoReader(bundle.source_video_path)).export(
        bundle,
        truth_set,
        (annotation,),
        tmp_path / "debug",
        source_video_path=bundle.source_video_path,
        debug_repository=debug,
    )
    assert debug.loaded == ["overlay", "normalized"]
    fixture = next((result.dataset_path / "fixtures").iterdir())
    assert (fixture / "official_debug" / "detection_debug.json").is_file()
    assert (fixture / "official_debug" / "overlay.png").is_file()
    assert not (fixture / "official_debug" / "normalized.png").exists()
    manifest = json.loads((fixture / "fixture_manifest.json").read_text(encoding="utf-8"))
    assert "official_debug/overlay.png" in manifest["official_debug_files"]
    assert any("normalized" in warning for warning in manifest["warnings"])


def test_debug_trace_absence_does_not_block_core_fixture(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    truth_set, annotation, _service = make_truth_set_and_annotation(bundle)
    result = _exporter(FakeVideoReader(bundle.source_video_path)).export(
        bundle,
        truth_set,
        (annotation,),
        tmp_path / "no-debug",
        source_video_path=bundle.source_video_path,
        debug_repository=None,
    )
    fixture = next((result.dataset_path / "fixtures").iterdir())
    assert not (fixture / "official_debug").exists()


def test_frame_identity_mismatch_fails_atomically_and_closes_reader(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    truth_set, annotation, _service = make_truth_set_and_annotation(bundle)
    reader = FakeVideoReader(bundle.source_video_path, frame_index=61, timestamp=2.0)
    destination = tmp_path / "mismatch"
    with pytest.raises(RegressionFixtureExportError, match="frame identity"):
        _exporter(reader).export(
            bundle,
            truth_set,
            (annotation,),
            destination,
            source_video_path=bundle.source_video_path,
        )
    assert reader.closed
    assert not list(destination.glob("oil_regression_dataset_*"))
    assert not list(destination.glob(".*.tmp-*"))


def test_timestamp_mismatch_uses_named_fps_policy(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    truth_set, annotation, _service = make_truth_set_and_annotation(bundle)
    policy = FrameIdentityPolicy()
    assert policy.timestamp_tolerance(30.0) == pytest.approx(0.02)
    reader = FakeVideoReader(bundle.source_video_path, timestamp=2.05)
    with pytest.raises(RegressionFixtureExportError, match="frame identity"):
        RegressionFixtureExporter(
            lambda _path: reader,
            frame_policy=policy,
            clock=lambda: FIXED_TIME,
        ).export(
            bundle,
            truth_set,
            (annotation,),
            tmp_path / "timestamp-mismatch",
            source_video_path=bundle.source_video_path,
        )


def test_source_missing_and_resolution_mismatch_are_rejected(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    truth_set, annotation, _service = make_truth_set_and_annotation(bundle)
    with pytest.raises(RegressionFixtureExportError, match="원본 영상"):
        RegressionFixtureExporter().export(
            bundle,
            truth_set,
            (annotation,),
            tmp_path / "missing",
            source_video_path=None,
        )
    reader = FakeVideoReader(bundle.source_video_path, width=640)
    with pytest.raises(RegressionFixtureExportError, match="해상도"):
        _exporter(reader).export(
            bundle,
            truth_set,
            (annotation,),
            tmp_path / "resolution",
            source_video_path=bundle.source_video_path,
        )
    assert reader.closed


def test_export_cancellation_cleans_temp_and_keeps_truth_and_bundle_unchanged(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    before_bundle = snapshot_tree(bundle.root)
    truth_set, annotation, _service = make_truth_set_and_annotation(bundle)
    before_truth = truth_set.to_dict()
    token = SimpleCancellationToken()
    token.cancel()
    destination = tmp_path / "cancel"
    with pytest.raises(RegressionFixtureExportCancelled):
        _exporter(FakeVideoReader(bundle.source_video_path)).export(
            bundle,
            truth_set,
            (annotation,),
            destination,
            source_video_path=bundle.source_video_path,
            cancellation=token,
        )
    assert snapshot_tree(bundle.root) == before_bundle
    assert truth_set.to_dict() == before_truth
    assert not list(destination.glob("oil_regression_dataset_*"))
    assert not list(destination.glob(".*.tmp-*"))


def test_export_keeps_official_bundle_and_active_truth_file_unchanged(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    truth_set, annotation, _service = make_truth_set_and_annotation(bundle)
    truth_path = tmp_path / "active.oiltruth"
    truth_path.write_text("active truth bytes", encoding="utf-8")
    before_bundle = snapshot_tree(bundle.root)
    before_truth = truth_path.read_bytes()
    _exporter(FakeVideoReader(bundle.source_video_path)).export(
        bundle,
        truth_set,
        (annotation,),
        tmp_path / "external",
        source_video_path=bundle.source_video_path,
        active_truth_path=truth_path,
    )
    assert snapshot_tree(bundle.root) == before_bundle
    assert truth_path.read_bytes() == before_truth


def test_fixture_destination_safety_rejects_bundle_truth_source_and_file(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    truth = tmp_path / "active.oiltruth"
    truth.touch()
    source = Path(bundle.source_video_path)
    for destination in (bundle.root, bundle.root / "child", truth, source):
        with pytest.raises(RegressionFixtureExportError):
            ensure_fixture_destination_safe(
                bundle.root,
                destination,
                active_truth_path=truth,
                source_video_path=source,
            )
    regular_file = tmp_path / "not-directory"
    regular_file.touch()
    with pytest.raises(RegressionFixtureExportError, match="폴더"):
        ensure_fixture_destination_safe(bundle.root, regular_file)


def test_fixture_destination_rejects_symlink_alias_and_existing_dataset(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    alias = tmp_path / "bundle-alias"
    try:
        alias.symlink_to(bundle.root, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlink is unavailable")
    with pytest.raises(RegressionFixtureExportError, match="bundle 내부"):
        ensure_fixture_destination_safe(bundle.root, alias / "dataset")

    truth_set, annotation, _service = make_truth_set_and_annotation(bundle)
    destination = tmp_path / "existing"
    existing = destination / "oil_regression_dataset_20260721_010203"
    existing.mkdir(parents=True)
    with pytest.raises(RegressionFixtureExportError, match="덮어쓸"):
        _exporter(FakeVideoReader(bundle.source_video_path)).export(
            bundle,
            truth_set,
            (annotation,),
            destination,
            source_video_path=bundle.source_video_path,
        )
    assert existing.is_dir()


def test_export_rejects_annotation_not_in_active_set(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    truth_set, annotation, _service = make_truth_set_and_annotation(bundle)
    foreign = replace(annotation, annotation_id="foreign")
    with pytest.raises(RegressionFixtureExportError, match="없는 annotation"):
        _exporter(FakeVideoReader(bundle.source_video_path)).export(
            bundle,
            truth_set,
            (foreign,),
            tmp_path / "foreign",
            source_video_path=bundle.source_video_path,
        )
