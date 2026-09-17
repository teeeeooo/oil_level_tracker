from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import math
from pathlib import Path
from statistics import median
from typing import Any, Iterable

import cv2
import numpy as np

from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.adapters.storage.json_truth_repository import JsonTruthRepository
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.adapters.vision.oil_interface_diagnostics import INTERFACE_DIAGNOSTICS_SCHEMA
from tests.diagnostics.s11_replay_provenance import capture_runtime_provenance
from tests.diagnostics.s11_resolver_replacement_profile import source_identity
from tests.diagnostics.s11_evidence_probe import (
    CORPUS_STEMS,
    authoritative_input_hashes,
    repository_root,
    validate_local_corpus,
)


SCHEMA_VERSION = "s11-interface-witness-public-probe-v2"
NEAR_TRUTH_TOLERANCE_PX = 8.0
REMOTE_DISTANCE_PX = 24.0


@dataclass(frozen=True)
class TransformSpec:
    name: str
    kind: str
    value: float


TRANSFORMS = {
    spec.name: spec
    for spec in (
        TransformSpec("original", "identity", 1.0),
        TransformSpec("brightness_0.80", "brightness", 0.80),
        TransformSpec("brightness_1.20", "brightness", 1.20),
        TransformSpec("gamma_0.80", "gamma", 0.80),
        TransformSpec("gamma_1.25", "gamma", 1.25),
        TransformSpec("contrast_0.80", "contrast", 0.80),
        TransformSpec("contrast_1.20", "contrast", 1.20),
    )
}


@dataclass(frozen=True)
class ProbeCase:
    sample: str
    frame_index: int
    timestamp_sec: float
    truth_y: float
    video_path: Path
    glass: Any

    @property
    def case_id(self) -> str:
        return f"{self.sample}:{self.frame_index}"


@dataclass(frozen=True)
class CandidateMeasurement:
    candidate_input_index: int
    source: str
    canonical_y: float
    distance_to_truth_px: float
    distance_partition: str
    rejected: bool
    native_path_geometry: bool
    usable_sector_count: int
    sector_count: int
    median_near_abs_contrast: float | None
    median_far_abs_contrast: float | None
    median_near_minus_far_abs_contrast: float | None
    near_far_same_sign_fraction: float | None
    median_peak_abs_offset_px: float | None
    median_glare_fraction: float | None
    median_near_gray_std: float | None
    boundary_likelihood: float | None
    final_score: float | None
    material_terminal_partition_support: float | None
    material_texture_conflict: float | None
    narrow_horizontal_coverage: float | None


@dataclass(frozen=True)
class FrameMeasurement:
    case_id: str
    sample: str
    frame_index: int
    timestamp_sec: float
    transform: str
    truth_y: float
    oil_candidate_count: int
    near_truth_candidate_count: int
    nearest_candidate_error_px: float | None
    nearest_candidate_source: str | None
    candidates: tuple[CandidateMeasurement, ...]


def _finite(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _median(values: Iterable[float | None]) -> float | None:
    finite = [float(value) for value in values if value is not None and math.isfinite(float(value))]
    return float(median(finite)) if finite else None


def _fraction(values: Iterable[bool]) -> float | None:
    rows = tuple(values)
    return float(sum(rows) / len(rows)) if rows else None


def _distance_partition(distance: float) -> str:
    if distance <= NEAR_TRUTH_TOLERANCE_PX:
        return "near_truth_geometry"
    if distance >= REMOTE_DISTANCE_PX:
        return "remote_geometry_not_proven_negative"
    return "guard_band"


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_cases(root: Path) -> tuple[ProbeCase, ...]:
    validate_local_corpus(root)
    recipe_repository = JsonRecipeRepository()
    truth_repository = JsonTruthRepository()
    cases: list[ProbeCase] = []
    for sample in CORPUS_STEMS:
        recipe = recipe_repository.load(root / "sample" / f"{sample}.oilrecipe")
        glass = recipe.glasses[0]
        truth = truth_repository.load(root / "sample" / f"{sample}.oiltruth").truth_set
        for annotation in truth.sorted_annotations():
            if annotation.disposition.value == "unusable" or annotation.oil_boundary is None:
                continue
            cases.append(
                ProbeCase(
                    sample=sample,
                    frame_index=int(annotation.frame_index),
                    timestamp_sec=float(annotation.actual_decoded_timestamp_sec),
                    truth_y=float(annotation.oil_boundary.source_frame_y),
                    video_path=root / "sample" / f"{sample}.mp4",
                    glass=glass,
                )
            )
    return tuple(cases)


def _decode(case: ProbeCase) -> np.ndarray:
    capture = cv2.VideoCapture(str(case.video_path))
    try:
        capture.set(cv2.CAP_PROP_POS_FRAMES, case.frame_index)
        ok, frame = capture.read()
    finally:
        capture.release()
    if not ok or frame is None:
        raise RuntimeError(f"Could not decode {case.case_id}")
    return frame


def _transform(frame: np.ndarray, spec: TransformSpec) -> np.ndarray:
    if spec.kind == "identity":
        return frame
    values = frame.astype(np.float64)
    if spec.kind == "brightness":
        transformed = values * spec.value
    elif spec.kind == "gamma":
        transformed = 255.0 * np.power(values / 255.0, spec.value)
    elif spec.kind == "contrast":
        transformed = (values - 127.5) * spec.value + 127.5
    else:
        raise ValueError(f"Unsupported transform kind: {spec.kind}")
    return np.clip(np.rint(transformed), 0.0, 255.0).astype(np.uint8)


def _sector_peak_offset(sector: dict[str, object]) -> float | None:
    if "peak_offset_from_path_px" in sector:
        return _finite(sector.get("peak_offset_from_path_px"))
    return _finite(sector.get("peak_offset_from_candidate_px"))


def _candidate_measurement(
    diagnostic: dict[str, object],
    candidate: Any,
    truth_y: float,
) -> CandidateMeasurement | None:
    canonical_y = _finite(diagnostic.get("canonical_y"))
    if canonical_y is None:
        return None
    path = diagnostic.get("path_aligned")
    native = bool(isinstance(path, dict) and path.get("status") == "measured")
    sectors = path.get("sectors", []) if native else diagnostic.get("sectors", [])
    sectors = tuple(value for value in sectors if isinstance(value, dict))
    usable = tuple(
        value
        for value in sectors
        if _finite(value.get("near_signed_contrast")) is not None
        and _finite(value.get("far_signed_contrast")) is not None
    )
    same_sign = []
    for value in usable:
        near = _finite(value.get("near_signed_contrast"))
        far = _finite(value.get("far_signed_contrast"))
        assert near is not None and far is not None
        if abs(near) > 1e-9 and abs(far) > 1e-9:
            same_sign.append(near * far > 0.0)
    glare_values: list[float | None] = []
    gray_stds: list[float | None] = []
    for value in usable:
        bands = value.get("bands")
        if not isinstance(bands, dict):
            continue
        for key in ("near_above", "near_below"):
            band = bands.get(key)
            if isinstance(band, dict):
                glare_values.append(_finite(band.get("glare_fraction")))
                gray_stds.append(_finite(band.get("gray_std")))
    features = candidate.features
    penalties = candidate.penalties
    conflicts = [_finite(mapping.get("material_texture_conflict")) for mapping in (features, penalties)]
    measured_conflicts = [value for value in conflicts if value is not None]
    distance = abs(canonical_y - truth_y)
    return CandidateMeasurement(
        candidate_input_index=int(diagnostic["candidate_input_index"]),
        source=str(diagnostic.get("source", candidate.source)),
        canonical_y=canonical_y,
        distance_to_truth_px=distance,
        distance_partition=_distance_partition(distance),
        rejected=bool(diagnostic.get("rejected", candidate.rejected)),
        native_path_geometry=native,
        usable_sector_count=len(usable),
        sector_count=len(sectors),
        median_near_abs_contrast=_median(
            abs(float(value["near_signed_contrast"])) for value in usable
        ),
        median_far_abs_contrast=_median(
            abs(float(value["far_signed_contrast"])) for value in usable
        ),
        median_near_minus_far_abs_contrast=_median(
            _finite(value.get("near_minus_far_abs_contrast")) for value in usable
        ),
        near_far_same_sign_fraction=_fraction(same_sign),
        median_peak_abs_offset_px=_median(
            abs(value) if value is not None else None
            for value in (_sector_peak_offset(sector) for sector in usable)
        ),
        median_glare_fraction=_median(glare_values),
        median_near_gray_std=_median(gray_stds),
        boundary_likelihood=_finite(features.get("boundary_likelihood")),
        final_score=_finite(candidate.final_score),
        material_terminal_partition_support=_finite(
            features.get("material_terminal_partition_support")
        ),
        material_texture_conflict=max(measured_conflicts) if measured_conflicts else None,
        narrow_horizontal_coverage=_finite(
            features.get("narrow_horizontal_coverage", features.get("horizontal_coverage"))
        ),
    )


def _probe(
    case: ProbeCase,
    spec: TransformSpec,
    decoded_frame: np.ndarray,
) -> FrameMeasurement:
    frame = _transform(decoded_frame, spec)
    detector = OpenCvPhaseDetector()
    detection, artifacts = detector.detect(
        frame,
        case.glass,
        case.frame_index,
        case.timestamp_sec,
        debug=True,
    )
    if artifacts is None:
        raise RuntimeError(f"Debug artifacts unavailable for {case.case_id}")
    interface_diagnostics = artifacts.state.get("oil_interface_diagnostics")
    if not isinstance(interface_diagnostics, dict):
        raise RuntimeError(f"Interface diagnostics unavailable for {case.case_id}")
    measurements: list[CandidateMeasurement] = []
    for diagnostic in interface_diagnostics.get("candidates", []):
        index = int(diagnostic["candidate_input_index"])
        if not 0 <= index < len(detection.candidates):
            raise RuntimeError(f"Candidate join failed for {case.case_id}:{index}")
        candidate = detection.candidates[index]
        if (candidate.source != diagnostic["source"] or candidate.y != diagnostic["canonical_y"]):
            raise RuntimeError(f"Candidate provenance mismatch for {case.case_id}:{index}")
        measured = _candidate_measurement(
            diagnostic,
            detection.candidates[index],
            case.truth_y,
        )
        if measured is not None:
            measurements.append(measured)
    measurements.sort(
        key=lambda value: (
            value.distance_to_truth_px,
            value.source,
            value.canonical_y,
            value.candidate_input_index,
        )
    )
    nearest = measurements[0] if measurements else None
    return FrameMeasurement(
        case_id=case.case_id,
        sample=case.sample,
        frame_index=case.frame_index,
        timestamp_sec=case.timestamp_sec,
        transform=spec.name,
        truth_y=case.truth_y,
        oil_candidate_count=len(measurements),
        near_truth_candidate_count=sum(
            value.distance_partition == "near_truth_geometry" for value in measurements
        ),
        nearest_candidate_error_px=(
            nearest.distance_to_truth_px if nearest is not None else None
        ),
        nearest_candidate_source=nearest.source if nearest is not None else None,
        candidates=tuple(measurements),
    )


def _distribution(values: Iterable[float | None]) -> dict[str, float | int | None]:
    finite = sorted(
        float(value) for value in values if value is not None and math.isfinite(float(value))
    )
    if not finite:
        return {"count": 0, "minimum": None, "median": None, "maximum": None}
    return {
        "count": len(finite),
        "minimum": finite[0],
        "median": float(median(finite)),
        "maximum": finite[-1],
    }


def _summary(rows: tuple[FrameMeasurement, ...]) -> dict[str, object]:
    by_transform: dict[str, list[FrameMeasurement]] = {}
    for row in rows:
        by_transform.setdefault(row.transform, []).append(row)
    transforms: dict[str, object] = {}
    for name, group in sorted(by_transform.items()):
        candidates = [candidate for row in group for candidate in row.candidates]
        near = [
            value
            for value in candidates
            if value.distance_partition == "near_truth_geometry"
        ]
        remote = [
            value
            for value in candidates
            if value.distance_partition == "remote_geometry_not_proven_negative"
        ]
        transforms[name] = {
            "annotation_count": len(group),
            "candidate_recall_within_8px_count": sum(
                row.nearest_candidate_error_px is not None
                and row.nearest_candidate_error_px <= NEAR_TRUTH_TOLERANCE_PX
                for row in group
            ),
            "nearest_candidate_error_px": _distribution(
                row.nearest_candidate_error_px for row in group
            ),
            "oil_candidate_count_per_frame": _distribution(
                float(row.oil_candidate_count) for row in group
            ),
            "near_truth_candidate_count_per_frame": _distribution(
                float(row.near_truth_candidate_count) for row in group
            ),
            "near_truth_geometry": {
                "candidate_count": len(near),
                "median_near_abs_contrast": _distribution(
                    value.median_near_abs_contrast for value in near
                ),
                "median_far_abs_contrast": _distribution(
                    value.median_far_abs_contrast for value in near
                ),
                "median_near_minus_far_abs_contrast": _distribution(
                    value.median_near_minus_far_abs_contrast for value in near
                ),
                "median_peak_abs_offset_px": _distribution(
                    value.median_peak_abs_offset_px for value in near
                ),
            },
            "remote_geometry_not_proven_negative": {
                "candidate_count": len(remote),
                "median_near_abs_contrast": _distribution(
                    value.median_near_abs_contrast for value in remote
                ),
                "median_far_abs_contrast": _distribution(
                    value.median_far_abs_contrast for value in remote
                ),
                "median_near_minus_far_abs_contrast": _distribution(
                    value.median_near_minus_far_abs_contrast for value in remote
                ),
                "median_peak_abs_offset_px": _distribution(
                    value.median_peak_abs_offset_px for value in remote
                ),
            },
        }
    return {
        "case_count": len({row.case_id for row in rows}),
        "measurement_count": len(rows),
        "transforms": transforms,
    }


def run(root: Path, transform_names: tuple[str, ...]) -> dict[str, object]:
    expected = authoritative_input_hashes(root)
    actual = {
        sample: {
            suffix: _sha256(root / "sample" / f"{sample}.{suffix}")
            for suffix in ("mp4", "oilrecipe", "oiltruth")
        }
        for sample in CORPUS_STEMS
    }
    if actual != expected:
        raise RuntimeError("S11 public probe input hashes do not match the manifest")
    cases = _load_cases(root)
    decoded_frames = {case.case_id: _decode(case) for case in cases}
    rows = tuple(
        _probe(case, TRANSFORMS[transform_name], decoded_frames[case.case_id])
        for transform_name in transform_names
        for case in cases
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "detector_runtime": OpenCvPhaseDetector.version,
        "diagnostic_schema": INTERFACE_DIAGNOSTICS_SCHEMA,
        "source_identity": source_identity(root),
        "runtime_provenance": {sample: capture_runtime_provenance(root / "sample" / f"{sample}.mp4") for sample in CORPUS_STEMS},
        "measurement_scope": {
            "frame_local": True,
            "fresh_detector_per_truth_frame": True,
            "static_artifact_learning": False,
            "completed_sequence_resolution": False,
            "distance_partition_is_physical_identity_label": False,
            "classification_or_threshold_selection": False,
            "near_truth_tolerance_px": NEAR_TRUTH_TOLERANCE_PX,
            "remote_distance_px": REMOTE_DISTANCE_PX,
        },
        "input_hashes_match_manifest": actual == expected,
        "expected_input_hashes": expected,
        "actual_input_hashes": actual,
        "transform_order": list(transform_names),
        "summary": _summary(rows),
        "frames": [asdict(row) for row in rows],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Measure existing R22-2 interface diagnostics around public truth geometry "
            "without changing detector authority or selecting thresholds."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=repository_root(),
        help="Repository root (defaults to the current checkout).",
    )
    parser.add_argument(
        "--transforms",
        default="original",
        help=(
            "Comma-separated transform names. Available: "
            + ", ".join(sorted(TRANSFORMS))
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="JSON output path.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    names = tuple(value.strip() for value in args.transforms.split(",") if value.strip())
    unknown = sorted(set(names) - set(TRANSFORMS))
    if not names or unknown:
        raise SystemExit(f"Invalid transforms: {unknown or names}")
    payload = run(args.root.resolve(), names)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2, allow_nan=False))
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
