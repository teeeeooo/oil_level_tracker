"""Scope checks for late-stage causal diagnostics, not evidence policies."""
from dataclasses import dataclass
from copy import deepcopy
from types import SimpleNamespace
import pytest
from oil_tracker.domain.enums import BoundaryKind
from tests.diagnostics.s11_single_observation_causality import late_foam_input, filtered_tracklets


@dataclass(frozen=True)
class Candidate:
    kind: BoundaryKind
    features: dict


@dataclass(frozen=True)
class Detection:
    frame_index: int
    candidates: tuple


@dataclass(frozen=True)
class TrackResult:
    refs_by_frame: tuple
    history: str = 'original confirmation is explicitly frozen'


def test_late_foam_only_changes_named_final_input():
    oil=Candidate(BoundaryKind.OIL_AIR,{'sequence_eligible':1})
    foam=Candidate(BoundaryKind.FOAM_FRONT,{'sequence_foam_eligible':1,'other':4})
    raw=(Detection(15,(oil,foam)),Detection(30,(oil,foam)))
    before=deepcopy(raw); changed=late_foam_input(raw,15)
    assert raw==before and changed[1]==raw[1]
    assert changed[0].candidates[0]==oil
    assert changed[0].candidates[1].features=={'sequence_foam_eligible':0,'other':4}


@pytest.mark.parametrize('index,remaining',[(0,[1]),(None,[])])
def test_late_track_drops_members_not_original_history(index,remaining):
    def ref(i): return SimpleNamespace(candidate_offset=i,candidate=SimpleNamespace(source='x',y=10+i))
    raw=TrackResult(((ref(0),ref(1)),(ref(0),)))
    before=deepcopy(raw); changed,removed=filtered_tracklets(raw,0,index)
    assert raw==before and changed.history==raw.history
    assert [r.candidate_offset for r in changed.refs_by_frame[0]]==remaining
    assert changed.refs_by_frame[1]==raw.refs_by_frame[1]
    assert len(removed)==2-len(remaining)


def test_late_track_empty_withdrawal_fails():
    with pytest.raises(ValueError): filtered_tracklets(TrackResult(((),)),0,None)
