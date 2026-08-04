from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

import pytest

from benchmark_fixtures import (
    export_benchmark_dataset,
    fixture_directory,
    read_json,
    rehash_dataset,
    write_catalog,
    write_json,
)
from oil_tracker.adapters.storage.regression_dataset_reader import (
    FilesystemRegressionDatasetReader,
    RegressionDatasetError,
    RegressionDatasetIntegrityError,
    UnsupportedRegressionDatasetSchema,
)
from oil_tracker.domain.detector_benchmark import BenchmarkCategory
from oil_tracker.domain.enums import FillState
from oil_tracker.domain.user_truth import TruthDisposition, TruthErrorType


def _refresh_dataset_manifest(dataset_root: Path, payload: dict) -> None:
    payload["dataset_content_hash"] = hashlib.sha256(
        json.dumps(
            payload["fixtures"],
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()
    write_json(dataset_root / "dataset_manifest.json", payload)


def test_valid_unicode_dataset_load_and_deterministic_fixture_order(tmp_path):
    dataset_root = export_benchmark_dataset(
        tmp_path / "유니코드 경로",
        timestamps=(3.0, 1.0, 2.0),
        foam_present=False,
    )
    loaded = FilesystemRegressionDatasetReader().load(dataset_root)
    assert loaded.schema_version == 1
    assert len(loaded.cases) == 3
    assert [case.case_id for case in loaded.cases] == sorted(
        case.case_id for case in loaded.cases
    )
    assert sorted(case.timestamp_sec for case in loaded.cases) == [1.0, 2.0, 3.0]
    assert all(case.category is BenchmarkCategory.CLEAR_OIL_BOUNDARY for case in loaded.cases)
    assert all(case.analysis_height_px > 0 for case in loaded.cases)
    assert loaded.fingerprint


def test_dataset_copy_has_identical_content_fingerprint(tmp_path):
    source = export_benchmark_dataset(tmp_path, label="원본")
    copied = tmp_path / "다른 폴더" / "복사 dataset"
    shutil.copytree(source, copied)
    reader = FilesystemRegressionDatasetReader()
    assert reader.load(source).fingerprint == reader.load(copied).fingerprint


def test_catalog_supplies_category_and_sequence_contract(tmp_path):
    dataset_root = export_benchmark_dataset(
        tmp_path, label="sequence", timestamps=(2.0, 1.0)
    )
    dataset = read_json(dataset_root / "dataset_manifest.json")
    fixtures = []
    for order, entry in enumerate(reversed(dataset["fixtures"])):
        fixtures.append(
            {
                "fixture_id": entry["fixture_id"],
                "category": "rapid_oil_flow",
                "sequence_id": "flow-01",
                "sequence_order": order,
            }
        )
    write_catalog(dataset_root, fixtures)
    loaded = FilesystemRegressionDatasetReader().load(dataset_root)
    assert loaded.catalog_present
    assert {case.category for case in loaded.cases} == {BenchmarkCategory.RAPID_OIL_FLOW}
    assert {case.sequence_id for case in loaded.cases} == {"flow-01"}


def test_unsupported_dataset_and_catalog_schema_are_explicit(tmp_path):
    dataset_root = export_benchmark_dataset(tmp_path, label="schema")
    manifest_path = dataset_root / "dataset_manifest.json"
    dataset = read_json(manifest_path)
    dataset["dataset_schema_version"] = 99
    write_json(manifest_path, dataset)
    with pytest.raises(UnsupportedRegressionDatasetSchema, match="unsupported dataset schema"):
        FilesystemRegressionDatasetReader().load(dataset_root)

    dataset["dataset_schema_version"] = 1
    write_json(manifest_path, dataset)
    entry = dataset["fixtures"][0]
    catalog = write_catalog(
        dataset_root,
        [{"fixture_id": entry["fixture_id"], "category": "clear_oil_boundary"}],
    )
    payload = read_json(catalog)
    payload["schema_version"] = 2
    write_json(catalog, payload)
    with pytest.raises(UnsupportedRegressionDatasetSchema, match="catalog schema"):
        FilesystemRegressionDatasetReader().load(dataset_root)


def test_missing_required_file_and_malformed_json_are_specific(tmp_path):
    dataset_root = export_benchmark_dataset(tmp_path, label="missing")
    fixture = fixture_directory(dataset_root)
    (fixture / "frame.png").unlink()
    with pytest.raises(RegressionDatasetError, match="required path is missing"):
        FilesystemRegressionDatasetReader().load(dataset_root)

    malformed = export_benchmark_dataset(tmp_path, label="malformed")
    (malformed / "dataset_manifest.json").write_text("{not-json", encoding="utf-8")
    with pytest.raises(RegressionDatasetError, match="JSON is malformed"):
        FilesystemRegressionDatasetReader().load(malformed)


def test_duplicate_case_id_and_duplicate_manifest_path_are_rejected(tmp_path):
    duplicate_id = export_benchmark_dataset(tmp_path, label="duplicate-id")
    payload = read_json(duplicate_id / "dataset_manifest.json")
    payload["fixtures"].append(dict(payload["fixtures"][0]))
    payload["fixture_count"] = 2
    _refresh_dataset_manifest(duplicate_id, payload)
    with pytest.raises(RegressionDatasetIntegrityError, match="duplicate fixture/case ID"):
        FilesystemRegressionDatasetReader().load(duplicate_id)

    duplicate_manifest = export_benchmark_dataset(tmp_path, label="duplicate-manifest")
    payload = read_json(duplicate_manifest / "dataset_manifest.json")
    second = dict(payload["fixtures"][0])
    second["fixture_id"] = "different-fixture-id"
    second["path"] = "different-fixture-path"
    payload["fixtures"].append(second)
    payload["fixture_count"] = 2
    _refresh_dataset_manifest(duplicate_manifest, payload)
    with pytest.raises(RegressionDatasetIntegrityError, match="duplicate manifest entry"):
        FilesystemRegressionDatasetReader().load(duplicate_manifest)


def test_unknown_or_unavailable_category_is_not_silently_other(tmp_path):
    unknown = export_benchmark_dataset(tmp_path, label="unknown-category")
    entry = read_json(unknown / "dataset_manifest.json")["fixtures"][0]
    write_catalog(
        unknown,
        [{"fixture_id": entry["fixture_id"], "category": "not-a-category"}],
    )
    with pytest.raises(RegressionDatasetError, match="unknown benchmark category"):
        FilesystemRegressionDatasetReader().load(unknown)

    ambiguous = export_benchmark_dataset(
        tmp_path,
        label="ambiguous-category",
        disposition=TruthDisposition.UNUSABLE,
        fill_state=None,
        oil_y=None,
        foam_present=False,
        error_types=(TruthErrorType.OTHER,),
        note="ambiguous",
    )
    with pytest.raises(RegressionDatasetError, match="benchmark_catalog.json"):
        FilesystemRegressionDatasetReader().load(ambiguous)


@pytest.mark.parametrize(
    ("kind", "expected_message"),
    [
        ("absolute", "absolute paths are not allowed"),
        ("traversal", "path traversal"),
    ],
)
def test_absolute_and_parent_traversal_fixture_paths_are_rejected(
    tmp_path, kind, expected_message
):
    dataset_root = export_benchmark_dataset(tmp_path, label=f"unsafe-{kind}")
    unsafe = (
        str((tmp_path / "outside-fixture").resolve())
        if kind == "absolute"
        else "../outside-fixture"
    )
    payload = read_json(dataset_root / "dataset_manifest.json")
    payload["fixtures"][0]["path"] = unsafe
    _refresh_dataset_manifest(dataset_root, payload)
    with pytest.raises(RegressionDatasetError, match=expected_message):
        FilesystemRegressionDatasetReader().load(dataset_root)


def test_root_escape_and_symlink_manifest_escape_are_rejected(tmp_path):
    dataset_root = export_benchmark_dataset(tmp_path, label="root-escape")
    outside = tmp_path / "outside-fixture"
    shutil.copytree(fixture_directory(dataset_root), outside)
    alias = dataset_root / "escape-alias"
    try:
        alias.symlink_to(outside, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlink is unavailable")
    payload = read_json(dataset_root / "dataset_manifest.json")
    payload["fixtures"][0]["path"] = "escape-alias"
    payload["fixtures"][0]["manifest"] = "escape-alias/fixture_manifest.json"
    _refresh_dataset_manifest(dataset_root, payload)
    with pytest.raises(RegressionDatasetError, match="escapes dataset root"):
        FilesystemRegressionDatasetReader().load(dataset_root)

    second = export_benchmark_dataset(tmp_path, label="manifest-symlink")
    fixture = fixture_directory(second)
    manifest = fixture / "fixture_manifest.json"
    outside_manifest = tmp_path / "outside-manifest.json"
    shutil.copyfile(manifest, outside_manifest)
    manifest.unlink()
    manifest.symlink_to(outside_manifest)
    with pytest.raises(RegressionDatasetError, match="escapes dataset root"):
        FilesystemRegressionDatasetReader().load(second)


def test_declared_hash_mismatch_is_rejected(tmp_path):
    dataset_root = export_benchmark_dataset(tmp_path, label="hash")
    frame = fixture_directory(dataset_root) / "frame.png"
    frame.write_bytes(frame.read_bytes() + b"tamper")
    with pytest.raises(RegressionDatasetIntegrityError, match="SHA-256 mismatch"):
        FilesystemRegressionDatasetReader().load(dataset_root)


@pytest.mark.parametrize(
    ("kind", "expected_message"),
    [
        ("recipe", "recipe snapshot hash mismatch"),
        ("session", "session source-frame identity mismatch"),
        ("frame", "truth and decoded frame index mismatch"),
    ],
)
def test_recipe_session_and_frame_identity_mismatch_are_rejected(
    tmp_path, kind, expected_message
):
    dataset_root = export_benchmark_dataset(tmp_path, label=f"identity-{kind}")
    fixture = fixture_directory(dataset_root)
    if kind == "recipe":
        path = fixture / "recipe_snapshot.oilrecipe"
        payload = read_json(path)
        payload["recipe_id"] = "different-recipe"
        write_json(path, payload)
    elif kind == "session":
        path = fixture / "session_snapshot.json"
        payload = read_json(path)
        payload["video_metadata"]["width"] += 1
        write_json(path, payload)
    else:
        path = fixture / "truth.json"
        payload = read_json(path)
        payload["frame_index"] += 1
        write_json(path, payload)
    rehash_dataset(dataset_root)
    with pytest.raises(RegressionDatasetIntegrityError, match=expected_message):
        FilesystemRegressionDatasetReader().load(dataset_root)


def test_unusable_reason_is_preserved_but_excluded_from_accuracy(tmp_path):
    dataset_root = export_benchmark_dataset(
        tmp_path,
        label="unusable",
        disposition=TruthDisposition.UNUSABLE,
        fill_state=None,
        oil_y=None,
        foam_present=False,
        error_types=(TruthErrorType.VIDEO_UNUSABLE,),
        note="motion blur",
    )
    case = FilesystemRegressionDatasetReader().load(dataset_root).cases[0]
    assert case.disposition is TruthDisposition.UNUSABLE
    assert "video_unusable" in case.unusable_reasons
    assert "note:motion blur" in case.unusable_reasons
    assert case.category is BenchmarkCategory.REFLECTION_OR_BLUR


def test_duplicate_json_manifest_key_is_rejected(tmp_path):
    dataset_root = export_benchmark_dataset(tmp_path, label="duplicate-key")
    manifest_path = dataset_root / "dataset_manifest.json"
    text = manifest_path.read_text(encoding="utf-8")
    text = text.replace('"dataset_id":', '"dataset_id": "duplicate",\n  "dataset_id":', 1)
    manifest_path.write_text(text, encoding="utf-8")
    with pytest.raises(RegressionDatasetError, match="duplicate JSON object key"):
        FilesystemRegressionDatasetReader().load(dataset_root)
