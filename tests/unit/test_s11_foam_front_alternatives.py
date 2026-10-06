import json

import numpy as np
import pytest

from tests.diagnostics.s11_foam_front_alternatives import measure


def scene():
    gray = np.full((40, 15), 40, np.uint8)
    gray[20:] = 200
    labels = np.zeros(gray.shape, np.uint16)
    labels[20:30, 3:12] = 2
    return gray, labels, np.ones(gray.shape, bool), np.zeros(gray.shape, bool)


def column(result):
    return result['components'][0]['columns'][4]


def test_step_plateau_not_arbitrary_single_pixel_front():
    arrays = scene()
    before = [a.copy() for a in arrays]
    result = measure(*arrays, origin=(100, 200))
    for view in column(result)['views']:
        assert view['fully_observed']
        assert view['appearance_state'] == 'single_peak'
        assert view['peaks'][0]['source_y_range'] == [219, 221]
    assert result['components'][0]['foam_front'] is None
    assert result['components'][0]['physical_identity'] == 'UNRESOLVED'
    for a, b in zip(arrays, before):
        np.testing.assert_array_equal(a, b)
    json.dumps(result, allow_nan=False)


def test_ribbon_keeps_two_competing_edges_without_winner():
    gray, labels, effective, glare = scene()
    gray[23:] = 40
    result = measure(gray, labels, effective, glare)
    view = column(result)['views'][1]
    assert view['appearance_state'] == 'multiple_peaks'
    assert [p['source_y_range'] for p in view['peaks']] == [[19, 21], [22, 24]]
    assert result['components'][0]['foam_front'] is None


def test_reflection_and_material_with_identical_pixels_are_indistinguishable():
    material = scene()
    reflection = tuple(a.copy() for a in material)
    assert measure(*material) == measure(*reflection)
    assert measure(*reflection)['components'][0]['physical_identity'] == 'UNRESOLVED'


@pytest.mark.parametrize('mask_name', ['effective', 'glare'])
def test_four_neighbour_mask_censors_instead_of_zero_or_interpolation(mask_name):
    gray, labels, effective, glare = scene()
    if mask_name == 'effective':
        effective[18, 7] = False
    else:
        glare[18, 7] = True
    view = column(measure(gray, labels, effective, glare))['views'][0]
    assert view['appearance_state'] == 'censored'
    assert view['vertical_samples'][1:4] == [None, None, None]
    assert view['peaks'] == []


def test_flat_and_window_clipped_peak_do_not_prove_no_boundary():
    gray, labels, effective, glare = scene()
    gray[:] = 40
    result = measure(gray, labels, effective, glare)
    assert column(result)['views'][0]['appearance_state'] == 'no_bracketed_peak'
    assert result['components'][0]['foam_front'] is None
    gray[16:] = 200  # plateau at 15..16: censored by radius-4 inspection window
    views = column(measure(gray, labels, effective, glare))['views']
    assert views[0]['peaks'] == []
    assert views[1]['peaks'][0]['source_y_range'] == [15, 17]


def test_crop_edge_and_missing_support_stay_explicit():
    gray, labels, effective, glare = scene()
    labels[:] = 0
    labels[0:3, 7] = 256
    result = measure(gray, labels, effective, glare)
    assert result['components'][0]['component_id'] == 256
    assert result['components'][0]['columns'][0]['views'][0]['appearance_state'] == 'censored'
    labels[:] = 0
    assert measure(gray, labels, effective, glare)['components'] == []


def test_slanted_front_translation_changes_only_source_coordinates():
    gray, labels, effective, glare = scene()
    for x in range(3, 12):
        y = 15 + x//2
        gray[:, x] = 40
        gray[y:, x] = 200
        labels[:, x] = 0
        labels[y:y+5, x] = 2
    base = measure(gray, labels, effective, glare)
    shifted = measure(gray, labels, effective, glare, origin=(13, 27))
    for a, b in zip(base['components'][0]['columns'], shifted['components'][0]['columns']):
        assert b['source_x']-a['source_x'] == 13
        assert b['support_top_source_y']-a['support_top_source_y'] == 27
        assert b['views'][1]['vertical_samples'] == a['views'][1]['vertical_samples']
        assert b['views'][1]['appearance_state'] == a['views'][1]['appearance_state']


@pytest.mark.parametrize('bad', ['gray', 'labels', 'shape', 'outside'])
def test_reject_bad_inputs(bad):
    gray, labels, effective, glare = scene()
    if bad == 'gray': gray = gray.astype(float)
    if bad == 'labels': labels = labels.astype(np.uint8)
    if bad == 'shape': glare = glare[:-1]
    if bad == 'outside': effective[20, 4] = False
    with pytest.raises(ValueError):
        measure(gray, labels, effective, glare)


def saved_capture(tmp_path):
    import cv2
    from tests.diagnostics.s11_foam_front_alternatives_run import sha
    root = tmp_path/'capture'
    trace = root/'trace'
    trace.mkdir(parents=True)
    gray, labels, effective, glare = scene()
    images = {'grayscale': gray, 'original_roi': cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR),
              'foam_component_labels': labels, 'effective_mask': effective.astype('uint8')*255,
              'glare_mask': glare.astype('uint8')*255}
    for name, pixels in images.items():
        assert cv2.imwrite(str(trace/(name+'.png')), pixels)
    diag = {'truncated': False, 'crop_origin': [100, 200],
            'components': [{'diagnostic_id': 2, 'pixel_count': 90, 'local_bbox_xyxy': [3, 20, 12, 30]}]}
    (trace/'debug_trace.jsonl').write_text(json.dumps({'state': {'foam_component_diagnostics': diag},
                                        'images': {k:k+'.png' for k in images}}))
    (root/'capture.json').write_text(json.dumps({'cases': [dict(case_id='synthetic', frame_index=42,
                    glass_id='glass', run_id='run', record_id='record', trace_directory='trace')]}))
    pins = {str(p.relative_to(root)):sha(p) for p in root.rglob('*') if p.is_file()}
    receipt = root/'receipt.json'
    receipt.write_text(json.dumps({'schema_version': 's11-local-foam-component-capture-receipt-v1',
                                  'status': 'CAPTURE_COMPLETE_NOT_EVALUATED', 'output_sha256s': pins}))
    return root, sha(receipt)


def test_saved_capture_entrypoint_receipt_and_no_overwrite(tmp_path):
    from tests.diagnostics.s11_foam_front_alternatives_run import run, sha
    root, pin = saved_capture(tmp_path)
    before = {p:sha(p) for p in root.rglob('*') if p.is_file()}
    out = tmp_path/'output'
    report = run(root, out, pin)
    assert report['cases'][0]['components'][0]['foam_front'] is None
    assert report['preserved_input_count'] == len(before)
    for p, digest in before.items(): assert sha(p) == digest
    receipt = json.loads((out/'receipt.json').read_text())
    for name, digest in receipt['outputs'].items(): assert sha(out/name) == digest
    with pytest.raises(FileExistsError): run(root, out, pin)


@pytest.mark.parametrize('bad', ['receipt', 'pixel'])
def test_saved_capture_rejects_tampering_before_output(tmp_path, bad):
    from tests.diagnostics.s11_foam_front_alternatives_run import run
    root, pin = saved_capture(tmp_path)
    if bad == 'receipt': pin = '0'*64
    else: (root/'trace/grayscale.png').write_bytes(b'changed')
    out = tmp_path/'output'
    with pytest.raises(ValueError): run(root, out, pin)
    assert not out.exists()


def test_byte_equal_slope_is_one_plateau_despite_float_subtraction():
    gray, labels, effective, glare = scene()
    gray[:] = 5
    # Constant 7-code-value slope: exact central numerator 14 across the ramp.
    for y in range(17, 24): gray[y] = 5 + 7*(y-16)
    gray[24:] = gray[23]
    view = column(measure(gray, labels, effective, glare))['views'][1]
    assert len(view['peaks']) == 1
    assert view['peaks'][0]['source_y_range'] == [17, 23]
    assert view['peaks'][0]['vertical_magnitude'] == 14/510


def test_runner_cannot_write_inside_capture(tmp_path):
    from tests.diagnostics.s11_foam_front_alternatives_run import run
    root, pin = saved_capture(tmp_path)
    with pytest.raises(ValueError, match='outside immutable capture'):
        run(root, root/'new', pin)
    assert not (root/'new').exists()
