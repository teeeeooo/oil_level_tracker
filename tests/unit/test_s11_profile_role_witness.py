from copy import deepcopy
import numpy as np
import pytest
from tests.diagnostics.s11_profile_role_witness import ARMS, MODELS, decision_controls, design, observe, preference, score_profile


def scored(kind, polarity=1.0):
    rows = np.r_[np.arange(40, 49), np.arange(52, 61)]
    z = (rows - 50.0) / 10.0
    values = 0.5 + 0.1*z
    if kind == 'jump':
        values += polarity * 0.15*np.sign(z)
    if kind == 'corner':
        values += polarity * 0.15*np.abs(z)
    if kind == 'separate_slopes':
        values += polarity * (0.1*np.sign(z) + 0.25*np.abs(z))
    return score_profile(rows, values, 50.0, 10)


@pytest.mark.parametrize('polarity', [-1.0, 1.0])
@pytest.mark.parametrize('arm', list(ARMS))
def test_step_both_polarities(polarity, arm):
    assert preference(scored('jump', polarity)['errors'], arm) == 'JUMP_PREFERRED'


@pytest.mark.parametrize('arm', list(ARMS))
def test_ramp_is_unknown(arm):
    assert preference(scored('affine')['errors'], arm) == 'UNKNOWN'


@pytest.mark.parametrize('polarity', [-1.0, 1.0])
def test_corner_is_not_physical_negative(polarity):
    errors = scored('corner', polarity)['errors']
    assert preference(errors, 'H1') == 'CORNER_PREFERRED'
    assert preference(errors, 'H2') == 'UNKNOWN'  # nested model ties exactly


@pytest.mark.parametrize('polarity', [-1.0, 1.0])
def test_independent_side_slopes(polarity):
    assert preference(scored('separate_slopes', polarity)['errors'], 'H2') == 'JUMP_PREFERRED'


def test_fold_disagreement_abstains():
    errors = {m: [2.0, 2.0] for m in MODELS}
    errors['jump'] = [1.0, 3.0]
    assert preference(errors, 'H1') == 'UNKNOWN'


def image_fixture():
    gray = np.full((100, 50), 50, dtype=np.uint8)
    gray[50:] = 200
    return gray, np.ones_like(gray, dtype=bool)


def measurement(gray=None, visible=None, **kwargs):
    default_gray, default_mask = image_fixture()
    return observe(default_gray if gray is None else gray,
                   default_mask if visible is None else visible,
                   origin=kwargs.get('origin', (0, 0)), frame=17, index=2,
                   source='fixture', y=kwargs.get('y', 49.5))


def test_exact_candidate_and_input_immutability():
    gray, mask = image_fixture(); before = gray.copy(), mask.copy()
    result = measurement(gray, mask)
    assert result['preferences'] == {a: 'JUMP_PREFERRED' for a in ARMS}
    assert (result['frame'], result['index'], result['y']) == (17, 2, 49.5)
    assert not result['native_path_created']
    assert np.array_equal(gray, before[0]) and np.array_equal(mask, before[1])


def test_source_origin_parity_invariance():
    a = measurement(); b = measurement(origin=(543, 799), y=848.5)
    assert a['preferences'] == b['preferences']
    assert all(np.allclose(a['errors'][m], b['errors'][m][::-1]) for m in MODELS)


@pytest.mark.parametrize('y', [0.0, 5.0, 95.0, 200.0, -20.0])
def test_censored_context_is_unavailable_not_negative(y):
    result = measurement(y=y)
    assert result['status'] == 'UNAVAILABLE_CROP'
    assert all(v == 'UNKNOWN' for v in result['preferences'].values())


def test_disjoint_columns_do_not_make_false_partition():
    gray, mask = image_fixture()
    mask[42, ::2] = False; mask[43, 1::2] = False
    result = measurement(gray, mask)
    assert result['status'] == 'UNAVAILABLE_SUPPORT'
    assert result['sectors'] == []


@pytest.mark.parametrize('invalid', ['dtype', 'shape', 'nan'])
def test_invalid_inputs_fail_clearly(invalid):
    gray, mask = image_fixture()
    with pytest.raises(ValueError):
        if invalid == 'dtype': measurement(gray.astype(float), mask)
        elif invalid == 'shape': measurement(gray, mask[:20])
        else: measurement(y=float('nan'))


def test_runtime_adapter_does_not_read_human_label():
    row = measurement(); other = deepcopy(row); other['review_label'] = 'OPPOSED'
    assert decision_controls([row], 'H1') == decision_controls([other], 'H1')


@pytest.mark.parametrize('origin_y', [0, 799])
def test_independent_pixel_and_normal_equation_verifier(origin_y):
    from tests.diagnostics.s11_profile_role_verify import verify_measurement
    gray, mask = image_fixture()
    row = measurement(gray, mask, origin=(543, origin_y), y=49.5+origin_y)
    checked = verify_measurement(row, gray, mask)
    assert checked['profile_count'] == 5 and checked['pixel_references'] > 0


@pytest.mark.parametrize('corruption', ['pixel', 'coordinate', 'role', 'coefficient', 'support'])
def test_independent_verifier_rejects_corruptions(corruption):
    from tests.diagnostics.s11_profile_role_verify import verify_measurement
    gray, mask = image_fixture(); row = measurement(gray, mask)
    if corruption == 'pixel': gray[42, 5] += 5
    elif corruption == 'coordinate': row['y'] += 1
    elif corruption == 'role': row['preferences']['H1'] = 'CORNER_PREFERRED'
    elif corruption == 'coefficient': row['sectors'][0]['coefficients']['jump'][0][0] += .01
    else: row['sectors'][0]['columns'] = []
    with pytest.raises((ValueError, StopIteration)):
        verify_measurement(row, gray, mask)


@pytest.mark.parametrize('case', ['valid', 'hash', 'missing', 'outside', 'traversal'])
def test_retained_alias_resolution(tmp_path, case):
    import json
    import hashlib
    from tests.diagnostics.s11_profile_role_verify import artifact_file
    repo=tmp_path/'repo'; directory=repo/'evidence'; directory.mkdir(parents=True)
    shared=repo/'shared.csv'; shared.write_text('original bytes')
    sha=hashlib.sha256(shared.read_bytes()).hexdigest()
    target='shared.csv'
    if case=='hash': sha='0'*64
    if case=='missing': target='missing.csv'
    if case=='outside':
        target='../outside.csv'
        (tmp_path/'outside.csv').write_text('original bytes')
    aliases={'aliases':{'arm/tracking.csv':{'path':target,'sha256':sha}}}
    (directory/'artifact-aliases.json').write_text(json.dumps(aliases))
    relative='../shared.csv' if case=='traversal' else 'arm/tracking.csv'
    if case=='valid':
        assert artifact_file(repo,directory,relative)==shared
    else:
        with pytest.raises(ValueError): artifact_file(repo,directory,relative)
