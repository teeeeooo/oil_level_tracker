"""D2 synthetic falsification: region connectivity is not physical identity.

The oracle receives exact nominal regions supplied by fixture construction.
There is no real-image segmentation, trained model, candidate selector or runtime
entry point here. This optimistic input isolates connectivity's information limit
before paying for a new private-image experiment. Semantic fixture assignments
never enter the oracle. The existing region model owns local adjacency summaries.
"""
from __future__ import annotations

import itertools

import cv2
import numpy as np
import pytest

from tests.diagnostics import s11_region_competition as region


def topology_oracle(labels, visible, points=()):
    """Test-only observed 4-connectivity, with no completion behind missing pixels."""
    assert labels.ndim == 2 and labels.shape == visible.shape
    assert visible.dtype == bool and 0 < labels.size <= 96 * 64
    h, w = labels.shape
    unknown_neighbour = np.zeros_like(visible)
    unknown_neighbour[1:] |= ~visible[:-1]
    unknown_neighbour[:-1] |= ~visible[1:]
    unknown_neighbour[:, 1:] |= ~visible[:, :-1]
    unknown_neighbour[:, :-1] |= ~visible[:, 1:]
    pieces = []
    for nominal in np.unique(labels[visible]):
        count, components = cv2.connectedComponents(
            ((labels == nominal) & visible).astype(np.uint8), connectivity=4)
        for cid in range(1, count):
            mask = components == cid
            pieces.append((int(np.flatnonzero(mask)[0]), mask))
    # Canonical IDs depend on geometry, not arbitrary nominal class numbering.
    pieces.sort(key=lambda item: item[0])
    observed = np.full(labels.shape, -1, dtype=np.int32)
    details = []
    for cid, (_, mask) in enumerate(pieces):
        yy, xx = np.nonzero(mask)
        observed[mask] = cid
        borders = [name for name, hit in (
            ('top', np.any(yy == 0)), ('bottom', np.any(yy == h - 1)),
            ('left', np.any(xx == 0)), ('right', np.any(xx == w - 1))) if hit]
        touches_unknown = bool(np.any(mask & unknown_neighbour))
        details.append({
            'id': cid, 'pixels': int(mask.sum()),
            'bbox_xyxy': [int(xx.min()), int(yy.min()), int(xx.max()) + 1, int(yy.max()) + 1],
            'viewport_contacts': borders, 'touches_unknown': touches_unknown,
            'enclosed_in_observed_domain': not borders and not touches_unknown,
        })
    samples = []
    for x, y in points:
        assert 0 <= x < w and 0 < y < h
        above, below = int(observed[y - 1, x]), int(observed[y, x])
        available = above >= 0 and below >= 0
        samples.append({
            'x': x, 'cut_y': y,
            'above_component': above if above >= 0 else None,
            'below_component': below if below >= 0 else None,
            'relation': ('unavailable' if not available else
                         'same_observed_region' if above == below else 'different_observed_regions'),
        })
    return {'observed_component_count': len(details), 'components': details,
            'samples': samples, 'identity_decision': 'NOT_EVALUATED'}


def partition_with_pocket():
    labels = np.zeros((64, 96), dtype=np.uint8)
    labels[32:] = 1
    labels[38:46, 4:20] = 0
    return labels


def test_full_partition_and_enclosed_pocket_have_distinct_support_relations():
    labels = partition_with_pocket()
    visible = np.ones_like(labels, dtype=bool)
    original = labels.copy(), visible.copy()
    result = topology_oracle(labels, visible, [(12, 32), (12, 46)])
    main, pocket = result['samples']
    assert main['relation'] == pocket['relation'] == 'different_observed_regions'
    assert main['below_component'] == pocket['below_component']
    assert main['above_component'] != pocket['above_component']
    assert not result['components'][main['above_component']]['enclosed_in_observed_domain']
    assert result['components'][pocket['above_component']]['enclosed_in_observed_domain']
    assert result['identity_decision'] == 'NOT_EVALUATED'
    assert np.array_equal(labels, original[0]) and np.array_equal(visible, original[1])


def test_mixed_path_keeps_local_pocket_and_main_partition_separate():
    labels = partition_with_pocket()
    # A constructed partial target, not a reconstruction of private idx13.
    points = [(12, 46), (30, 32), (48, 32), (66, 32), (84, 32)]
    result = topology_oracle(labels, np.ones_like(labels, dtype=bool), points)
    pairs = [(p['above_component'], p['below_component']) for p in result['samples']]
    assert pairs[0] != pairs[1] and pairs[1:] == [pairs[1]] * 4
    assert len(result['samples']) == 5
    assert not {'candidate_score', 'selected_candidate', 'target_role'} & result.keys()


def test_full_width_structural_step_collides_with_fluid_partition():
    # These two physical explanations can supply identical single-frame inputs.
    # Fixture semantics are the required opposing answers, never oracle features.
    fluid = np.zeros((64, 96), dtype=np.uint8)
    fluid[32:] = 1
    structure = fluid.copy()
    points = [(x, 32) for x in (12, 30, 48, 66, 84)]
    a = topology_oracle(fluid, np.ones_like(fluid, dtype=bool), points)
    b = topology_oracle(structure, np.ones_like(structure, dtype=bool), points)
    assert a == b
    assert all(set(c['viewport_contacts']) >= {'left', 'right'} for c in a['components'])
    # No mapping of this complete oracle result can yield both required answers.
    required_answers = {'fluid': 'target', 'structure': 'other_non_target'}
    assert len(set(required_answers.values())) == 2
    assert a['identity_decision'] == 'NOT_EVALUATED'


def test_viewport_hides_pocket_return_and_produces_partition_collision():
    pocket = partition_with_pocket()[42:50, 8:16]
    partition = np.zeros_like(pocket)
    partition[4:] = 1
    assert np.array_equal(pocket, partition)
    visible = np.ones_like(pocket, dtype=bool)
    assert topology_oracle(pocket, visible, [(4, 4)]) == topology_oracle(partition, visible, [(4, 4)])
    assert not any(c['enclosed_in_observed_domain']
                   for c in topology_oracle(pocket, visible)['components'])


def test_mask_hidden_return_cannot_be_completed_or_read():
    pocket = partition_with_pocket()
    partition = np.zeros_like(pocket)
    partition[46:] = 1
    visible = np.zeros_like(pocket, dtype=bool)
    visible[42:50, 8:16] = True
    assert np.array_equal(pocket[visible], partition[visible])
    a = topology_oracle(pocket, visible, [(12, 46)])
    assert a == topology_oracle(partition, visible, [(12, 46)])
    assert all(c['touches_unknown'] for c in a['components'])
    assert not any(c['enclosed_in_observed_domain'] for c in a['components'])
    pocket[~visible] = 231
    assert topology_oracle(pocket, visible, [(12, 46)]) == a


@pytest.mark.parametrize('occlusion', ['vertical_gap', 'point_missing'])
def test_missing_support_is_not_a_physical_split_or_negative(occlusion):
    labels = np.zeros((8, 8), dtype=np.uint8)
    visible = np.ones_like(labels, dtype=bool)
    if occlusion == 'vertical_gap':
        visible[:, 4] = False
    else:
        visible[3:5, 4] = False
    result = topology_oracle(labels, visible, [(4, 4)])
    assert result['samples'][0]['relation'] == 'unavailable'
    assert all(c['touches_unknown'] for c in result['components'])
    assert result['identity_decision'] == 'NOT_EVALUATED'


def test_component_ids_ignore_nominal_class_names_and_polarity():
    labels = partition_with_pocket()
    mask = np.ones_like(labels, dtype=bool)
    points = [(12, 32), (12, 46)]
    expected = topology_oracle(labels, mask, points)
    assert topology_oracle(1 - labels, mask, points) == expected
    assert topology_oracle(np.where(labels == 0, 99, 7), mask, points) == expected


def test_corner_contact_does_not_create_unobserved_four_connected_path():
    labels = np.eye(4, dtype=np.uint8)
    result = topology_oracle(labels, np.ones_like(labels, dtype=bool))
    assert result['observed_component_count'] == 6  # 4 diagonal singletons + 2 sides


def find_local_summary_collision():
    """Exhaustive tiny synthetic construction, never a private-data parameter fit."""
    rows = [np.array([int(x in pair) for x in range(4)], dtype=np.uint8)
            for pair in itertools.combinations(range(4), 2)]
    seen = {}
    for choice in itertools.product(rows, repeat=4):
        pixels = np.stack(choice)
        if not np.all(pixels.sum(axis=0) == 2):
            continue
        h = int(np.count_nonzero(pixels[:, 1:] != pixels[:, :-1]))
        v = int(np.count_nonzero(pixels[1:] != pixels[:-1]))
        key = h, v
        count = topology_oracle(pixels, np.ones_like(pixels, dtype=bool))['observed_component_count']
        if key in seen and count != seen[key][1]:
            return seen[key][0], pixels
        seen.setdefault(key, (pixels, count))
    raise AssertionError('Constructed local-summary collision not found')


def test_global_connectivity_can_add_information_without_identity():
    a, b = find_local_summary_collision()
    mask = np.ones_like(a, dtype=bool)
    side = np.zeros_like(a, dtype=bool)
    assert np.array_equal(a.sum(axis=0), b.sum(axis=0))
    assert np.array_equal(a.sum(axis=1), b.sum(axis=1))
    # Actual existing owner: same immediate-neighbour horizontal/vertical energy.
    assert region._adjacency(a[..., None].astype(float), mask, side) == region._adjacency(
        b[..., None].astype(float), mask, side)
    assert topology_oracle(a, mask)['observed_component_count'] != topology_oracle(
        b, mask)['observed_component_count']
