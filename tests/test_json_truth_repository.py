from __future__ import annotations

import json
from pathlib import Path

import pytest

from oil_tracker.adapters.storage import json_truth_repository as repository_module
from oil_tracker.adapters.storage.json_truth_repository import (
    JsonTruthRepository,
    TruthIdentityMismatchError,
    TruthRepositoryError,
    build_truth_bundle_identity,
    ensure_truth_destination_outside_bundle,
)
from oil_tracker.domain.user_truth import TruthBundleIdentity
from user_truth_fixtures import (
    make_truth_bundle,
    make_truth_set_and_annotation,
    snapshot_tree,
)


def test_oiltruth_round_trip_extension_unicode_and_schema(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    truth_set, annotation, _service = make_truth_set_and_annotation(bundle)
    repository = JsonTruthRepository()
    destination = tmp_path / "정답 자료" / "압축기 유면 정답"
    path = repository.save(
        destination,
        truth_set,
        bundle_root=bundle.root,
        bundle=bundle,
    )
    assert path.suffix == ".oiltruth"
    assert path.name == "압축기 유면 정답.oiltruth"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert payload["annotation_set_id"] == truth_set.annotation_set_id
    assert payload["annotations"][0]["annotation_id"] == annotation.annotation_id
    loaded = repository.load(
        path,
        expected_identity=build_truth_bundle_identity(bundle),
        bundle=bundle,
    )
    assert loaded.path == path.resolve()
    assert loaded.warnings == ()
    assert loaded.truth_set.to_dict() == truth_set.to_dict()


def test_truth_repository_same_bundle_metadata_difference_is_warning(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    truth_set, _annotation, _service = make_truth_set_and_annotation(bundle)
    repository = JsonTruthRepository()
    path = repository.save(tmp_path / "truth", truth_set, bundle_root=bundle.root, bundle=bundle)
    expected = build_truth_bundle_identity(bundle)
    warning_identity = TruthBundleIdentity(
        run_id=expected.run_id,
        recipe_id=expected.recipe_id,
        recipe_snapshot_hash=expected.recipe_snapshot_hash,
        source_video_basename="renamed.mp4",
        source_width=expected.source_width,
        source_height=expected.source_height,
        source_fps=29.0,
        source_duration_sec=expected.source_duration_sec,
    )
    result = repository.load(path, expected_identity=warning_identity)
    assert "원본 영상 파일명이 다릅니다." in result.warnings
    assert "원본 영상 FPS가 다릅니다." in result.warnings


def test_truth_repository_rejects_strict_bundle_identity_mismatch(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    truth_set, _annotation, _service = make_truth_set_and_annotation(bundle)
    repository = JsonTruthRepository()
    path = repository.save(tmp_path / "truth", truth_set, bundle_root=bundle.root, bundle=bundle)
    expected = build_truth_bundle_identity(bundle)
    mismatch = TruthBundleIdentity(
        run_id="other-run",
        recipe_id=expected.recipe_id,
        recipe_snapshot_hash=expected.recipe_snapshot_hash,
        source_video_basename=expected.source_video_basename,
        source_width=640,
        source_height=expected.source_height,
        source_fps=expected.source_fps,
        source_duration_sec=expected.source_duration_sec,
    )
    with pytest.raises(TruthIdentityMismatchError) as error:
        repository.load(path, expected_identity=mismatch)
    assert error.value.mismatches == ("분석 run ID", "기준 영상 해상도")


def test_truth_repository_overwrite_confirmation_contract(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    truth_set, _annotation, _service = make_truth_set_and_annotation(bundle)
    repository = JsonTruthRepository()
    path = repository.save(tmp_path / "truth", truth_set, bundle_root=bundle.root, bundle=bundle)
    original = path.read_bytes()
    calls = []
    with pytest.raises(TruthRepositoryError, match="취소"):
        repository.save(
            path,
            truth_set,
            bundle_root=bundle.root,
            bundle=bundle,
            confirm_overwrite=lambda candidate: calls.append(candidate) or False,
        )
    assert calls == [path]
    assert path.read_bytes() == original
    saved = repository.save(
        path,
        truth_set,
        bundle_root=bundle.root,
        bundle=bundle,
        confirm_overwrite=lambda candidate: candidate == path,
    )
    assert saved == path


@pytest.mark.parametrize(
    "text, match",
    [
        ("{", "JSON"),
        ('{"schema_version": 99}', "지원하지 않는"),
        ('{"schema_version": NaN}', "허용되지 않는"),
    ],
)
def test_truth_repository_rejects_malformed_unsupported_and_nonfinite_json(tmp_path, text, match):
    path = tmp_path / "bad.oiltruth"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(TruthRepositoryError, match=match):
        JsonTruthRepository().load(path)


def test_truth_repository_rejects_invalid_enum_and_coordinate(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    truth_set, _annotation, _service = make_truth_set_and_annotation(bundle)
    repository = JsonTruthRepository()
    path = repository.save(tmp_path / "truth", truth_set, bundle_root=bundle.root, bundle=bundle)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["annotations"][0]["disposition"] = "not-real"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(TruthRepositoryError, match="annotation"):
        repository.load(path)
    payload = truth_set.to_dict()
    payload["annotations"][0]["oil_boundary"]["source_frame_y"] = 1.0e9
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(TruthRepositoryError, match="타원 밖"):
        repository.load(path, bundle=bundle)


def test_truth_destination_rejects_bundle_root_descendant_and_nonexistent_descendant(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    with pytest.raises(TruthRepositoryError, match="bundle 내부"):
        ensure_truth_destination_outside_bundle(bundle.root, bundle.root)
    with pytest.raises(TruthRepositoryError, match="bundle 내부"):
        ensure_truth_destination_outside_bundle(bundle.root, bundle.root / "truth.oiltruth")
    with pytest.raises(TruthRepositoryError, match="bundle 내부"):
        ensure_truth_destination_outside_bundle(bundle.root, bundle.root / "new" / "truth.oiltruth")
    with pytest.raises(TruthRepositoryError, match="bundle 내부"):
        ensure_truth_destination_outside_bundle(bundle.root, bundle.files["recipe_snapshot"])


def test_truth_destination_rejects_symlink_alias_into_bundle(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    alias = tmp_path / "bundle-alias"
    try:
        alias.symlink_to(bundle.root, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlink is unavailable")
    with pytest.raises(TruthRepositoryError, match="bundle 내부"):
        ensure_truth_destination_outside_bundle(bundle.root, alias / "truth.oiltruth")


def test_atomic_failure_preserves_existing_file_and_cleans_partial_temp(tmp_path, monkeypatch):
    bundle = make_truth_bundle(tmp_path)
    truth_set, _annotation, _service = make_truth_set_and_annotation(bundle)
    repository = JsonTruthRepository()
    path = repository.save(tmp_path / "truth", truth_set, bundle_root=bundle.root, bundle=bundle)
    original = path.read_bytes()

    def fail_replace(_source, _destination):
        raise OSError("replace failed")

    monkeypatch.setattr(repository_module.os, "replace", fail_replace)
    with pytest.raises(TruthRepositoryError, match="replace failed"):
        repository.save(
            path,
            truth_set,
            bundle_root=bundle.root,
            bundle=bundle,
            overwrite=True,
        )
    assert path.read_bytes() == original
    assert not list(path.parent.glob(f".{path.name}.*.tmp"))


def test_truth_save_and_load_leave_official_bundle_byte_for_byte_unchanged(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    before = snapshot_tree(bundle.root)
    truth_set, _annotation, _service = make_truth_set_and_annotation(bundle)
    repository = JsonTruthRepository()
    path = repository.save(tmp_path / "외부" / "truth", truth_set, bundle_root=bundle.root, bundle=bundle)
    repository.load(path, expected_identity=build_truth_bundle_identity(bundle), bundle=bundle)
    assert snapshot_tree(bundle.root) == before
    assert path.resolve().is_relative_to(tmp_path.resolve())
    assert not path.resolve().is_relative_to(bundle.root.resolve())


def test_truth_repository_rejects_directory_destination(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    truth_set, _annotation, _service = make_truth_set_and_annotation(bundle)
    directory = tmp_path / "already.oiltruth"
    directory.mkdir()
    with pytest.raises(TruthRepositoryError, match="폴더"):
        JsonTruthRepository().save(
            directory,
            truth_set,
            bundle_root=bundle.root,
            bundle=bundle,
            overwrite=True,
        )
