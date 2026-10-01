"""Information-gain/collision controls for the proposed spatial observable."""
import copy
from dataclasses import asdict

import numpy as np
import pytest

from tests.diagnostics.s11_spatial_context_probe import measure_context
from tests.diagnostics import s11_shadow_experiment as scores
from tests.unit.test_oil_interface_witness import measure
from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind


def point(index=0, x=(0, 200), y=100, basis='candidate_center'):
    return dict(candidate_input_index=index, geometry_basis=basis, source_x_range=list(x), source_y=y)


def probe(gray, *, mask=None, glare=None, points=None, origin=(0, 0)):
    return measure_context(gray, np.ones_like(gray) if mask is None else mask,
                           np.zeros_like(gray) if glare is None else glare,
                           [point()] if points is None else points, origin=origin)


@pytest.mark.parametrize('return_y', [155, 175])
@pytest.mark.parametrize('invert', [False, True])
def test_new_extent_distinguishes_old_complete_witness_collision(return_y, invert):
    step = np.full((200, 200), 180, np.uint8); step[100:] = 80
    stripe = step.copy(); stripe[return_y:] = 180
    if invert: step, stripe = 255-step, 255-stripe
    ca, cb = (asdict(measure(g).candidates[0]) for g in (step, stripe))
    assert ca == cb and scores.score_candidate(ca) == scores.score_candidate(cb)
    before = (step.copy(), stripe.copy())
    a, b = probe(step), probe(stripe)
    assert a['profiles'][0]['gray_mean'][:return_y] == b['profiles'][0]['gray_mean'][:return_y]
    assert a['profiles'][0]['gray_mean'][return_y:] != b['profiles'][0]['gray_mean'][return_y:]
    assert a['decision'] == b['decision'] == 'NOT_EVALUATED'
    assert np.array_equal(step, before[0]) and np.array_equal(stripe, before[1])


@pytest.mark.parametrize('occlusion', ['mask', 'glare'])
def test_return_hidden_by_occlusion_stays_missing_and_cannot_be_recovered(occlusion):
    step = np.full((200, 200), 180, np.uint8); step[100:] = 80
    stripe = step.copy(); stripe[155:] = 180
    mask = np.ones_like(step); glare = np.zeros_like(step)
    if occlusion == 'mask': mask[155:] = 0
    else: glare[155:] = 255
    a, b = probe(step, mask=mask, glare=glare), probe(stripe, mask=mask, glare=glare)
    assert a == b  # pixels outside visibility cannot be manufactured
    p = a['profiles'][0]
    assert p['gray_mean'][155:] == [None]*45
    assert p['visible_count'][155:] == [0]*45
    assert p['row_state'][155] == ('outside_effective_mask' if occlusion == 'mask' else 'glare_excluded')
    assert p['extent_censored']


def test_same_raster_physical_alias_and_stationary_scene_remain_undecided():
    image = np.full((200, 200), 180, np.uint8); image[100:] = 80
    # Could be an Oil boundary or a broad structural step; physical origin isn't an input.
    assert probe(image) == probe(image.copy())
    assert probe(image)['decision'] == 'NOT_EVALUATED'
    # Real Oil plus a reflection can have the same bounded stripe as an artifact.
    image[175:] = 180
    assert probe(image)['decision'] == 'NOT_EVALUATED'


def test_row_order_is_retained_but_horizontal_permutations_can_still_collide():
    a = np.full((200, 200), 180, np.uint8); a[100:150] = 80
    b = np.full_like(a, 180); b[150:] = 80
    assert np.array_equal(np.sort(a.ravel()), np.sort(b.ravel()))
    assert probe(a)['profiles'] != probe(b)['profiles']
    left = np.full_like(a, 180); left[:, :100] = 80
    right = np.flip(left, axis=1).copy()
    assert probe(left) == probe(right)  # row means don't retain full 2-D topology


def test_coordinate_provenance_shared_strip_and_coverage_preserve_geometry():
    image = np.zeros((20, 30), np.uint8)
    mask = np.ones_like(image); mask[0] = 0; mask[2, 1:] = 0
    points = [point(2, (40, 70), 60, 'native_path'), point(3, (40, 70), 65)]
    before = copy.deepcopy(points)
    result = probe(image, mask=mask, points=points, origin=(40, 50))
    assert len(result['profiles']) == 1 and result['point_count'] == 2
    assert [p['source_y'] for p in result['points']] == [60, 65]
    p = result['profiles'][0]
    assert p['source_y_start'] == 50 and p['source_y_stop_exclusive'] == 70
    assert p['gray_mean'][:3] == [None, 0.0, 0.0]
    assert p['visible_count'][:3] == [0, 30, 1]  # observed doesn't mean sufficient support
    assert points == before


@pytest.mark.parametrize('fault', ['x', 'y', 'float_x', 'bool_index', 'duplicate', 'shape', 'dtype', 'point_bound', 'origin'])
def test_invalid_inputs_do_not_silently_clip_geometry(fault):
    image = np.zeros((200, 200), np.uint8); mask = np.ones_like(image); points = [point()]; origin = (0, 0)
    if fault == 'x': points[0]['source_x_range'] = [-1, 200]
    if fault == 'y': points[0]['source_y'] = 200
    if fault == 'float_x': points[0]['source_x_range'] = [0.0, 200.0]
    if fault == 'bool_index': points[0]['candidate_input_index'] = False
    if fault == 'duplicate': points *= 2
    if fault == 'shape': mask = mask[:-1]
    if fault == 'dtype': image = image.astype(float)
    if fault == 'point_bound': points = [point(i) for i in range(513)]
    if fault == 'origin': origin = (True, 0)
    with pytest.raises(ValueError): probe(image, mask=mask, points=points, origin=origin)


def test_empty_inventory_does_not_invent_candidate_or_success():
    result = probe(np.zeros((10, 10), np.uint8), points=[])
    assert result['profiles'] == result['points'] == []
    assert result['point_count'] == 0 and result['decision'] == 'NOT_EVALUATED'


@pytest.mark.parametrize('invert', [False, True])
@pytest.mark.parametrize('second_y,packet_changes', [(110, False), (170, True)])
def test_remote_context_novelty_depends_on_all_candidate_witnesses(invert, second_y, packet_changes):
    """A return outside one candidate is not necessarily absent from the packet.

    These are fixed-raster extractor controls, not physical class labels or a
    rerun of preprocessing/proposals. Auxiliary channels are held fixed.
    """
    step = np.full((200, 200), 180, np.uint8)
    step[100:] = 80
    returning = step.copy()
    returning[175:] = 180
    if invert:
        step, returning = 255-step, 255-returning
    candidates = [BoundaryCandidate('test', BoundaryKind.OIL_AIR, y)
                  for y in (100, second_y)]
    a, b = [measure(g, candidates=candidates) for g in (step, returning)]
    assert a.candidates[0] == b.candidates[0]
    assert (a != b) == packet_changes  # full serialized witness, including observability
    assert (a.candidates[1] != b.candidates[1]) == packet_changes
    if not packet_changes:
        assert [scores.score_candidate(asdict(c)) for c in a.candidates] == [
            scores.score_candidate(asdict(c)) for c in b.candidates]
    points = [point(i, y=y) for i, y in enumerate((100, second_y))]
    left, right = [probe(g, points=points) for g in (step, returning)]
    assert left['points'] == right['points']
    assert len(left['profiles']) == len(right['profiles']) == 1
    assert left['profiles'][0]['gray_mean'][175:] != right['profiles'][0]['gray_mean'][175:]
    assert left['decision'] == right['decision'] == 'NOT_EVALUATED'


@pytest.mark.parametrize('invert', [False, True])
def test_unsampled_center_row_can_already_be_visible_to_o1_peak_measurement(invert):
    flat = np.full((200, 200), 120, np.uint8)
    spike = flat.copy()
    spike[100] = 220
    if invert:
        flat, spike = 255-flat, 255-spike
    a, b = [measure(g).candidates[0] for g in (flat, spike)]
    for sa, sb in zip(a.sectors, b.sectors, strict=True):
        for ca, cb in zip(sa.centers, sb.centers, strict=True):
            for aa, bb in zip(ca.scales, cb.scales, strict=True):
                for ba, band in zip(aa.bands, bb.bands, strict=True):
                    assert not (band.local_y_range[0] <= 100 < band.local_y_range[1])
                    lo, hi = band.local_y_range
                    assert np.array_equal(flat[lo:hi], spike[lo:hi])
                    # Prefix-sum subtraction can differ at floating roundoff.
                    assert ba.gray_mean == pytest.approx(band.gray_mean, rel=0, abs=1e-12)
                assert aa.peak_count_before_truncation == 0
                assert bb.peak_count_before_truncation > 0
                assert aa.peaks != bb.peaks
    assert a != b  # absence from band means is not absence from all O1 fields
