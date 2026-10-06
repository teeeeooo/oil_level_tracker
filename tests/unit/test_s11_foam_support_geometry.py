"""Two-sided geometry controls, not synthetic physical Foam truth."""
import json

import cv2
import numpy as np
import pytest

from tests.diagnostics.s11_foam_support_geometry import measure


def scene():
    labels = np.zeros((100, 100), np.uint16)
    # U-shaped reference has high sides and a low base: its box overlaps target.
    labels[20:81, 10:15] = 1
    labels[20:81, 85:90] = 1
    labels[75:81, 10:90] = 1
    labels[25:41, 30:70] = 2
    return labels, np.ones(labels.shape, bool)


def test_box_overlap_does_not_imply_column_proximity():
    labels, visible = scene()
    before = labels.copy()
    result = measure(labels, visible, 2, 1)
    assert result['bbox_below_gap_px'] == -21
    assert result['bbox_x_overlap_px'] == 40
    assert result['shared_columns'] == result['fully_visible_below_columns'] == 40
    assert result['visible_below_gap_min'] == result['visible_below_gap_max'] == 34
    assert result['columns_with_reference_in_target_y_extent'] == 0
    assert result['substrate_decision'] == result['foam_front'] == 'NOT_ASSIGNED'
    np.testing.assert_array_equal(labels, before)
    json.dumps(result, allow_nan=False)


def test_same_boxes_can_contain_close_reference_support():
    labels, visible = scene()
    far = measure(labels, visible, 2, 1)
    # A connected arm preserves reference bbox but comes directly below target.
    labels[44:47, 10:70] = 1
    close = measure(labels, visible, 2, 1)
    assert far['reference_bbox'] == close['reference_bbox']
    assert far['bbox_below_gap_px'] == close['bbox_below_gap_px']
    assert close['visible_below_gap_min'] == close['visible_below_gap_max'] == 3
    assert close['physical_identity'] == 'UNRESOLVED'


@pytest.mark.parametrize('scale', [1, 2, 3])
def test_translation_and_scale_preserve_gap_meaning(scale):
    labels, visible = scene()
    labels = np.repeat(np.repeat(labels, scale, 0), scale, 1)
    visible = np.ones(labels.shape, bool)
    base = measure(labels, visible, 2, 1)
    shifted = measure(labels, visible, 2, 1, origin=(117, 263))
    assert shifted['visible_below_gap_min'] == 34 * scale
    assert shifted['bbox_below_gap_px'] == -21 * scale
    assert shifted['target_bbox'] == [base['target_bbox'][i]+[117,263][i%2] for i in range(4)]
    assert shifted['columns'][0]['target_top_source_y'] == 25 * scale + 263


def test_masked_corridor_is_not_observed_gap_or_zero():
    labels, visible = scene()
    visible[55, 30:70] = False
    result = measure(labels, visible, 2, 1)
    assert result['below_columns'] == 40
    assert result['fully_visible_below_columns'] == 0
    assert result['visible_below_gap_min'] is None
    assert all(r['below_gap_px'] == 34 and r['below_corridor_fully_visible'] is False for r in result['columns'])


def test_lateral_support_and_absent_id_do_not_become_zero_gap():
    labels, visible = scene()
    labels[labels == 1] = 0
    labels[20:81, 10:15] = 1
    result = measure(labels, visible, 2, 1)
    assert result['shared_columns'] == result['below_columns'] == 0
    assert result['visible_below_gap_min'] is None
    absent = measure(labels, visible, 2, 3)
    assert absent['status'] == 'missing_retained_support'
    assert absent['bbox_below_gap_px'] is None
    assert absent['reference_bbox'] is None


def test_interleaved_support_and_zero_gap_are_distinct():
    labels = np.zeros((12, 4), np.uint16)
    labels[2:5] = 2
    labels[6:9] = 2
    labels[5] = 1
    labels[9] = 1
    result = measure(labels, np.ones(labels.shape, bool), 2, 1)
    assert result['columns_with_reference_in_target_y_extent'] == 4
    assert result['visible_below_gap_min'] == 0
    assert all(r['reference_pixels_in_target_y_extent'] == 1 for r in result['columns'])


def test_support_top_on_crop_edge_is_not_an_observed_boundary():
    labels = np.zeros((12, 4), np.uint16)
    labels[:3] = 2
    labels[9:] = 1
    result = measure(labels, np.ones(labels.shape, bool), 2, 1)
    assert not any(r['target_top_preceding_pixel_visible'] for r in result['columns'])
    assert result['foam_front'] == 'NOT_ASSIGNED'


def test_saved_uint16_png_entry_and_source_coordinates(tmp_path):
    labels, visible = scene()
    labels[labels == 2] = 256
    path = tmp_path/'ids.png'
    assert cv2.imwrite(str(path), labels)
    read = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    result = measure(read, visible, 256, 1, origin=(543, 798))
    assert result['target_bbox'] == [573, 823, 613, 839]
    assert result['visible_below_gap_min'] == 34


@pytest.mark.parametrize('kind', ['dtype', 'visible_shape', 'visible_type', 'same_id', 'zero_id', 'support_outside', 'empty'])
def test_invalid_inputs_fail_explicitly(kind):
    labels, visible = scene()
    a, b = 2, 1
    if kind == 'dtype': labels = labels.astype(np.uint8)
    elif kind == 'visible_shape': visible = visible[:-1]
    elif kind == 'visible_type': visible = visible.astype(np.uint8)
    elif kind == 'same_id': a = b
    elif kind == 'zero_id': a = 0
    elif kind == 'support_outside': visible[30, 40] = False
    elif kind == 'empty': labels, visible = labels[:0], visible[:0]
    with pytest.raises(ValueError):
        measure(labels, visible, a, b)
