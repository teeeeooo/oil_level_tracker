from dataclasses import asdict
import json
from pathlib import Path

import cv2
import numpy as np
import pytest

from foam_benchmark_fixtures import controlled_scenes
from oil_tracker.adapters.vision import foam_front_detector as foam_module
from oil_tracker.adapters.vision.foam_front_detector import detect_bottom_connected_foam
from oil_tracker.adapters.vision.preprocessing import preprocess
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.adapters.storage.jsonl_debug_trace_writer import JsonlDebugTraceWriter
from oil_tracker.domain.recipe import InspectionRecipe, DetectorSettings
from oil_tracker.domain.session import DebugTraceLevel
from oil_tracker.domain.debug_trace import DebugCaptureDecision, DebugCaptureReason


@pytest.mark.parametrize('scene', controlled_scenes(), ids=lambda s: s.case_id)
def test_component_capture_does_not_change_detection_or_rejected_masks(scene):
    glass = InspectionRecipe.default_glass(320, 240)
    plain, no_artifacts = OpenCvPhaseDetector().detect(scene.frame, glass, 5, 1.0, debug=False)
    captured, artifacts = OpenCvPhaseDetector().detect(scene.frame, glass, 5, 1.0, debug=True)
    assert asdict(plain) == asdict(captured)
    assert no_artifacts is None
    diag = artifacts.state['foam_component_diagnostics']
    assert 'foam_component_diagnostics' not in captured.debug_metrics
    assert diag['retained_count'] <= 256
    assert diag['frame_index'] == 5
    ox, oy = diag['crop_origin']
    raster = artifacts.images['foam_component_labels']
    assert raster.dtype == np.uint16
    assert set(np.unique(raster)) - {0} == {r['diagnostic_id'] for r in diag['components']}
    for row in diag['components']:
        assert row['source_front_y'] == row['local_front_y'] + oy
        x0, y0, x1, y1 = row['local_bbox_xyxy']
        assert row['source_bbox_xyxy'] == [x0+ox,y0+oy,x1+ox,y1+oy]
        assert np.count_nonzero(raster == row['diagnostic_id']) == row['pixel_count']
    if captured.debug_metrics['foam_decision_status'] in {'weak_rejected', 'ambiguous', 'glare_rejected'}:
        assert not any(c.kind.value == 'foam_front' for c in captured.candidates)
        assert not np.any(artifacts.images['foam_mask'])


def test_no_visible_pixels_is_explicit_empty_capture():
    crop = np.zeros((20,30,3), np.uint8)
    plane = np.zeros((20,30), np.uint8)
    result = detect_bottom_connected_foam(crop,plane,plane,plane,plane,DetectorSettings(),capture_diagnostics=True)
    assert result.diagnostics['component_count'] == 0
    assert result.diagnostics['selected_label'] is None
    assert not result.diagnostics['truncated']
    assert not np.any(result.diagnostic_labels)


def test_truncation_preserves_selected_rank_and_does_not_change_components(monkeypatch):
    crop = np.full((160,160,3),45,np.uint8)
    for x,y in [(20,20),(60,20),(100,20),(20,80)]:
        cv2.rectangle(crop,(x,y),(x+14,y+18),(180,180,180),-1)
        for dy in range(2,18,4):
            for dx in range(2,14,4):
                cv2.circle(crop,(x+dx,y+dy),1,(110,110,110),-1)
    settings=DetectorSettings()
    mask=np.full(crop.shape[:2],255,np.uint8)
    pre=preprocess(crop,mask,settings)
    args=(crop,pre.gray,pre.canny,pre.glare_mask,mask,settings)
    before=detect_bottom_connected_foam(*args)
    monkeypatch.setattr(foam_module,'_DIAGNOSTIC_COMPONENT_LIMIT',1)
    result=detect_bottom_connected_foam(*args,capture_diagnostics=True)
    assert result.components == before.components
    assert result.selected_component == before.selected_component
    assert len(result.components)>1
    assert result.diagnostics['truncated']
    assert result.diagnostics['retained_count']==1
    assert result.diagnostics['selected_label']==result.selected_component.label
    assert np.max(result.diagnostic_labels)==1


@pytest.mark.parametrize('level', [DebugTraceLevel.BASIC, DebugTraceLevel.FULL])
def test_actual_detector_writer_retains_geometry_and_uint16_labels(tmp_path, level):
    glass=InspectionRecipe.default_glass(320,240)
    scene=next(s for s in controlled_scenes() if s.case_id=='white-foam')
    detection,artifacts=OpenCvPhaseDetector().detect(scene.frame,glass,5,1.0,debug=True)
    writer=JsonlDebugTraceWriter('component-test',level,staging_parent=tmp_path)
    writer.write(glass,detection,artifacts,DebugCaptureDecision(True,(DebugCaptureReason.FIRST_SAMPLE,)))
    directory=Path(writer.finalize().staging_directory)
    record=json.loads((directory/'debug_trace.jsonl').read_text().splitlines()[0])
    assert record['state']['foam_component_diagnostics']==artifacts.state['foam_component_diagnostics']
    if level is DebugTraceLevel.FULL:
        saved=cv2.imread(str(directory/record['images']['foam_component_labels']),cv2.IMREAD_UNCHANGED)
        np.testing.assert_array_equal(saved,artifacts.images['foam_component_labels'])
        assert saved.dtype==np.uint16
        assert 'foam_material_support_mask' in record['images']
    else:
        assert 'foam_component_labels' not in record['images']


def test_png_label_256_is_not_normalized(tmp_path):
    from oil_tracker.adapters.storage.jsonl_debug_trace_writer import _write_png
    labels = np.array([[0, 1, 255, 256]], dtype=np.uint16)
    path = tmp_path / "labels.png"
    _write_png(path, labels, preserve_uint16=True)
    np.testing.assert_array_equal(cv2.imread(str(path), cv2.IMREAD_UNCHANGED), labels)
