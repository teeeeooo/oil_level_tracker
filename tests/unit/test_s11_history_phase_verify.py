from copy import deepcopy
import pytest
from tests.diagnostics.s11_history_phase_verify import check_scalar_capture, check_group_capture


def scalar_fixture():
    row=dict(frame_offset=0,candidate_offset=2,source='native',y=12.,authority=3,track_opposition=.2)
    capture=dict(recurrence_native=[[row]],recurrence_used=[[dict(row,track_opposition=.3)]],
                 scalar_edits=[dict(frame_offset=0,candidate_offset=2,source='native',y=12.,before=.2,after=.3)])
    donor=[[dict(row,track_opposition=.3)]]
    return capture,donor


def test_scalar_verifier_accepts_only_exact_scope():
    c,d=scalar_fixture();assert check_scalar_capture(c,d)==1


@pytest.mark.parametrize('mutation',['authority','y','source','membership','ledger'])
def test_scalar_verifier_rejects_corrupted_scope(mutation):
    c,d=scalar_fixture()
    if mutation in ('authority','y','source'):c['recurrence_used'][0][0][mutation]='corrupt'
    elif mutation=='membership':c['recurrence_used'][0].append(dict(c['recurrence_used'][0][0],candidate_offset=3))
    else:c['scalar_edits'][0]['after']=.4
    with pytest.raises(ValueError):check_scalar_capture(c,d)


def group_fixture():
    group=dict(members=[2],y=12.,local_quality=.4,motion_support=.5,motion_coverage=.6)
    zero=dict(row_groups=[[group]])
    pre=dict(offset=0,current=group,donor=dict(group,y=11.,local_quality=.7,motion_support=.8,motion_coverage=.9))
    after=dict(group,y=11.)
    c=dict(row_groups=[[after]],group_edits=[dict(mask=1,before=group,after=after)])
    return c,zero,pre


def test_group_verifier_accepts_single_geometry_block():
    check_group_capture(*group_fixture(),1)


@pytest.mark.parametrize('field',['members','local_quality','motion_support','motion_coverage'])
def test_group_verifier_rejects_unlisted_mutation(field):
    c,z,p=deepcopy(group_fixture());c['row_groups'][0][0][field]='corrupt'
    with pytest.raises(ValueError):check_group_capture(c,z,p,1)
