from __future__ import annotations

import inspect

from oil_tracker.adapters.vision.oil_candidate_evidence import (
    OilCandidateEvidence,
)
from oil_tracker.adapters.vision.oil_observation_resolver import (
    OilAdmissionEvidenceOwner,
    OilConnectivityTrackOppositionOwner,
    OilObservationResolver,
    OilPathLifecycleOwner,
    OilResolutionProjectionOwner,
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
        resolver.connectivity_opposition,
        OilConnectivityTrackOppositionOwner,
    )
    assert isinstance(resolver.path_lifecycle, OilPathLifecycleOwner)
    assert isinstance(resolver.projection, OilResolutionProjectionOwner)
    assert resolver.admission_evidence.config is resolver.config
    assert resolver.connectivity_opposition.config is resolver.config
    assert resolver.path_lifecycle.config is resolver.config
    source = inspect.getsource(OilObservationResolver.resolve)
    assert "OilCandidateEvidenceIndex" in source
    assert "admission_evidence.prepare" in source
    assert "connectivity_opposition.resolve" in source
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
