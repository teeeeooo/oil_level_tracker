from dataclasses import dataclass, replace
import math
import pytest
from tests.diagnostics.s11_history_phase_amplification import penalty_map, transplant_penalties

@dataclass(frozen=True)
class Candidate:
    source: str = 'native'
    y: float = 10.

@dataclass(frozen=True)
class Ref:
    frame_offset: int = 1
    candidate_offset: int = 2
    candidate: Candidate = Candidate()
    track_opposition: float = .3
    authority: int = 2
    local_quality: float = .7


def test_scalar_only_without_membership_or_authority_transfer():
    ref=Ref(); absent=Ref(candidate_offset=3)
    donor={(1,2):('native',10.,.2),(1,9):('other',99.,1.)}
    result,edits=transplant_penalties(((ref,absent),),donor)
    assert result==((replace(ref,track_opposition=.2),absent),)
    assert ref.track_opposition==.3 and len(edits)==1
    assert result[0][0].authority==ref.authority
    assert result[0][0].candidate is ref.candidate


def test_noop_donor_preserves_exact_refs():
    frames=((Ref(),),())
    result,edits=transplant_penalties(frames,penalty_map(frames))
    assert result==frames and result[0][0] is frames[0][0] and edits==[]


@pytest.mark.parametrize('source,y',[('other',10.),('native',11.)])
def test_donor_identity_guard(source,y):
    with pytest.raises(ValueError,match='identity mismatch'):
        transplant_penalties(((Ref(),),),{(1,2):(source,y,.2)})


@pytest.mark.parametrize('value',[math.nan,math.inf,-.01,1.01])
def test_invalid_donor_values_fail_closed(value):
    with pytest.raises(ValueError,match='invalid donor scalar'):
        transplant_penalties(((Ref(),),),{(1,2):('native',10.,value)})


@pytest.mark.parametrize('mask',range(8))
def test_factorial_mask_changes_only_selected_blocks(mask):
    from tests.diagnostics.s11_history_phase_factorial import fields_for_mask, transplant_group
    @dataclass(frozen=True)
    class Group:
        y: float = 10.
        local_quality: float = .2
        motion_support: float = .3
        motion_coverage: float = .4
        members: tuple = (Ref(),)
        anchor_signal: bool = False
    original=Group(); donor=dict(y=11.,local_quality=.6,motion_support=.7,motion_coverage=.8)
    result=transplant_group(original,donor,mask)
    assert result.members is original.members and not result.anchor_signal
    assert result==replace(original,**{f:donor[f] for f in fields_for_mask(mask)})
