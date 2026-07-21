from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from oil_tracker.domain.detector_benchmark import BenchmarkCategory, BenchmarkTruth
from oil_tracker.domain.recipe import GlassInspectionConfig
from oil_tracker.domain.user_truth import TruthDisposition


@dataclass(frozen=True)
class RegressionDatasetCase:
    dataset_id: str
    case_id: str
    sequence_id: str | None
    sequence_order: int | None
    category: BenchmarkCategory
    disposition: TruthDisposition
    unusable_reasons: tuple[str, ...]
    timestamp_sec: float
    frame_index: int
    frame_identity: str
    frame: Any
    source_y_offset: float
    analysis_height_px: float
    glass: GlassInspectionConfig
    truth: BenchmarkTruth
    fixture_manifest_hash: str
    frame_hash: str


@dataclass(frozen=True)
class RegressionDataset:
    root: Path
    dataset_id: str
    schema_version: int
    fingerprint: str
    source_bundle_identity: dict[str, Any]
    annotation_set_identity: dict[str, Any]
    cases: tuple[RegressionDatasetCase, ...]
    warnings: tuple[str, ...]
    catalog_present: bool


class RegressionDatasetReader(Protocol):
    def load(self, path: str | Path) -> RegressionDataset: ...
