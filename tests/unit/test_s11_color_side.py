"""Color-side information controls; neither color nor gray is physical truth."""
import copy
import csv
import io
import json
import os
from pathlib import Path
import subprocess
import sys

import cv2
import numpy as np
import pytest

from tests.diagnostics import s11_joint_context_run as run
from tests.diagnostics import s11_spatial_context_probe as probe
from tests.diagnostics import s11_interface_shadow_evaluation as o2
from tests.unit.test_s11_joint_context import stored, reseal  # actual producer fixture


def sample(above=(0, 0, 100), below=(0, 51, 0)):
    crop = np.empty((8, 2, 3), np.uint8)
    crop[:4] = above
    crop[4:] = below
    # Two rows per band; the middle gap is deliberately excluded.
    bands = [{'name': name, 'local_y_range': [a, b], 'clipped_local_y_range': [a, b],
              'available': True, 'reason': 'available', 'valid_pixel_count': 4}
             for name, a, b in [('near_above', 2, 4), ('near_below', 4, 6),
                                ('far_above', 0, 2), ('far_below', 6, 8)]]
    point = {'candidate_input_index': 7, 'geometry_basis': 'native_path',
             'source_x_range': [40, 42], 'source_y': 64,
             'band_binding': 'exact_role', 'band_center_role': 'native_path',
             'scales': [{'band_width_px': 2, 'bands': bands}]}
    return crop, np.ones((8, 2), np.uint8), np.zeros((8, 2), np.uint8), [point]


def measure(crop, mask, glare, points):
    return probe.measure_color_side(crop, cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY),
                                    mask, glare, points, origin=(40, 60))


def test_equal_gray_color_step_channel_order_polarity_and_no_identity():
    args = sample()
    before = copy.deepcopy(args)
    result = measure(*args)
    assert np.unique(cv2.cvtColor(args[0], cv2.COLOR_BGR2GRAY)).tolist() == [30]
    for pair in result['points'][0]['scales'][0]['pairs'].values():
        assert pair['mean_column_delta_bgr_gray'] == [0, 51, -100, 0]
        assert pair['mean_column_delta_opponents'] == [-51, -151]
        assert pair['column_delta_bgr_gray'] == [[0, 51, -100, 0]] * 2
    reverse = measure(*sample((0, 51, 0), (0, 0, 100)))
    assert reverse['points'][0]['scales'][0]['pairs']['near']['mean_column_delta_bgr_gray'] == [0, -51, 100, 0]
    assert result['decision'] == 'NOT_EVALUATED' and result['spec']['threshold'] is None
    assert result == measure(*args)  # same pixels admit the same result regardless of physical cause
    for a, b in zip(args[:3], before[:3], strict=True): np.testing.assert_array_equal(a, b)
    assert args[3] == before[3]
    json.dumps(result, allow_nan=False)


@pytest.mark.parametrize('reverse', [False, True])
def test_full_color_side_output_cannot_reconstruct_two_dimensional_adjacency(reverse):
    """Same complete output, different RGB adjacency; neither image is Oil truth.

    This extends the gray lateral collision to equal-gray chromatic rasters:
    even ordered column deltas and all band support/means cannot recover the
    within-band arrangement needed by a candidate-level region hypothesis.
    """
    crop, mask, glare, points = sample()
    colors = np.array([[0, 0, 100], [0, 51, 0]], dtype=np.uint8)
    if reverse:
        colors = colors[::-1]
    crop[:] = colors[np.arange(8) % 2, None, :]
    rearranged = crop.copy()
    rearranged[:, 1] = colors[(np.arange(8) + 1) % 2]

    # Each two-row band has the same color multiset in each ordered X column.
    for band in points[0]['scales'][0]['bands']:
        lo, hi = band['clipped_local_y_range']
        np.testing.assert_array_equal(crop[lo:hi].sum(axis=0),
                                      rearranged[lo:hi].sum(axis=0))
    # Horizontal chromatic runs exist only in the first raster. No classifier
    # threshold or connected-region/Oil label is manufactured by this oracle.
    assert np.all(crop[:, 0] == crop[:, 1])
    assert np.all(np.any(rearranged[:, 0] != rearranged[:, 1], axis=1))
    np.testing.assert_array_equal(cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY),
                                  cv2.cvtColor(rearranged, cv2.COLOR_BGR2GRAY))
    assert np.unique(cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)).tolist() == [30]
    first = measure(crop, mask, glare, points)
    second = measure(rearranged, mask, glare, points)
    assert first == second  # includes every reported band, column, mean and status
    assert first['decision'] == 'NOT_EVALUATED'


@pytest.mark.parametrize('below', [30, 100])
def test_achromatic_step_and_observed_zero_are_not_missing(below):
    result = measure(*sample((30,)*3, (below,)*3))
    pair = result['points'][0]['scales'][0]['pairs']['near']
    assert pair['status'] == 'observed'
    assert pair['mean_column_delta_bgr_gray'] == [below-30]*4
    assert pair['mean_column_delta_opponents'] == [0, 0]


@pytest.mark.parametrize('kind', ['mask', 'glare'])
def test_hidden_color_never_leaks_and_null_is_not_zero(kind):
    crop, mask, glare, points = sample()
    if kind == 'mask': mask[:, 1] = 0
    else: glare[:, 1] = 255
    for band in points[0]['scales'][0]['bands']: band['valid_pixel_count'] = 2
    first = measure(crop, mask, glare, points)
    crop[:, 1] = [255, 200, 17]
    assert measure(crop, mask, glare, points) == first
    pair = first['points'][0]['scales'][0]['pairs']['near']
    assert pair['observed_paired_columns'] == 1
    assert pair['column_delta_bgr_gray'] == [[0, 51, -100, 0], None]
    mask[:] = 0
    for band in points[0]['scales'][0]['bands']: band['valid_pixel_count'] = 0
    empty = measure(crop, mask, glare, points)['points'][0]['scales'][0]
    assert empty['bands'][0]['observed_mean_bgr_gray'] is None
    assert empty['pairs']['near']['status'] == 'no_paired_columns'
    assert empty['pairs']['near']['mean_column_delta_bgr_gray'] is None


def test_nonoverlapping_column_support_cannot_create_a_side_pair():
    crop, mask, glare, points = sample()
    mask[:4, 1] = 0; mask[4:, 0] = 0
    for band in points[0]['scales'][0]['bands']: band['valid_pixel_count'] = 2
    r = measure(crop, mask, glare, points)['points'][0]['scales'][0]
    assert all(b['visible_pixel_count'] == 2 for b in r['bands'])
    assert all(p['status'] == 'no_paired_columns' for p in r['pairs'].values())


def test_column_weighting_does_not_become_pixel_weighted_or_wrap_uint8():
    crop, mask, glare, points = sample((100,)*3, (0,)*3)
    crop[4:, 1] = 200; mask[4, 1] = 0
    points[0]['scales'][0]['bands'][1]['valid_pixel_count'] = 3
    r = measure(crop, mask, glare, points)['points'][0]['scales'][0]
    assert r['pairs']['near']['column_delta_bgr_gray'] == [[-100]*4, [100]*4]
    assert r['pairs']['near']['mean_column_delta_bgr_gray'] == [0]*4
    assert r['bands'][1]['observed_mean_bgr_gray'] == pytest.approx([200/3]*4)


def test_unavailable_clipped_band_keeps_observation_but_not_eligible_delta():
    crop, mask, glare, points = sample()
    b = points[0]['scales'][0]['bands'][2]
    b.update(local_y_range=[-2, 2], available=False, reason='outside_crop')
    r = measure(crop, mask, glare, points)['points'][0]['scales'][0]
    assert r['bands'][2]['clipped_source_y_range'] == [60, 62]
    assert r['bands'][2]['visible_pixel_count'] == 4
    assert r['pairs']['far']['status'] == 'o1_unavailable'
    assert r['pairs']['far']['column_delta_bgr_gray'] == [None, None]
    assert r['pairs']['near']['status'] == 'observed'


@pytest.mark.parametrize('fault', ['gray', 'count', 'range', 'duplicate', 'channels', 'resources'])
def test_color_guards(fault, monkeypatch):
    crop, mask, glare, points = sample()
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    if fault == 'gray': gray[0, 0] += 1
    if fault == 'count': points[0]['scales'][0]['bands'][0]['valid_pixel_count'] = 3
    if fault == 'range': points[0]['scales'][0]['bands'][0]['clipped_local_y_range'] = [-1, 4]
    if fault == 'duplicate': points *= 2
    if fault == 'channels': crop = crop[:, :, :2]
    if fault == 'resources': monkeypatch.setitem(probe.COLOR_SIDE_SPEC, 'max_sample_pixels', 1)
    with pytest.raises(ValueError):
        probe.measure_color_side(crop, gray, mask, glare, points, origin=(40, 60))


def test_color_cli_unicode_nonrepo_cwd_hashes_support_and_roles(stored, tmp_path):
    root, digest = stored
    before = {p: p.read_bytes() for p in root.iterdir()}
    cwd = tmp_path/'외부 작업'; cwd.mkdir(); out = tmp_path/'색상 결과'
    result = subprocess.run([sys.executable, str(Path(run.__file__).resolve()), '--color-side',
        '--source', str(root), '--expected-source-artifact', digest, '--output', str(out)],
        cwd=cwd, stdin=subprocess.DEVNULL, env={**os.environ, 'PYTHONUTF8': '1'},
        capture_output=True, text=True, encoding='utf-8', timeout=60)
    assert result.returncode == 0, result.stderr
    receipt = o2.read_json(out/'complete.json'); report = o2.read_json(out/'experiment.json')
    assert receipt['schema_version'] == report['schema_version'] == run.COLOR_SCHEMA
    assert receipt['artifact_sha256'] == report['artifact']['sha256']
    assert set(receipt['outputs']) == {'experiment.json', 'summary.md', 'color-side.csv'}
    assert len(list(out.iterdir())) == 4
    assert all(o2.sha256_file(out/name) == h for name, h in receipt['outputs'].items())
    assert all(p.read_bytes() == raw for p, raw in before.items())
    assert len(report['input_preservation']) == len(before)
    assert all(p['before_sha256'] == p['after_sha256'] for p in report['input_preservation'])
    points = report['cases'][0]['color_side']['points']
    assert len(points) == 6
    assert [p['source_y'] for p in points if p['geometry_basis'] == 'native_path'] == [152, 160, 168]
    alias = [p for p in points if p['band_binding'] == 'coincident_recorded_native_center']
    assert len(alias) == 1 and alias[0]['source_y'] == 160
    rows = list(csv.DictReader(io.StringIO((out/'color-side.csv').read_text(encoding='utf-8'))))
    assert len(rows) == 36
    assert all(float(r['delta_B_minus_G']) == float(r['delta_R_minus_G']) == 0 for r in rows if r['status'] == 'observed')
    assert report['decision'] == 'NOT_EVALUATED' and report['field_disposition'] == 'FIELD FAIL'
    assert report['auto_acceptance'] is report['production_decisions_emitted'] is False
    assert report['numeric_localization'] == 'NOT_MEASURED'
    with pytest.raises(ValueError, match='already exists'):
        run.run(root, out, expected_source_artifact=digest, color_side=True)


@pytest.mark.parametrize('phase', ['measure', 'publish'])
def test_color_mutation_never_publishes_complete(stored, tmp_path, monkeypatch, phase):
    root, digest = stored; out = tmp_path/'failure'
    owner, name = (probe, 'measure_color_side') if phase == 'measure' else (run, '_write_color_outputs')
    original = getattr(owner, name)
    def mutate(*args, **kwargs):
        result = original(*args, **kwargs)
        (root/'crop.png').write_bytes(b'changed')
        return result
    monkeypatch.setattr(owner, name, mutate)
    with pytest.raises(ValueError, match='changed'):
        run.run(root, out, expected_source_artifact=digest, color_side=True)
    assert not (out/'complete.json').exists()


def test_color_gray_mismatch_rejected_even_with_valid_receipt(stored, tmp_path):
    root, digest = stored
    crop = np.zeros((200, 200, 3), np.uint8)
    (root/'crop.png').write_bytes(cv2.imencode('.png', crop)[1].tobytes())
    report = o2.read_json(root/'experiment.json')
    report['cases'][0]['rasters']['crop'] = {'file': 'crop.png', **run.source_run.raster_identity(crop)}
    (root/'experiment.json').write_text(json.dumps(report), encoding='utf-8'); reseal(root)
    out = tmp_path/'failure'
    with pytest.raises(ValueError, match='BGR-to-gray mismatch'):
        run.run(root, out, expected_source_artifact=digest, color_side=True)
    assert not (out/'complete.json').exists()


def test_saved_bgr_is_measured_without_new_joint_map(stored, tmp_path, monkeypatch):
    root, digest = stored
    crop = cv2.imdecode(np.frombuffer((root/'crop.png').read_bytes(), np.uint8), cv2.IMREAD_UNCHANGED)
    crop[:100] = [173, 180, 183]
    crop[100:] = [87, 80, 77]
    (root/'crop.png').write_bytes(cv2.imencode('.png', crop)[1].tobytes())
    source = o2.read_json(root/'experiment.json')
    source['cases'][0]['rasters']['crop'] = {'file': 'crop.png', **run.source_run.raster_identity(crop)}
    (root/'experiment.json').write_text(json.dumps(source), encoding='utf-8'); reseal(root)
    def forbidden(*args, **kwargs):
        pytest.fail('color-side mode must not build a new joint gradient map')
    monkeypatch.setattr(probe, 'measure_joint_context', forbidden)
    result = run.run(root, tmp_path/'colors', expected_source_artifact=digest, color_side=True)
    p = next(p for p in result['cases'][0]['color_side']['points']
             if p['geometry_basis'] == 'native_path' and p['source_y'] == 160)
    for scale in p['scales']:
        assert scale['pairs']['near']['mean_column_delta_bgr_gray'] == [-86, -100, -106, -100]
        assert scale['pairs']['near']['mean_column_delta_opponents'] == [14, -6]
