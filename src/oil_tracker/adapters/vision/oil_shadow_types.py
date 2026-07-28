from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import math
from typing import TypeAlias


class ShadowSourceFamily(str, Enum):
    SOBEL = "sobel"
    CANNY = "canny"
    HOUGH = "hough"
    REGION_STEP = "region_step"


class ShadowHypothesisLabel(str, Enum):
    BOUNDARY_LIKE = "boundary_like"
    ARTIFACT_LIKE = "artifact_like"
    AMBIGUOUS = "ambiguous"


class ShadowObservationKind(str, Enum):
    BOUNDARY = "boundary"
    NO_INTERFACE = "no_interface"
    AMBIGUOUS = "ambiguous"
    UNAVAILABLE = "unavailable"


class ShadowTemporalStatus(str, Enum):
    BOUNDARY_ACCEPTED = "boundary_accepted"
    NO_INTERFACE_ACCEPTED = "no_interface_accepted"
    AMBIGUOUS = "ambiguous"
    UNAVAILABLE = "unavailable"
    REACQUISITION_PENDING = "reacquisition_pending"


@dataclass(frozen=True)
class OilShadowBounds:
    observations_per_source_scale: int = 6
    total_raw_observations: int = 48
    broad_band_scales: tuple[int, ...] = (3, 6, 10)
    narrow_scales: tuple[int, ...] = (1, 2, 3)
    narrow_lobe_search_radius_px: int = 12
    maximum_proposal_diameter_px: float = 6.0
    members_per_proposal: int = 8
    total_proposals: int = 12
    total_retained_members: int = 48
    semantic_hypotheses: int = 10
    temporal_beam_width: int = 4
    temporal_history_window: int = 6
    reacquisition_frames: int = 2
    no_interface_clear_frames: int = 2
    unavailable_clear_frames: int = 6
    maximum_static_prior: float = 0.28
    static_prior_scalars_per_glass: int = 2
    maximum_debug_scalar_count: int = 96

    def __post_init__(self) -> None:
        integer_fields = (
            self.observations_per_source_scale,
            self.total_raw_observations,
            self.narrow_lobe_search_radius_px,
            self.members_per_proposal,
            self.total_proposals,
            self.total_retained_members,
            self.semantic_hypotheses,
            self.temporal_beam_width,
            self.temporal_history_window,
            self.reacquisition_frames,
            self.no_interface_clear_frames,
            self.unavailable_clear_frames,
            self.static_prior_scalars_per_glass,
            self.maximum_debug_scalar_count,
        )
        if any(value < 1 for value in integer_fields):
            raise ValueError("Oil shadow integer bounds must be positive.")
        if not self.broad_band_scales or not self.narrow_scales:
            raise ValueError("Oil shadow scale sets must not be empty.")
        if any(value < 1 for value in self.broad_band_scales + self.narrow_scales):
            raise ValueError("Oil shadow scales must be positive.")
        _positive_finite(self.maximum_proposal_diameter_px, "maximum proposal diameter")
        _unit(self.maximum_static_prior, "maximum static prior")
        if self.total_retained_members > self.total_raw_observations:
            raise ValueError("Retained proposal members cannot exceed total raw observations.")


@dataclass(frozen=True)
class RawEdgeObservation:
    identity: str
    source_family: ShadowSourceFamily
    measurement_scale: int
    local_y: float
    source_y: float
    polarity_available: bool
    polarity: float
    response_strength: float
    horizontal_support: float
    valid_mask_support: float
    glare_visible_support: float
    measurement_width_px: float
    band_height_px: float
    source_local_index: int
    source_angle_deg: float | None = None

    def __post_init__(self) -> None:
        _identity(self.identity)
        if self.measurement_scale < 1 or self.source_local_index < 0:
            raise ValueError("Observation scale and source-local index are invalid.")
        _finite(self.local_y, "observation local Y")
        _finite(self.source_y, "observation source Y")
        _signed_unit(self.polarity, "observation polarity")
        for value, name in (
            (self.response_strength, "response strength"),
            (self.horizontal_support, "horizontal support"),
            (self.valid_mask_support, "valid-mask support"),
            (self.glare_visible_support, "glare-visible support"),
        ):
            _unit(value, name)
        _positive_finite(self.measurement_width_px, "measurement width")
        _positive_finite(self.band_height_px, "band height")
        if self.source_angle_deg is not None:
            _nonnegative_finite(self.source_angle_deg, "observation source angle")
            if self.source_angle_deg > 90.0:
                raise ValueError("Observation source angle exceeds its physical range.")
        if not self.polarity_available and abs(self.polarity) > 1e-12:
            raise ValueError("Unavailable polarity must use the neutral scalar value 0.0.")

    @property
    def canonical_key(self) -> tuple[float, str, int, float, str]:
        return (
            self.local_y,
            self.source_family.value,
            self.measurement_scale,
            -self.response_strength,
            self.identity,
        )


@dataclass(frozen=True)
class BoundedYProposal:
    identity: str
    member_ids: tuple[str, ...]
    minimum_local_y: float
    maximum_local_y: float
    representative_local_y: float
    representative_source_y: float
    source_family_count: int

    def __post_init__(self) -> None:
        _identity(self.identity)
        _identity_tuple(self.member_ids, "proposal members")
        for value, name in (
            (self.minimum_local_y, "proposal minimum Y"),
            (self.maximum_local_y, "proposal maximum Y"),
            (self.representative_local_y, "proposal representative Y"),
            (self.representative_source_y, "proposal source Y"),
        ):
            _finite(value, name)
        if self.maximum_local_y < self.minimum_local_y:
            raise ValueError("Proposal Y bounds are inverted.")
        if not self.minimum_local_y - 1e-12 <= self.representative_local_y <= self.maximum_local_y + 1e-12:
            raise ValueError("Proposal representative Y must stay inside the member diameter.")
        if self.source_family_count < 1:
            raise ValueError("Proposal source-family count must be positive.")

    @property
    def diameter_px(self) -> float:
        return self.maximum_local_y - self.minimum_local_y

    @property
    def member_count(self) -> int:
        return len(self.member_ids)


@dataclass(frozen=True)
class BroadScaleEvidence:
    band_scale: int
    available: bool
    signed_contrast: float
    strength: float
    visible_support: float
    glare_conflict: float
    exclusion_conflict: float
    transition_local_y: float

    def __post_init__(self) -> None:
        if self.band_scale < 1:
            raise ValueError("Broad scale must be positive.")
        _signed_unit(self.signed_contrast, "broad signed contrast")
        for value, name in (
            (self.strength, "broad strength"),
            (self.visible_support, "broad visible support"),
            (self.glare_conflict, "broad glare conflict"),
            (self.exclusion_conflict, "broad exclusion conflict"),
        ):
            _unit(value, name)
        _finite(self.transition_local_y, "broad transition Y")
        if not self.available and (abs(self.signed_contrast) > 1e-12 or self.strength > 1e-12):
            raise ValueError("Unavailable broad evidence cannot masquerade as scored evidence.")


@dataclass(frozen=True)
class BroadEvidenceSummary:
    scales: tuple[BroadScaleEvidence, ...]
    available_scale_count: int
    signed_contrast: float
    strength: float
    scale_consistency: float
    polarity_consistency: float
    transition_local_y: float
    visibility: float
    glare_conflict: float
    exclusion_conflict: float

    def __post_init__(self) -> None:
        if not isinstance(self.scales, tuple):
            raise TypeError("Broad scales must be stored as an immutable tuple.")
        if not 0 <= self.available_scale_count <= len(self.scales):
            raise ValueError("Broad available-scale count is invalid.")
        _signed_unit(self.signed_contrast, "broad summary signed contrast")
        for value, name in (
            (self.strength, "broad summary strength"),
            (self.scale_consistency, "broad scale consistency"),
            (self.polarity_consistency, "broad polarity consistency"),
            (self.visibility, "broad visibility"),
            (self.glare_conflict, "broad summary glare conflict"),
            (self.exclusion_conflict, "broad summary exclusion conflict"),
        ):
            _unit(value, name)
        _finite(self.transition_local_y, "broad summary transition Y")


@dataclass(frozen=True)
class NarrowScaleEvidence:
    scale: int
    available: bool
    peak_strength: float
    horizontal_coverage: float

    def __post_init__(self) -> None:
        if self.scale < 1:
            raise ValueError("Narrow scale must be positive.")
        _unit(self.peak_strength, "narrow peak strength")
        _unit(self.horizontal_coverage, "narrow horizontal coverage")
        if not self.available and (self.peak_strength > 1e-12 or self.horizontal_coverage > 1e-12):
            raise ValueError("Unavailable narrow evidence cannot masquerade as scored evidence.")


@dataclass(frozen=True)
class NarrowEvidenceSummary:
    scales: tuple[NarrowScaleEvidence, ...]
    available: bool
    peak_strength: float
    horizontal_coverage: float
    signed_lobe_order: float
    paired_edge_separation_px: float
    paired_edge_strength: float
    pulse_symmetry: float
    center_offset_px: float
    scale_persistence: float
    border_overlap: float
    exclusion_overlap: float
    glare_overlap: float
    static_overlap: float

    def __post_init__(self) -> None:
        if not isinstance(self.scales, tuple):
            raise TypeError("Narrow scales must be stored as an immutable tuple.")
        for value, name in (
            (self.peak_strength, "narrow peak strength"),
            (self.horizontal_coverage, "narrow coverage"),
            (self.paired_edge_strength, "paired-edge strength"),
            (self.pulse_symmetry, "pulse symmetry"),
            (self.scale_persistence, "narrow scale persistence"),
            (self.border_overlap, "border overlap"),
            (self.exclusion_overlap, "exclusion overlap"),
            (self.glare_overlap, "glare overlap"),
            (self.static_overlap, "static overlap"),
        ):
            _unit(value, name)
        _signed_unit(self.signed_lobe_order, "signed lobe order")
        _nonnegative_finite(self.paired_edge_separation_px, "paired-edge separation")
        _finite(self.center_offset_px, "narrow center offset")


@dataclass(frozen=True)
class StaticPriorEvidence:
    available: bool
    coverage: float
    overlap: float
    contribution: float

    def __post_init__(self) -> None:
        for value, name in (
            (self.coverage, "static coverage"),
            (self.overlap, "static overlap"),
            (self.contribution, "static-prior contribution"),
        ):
            _unit(value, name)
        if not self.available and (self.overlap > 1e-12 or self.contribution > 1e-12):
            raise ValueError("Unavailable static evidence must be neutral.")


@dataclass(frozen=True)
class SemanticHypothesis:
    identity: str
    proposal_ids: tuple[str, ...]
    observation_ids: tuple[str, ...]
    representative_local_y: float
    representative_source_y: float
    minimum_local_y: float
    maximum_local_y: float
    broad: BroadEvidenceSummary
    narrow: NarrowEvidenceSummary
    static_prior: StaticPriorEvidence
    boundary_likelihood: float
    artifact_likelihood: float
    ambiguity_likelihood: float
    evidence_availability: float
    visibility: float
    polarity_available: bool
    polarity: float
    polarity_confidence: float
    label: ShadowHypothesisLabel
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        _identity(self.identity)
        _identity_tuple(self.proposal_ids, "hypothesis proposals")
        _identity_tuple(self.observation_ids, "hypothesis observations")
        _identity_tuple(self.provenance, "hypothesis provenance")
        for value, name in (
            (self.representative_local_y, "hypothesis local Y"),
            (self.representative_source_y, "hypothesis source Y"),
            (self.minimum_local_y, "hypothesis minimum Y"),
            (self.maximum_local_y, "hypothesis maximum Y"),
        ):
            _finite(value, name)
        if self.maximum_local_y < self.minimum_local_y:
            raise ValueError("Hypothesis Y bounds are inverted.")
        if not self.minimum_local_y - 1e-12 <= self.representative_local_y <= self.maximum_local_y + 1e-12:
            raise ValueError("Hypothesis representative Y must stay within its evidence diameter.")
        for value, name in (
            (self.boundary_likelihood, "boundary likelihood"),
            (self.artifact_likelihood, "artifact likelihood"),
            (self.ambiguity_likelihood, "ambiguity likelihood"),
            (self.evidence_availability, "evidence availability"),
            (self.visibility, "hypothesis visibility"),
            (self.polarity_confidence, "polarity confidence"),
        ):
            _unit(value, name)
        _signed_unit(self.polarity, "hypothesis polarity")
        if not self.polarity_available and abs(self.polarity) > 1e-12:
            raise ValueError("Unavailable hypothesis polarity must be neutral.")

    @property
    def diameter_px(self) -> float:
        return self.maximum_local_y - self.minimum_local_y


@dataclass(frozen=True)
class ShadowNoInterfaceEvidence:
    available: bool
    likelihood: float
    full_likelihood: float
    empty_likelihood: float
    region_uniformity: float
    weak_boundary_evidence: float
    competing_boundary_likelihood: float
    visibility: float
    glare_conflict: float
    mean_intensity: float | None
    texture: float | None
    reason: str

    def __post_init__(self) -> None:
        for value, name in (
            (self.likelihood, "no-interface likelihood"),
            (self.full_likelihood, "full likelihood"),
            (self.empty_likelihood, "empty likelihood"),
            (self.region_uniformity, "region uniformity"),
            (self.weak_boundary_evidence, "weak-boundary evidence"),
            (self.competing_boundary_likelihood, "competing boundary likelihood"),
            (self.visibility, "no-interface visibility"),
            (self.glare_conflict, "no-interface glare conflict"),
        ):
            _unit(value, name)
        if self.mean_intensity is not None:
            _finite(self.mean_intensity, "no-interface mean intensity")
        if self.texture is not None:
            _nonnegative_finite(self.texture, "no-interface texture")
        if not self.reason:
            raise ValueError("No-interface evidence requires a reason.")


class CompatibilityTrackerAction(str, Enum):
    ACCEPT_BOUNDARY = "ACCEPT_BOUNDARY"
    NO_UPDATE = "NO_UPDATE"


class SmoothingAction(str, Enum):
    PRESERVE = "PRESERVE"
    CLEAR_BEFORE_ACCEPT = "CLEAR_BEFORE_ACCEPT"
    CLEAR_STALE_AFTER_STABLE_ABSENCE = "CLEAR_STALE_AFTER_STABLE_ABSENCE"


class BoundaryAcceptanceMode(str, Enum):
    INITIAL = "initial"
    CONTINUOUS = "continuous"
    REACQUIRED = "reacquired"


class AbsenceStabilityMode(str, Enum):
    PENDING = "pending"
    STABLE = "stable"


class PipelineFailureStage(str, Enum):
    EVIDENCE_CONSTRUCTION = "evidence_construction"
    PHASE_A = "phase_a"
    TEMPORAL_EVALUATION = "temporal_evaluation"
    PHASE_B = "phase_b"
    OUTCOME_PREPARATION = "outcome_preparation"
    COMMIT = "commit"
    EXTERNAL_RUNNER = "external_runner"


JsonScalar: TypeAlias = str | int | float | bool | None
DiagnosticItems: TypeAlias = tuple[tuple[str, JsonScalar], ...]


@dataclass(frozen=True)
class ShadowBoundaryObservation:
    hypothesis: SemanticHypothesis
    alternatives: tuple[str, ...] = ()
    diagnostics: DiagnosticItems = ()

    def __post_init__(self) -> None:
        if not isinstance(self.alternatives, tuple):
            raise TypeError("Boundary alternatives must be an immutable tuple.")
        if self.alternatives and tuple(sorted(set(self.alternatives))) != self.alternatives:
            raise ValueError("Boundary alternatives must be unique and canonically sorted.")
        _diagnostics(self.diagnostics)

    @property
    def kind(self) -> ShadowObservationKind:
        return ShadowObservationKind.BOUNDARY

    @property
    def visibility(self) -> float:
        return self.hypothesis.visibility


@dataclass(frozen=True)
class ShadowNoInterfaceObservation:
    evidence: ShadowNoInterfaceEvidence
    diagnostics: DiagnosticItems = ()

    def __post_init__(self) -> None:
        if not self.evidence.available:
            raise ValueError("Positive no-interface observation requires available evidence.")
        _diagnostics(self.diagnostics)

    @property
    def kind(self) -> ShadowObservationKind:
        return ShadowObservationKind.NO_INTERFACE

    @property
    def visibility(self) -> float:
        return self.evidence.visibility


@dataclass(frozen=True)
class ShadowAmbiguousObservation:
    hypothesis_ids: tuple[str, ...]
    boundary_likelihood: float
    artifact_likelihood: float
    ambiguity_likelihood: float
    no_interface_likelihood: float
    visibility: float
    projected_source_y: float | None
    reason: str
    diagnostics: DiagnosticItems = ()

    def __post_init__(self) -> None:
        if not isinstance(self.hypothesis_ids, tuple):
            raise TypeError("Ambiguous hypothesis identities must be an immutable tuple.")
        if self.hypothesis_ids and tuple(sorted(set(self.hypothesis_ids))) != self.hypothesis_ids:
            raise ValueError("Ambiguous hypothesis identities must be unique and canonical.")
        for value, name in (
            (self.boundary_likelihood, "ambiguous boundary likelihood"),
            (self.artifact_likelihood, "ambiguous artifact likelihood"),
            (self.ambiguity_likelihood, "ambiguous likelihood"),
            (self.no_interface_likelihood, "ambiguous no-interface likelihood"),
            (self.visibility, "ambiguous visibility"),
        ):
            _unit(value, name)
        if self.projected_source_y is not None:
            _finite(self.projected_source_y, "ambiguous diagnostic source Y")
        if not self.reason:
            raise ValueError("Ambiguous observation requires a reason.")
        _diagnostics(self.diagnostics)

    @property
    def kind(self) -> ShadowObservationKind:
        return ShadowObservationKind.AMBIGUOUS


@dataclass(frozen=True)
class ShadowUnavailableObservation:
    visibility: float
    reason: str
    diagnostics: DiagnosticItems = ()

    def __post_init__(self) -> None:
        _unit(self.visibility, "unavailable visibility")
        if not self.reason:
            raise ValueError("Successful evidence-unavailable observation requires a reason.")
        _diagnostics(self.diagnostics)

    @property
    def kind(self) -> ShadowObservationKind:
        return ShadowObservationKind.UNAVAILABLE


ShadowCurrentObservation: TypeAlias = (
    ShadowBoundaryObservation
    | ShadowNoInterfaceObservation
    | ShadowAmbiguousObservation
    | ShadowUnavailableObservation
)


@dataclass(frozen=True)
class TemporalResourceMetrics:
    beam_count: int
    history_length: int
    retained_scalar_count: int
    reacquisition_count: int

    def __post_init__(self) -> None:
        if any(value < 0 for value in (
            self.beam_count,
            self.history_length,
            self.retained_scalar_count,
            self.reacquisition_count,
        )):
            raise ValueError("Temporal resource counters cannot be negative.")


@dataclass(frozen=True)
class BoundaryAcceptedDecision:
    selected_hypothesis: SemanticHypothesis
    accepted_source_y: float
    confidence: float
    decision_margin: float
    acceptance_mode: BoundaryAcceptanceMode
    reason: str
    resources: TemporalResourceMetrics

    def __post_init__(self) -> None:
        _finite(self.accepted_source_y, "accepted boundary source Y")
        _unit(self.confidence, "temporal confidence")
        _unit(self.decision_margin, "temporal decision margin")
        if not isinstance(self.acceptance_mode, BoundaryAcceptanceMode):
            raise TypeError("Boundary decision requires a closed acceptance mode.")
        if not self.reason:
            raise ValueError("Boundary decision requires a reason.")

    @property
    def status(self) -> ShadowTemporalStatus:
        return ShadowTemporalStatus.BOUNDARY_ACCEPTED

    @property
    def observation_kind(self) -> ShadowObservationKind:
        return ShadowObservationKind.BOUNDARY

    @property
    def tracker_action(self) -> CompatibilityTrackerAction:
        return CompatibilityTrackerAction.ACCEPT_BOUNDARY

    @property
    def smoothing_action(self) -> SmoothingAction:
        return (
            SmoothingAction.CLEAR_BEFORE_ACCEPT
            if self.acceptance_mode is BoundaryAcceptanceMode.REACQUIRED
            else SmoothingAction.PRESERVE
        )


@dataclass(frozen=True)
class NoInterfaceAcceptedDecision:
    evidence: ShadowNoInterfaceEvidence
    confidence: float
    decision_margin: float
    stability_mode: AbsenceStabilityMode
    reason: str
    resources: TemporalResourceMetrics

    def __post_init__(self) -> None:
        if not self.evidence.available:
            raise ValueError("No-interface decision requires positive available evidence.")
        _unit(self.confidence, "temporal confidence")
        _unit(self.decision_margin, "temporal decision margin")
        if not isinstance(self.stability_mode, AbsenceStabilityMode):
            raise TypeError("No-interface decision requires a closed stability mode.")
        if not self.reason:
            raise ValueError("No-interface decision requires a reason.")

    @property
    def status(self) -> ShadowTemporalStatus:
        return ShadowTemporalStatus.NO_INTERFACE_ACCEPTED

    @property
    def observation_kind(self) -> ShadowObservationKind:
        return ShadowObservationKind.NO_INTERFACE

    @property
    def tracker_action(self) -> CompatibilityTrackerAction:
        return CompatibilityTrackerAction.NO_UPDATE

    @property
    def smoothing_action(self) -> SmoothingAction:
        return (
            SmoothingAction.CLEAR_STALE_AFTER_STABLE_ABSENCE
            if self.stability_mode is AbsenceStabilityMode.STABLE
            else SmoothingAction.PRESERVE
        )


@dataclass(frozen=True)
class AmbiguousDecision:
    hypothesis_ids: tuple[str, ...]
    projected_source_y: float | None
    confidence: float
    decision_margin: float
    reason: str
    resources: TemporalResourceMetrics

    def __post_init__(self) -> None:
        if self.projected_source_y is not None:
            _finite(self.projected_source_y, "ambiguous diagnostic source Y")
        _unit(self.confidence, "temporal confidence")
        _unit(self.decision_margin, "temporal decision margin")
        if not self.reason:
            raise ValueError("Ambiguous decision requires a reason.")

    @property
    def status(self) -> ShadowTemporalStatus:
        return ShadowTemporalStatus.AMBIGUOUS

    @property
    def observation_kind(self) -> ShadowObservationKind:
        return ShadowObservationKind.AMBIGUOUS

    @property
    def tracker_action(self) -> CompatibilityTrackerAction:
        return CompatibilityTrackerAction.NO_UPDATE

    @property
    def smoothing_action(self) -> SmoothingAction:
        return SmoothingAction.PRESERVE


@dataclass(frozen=True)
class EvidenceUnavailableDecision:
    visibility: float
    confidence: float
    decision_margin: float
    stability_mode: AbsenceStabilityMode
    reason: str
    resources: TemporalResourceMetrics

    def __post_init__(self) -> None:
        _unit(self.visibility, "unavailable visibility")
        _unit(self.confidence, "temporal confidence")
        _unit(self.decision_margin, "temporal decision margin")
        if not isinstance(self.stability_mode, AbsenceStabilityMode):
            raise TypeError("Unavailable decision requires a closed stability mode.")
        if not self.reason:
            raise ValueError("Evidence-unavailable decision requires a reason.")

    @property
    def status(self) -> ShadowTemporalStatus:
        return ShadowTemporalStatus.UNAVAILABLE

    @property
    def observation_kind(self) -> ShadowObservationKind:
        return ShadowObservationKind.UNAVAILABLE

    @property
    def tracker_action(self) -> CompatibilityTrackerAction:
        return CompatibilityTrackerAction.NO_UPDATE

    @property
    def smoothing_action(self) -> SmoothingAction:
        return (
            SmoothingAction.CLEAR_STALE_AFTER_STABLE_ABSENCE
            if self.stability_mode is AbsenceStabilityMode.STABLE
            else SmoothingAction.PRESERVE
        )


@dataclass(frozen=True)
class ReacquisitionPendingDecision:
    pending_hypothesis: SemanticHypothesis
    confidence: float
    decision_margin: float
    reason: str
    resources: TemporalResourceMetrics

    def __post_init__(self) -> None:
        _unit(self.confidence, "temporal confidence")
        _unit(self.decision_margin, "temporal decision margin")
        if not self.reason:
            raise ValueError("Reacquisition decision requires a reason.")

    @property
    def status(self) -> ShadowTemporalStatus:
        return ShadowTemporalStatus.REACQUISITION_PENDING

    @property
    def observation_kind(self) -> ShadowObservationKind:
        return ShadowObservationKind.BOUNDARY

    @property
    def tracker_action(self) -> CompatibilityTrackerAction:
        return CompatibilityTrackerAction.NO_UPDATE

    @property
    def smoothing_action(self) -> SmoothingAction:
        return SmoothingAction.PRESERVE


ShadowTemporalDecision: TypeAlias = (
    BoundaryAcceptedDecision
    | NoInterfaceAcceptedDecision
    | AmbiguousDecision
    | EvidenceUnavailableDecision
    | ReacquisitionPendingDecision
)


@dataclass(frozen=True)
class ShadowResourceSummary:
    raw_observation_count: int
    raw_observation_limit: int
    broad_scale_count: int
    broad_scale_limit: int
    narrow_scale_count: int
    narrow_scale_limit: int
    narrow_examined_rows_per_hypothesis: int
    narrow_examined_rows_per_hypothesis_limit: int
    proposal_count: int
    proposal_limit: int
    maximum_proposal_diameter_px: float
    proposal_diameter_limit_px: float
    maximum_members_per_proposal: int
    members_per_proposal_limit: int
    retained_member_count: int
    retained_member_limit: int
    semantic_hypothesis_count: int
    semantic_hypothesis_limit: int
    temporal_beam_count: int
    temporal_beam_limit: int
    temporal_history_length: int
    temporal_history_limit: int
    retained_temporal_scalar_count: int
    retained_temporal_scalar_limit: int
    static_prior_scalar_count: int
    static_prior_scalar_limit: int
    debug_scalar_count: int
    debug_scalar_limit: int

    def __post_init__(self) -> None:
        values = tuple(
            value for name, value in self.__dict__.items()
            if name not in {"maximum_proposal_diameter_px", "proposal_diameter_limit_px"}
        )
        if any(value < 0 for value in values):
            raise ValueError("Shadow resource counts and limits cannot be negative.")
        _nonnegative_finite(self.maximum_proposal_diameter_px, "maximum proposal diameter")
        _positive_finite(self.proposal_diameter_limit_px, "proposal diameter limit")
        pairs = (
            (self.raw_observation_count, self.raw_observation_limit),
            (self.broad_scale_count, self.broad_scale_limit),
            (self.narrow_scale_count, self.narrow_scale_limit),
            (self.narrow_examined_rows_per_hypothesis, self.narrow_examined_rows_per_hypothesis_limit),
            (self.proposal_count, self.proposal_limit),
            (self.maximum_members_per_proposal, self.members_per_proposal_limit),
            (self.retained_member_count, self.retained_member_limit),
            (self.semantic_hypothesis_count, self.semantic_hypothesis_limit),
            (self.temporal_beam_count, self.temporal_beam_limit),
            (self.temporal_history_length, self.temporal_history_limit),
            (self.retained_temporal_scalar_count, self.retained_temporal_scalar_limit),
            (self.static_prior_scalar_count, self.static_prior_scalar_limit),
            (self.debug_scalar_count, self.debug_scalar_limit),
        )
        if any(count > limit for count, limit in pairs):
            raise ValueError("Shadow resource count exceeds its configured limit.")
        if self.maximum_proposal_diameter_px > self.proposal_diameter_limit_px + 1e-12:
            raise ValueError("Observed proposal diameter exceeds its configured limit.")


@dataclass(frozen=True)
class SuccessfulPipelineFrame:
    raw_observations: tuple[RawEdgeObservation, ...]
    proposals: tuple[BoundedYProposal, ...]
    hypotheses: tuple[SemanticHypothesis, ...]
    current_observation: ShadowCurrentObservation
    frame_height: int
    frame_width: int
    diagnostics: DiagnosticItems = ()

    def __post_init__(self) -> None:
        if any(not isinstance(value, tuple) for value in (
            self.raw_observations, self.proposals, self.hypotheses
        )):
            raise TypeError("Successful pipeline evidence must use immutable tuples.")
        if self.frame_height < 1 or self.frame_width < 1:
            raise ValueError("Successful pipeline frame dimensions must be positive.")
        _diagnostics(self.diagnostics)


@dataclass(frozen=True)
class FailedPipelineFrame:
    reason: str
    stage: PipelineFailureStage
    visibility: float = 0.0
    diagnostics: DiagnosticItems = ()

    def __post_init__(self) -> None:
        if not self.reason:
            raise ValueError("Failed pipeline frame requires a reason.")
        if not isinstance(self.stage, PipelineFailureStage):
            raise TypeError("Failed pipeline frame requires a closed failure stage.")
        _unit(self.visibility, "failure visibility")
        _diagnostics(self.diagnostics)


class OilCanonicalOutcomeBase:
    @property
    def tracker_action(self) -> CompatibilityTrackerAction:
        raise NotImplementedError

    @property
    def smoothing_action(self) -> SmoothingAction:
        raise NotImplementedError


@dataclass(frozen=True)
class AcceptedBoundaryOutcome(OilCanonicalOutcomeBase):
    selected_hypothesis: SemanticHypothesis
    hypotheses: tuple[SemanticHypothesis, ...]
    resources: ShadowResourceSummary
    confidence: float
    decision_margin: float
    acceptance_mode: BoundaryAcceptanceMode
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.hypotheses, tuple):
            raise TypeError("Accepted-boundary hypotheses must be immutable.")
        if self.selected_hypothesis not in self.hypotheses:
            raise ValueError("Accepted boundary must select canonical evidence.")
        _unit(self.confidence, "accepted-boundary confidence")
        _unit(self.decision_margin, "accepted-boundary margin")
        if not isinstance(self.acceptance_mode, BoundaryAcceptanceMode):
            raise TypeError("Accepted boundary requires a closed acceptance mode.")
        if not self.reason:
            raise ValueError("Accepted-boundary outcome requires a reason.")

    @property
    def raw_source_y(self) -> float:
        return self.selected_hypothesis.representative_source_y

    @property
    def status(self) -> ShadowTemporalStatus:
        return ShadowTemporalStatus.BOUNDARY_ACCEPTED

    @property
    def tracker_action(self) -> CompatibilityTrackerAction:
        return CompatibilityTrackerAction.ACCEPT_BOUNDARY

    @property
    def smoothing_action(self) -> SmoothingAction:
        return SmoothingAction.CLEAR_BEFORE_ACCEPT if self.acceptance_mode is BoundaryAcceptanceMode.REACQUIRED else SmoothingAction.PRESERVE


@dataclass(frozen=True)
class NoInterfaceOutcome(OilCanonicalOutcomeBase):
    evidence: ShadowNoInterfaceEvidence
    hypotheses: tuple[SemanticHypothesis, ...]
    resources: ShadowResourceSummary
    confidence: float
    decision_margin: float
    stability_mode: AbsenceStabilityMode
    reason: str

    def __post_init__(self) -> None:
        if not self.evidence.available:
            raise ValueError("No-interface outcome requires positive available evidence.")
        if not isinstance(self.hypotheses, tuple):
            raise TypeError("No-interface hypotheses must be immutable.")
        _unit(self.confidence, "no-interface confidence")
        _unit(self.decision_margin, "no-interface margin")
        if not isinstance(self.stability_mode, AbsenceStabilityMode):
            raise TypeError("No-interface outcome requires a closed stability mode.")
        if not self.reason:
            raise ValueError("No-interface outcome requires a reason.")

    @property
    def status(self) -> ShadowTemporalStatus:
        return ShadowTemporalStatus.NO_INTERFACE_ACCEPTED

    @property
    def tracker_action(self) -> CompatibilityTrackerAction:
        return CompatibilityTrackerAction.NO_UPDATE

    @property
    def smoothing_action(self) -> SmoothingAction:
        return SmoothingAction.CLEAR_STALE_AFTER_STABLE_ABSENCE if self.stability_mode is AbsenceStabilityMode.STABLE else SmoothingAction.PRESERVE


@dataclass(frozen=True)
class AmbiguousOutcome(OilCanonicalOutcomeBase):
    hypotheses: tuple[SemanticHypothesis, ...]
    hypothesis_ids: tuple[str, ...]
    projected_source_y: float | None
    boundary_likelihood: float
    artifact_likelihood: float
    ambiguity_likelihood: float
    no_interface_likelihood: float
    visibility: float
    resources: ShadowResourceSummary
    confidence: float
    decision_margin: float
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.hypotheses, tuple) or not isinstance(self.hypothesis_ids, tuple):
            raise TypeError("Ambiguous outcome evidence must be immutable.")
        canonical_ids = {item.identity for item in self.hypotheses}
        if not set(self.hypothesis_ids) <= canonical_ids:
            raise ValueError("Ambiguous outcome references non-canonical evidence.")
        if self.projected_source_y is not None:
            _finite(self.projected_source_y, "ambiguous outcome diagnostic Y")
        for value, name in (
            (self.boundary_likelihood, "ambiguous boundary likelihood"),
            (self.artifact_likelihood, "ambiguous artifact likelihood"),
            (self.ambiguity_likelihood, "ambiguous likelihood"),
            (self.no_interface_likelihood, "ambiguous no-interface likelihood"),
            (self.visibility, "ambiguous visibility"),
            (self.confidence, "ambiguous confidence"),
            (self.decision_margin, "ambiguous margin"),
        ):
            _unit(value, name)
        if not self.reason:
            raise ValueError("Ambiguous outcome requires a reason.")

    @property
    def status(self) -> ShadowTemporalStatus:
        return ShadowTemporalStatus.AMBIGUOUS

    @property
    def tracker_action(self) -> CompatibilityTrackerAction:
        return CompatibilityTrackerAction.NO_UPDATE

    @property
    def smoothing_action(self) -> SmoothingAction:
        return SmoothingAction.PRESERVE


@dataclass(frozen=True)
class EvidenceUnavailableOutcome(OilCanonicalOutcomeBase):
    hypotheses: tuple[SemanticHypothesis, ...]
    resources: ShadowResourceSummary
    visibility: float
    confidence: float
    decision_margin: float
    stability_mode: AbsenceStabilityMode
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.hypotheses, tuple):
            raise TypeError("Evidence-unavailable hypotheses must be immutable.")
        _unit(self.visibility, "evidence-unavailable visibility")
        _unit(self.confidence, "evidence-unavailable confidence")
        _unit(self.decision_margin, "evidence-unavailable margin")
        if not isinstance(self.stability_mode, AbsenceStabilityMode):
            raise TypeError("Evidence-unavailable outcome requires a closed stability mode.")
        if not self.reason:
            raise ValueError("Evidence-unavailable outcome requires a reason.")

    @property
    def status(self) -> ShadowTemporalStatus:
        return ShadowTemporalStatus.UNAVAILABLE

    @property
    def tracker_action(self) -> CompatibilityTrackerAction:
        return CompatibilityTrackerAction.NO_UPDATE

    @property
    def smoothing_action(self) -> SmoothingAction:
        return SmoothingAction.CLEAR_STALE_AFTER_STABLE_ABSENCE if self.stability_mode is AbsenceStabilityMode.STABLE else SmoothingAction.PRESERVE


@dataclass(frozen=True)
class ReacquisitionPendingOutcome(OilCanonicalOutcomeBase):
    pending_hypothesis: SemanticHypothesis
    hypotheses: tuple[SemanticHypothesis, ...]
    resources: ShadowResourceSummary
    confidence: float
    decision_margin: float
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.hypotheses, tuple):
            raise TypeError("Reacquisition hypotheses must be immutable.")
        if self.pending_hypothesis not in self.hypotheses:
            raise ValueError("Reacquisition must reference canonical evidence.")
        _unit(self.confidence, "reacquisition confidence")
        _unit(self.decision_margin, "reacquisition margin")
        if not self.reason:
            raise ValueError("Reacquisition outcome requires a reason.")

    @property
    def status(self) -> ShadowTemporalStatus:
        return ShadowTemporalStatus.REACQUISITION_PENDING

    @property
    def tracker_action(self) -> CompatibilityTrackerAction:
        return CompatibilityTrackerAction.NO_UPDATE

    @property
    def smoothing_action(self) -> SmoothingAction:
        return SmoothingAction.PRESERVE


@dataclass(frozen=True)
class PipelineFailureOutcome(OilCanonicalOutcomeBase):
    reason: str
    stage: PipelineFailureStage
    visibility: float = 0.0
    diagnostics: DiagnosticItems = ()

    def __post_init__(self) -> None:
        if not self.reason:
            raise ValueError("Pipeline failure outcome requires a reason.")
        if not isinstance(self.stage, PipelineFailureStage):
            raise TypeError("Pipeline failure requires a closed failure stage.")
        _unit(self.visibility, "pipeline failure visibility")
        _diagnostics(self.diagnostics)

    @property
    def tracker_action(self) -> CompatibilityTrackerAction:
        return CompatibilityTrackerAction.NO_UPDATE

    @property
    def smoothing_action(self) -> SmoothingAction:
        return SmoothingAction.PRESERVE


OilCanonicalOutcome: TypeAlias = (
    AcceptedBoundaryOutcome
    | NoInterfaceOutcome
    | AmbiguousOutcome
    | EvidenceUnavailableOutcome
    | ReacquisitionPendingOutcome
    | PipelineFailureOutcome
)
OilShadowFrameResult: TypeAlias = OilCanonicalOutcome


def _diagnostics(items: DiagnosticItems) -> None:
    if not isinstance(items, tuple):
        raise TypeError("Diagnostics must be an immutable tuple.")
    keys = [key for key, _value in items]
    if len(keys) != len(set(keys)) or tuple(sorted(keys)) != tuple(keys):
        raise ValueError("Diagnostics must have unique canonical keys.")
    for key, value in items:
        if not isinstance(key, str) or not key:
            raise ValueError("Diagnostic keys must be non-empty strings.")
        if isinstance(value, float):
            _finite(value, f"diagnostic {key}")
        elif value is not None and not isinstance(value, (str, int, bool)):
            raise TypeError("Diagnostics must contain JSON-safe scalar values.")

def stable_digest(kind: str, scalar_items: tuple[tuple[str, str | int | float | bool | None], ...]) -> str:
    payload = {
        "kind": str(kind),
        "scalars": [
            [str(key), _canonical_scalar(value)] for key, value in sorted(scalar_items)
        ],
    }
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:24]


def _canonical_scalar(value: str | int | float | bool | None) -> str | int | bool | None:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    number = _finite(value, "identity scalar")
    return format(number, ".9f")


def _identity(value: str) -> None:
    if not isinstance(value, str) or len(value) < 8:
        raise ValueError("Deterministic identity must be a non-empty stable string.")


def _identity_tuple(values: tuple[str, ...], name: str) -> None:
    if not isinstance(values, tuple) or not values:
        raise TypeError(f"{name} must be a non-empty immutable tuple.")
    if tuple(sorted(set(values))) != values:
        raise ValueError(f"{name} must be unique and canonically sorted.")
    for value in values:
        _identity(value)


def _finite(value: float, name: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite.")
    return number


def _positive_finite(value: float, name: str) -> float:
    number = _finite(value, name)
    if number <= 0.0:
        raise ValueError(f"{name} must be greater than zero.")
    return number


def _nonnegative_finite(value: float, name: str) -> float:
    number = _finite(value, name)
    if number < 0.0:
        raise ValueError(f"{name} cannot be negative.")
    return number


def _unit(value: float, name: str) -> float:
    number = _finite(value, name)
    if number < -1e-12 or number > 1.0 + 1e-12:
        raise ValueError(f"{name} must be normalized to [0, 1].")
    return number


def _signed_unit(value: float, name: str) -> float:
    number = _finite(value, name)
    if number < -1.0 - 1e-12 or number > 1.0 + 1e-12:
        raise ValueError(f"{name} must be normalized to [-1, 1].")
    return number
