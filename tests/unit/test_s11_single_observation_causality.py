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


from tests.diagnostics.s11_single_observation_causal_verify import members, stage_difference
from tests.diagnostics.s11_single_observation_backfill import without_backfill


def test_stage_identity_change_is_separate_from_coordinate_change():
    a=[[dict(frame_offset=0,candidate_offset=1,tracklet_id='a',y=10)]]
    b=[[dict(frame_offset=0,candidate_offset=1,tracklet_id='b',y=10)]]
    delta=stage_difference(a,b,[dict(frame_index=15,time_sec=.5)])
    assert delta['field_counts']=={'tracklet_id':1}
    assert not delta['added'] and not delta['removed']


def test_stage_member_key_mismatch_and_duplicates_fail():
    with pytest.raises(ValueError): members([[dict(frame_offset=1,candidate_offset=0)]])
    with pytest.raises(ValueError): members([[dict(frame_offset=0,candidate_offset=0)]*2])


def test_no_backfill_never_restores_missing_member_or_filters_other_frames():
    def ref(i): return SimpleNamespace(candidate_offset=i,candidate=SimpleNamespace(source='x',y=10+i))
    raw=((ref(1),ref(2)),(ref(2),)); before=deepcopy(raw)
    changed,removed=without_backfill(raw,[{0,1},{0}],0)
    assert raw==before and [r.candidate_offset for r in changed[0]]==[1]
    assert changed[1]==raw[1] and [r['candidate_offset'] for r in removed]==[2]
