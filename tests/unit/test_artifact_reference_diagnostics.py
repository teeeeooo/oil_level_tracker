from copy import deepcopy
from dataclasses import asdict, replace
from types import SimpleNamespace
import json

import numpy as np
import pytest

from oil_tracker.adapters.vision import artifact_reference_diagnostics as diagnostics
from oil_tracker.adapters.vision.artifact_reference import capture_reference, decode_reference
from oil_tracker.adapters.vision.oil_supplemental_path import phase_transition_support
from oil_tracker.adapters.vision.oil_material_path import MaterialPathDiagnostic, MaterialPathEvidence, MaterialPathSample
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.domain.artifact_reference import ArtifactSupportReference
from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind
from oil_tracker.domain.geometry import ArtifactTemplate
from tests.fixtures.artifact_reference import reference_fixture


def case(y=60):
    frame, glass, template, _, artifacts = reference_fixture()
    snapshot, _ = decode_reference(template.support_reference)
    ox, oy = snapshot["crop_origin"]
    reference = replace(template.support_reference.with_source_position(1, 0.),
                        review_state="reviewed_support", review_rect=(25-ox, 58-oy, 60, 3))
    glass.geometry.artifact_templates = [replace(template, support_reference=reference)]
    source = artifacts.images
    gray = source['original_roi'][:, :, 0].copy()
    visible = (source['effective_mask'] > 0) & (source['glare_mask'] == 0)
    candidate = BoundaryCandidate('phase_transition_scan', BoundaryKind.OIL_AIR, y)
    rows = phase_transition_support(gray, visible, local_y=y-10, crop_origin=(10, 10))
    lineage = {"source_frame_index": 2, "glass_id": glass.id, "crop_origin": (10, 10),
               "candidate_index_space": "detection.candidates_before_trace_score_sort",
               "candidates": [{"candidate_input_index": 0, "source": candidate.source,
                               "source_y": y, "status": "measured", "phase_support": rows}]}
    return dict(frame=frame, glass=glass,
                detection=SimpleNamespace(candidates=[candidate], frame_index=2, time_sec=.5),
                pre=SimpleNamespace(gray=gray, glare_mask=source['glare_mask'].copy()),
                bundle=SimpleNamespace(effective_mask=source['effective_mask'].copy(), crop_origin=(10, 10)),
                lineage=lineage, material_paths={})


def run(args):
    return diagnostics.compare_reference_measurements(**args)


def test_exact_sampling_union_masks_and_excluded_center_not_edge_correspondence():
    args = case()
    before = deepcopy(args)
    result = run(args)
    ref = result['references'][0]
    assert ref['reference_edge_count'] == ref['reference_edges_in_common'] == 70
    assert ref['common_sampling_pixels'] == 178  # Two masked/glared positions removed.
    assert ref['candidates'][0]['statistics'] == {
        'measurement_pixels_in_common': 120, 'reference_edges_sampled': 12,
        'reference_edges_not_sampled': 58, 'reference_sampling_fraction': 12/70}
    assert ref['edge_overlap'] is None  # Pooled areas are never object-edge equality.
    assert result['physical_identity'] == result['scalar_eligibility'] == 'NOT_EVALUATED'
    assert result['optical_visibility'] == 'NOT_ESTABLISHED'
    assert np.array_equal(args['frame'], before['frame'])
    assert np.array_equal(args['bundle'].effective_mask, before['bundle'].effective_mask)
    assert args['lineage'] == before['lineage']
    assert asdict(args['glass']) == asdict(before['glass'])


def test_disjoint_and_stationary_sampling_never_grant_fluid_or_artifact_identity():
    for y in (60, 90):
        result = run(case(y))
        stat = result['references'][0]['candidates'][0]['statistics']
        assert stat['reference_edges_sampled'] == (12 if y == 60 else 0)
        assert all(result[k] == 'NOT_EVALUATED' for k in
                   ('physical_identity', 'target_role', 'path_identity', 'scalar_eligibility'))


@pytest.mark.parametrize('kind', ['no_domain', 'no_edges'])
def test_censored_and_zero_denominator_are_null_not_clean(kind):
    args = case()
    if kind == 'no_domain':
        args['pre'].glare_mask[:] = 255
    else:
        source = reference_fixture()[-1].images['canny']
        args['bundle'].effective_mask[source > 0] = 0
    result = run(args)['references'][0]
    assert result['reference_edges_in_common'] == 0
    row = result['candidates'][0]
    if kind == 'no_domain':
        assert row['statistics'] is None and row['reason'] == 'no_common_sampling_domain'
    else:
        assert row['statistics']['reference_sampling_fraction'] is None


@pytest.mark.parametrize('state', ['unreviewed', 'proposal_negative', 'mixed_or_uncertain'])
def test_scope_without_human_attribution_is_not_compared(state):
    args = case()
    template = args['glass'].geometry.artifact_templates[0]
    args['glass'].geometry.artifact_templates[0] = replace(
        template, support_reference=replace(template.support_reference, review_state=state))
    ref = run(args)['references'][0]
    assert ref['reason'] == 'reviewed_reference_unavailable' and ref['candidates'] == []


@pytest.mark.parametrize('fault', ['legacy', 'hash', 'missing_image', 'preprocessing', 'geometry', 'bool_rect'])
def test_invalid_context_and_legacy_reference_stay_unavailable(fault):
    args = case()
    template = args['glass'].geometry.artifact_templates[0]
    ref = template.support_reference
    if fault == 'legacy': ref = None
    elif fault == 'hash': ref = replace(ref, snapshot_sha256='0'*64)
    elif fault == 'geometry': args['glass'].detector_settings.canny_low += 1
    elif fault == 'bool_rect': ref = replace(ref, review_rect=(True, 1, 4, 4))
    else:
        snapshot = ref.snapshot()
        if fault == 'missing_image': del snapshot['images']['canny']
        else: snapshot['preprocessing']['contract'] = 'other'
        ref = replace(ArtifactSupportReference.capture(snapshot), review_state=ref.review_state, review_rect=ref.review_rect)
    args['glass'].geometry.artifact_templates[0] = replace(template, support_reference=ref)
    result = run(args)['references'][0]
    assert result['status'] == 'unavailable' and result['candidates'] == []


def test_scope_and_current_frame_are_part_of_comparison_identity_with_no_cache():
    args = case()
    original = run(args)['references'][0]
    template = args['glass'].geometry.artifact_templates[0]
    rect = template.support_reference.review_rect
    new_ref = replace(template.support_reference, review_rect=(rect[0], rect[1], rect[2]-1, rect[3]))
    assert new_ref.snapshot_sha256 == template.support_reference.snapshot_sha256
    args['glass'].geometry.artifact_templates[0] = replace(template, support_reference=new_ref)
    scoped = run(args)['references'][0]
    assert scoped['comparison_sha256'] != original['comparison_sha256']
    args['frame'][0, 0, 0] = 1
    assert run(args)['references'][0]['comparison_sha256'] != scoped['comparison_sha256']


def test_native_contrast_uses_actual_sector_y_and_scale_not_centered_diagnostic_bands():
    args = case()
    candidate = BoundaryCandidate('material_path', BoundaryKind.OIL_AIR, 75)
    args['detection'].candidates = [candidate]
    sample = MaterialPathSample(0, 15, 45, 50, .4, -.3, 'blurred_gray_dynamic_range', 3)
    path = MaterialPathEvidence(65, (50,), 1, .2, .4, -.3, 0., 0, 0., 0., (sample,))
    args['material_paths'] = {0: MaterialPathDiagnostic('material_path', 75, path)}
    result = run(args)
    assert result['candidates'][0]['windows'] == [[25,57,55,60], [25,61,55,64]]
    assert result['candidates'][0]['complete_score_dependency_mask'] is False
    args['material_paths'][0] = replace(args['material_paths'][0], candidate_y=74)
    assert run(args)['reason'] == 'invalid_measurement_input'


def test_missing_family_support_does_not_fall_back_to_canny_or_centered_envelope():
    args = case()
    args['detection'].candidates[0] = BoundaryCandidate('calibrated_high_recall', BoundaryKind.OIL_AIR, 60)
    result = run(args)
    assert result['candidates'][0]['observed_raw_edge'] == 'unavailable'
    assert result['references'][0]['candidates'][0]['statistics'] is None


def test_duplicate_and_lineage_order_keep_index_binding_without_extra_votes():
    args = case()
    candidate = args['detection'].candidates[0]
    args['detection'].candidates.append(candidate)
    args['lineage']['candidates'].append({**args['lineage']['candidates'][0], 'candidate_input_index':1})
    result = run(args)
    rows = result['references'][0]['candidates']
    assert [r['candidate_input_index'] for r in rows] == [0,1]
    assert rows[0]['statistics'] == rows[1]['statistics']
    args['lineage']['candidates'].reverse()
    assert run(args) == result
    args['lineage']['candidates'][0]['source_y'] += 1
    assert run(args)['reason'] == 'invalid_measurement_input'


def test_distinct_candidate_permutation_preserves_each_sampling_result():
    args = case()
    far = case(90)
    args['detection'].candidates.extend([
        far['detection'].candidates[0],
        BoundaryCandidate('calibrated_high_recall', BoundaryKind.OIL_AIR, 60),
    ])
    args['lineage']['candidates'].append(
        {**far['lineage']['candidates'][0], 'candidate_input_index': 1})

    def by_identity(result):
        measures = {row['candidate_input_index']: row for row in result['candidates']}
        return {(measures[row['candidate_input_index']]['source'],
                 measures[row['candidate_input_index']]['source_y']):
                (row['basis'], row['statistics'])
                for row in result['references'][0]['candidates']}

    expected = by_identity(run(args))
    order = [2, 0, 1]
    args['detection'].candidates = [args['detection'].candidates[i] for i in order]
    for row in args['lineage']['candidates']:
        row['candidate_input_index'] = order.index(row['candidate_input_index'])
    assert by_identity(run(args)) == expected


@pytest.mark.parametrize('fault', ['frame', 'glass', 'crop', 'duplicate'])
def test_foreign_lineage_is_explicitly_unavailable(fault):
    args = case()
    if fault == 'frame': args['lineage']['source_frame_index'] += 1
    if fault == 'glass': args['lineage']['glass_id'] = 'different'
    if fault == 'crop': args['lineage']['crop_origin'] = (0,0)
    if fault == 'duplicate': args['lineage']['candidates'] *= 2
    result = run(args)
    assert result['reason'] == 'invalid_measurement_input' and not result['references']


@pytest.mark.parametrize('cap', ['MAX_PAIRS', 'MAX_DOMAIN_PIXELS', 'MAX_RECORD_BYTES', 'MAX_CANDIDATES'])
def test_resource_limits_fail_all_or_none_without_order_dependent_partial_results(monkeypatch, cap):
    args = case()
    monkeypatch.setattr(diagnostics, cap, 0)
    result = run(args)
    assert result['status'] == 'unavailable' and result['references'] == result['candidates'] == []


def registered_detector_case():
    from tests.test_oil_detector_integration import glass, oil_frame
    config = glass()
    frame = oil_frame(130)
    detection, artifacts = OpenCvPhaseDetector().detect(frame, config, 1, 0., debug=True)
    template = ArtifactTemplate('synthetic', 'line', .5, .5, .8, .04)
    ref = capture_reference(frame, config, template, artifacts)
    snapshot, rasters = decode_reference(ref)
    w, h = snapshot['crop_size']
    assert np.count_nonzero(rasters['canny']) > 0
    ref = replace(ref.with_source_position(1, 0.), review_state='reviewed_support', review_rect=(0,0,w,h))
    config.geometry.artifact_templates = [replace(template, support_reference=ref)]
    return frame, config, template


def test_real_detector_entry_metadata_neutrality_and_none_bypass(monkeypatch):
    from oil_tracker.adapters.vision import phase_frame_detection
    frame, config, template = registered_detector_case()
    no_debug, _ = OpenCvPhaseDetector().detect(frame, config, 2, .5, debug=False)
    debug, artifacts = OpenCvPhaseDetector().detect(frame, config, 2, .5, debug=True)
    assert asdict(no_debug) == asdict(debug)
    result = artifacts.state['artifact_reference_comparison']
    assert result['status'] == 'recorded' and result['references'][0]['status'] == 'recorded'
    assert 'artifact_reference_comparison' not in debug.debug_metrics
    config.geometry.artifact_templates = [template]
    geometry_only, _ = OpenCvPhaseDetector().detect(frame, config, 2, .5, debug=False)
    assert asdict(geometry_only) == asdict(debug)
    def forbidden(**kwargs): raise AssertionError('comparison requested with debug NONE')
    monkeypatch.setattr(phase_frame_detection, 'compare_reference_measurements', forbidden)
    OpenCvPhaseDetector().detect(frame, config, 3, 1., debug=False)


@pytest.mark.parametrize('level', ['basic', 'full'])
def test_existing_trace_writer_preserves_comparison_and_candidate_join(tmp_path, level):
    from pathlib import Path
    from oil_tracker.adapters.storage.jsonl_debug_trace_writer import JsonlDebugTraceWriter
    from oil_tracker.domain.debug_trace import DebugCaptureDecision, DebugCaptureReason
    from oil_tracker.domain.session import DebugTraceLevel
    frame, config, _ = registered_detector_case()
    detector = OpenCvPhaseDetector()
    detection, artifacts = detector.detect(frame, config, 42, 1.75, debug=True)
    writer = JsonlDebugTraceWriter('reference-test', DebugTraceLevel(level), staging_parent=tmp_path)
    writer.write(config, detection, artifacts, DebugCaptureDecision(True, (DebugCaptureReason.FIRST_SAMPLE,)))
    writer.annotate_sequence(config, detector.resolve_sequence([detection], config).detections)
    done = writer.finalize()
    record = json.loads((Path(done.staging_directory)/'debug_trace.jsonl').read_text(encoding='utf-8'))
    assert record['state']['artifact_reference_comparison'] == json.loads(json.dumps(artifacts.state['artifact_reference_comparison']))
    assert record['state']['artifact_reference_comparison']['source_frame_index'] == record['frame_index'] == 42
    originals = {row['candidate_input_index']: row for row in record['candidates']}
    for row in record['state']['artifact_reference_comparison']['candidates']:
        source = originals[row['candidate_input_index']]
        assert (row['source'], row['source_y']) == (source['source'], source['canonical_y'])
