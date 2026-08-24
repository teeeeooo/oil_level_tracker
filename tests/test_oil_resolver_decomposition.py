from __future__ import annotations

import inspect

import oil_tracker.adapters.vision.oil_observation_resolver as resolver_module
from oil_tracker.adapters.vision.oil_candidate_evidence import (
    OilCandidateEvidence,
)
from oil_tracker.adapters.vision.oil_observation_resolver import (
    OilAdmissionEvidenceOwner,
    OilObservationResolver,
    OilPathLifecycleOwner,
    OilResolutionProjectionOwner,
    OilTrackletOppositionOwner,
)
from test_r16_refactor_characterization import (
    _glass,
    _sequence_candidate,
    _sequence_detection,
)


def _detections():
    return tuple(
        _sequence_detection(
            index,
            _sequence_candidate(
                160.0 - index,
                boundary=0.72 if index < 3 or index >= 8 else 0.24,
                broad=0.62 if index < 3 or index >= 8 else 0.30,
                artifact=0.08 if index < 3 or index >= 8 else 0.21,
                ambiguity=0.20 if index < 3 or index >= 8 else 0.62,
            ),
        )
        for index in range(11)
    )


def test_resolver_facade_coordinates_cohesive_policy_owners() -> None:
    resolver = OilObservationResolver()

    assert isinstance(resolver.admission_evidence, OilAdmissionEvidenceOwner)
    assert isinstance(
        resolver.tracklet_opposition,
        OilTrackletOppositionOwner,
    )
    assert isinstance(resolver.path_lifecycle, OilPathLifecycleOwner)
    assert isinstance(resolver.projection, OilResolutionProjectionOwner)
    assert resolver.admission_evidence.config is resolver.config
    assert resolver.tracklet_opposition.config is resolver.config
    assert resolver.path_lifecycle.config is resolver.config
    source = inspect.getsource(OilObservationResolver.resolve)
    assert "OilCandidateEvidenceIndex" in source
    assert "admission_evidence.prepare" in source
    assert "tracklet_opposition.resolve" in source
    assert "path_lifecycle.resolve" in source
    assert "projection.project" in source


def test_completed_window_normalizes_candidate_evidence_once(monkeypatch) -> None:
    detections = _detections()
    expected = sum(len(detection.candidates) for detection in detections)
    calls = 0
    original = OilCandidateEvidence.from_candidate.__func__

    def counted(cls, candidate):
        nonlocal calls
        calls += 1
        return original(cls, candidate)

    monkeypatch.setattr(
        OilCandidateEvidence,
        "from_candidate",
        classmethod(counted),
    )

    OilObservationResolver().resolve(detections, _glass())

    assert calls == expected


def test_path_lifecycle_has_one_extracted_selector_and_phase_owner() -> None:
    module_source = inspect.getsource(resolver_module)
    lifecycle_source = inspect.getsource(OilPathLifecycleOwner)

    assert "BoundedOilInterfaceSelector" in lifecycle_source
    assert "OilMaterialPhaseLifecycleOwner" in lifecycle_source
    assert len(lifecycle_source.splitlines()) <= 260
    assert len(module_source.splitlines()) <= 2_700
    for retired_owner in (
        "_bounded_tracklet_path",
        "_suppress_completed_fill_reacquisition",
        "_completed_fill_phase_witness",
        "_is_confirmed_downward_reacquisition",
    ):
        assert retired_owner not in module_source
