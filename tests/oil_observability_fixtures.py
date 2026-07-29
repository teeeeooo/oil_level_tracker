from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import cv2
import numpy as np

from foam_benchmark_fixtures import controlled_scenes as controlled_foam_scenes
from oil_benchmark_fixtures import controlled_oil_scenes
from oil_tracker.domain.geometry import EllipseGeometry


class LatentSceneCause(str, Enum):
    PARTIAL_GLARE = "partial_glare"
    LEGITIMATE_OIL_BOUNDARY = "legitimate_oil_boundary"


class DetectorObservability(str, Enum):
    IDENTIFIABLE = "identifiable"
    UNIDENTIFIABLE = "unidentifiable"


class ExpectedCanonicalFamily(str, Enum):
    ACCEPTED_BOUNDARY = "accepted_boundary"
    AMBIGUOUS = "ambiguous"


@dataclass(frozen=True)
class OilObservabilityScene:
    case_id: str
    collision_id: str
    frame: np.ndarray
    ellipse: EllipseGeometry
    latent_cause: LatentSceneCause
    numeric_oil_geometry_present: bool
    latent_oil_y: float | None
    detector_observability: DetectorObservability
    expected_canonical_family: ExpectedCanonicalFamily

    def __post_init__(self) -> None:
        if self.numeric_oil_geometry_present != (self.latent_oil_y is not None):
            raise ValueError("Latent oil geometry and numeric truth must agree.")
        if self.detector_observability is DetectorObservability.UNIDENTIFIABLE:
            if self.expected_canonical_family is not ExpectedCanonicalFamily.AMBIGUOUS:
                raise ValueError("Unidentifiable input must expect canonical ambiguity.")
        if self.frame.shape != (240, 320, 3) or self.frame.dtype != np.uint8:
            raise ValueError("Controlled observability frames have one canonical raster shape.")


@dataclass(frozen=True)
class HistoricalGlareNegative:
    case_id: str
    frame: np.ndarray


def single_frame_observability_collisions() -> tuple[OilObservabilityScene, ...]:
    rows: list[OilObservabilityScene] = []
    for width in (72, 74):
        collision_id = f"centered-partial-glare-{width}"
        ellipse = EllipseGeometry(160.0, 120.0, 36.0, 64.8)
        _add_collision_pair(
            rows,
            collision_id,
            _partial_component(width=width),
            _oil_phase(texture="uniform", bright_side="below"),
            ellipse,
        )
    for center_x, label in ((152, "left"), (168, "right")):
        _add_collision_pair(
            rows,
            f"roi-location-{label}-component-edge-hidden",
            _partial_component(width=74, center_x=center_x),
            _oil_phase(texture="uniform", bright_side="below"),
            EllipseGeometry(float(center_x), 120.0, 34.0, 64.8),
        )

    for texture, bright_side in (
        ("alternating", "below"),
        ("block", "below"),
        ("sinusoid", "below"),
        ("sinusoid", "above"),
    ):
        collision_id = f"{texture}-{bright_side}-latent-cause-collision"
        frame = _oil_phase(texture=texture, bright_side=bright_side)
        _add_collision_pair(
            rows,
            collision_id,
            frame,
            frame.copy(),
            EllipseGeometry(160.0, 120.0, 36.0, 64.8),
        )
    return tuple(rows)


def historical_glare_negatives() -> tuple[HistoricalGlareNegative, ...]:
    oil_scenes = {scene.case_id: scene for scene in controlled_oil_scenes()}
    foam_scenes = {scene.case_id: scene for scene in controlled_foam_scenes()}
    glare = oil_scenes["glare-recovery-1"].frame
    foam_glare = foam_scenes["clipped-glare"].frame
    rows = [
        HistoricalGlareNegative(
            f"glare-only-contrast-{factor:.2f}",
            _adjust_contrast(glare, factor),
        )
        for factor in (0.90, 0.92)
    ]
    rows.extend(
        HistoricalGlareNegative(f"foam-clipped-glare-geometry-{delta:+d}", frame)
        for delta, frame in (
            (delta, _shift_vertical(foam_glare, delta))
            for delta in (-2, -1, 0, 1, 2)
        )
    )
    rows.extend(
        HistoricalGlareNegative(f"foam-clipped-glare-brightness-{delta:+d}", frame)
        for delta, frame in (
            (delta, _adjust_brightness(foam_glare, delta))
            for delta in (-8, -4, 0, 4, 8)
        )
    )
    rows.extend(
        HistoricalGlareNegative(f"foam-clipped-glare-contrast-{factor:.2f}", frame)
        for factor, frame in (
            (factor, _adjust_contrast(foam_glare, factor))
            for factor in (0.90, 0.92, 1.08, 1.10)
        )
    )
    rows.extend(
        HistoricalGlareNegative(f"foam-clipped-glare-noise-{seed}", frame)
        for seed, frame in (
            (seed, _add_noise(foam_glare, seed))
            for seed in (7, 19, 43, 101, 211)
        )
    )
    if len(rows) != 21:
        raise AssertionError("The retained historical glare-negative contract has 21 cases.")
    return tuple(rows)


def _add_collision_pair(
    rows: list[OilObservabilityScene],
    collision_id: str,
    glare_frame: np.ndarray,
    oil_frame: np.ndarray,
    ellipse: EllipseGeometry,
) -> None:
    rows.extend(
        (
            OilObservabilityScene(
                case_id=f"{collision_id}-latent-glare",
                collision_id=collision_id,
                frame=_readonly(glare_frame),
                ellipse=ellipse,
                latent_cause=LatentSceneCause.PARTIAL_GLARE,
                numeric_oil_geometry_present=False,
                latent_oil_y=None,
                detector_observability=DetectorObservability.UNIDENTIFIABLE,
                expected_canonical_family=ExpectedCanonicalFamily.AMBIGUOUS,
            ),
            OilObservabilityScene(
                case_id=f"{collision_id}-latent-oil",
                collision_id=collision_id,
                frame=_readonly(oil_frame),
                ellipse=ellipse,
                latent_cause=LatentSceneCause.LEGITIMATE_OIL_BOUNDARY,
                numeric_oil_geometry_present=True,
                latent_oil_y=80.0,
                detector_observability=DetectorObservability.UNIDENTIFIABLE,
                expected_canonical_family=ExpectedCanonicalFamily.AMBIGUOUS,
            ),
        )
    )


def _partial_component(
    *,
    width: int,
    center_x: int = 160,
    y: int = 80,
) -> np.ndarray:
    frame = np.full((240, 320, 3), 90, dtype=np.uint8)
    left = center_x - width // 2
    frame[y:185, left : left + width] = 244
    return frame


def _oil_phase(
    *,
    texture: str,
    bright_side: str,
    y: int = 80,
    low: int = 240,
    high: int = 244,
    period: int = 4,
) -> np.ndarray:
    frame = np.full((240, 320, 3), 90, dtype=np.uint8)
    x = np.arange(320, dtype=np.float64)
    if texture == "uniform":
        values = np.full(320, high, dtype=np.uint8)
    elif texture == "alternating":
        values = np.where((x.astype(int) % 2) == 0, low, high).astype(np.uint8)
    elif texture == "block":
        values = np.where(((x.astype(int) // period) % 2) == 0, low, high).astype(np.uint8)
    elif texture == "sinusoid":
        midpoint = (low + high) / 2.0
        amplitude = (high - low) / 2.0
        values = np.clip(
            midpoint + amplitude * np.sin(2.0 * np.pi * x / period),
            0,
            255,
        ).astype(np.uint8)
    else:
        raise ValueError(f"Unsupported controlled texture: {texture}")
    if bright_side == "below":
        frame[y:] = values[None, :, None]
    elif bright_side == "above":
        frame[:y] = values[None, :, None]
    else:
        raise ValueError(f"Unsupported controlled bright side: {bright_side}")
    return frame


def _shift_vertical(frame: np.ndarray, delta: int) -> np.ndarray:
    height, width = frame.shape[:2]
    transform = np.array(
        ((1.0, 0.0, 0.0), (0.0, 1.0, float(delta))),
        dtype=np.float32,
    )
    return cv2.warpAffine(
        frame,
        transform,
        (width, height),
        flags=cv2.INTER_NEAREST,
        borderMode=cv2.BORDER_REPLICATE,
    )


def _adjust_brightness(frame: np.ndarray, delta: int) -> np.ndarray:
    adjusted = frame.astype(np.int16) + int(delta)
    return np.clip(adjusted, 0, 255).astype(frame.dtype)


def _adjust_contrast(frame: np.ndarray, factor: float) -> np.ndarray:
    center = 127.5
    adjusted = (frame.astype(np.float32) - center) * factor + center
    return np.clip(adjusted, 0, 255).astype(frame.dtype)


def _add_noise(frame: np.ndarray, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    noisy = frame.astype(np.float32) + rng.normal(0.0, 1.5, frame.shape)
    return np.clip(noisy, 0, 255).astype(frame.dtype)


def _readonly(frame: np.ndarray) -> np.ndarray:
    owned = np.ascontiguousarray(frame.copy())
    owned.setflags(write=False)
    return owned
