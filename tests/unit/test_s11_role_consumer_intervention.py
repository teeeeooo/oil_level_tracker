from copy import deepcopy
import itertools

import pytest

from oil_tracker.adapters.vision.oil_candidate_authority import (
    AuthorityDecision, AuthorityReason, OilCandidateAuthority as Tier,
)
from tests.diagnostics.s11_role_consumer_intervention import (
    VARIANTS, bind_controls, control_status, intervene_authority, prepare_input, sampled_runs,
)


def raw_and_units():
    raw = [{'frame_index': 90, 'candidates': [
        {'source': 'same', 'kind': 'oil_air', 'y': 8.0, 'features': {'sequence_eligible': 1.0}},
        {'source': 'same', 'kind': 'oil_air', 'y': 8.0, 'features': {'sequence_eligible': 1.0}},
        {'source': 'foam', 'kind': 'foam_front', 'y': 4.0, 'features': {}},
    ]}]
    unit = {'id': 'physical', 'group': 'sample4', 'review_label': 'ACCEPTED',
            'query': {'frame': 90, 'candidate_index': 0, 'source': 'same', 'source_xy': [5, 8.0]},
            'label_basis': {'physical': 'TARGET_CORRESPONDENCE', 'practical': 'NOT_REVIEWED'}}
    return raw, [unit]


@pytest.mark.parametrize('variant,tier', list(itertools.product(VARIANTS, list(Tier))))
def test_unreviewed_authority_is_unchanged(variant, tier):
    d = AuthorityDecision(tier, AuthorityReason.CONTINUATION, ('original',))
    assert intervene_authority(d, variant=variant, opposed=False, physical_positive=False) is d


@pytest.mark.parametrize('tier', list(Tier))
def test_demotion_only_changes_opposed_anchor(tier):
    d = AuthorityDecision(tier, AuthorityReason.ORDERED_LOWER_INTERFACE)
    result = intervene_authority(d, variant='negative_anchor_demotion', opposed=True, physical_positive=False)
    assert result.tier == (Tier.CONTINUATION_ELIGIBLE if tier == Tier.ANCHOR_ELIGIBLE else tier)
    assert result.reason == d.reason  # Preserve original reason; diagnostic tag explains inconsistency.
    assert d.tier == tier


@pytest.mark.parametrize('variant,tier', list(itertools.product(
    ['positive_authority_only','negative_veto_positive_authority'], list(Tier))))
def test_positive_intervention_does_not_rescue_hard_invalid(variant, tier):
    d=AuthorityDecision(tier, AuthorityReason.INSUFFICIENT_AUTHORITY)
    result=intervene_authority(d, variant=variant, opposed=False, physical_positive=True)
    assert result.tier == (Tier.HARD_INVALID if tier == Tier.HARD_INVALID else Tier.ANCHOR_ELIGIBLE)


def test_practical_acceptance_not_physical_anchor():
    raw, units=raw_and_units()
    units[0]['label_basis']={'physical': 'NOT_QUALIFIED', 'practical': 'ACCEPTED_APPROXIMATION'}
    c=bind_controls(raw, units)[0]
    assert c['practical_only'] and not c['physical_positive']


def test_exact_index_not_same_y_alias():
    raw, units=raw_and_units()
    units[0]['review_label']='OPPOSED'
    units[0]['label_basis']={'physical': 'OPPOSED_OIL_TARGET'}
    controls=bind_controls(raw,units)
    before=deepcopy(raw)
    changed, edits=prepare_input(raw,controls,'negative_member_veto')
    assert raw == before
    assert len(edits)==1 and changed[0]['candidates'][0]['features']['sequence_eligible']==0
    assert changed[0]['candidates'][1:] == raw[0]['candidates'][1:]
    assert len(changed[0]['candidates'])==len(raw[0]['candidates'])


def test_no_label_propagation_to_other_frame():
    raw, units=raw_and_units()
    units[0]['review_label']='OPPOSED'
    raw.append({**deepcopy(raw[0]),'frame_index':91})
    controls=bind_controls(raw,units)
    changed,_=prepare_input(raw,controls,'negative_member_veto')
    assert changed[1]==raw[1]


@pytest.mark.parametrize('change', ['source','y','index','frame','kind','duplicate'])
def test_binding_fail_closed(change):
    raw,units=raw_and_units()
    if change=='source': units[0]['query']['source']='other'
    if change=='y': units[0]['query']['source_xy'][1]=9
    if change=='index': units[0]['query']['candidate_index']=100
    if change=='frame': units[0]['query']['frame']=999
    if change=='kind': raw[0]['candidates'][0]['kind']='foam_front'
    if change=='duplicate': units.append(deepcopy(units[0]))
    with pytest.raises(ValueError): bind_controls(raw,units)


def test_unreviewed_and_other_source_not_injected():
    raw,units=raw_and_units()
    units[0]['review_label']='UNASSESSED'
    public=deepcopy(units[0]); public.update(group='public',review_label='ACCEPTED')
    public['query']['frame']=1234
    assert bind_controls(raw,[*units,public])==[]


@pytest.mark.parametrize('variant', ['baseline','negative_anchor_demotion','positive_authority_only'])
def test_non_veto_variants_do_not_edit_candidates(variant):
    raw,units=raw_and_units(); controls=bind_controls(raw,units)
    changed,edits=prepare_input(raw,controls,variant)
    assert changed==raw and not edits
    assert changed is not raw


def test_selected_same_y_unknown_remains_unknown():
    raw,units=raw_and_units(); controls=bind_controls(raw,units)
    row={'frame_index':90,'selected':{'candidate_offset':1,'source':'same','y':8.0}}
    assert control_status(row,controls)=='UNASSESSED_SELECTION'
    row['selected']['candidate_offset']=0
    assert control_status(row,controls)=='PHYSICAL_CORRESPONDENCE'
    row['selected']=None
    assert control_status(row,controls)=='NO_NUMERIC_OIL'


def test_run_span_is_not_invented_sample_duration():
    rows=[{'time_sec':t,'ok':b} for t,b in [(0,False),(.5,True),(1,True),(1.5,False),(2,True)]]
    assert sampled_runs(rows,lambda r:r['ok'])==[
        {'start_sec':.5,'last_sample_sec':1,'sample_count':2,'sampled_span_sec':.5},
        {'start_sec':2,'last_sample_sec':2,'sample_count':1,'sampled_span_sec':0}]


def test_empty_runs():
    assert sampled_runs([],lambda r:True)==[]


def test_unknown_variant_rejected():
    with pytest.raises(ValueError): prepare_input([],[],'tuned_after_run')


def test_full_event_join_accepts_same_frame_values():
    from tests.diagnostics.s11_role_consumer_verify import verify_event_sample
    event = {'representative_frame_index': '12', 'start_time_sec': '2',
             'oil_level_px': '8', 'foam_front_px': '12'}
    sample = {'timestamp_sec': '2', 'smoothed_oil_air_level_px_from_zero': '8',
              'smoothed_foam_front_px_from_zero': '12'}
    verify_event_sample(event, {'12': sample})


@pytest.mark.parametrize('field,value', [('representative_frame_index','13'),('start_time_sec','3'),
                                        ('oil_level_px','9'),('foam_front_px','13')])
def test_full_event_join_rejects_mismatched_output(field, value):
    from tests.diagnostics.s11_role_consumer_verify import verify_event_sample
    event = {'representative_frame_index': '12', 'start_time_sec': '2',
             'oil_level_px': '8', 'foam_front_px': '12', field: value}
    sample = {'timestamp_sec': '2', 'smoothed_oil_air_level_px_from_zero': '8',
              'smoothed_foam_front_px_from_zero': '12'}
    with pytest.raises(ValueError): verify_event_sample(event, {'12': sample})


def test_foam_event_does_not_require_an_oil_coordinate():
    from tests.diagnostics.s11_role_consumer_verify import verify_event_sample
    event = {'representative_frame_index': '12', 'start_time_sec': '2',
             'oil_level_px': '', 'foam_front_px': '12'}
    sample = {'timestamp_sec': '2', 'smoothed_oil_air_level_px_from_zero': '',
              'smoothed_foam_front_px_from_zero': '12'}
    verify_event_sample(event, {'12': sample})
