from __future__ import annotations

from dataclasses import dataclass

from oil_tracker.domain.detection import BoundaryCandidate


@dataclass(frozen=True)
class EvidenceAvailability:
    boundary: bool
    phase: bool
    optics: bool
    artifact: bool
    motion: bool
    material_texture: bool

    def as_features(self) -> dict[str, float]:
        return {
            "boundary_evidence_available": float(self.boundary),
            "phase_evidence_available": float(self.phase),
            "optics_evidence_available": float(self.optics),
            "artifact_evidence_available": float(self.artifact),
            "motion_evidence_available": float(self.motion),
            "material_texture_evidence_available": float(
                self.material_texture
            ),
        }


@dataclass(frozen=True)
class OilCandidateEvidence:
    """Semantic view over compatibility candidate dictionaries.

    Versioned feature names remain an adapter concern.  Policies consume this
    immutable view so storage location and historical names cannot silently
    change authority behavior.
    """

    boundary: float
    artifact_likelihood: float
    artifact_signature: float
    ambiguity: float
    optics_opposition: float
    material_support: float
    narrow_strength: float
    horizontal_coverage: float
    sector_fraction: float
    terminal_support: float
    static_contradiction: float
    registered_motion: float
    registered_motion_coverage: float
    material_texture_conflict: float
    raw_material_row_support: float
    material_layer_topology: float
    material_path: bool
    supplemental: bool
    calibrated_high_recall: bool
    availability: EvidenceAvailability

    @classmethod
    def from_candidate(cls, candidate: BoundaryCandidate) -> OilCandidateEvidence:
        features = candidate.features
        penalties = candidate.penalties
        phase_keys = {
            "broad_strength",
            "region_contrast",
            "narrow_peak_strength",
            "edge_strength",
            "polarity_confidence",
        }
        optics_keys = {
            "optics_conflict",
            "glare_conflict",
            "glare_penalty",
        }
        artifact_keys = {
            "artifact_likelihood",
            "static_prior_contribution",
            "static_artifact_penalty",
            "border_penalty",
            "exclusion_conflict",
            "exclusion_penalty",
        }
        availability = EvidenceAvailability(
            boundary=(
                "boundary_likelihood" in features
                or candidate.feature_score is not None
            ),
            phase=any(key in features for key in phase_keys),
            optics=any(key in features or key in penalties for key in optics_keys),
            artifact=any(
                key in features or key in penalties for key in artifact_keys
            ),
            motion=(
                "registered_oil_band_motion_support" in features
                and "registered_oil_band_motion_coverage" in features
            ),
            material_texture=(
                "material_texture_conflict" in features
                or "material_texture_conflict" in penalties
            ),
        )
        boundary = unit(features.get("boundary_likelihood", candidate.feature_score))
        artifact_likelihood = unit(
            features.get(
                "artifact_likelihood",
                penalties.get("artifact_likelihood", 0.0),
            )
        )
        optics = unit(
            max(
                penalties.get("optics_conflict", 0.0),
                penalties.get(
                    "glare_conflict",
                    penalties.get("glare_penalty", 0.0),
                ),
            )
        )
        terminal = unit(features.get("material_terminal_partition_support", 0.0))
        material_path = unit(
            features.get("material_path", features.get("r6_material_path", 0.0))
        ) >= 0.5
        static = unit(
            features.get(
                "static_prior_contribution",
                penalties.get("static_artifact_penalty", 0.0),
            )
        )
        material = unit(
            0.34 * boundary
            + 0.18
            * unit(features.get("broad_strength", features.get("region_contrast", 0.0)))
            + 0.14
            * unit(features.get("narrow_peak_strength", features.get("edge_strength", 0.0)))
            + 0.13
            * unit(
                features.get(
                    "narrow_horizontal_coverage",
                    features.get("horizontal_coverage", 0.0),
                )
            )
            + 0.07 * unit(features.get("broad_scale_consistency", 0.0))
            + 0.05 * unit(features.get("polarity_confidence", 0.0))
        )
        artifact_signature = unit(
            0.40 * artifact_likelihood
            + 0.18 * static
            + 0.20 * optics
            + 0.12 * unit(penalties.get("border_penalty", 0.0))
            + 0.10
            * unit(
                penalties.get(
                    "exclusion_conflict",
                    penalties.get("exclusion_penalty", 0.0),
                )
            )
        )
        return cls(
            boundary=boundary,
            artifact_likelihood=artifact_likelihood,
            artifact_signature=artifact_signature,
            ambiguity=unit(
                features.get(
                    "ambiguity_likelihood",
                    penalties.get("ambiguity_likelihood", 0.0),
                )
            ),
            optics_opposition=optics,
            material_support=material,
            narrow_strength=unit(
                features.get(
                    "narrow_peak_strength",
                    features.get("edge_strength", 0.0),
                )
            ),
            horizontal_coverage=unit(
                features.get(
                    "narrow_horizontal_coverage",
                    features.get("horizontal_coverage", 0.0),
                )
            ),
            sector_fraction=unit(features.get("material_path_sector_fraction", 0.0)),
            terminal_support=terminal,
            static_contradiction=unit(
                static * (1.0 - 0.85 * terminal if material_path else 1.0)
            ),
            registered_motion=unit(
                features.get("registered_oil_band_motion_support", 0.0)
            ),
            registered_motion_coverage=unit(
                features.get("registered_oil_band_motion_coverage", 0.0)
            ),
            material_texture_conflict=max(
                unit(features.get("material_texture_conflict", 0.0)),
                unit(penalties.get("material_texture_conflict", 0.0)),
            ),
            raw_material_row_support=unit(
                features.get("raw_material_row_support", 0.0)
            ),
            material_layer_topology=unit(
                features.get("sequence_material_layer_topology", 0.0)
            ),
            material_path=material_path,
            supplemental=unit(
                features.get(
                    "supplemental_path",
                    features.get("r8_supplemental_path", 0.0),
                )
            )
            >= 0.5,
            calibrated_high_recall=(
                unit(
                    features.get(
                        "calibrated_high_recall",
                        features.get("r9_calibrated_high_recall", 0.0),
                    )
                )
                >= 0.5
            ),
            availability=availability,
        )


def candidate_is_eligible(candidate: BoundaryCandidate) -> bool:
    if unit(candidate.features.get("calibrated_artifact_match", 0.0)) >= 0.72:
        return False
    explicit = candidate.features.get("sequence_eligible")
    if explicit is not None:
        return unit(explicit) >= 0.5
    availability = unit(candidate.features.get("evidence_availability", 1.0))
    visibility = unit(candidate.features.get("visibility", 1.0))
    conflicts = (
        OilCandidateEvidence.from_candidate(candidate).optics_opposition,
        unit(candidate.penalties.get("exclusion_conflict", 0.0)),
        unit(candidate.penalties.get("border_penalty", 0.0)),
    )
    return bool(availability >= 0.30 and visibility >= 0.30 and max(conflicts) < 0.55)


def unit(value: object) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    if number != number or number in (float("inf"), float("-inf")):
        return 0.0
    return min(1.0, max(0.0, number))
