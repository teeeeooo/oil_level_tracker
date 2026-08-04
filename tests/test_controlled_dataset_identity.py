from __future__ import annotations

from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from uuid import UUID

import cv2
import numpy as np

from controlled_dataset_identity import (
    CONTROLLED_CONTRACT_VERSION,
    dataset_identity_summary,
    prepare_controlled_dataset_identity,
)
from foam_benchmark_fixtures import (
    generate_controlled_foam_dataset,
)
from oil_benchmark_fixtures import (
    _make_recipe_snapshot_base_compatible,
    controlled_oil_scenes,
    generate_controlled_oil_dataset,
)
from oil_observability_fixtures import (
    historical_glare_negatives,
    single_frame_observability_collisions,
)
from oil_tracker.adapters.storage.json_truth_repository import (
    build_truth_bundle_identity,
)
from oil_tracker.adapters.storage.regression_fixture_exporter import (
    RegressionFixtureExporter,
)
from oil_tracker.domain.user_truth import UserTruthSet
from user_truth_fixtures import (
    FakeVideoReader,
    make_truth_bundle,
    make_truth_set_and_annotation,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRECT_LOGICAL_ARRAY_SHA256 = (
    "0b434069a926093cdf2afd79f922f912ce8264b8fcbf3d85ed0569c35840e491"
)
EXPECTED_DIRECT_MANIFEST_SHA256 = (
    "9d49789d7b092dc5c0ef5c26e48b6d477dffcf02c0e0417970a0ea0fe1dcc7aa"
)


def test_controlled_oil_dataset_is_byte_reproducible_across_roots(tmp_path):
    first_path, first_scenes = generate_controlled_oil_dataset(tmp_path / "first")
    second_path, second_scenes = generate_controlled_oil_dataset(tmp_path / "second")
    first = dataset_identity_summary(first_path)
    second = dataset_identity_summary(second_path)

    assert len(first_scenes) == len(second_scenes) == 58
    assert first["case_count"] == second["case_count"] == 58
    assert first["sequence_count"] == second["sequence_count"] == 11
    _assert_complete_identity_equal(first, second)


def test_controlled_foam_dataset_is_byte_reproducible_across_roots(tmp_path):
    first_path, first_scenes = generate_controlled_foam_dataset(tmp_path / "first")
    second_path, second_scenes = generate_controlled_foam_dataset(tmp_path / "second")
    first = dataset_identity_summary(first_path)
    second = dataset_identity_summary(second_path)

    assert len(first_scenes) == len(second_scenes) == 16
    assert first["case_count"] == second["case_count"] == 16
    assert first["sequence_count"] == second["sequence_count"] == 2
    _assert_complete_identity_equal(first, second)


def test_oil_and_foam_controlled_identities_do_not_collide(tmp_path):
    oil_path, _ = generate_controlled_oil_dataset(tmp_path / "oil")
    foam_path, _ = generate_controlled_foam_dataset(tmp_path / "foam")
    oil = dataset_identity_summary(oil_path)
    foam = dataset_identity_summary(foam_path)

    assert oil["dataset_id"] != foam["dataset_id"]
    assert oil["annotation_set_id"] != foam["annotation_set_id"]
    assert oil["fingerprint"] != foam["fingerprint"]
    assert oil["tree_digest"] != foam["tree_digest"]
    UUID(oil["dataset_id"])
    UUID(foam["dataset_id"])


def test_controlled_datasets_reproduce_across_fresh_python_processes(tmp_path):
    for kind, expected_cases, expected_sequences in (
        ("oil", 58, 11),
        ("foam", 16, 2),
    ):
        first = _generate_in_subprocess(kind, tmp_path / f"{kind}-process-a")
        second = _generate_in_subprocess(kind, tmp_path / f"{kind}-process-b")
        assert first["case_count"] == second["case_count"] == expected_cases
        assert first["sequence_count"] == second["sequence_count"] == expected_sequences
        _assert_complete_identity_equal(first, second)


def test_reader_contract_and_integrity_payload_are_identical(tmp_path):
    first_path, _ = generate_controlled_oil_dataset(tmp_path / "reader-a")
    second_path, _ = generate_controlled_oil_dataset(tmp_path / "reader-b")
    first = dataset_identity_summary(first_path)
    second = dataset_identity_summary(second_path)

    assert first["fingerprint"] == second["fingerprint"]
    assert first["case_contract"] == second["case_contract"]
    assert first["fixture_ids"] == second["fixture_ids"]
    assert first["fixture_manifest_hashes"] == second["fixture_manifest_hashes"]


def test_production_default_truth_and_export_ids_remain_random(tmp_path):
    bundle = make_truth_bundle(tmp_path / "production")
    identity = build_truth_bundle_identity(bundle)
    assert UserTruthSet.create(identity).annotation_set_id != UserTruthSet.create(
        identity
    ).annotation_set_id

    truth_set, annotation, _service = make_truth_set_and_annotation(bundle)
    exporter = RegressionFixtureExporter(
        lambda _path: FakeVideoReader(bundle.source_video_path)
    )
    first = exporter.export(
        bundle,
        truth_set,
        (annotation,),
        tmp_path / "production-export-a",
        source_video_path=bundle.source_video_path,
    )
    second = exporter.export(
        bundle,
        truth_set,
        (annotation,),
        tmp_path / "production-export-b",
        source_video_path=bundle.source_video_path,
    )
    assert first.dataset_id != second.dataset_id
    UUID(first.dataset_id)
    UUID(second.dataset_id)


def test_injected_dataset_id_seam_is_explicit_and_local(tmp_path):
    bundle = make_truth_bundle(tmp_path / "explicit")
    truth_set, annotation, _service = make_truth_set_and_annotation(bundle)
    expected = "12c3e7a1-0ae4-55ca-aed0-77e65f79ec6b"
    result = RegressionFixtureExporter(
        lambda _path: FakeVideoReader(bundle.source_video_path),
        dataset_id_factory=lambda: expected,
    ).export(
        bundle,
        truth_set,
        (annotation,),
        tmp_path / "explicit-export",
        source_video_path=bundle.source_video_path,
    )
    manifest = json.loads(
        (result.dataset_path / "dataset_manifest.json").read_text(encoding="utf-8")
    )
    assert result.dataset_id == manifest["dataset_id"] == expected


def test_contract_version_and_raster_mutation_change_identity(tmp_path):
    version_one_path, _ = generate_controlled_oil_dataset(
        tmp_path / "version-one",
        contract_version=CONTROLLED_CONTRACT_VERSION,
    )
    version_two_path, _ = generate_controlled_oil_dataset(
        tmp_path / "version-two",
        contract_version="v2",
    )
    version_one = dataset_identity_summary(version_one_path)
    version_two = dataset_identity_summary(version_two_path)
    assert version_one["dataset_id"] != version_two["dataset_id"]
    assert version_one["fingerprint"] != version_two["fingerprint"]
    assert version_one["tree_digest"] != version_two["tree_digest"]

    original_scenes = controlled_oil_scenes()
    changed_frame = original_scenes[0].frame.copy()
    changed_frame[0, 0, 0] ^= np.uint8(1)
    changed_scenes = (
        replace(original_scenes[0], frame=changed_frame),
        *original_scenes[1:],
    )
    original_bundle = make_truth_bundle(tmp_path / "original-contract")
    changed_bundle = make_truth_bundle(tmp_path / "changed-contract")
    _make_recipe_snapshot_base_compatible(original_bundle)
    _make_recipe_snapshot_base_compatible(changed_bundle)
    from oil_benchmark_fixtures import FIXED_TIME

    original = prepare_controlled_dataset_identity(
        original_bundle,
        original_scenes,
        dataset_kind="oil",
        contract_version=CONTROLLED_CONTRACT_VERSION,
        fixed_time=FIXED_TIME,
    )
    changed = prepare_controlled_dataset_identity(
        changed_bundle,
        changed_scenes,
        dataset_kind="oil",
        contract_version=CONTROLLED_CONTRACT_VERSION,
        fixed_time=FIXED_TIME,
    )
    assert original.contract_digest != changed.contract_digest
    assert original.dataset_id != changed.dataset_id
    assert original.annotation_set_id != changed.annotation_set_id


def test_direct_fifty_frame_bundle_identity_remains_exact(tmp_path):
    frames, manifest = _direct_bundle_contract()
    npz_path = tmp_path / "direct_frames.npz"
    manifest_path = tmp_path / "direct_manifest.json"
    np.savez(npz_path, **frames)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True),
        encoding="utf-8",
        newline="\n",
    )

    assert len(manifest) == 50
    assert _logical_array_fingerprint(frames) == EXPECTED_DIRECT_LOGICAL_ARRAY_SHA256
    with np.load(npz_path, allow_pickle=False) as loaded:
        round_trip = {key: loaded[key] for key in loaded.files}
    assert _logical_array_fingerprint(round_trip) == EXPECTED_DIRECT_LOGICAL_ARRAY_SHA256
    assert (
        hashlib.sha256(manifest_path.read_bytes()).hexdigest()
        == EXPECTED_DIRECT_MANIFEST_SHA256
    )


def _logical_array_fingerprint(arrays) -> str:
    digest = hashlib.sha256()
    for key in sorted(arrays):
        array = np.ascontiguousarray(arrays[key])
        metadata = json.dumps(
            {"dtype": array.dtype.str, "key": key, "shape": list(array.shape)},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        content = array.tobytes(order="C")
        digest.update(len(metadata).to_bytes(8, "big"))
        digest.update(metadata)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def _assert_complete_identity_equal(first: dict, second: dict) -> None:
    for key in (
        "dataset_id",
        "annotation_set_id",
        "dataset_content_hash",
        "fingerprint",
        "fixture_ids",
        "fixture_manifest_hashes",
        "catalog_sha256",
        "tree_digest",
        "case_contract",
    ):
        assert first[key] == second[key], key


def _generate_in_subprocess(kind: str, root: Path) -> dict:
    code = """
import json
from pathlib import Path
import sys
from controlled_dataset_identity import dataset_identity_summary
from foam_benchmark_fixtures import generate_controlled_foam_dataset
from oil_benchmark_fixtures import generate_controlled_oil_dataset
kind = sys.argv[1]
root = Path(sys.argv[2])
generator = (
    generate_controlled_oil_dataset
    if kind == "oil"
    else generate_controlled_foam_dataset
)
dataset_path, _scenes = generator(root)
print(json.dumps(dataset_identity_summary(dataset_path), sort_keys=True))
"""
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        (str(PROJECT_ROOT / "src"), str(PROJECT_ROOT / "tests"))
    )
    env["PYTHONIOENCODING"] = "utf-8"
    completed = subprocess.run(
        (sys.executable, "-c", code, kind, str(root)),
        cwd=PROJECT_ROOT,
        env=env,
        stdin=subprocess.DEVNULL,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return json.loads(completed.stdout)


def _direct_bundle_contract() -> tuple[dict[str, np.ndarray], list[dict]]:
    frames: dict[str, np.ndarray] = {}
    manifest: list[dict] = []
    for index, scene in enumerate(single_frame_observability_collisions()):
        key = f"obs_{index:03d}"
        frames[key] = np.ascontiguousarray(scene.frame)
        ellipse = scene.ellipse
        manifest.append(
            {
                "key": key,
                "group": "observability",
                "case_id": scene.case_id,
                "collision_id": scene.collision_id,
                "latent_cause": scene.latent_cause.value,
                "truth_numeric_present": scene.numeric_oil_geometry_present,
                "truth_y": scene.latent_oil_y,
                "expected_family": scene.expected_canonical_family.value,
                "ellipse": [
                    ellipse.center_x,
                    ellipse.center_y,
                    ellipse.radius_x,
                    ellipse.radius_y,
                ],
                "learn_static": False,
            }
        )
    for index, scene in enumerate(historical_glare_negatives()):
        key = f"hist_{index:03d}"
        frames[key] = np.ascontiguousarray(scene.frame)
        manifest.append(
            {
                "key": key,
                "group": "historical_glare",
                "case_id": scene.case_id,
                "expected_family": "no_numeric",
                "ellipse": [160.0, 120.0, 38.4, 64.8],
                "learn_static": False,
            }
        )
    scene_map = {scene.case_id: scene for scene in controlled_oil_scenes()}
    for case_id, expected in (
        ("clear-upper", "numeric"),
        ("rapid-filling-0", "numeric"),
        ("structural-plus-real", "numeric"),
        ("reflection-only", "no_numeric"),
        ("glare-recovery-1", "no_numeric"),
        ("shimmer-only", "no_numeric"),
        ("transient-false-line-1", "no_numeric"),
        ("rim-line", "no_numeric"),
        ("full-no-interface", "no_numeric"),
        ("empty-no-interface", "no_numeric"),
        ("glare-recovery-3", "numeric"),
    ):
        scene = scene_map[case_id]
        key = "ctl_" + case_id.replace("-", "_")
        frames[key] = np.ascontiguousarray(scene.frame)
        manifest.append(
            {
                "key": key,
                "group": "control",
                "case_id": case_id,
                "expected_family": expected,
                "truth_y": scene.oil_y,
                "ellipse": [160.0, 120.0, 38.4, 64.8],
                "learn_static": False,
            }
        )
    thin = np.full((240, 320, 3), 105, dtype=np.uint8)
    cv2.line(thin, (0, 120), (319, 120), (235, 235, 235), 1)
    for case_id, learn_static in (
        ("structural-only", False),
        ("learned-static-overlap", True),
    ):
        key = "ctl_" + case_id.replace("-", "_")
        frames[key] = thin.copy()
        manifest.append(
            {
                "key": key,
                "group": "control",
                "case_id": case_id,
                "expected_family": "no_numeric",
                "ellipse": [160.0, 120.0, 38.4, 64.8],
                "learn_static": learn_static,
            }
        )
    return frames, manifest
