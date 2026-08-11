from __future__ import annotations

from dataclasses import dataclass
import math

import cv2
import numpy as np


@dataclass(frozen=True)
class RegisteredFoamMotionEvidence:
    available: bool = False
    exact_overlap: float = 0.0
    tolerant_overlap: float = 0.0
    reciprocal_overlap: float = 0.0
    mask_turnover: float = 0.0
    area_change_ratio: float = 0.0
    front_delta_ratio: float = 0.0
    internal_motion_ratio: float = 0.0
    internal_motion_support: float = 0.0
    dynamic_support: float = 0.0
    registration_dx: float = 0.0
    registration_dy: float = 0.0
    registration_response: float = 0.0
    exposure_gain: float = 1.0
    exposure_offset: float = 0.0


@dataclass(frozen=True)
class RegisteredOilRasterEvidence:
    """Registered adjacent-frame change available for row-local Oil queries."""

    available: bool = False
    changed: np.ndarray | None = None
    residual_support: np.ndarray | None = None
    common: np.ndarray | None = None
    registration_dx: float = 0.0
    registration_dy: float = 0.0
    registration_response: float = 0.0
    exposure_gain: float = 1.0
    exposure_offset: float = 0.0


@dataclass
class _RasterState:
    gray: np.ndarray
    effective: np.ndarray
    foam: np.ndarray
    front_y: float | None


class RegisteredFoamMotionTracker:
    """Measure Foam-internal change after camera/exposure compensation.

    The tracker retains one bounded ROI raster per Glass. It is evidence only:
    it neither publishes Foam nor mutates Oil state.
    """

    def __init__(self) -> None:
        self._states: dict[str, _RasterState] = {}

    @property
    def state_count(self) -> int:
        return len(self._states)

    def reset(self, glass_id: str | None = None) -> None:
        if glass_id is None:
            self._states.clear()
        else:
            self._states.pop(str(glass_id), None)

    def evaluate(
        self,
        glass_id: str,
        gray: np.ndarray,
        effective_mask: np.ndarray,
        foam_mask: np.ndarray,
        front_y: float | None,
    ) -> RegisteredFoamMotionEvidence:
        _validate_rasters(gray, effective_mask, foam_mask)
        current_gray = np.asarray(gray, dtype=np.float32)
        current_effective = np.asarray(effective_mask) > 0
        current_foam = (np.asarray(foam_mask) > 0) & current_effective
        key = str(glass_id)
        prior = self._states.get(key)
        evidence = RegisteredFoamMotionEvidence()
        if prior is not None and prior.gray.shape == current_gray.shape:
            evidence = _registered_motion(
                prior,
                current_gray,
                current_effective,
                current_foam,
                front_y,
            )
        self._states[key] = _owned_state(
            current_gray,
            current_effective,
            current_foam,
            front_y,
        )
        return evidence


class RegisteredOilMotionTracker:
    """Retain one ROI raster and expose only row-local registered change.

    The returned raster is transient detector evidence. It is never serialized,
    never selects a row itself and is not shared with Foam authority.
    """

    def __init__(self) -> None:
        self._states: dict[str, tuple[np.ndarray, np.ndarray]] = {}

    @property
    def state_count(self) -> int:
        return len(self._states)

    def reset(self, glass_id: str | None = None) -> None:
        if glass_id is None:
            self._states.clear()
        else:
            self._states.pop(str(glass_id), None)

    def evaluate(
        self,
        glass_id: str,
        gray: np.ndarray,
        effective_mask: np.ndarray,
    ) -> RegisteredOilRasterEvidence:
        if gray.ndim != 2 or effective_mask.shape != gray.shape:
            raise ValueError("Registered Oil rasters must share one two-dimensional shape.")
        current_gray = np.asarray(gray, dtype=np.float32)
        current_effective = np.asarray(effective_mask) > 0
        key = str(glass_id)
        prior = self._states.get(key)
        evidence = RegisteredOilRasterEvidence()
        if prior is not None and prior[0].shape == current_gray.shape:
            evidence = _registered_oil_raster(
                prior[0],
                prior[1],
                current_gray,
                current_effective,
            )
        owned_gray = np.array(current_gray, dtype=np.float32, copy=True)
        owned_effective = np.array(current_effective, dtype=bool, copy=True)
        owned_gray.setflags(write=False)
        owned_effective.setflags(write=False)
        self._states[key] = (owned_gray, owned_effective)
        return evidence


def registered_oil_candidate_features(
    evidence: RegisteredOilRasterEvidence,
    *,
    local_y: float,
) -> dict[str, float]:
    """Summarize registered change only in a candidate-centered horizontal band."""

    base = {
        "registered_oil_motion_available": float(evidence.available),
        "registered_oil_band_motion_ratio": 0.0,
        "registered_oil_band_motion_coverage": 0.0,
        "registered_oil_band_motion_support": 0.0,
        "registered_oil_dx": float(evidence.registration_dx),
        "registered_oil_dy": float(evidence.registration_dy),
        "registered_oil_response": float(evidence.registration_response),
        "registered_oil_exposure_gain": float(evidence.exposure_gain),
        "registered_oil_exposure_offset": float(evidence.exposure_offset),
    }
    if (
        not evidence.available
        or evidence.changed is None
        or evidence.residual_support is None
        or evidence.common is None
    ):
        return base
    height, width = evidence.changed.shape
    center = min(height - 1, max(0, int(round(float(local_y)))))
    half_band = max(3, min(10, int(round(height * 0.025))))
    start = max(0, center - half_band)
    stop = min(height, center + half_band + 1)
    common_band = evidence.common[start:stop]
    count = int(np.count_nonzero(common_band))
    if count < 12:
        return base
    changed_band = evidence.changed[start:stop]
    support_band = evidence.residual_support[start:stop]
    motion_ratio = float(np.count_nonzero(changed_band & common_band)) / count
    mean_support = float(np.mean(support_band[common_band]))

    sector_hits = 0
    sector_total = 0
    for sector in range(5):
        x0 = int(round(width * sector / 5.0))
        x1 = int(round(width * (sector + 1) / 5.0))
        sector_common = common_band[:, x0:x1]
        sector_count = int(np.count_nonzero(sector_common))
        if sector_count < 3:
            continue
        sector_total += 1
        sector_ratio = float(
            np.count_nonzero(changed_band[:, x0:x1] & sector_common)
        ) / sector_count
        sector_support = float(np.mean(support_band[:, x0:x1][sector_common]))
        if sector_ratio >= 0.025 or sector_support >= 0.08:
            sector_hits += 1
    coverage = sector_hits / max(1, sector_total)
    strength = _unit(max((motion_ratio - 0.012) / 0.16, mean_support))
    support = _unit(strength * (0.45 + 0.55 * coverage))
    return {
        **base,
        "registered_oil_band_motion_ratio": motion_ratio,
        "registered_oil_band_motion_coverage": coverage,
        "registered_oil_band_motion_support": support,
    }


def registered_foam_motion_features(
    evidence: RegisteredFoamMotionEvidence,
) -> dict[str, float]:
    return {
        "registered_motion_available": float(evidence.available),
        "registered_exact_overlap": float(evidence.exact_overlap),
        "registered_tolerant_overlap": float(evidence.tolerant_overlap),
        "registered_reciprocal_overlap": float(evidence.reciprocal_overlap),
        "registered_mask_turnover": float(evidence.mask_turnover),
        "registered_area_change_ratio": float(evidence.area_change_ratio),
        "registered_front_delta_ratio": float(evidence.front_delta_ratio),
        "registered_internal_motion_ratio": float(evidence.internal_motion_ratio),
        "registered_internal_motion_support": float(evidence.internal_motion_support),
        "registered_dynamic_support": float(evidence.dynamic_support),
        "registered_dx": float(evidence.registration_dx),
        "registered_dy": float(evidence.registration_dy),
        "registered_response": float(evidence.registration_response),
        "registered_exposure_gain": float(evidence.exposure_gain),
        "registered_exposure_offset": float(evidence.exposure_offset),
    }


def _registered_oil_raster(
    prior_gray: np.ndarray,
    prior_effective: np.ndarray,
    current_gray: np.ndarray,
    current_effective: np.ndarray,
) -> RegisteredOilRasterEvidence:
    common = prior_effective & current_effective
    if np.count_nonzero(common) < 32:
        return RegisteredOilRasterEvidence()
    direct_delta = np.abs(prior_gray - current_gray)
    if float(np.percentile(direct_delta[common], 99.0)) <= 1.0:
        zeros = np.zeros_like(current_gray, dtype=np.float32)
        changed = np.zeros_like(current_effective, dtype=bool)
        for value in (zeros, changed, common):
            value.setflags(write=False)
        return RegisteredOilRasterEvidence(
            available=True,
            changed=changed,
            residual_support=zeros,
            common=common,
        )

    dx, dy, response = _translation(prior_gray, current_gray, common)
    height, width = current_gray.shape
    transform = np.asarray(((1.0, 0.0, dx), (0.0, 1.0, dy)), dtype=np.float32)
    warped_gray = cv2.warpAffine(
        prior_gray,
        transform,
        (width, height),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REPLICATE,
    )
    warped_effective = cv2.warpAffine(
        prior_effective.astype(np.uint8),
        transform,
        (width, height),
        flags=cv2.INTER_NEAREST,
        borderValue=0,
    ) > 0
    common = warped_effective & current_effective
    if np.count_nonzero(common) < 32:
        return RegisteredOilRasterEvidence()

    gain, offset = _exposure_fit(warped_gray[common], current_gray[common])
    residual = np.abs(current_gray - (gain * warped_gray + offset))
    values = residual[common]
    median = float(np.median(values))
    mad = float(np.median(np.abs(values - median)))
    threshold = max(8.0, median + 3.0 * max(1.0, mad))
    upper = max(threshold + 1.0, float(np.percentile(values, 95.0)))
    changed = (residual >= threshold) & common
    residual_support = np.where(
        common,
        np.clip((residual - threshold) / (upper - threshold), 0.0, 1.0),
        0.0,
    ).astype(np.float32)
    owned_changed = np.array(changed, dtype=bool, copy=True)
    owned_support = np.array(residual_support, dtype=np.float32, copy=True)
    owned_common = np.array(common, dtype=bool, copy=True)
    for value in (owned_changed, owned_support, owned_common):
        value.setflags(write=False)
    return RegisteredOilRasterEvidence(
        available=True,
        changed=owned_changed,
        residual_support=owned_support,
        common=owned_common,
        registration_dx=dx,
        registration_dy=dy,
        registration_response=response,
        exposure_gain=gain,
        exposure_offset=offset,
    )


def _registered_motion(
    prior: _RasterState,
    current_gray: np.ndarray,
    current_effective: np.ndarray,
    current_foam: np.ndarray,
    current_front_y: float | None,
) -> RegisteredFoamMotionEvidence:
    common = prior.effective & current_effective
    if np.count_nonzero(common) < 32:
        return RegisteredFoamMotionEvidence()

    direct_delta = np.abs(prior.gray - current_gray)
    if (
        float(np.percentile(direct_delta[common], 99.0)) <= 1.0
        and np.array_equal(prior.foam & common, current_foam & common)
    ):
        present = bool(np.any(current_foam & common))
        return RegisteredFoamMotionEvidence(
            available=True,
            exact_overlap=1.0 if present else 0.0,
            tolerant_overlap=1.0 if present else 0.0,
            reciprocal_overlap=1.0 if present else 0.0,
        )

    dx, dy, response = _translation(
        prior.gray,
        current_gray,
        common,
    )
    height, width = current_gray.shape
    transform = np.asarray(((1.0, 0.0, dx), (0.0, 1.0, dy)), dtype=np.float32)
    warped_gray = cv2.warpAffine(
        prior.gray,
        transform,
        (width, height),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REPLICATE,
    )
    warped_effective = cv2.warpAffine(
        prior.effective.astype(np.uint8),
        transform,
        (width, height),
        flags=cv2.INTER_NEAREST,
        borderValue=0,
    ) > 0
    warped_foam = cv2.warpAffine(
        prior.foam.astype(np.uint8),
        transform,
        (width, height),
        flags=cv2.INTER_NEAREST,
        borderValue=0,
    ) > 0
    common = warped_effective & current_effective
    if np.count_nonzero(common) < 32:
        return RegisteredFoamMotionEvidence()

    gain, offset = _exposure_fit(warped_gray[common], current_gray[common])
    residual = np.abs(current_gray - (gain * warped_gray + offset))
    global_residual = residual[common]
    median = float(np.median(global_residual))
    mad = float(np.median(np.abs(global_residual - median)))
    threshold = max(8.0, median + 3.0 * max(1.0, mad))

    prior_count = int(np.count_nonzero(warped_foam))
    current_count = int(np.count_nonzero(current_foam))
    if prior_count == 0 or current_count == 0:
        return RegisteredFoamMotionEvidence(
            available=True,
            registration_dx=dx,
            registration_dy=dy,
            registration_response=response,
            exposure_gain=gain,
            exposure_offset=offset,
        )

    radius = max(1, min(3, int(round(min(height, width) * 0.01))))
    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (2 * radius + 1, 2 * radius + 1),
    )
    dilated_prior = cv2.dilate(warped_foam.astype(np.uint8), kernel) > 0
    dilated_current = cv2.dilate(current_foam.astype(np.uint8), kernel) > 0
    intersection = int(np.count_nonzero(warped_foam & current_foam))
    union = int(np.count_nonzero(warped_foam | current_foam))
    exact = intersection / max(1, union)
    tolerant = float(np.count_nonzero(current_foam & dilated_prior)) / current_count
    reciprocal = float(np.count_nonzero(warped_foam & dilated_current)) / prior_count
    turnover = _unit(1.0 - min(tolerant, reciprocal))
    area_change = _unit(abs(current_count - prior_count) / max(prior_count, current_count))

    material_region = (current_foam | warped_foam) & common
    material_count = int(np.count_nonzero(material_region))
    motion_ratio = (
        0.0
        if material_count == 0
        else float(np.count_nonzero((residual >= threshold) & material_region))
        / material_count
    )
    internal_support = _unit((motion_ratio - 0.025) / 0.225)

    front_delta = 0.0
    if prior.front_y is not None and current_front_y is not None:
        registered_prior_front = float(prior.front_y) + dy
        front_delta = _unit(
            abs(float(current_front_y) - registered_prior_front)
            / max(1.0, height * 0.15)
        )

    # Shape/front change may strengthen real internal motion but cannot create
    # dynamics by itself. This is the key distinction from R5 mask turnover.
    coupled_shape = min(
        internal_support,
        0.55 * turnover + 0.25 * area_change + 0.20 * front_delta,
    )
    dynamic = _unit(max(internal_support, internal_support * 0.75 + coupled_shape * 0.50))
    return RegisteredFoamMotionEvidence(
        available=True,
        exact_overlap=exact,
        tolerant_overlap=tolerant,
        reciprocal_overlap=reciprocal,
        mask_turnover=turnover,
        area_change_ratio=area_change,
        front_delta_ratio=front_delta,
        internal_motion_ratio=motion_ratio,
        internal_motion_support=internal_support,
        dynamic_support=dynamic,
        registration_dx=dx,
        registration_dy=dy,
        registration_response=response,
        exposure_gain=gain,
        exposure_offset=offset,
    )


def _translation(
    prior_gray: np.ndarray,
    current_gray: np.ndarray,
    common: np.ndarray,
) -> tuple[float, float, float]:
    prior_values = prior_gray[common]
    current_values = current_gray[common]
    prior_centered = np.where(
        common,
        prior_gray - float(np.median(prior_values)),
        0.0,
    ).astype(np.float32)
    current_centered = np.where(
        common,
        current_gray - float(np.median(current_values)),
        0.0,
    ).astype(np.float32)
    prior_centered = cv2.GaussianBlur(prior_centered, (5, 5), 0)
    current_centered = cv2.GaussianBlur(current_centered, (5, 5), 0)
    try:
        (dx, dy), response = cv2.phaseCorrelate(prior_centered, current_centered)
    except cv2.error:
        return 0.0, 0.0, 0.0
    if not all(math.isfinite(value) for value in (dx, dy, response)):
        return 0.0, 0.0, 0.0
    maximum = max(2.0, min(prior_gray.shape) * 0.035)
    if abs(dx) > maximum or abs(dy) > maximum or response < 0.02:
        return 0.0, 0.0, max(0.0, float(response))
    return float(dx), float(dy), _unit(response)


def _exposure_fit(prior: np.ndarray, current: np.ndarray) -> tuple[float, float]:
    prior_q = np.percentile(prior, (20.0, 50.0, 80.0))
    current_q = np.percentile(current, (20.0, 50.0, 80.0))
    prior_span = max(1.0, float(prior_q[2] - prior_q[0]))
    current_span = max(1.0, float(current_q[2] - current_q[0]))
    gain = min(1.35, max(0.70, current_span / prior_span))
    offset = float(current_q[1] - gain * prior_q[1])
    return float(gain), offset


def _owned_state(
    gray: np.ndarray,
    effective: np.ndarray,
    foam: np.ndarray,
    front_y: float | None,
) -> _RasterState:
    owned_gray = np.array(gray, dtype=np.float32, copy=True)
    owned_effective = np.array(effective, dtype=bool, copy=True)
    owned_foam = np.array(foam, dtype=bool, copy=True)
    for value in (owned_gray, owned_effective, owned_foam):
        value.setflags(write=False)
    return _RasterState(
        owned_gray,
        owned_effective,
        owned_foam,
        None if front_y is None else float(front_y),
    )


def _validate_rasters(
    gray: np.ndarray,
    effective_mask: np.ndarray,
    foam_mask: np.ndarray,
) -> None:
    if gray.ndim != 2:
        raise ValueError("Registered Foam motion requires two-dimensional grayscale input.")
    if effective_mask.shape != gray.shape or foam_mask.shape != gray.shape:
        raise ValueError("Registered Foam motion rasters must share one shape.")


def _unit(value: float) -> float:
    if not math.isfinite(float(value)):
        return 0.0
    return min(1.0, max(0.0, float(value)))
