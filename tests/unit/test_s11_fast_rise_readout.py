from __future__ import annotations

from tests.diagnostics import s11_fast_rise_readout as frr

PARAMS = dict(cap=32.0, bound=96.0, row_tolerance=12.0, motion_min=0.5, coverage_min=0.5)


def _seq(y, *, tier='ANCHOR_ELIGIBLE', row='', ordered_lower=0.0, tracklet='t', source='s'):
    return dict(kind='oil_air', source=source, canonical_y=y, post_track_authority=tier, initial_authority=tier,
                authority=tier, ordered_lower=ordered_lower, row_hypothesis_id=row, tracklet_id=tracklet,
                tracklet_lifecycle='PROVISIONAL', tracklet_admitted=0.0, tracklet_failure_reason='PROVISIONAL_TRACKLET',
                selected=False)


def _features(*, motion=0.8, coverage=0.8, high_recall=0.0):
    return dict(registered_oil_band_motion_support=motion, registered_oil_band_motion_coverage=coverage,
                calibrated_high_recall=high_recall)


def _row(y, **kwargs):
    item = frr.member(_seq(y, row=f'r{y}'), [_features(**kwargs)])
    return frr.rows_of([item], PARAMS)[0]


def _frame(offset, *rows):
    return dict(offset=offset, frame=offset * 15, time=offset * 0.5, rows=list(rows))


def test_member_keeps_only_builder_eligible_oil_and_joins_detector_features():
    assert frr.member(_seq(500.0, tier='CANDIDATE_ONLY'), [_features()]) is None
    assert frr.member(_seq(500.0, tier=None), [_features()]) is None
    item = frr.member(_seq(500.0, tier='CONTINUATION_ELIGIBLE'), [_features(motion=0.4), _features(motion=0.7)])
    assert (item['tier'], item['motion'], item['ambiguous_join']) == (2, 0.7, True)


def test_record_join_matches_on_source_and_y():
    record = dict(candidates=[dict(kind='oil_air', source='a', canonical_y=500.0, features=_features(motion=0.9)),
                              dict(kind='foam_front', source='a', canonical_y=500.0, features={})],
                  sequence=dict(candidates=[_seq(500.0, source='a'), _seq(501.0, source='a')]))
    pairs = frr.joined(record)
    assert [len(matches) for _, matches in pairs] == [1, 0]


def test_rows_follow_trace_ids_and_need_all_four_witness_parts():
    members = [frr.member(_seq(500.0, row='r1', tier='CONTINUATION_ELIGIBLE'), [_features()]),
               frr.member(_seq(504.0, row='r1'), [_features(high_recall=1.0)]),
               frr.member(_seq(560.0, row='r2'), [_features(coverage=0.4)])]
    first, second = frr.rows_of(members, PARAMS)
    assert (first['y'], first['members'], first['anchor'], first['physical'], first['witness']) == (502.0, 2, True, True, True)
    assert (second['y'], second['witness']) == (560.0, False)


def test_rows_without_an_id_use_the_builder_span_rule():
    members = [frr.member(_seq(y), [_features()]) for y in (500.0, 510.0, 530.0)]
    assert [row['members'] for row in frr.rows_of(members, PARAMS)] == [2, 1]


def test_triplets_need_consecutive_frames_upward_steps_beyond_the_cap_and_within_the_bound():
    frames = [_frame(0, _row(700.0)), _frame(1, _row(630.0)), _frame(2, _row(560.0), _row(640.0))]
    (item,) = frr.triplets(frames, PARAMS)
    assert (item['steps'], item['constant_velocity'], item['qualifies']) == ([-70.0, -70.0], True, True)
    assert frr.triplets([frames[0], frames[1], _frame(3, _row(560.0))], PARAMS) == []  # a gap
    assert frr.triplets([_frame(0, _row(700.0)), _frame(1, _row(670.0)), _frame(2, _row(640.0))], PARAMS) == []
    assert frr.triplets([_frame(0, _row(700.0)), _frame(1, _row(600.0)), _frame(2, _row(500.0))], PARAMS) == []


def test_a_triplet_qualifies_only_with_constant_velocity_shared_representation_and_three_witnesses():
    def one(third, **kwargs):
        frames = [_frame(0, _row(700.0)), _frame(1, _row(630.0)), _frame(2, third)]
        return frr.triplets(frames, PARAMS)[0]

    assert not one(_row(540.0))['constant_velocity']  # steps -70, -90
    assert not one(_row(560.0, motion=0.2))['qualifies']
    lower = frr.rows_of([frr.member(_seq(560.0, row='x', ordered_lower=1.0), [_features()])], PARAMS)[0]
    assert not one(lower)['same_representation']


def test_readout_counts_only_the_window():
    frames = [_frame(0, _row(700.0)), _frame(1, _row(630.0)), _frame(2, _row(560.0))]
    for frame in frames:
        frame.update(oil_candidates=1, eligible=1, ambiguous_joins=0)
    window, found, counts = frr.readout(frames, PARAMS, 0.5, 1.0)
    assert (len(window), counts['rows'], counts['upward_beyond_cap']) == (2, 2, 0)
    _, _, counts = frr.readout(frames, PARAMS, 0.0, 1.0)
    assert (counts['witnessed'], counts['qualifying']) == (3, 1)
