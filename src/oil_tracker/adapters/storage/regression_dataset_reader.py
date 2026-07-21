from __future__ import annotations

from dataclasses import replace
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any, Iterable, Mapping

import cv2
import numpy as np

from oil_tracker.adapters.storage.json_truth_repository import sha256_file
from oil_tracker.adapters.vision.geometry_masks import build_mask_bundle
from oil_tracker.application.ports.regression_dataset_reader import (
    RegressionDataset,
    RegressionDatasetCase,
)
from oil_tracker.domain.detector_benchmark import (
    BENCHMARK_CATALOG_SCHEMA_VERSION,
    BenchmarkCategory,
    BenchmarkTruth,
    BenchmarkValidationError,
    fingerprint_json,
)
from oil_tracker.domain.enums import FillState
from oil_tracker.domain.geometry import EllipseGeometry, ExclusionZone, GlassGeometry, Rect
from oil_tracker.domain.recipe import GlassInspectionConfig, InspectionRecipe
from oil_tracker.domain.session import AnalysisSession
from oil_tracker.domain.user_truth import TruthDisposition, TruthErrorType


DATASET_SCHEMA_VERSION = 1
FIXTURE_SCHEMA_VERSION = 1
TRUTH_FIXTURE_SCHEMA_VERSION = 1
_HASH_RE = re.compile(r"^[0-9a-f]{64}$")


class RegressionDatasetError(BenchmarkValidationError):
    """A regression dataset is malformed, unsafe, or has failed integrity checks."""


class UnsupportedRegressionDatasetSchema(RegressionDatasetError):
    pass


class RegressionDatasetIntegrityError(RegressionDatasetError):
    pass


class FilesystemRegressionDatasetReader:
    catalog_name = "benchmark_catalog.json"

    def load(self, path: str | Path) -> RegressionDataset:
        source = Path(path).expanduser()
        try:
            root = source.resolve(strict=True)
        except OSError as exc:
            raise RegressionDatasetError(f"dataset directory does not exist: {source}") from exc
        if not root.is_dir():
            raise RegressionDatasetError(f"dataset path is not a directory: {source}")

        dataset_path = root / "dataset_manifest.json"
        dataset = _read_json(dataset_path, "dataset manifest")
        version = _required_int(dataset, "dataset_schema_version", dataset_path)
        if version != DATASET_SCHEMA_VERSION:
            raise UnsupportedRegressionDatasetSchema(
                f"unsupported dataset schema version: {version}; supported={DATASET_SCHEMA_VERSION}"
            )
        dataset_id = _required_text(dataset, "dataset_id", dataset_path)
        if dataset.get("status") != "complete":
            raise RegressionDatasetError("dataset manifest status must be 'complete'")
        fixtures = dataset.get("fixtures")
        if not isinstance(fixtures, list):
            raise RegressionDatasetError("dataset manifest fixtures must be a JSON array")
        expected_count = _required_int(dataset, "fixture_count", dataset_path)
        if expected_count != len(fixtures):
            raise RegressionDatasetIntegrityError(
                f"fixture_count mismatch: declared={expected_count}, actual={len(fixtures)}"
            )
        expected_content_hash = _required_hash(
            dataset, "dataset_content_hash", dataset_path
        )
        actual_content_hash = hashlib.sha256(
            json.dumps(
                fixtures,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8")
        ).hexdigest()
        if expected_content_hash != actual_content_hash:
            raise RegressionDatasetIntegrityError("dataset_content_hash mismatch")

        source_identity = _required_object(dataset, "source_bundle_identity", dataset_path)
        annotation_identity = _required_object(
            dataset, "annotation_set_identity", dataset_path
        )
        catalog, catalog_present = self._load_catalog(root, dataset_id)
        seen_fixture_ids: set[str] = set()
        seen_paths: set[str] = set()
        seen_manifests: set[str] = set()
        cases: list[RegressionDatasetCase] = []
        fingerprint_cases: list[dict[str, Any]] = []
        warnings = [str(value) for value in dataset.get("warnings", [])]

        for index, raw_entry in enumerate(fixtures):
            if not isinstance(raw_entry, Mapping):
                raise RegressionDatasetError(
                    f"dataset fixture entry {index} must be a JSON object"
                )
            fixture_id = _required_text(raw_entry, "fixture_id", dataset_path)
            if fixture_id in seen_fixture_ids:
                raise RegressionDatasetIntegrityError(
                    f"duplicate fixture/case ID: {fixture_id}"
                )
            seen_fixture_ids.add(fixture_id)
            fixture_relative = _required_text(raw_entry, "path", dataset_path)
            manifest_relative = _required_text(raw_entry, "manifest", dataset_path)
            if fixture_relative in seen_paths:
                raise RegressionDatasetIntegrityError(
                    f"duplicate fixture path entry: {fixture_relative}"
                )
            if manifest_relative in seen_manifests:
                raise RegressionDatasetIntegrityError(
                    f"duplicate manifest entry: {manifest_relative}"
                )
            seen_paths.add(fixture_relative)
            seen_manifests.add(manifest_relative)
            fixture_root = _safe_resolve(
                root, fixture_relative, f"fixture {fixture_id} path", expect="directory"
            )
            manifest_path = _safe_resolve(
                root,
                manifest_relative,
                f"fixture {fixture_id} manifest",
                expect="file",
            )
            if fixture_root not in manifest_path.parents:
                raise RegressionDatasetIntegrityError(
                    f"fixture {fixture_id}: manifest is outside the fixture directory"
                )
            expected_manifest_hash = _required_hash(
                raw_entry, "manifest_sha256", dataset_path
            )
            actual_manifest_hash = sha256_file(manifest_path)
            if actual_manifest_hash != expected_manifest_hash:
                raise RegressionDatasetIntegrityError(
                    f"fixture {fixture_id}: manifest SHA-256 mismatch"
                )
            case, component, case_warnings = self._load_case(
                root=root,
                fixture_root=fixture_root,
                manifest_path=manifest_path,
                fixture_id=fixture_id,
                dataset_id=dataset_id,
                dataset_source_identity=source_identity,
                entry=raw_entry,
                catalog_entry=catalog.get(fixture_id),
                manifest_hash=actual_manifest_hash,
            )
            cases.append(case)
            fingerprint_cases.append(component)
            warnings.extend(case_warnings)

        unknown_catalog_ids = sorted(set(catalog) - seen_fixture_ids)
        if unknown_catalog_ids:
            raise RegressionDatasetIntegrityError(
                "benchmark catalog references unknown fixture IDs: "
                + ", ".join(unknown_catalog_ids)
            )
        self._validate_sequence_contract(cases)
        ordered_cases = tuple(sorted(cases, key=_case_sort_key))
        ordered_components = sorted(
            fingerprint_cases,
            key=lambda value: (
                value.get("sequence_id") or f"~{value['fixture_id']}",
                value.get("sequence_order") or 0,
                value["decoded_timestamp_sec"],
                value["decoded_frame_index"],
                value["fixture_id"],
            ),
        )
        fingerprint = fingerprint_json(
            {
                "dataset_schema_version": version,
                "source_bundle_identity": source_identity,
                "annotation_set_identity": {
                    "annotation_set_id": annotation_identity.get("annotation_set_id"),
                    "schema_version": annotation_identity.get("schema_version"),
                },
                "fixtures": ordered_components,
            }
        )
        return RegressionDataset(
            root=root,
            dataset_id=dataset_id,
            schema_version=version,
            fingerprint=fingerprint,
            source_bundle_identity=dict(source_identity),
            annotation_set_identity=dict(annotation_identity),
            cases=ordered_cases,
            warnings=tuple(sorted(set(warnings))),
            catalog_present=catalog_present,
        )

    def _load_catalog(
        self, root: Path, dataset_id: str
    ) -> tuple[dict[str, dict[str, Any]], bool]:
        path = root / self.catalog_name
        if not path.exists() and not path.is_symlink():
            return {}, False
        resolved = _safe_resolve(root, self.catalog_name, "benchmark catalog", expect="file")
        payload = _read_json(resolved, "benchmark catalog")
        version = _required_int(payload, "schema_version", resolved)
        if version != BENCHMARK_CATALOG_SCHEMA_VERSION:
            raise UnsupportedRegressionDatasetSchema(
                f"unsupported benchmark catalog schema version: {version}"
            )
        catalog_dataset_id = _required_text(payload, "dataset_id", resolved)
        if catalog_dataset_id != dataset_id:
            raise RegressionDatasetIntegrityError(
                "benchmark catalog dataset_id does not match dataset manifest"
            )
        fixtures = payload.get("fixtures")
        if not isinstance(fixtures, list):
            raise RegressionDatasetError("benchmark catalog fixtures must be an array")
        output: dict[str, dict[str, Any]] = {}
        for index, raw in enumerate(fixtures):
            if not isinstance(raw, Mapping):
                raise RegressionDatasetError(
                    f"benchmark catalog fixture entry {index} must be an object"
                )
            fixture_id = _required_text(raw, "fixture_id", resolved)
            if fixture_id in output:
                raise RegressionDatasetIntegrityError(
                    f"duplicate benchmark catalog fixture ID: {fixture_id}"
                )
            category_text = _required_text(raw, "category", resolved)
            try:
                BenchmarkCategory(category_text)
            except ValueError as exc:
                raise RegressionDatasetError(
                    f"fixture {fixture_id}: unknown benchmark category: {category_text}"
                ) from exc
            sequence_id = raw.get("sequence_id")
            sequence_order = raw.get("sequence_order")
            if sequence_id is not None:
                if not isinstance(sequence_id, str) or not sequence_id.strip():
                    raise RegressionDatasetError(
                        f"fixture {fixture_id}: sequence_id must be a non-empty string"
                    )
                if isinstance(sequence_order, bool) or not isinstance(sequence_order, int):
                    raise RegressionDatasetError(
                        f"fixture {fixture_id}: sequence_order is required for a sequence"
                    )
                if sequence_order < 0:
                    raise RegressionDatasetError(
                        f"fixture {fixture_id}: sequence_order must be non-negative"
                    )
            elif sequence_order is not None:
                raise RegressionDatasetError(
                    f"fixture {fixture_id}: sequence_order requires sequence_id"
                )
            output[fixture_id] = {
                "fixture_id": fixture_id,
                "category": category_text,
                "sequence_id": sequence_id,
                "sequence_order": sequence_order,
            }
        return output, True

    def _load_case(
        self,
        *,
        root: Path,
        fixture_root: Path,
        manifest_path: Path,
        fixture_id: str,
        dataset_id: str,
        dataset_source_identity: Mapping[str, Any],
        entry: Mapping[str, Any],
        catalog_entry: Mapping[str, Any] | None,
        manifest_hash: str,
    ) -> tuple[RegressionDatasetCase, dict[str, Any], tuple[str, ...]]:
        manifest = _read_json(manifest_path, f"fixture {fixture_id} manifest")
        version = _required_int(manifest, "fixture_schema_version", manifest_path)
        if version != FIXTURE_SCHEMA_VERSION:
            raise UnsupportedRegressionDatasetSchema(
                f"fixture {fixture_id}: unsupported fixture schema version: {version}"
            )
        if _required_text(manifest, "fixture_id", manifest_path) != fixture_id:
            raise RegressionDatasetIntegrityError(
                f"fixture {fixture_id}: fixture ID does not match its manifest"
            )
        if _required_text(manifest, "annotation_id", manifest_path) != _required_text(
            entry, "annotation_id", manifest_path
        ):
            raise RegressionDatasetIntegrityError(
                f"fixture {fixture_id}: annotation ID mismatch"
            )
        if _required_int(manifest, "annotation_revision", manifest_path) != _required_int(
            entry, "revision", manifest_path
        ):
            raise RegressionDatasetIntegrityError(
                f"fixture {fixture_id}: annotation revision mismatch"
            )
        relative_files = manifest.get("relative_files")
        hashes = manifest.get("sha256")
        if not isinstance(relative_files, list) or not all(
            isinstance(value, str) and value for value in relative_files
        ):
            raise RegressionDatasetError(
                f"fixture {fixture_id}: relative_files must be a string array"
            )
        if len(relative_files) != len(set(relative_files)):
            raise RegressionDatasetIntegrityError(
                f"fixture {fixture_id}: duplicate relative file manifest entry"
            )
        if not isinstance(hashes, Mapping):
            raise RegressionDatasetError(
                f"fixture {fixture_id}: sha256 must be a JSON object"
            )
        if set(relative_files) != set(hashes):
            raise RegressionDatasetIntegrityError(
                f"fixture {fixture_id}: relative_files and sha256 keys differ"
            )
        verified_hashes: dict[str, str] = {}
        for relative in sorted(relative_files):
            declared = str(hashes[relative])
            if not _HASH_RE.fullmatch(declared):
                raise RegressionDatasetError(
                    f"fixture {fixture_id}: invalid SHA-256 for {relative}"
                )
            file_path = _safe_resolve(
                fixture_root,
                relative,
                f"fixture {fixture_id} file {relative}",
                expect="file",
            )
            actual = sha256_file(file_path)
            if actual != declared:
                raise RegressionDatasetIntegrityError(
                    f"fixture {fixture_id}: SHA-256 mismatch for {relative}"
                )
            verified_hashes[relative] = actual

        required = {
            "truth.json",
            "official_reference.json",
            "recipe_snapshot.oilrecipe",
            "session_snapshot.json",
        }
        missing = sorted(required - set(relative_files))
        if missing:
            raise RegressionDatasetError(
                f"fixture {fixture_id}: required files are missing: {', '.join(missing)}"
            )
        if "frame.png" not in verified_hashes and "roi_crop.png" not in verified_hashes:
            raise RegressionDatasetError(
                f"fixture {fixture_id}: frame.png or roi_crop.png is required"
            )

        truth_path = fixture_root / "truth.json"
        recipe_path = fixture_root / "recipe_snapshot.oilrecipe"
        session_path = fixture_root / "session_snapshot.json"
        truth_payload = _read_json(truth_path, f"fixture {fixture_id} truth")
        truth_version = _required_int(
            truth_payload, "truth_schema_version", truth_path
        )
        if truth_version != TRUTH_FIXTURE_SCHEMA_VERSION:
            raise UnsupportedRegressionDatasetSchema(
                f"fixture {fixture_id}: unsupported truth fixture schema version: {truth_version}"
            )
        if _required_text(truth_payload, "annotation_id", truth_path) != _required_text(
            manifest, "annotation_id", manifest_path
        ):
            raise RegressionDatasetIntegrityError(
                f"fixture {fixture_id}: truth annotation ID mismatch"
            )
        if _required_int(truth_payload, "revision", truth_path) != _required_int(
            manifest, "annotation_revision", manifest_path
        ):
            raise RegressionDatasetIntegrityError(
                f"fixture {fixture_id}: truth revision mismatch"
            )
        try:
            disposition = TruthDisposition(
                _required_text(truth_payload, "disposition", truth_path)
            )
        except ValueError as exc:
            raise RegressionDatasetError(
                f"fixture {fixture_id}: unknown truth disposition"
            ) from exc
        try:
            raw_state = truth_payload.get("fill_state")
            fill_state = FillState(str(raw_state)) if raw_state is not None else None
        except ValueError as exc:
            raise RegressionDatasetError(
                f"fixture {fixture_id}: unknown truth fill state: {raw_state}"
            ) from exc
        foam_present = truth_payload.get("foam_present")
        if not isinstance(foam_present, bool):
            raise RegressionDatasetError(
                f"fixture {fixture_id}: foam_present must be a JSON boolean"
            )
        error_values = truth_payload.get("error_types", [])
        if not isinstance(error_values, list):
            raise RegressionDatasetError(
                f"fixture {fixture_id}: error_types must be an array"
            )
        try:
            error_types = tuple(TruthErrorType(str(value)) for value in error_values)
        except ValueError as exc:
            raise RegressionDatasetError(
                f"fixture {fixture_id}: unknown truth error type"
            ) from exc
        if len(error_types) != len(set(error_types)):
            raise RegressionDatasetIntegrityError(
                f"fixture {fixture_id}: duplicate truth error type"
            )
        note = str(truth_payload.get("note", ""))

        recipe_payload = _read_json(recipe_path, f"fixture {fixture_id} recipe snapshot")
        try:
            recipe = InspectionRecipe.from_dict(recipe_payload)
        except Exception as exc:
            raise RegressionDatasetError(
                f"fixture {fixture_id}: recipe snapshot is invalid: {exc}"
            ) from exc
        actual_recipe_hash = verified_hashes["recipe_snapshot.oilrecipe"]
        declared_recipe_hash = _required_hash(
            manifest, "recipe_snapshot_hash", manifest_path
        )
        if actual_recipe_hash != declared_recipe_hash:
            raise RegressionDatasetIntegrityError(
                f"fixture {fixture_id}: recipe snapshot hash mismatch"
            )
        if str(dataset_source_identity.get("recipe_snapshot_hash", "")) != actual_recipe_hash:
            raise RegressionDatasetIntegrityError(
                f"fixture {fixture_id}: recipe snapshot differs from dataset source identity"
            )
        if recipe.recipe_id != _required_text(manifest, "recipe_id", manifest_path):
            raise RegressionDatasetIntegrityError(
                f"fixture {fixture_id}: recipe ID mismatch"
            )
        if str(dataset_source_identity.get("recipe_id", "")) != recipe.recipe_id:
            raise RegressionDatasetIntegrityError(
                f"fixture {fixture_id}: recipe ID differs from dataset source identity"
            )

        session_payload = _read_json(
            session_path, f"fixture {fixture_id} session snapshot"
        )
        try:
            session = AnalysisSession.from_dict(session_payload)
        except Exception as exc:
            raise RegressionDatasetError(
                f"fixture {fixture_id}: session snapshot is invalid: {exc}"
            ) from exc
        glass_id = _required_text(truth_payload, "glass_id", truth_path)
        glass = next((value for value in recipe.glasses if value.id == glass_id), None)
        if glass is None:
            raise RegressionDatasetIntegrityError(
                f"fixture {fixture_id}: truth glass ID is absent from recipe snapshot"
            )

        decoded_frame_index = _required_int(
            manifest, "decoded_frame_index", manifest_path
        )
        decoded_timestamp = _required_float(
            manifest, "decoded_timestamp_sec", manifest_path
        )
        annotation_timestamp = _required_float(
            manifest, "annotation_actual_decoded_timestamp_sec", manifest_path
        )
        tolerance = _required_float(
            manifest, "frame_identity_tolerance_sec", manifest_path
        )
        truth_timestamp = _required_float(
            truth_payload, "actual_decoded_timestamp_sec", truth_path
        )
        truth_frame_index = _required_int(truth_payload, "frame_index", truth_path)
        if truth_frame_index >= 0 and truth_frame_index != decoded_frame_index:
            raise RegressionDatasetIntegrityError(
                f"fixture {fixture_id}: truth and decoded frame index mismatch"
            )
        if abs(truth_timestamp - annotation_timestamp) > 1e-9:
            raise RegressionDatasetIntegrityError(
                f"fixture {fixture_id}: truth and manifest annotation timestamp mismatch"
            )
        if abs(decoded_timestamp - annotation_timestamp) > max(0.0, tolerance):
            raise RegressionDatasetIntegrityError(
                f"fixture {fixture_id}: canonical decoded frame identity mismatch"
            )

        frame_width = _required_int(manifest, "frame_width", manifest_path)
        frame_height = _required_int(manifest, "frame_height", manifest_path)
        if frame_width <= 0 or frame_height <= 0:
            raise RegressionDatasetError(
                f"fixture {fixture_id}: frame dimensions must be positive"
            )
        if (recipe.reference_frame_width, recipe.reference_frame_height) != (
            frame_width,
            frame_height,
        ):
            raise RegressionDatasetIntegrityError(
                f"fixture {fixture_id}: recipe reference frame identity mismatch"
            )
        if (
            int(dataset_source_identity.get("source_width", 0)),
            int(dataset_source_identity.get("source_height", 0)),
        ) != (frame_width, frame_height):
            raise RegressionDatasetIntegrityError(
                f"fixture {fixture_id}: dataset source-frame identity mismatch"
            )
        if session.video_metadata is None or (
            session.video_metadata.width,
            session.video_metadata.height,
        ) != (frame_width, frame_height):
            raise RegressionDatasetIntegrityError(
                f"fixture {fixture_id}: session source-frame identity mismatch"
            )

        crop_origin = _required_xy(manifest, "roi_crop_origin", manifest_path)
        crop_size = _required_size(manifest, "roi_crop_size", manifest_path)
        oil_y = _coordinate_y(
            truth_payload.get("oil"),
            "oil",
            fixture_id,
            glass,
            crop_origin,
        )
        foam_y = _coordinate_y(
            truth_payload.get("foam"),
            "foam",
            fixture_id,
            glass,
            crop_origin,
        )
        if disposition is TruthDisposition.UNUSABLE:
            if fill_state is not None or oil_y is not None or foam_y is not None or foam_present:
                raise RegressionDatasetIntegrityError(
                    f"fixture {fixture_id}: unusable truth must not contain state or boundary values"
                )
        if fill_state in {FillState.FULL_NO_INTERFACE, FillState.EMPTY_NO_INTERFACE} and oil_y is not None:
            raise RegressionDatasetIntegrityError(
                f"fixture {fixture_id}: no-interface truth cannot contain an oil boundary"
            )
        if not foam_present and foam_y is not None:
            raise RegressionDatasetIntegrityError(
                f"fixture {fixture_id}: foam front exists while foam_present is false"
            )

        full_frame_path = fixture_root / "frame.png"
        roi_path = fixture_root / "roi_crop.png"
        if "frame.png" in verified_hashes:
            frame = _read_image(full_frame_path, fixture_id)
            if frame.shape[1] != frame_width or frame.shape[0] != frame_height:
                raise RegressionDatasetIntegrityError(
                    f"fixture {fixture_id}: decoded frame dimensions do not match manifest"
                )
            detector_glass = glass
            source_y_offset = 0.0
            image_hash = verified_hashes["frame.png"]
        else:
            frame = _read_image(roi_path, fixture_id)
            if (frame.shape[1], frame.shape[0]) != crop_size:
                raise RegressionDatasetIntegrityError(
                    f"fixture {fixture_id}: ROI image dimensions do not match manifest"
                )
            detector_glass = _translate_glass_to_crop(glass, crop_origin)
            source_y_offset = float(crop_origin[1])
            image_hash = verified_hashes["roi_crop.png"]
        if "roi_crop.png" in verified_hashes:
            roi = _read_image(roi_path, fixture_id)
            if (roi.shape[1], roi.shape[0]) != crop_size:
                raise RegressionDatasetIntegrityError(
                    f"fixture {fixture_id}: ROI image dimensions do not match manifest"
                )
        try:
            mask = build_mask_bundle(frame, detector_glass).effective_mask
        except Exception as exc:
            raise RegressionDatasetError(
                f"fixture {fixture_id}: effective analysis region cannot be built: {exc}"
            ) from exc
        valid_rows = np.where(mask.any(axis=1))[0]
        if valid_rows.size == 0:
            raise RegressionDatasetError(
                f"fixture {fixture_id}: effective analysis height is zero"
            )
        analysis_height = float(valid_rows.max() - valid_rows.min() + 1)
        if analysis_height <= 0:
            raise RegressionDatasetError(
                f"fixture {fixture_id}: effective analysis height is invalid"
            )

        if catalog_entry is not None:
            category = BenchmarkCategory(str(catalog_entry["category"]))
            sequence_id = catalog_entry.get("sequence_id")
            sequence_order = catalog_entry.get("sequence_order")
            category_source = "benchmark_catalog"
        else:
            category = _infer_category(fill_state, foam_present, error_types)
            sequence_id = None
            sequence_order = None
            category_source = "truth_inference"
        unusable_reasons = tuple(
            [value.value for value in error_types]
            + ([f"note:{note}"] if note.strip() else [])
        )
        truth = BenchmarkTruth(
            fill_state=fill_state,
            oil_boundary_y=oil_y,
            foam_present=foam_present if disposition is not TruthDisposition.UNUSABLE else None,
            foam_front_y=foam_y,
        )
        frame_identity = f"{decoded_frame_index}@{decoded_timestamp:.9f}"
        case = RegressionDatasetCase(
            dataset_id=dataset_id,
            case_id=fixture_id,
            sequence_id=str(sequence_id) if sequence_id else None,
            sequence_order=int(sequence_order) if sequence_order is not None else None,
            category=category,
            disposition=disposition,
            unusable_reasons=unusable_reasons,
            timestamp_sec=decoded_timestamp,
            frame_index=decoded_frame_index,
            frame_identity=frame_identity,
            frame=frame,
            source_y_offset=source_y_offset,
            analysis_height_px=analysis_height,
            glass=detector_glass,
            truth=truth,
            fixture_manifest_hash=manifest_hash,
            frame_hash=image_hash,
        )
        component = {
            "fixture_id": fixture_id,
            "fixture_schema_version": version,
            "manifest_sha256": manifest_hash,
            "declared_file_hashes": dict(sorted(verified_hashes.items())),
            "annotation_id": _required_text(manifest, "annotation_id", manifest_path),
            "annotation_revision": _required_int(
                manifest, "annotation_revision", manifest_path
            ),
            "decoded_frame_index": decoded_frame_index,
            "decoded_timestamp_sec": decoded_timestamp,
            "frame_identity_tolerance_sec": tolerance,
            "category": category.value,
            "category_source": category_source,
            "sequence_id": sequence_id,
            "sequence_order": sequence_order,
            "analysis_height_px": analysis_height,
            "source_y_offset": source_y_offset,
        }
        case_warnings = [str(value) for value in manifest.get("warnings", [])]
        if catalog_entry is None:
            case_warnings.append(
                f"{fixture_id}: benchmark category inferred from existing truth fields"
            )
        return case, component, tuple(case_warnings)

    @staticmethod
    def _validate_sequence_contract(cases: Iterable[RegressionDatasetCase]) -> None:
        seen: set[tuple[str, int]] = set()
        for case in cases:
            if case.sequence_id is None:
                continue
            key = (case.sequence_id, int(case.sequence_order or 0))
            if key in seen:
                raise RegressionDatasetIntegrityError(
                    f"duplicate sequence order: {case.sequence_id}/{case.sequence_order}"
                )
            seen.add(key)


def _infer_category(
    fill_state: FillState | None,
    foam_present: bool,
    error_types: tuple[TruthErrorType, ...],
) -> BenchmarkCategory:
    errors = set(error_types)
    if foam_present or fill_state in {FillState.FULL_WITH_FOAM, FillState.FOAMING_VISIBLE}:
        return BenchmarkCategory.WHITE_FOAM
    if TruthErrorType.FOAM_MISCLASSIFIED in errors and not foam_present:
        return BenchmarkCategory.TRANSPARENT_OIL_SHIMMER
    if errors & {TruthErrorType.GLARE_OR_REFLECTION, TruthErrorType.VIDEO_UNUSABLE}:
        return BenchmarkCategory.REFLECTION_OR_BLUR
    if TruthErrorType.STRUCTURAL_EDGE in errors:
        return BenchmarkCategory.STRUCTURAL_HORIZONTAL_EDGE
    if fill_state in {FillState.FULL_NO_INTERFACE, FillState.EMPTY_NO_INTERFACE}:
        return BenchmarkCategory.NO_INTERFACE
    if fill_state in {
        FillState.FILLING_VISIBLE,
        FillState.PARTIAL_VISIBLE,
        FillState.DRAINING_VISIBLE,
    }:
        return BenchmarkCategory.CLEAR_OIL_BOUNDARY
    raise RegressionDatasetError(
        "fixture category cannot be determined from exporter schema v1; "
        "add benchmark_catalog.json with an explicit supported category"
    )


def _coordinate_y(
    payload: Any,
    label: str,
    fixture_id: str,
    glass: GlassInspectionConfig,
    crop_origin: tuple[int, int],
) -> float | None:
    if payload is None:
        return None
    if not isinstance(payload, Mapping):
        raise RegressionDatasetError(
            f"fixture {fixture_id}: {label} truth coordinate must be an object"
        )
    source_y = _required_float(payload, "source_frame_y", Path(f"{label} truth"))
    local_y = _required_float(payload, "roi_local_y", Path(f"{label} truth"))
    if not math.isclose(source_y - crop_origin[1], local_y, abs_tol=1e-9):
        raise RegressionDatasetIntegrityError(
            f"fixture {fixture_id}: {label} source-frame/ROI coordinate mismatch"
        )
    expected_px = glass.geometry.level_px_from_zero(source_y)
    raw_px = payload.get("px_from_zero")
    if expected_px is None:
        if raw_px is not None:
            raise RegressionDatasetIntegrityError(
                f"fixture {fixture_id}: {label} px_from_zero exists without a zero line"
            )
    elif raw_px is None or not math.isclose(
        expected_px, _finite(raw_px, f"{label} px_from_zero"), abs_tol=1e-9
    ):
        raise RegressionDatasetIntegrityError(
            f"fixture {fixture_id}: {label} px_from_zero mismatch"
        )
    raw_mm = payload.get("mm_from_zero")
    expected_mm = glass.geometry.level_mm_from_zero(source_y, glass.mm_per_pixel)
    if expected_mm is None:
        if raw_mm is not None:
            raise RegressionDatasetIntegrityError(
                f"fixture {fixture_id}: {label} mm_from_zero is unexpectedly present"
            )
    elif raw_mm is None or not math.isclose(
        expected_mm, _finite(raw_mm, f"{label} mm_from_zero"), abs_tol=1e-9
    ):
        raise RegressionDatasetIntegrityError(
            f"fixture {fixture_id}: {label} mm_from_zero mismatch"
        )
    if glass.geometry.ellipse.horizontal_extent_at(source_y) is None:
        raise RegressionDatasetIntegrityError(
            f"fixture {fixture_id}: {label} truth is outside the canonical Glass geometry"
        )
    return source_y


def _translate_glass_to_crop(
    glass: GlassInspectionConfig, origin: tuple[int, int]
) -> GlassInspectionConfig:
    ox, oy = origin
    ellipse = glass.geometry.ellipse
    translated_ellipse = EllipseGeometry(
        ellipse.center_x - ox,
        ellipse.center_y - oy,
        ellipse.radius_x,
        ellipse.radius_y,
    )
    exclusions = [
        ExclusionZone(
            value.id,
            Rect(
                value.rect.x - ox,
                value.rect.y - oy,
                value.rect.width,
                value.rect.height,
            ),
            value.name,
            value.note,
        )
        for value in glass.geometry.exclusions
    ]
    geometry = GlassGeometry(
        translated_ellipse,
        None
        if glass.geometry.zero_line_y is None
        else glass.geometry.zero_line_y - oy,
        glass.geometry.margin_ratio,
        exclusions,
    )
    return replace(glass, geometry=geometry)


def _read_image(path: Path, fixture_id: str) -> np.ndarray:
    try:
        encoded = np.fromfile(str(path), dtype=np.uint8)
        image = cv2.imdecode(encoded, cv2.IMREAD_UNCHANGED)
    except Exception as exc:
        raise RegressionDatasetError(
            f"fixture {fixture_id}: image decode failed for {path.name}: {exc}"
        ) from exc
    if image is None or image.ndim not in (2, 3):
        raise RegressionDatasetError(
            f"fixture {fixture_id}: image decode returned no usable frame: {path.name}"
        )
    return np.ascontiguousarray(image)


def _safe_resolve(
    root: Path, raw: str, label: str, *, expect: str
) -> Path:
    relative = Path(str(raw))
    if relative.is_absolute():
        raise RegressionDatasetError(f"{label}: absolute paths are not allowed")
    if ".." in relative.parts:
        raise RegressionDatasetError(f"{label}: '..' path traversal is not allowed")
    try:
        resolved_root = root.resolve(strict=True)
        resolved = (root / relative).resolve(strict=True)
    except OSError as exc:
        raise RegressionDatasetError(f"{label}: required path is missing") from exc
    if resolved != resolved_root and resolved_root not in resolved.parents:
        raise RegressionDatasetError(f"{label}: resolved path escapes dataset root")
    if expect == "file" and not resolved.is_file():
        raise RegressionDatasetError(f"{label}: expected a file")
    if expect == "directory" and not resolved.is_dir():
        raise RegressionDatasetError(f"{label}: expected a directory")
    return resolved


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
        payload = json.loads(
            text,
            parse_constant=lambda value: (_raise_invalid_constant(value)),
            object_pairs_hook=_unique_object,
        )
    except RegressionDatasetError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise RegressionDatasetError(f"{label} JSON is malformed: {exc}") from exc
    if not isinstance(payload, dict):
        raise RegressionDatasetError(f"{label} must contain a JSON object")
    return payload


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in pairs:
        if key in output:
            raise RegressionDatasetError(f"duplicate JSON object key: {key}")
        output[key] = value
    return output


def _raise_invalid_constant(value: str):
    raise RegressionDatasetError(f"JSON constant is not allowed: {value}")


def _required_object(
    payload: Mapping[str, Any], key: str, path: Path
) -> Mapping[str, Any]:
    value = payload.get(key)
    if not isinstance(value, Mapping):
        raise RegressionDatasetError(f"{path}: missing or invalid object field '{key}'")
    return value


def _required_text(payload: Mapping[str, Any], key: str, path: Path) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RegressionDatasetError(f"{path}: missing or invalid text field '{key}'")
    return value


def _required_int(payload: Mapping[str, Any], key: str, path: Path) -> int:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise RegressionDatasetError(f"{path}: missing or invalid integer field '{key}'")
    return value


def _required_float(payload: Mapping[str, Any], key: str, path: Path) -> float:
    if key not in payload:
        raise RegressionDatasetError(f"{path}: missing numeric field '{key}'")
    return _finite(payload[key], f"{path}:{key}")


def _required_hash(payload: Mapping[str, Any], key: str, path: Path) -> str:
    value = _required_text(payload, key, path)
    if not _HASH_RE.fullmatch(value):
        raise RegressionDatasetError(f"{path}: invalid SHA-256 field '{key}'")
    return value


def _required_xy(
    payload: Mapping[str, Any], key: str, path: Path
) -> tuple[int, int]:
    value = _required_object(payload, key, path)
    x = _required_int(value, "x", path)
    y = _required_int(value, "y", path)
    if x < 0 or y < 0:
        raise RegressionDatasetError(f"{path}: {key} must be non-negative")
    return x, y


def _required_size(
    payload: Mapping[str, Any], key: str, path: Path
) -> tuple[int, int]:
    value = _required_object(payload, key, path)
    width = _required_int(value, "width", path)
    height = _required_int(value, "height", path)
    if width <= 0 or height <= 0:
        raise RegressionDatasetError(f"{path}: {key} must be positive")
    return width, height


def _finite(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise RegressionDatasetError(f"{label} must be numeric") from exc
    if not math.isfinite(number):
        raise RegressionDatasetError(f"{label} must be finite")
    return number


def _case_sort_key(case: RegressionDatasetCase) -> tuple[Any, ...]:
    group = case.sequence_id or f"~{case.case_id}"
    order = case.sequence_order if case.sequence_order is not None else 0
    return group, order, case.timestamp_sec, case.frame_index, case.case_id
