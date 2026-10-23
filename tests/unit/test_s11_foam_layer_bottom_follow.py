from tests.diagnostics import s11_foam_layer_bottom_follow as flb


def _frame(time, ordinary, foam=(), rows=()):
    return dict(time=time, frame=int(time * 30), ordinary_y=ordinary, foam=list(foam), oil_rows=sorted(rows))


def _run(frames):
    return flb.follow(frames, tolerance=5.0, max_jump=32.0)


def test_follows_the_layer_bottom_then_hands_off_below_it():
    out = _run([
        _frame(1.0, 840.0),                                            # no Foam: ordinary
        _frame(1.5, 851.0, [(813.0, 834.0, True)], [820.0, 829.0, 851.0]),
        _frame(2.0, 851.0, [(858.0, 883.0, False)], [851.0]),          # layer gone: hand off
        _frame(2.5, 852.0, [(837.0, 837.0, True)], [837.0, 852.0]),    # bottom far above the Oil: no re-entry
    ])
    assert [(r['y'], r['state'], r['reason']) for r in out] == [
        (840.0, flb.NONE, 'ORDINARY'),
        (829.0, flb.FOLLOW, 'FOLLOW_LAYER_BOTTOM'),
        (851.0, flb.HANDOFF, 'HANDOFF_BELOW_LAST_BOTTOM'),
        (852.0, flb.HANDOFF, 'HANDOFF_BELOW_LAST_BOTTOM'),
    ]


def test_fails_closed_without_a_row_at_the_bottom_or_with_output_above_it():
    out = _run([
        _frame(1.0, 851.0, [(813.0, 834.0, True)], [851.0]),           # no row within 5 px
        _frame(1.5, 820.0, [], [820.0]),                               # hand-off output above the bottom
        _frame(2.0, None, [], []),
    ])
    assert [(r['y'], r['reason']) for r in out] == [
        (None, 'FOLLOW_NO_ROW'), (None, 'HANDOFF_ABOVE_LAST_BOTTOM'), (None, 'HANDOFF_NO_LOWER_OUTPUT')]


def test_reenters_when_the_bottom_meets_the_oil_and_breaks_on_a_jump():
    out = _run([
        _frame(1.0, 840.0, [(813.0, 834.0, True)], [833.0]),
        _frame(1.5, 836.0, [], [836.0]),                               # hand off at 836
        _frame(2.0, 860.0, [(812.0, 838.0, True)], [838.0, 860.0]),    # bottom 2 px from 836: re-enter
        _frame(2.5, 860.0, [(812.0, 880.0, True)], [880.0, 860.0]),    # 42 px jump: not the same layer
    ])
    assert [(r['y'], r['state']) for r in out] == [
        (833.0, flb.FOLLOW), (836.0, flb.HANDOFF), (838.0, flb.FOLLOW), (860.0, flb.HANDOFF)]


def test_nearest_row_prefers_the_lower_row_on_a_tie_and_ignores_ineligible_foam():
    assert flb.nearest_row([830.0, 838.0], 834.0, 5.0) == 838.0
    assert flb.witness(_frame(1.0, None, [(820.0, 840.0, False), (815.0, None, True)])) is None
    assert flb.witness(_frame(1.0, None, [(818.0, 836.0, True), (812.0, 834.0, True)])) == 834.0


def test_scoring_uses_bands_accepted_and_wrong_values():
    ref = dict(accepted=[841.0], wrong=[865.5], band=None, confidence='clear')
    assert [flb.outcome(y, ref) for y in (843.0, 865.0, None, 900.0)] == ['C', 'A', 'B', 'A']
    band = dict(accepted=[], wrong=[], band=[828.7, 840.9], confidence='approximate')
    assert [flb.outcome(y, band) for y in (829.0, 851.0)] == ['C', 'A']
    assert flb.outcome(None, dict(accepted=[], wrong=[805.0], band=None, confidence='clear')) is None


# --- FLB-2 -------------------------------------------------------------------------

def _layer(y, bottom, eligible=True, phenotype='detached_layer'):
    return dict(y=y, bottom=bottom, eligible=eligible, phenotype=phenotype)


def _frame2(time, ordinary, foam=(), rows=()):
    return dict(time=time, frame=int(time * 30), ordinary_y=ordinary, foam_full=list(foam), oil_rows=sorted(rows))


def _run2(frames):
    return [(r['y'], r['state'], r['reason']) for r in flb.follow2(frames, tolerance=5.0, max_jump=32.0)]


def test_layer_witness_takes_only_eligible_detached_layers_highest_front_first():
    assert flb.layer_witness(_frame2(1.0, None, [_layer(810.0, 834.0, phenotype='detached_droplet'),
                                                 _layer(805.0, 830.0, eligible=False),
                                                 _layer(812.0, None)])) is None
    assert flb.layer_witness(_frame2(1.0, None, [_layer(815.0, 838.0), _layer(812.0, 836.0)])) == 836.0


def test_entry_needs_the_bottom_near_the_recent_output_or_no_recent_output():
    assert _run2([
        _frame2(1.0, 830.0),
        _frame2(1.5, 830.0, [_layer(840.0, 860.0)], [858.0]),   # 30 px from the 1.0 s output: no entry
        _frame2(5.0, None),
        _frame2(5.5, None, [_layer(840.0, 860.0)], [858.0]),    # no output in the last 3 s: entry
    ]) == [(830.0, flb.NONE, 'ORDINARY'), (830.0, flb.NONE, 'ORDINARY'),
           (None, flb.NONE, 'ORDINARY'), (858.0, flb.FOLLOW, 'FOLLOW_LAYER_BOTTOM')]


def test_follow_breaks_on_a_jump_and_hands_off_below_the_last_bottom():
    assert _run2([
        _frame2(1.0, 851.0, [_layer(813.0, 834.0)], [833.0, 851.0]),
        _frame2(1.5, 870.0, [_layer(813.0, 870.0)], [870.0]),   # 36 px jump: not the same layer
        _frame2(2.0, 820.0),                                    # above the last bottom: nothing
    ]) == [(833.0, flb.FOLLOW, 'FOLLOW_LAYER_BOTTOM'), (870.0, flb.HANDOFF, 'HANDOFF_BELOW_LAST_BOTTOM'),
           (None, flb.HANDOFF, 'HANDOFF_ABOVE_LAST_BOTTOM')]


def test_handoff_memory_expires_three_seconds_after_the_last_witness():
    assert _run2([
        _frame2(1.0, 851.0, [_layer(813.0, 834.0)], [833.0]),
        _frame2(1.5, 851.0, [_layer(815.0, 840.0)], [841.0]),
        _frame2(2.5, 851.0, [_layer(850.0, 880.0)], [880.0]),   # 40 px jump from the last bottom: hand off
        _frame2(4.5, 820.0),                                    # 3.0 s after the last witness: still held
        _frame2(4.6, 820.0),                                    # 3.1 s: expired, ordinary again
    ]) == [(833.0, flb.FOLLOW, 'FOLLOW_LAYER_BOTTOM'), (841.0, flb.FOLLOW, 'FOLLOW_LAYER_BOTTOM'),
           (851.0, flb.HANDOFF, 'HANDOFF_BELOW_LAST_BOTTOM'), (None, flb.HANDOFF, 'HANDOFF_ABOVE_LAST_BOTTOM'),
           (820.0, flb.NONE, 'ORDINARY')]


def test_review012_references_and_held_out_readings():
    table_v = [dict(frame=10, y_range=[300.0, 304.0], words=''),
               dict(frame=20, y_range=[310.0, 312.0], words='대략'),
               dict(frame=30, y_range=None, words='안 보임'),
               dict(frame=40, y_range=None, words='')]
    refs = flb.review_references(table_v, 10.0)
    assert refs[10]['band'] == [290.0, 314.0] and refs[10]['confidence'] == 'clear'
    assert refs[20]['confidence'] == 'approximate' and refs[30]['confidence'] == 'not_visible' and 40 not in refs
    assert [flb.outcome(y, refs[30]) for y in (None, 305.0)] == ['C', 'A']
    rows = [dict(time=1.0, frame=10, ordinary_y=302.0, y=303.0, reason='FOLLOW_LAYER_BOTTOM'),
            dict(time=2.0, frame=20, ordinary_y=350.0, y=311.0, reason='FOLLOW_LAYER_BOTTOM'),
            dict(time=3.0, frame=30, ordinary_y=None, y=None, reason='ORDINARY')]
    result = flb.held_out(rows, table_v, 10.0)
    assert result['counts'] == {'ordinary': {'C': 2, 'A': 1}, 'rule': {'C': 3}}
    assert result['r1_no_clear_regression'] and result['r2_fewer_wrong'] and result['r3_follow_tested']
    rows[0]['y'] = None  # a clear-mark frame turned from C to B
    assert flb.held_out(rows, table_v, 10.0)['regressions'][0]['frame'] == 10
