from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
import shutil
from types import SimpleNamespace

import numpy as np
import pytest

from oil_tracker.adapters.storage.debug_trace_repository import DebugTraceError, DebugTraceRepository
from oil_tracker.adapters.storage.jsonl_debug_trace_writer import JsonlDebugTraceWriter
from oil_tracker.domain.debug_trace import DebugCaptureDecision, DebugCaptureReason
from oil_tracker.domain.detection import BoundaryCandidate, PhaseDetection
from oil_tracker.domain.enums import BoundaryKind, FillState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.session import DebugTraceLevel


def _glass(glass_id="유리/../A"):
    glass = InspectionRecipe.default_glass(320, 240, 1)
    glass.id = glass_id
    glass.name = "관찰창 한글"
    return glass


def _detection(glass_id, frame=10, time=1.25):
    candidate = BoundaryCandidate(
        source="sobel",
        kind=BoundaryKind.OIL_AIR,
        y=120.0,
        features={"local_y": np.float32(10.0), "bad": np.float64(float("nan"))},
        penalties={"jump": np.float32(0.1), "infinite": float("inf")},
        feature_score=np.float32(0.8),
        penalty=np.float32(0.1),
        final_score=np.float32(0.7),
        selected=True,
    )
    return PhaseDetection(
        glass_id=glass_id,
        frame_index=frame,
        time_sec=time,
        fill_state=FillState.PARTIAL_VISIBLE,
        oil_air_level_y=121.0,
        oil_air_level_px_from_zero=4.0,
        oil_air_level_mm_from_zero=None,
        foam_front_y=None,
        foam_front_px_from_zero=None,
        foam_front_mm_from_zero=None,
        oil_air_confidence=0.7,
        foam_confidence=0.0,
        visibility_confidence=0.8,
        overall_confidence=0.7,
        raw_oil_air_level_y=120.0,
        smoothed_oil_air_level_y=121.0,
        candidates=[candidate],
        flags=["LOW_CONFIDENCE"],
        debug_metrics={"glare_ratio": np.float32(0.2), "nonfinite": float("-inf")},
    )


def _artifacts(missing=False):
    image = np.full((12, 16), 127, dtype=np.uint8)
    images = {
        "overlay": np.dstack([image, image, image]),
        "original_roi": np.dstack([image, image, image]),
        "normalized": image,
        "sobel": image,
        "canny": image,
        "effective_mask": image,
        "glare_mask": image,
        "foam_mask": None if missing else image,
        "ellipse_mask": image,
    }
    return SimpleNamespace(images=images, state={"previous_state": "EMPTY_NO_INTERFACE", "proposed_state": "PARTIAL_VISIBLE"})


def _decision():
    return DebugCaptureDecision(True, (DebugCaptureReason.FIRST_SAMPLE, DebugCaptureReason.LOW_CONFIDENCE))


def _write(tmp_path: Path, level=DebugTraceLevel.BASIC, *, missing=False):
    tmp_path.mkdir(parents=True, exist_ok=True)
    glass = _glass()
    writer = JsonlDebugTraceWriter("run-한글", level, staging_parent=tmp_path)
    writer.write(glass, _detection(glass.id), _artifacts(missing), _decision())
    completion = writer.finalize()
    return glass, Path(completion.staging_directory)


def test_writer_emits_valid_independent_jsonl_and_utf8_byte_offsets(tmp_path):
    _glass_value, staging = _write(tmp_path)
    index = json.loads((staging / "debug_index.json").read_text(encoding="utf-8"))
    summary = index["records"][0]
    with (staging / "debug_trace.jsonl").open("rb") as handle:
        handle.seek(summary["byte_offset"])
        raw = handle.read(summary["byte_length"])
    record = json.loads(raw.decode("utf-8"))
    assert record["run_id"] == "run-한글"
    assert record["glass_name"] == "관찰창 한글"
    assert record["record_id"] == summary["record_id"]
    assert b"\n" not in raw


def test_writer_converts_numpy_and_nonfinite_values_to_json_safe_null(tmp_path):
    _glass_value, staging = _write(tmp_path)
    record = json.loads((staging / "debug_trace.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert record["candidates"][0]["features"]["local_y"] == 10.0
    assert record["candidates"][0]["features"]["bad"] is None
    assert record["candidates"][0]["penalties"]["infinite"] is None
    assert record["state"]["nonfinite"] is None


def test_basic_writes_only_required_subset_and_safe_paths(tmp_path):
    glass, staging = _write(tmp_path)
    record = json.loads((staging / "debug_trace.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert "ellipse_mask" not in record["images"]
    assert "overlay" in record["images"]
    for relative in record["images"].values():
        assert ".." not in Path(relative).parts
        assert glass.id not in relative
        assert (staging / relative).is_file()


def test_full_writes_all_available_artifacts(tmp_path):
    _glass_value, staging = _write(tmp_path, DebugTraceLevel.FULL)
    record = json.loads((staging / "debug_trace.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert "ellipse_mask" in record["images"]
    assert len(record["images"]) >= 8


def test_missing_optional_image_is_record_warning_not_writer_failure(tmp_path):
    _glass_value, staging = _write(tmp_path, missing=True)
    record = json.loads((staging / "debug_trace.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert "foam_mask" not in record["images"]
    assert "missing_optional_image:foam_mask" in record["warnings"]


def test_duplicate_glass_frame_timestamp_is_not_written_twice(tmp_path):
    glass = _glass("g1")
    writer = JsonlDebugTraceWriter("run-1", DebugTraceLevel.BASIC, staging_parent=tmp_path)
    detection = _detection(glass.id)
    writer.write(glass, detection, _artifacts(), _decision())
    writer.write(glass, detection, _artifacts(), _decision())
    completion = writer.finalize()
    index = json.loads((Path(completion.staging_directory) / "debug_index.json").read_text(encoding="utf-8"))
    assert index["record_count"] == 1
    assert len((Path(completion.staging_directory) / "debug_trace.jsonl").read_text(encoding="utf-8").splitlines()) == 1


def test_foam_candidate_uses_foam_episode_stage_not_oil_top_k(tmp_path):
    glass = _glass("g-foam")
    detection = _detection(glass.id)
    detection.candidates.append(
        BoundaryCandidate(
            source="foam_evidence",
            kind=BoundaryKind.FOAM_FRONT,
            y=90.0,
            features={"sequence_foam_eligible": 1.0},
            rejected=True,
        )
    )
    detection.flags.append("R7_FOAM_UNCONFIRMED")
    writer = JsonlDebugTraceWriter(
        "run-foam",
        DebugTraceLevel.BASIC,
        staging_parent=tmp_path,
    )
    writer.write(glass, detection, _artifacts(), _decision())
    writer.annotate_sequence(glass, (detection,))
    completion = writer.finalize()
    record = json.loads(
        Path(completion.staging_directory)
        .joinpath("debug_trace.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()[0]
    )
    foam = next(
        item
        for item in record["sequence"]["candidates"]
        if item["kind"] == "foam_front"
    )
    assert foam["sequence_foam_eligible"] == 1.0
    assert foam["reject_stage"] == "FOAM_EPISODE_UNCONFIRMED"


def test_sequence_annotation_preserves_raw_record_and_adds_final_authority(tmp_path):
    glass = _glass("g1")
    writer = JsonlDebugTraceWriter(
        "run-1",
        DebugTraceLevel.BASIC,
        staging_parent=tmp_path,
    )
    raw = _detection(glass.id)
    writer.write(glass, raw, _artifacts(), _decision())
    final_candidate = replace(
        raw.candidates[0],
        features={
            **raw.candidates[0].features,
            "sequence_initial_authority_tier": 2.0,
            "sequence_post_track_authority_tier": 2.0,
            "sequence_final_authority_tier": 3.0,
            "sequence_trajectory_support": 1.0,
            "sequence_cluster_support": 1.0,
            "sequence_selected": 1.0,
            "sequence_phase_identity": "direct_interface",
            "sequence_phase_identity_failed_gates": "",
            "sequence_track_opposition": 0.8,
            "sequence_effective_track_opposition": 0.2,
            "sequence_tracklet_id": "oil-tracklet:000000:0000",
            "sequence_row_hypothesis_id": "oil-row:000000:000",
            "sequence_tracklet_lifecycle": "confirmed",
            "sequence_tracklet_admitted": 1.0,
            "sequence_tracklet_confirmation_profile": "anchor_corridor",
            "sequence_tracklet_confirmation_support": 0.92,
            "sequence_tracklet_net_progress_px": 12.0,
            "sequence_tracklet_directional_agreement": 0.8,
            "sequence_tracklet_motion_support": 0.6,
            "sequence_tracklet_motion_coverage": 0.7,
            "sequence_tracklet_incompatible": 0.0,
            "sequence_tracklet_failure_reason": "",
        },
    )
    final = replace(
        raw,
        raw_oil_air_level_y=118.0,
        fill_state=FillState.DRAINING_VISIBLE,
        candidates=[final_candidate],
        flags=["SEQUENCE_RESOLVED_OIL"],
        debug_metrics={"sequence_resolved_kind": "oil"},
    )

    writer.annotate_sequence(glass, (final,))
    completion = writer.finalize()
    staging = Path(completion.staging_directory)
    record = json.loads(
        (staging / "debug_trace.jsonl").read_text(encoding="utf-8").splitlines()[0]
    )
    index = json.loads((staging / "debug_index.json").read_text(encoding="utf-8"))

    assert record["positions"]["raw_oil_y"] == 120.0
    assert record["sequence"]["positions"]["raw_oil_y"] == 118.0
    assert record["sequence"]["candidates"][0]["initial_authority"] == "CONTINUATION_ELIGIBLE"
    assert record["sequence"]["candidates"][0]["authority"] == "ANCHOR_ELIGIBLE"
    assert record["sequence"]["candidates"][0]["phase_identity"] == "direct_interface"
    assert record["sequence"]["candidates"][0]["track_opposition"] == 0.8
    assert record["sequence"]["candidates"][0]["effective_track_opposition"] == 0.2
    candidate = record["sequence"]["candidates"][0]
    assert candidate["component_id"] is None
    assert candidate["tracklet_id"] == "oil-tracklet:000000:0000"
    assert candidate["row_hypothesis_id"] == "oil-row:000000:000"
    assert candidate["tracklet_lifecycle"] == "confirmed"
    assert candidate["tracklet_confirmation_profile"] == "anchor_corridor"
    assert candidate["tracklet_net_progress_px"] == 12.0
    assert record["sequence"]["candidates"][0]["reject_stage"] == "ACCEPTED"
    assert index["records"][0]["fill_state"] == FillState.DRAINING_VISIBLE.value


def test_abort_removes_staging_directory(tmp_path):
    writer = JsonlDebugTraceWriter("run-1", DebugTraceLevel.BASIC, staging_parent=tmp_path)
    staging = writer.staging_directory
    writer.abort()
    assert not staging.exists()


def _repository_bundle(tmp_path: Path):
    glass, staging = _write(tmp_path)
    root = tmp_path / "bundle"
    (root / "debug").mkdir(parents=True)
    for source in staging.rglob("*"):
        target = root / "debug" / source.relative_to(staging)
        if source.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    recipe = InspectionRecipe.empty(320, 240, "review")
    recipe.glasses.append(glass)
    review_index = {
        "debug_trace_level": "basic",
        "debug_index": "debug/debug_index.json",
        "debug_trace": "debug/debug_trace.jsonl",
        "debug_record_count": 1,
    }
    return SimpleNamespace(
        root=root,
        run_id="run-한글",
        recipe=recipe,
        review_index=review_index,
        debug_trace_level="basic",
    )


def test_repository_loads_index_only_then_lazy_record_and_image(tmp_path):
    bundle = _repository_bundle(tmp_path)
    repository = DebugTraceRepository(bundle, record_cache_size=1, image_cache_size=1)
    assert repository.record_load_count == 0
    assert repository.image_load_count == 0
    summary = repository.index.records[0]
    record = repository.load_record(summary.record_id)
    assert repository.record_load_count == 1
    repository.load_record(summary.record_id)
    assert repository.record_load_count == 1
    image = repository.load_image(record, "overlay")
    assert image.shape[:2] == (12, 16)
    repository.load_image(record, "overlay")
    assert repository.image_load_count == 1


def test_repository_rejects_invalid_offset_and_unknown_glass(tmp_path):
    bundle = _repository_bundle(tmp_path)
    index_path = bundle.root / "debug" / "debug_index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    index["records"][0]["byte_offset"] = 10**9
    index_path.write_text(json.dumps(index), encoding="utf-8")
    with pytest.raises(DebugTraceError, match="offset"):
        DebugTraceRepository(bundle)

    bundle = _repository_bundle(tmp_path / "other")
    index_path = bundle.root / "debug" / "debug_index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    index["records"][0]["glass_id"] = "unknown"
    index_path.write_text(json.dumps(index), encoding="utf-8")
    with pytest.raises(DebugTraceError, match="없는 glass_id"):
        DebugTraceRepository(bundle)


def test_repository_rejects_unsupported_schema_and_path_traversal(tmp_path):
    bundle = _repository_bundle(tmp_path)
    index_path = bundle.root / "debug" / "debug_index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    index["schema_version"] = 99
    index_path.write_text(json.dumps(index), encoding="utf-8")
    with pytest.raises(DebugTraceError, match="지원하지 않는"):
        DebugTraceRepository(bundle)

    bundle = _repository_bundle(tmp_path / "other")
    bundle.review_index["debug_index"] = "../outside.json"
    with pytest.raises(DebugTraceError, match="상대경로|밖"):
        DebugTraceRepository(bundle)
