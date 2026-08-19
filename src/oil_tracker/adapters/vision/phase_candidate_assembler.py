from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Sequence

import numpy as np

from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind
from oil_tracker.domain.recipe import DetectorSettings

from .foam_front_detector import FoamDetectionResult
from .geometry_masks import MaskBundle
from .oil_material_path import (
    generate_material_path_candidates,
    material_layer_context_features,
)
from .oil_supplemental_path import (
    generate_calibrated_high_recall_candidates,
    generate_distributed_sobel_candidates,
    generate_phase_transition_candidates,
)
from .preprocessing import PreprocessResult
from .temporal_raster_evidence import (
    RegisteredOilRasterEvidence,
    registered_oil_candidate_features,
)


@dataclass(frozen=True)
class PhaseCandidateAssembly:
    """Candidate-family output before spatial calibration and sequence policy."""

    candidates: tuple[BoundaryCandidate, ...]
    material_path_count: int
    raster_material_path_count: int
    distributed_sobel_count: int
    calibrated_high_recall_count: int
    phase_transition_count: int


def assemble_phase_candidates(
    projection_candidates: Sequence[BoundaryCandidate],
    *,
    pre: PreprocessResult,
    bundle: MaskBundle,
    static_map: np.ndarray | None,
    foam: FoamDetectionResult,
    oil_motion: RegisteredOilRasterEvidence,
    settings: DetectorSettings,
    artifact_template_count: int,
    material_layer_topology: bool,
    white_material_layer_topology: bool,
    white_material_texture_present: bool,
) -> PhaseCandidateAssembly:
    """Generate and enrich all Oil proposal families without selecting one."""

    origin_y = float(bundle.crop_origin[1])
    material_path_candidates: list[BoundaryCandidate] = []
    for candidate in generate_material_path_candidates(
        pre,
        bundle.effective_mask,
        static_map,
        crop_origin_y=origin_y,
        top_k=artifact_compensated_top_k(
            settings.candidate_top_k,
            artifact_template_count,
            base_cap=6,
            calibrated_cap=8,
        ),
        # Generic material texture corroborates a lower phase boundary. It is
        # not accepted/public Foam authority.
        material_evidence_map=foam.combined_evidence_map,
    ):
        material_context = material_layer_context_features(
            foam.combined_evidence_map,
            bundle.effective_mask,
            pre.glare_mask,
            local_y=float(candidate.y) - origin_y,
        )
        material_path_candidates.append(
            replace(
                candidate,
                features={
                    **candidate.features,
                    **material_context,
                    "material_texture_evidence_available": 1.0,
                    **registered_oil_candidate_features(
                        oil_motion,
                        local_y=float(candidate.y) - origin_y,
                    ),
                    **_layer_features(
                        material_layer_topology,
                        white_material_layer_topology,
                        white_material_texture_present,
                    ),
                },
                penalties={
                    **candidate.penalties,
                    "material_texture_conflict": float(
                        material_context["material_texture_conflict"]
                        if white_material_texture_present
                        else 0.0
                    ),
                },
            )
        )

    # This bounded raster path is independent of raw Foam-like texture. It is
    # additive and begins without direct anchor authority.
    raster_material_path_candidates: list[BoundaryCandidate] = []
    for candidate in generate_material_path_candidates(
        pre,
        bundle.effective_mask,
        static_map,
        crop_origin_y=origin_y,
        top_k=artifact_compensated_top_k(
            settings.candidate_top_k,
            artifact_template_count,
            base_cap=4,
            calibrated_cap=6,
        ),
        material_evidence_map=None,
    ):
        if any(
            abs(float(candidate.y) - float(existing.y)) <= 6.0
            for existing in material_path_candidates
        ):
            continue
        material_context = material_layer_context_features(
            foam.combined_evidence_map,
            bundle.effective_mask,
            pre.glare_mask,
            local_y=float(candidate.y) - origin_y,
        )
        raster_material_path_candidates.append(
            replace(
                candidate,
                source="raster_material_path",
                features={
                    **candidate.features,
                    **material_context,
                    "material_texture_evidence_available": 1.0,
                    **registered_oil_candidate_features(
                        oil_motion,
                        local_y=float(candidate.y) - origin_y,
                    ),
                    "supplemental_path": 1.0,
                    **_layer_features(False, False, False),
                },
                penalties={
                    **candidate.penalties,
                    "material_texture_conflict": float(
                        material_context["material_texture_conflict"]
                    ),
                },
            )
        )

    distributed_sobel_candidates = tuple(
        _enrich_generated_candidate(
            candidate,
            pre=pre,
            bundle=bundle,
            foam=foam,
            oil_motion=oil_motion,
            layer_features=_layer_features(False, False, False),
        )
        for candidate in generate_distributed_sobel_candidates(
            pre,
            bundle.effective_mask,
            static_map,
            crop_origin_y=origin_y,
        )
    )
    calibrated_high_recall_candidates = tuple(
        _enrich_generated_candidate(
            candidate,
            pre=pre,
            bundle=bundle,
            foam=foam,
            oil_motion=oil_motion,
            layer_features=_layer_features(False, False, False),
        )
        for candidate in (
            generate_calibrated_high_recall_candidates(
                pre,
                bundle.effective_mask,
                static_map,
                crop_origin_y=origin_y,
                limit=min(12, 6 + artifact_template_count),
            )
            if artifact_template_count
            else ()
        )
    )
    phase_transition_candidates = tuple(
        _enrich_generated_candidate(
            candidate,
            pre=pre,
            bundle=bundle,
            foam=foam,
            oil_motion=oil_motion,
            layer_features=_layer_features(False, False, False),
        )
        for candidate in (
            generate_phase_transition_candidates(
                pre,
                bundle.effective_mask,
                static_map,
                crop_origin_y=origin_y,
                limit=min(6, 3 + artifact_template_count),
            )
            if artifact_template_count
            else ()
        )
    )

    oil_candidates = tuple(
        _enrich_projection_candidate(
            candidate,
            pre=pre,
            bundle=bundle,
            foam=foam,
            oil_motion=oil_motion,
            white_material_texture_present=white_material_texture_present,
            layer_features=_layer_features(
                material_layer_topology,
                white_material_layer_topology,
                white_material_texture_present,
            ),
        )
        for candidate in projection_candidates
    )
    all_candidates = (
        *oil_candidates,
        *material_path_candidates,
        *raster_material_path_candidates,
        *distributed_sobel_candidates,
        *calibrated_high_recall_candidates,
        *phase_transition_candidates,
    )
    return PhaseCandidateAssembly(
        candidates=all_candidates,
        material_path_count=len(material_path_candidates),
        raster_material_path_count=len(raster_material_path_candidates),
        distributed_sobel_count=len(distributed_sobel_candidates),
        calibrated_high_recall_count=(
            len(calibrated_high_recall_candidates)
            + len(phase_transition_candidates)
        ),
        phase_transition_count=len(phase_transition_candidates),
    )


def artifact_compensated_top_k(
    configured: int,
    artifact_template_count: int,
    *,
    base_cap: int,
    calibrated_cap: int,
) -> int:
    """Keep the ordinary proposal budget after user-confirmed exclusions."""

    ordinary = max(1, min(int(base_cap), int(configured)))
    compensation = min(3, max(0, int(artifact_template_count)))
    return min(int(calibrated_cap), ordinary + compensation)


def _enrich_projection_candidate(
    candidate: BoundaryCandidate,
    *,
    pre: PreprocessResult,
    bundle: MaskBundle,
    foam: FoamDetectionResult,
    oil_motion: RegisteredOilRasterEvidence,
    white_material_texture_present: bool,
    layer_features: dict[str, float],
) -> BoundaryCandidate:
    if candidate.kind is not BoundaryKind.OIL_AIR:
        return candidate
    origin_y = float(bundle.crop_origin[1])
    material_context = material_layer_context_features(
        foam.combined_evidence_map,
        bundle.effective_mask,
        pre.glare_mask,
        local_y=float(candidate.y) - origin_y,
    )
    return replace(
        candidate,
        features={
            **candidate.features,
            **material_context,
            "material_texture_evidence_available": 1.0,
            **registered_oil_candidate_features(
                oil_motion,
                local_y=float(candidate.y) - origin_y,
            ),
            **layer_features,
        },
        penalties={
            **candidate.penalties,
            "material_texture_conflict": float(
                material_context["material_texture_conflict"]
                if white_material_texture_present
                else 0.0
            ),
        },
    )


def _enrich_generated_candidate(
    candidate: BoundaryCandidate,
    *,
    pre: PreprocessResult,
    bundle: MaskBundle,
    foam: FoamDetectionResult,
    oil_motion: RegisteredOilRasterEvidence,
    layer_features: dict[str, float],
) -> BoundaryCandidate:
    origin_y = float(bundle.crop_origin[1])
    material_context = material_layer_context_features(
        foam.combined_evidence_map,
        bundle.effective_mask,
        pre.glare_mask,
        local_y=float(candidate.y) - origin_y,
    )
    return replace(
        candidate,
        features={
            **candidate.features,
            **material_context,
            "material_texture_evidence_available": 1.0,
            **registered_oil_candidate_features(
                oil_motion,
                local_y=float(candidate.y) - origin_y,
            ),
            **layer_features,
        },
        penalties={
            **candidate.penalties,
            "material_texture_conflict": float(
                material_context["material_texture_conflict"]
            ),
        },
    )


def _layer_features(
    material_layer_topology: bool,
    white_material_layer_topology: bool,
    white_material_texture_present: bool,
) -> dict[str, float]:
    return {
        "sequence_material_layer_topology": float(material_layer_topology),
        "sequence_white_material_layer_topology": float(
            white_material_layer_topology
        ),
        "sequence_white_material_texture_present": float(
            white_material_texture_present
        ),
    }
