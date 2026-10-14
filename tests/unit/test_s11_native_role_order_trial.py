"""Role-order boundaries: source splits, missing public paths and unknowns."""
import copy

import numpy as np
import pytest

from tests.diagnostics import s11_native_role_order_trial as trial


def units():
    rows = [dict(id=sid, review_role=role, partition='train', availability=trial.READY,
                 source_recording=dict(sha256='water' if i < 2 else 'sample4'))
            for i, (sid, role) in enumerate(zip(trial.TRAIN,
                ['EXTERNAL_SURFACE', 'INTERNAL_FOAM_CHANGE', 'EXTERNAL_SURFACE',
                 'INTERNAL_FOAM_CHANGE', 'STRUCTURE_BOUNDARY']))]
    for sid in trial.POSITIVE + trial.RIM + ['fragment-9', 'fragment-10']:
        rows.append(dict(id=sid, native_fragment_id=int(sid.split('-')[1]), partition='transfer',
                         source_recording=dict(sha256='public'), availability=trial.READY if sid != 'fragment-10' else 'UNAVAILABLE',
                         review_role='EXTERNAL_SURFACE' if sid in trial.POSITIVE else 'STRUCTURE_BOUNDARY' if sid in trial.RIM else None))
    return rows


def test_pairs_preserve_source_groups_and_exclude_unreviewed_unavailable_units():
    rows = units(); trial.validate_units(rows)
    assert trial.pairs_by_source(rows, 'train') == {'sample4': [['N3', 'N4'], ['N3', 'N5']], 'water': [['N1', 'N2']]}
    pairs = trial.pairs_by_source(rows, 'transfer')['public']
    assert len(pairs) == 12 and all(a in trial.POSITIVE and b in trial.RIM for a, b in pairs)


@pytest.mark.parametrize('change,match', [('source', 'leakage'), ('fit', 'fit roster'),
    ('role', 'reviewed role'), ('unknown', 'unreviewed unit'), ('unavailable', 'input unavailable'),
    ('duplicate', 'duplicate')])
def test_changed_data_scope_is_rejected(change, match):
    rows = units()
    if change == 'source':
        for u in rows[5:]: u['source_recording']['sha256'] = 'sample4'
    if change == 'fit': rows[0]['partition'] = 'transfer'
    if change == 'role': rows[4]['review_role'] = 'INTERNAL_FOAM_CHANGE'
    if change == 'unknown': rows[-2]['review_role'] = 'STRUCTURE_BOUNDARY'
    if change == 'unavailable': rows[5]['availability'] = 'UNAVAILABLE'
    if change == 'duplicate': rows.append(copy.deepcopy(rows[0]))
    with pytest.raises(ValueError, match=match): trial.validate_units(rows)


def test_unknown_path_cannot_disappear_from_full_public_roster():
    rows = units(); packet = {'fragments': [{'fragment_id': u['native_fragment_id']} for u in rows[5:]]}
    with pytest.raises(ValueError, match='population dropped'):
        trial.validate_public_roster(rows[:-1], packet)


def test_patch_mean_ablation_retains_color_and_patch_order_but_removes_spatial_pattern():
    array = np.arange(2*3*49, dtype=np.float32).reshape(2, 3, 7, 7) / 255
    mean = trial.transform(array, 'mean_rgb')
    assert mean.shape == array.shape
    assert np.allclose(mean[:, :, 0, 0], array.mean(axis=(2, 3)))
    assert np.array_equal(mean[:, :, 0, 0], mean[:, :, -1, -1])
    assert np.array_equal(trial.transform(array, 'native'), array)
    mean[0] = 0
    assert array[0].any()


def test_order_is_invariant_to_common_score_offset_but_ties_and_reversal_fail():
    groups = {'s': [['positive', 'rim']]}
    good = trial.compare({'positive': -100, 'rim': -101}, groups)
    shifted = trial.compare({'positive': 6, 'rim': 5}, groups)
    assert good == shifted and good['absolute_accuracy'] is None and not good['independent_trials']
    assert trial.compare({'positive': 0, 'rim': 0}, groups)['ties'] == 1
    assert trial.compare({'positive': -1, 'rim': 0}, groups)['ordered'] == 0
    with pytest.raises(ValueError, match='nonfinite'): trial.compare({'positive': np.nan, 'rim': 0}, groups)


def test_full_success_without_mean_ablation_advantage_is_not_native_pattern_success():
    passed = {'pairs': 12, 'ordered': 12}; failed = {'pairs': 12, 'ordered': 11}
    arms = {'native': {'train': passed, 'transfer': passed}, 'mean_rgb': {'train': passed, 'transfer': passed}}
    assert trial.disposition(arms) == 'NO_NATIVE_PATTERN_ADVANTAGE'
    arms['mean_rgb']['transfer'] = failed
    assert trial.disposition(arms) == 'LIMITED_EXPOSED_ORDER_INFORMATION'
    arms['native']['train'] = failed
    assert trial.disposition(arms) == 'CLOSED_WITHOUT_PROMOTION'
