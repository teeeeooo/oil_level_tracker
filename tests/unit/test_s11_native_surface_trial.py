"""Contract tests: source leakage, non-target semantics, native inputs and unknowns."""
from __future__ import annotations

import copy

import numpy as np
import pytest

from tests.diagnostics import s11_native_surface_trial as trial


def units():
    roles = ['EXTERNAL_SURFACE', 'INTERNAL_FOAM_CHANGE', 'EXTERNAL_SURFACE',
             'INTERNAL_FOAM_CHANGE', 'STRUCTURE_BOUNDARY']
    return [dict(id=f'N{i+1}', review_role=role, target=trial.TARGETS[role],
                 source_recording=dict(sha256='a' if i < 2 else 'b')) for i, role in enumerate(roles)]


def test_internal_and_structure_are_distinct_review_roles_with_same_limited_target():
    rows = units()
    trial.validate_split(rows, trial.SPLIT)
    assert rows[-1]['review_role'] == 'STRUCTURE_BOUNDARY'
    assert trial.CLASSES[rows[-1]['target']] == 'NON_EXTERNAL_SURFACE'
    assert rows[-1]['review_role'] != rows[-2]['review_role']


@pytest.mark.parametrize('change,match', [('source', 'leakage'), ('split', 'every unit'),
                                         ('target', 'reviewed role'), ('duplicate', 'duplicate')])
def test_bad_partition_or_label_is_rejected(change, match):
    rows, split = units(), copy.deepcopy(trial.SPLIT)
    if change == 'source': rows[-1]['source_recording']['sha256'] = 'a'
    if change == 'split': split['transfer'].pop()
    if change == 'target': rows[-1]['target'] = 0
    if change == 'duplicate': rows.append(copy.deepcopy(rows[-1]))
    with pytest.raises(ValueError, match=match):
        trial.validate_split(rows, split)


def test_rgb_footprint_order_and_pixels_outside_dependency():
    rgb = np.arange(19*23*3, dtype=np.uint8).reshape(19, 23, 3)
    before = trial.patches(rgb, [[10, 9]])
    assert before.shape == (1, 3, 7, 7)
    assert np.array_equal(before[0, :, 0, 0], rgb[6, 7])
    rgb[:6] = 0
    assert np.array_equal(before, trial.patches(rgb, [[10, 9]]))
    rgb[6, 7] ^= 255
    assert not np.array_equal(before, trial.patches(rgb, [[10, 9]]))
    for centers in ([], [[1, 9]], [[10, 9], [10, 9]]):
        with pytest.raises(ValueError): trial.patches(rgb, centers)


def test_all_unknown_cannot_pass_and_structure_false_accept_is_not_internal_success():
    rows = [dict(id=r['id'], partition='train' if i < 2 else 'transfer', review_role=r['review_role'],
                 expected=trial.CLASSES[r['target']], decision=trial.decision([0., 0.]))
            for i, r in enumerate(units())]
    summary = trial.summarize(rows)
    assert summary['transfer'] == dict(units=3, correct=0, unknown=3, target_loss=1, wrong_external_acceptance=0)
    rows[-1]['decision'] = trial.decision([1., 0.])
    assert trial.summarize(rows)['transfer']['wrong_external_acceptance'] == 1
    with pytest.raises(ValueError, match='nonfinite'): trial.decision([np.nan, 0.])


def test_pins_reject_changed_bytes_and_escape(tmp_path):
    source = tmp_path / 'native.json'
    source.write_text('{}', encoding='utf-8')
    pin = trial.pin(tmp_path, source)
    assert trial.verified(tmp_path, pin) == source
    source.write_text('changed', encoding='utf-8')
    with pytest.raises(ValueError, match='hash'): trial.verified(tmp_path, pin)
    pin['path'] = '../native.json'
    with pytest.raises(ValueError, match='escapes'): trial.verified(tmp_path, pin)
