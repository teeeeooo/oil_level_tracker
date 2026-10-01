"""Paired aggregation controls; synthetic arithmetic is not field efficacy."""
import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from tests.diagnostics import s11_shadow_experiment as e
from tests.unit.test_s11_shadow_experiment import candidate, inputs  # noqa: F401


def point(values, widths=(8, 16, 24)):
    return {
        'geometry_basis': 'native_path', 'source_x_range': [0, 20], 'source_y': 10,
        'scales': [{'band_width_px': w, 'scores': dict.fromkeys(e.METHODS, v)}
                   for w, v in zip(widths, values)],
        'matched_scores': dict.fromkeys(e.METHODS, e.median([v for v in values if v is not None])),
    }


def test_positive_and_counter_control_show_both_directions():
    a, b = point([.9, .4, .2]), point([.6, .5, .1])
    before = copy.deepcopy((a, b))
    r = e.paired_scale_order(a, b)
    assert r['joint_baseline_outcome'] == 'reversed'
    assert r['paired_outcome'] == 'correct'
    assert r['paired_difference'] == pytest.approx(.1)
    opposite = e.paired_scale_order(b, a)
    assert opposite['joint_baseline_outcome'] == 'correct'
    assert opposite['paired_outcome'] == 'reversed'
    assert opposite['paired_difference'] == pytest.approx(-r['paired_difference'])
    assert (a, b) == before


@pytest.mark.parametrize('a,b,outcome', [([.4], [.3], 'correct'),
    ([.1, .7], [.2, .4], 'correct'), ([.3, .7], [.7, .3], 'tie'),
    ([0], [0], 'tie'), ([None], [.5], 'unscorable'), ([], [], 'unscorable')])
def test_small_support_and_missing(a, b, outcome):
    r = e.paired_scale_order(point(a), point(b))
    assert r['joint_baseline_outcome'] == r['paired_outcome'] == outcome
    if outcome == 'unscorable':
        assert r['paired_difference'] is None


def test_width_join_and_permutation_use_identical_support():
    a, b = point([.9, .4, .2]), point([.6, .5, .1])
    r = e.paired_scale_order(a, b)
    a['scales'].reverse()
    b['scales'] = b['scales'][1:] + b['scales'][:1]
    assert e.paired_scale_order(a, b) == r
    b['scales'][0]['scores']['combined'] = None
    r = e.paired_scale_order(a, b)
    assert r['common_band_widths'] == [8, 24]
    assert r['excluded_scales'] == [{'band_width_px': 16, 'reason': 'v1_method_unavailable',
                                     'fields': ['right.combined']}]
    assert r['joint_baseline_difference'] == pytest.approx(r['paired_difference'])


def test_disjoint_widths_cannot_expand_support():
    r = e.paired_scale_order(point([.8], [8]), point([.4], [16]))
    assert r['legacy_outcome'] == 'correct'
    assert r['paired_outcome'] == r['joint_baseline_outcome'] == 'unscorable'
    assert r['common_scale_count'] == 0
    assert len(r['excluded_scales']) == 2


@pytest.mark.parametrize('change', ['basis', 'x', 'duplicate'])
def test_wrong_geometry_or_duplicate_width_rejected(change):
    a, b = point([.8]), point([.4])
    if change == 'basis': b['geometry_basis'] = 'candidate_center'
    if change == 'x': b['source_x_range'] = [0, 21]
    if change == 'duplicate': b['scales'] *= 2
    with pytest.raises(ValueError):
        e.paired_scale_order(a, b)


def test_metadata_and_y_do_not_decide_order():
    a, b = point([.8]), point([.4])
    expected = e.paired_scale_order(a, b)
    a.update(source_y=900, identity='non_interface', judgment='off_interface', candidate_input_index=75)
    b.update(source_y=3, identity='interface', judgment='near_interface', candidate_input_index=2)
    assert e.paired_scale_order(a, b) == expected


def test_pairwise_cycles_are_possible_not_a_total_rank():
    a, b, c = point([1, .5, 0]), point([0, 1, .5]), point([.5, 0, 1])
    assert all(e.paired_scale_order(x, y)['paired_outcome'] == 'correct'
               for x, y in ((b, a), (c, b), (a, c)))


def evaluated_case():
    scored, labels = [], []
    for idx, identity, judgment, vals in [
        (0, 'interface', 'near_interface', [.9, .4, .2]),
        (1, 'interface', 'off_interface', [.6, .5, .1]),
        (2, 'non_interface', 'off_interface', [.6, .5, .1]),
        (3, 'unreviewed', 'unreviewed', [.6, .5, .1])]:
        c = e.score_candidate(candidate(equal=True))
        c['candidate_input_index'] = idx
        c['points'][0].update(point(vals))
        scored.append(c)
        labels.append({'candidate_input_index': idx, 'identity': identity, 'path_reviews': [] if idx == 3 else [
            {'geometry_basis': 'native_path', 'source_x_range': [0, 20], 'source_y': 10, 'judgment': judgment}]})
    evaluation = e.evaluate_case({'case_id': 'synthetic', 'partition': 'regression',
                                 'visibility': 'visible', 'candidates': labels}, scored)
    return evaluation, scored


def test_existing_inventory_identity_and_basis_are_preserved():
    evaluation, scored = evaluated_case()
    before = copy.deepcopy((evaluation, scored))
    result = e.evaluate_paired_scales(evaluation, scored)
    for name in ('interface_location_same_x', 'identity_negative_control_same_x'):
        task = result['tasks']['native_path/' + name]
        assert task['pair_count'] == task['improved'] == 1
        assert task['regressed'] == 0
        assert task['common_scale_count_histogram'] == {3: 1}
        assert result['tasks']['candidate_center/' + name]['pair_count'] == 0
    assert result['point_inventory']['native_path']['unreviewed/unreviewed'] == 1
    assert (evaluation, scored) == before


def test_support_loss_not_counted_as_method_regression():
    evaluation, scored = evaluated_case()
    scored[0]['points'][0]['scales'] = point([.8], [4])['scales']
    r = e.evaluate_paired_scales(evaluation, scored)['tasks']['native_path/interface_location_same_x']
    assert r['lost_legacy_scorable'] == 1
    assert r['improved'] == r['regressed'] == r['common_scorable_pair_count'] == 0


def test_cli_receipt_reference_and_input_preservation(inputs, tmp_path):
    old = e.run([inputs], tmp_path / 'reference')
    ref = tmp_path / 'reference' / 'experiment.json'
    before = {p: p.read_bytes() for p in inputs.parent.iterdir() if p.is_file()}
    before[ref] = ref.read_bytes()
    cwd = tmp_path / '별도 작업'; cwd.mkdir()
    out = tmp_path / '새 결과'
    proc = subprocess.run([sys.executable, str(Path(e.__file__).resolve()), '--labels', str(inputs),
        '--paired-scale', '--reference', str(ref), '--output', str(out)], cwd=cwd,
        stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8')
    assert proc.returncode == 0, proc.stderr
    report = e.o2.read_json(out / 'experiment.json')
    assert report['reference']['inputs_scores_evaluation_equal'] is True
    assert all(report[k] == old[k] for k in ('inputs', 'scores', 'evaluation'))
    receipt = e.o2.read_json(out / 'complete.json')
    assert receipt['schema_version'] == e.PAIRED_SCHEMA
    assert receipt['status'] == 'COMPLETE'
    assert all(e.o2.sha256_file(out / name) == digest for name, digest in receipt['outputs'].items())
    assert all(p.read_bytes() == value for p, value in before.items())
    assert all(r['before_sha256'] == r['after_sha256'] for r in report['input_preservation'])
    assert not report['auto_acceptance'] and not report['production_decisions_emitted']
    assert report['numeric_localization'] == 'NOT_MEASURED'
    with pytest.raises(ValueError, match='already exists'):
        e.run([inputs], out, paired_scale=True, reference=ref)


def test_reference_drift_blocks_publication(inputs, tmp_path):
    e.run([inputs], tmp_path / 'reference')
    ref = tmp_path / 'reference' / 'experiment.json'
    data = e.o2.read_json(ref); data['evaluation'] = []
    ref.write_text(json.dumps(data), encoding='utf-8')
    out = tmp_path / 'out'
    with pytest.raises(ValueError, match='reference evaluation differs'):
        e.run([inputs], out, paired_scale=True, reference=ref)
    assert not out.exists()


@pytest.mark.parametrize('extra', [{}, {'reference': 'absent', 'target_audit': True},
                                  {'reference': 'absent', 'bundle': 'unused'}])
def test_mode_guards_before_reading_inputs(tmp_path, extra):
    with pytest.raises(ValueError):
        e.run([], tmp_path / 'out', paired_scale=True, **extra)
    assert not (tmp_path / 'out').exists()
