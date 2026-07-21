from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Iterable

from oil_tracker.adapters.storage.json_truth_repository import sha256_file
from oil_tracker.adapters.storage.regression_fixture_exporter import RegressionFixtureExporter
from oil_tracker.domain.enums import FillState
from oil_tracker.domain.user_truth import TruthDisposition, TruthErrorType
from user_truth_fixtures import make_truth_bundle, make_truth_set_and_annotation


FIXED_TIME = datetime(2026, 7, 21, 12, 34, 56, tzinfo=timezone.utc)


class TimestampVideoReader:
    def __init__(self, source, metadata) -> None:
        self.path = str(source)
        self.metadata = metadata
        self.closed = False
        self.requests: list[float] = []

    def read_at(self, timestamp: float):
        import numpy as np

        self.requests.append(float(timestamp))
        frame = np.zeros((self.metadata.height, self.metadata.width, 3), dtype=np.uint8)
        frame[:, :, 0] = 12
        frame[:, :, 1] = 34
        frame[:, :, 2] = 56
        frame_index = int(round(float(timestamp) * self.metadata.fps))
        return frame, frame_index, float(timestamp)

    def close(self) -> None:
        self.closed = True


def export_benchmark_dataset(
    tmp_path: Path,
    *,
    label: str = "기본",
    timestamps: Iterable[float] = (2.0,),
    disposition: TruthDisposition = TruthDisposition.CORRECTED,
    fill_state: FillState | None = FillState.PARTIAL_VISIBLE,
    oil_y: float | None = 128.0,
    foam_present: bool = False,
    foam_y: float | None = None,
    error_types: tuple[TruthErrorType, ...] = (TruthErrorType.WRONG_CANDIDATE,),
    note: str = "benchmark truth",
) -> Path:
    bundle = make_truth_bundle(tmp_path / label)
    truth_set, annotation, _service = make_truth_set_and_annotation(
        bundle,
        disposition=disposition,
        fill_state=fill_state,
        oil_y=oil_y,
        foam_present=foam_present,
        foam_y=foam_y,
        error_types=error_types,
        note=note,
    )
    values = tuple(float(value) for value in timestamps)
    annotations = []
    truth_set.annotations.clear()
    for index, timestamp in enumerate(values):
        current = replace(
            annotation,
            annotation_id=f"annotation-{index + 1}",
            requested_timestamp_sec=timestamp,
            actual_decoded_timestamp_sec=timestamp,
            frame_index=int(round(timestamp * bundle.source_metadata.fps)),
            revision=index + 1,
        )
        truth_set.upsert(current)
        annotations.append(current)
    reader = TimestampVideoReader(bundle.source_video_path, bundle.source_metadata)
    exporter = RegressionFixtureExporter(
        lambda _path: reader,
        clock=lambda: FIXED_TIME,
    )
    result = exporter.export(
        bundle,
        truth_set,
        annotations,
        tmp_path / f"dataset-output-{label}",
        source_video_path=bundle.source_video_path,
    )
    assert reader.closed
    return result.dataset_path


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )


def fixture_entry(dataset_root: Path, index: int = 0) -> dict:
    return read_json(dataset_root / "dataset_manifest.json")["fixtures"][index]


def fixture_directory(dataset_root: Path, index: int = 0) -> Path:
    entry = fixture_entry(dataset_root, index)
    return dataset_root / entry["path"]


def write_catalog(dataset_root: Path, fixtures: list[dict]) -> Path:
    dataset = read_json(dataset_root / "dataset_manifest.json")
    path = dataset_root / "benchmark_catalog.json"
    write_json(
        path,
        {
            "schema_version": 1,
            "dataset_id": dataset["dataset_id"],
            "fixtures": fixtures,
        },
    )
    return path


def rehash_dataset(dataset_root: Path) -> None:
    dataset_path = dataset_root / "dataset_manifest.json"
    dataset = read_json(dataset_path)
    for entry in dataset["fixtures"]:
        fixture_root = dataset_root / entry["path"]
        manifest_path = dataset_root / entry["manifest"]
        manifest = read_json(manifest_path)
        hashes = {}
        for relative in manifest["relative_files"]:
            hashes[relative] = sha256_file(fixture_root / relative)
        manifest["sha256"] = hashes
        write_json(manifest_path, manifest)
        entry["manifest_sha256"] = sha256_file(manifest_path)
    dataset["dataset_content_hash"] = hashlib.sha256(
        json.dumps(
            dataset["fixtures"],
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()
    write_json(dataset_path, dataset)
