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
