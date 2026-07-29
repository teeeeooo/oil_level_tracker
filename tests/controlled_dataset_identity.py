from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from uuid import NAMESPACE_URL, UUID, uuid5

import numpy as np

from oil_tracker.adapters.storage.json_truth_repository import (
    build_truth_bundle_identity,
    sha256_file,
)
from oil_tracker.adapters.storage.regression_dataset_reader import (
    FilesystemRegressionDatasetReader,
)
from oil_tracker.domain.detector_benchmark import fingerprint_json
from oil_tracker.domain.user_truth import UserTruthSet


CONTROLLED_CONTRACT_VERSION = "v1"
CONTROLLED_IDENTITY_NAMESPACE: UUID = uuid5(
    NAMESPACE_URL,
    "https://github.com/teeeeooo/oil_level_tracker/controlled-dataset-identity",
)


@dataclass(frozen=True)
class ControlledDatasetIdentity:
    dataset_kind: str
    contract_version: str
    contract_digest: str
    dataset_id: str
    annotation_set_id: str
    timestamp_iso: str
    truth_set: UserTruthSet

    def annotation_id(self, index: int, case_id: str) -> str:
        return str(
            uuid5(
                CONTROLLED_IDENTITY_NAMESPACE,
                ":".join(
                    (
                        self.dataset_kind,
                        self.contract_version,
                        self.contract_digest,
                        "annotation",
                        str(int(index)),
                        str(case_id),
                    )
                ),
            )
        )


def prepare_controlled_dataset_identity(
    bundle,
    scenes,
    *,
    dataset_kind: str,
    contract_version: str,
    fixed_time: datetime,
) -> ControlledDatasetIdentity:
    kind = str(dataset_kind).strip().lower()
    version = str(contract_version).strip()
    if kind not in {"oil", "foam"}:
        raise ValueError(f"unsupported controlled dataset kind: {dataset_kind}")
    if not version:
        raise ValueError("controlled contract version must not be empty")
    timestamp = fixed_time.astimezone(timezone.utc).isoformat()
    _normalize_recipe_snapshot(bundle, timestamp)
    _normalize_session_snapshot(bundle, kind, version)
    identity = build_truth_bundle_identity(bundle)
    contract_payload = {
        "dataset_kind": kind,
        "contract_version": version,
        "fixed_timestamp": timestamp,
        "bundle_identity": identity.to_dict(),
        "recipe_snapshot_sha256": sha256_file(Path(bundle.files["recipe_snapshot"])),
        "session_snapshot_sha256": sha256_file(Path(bundle.files["session"])),
        "scenes": [_scene_contract(scene) for scene in scenes],
    }
    digest = fingerprint_json(contract_payload)
    dataset_id = _stable_uuid(kind, version, digest, "dataset")
    annotation_set_id = _stable_uuid(kind, version, digest, "annotation-set")
    truth_set = UserTruthSet(
        annotation_set_id=annotation_set_id,
        bundle_identity=identity,
        created_at=timestamp,
        updated_at=timestamp,
    )
    return ControlledDatasetIdentity(
        dataset_kind=kind,
        contract_version=version,
        contract_digest=digest,
        dataset_id=dataset_id,
        annotation_set_id=annotation_set_id,
        timestamp_iso=timestamp,
        truth_set=truth_set,
    )


def dataset_identity_summary(dataset_path: Path) -> dict:
    root = Path(dataset_path)
    manifest = json.loads((root / "dataset_manifest.json").read_text(encoding="utf-8"))
    catalog_bytes = (root / "benchmark_catalog.json").read_bytes()
    loaded = FilesystemRegressionDatasetReader().load(root)
    return {
        "dataset_id": manifest["dataset_id"],
        "annotation_set_id": manifest["annotation_set_identity"]["annotation_set_id"],
        "dataset_content_hash": manifest["dataset_content_hash"],
        "fingerprint": loaded.fingerprint,
        "fixture_ids": [item["fixture_id"] for item in manifest["fixtures"]],
        "fixture_manifest_hashes": [
            item["manifest_sha256"] for item in manifest["fixtures"]
        ],
        "catalog_sha256": hashlib.sha256(catalog_bytes).hexdigest(),
        "tree_digest": relative_tree_digest(root),
        "case_count": len(loaded.cases),
        "sequence_count": len(
            {case.sequence_id for case in loaded.cases if case.sequence_id is not None}
        ),
        "case_contract": [
            {
                "case_id": case.case_id,
                "category": case.category.value,
                "sequence_id": case.sequence_id,
                "sequence_order": case.sequence_order,
                "truth_fill_state": (
                    case.truth.fill_state.value if case.truth.fill_state is not None else None
                ),
                "truth_oil_y": case.truth.oil_boundary_y,
                "truth_foam_present": case.truth.foam_present,
                "truth_foam_y": case.truth.foam_front_y,
                "settings": asdict(case.glass.detector_settings),
            }
            for case in loaded.cases
        ],
    }


def relative_tree_digest(root: Path) -> str:
    root = Path(root)
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        kind = b"d" if path.is_dir() else b"f"
        digest.update(kind)
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        if path.is_file():
            content = path.read_bytes()
            digest.update(len(content).to_bytes(8, "big"))
            digest.update(content)
    return digest.hexdigest()


def _normalize_recipe_snapshot(bundle, timestamp: str) -> None:
    recipe_path = Path(bundle.files["recipe_snapshot"])
    payload = json.loads(recipe_path.read_text(encoding="utf-8"))
    payload["created_at"] = timestamp
    payload["updated_at"] = timestamp
    recipe_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )


def _normalize_session_snapshot(bundle, kind: str, version: str) -> None:
    session_path = Path(bundle.files["session"])
    payload = json.loads(session_path.read_text(encoding="utf-8"))
    stable_source = f"controlled://rotary-oil-level-tracker/{kind}/{version}/source.mp4"
    payload["input_video_path"] = stable_source
    metadata = payload.get("video_metadata")
    if not isinstance(metadata, dict):
        raise ValueError("controlled session snapshot must contain video_metadata")
    metadata["path"] = stable_source
    session_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )


def _scene_contract(scene) -> dict:
    frame = np.ascontiguousarray(scene.frame)
    return {
        "case_id": str(scene.case_id),
        "category": scene.category.value,
        "timestamp": float(scene.timestamp),
        "fill_state": scene.fill_state.value,
        "oil_y": None if scene.oil_y is None else float(scene.oil_y),
        "foam_present": bool(scene.foam_present),
        "foam_y": None if scene.foam_y is None else float(scene.foam_y),
        "sequence_id": scene.sequence_id,
        "sequence_order": scene.sequence_order,
        "frame_shape": list(frame.shape),
        "frame_dtype": str(frame.dtype),
        "frame_sha256": hashlib.sha256(frame.tobytes()).hexdigest(),
    }


def _stable_uuid(kind: str, version: str, digest: str, role: str) -> str:
    return str(
        uuid5(
            CONTROLLED_IDENTITY_NAMESPACE,
            ":".join((kind, version, digest, role)),
        )
    )
