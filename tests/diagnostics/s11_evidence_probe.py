from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from statistics import median
import sys
import time
from unittest.mock import patch

import cv2
import numpy as np

from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.adapters.storage.json_truth_repository import JsonTruthRepository
from oil_tracker.adapters.vision import oil_shadow_observations as observations
from oil_tracker.adapters.vision.foam_front_detector import detect_bottom_connected_foam
from oil_tracker.adapters.vision.foam_temporal_gate import FoamTemporalGate
from oil_tracker.adapters.vision.geometry_masks import build_mask_bundle
from oil_tracker.adapters.vision.oil_hypothesis_projection import project_production_result
from oil_tracker.adapters.vision.oil_shadow_pipeline import _FixedCanonicalReducer
from oil_tracker.adapters.vision.oil_shadow_temporal import GlassTemporalRecord
from oil_tracker.adapters.vision.oil_shadow_types import (
    BroadEvidenceSummary,
    BroadScaleEvidence,
    OilShadowBounds,
    ShadowAmbiguousObservation,
    ShadowBoundaryObservation,
    ShadowNoInterfaceEvidence,
    ShadowNoInterfaceObservation,
    ShadowSourceFamily,
    SuccessfulPipelineFrame,
)
from oil_tracker.adapters.vision.preprocessing import preprocess
from oil_tracker.adapters.vision.row_features import masked_band_intensity_profiles, masked_row_mean
from oil_tracker.domain.recipe import GlassInspectionConfig


BASELINE_MAIN_SHA = "0fd8ca0d423a1f632ad9a026d8f396686870d633"
CORPUS_STEMS = ("base_sample_1", "sample2", "sample3", "sample4")
CORPUS_MANIFEST_RELATIVE_PATH = Path(
    "docs/30-quality/s11-a-opencv-evidence-architecture-probe-manifest.json"
)
VARIANTS = ("P0", "P1", "P2", "P3")


class LocalCorpusUnavailableError(RuntimeError):
    """Required ignored S11 MP4 corpus is not present in this checkout."""


class LocalCorpusIdentityError(RuntimeError):
    """A present S11 MP4 does not match the frozen authoritative identity."""


@dataclass(frozen=True)
class TransformSpec:
    name: str
    kind: str
    value: float


TRANSFORMS = (
    TransformSpec("brightness_1.00", "brightness", 1.00),
    TransformSpec("brightness_0.80", "brightness", 0.80),
    TransformSpec("brightness_0.60", "brightness", 0.60),
    TransformSpec("brightness_0.45", "brightness", 0.45),
    TransformSpec("gamma_0.80", "gamma", 0.80),
    TransformSpec("gamma_1.25", "gamma", 1.25),
    TransformSpec("contrast_0.80", "contrast", 0.80),
    TransformSpec("contrast_1.20", "contrast", 1.20),
)


@dataclass(frozen=True)
class ProbeCase:
    sample: str
    frame_index: int
    time_sec: float
    truth_oil_y: float
    truth_foam_present: bool
    truth_foam_y: float | None
    glass: GlassInspectionConfig
    video_path: Path

    @property
    def case_id(self) -> str:
        return f"{self.sample}:{self.frame_index}"


@dataclass(frozen=True)
class ProbeResult:
    case_id: str
    sample: str
    frame_index: int
    transform: str
    variant: str
    truth_oil_y: float
    oil_y: float | None
    oil_error_px: float | None
    current_kind: str
    no_interface_likelihood: float
    foam_y: float | None
    foam_truth_present: bool
    raw_observation_count: int
    proposal_count: int
    hypothesis_count: int
    elapsed_ms: float


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def authoritative_mp4_hashes(root: Path) -> dict[str, str]:
    manifest_path = Path(root) / CORPUS_MANIFEST_RELATIVE_PATH
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    inputs = manifest["inputs"]
    return {sample: str(inputs[sample]["mp4"]) for sample in CORPUS_STEMS}


def validate_local_corpus(root: Path) -> None:
    root = Path(root)
    expected_hashes = authoritative_mp4_hashes(root)
    missing: list[str] = []
    mismatches: list[str] = []
    for sample in CORPUS_STEMS:
        path = root / "sample" / f"{sample}.mp4"
        if not path.is_file():
            missing.append(path.as_posix())
            continue
        actual = file_sha256(path)
        expected = expected_hashes[sample]
        if actual != expected:
            mismatches.append(f"{path.as_posix()} expected={expected} actual={actual}")
    if mismatches:
        raise LocalCorpusIdentityError(
            "S11 local corpus identity mismatch: " + "; ".join(mismatches)
        )
    if missing:
        raise LocalCorpusUnavailableError(
            "S11 local corpus NOT AVAILABLE; missing required MP4: " + ", ".join(missing)
        )


def load_cases(root: Path) -> tuple[ProbeCase, ...]:
    root = Path(root)
    validate_local_corpus(root)
    recipe_repo = JsonRecipeRepository()
    truth_repo = JsonTruthRepository()
    cases: list[ProbeCase] = []
    for sample in CORPUS_STEMS:
        recipe = recipe_repo.load(root / "sample" / f"{sample}.oilrecipe")
        truth = truth_repo.load(root / "sample" / f"{sample}.oiltruth").truth_set
        glass = recipe.glasses[0]
        for annotation in truth.annotations:
            if annotation.disposition.value == "unusable":
                continue
            if annotation.oil_boundary is None:
                raise ValueError(f"Usable truth lacks Oil geometry: {sample}:{annotation.frame_index}")
            cases.append(
                ProbeCase(
                    sample=sample,
                    frame_index=int(annotation.frame_index),
                    time_sec=float(annotation.actual_decoded_timestamp_sec),
                    truth_oil_y=float(annotation.oil_boundary.source_frame_y),
                    truth_foam_present=bool(annotation.foam_present),
                    truth_foam_y=(
                        None if annotation.foam_front is None
                        else float(annotation.foam_front.source_frame_y)
                    ),
                    glass=glass,
                    video_path=root / "sample" / f"{sample}.mp4",
                )
            )
    return tuple(cases)


def decode_frame(case: ProbeCase) -> np.ndarray:
    capture = cv2.VideoCapture(str(case.video_path))
    capture.set(cv2.CAP_PROP_POS_FRAMES, case.frame_index)
    ok, frame = capture.read()
    capture.release()
    if not ok or frame is None:
        raise RuntimeError(f"Could not decode {case.case_id}")
    return frame


def transform_frame(frame: np.ndarray, spec: TransformSpec) -> np.ndarray:
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


def _relative_signed_profile(profiles) -> np.ndarray:
    denominator = np.maximum(np.abs(profiles.above) + np.abs(profiles.below), 1.0)
    relative = 2.0 * profiles.signed_difference / denominator
    return np.where(profiles.available, np.clip(relative, -1.0, 1.0), 0.0)


def _relative_region_observations(pre, effective_mask: np.ndarray, bounds: OilShadowBounds, crop_origin_y: float):
    production = observations.extract_raw_observations(
        pre, effective_mask, crop_origin_y=crop_origin_y, bounds=bounds
    )
    retained = [item for item in production if item.source_family is not ShadowSourceFamily.REGION_STEP]
    effective = effective_mask > 0
    visible = effective & ~(pre.glare_mask > 0)
    _height, width = effective.shape
    valid_support = effective.sum(axis=1).astype(np.float64) / max(1, width)
    visible_support = np.divide(
        visible.sum(axis=1).astype(np.float64), np.maximum(1, effective.sum(axis=1))
    )
    for band in bounds.broad_band_scales:
        profiles = masked_band_intensity_profiles(
            pre.blurred, visible, band, reference_mask=effective,
            minimum_fraction=0.40, minimum_pixels=5,
        )
        signed = _relative_signed_profile(profiles)
        strength = np.where(profiles.available, np.abs(signed), 0.0)
        retained.extend(
            observations._profile_observations(
                ShadowSourceFamily.REGION_STEP, band, strength, signed,
                valid_support, visible_support, crop_origin_y, width, bounds,
                availability=profiles.available, band_height=float(band),
                horizontal_support=valid_support,
            )
        )
    return tuple(sorted(retained, key=lambda item: item.canonical_key)[: bounds.total_raw_observations])


def _relative_broad_summary(proposal, profiles_by_scale, bounds: OilShadowBounds) -> BroadEvidenceSummary:
    rows: list[BroadScaleEvidence] = []
    height = next(iter(profiles_by_scale.values()))[1].size
    center = int(round(proposal.representative_local_y))
    search = range(max(0, center - 2), min(height, center + 3))
    for scale in bounds.broad_band_scales:
        profiles, visible_support, glare, exclusion = profiles_by_scale[scale]
        signed_profile = _relative_signed_profile(profiles)
        candidates = []
        for row in search:
            available = bool(profiles.available[row])
            signed = float(signed_profile[row]) if available else 0.0
            candidates.append((
                -abs(signed), row, available, signed,
                observations._unit(visible_support[row]), observations._unit(glare[row]),
                observations._unit(exclusion[row]),
            ))
        _negative, row, available, signed, visible, glare_value, exclusion_value = min(candidates)
        transition_y = min(proposal.maximum_local_y, max(proposal.minimum_local_y, float(row)))
        rows.append(BroadScaleEvidence(
            band_scale=scale, available=available, signed_contrast=signed,
            strength=abs(signed) if available else 0.0, visible_support=visible,
            glare_conflict=glare_value, exclusion_conflict=exclusion_value,
            transition_local_y=transition_y,
        ))
    available_rows = [item for item in rows if item.available]
    strengths = [item.strength for item in available_rows]
    signs = [1.0 if item.signed_contrast > 0.0 else -1.0 for item in available_rows if abs(item.signed_contrast) > 1e-12]
    scale_consistency = 0.0 if not strengths else observations._unit(1.0 - (max(strengths) - min(strengths)))
    polarity_consistency = 0.0 if not signs else max(signs.count(1.0), signs.count(-1.0)) / len(signs)
    signed = 0.0 if not available_rows else sum(item.signed_contrast for item in available_rows) / len(available_rows)
    strength = 0.0 if not strengths else observations._unit(sum(strengths) / len(strengths) * (0.55 + 0.45 * scale_consistency))
    transition = proposal.representative_local_y if not available_rows else float(median(item.transition_local_y for item in available_rows))
    visibility = 0.0 if not rows else observations._unit(sum(item.visible_support for item in rows) / len(rows))
    glare_value = 0.0 if not rows else observations._unit(sum(item.glare_conflict for item in rows) / len(rows))
    exclusion_value = 0.0 if not rows else observations._unit(sum(item.exclusion_conflict for item in rows) / len(rows))
    return BroadEvidenceSummary(
        scales=tuple(rows), available_scale_count=len(available_rows),
        signed_contrast=observations._signed_unit(signed), strength=strength,
        scale_consistency=scale_consistency, polarity_consistency=observations._unit(polarity_consistency),
        transition_local_y=transition, visibility=visibility, glare_conflict=glare_value,
        exclusion_conflict=exclusion_value,
    )

def _relative_hypotheses(proposals, raw, pre, bundle, bounds: OilShadowBounds):
    observation_by_id = {item.identity: item for item in raw}
    broad_profiles = observations._broad_profiles(pre, bundle.effective_mask, bundle.exclusion_mask, bounds)
    narrow_context = observations._narrow_context(
        pre, bundle.effective_mask, bundle.ellipse_mask, bundle.exclusion_mask, None, bounds
    )
    plateau_context = observations._build_plateau_evidence_context(pre.gray, bundle.effective_mask) if proposals else None
    hypotheses = []
    for proposal in proposals:
        members = tuple(observation_by_id[item] for item in proposal.member_ids)
        broad = _relative_broad_summary(proposal, broad_profiles, bounds)
        narrow = observations._narrow_summary(proposal, narrow_context, bounds)
        static_prior = observations._static_prior(narrow, broad, None, bounds)
        plateau = observations._plateau_artifact_from_context(plateau_context, broad.transition_local_y)
        hypotheses.append(
            observations._semantic_hypothesis(
                proposal, members, broad, narrow, static_prior, plateau,
                float(bundle.crop_origin[1]),
            )
        )
    return observations.semantic_deduplicate(tuple(hypotheses), bounds)


def _p0_no_interface(pre, effective_mask: np.ndarray, hypotheses) -> ShadowNoInterfaceEvidence:
    valid = effective_mask > 0
    count = int(np.count_nonzero(valid))
    if count == 0:
        return ShadowNoInterfaceEvidence(
            False, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, None, None,
            "empty_effective_mask",
        )
    glare = (pre.glare_mask > 0) & valid
    visible = valid & ~glare
    visible_count = int(np.count_nonzero(visible))
    visibility = observations._unit(visible_count / max(1, count))
    glare_conflict = observations._unit(np.count_nonzero(glare) / max(1, count))
    competing = max((item.boundary_likelihood for item in hypotheses), default=0.0)
    if visible_count < max(10, int(count * 0.08)):
        return ShadowNoInterfaceEvidence(
            False, 0.0, 0.0, 0.0, 0.0, 0.0, competing, visibility,
            glare_conflict, None, None, "insufficient_visible_support",
        )
    values = pre.gray[visible].astype(np.float32)
    mean_intensity = float(np.median(values))
    texture = float(np.std(values))
    uniformity = observations._unit(1.0 - texture / 58.0)
    row_energy = observations._normalize_profile(masked_row_mean(pre.sobel_y_abs, visible))
    raster_weakness = observations._unit(1.0 - float(np.max(row_energy)))
    weak_boundary = observations._unit(0.58 * (1.0 - competing) + 0.42 * raster_weakness)
    full = observations._unit((145.0 - mean_intensity) / 55.0) * uniformity
    empty = observations._unit((mean_intensity - 115.0) / 70.0) * uniformity
    state_evidence = max(full, empty)
    likelihood = observations._unit(
        0.36 * weak_boundary + 0.27 * uniformity + 0.20 * visibility
        + 0.17 * state_evidence - 0.30 * glare_conflict - 0.38 * competing
    )
    if competing >= 0.72:
        reason = "strong_competing_boundary"
    elif glare_conflict >= 0.45:
        reason = "glare_visibility_conflict"
    elif state_evidence >= 0.45 and uniformity >= 0.65:
        reason = "positive_uniform_full_or_empty_evidence"
    else:
        reason = "mixed_no_interface_evidence"
    return ShadowNoInterfaceEvidence(
        True, likelihood, observations._unit(full), observations._unit(empty),
        uniformity, weak_boundary, observations._unit(competing), visibility,
        glare_conflict, mean_intensity, texture, reason,
    )


def _p2_no_interface(pre, effective_mask: np.ndarray, hypotheses) -> ShadowNoInterfaceEvidence:
    valid = effective_mask > 0
    count = int(np.count_nonzero(valid))
    if count == 0:
        return ShadowNoInterfaceEvidence(
            False, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, None, None,
            "empty_effective_mask",
        )
    glare = (pre.glare_mask > 0) & valid
    visible = valid & ~glare
    visible_count = int(np.count_nonzero(visible))
    visibility = observations._unit(visible_count / max(1, count))
    glare_conflict = observations._unit(np.count_nonzero(glare) / max(1, count))
    competing = max((item.boundary_likelihood for item in hypotheses), default=0.0)
    if visible_count < max(10, int(count * 0.08)):
        return ShadowNoInterfaceEvidence(
            False, 0.0, 0.0, 0.0, 0.0, 0.0, competing, visibility,
            glare_conflict, None, None, "insufficient_visible_support",
        )
    raw_values = pre.gray[visible].astype(np.float32)
    normalized_values = pre.normalized[visible].astype(np.float32)
    mean_intensity = float(np.median(raw_values))
    texture = float(np.std(normalized_values))
    uniformity = observations._unit(1.0 - texture / 58.0)
    row_energy = observations._normalize_profile(masked_row_mean(pre.sobel_y_abs, visible))
    raster_weakness = observations._unit(1.0 - float(np.max(row_energy)))
    weak_boundary = observations._unit(0.58 * (1.0 - competing) + 0.42 * raster_weakness)
    diagnostic_texture = float(np.std(raw_values))
    full = observations._unit((145.0 - mean_intensity) / 55.0) * uniformity
    empty = observations._unit((mean_intensity - 115.0) / 70.0) * uniformity
    likelihood = observations._unit(
        0.36 * weak_boundary + 0.27 * uniformity + 0.20 * visibility
        - 0.30 * glare_conflict - 0.38 * competing
    )
    if competing >= 0.72:
        reason = "strong_competing_boundary"
    elif glare_conflict >= 0.45:
        reason = "glare_visibility_conflict"
    elif likelihood >= 0.58 and uniformity >= 0.65:
        reason = "positive_exposure_decoupled_absence_evidence"
    else:
        reason = "mixed_exposure_decoupled_absence_evidence"
    return ShadowNoInterfaceEvidence(
        True, likelihood, observations._unit(full), observations._unit(empty),
        uniformity, weak_boundary, observations._unit(competing), visibility,
        glare_conflict, mean_intensity, diagnostic_texture, reason,
    )


def _current_no_interface_likelihood(current) -> float:
    if isinstance(current, ShadowNoInterfaceObservation):
        return float(current.evidence.likelihood)
    if isinstance(current, ShadowAmbiguousObservation):
        return float(current.no_interface_likelihood)
    return 0.0


def _evaluate_current(pre, bundle, hypotheses, *, decoupled_absence: bool, foam_front, foam_mask):
    no_interface = (
        _p2_no_interface(pre, bundle.effective_mask, hypotheses)
        if decoupled_absence
        else _p0_no_interface(pre, bundle.effective_mask, hypotheses)
    )
    with patch.object(observations, "_no_interface_evidence", return_value=no_interface):
        return observations.evaluate_typed_current_observation(
            pre, bundle.effective_mask, hypotheses,
            accepted_foam_front_local_y=foam_front,
            accepted_foam_component_mask=foam_mask,
        )


def run_variant(frame: np.ndarray, case: ProbeCase, variant: str) -> ProbeResult:
    if variant not in VARIANTS:
        raise ValueError(f"Unsupported variant: {variant}")
    started = time.perf_counter_ns()
    glass = case.glass
    settings = glass.detector_settings
    bundle = build_mask_bundle(frame, glass)
    pre = preprocess(bundle.crop, bundle.effective_mask, settings)
    foam = detect_bottom_connected_foam(
        bundle.crop, pre.gray, pre.canny, pre.glare_mask,
        bundle.effective_mask, settings,
    )
    foam_temporal = FoamTemporalGate().evaluate(glass.id, foam, settings)
    foam_candidate = foam_temporal.candidate
    accepted_foam_front_local_y = None if foam_candidate is None else float(foam_candidate.y)
    accepted_foam_component_mask = None if foam_candidate is None else foam.mask
    bounds = OilShadowBounds()
    relative_phase = variant in {"P1", "P3"}
    decoupled_absence = variant in {"P2", "P3"}
    raw = observations.extract_raw_observations(
        pre, bundle.effective_mask,
        crop_origin_y=float(bundle.crop_origin[1]), bounds=bounds,
    )
    proposals = observations.build_bounded_proposals(raw, bounds)
    hypotheses = observations.evaluate_semantic_hypotheses(
        proposals, raw, pre, bundle.effective_mask, bundle.ellipse_mask,
        bundle.exclusion_mask, None,
        crop_origin_y=float(bundle.crop_origin[1]), bounds=bounds,
    )
    current = _evaluate_current(
        pre, bundle, hypotheses, decoupled_absence=decoupled_absence,
        foam_front=accepted_foam_front_local_y, foam_mask=accepted_foam_component_mask,
    )
    if relative_phase and isinstance(current, ShadowAmbiguousObservation):
        relative_raw = _relative_region_observations(
            pre, bundle.effective_mask, bounds, float(bundle.crop_origin[1])
        )
        relative_proposals = observations.build_bounded_proposals(relative_raw, bounds)
        relative_hypotheses = _relative_hypotheses(
            relative_proposals, relative_raw, pre, bundle, bounds
        )
        relative_current = _evaluate_current(
            pre, bundle, relative_hypotheses, decoupled_absence=decoupled_absence,
            foam_front=accepted_foam_front_local_y, foam_mask=accepted_foam_component_mask,
        )
        if isinstance(relative_current, ShadowBoundaryObservation):
            raw = relative_raw
            proposals = relative_proposals
            hypotheses = relative_hypotheses
            current = relative_current
    pipeline_frame = SuccessfulPipelineFrame(
        raw_observations=raw, proposals=proposals, hypotheses=hypotheses,
        current_observation=current, frame_height=pre.gray.shape[0],
        frame_width=pre.gray.shape[1],
    )
    reduction = _FixedCanonicalReducer(bounds).reduce(
        GlassTemporalRecord.initial(glass.id), pipeline_frame
    )
    projection = project_production_result(reduction.outcome)
    oil_y = None if projection.raw_source_y is None else float(projection.raw_source_y)
    oil_error = None if oil_y is None else abs(oil_y - case.truth_oil_y)
    foam_y = (
        None if foam_candidate is None
        else float(foam_candidate.y + bundle.crop_origin[1])
    )
    elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000.0
    return ProbeResult(
        case_id=case.case_id, sample=case.sample, frame_index=case.frame_index,
        transform="", variant=variant, truth_oil_y=case.truth_oil_y,
        oil_y=oil_y, oil_error_px=oil_error, current_kind=current.kind.value,
        no_interface_likelihood=_current_no_interface_likelihood(current),
        foam_y=foam_y, foam_truth_present=case.truth_foam_present,
        raw_observation_count=len(raw), proposal_count=len(proposals),
        hypothesis_count=len(hypotheses), elapsed_ms=elapsed_ms,
    )


def run_experiment(root: Path | None = None) -> tuple[ProbeResult, ...]:
    root = repository_root() if root is None else Path(root)
    cases = load_cases(root)
    results: list[ProbeResult] = []
    decoded = {case.case_id: decode_frame(case) for case in cases}
    for spec in TRANSFORMS:
        for case in cases:
            transformed = transform_frame(decoded[case.case_id], spec)
            for variant in VARIANTS:
                row = run_variant(transformed, case, variant)
                results.append(
                    ProbeResult(**{**asdict(row), "transform": spec.name})
                )
    return tuple(results)


def _aggregate(rows: tuple[ProbeResult, ...]) -> dict[str, object]:
    numeric = [row for row in rows if row.oil_y is not None]
    errors = [row.oil_error_px for row in numeric if row.oil_error_px is not None]
    foam_truth_count = sum(row.foam_truth_present for row in rows)
    foam_detected_truth = sum(row.foam_truth_present and row.foam_y is not None for row in rows)
    foam_false_positive = sum((not row.foam_truth_present) and row.foam_y is not None for row in rows)
    return {
        "count": len(rows),
        "oil_coverage": len(numeric),
        "oil_mae_px": None if not errors else sum(errors) / len(errors),
        "false_no_interface": sum(row.current_kind == "no_interface" for row in rows),
        "unknown_or_ambiguous": sum(row.current_kind == "ambiguous" for row in rows),
        "foam_truth_count": foam_truth_count,
        "foam_detected_truth": foam_detected_truth,
        "foam_false_positive": foam_false_positive,
        "max_raw_observations": max(row.raw_observation_count for row in rows),
        "max_proposals": max(row.proposal_count for row in rows),
        "max_hypotheses": max(row.hypothesis_count for row in rows),
    }


def _canonical_result_payload(rows: tuple[ProbeResult, ...]) -> list[dict[str, object]]:
    payload = []
    for row in sorted(rows, key=lambda item: (item.transform, item.case_id, item.variant)):
        item = asdict(row)
        item.pop("elapsed_ms")
        payload.append(item)
    return payload


def build_manifest(results: tuple[ProbeResult, ...], root: Path | None = None) -> dict[str, object]:
    root = repository_root() if root is None else Path(root)
    validate_local_corpus(root)
    canonical = _canonical_result_payload(results)
    fingerprint = sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    aggregate = {}
    for spec in TRANSFORMS:
        aggregate[spec.name] = {}
        for variant in VARIANTS:
            selected = tuple(
                row for row in results
                if row.transform == spec.name and row.variant == variant
            )
            aggregate[spec.name][variant] = _aggregate(selected)
    key_case_ids = {
        "base_sample_1:144", "base_sample_1:156", "base_sample_1:240",
        "sample2:0", "sample2:30", "sample2:60",
        "sample3:900", "sample3:1035",
        "sample4:0", "sample4:450", "sample4:900", "sample4:1470", "sample4:1680",
    }
    key_rows = [
        item for item in canonical
        if item["case_id"] in key_case_ids
        and item["transform"] in {"brightness_1.00", "brightness_0.80", "brightness_0.60", "brightness_0.45"}
    ]
    inputs = {}
    for sample in CORPUS_STEMS:
        inputs[sample] = {
            suffix: file_sha256(root / "sample" / f"{sample}.{suffix}")
            for suffix in ("mp4", "oilrecipe", "oiltruth")
        }
    return {
        "schema": "s11-a-evidence-probe-v1",
        "baseline_main_sha": BASELINE_MAIN_SHA,
        "inputs": inputs,
        "transforms": [asdict(item) for item in TRANSFORMS],
        "variants": list(VARIANTS),
        "result_fingerprint_sha256": fingerprint,
        "aggregate": aggregate,
        "key_cases": key_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the S11-A detector evidence architecture probe.")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        results = run_experiment()
    except LocalCorpusUnavailableError as exc:
        print(f"NOT AVAILABLE: {exc}", file=sys.stderr)
        return 2
    manifest = build_manifest(results)
    encoded = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(encoded, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
        print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
