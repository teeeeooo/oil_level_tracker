"""Scope and accounting controls for diagnostic eligibility-loss experiments."""
from copy import deepcopy
import pytest
from tests.diagnostics.s11_single_observation_influence import intervene, enumerate_cases, case_id, representatives


def raw_fixture():
    def candidate(kind, source, y, **features):
        return dict(kind=kind, source=source, y=y, features=features)
    return [dict(frame_index=15, time_sec=.5, candidates=[
        candidate('oil_air', 'material_path', 10, sequence_eligible=1),
        candidate('foam_front', 'foam', 5, sequence_foam_eligible=1),
        candidate('oil_air', 'edge', 10)]),
        dict(frame_index=30, time_sec=1, candidates=[candidate('oil_air','edge',12)])]


@pytest.mark.parametrize('mode,count,field', [('selected_oil',1,'sequence_eligible'),
    ('all_oil',2,'sequence_eligible'),('all_foam',1,'sequence_foam_eligible')])
def test_only_declared_fields_withdrawn(mode, count, field):
    raw = raw_fixture(); before = deepcopy(raw)
    changed, edits = intervene(raw, dict(mode=mode, frame=15, index=0))
    assert raw == before and len(edits) == count
    restored = deepcopy(changed)
    for edit in edits:
        features = restored[0]['candidates'][edit['index']]['features']
        assert features[field] == 0
        if edit['before_present']: features[field] = edit['before']
        else: del features[field]
    assert restored == before


@pytest.mark.parametrize('case', [dict(mode='bad',frame=15,index=0),
    dict(mode='all_oil',frame=99,index=None), dict(mode='selected_oil',frame=15,index=1)])
def test_invalid_interventions_fail_closed(case):
    with pytest.raises(ValueError): intervene(raw_fixture(), case)


def test_baseline_and_duplicate_frames():
    raw = raw_fixture()
    assert intervene(raw,None) == (raw,[])
    with pytest.raises(ValueError): intervene([raw[0],raw[0]],dict(mode='all_oil',frame=15,index=None))


def test_population_uses_original_selected_offset_and_retains_unselected_frames():
    raw = raw_fixture()
    baseline = [dict(debug_metrics=dict(sequence_decision_witness=dict(selection=dict(selected_candidate=s))))
        for s in [dict(candidate_offset=2),None]]
    cases = enumerate_cases(raw,baseline)
    assert [c['mode'] for c in cases] == ['selected_oil','all_oil','all_oil','all_foam']
    assert cases[0]['index'] == 2 and cases[2]['frame'] == 30
    assert len({case_id(c) for c in cases}) == 4


def test_representatives_tie_by_earliest_frame_not_truth():
    rows = [dict(id=f'{m}-{f}',case=dict(mode=m,frame=f),oil_changed_elsewhere=2,foam_changed_elsewhere=4)
        for m in ['selected_oil','all_oil','all_foam'] for f in [30,15]]
    assert representatives(rows) == ['selected_oil-15','all_oil-15','all_foam-15']


from tests.diagnostics.s11_single_observation_verify import check_row, runs


def row_fixture():
    return dict(frame_index=15,time_sec=.5,oil_y=10,foam_y=5,
        selected=dict(candidate_offset=0,source='material_path',y=10),
        sample=dict(frame_index=15,timestamp_sec=.5,raw_oil_air_level_y=10,raw_foam_front_y=5))


def test_independent_row_verifier():
    check_row(row_fixture(),raw_fixture()[0])


@pytest.mark.parametrize('field,value',[('oil_y',11),('foam_y',8),('frame_index',30),('time_sec',1)])
def test_independent_verifier_detects_bad_join(field,value):
    row=row_fixture(); row[field]=value
    with pytest.raises(ValueError): check_row(row,raw_fixture()[0])


def test_irregular_sample_spans_are_not_continuous_durations():
    rows=[dict(time_sec=t,oil_y=y) for t,y in [(0,None),(.5,10),(2,10),(3,None)]]
    assert runs(rows,'oil_y',True)==[dict(start_sec=.5,last_sample_sec=2,sample_count=2,sampled_span_sec=1.5)]
    assert runs(rows,'oil_y',False)[-1]['sampled_span_sec']==0


from tests.diagnostics.s11_single_observation_verify import check_event_levels


def test_coordinate_free_lifecycle_event_is_not_fabricated_sample():
    sample=dict(smoothed_oil_air_level_px_from_zero=-1,smoothed_foam_front_px_from_zero=4)
    check_event_levels(dict(event_type='ANALYSIS_END',oil_level_px=None,foam_front_px=None),sample)
    check_event_levels(dict(event_type='MAXIMUM_OIL_LEVEL',oil_level_px=-1,foam_front_px=4),sample)
    for event in [dict(event_type='MAXIMUM_OIL_LEVEL',oil_level_px=2,foam_front_px=4),
        dict(event_type='MAXIMUM_OIL_LEVEL',oil_level_px=-1,foam_front_px=5),
        dict(event_type='MAXIMUM_OIL_LEVEL',oil_level_px=None,foam_front_px=4),
        dict(event_type='ANALYSIS_END',oil_level_px=-1,foam_front_px=None)]:
        with pytest.raises(ValueError): check_event_levels(event,sample)
