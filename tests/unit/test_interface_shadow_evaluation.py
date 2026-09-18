"""Known-label evaluator controls, not evidence of a working image classifier."""
import copy
from dataclasses import asdict
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import numpy as np
import pytest

from oil_tracker.adapters.vision.oil_interface_diagnostics import measure_oil_interfaces
from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind
from tests.diagnostics import s11_interface_shadow_evaluation as o2


def _record(frame_index=1, *, empty=False):
    gray = np.full((200, 200), 180, dtype=np.uint8)
    gray[100:] = 80
    gray[48:52] = 80  # Constructed internal stripe; no real-video label inferred.
    candidates = [] if empty else [BoundaryCandidate('material_path', BoundaryKind.OIL_AIR, y) for y in (100, 108, 50)]
    sink = []
    measure_oil_interfaces(candidates, gray=gray, effective_mask=np.ones_like(gray),
        glare_mask=np.zeros_like(gray), material_map=np.zeros_like(gray, dtype=float), static_map=None,
        crop_origin=(0, 0), frame_index=frame_index, witness_sink=sink, glass_id='g', canny=np.zeros_like(gray))
    witness = json.loads(json.dumps(asdict(sink[0])))
    raw = [{k: c[k] for k in ('candidate_input_index', 'source', 'kind', 'canonical_y', 'local_y', 'rejected')} for c in witness['candidates']]
    return SimpleNamespace(state={'oil_interface_witness': witness}, candidates=raw[::-1],
        record_id=f'r{frame_index}', run_id='synthetic-run', glass_id='g', frame_index=frame_index, timestamp_sec=frame_index / 2)


def _dataset(tmp_path):
    packet = {'schema_version': o2.PACKET_SCHEMA, 'frames': [o2.extract_frame(_record(), 'a'), o2.extract_frame(_record(2, empty=True), 'empty')]}
    sha = o2.fingerprint_json(packet)
    o2.write_new(tmp_path / 'packet.json', packet)
    cases = []
    for frame in packet['frames']:
        cases.append({'case_id': frame['case_id'], 'packet_sha256': sha,
            'recording_group': 'synthetic-recording', 'episode_id': 'episode',
            'physical_case_id': frame['case_id'], 'transform_id': 'original',
            'partition': 'regression', 'previously_reviewed': True, 'visibility': 'visible',
            'label_basis': 'synthetic_construction', 'reviewer': 'fixture-construction',
            'review_note': 'Known raster geometry; evaluator test only.',
            'contour': [{'source_x_range': [80, 120], 'source_y_interval': [99, 101]}],
            'candidates': [{'candidate_input_index': c['candidate_input_index'], 'witness_sha256': o2.fingerprint_json(c),
                'label': ('interface', 'localization_mismatch', 'reflection')[c['candidate_input_index']], 'entity_id': f"e{c['candidate_input_index']}"}
                for c in frame['witness']['candidates']]})
    labels = {'schema_version': o2.LABEL_SCHEMA, 'dataset_id': 'controls', 'label_owner': 'fixture-construction',
        'split_owner': 'fixture-construction', 'split_rationale': 'Regression only; no independent holdout claim.',
        'packets': [{'path': 'packet.json', 'sha256': sha}], 'cases': cases}
    return labels, {sha: {f['case_id']: f for f in packet['frames']}}


def _frozen(labels):
    content = {k: v for k, v in labels.items() if k != 'packets'}
    return {'schema_version': o2.FREEZE_SCHEMA, 'content': content, 'content_sha256': o2.fingerprint_json(content), 'packets': labels['packets']}


def _predictions(frozen, decisions=('INTERFACE_SUPPORTED', 'UNRESOLVED', 'INTERFACE_SUPPORTED')):
    return {'schema_version': o2.PREDICTION_SCHEMA, 'frozen_labels_sha256': frozen['content_sha256'],
        'classifier_id': 'scripted-test-not-image-classifier', 'artifact_sha256': 'a' * 64,
        'fit_partitions': ['development'], 'operating_point_description': 'Test decisions, no learned operating point.',
        'predictions': [{'case_id': 'a', 'candidate_input_index': a['candidate_input_index'],
            'witness_sha256': a['witness_sha256'], 'decision': decision, 'reason': 'scripted evaluator control',
            'intervals': [{'source_x_range': [80, 120], 'source_y_interval': [99, 101]}]}
            for a, decision in zip(frozen['content']['cases'][0]['candidates'], decisions)]}


def test_trace_join_uses_explicit_id_not_score_order():
    record = _record()
    frame = o2.extract_frame(record, 'a')
    assert [c['candidate_input_index'] for c in frame['witness']['candidates']] == [0, 1, 2]
    record.candidates[0]['canonical_y'] = 51
    with pytest.raises(ValueError, match='provenance'):
        o2.extract_frame(record, 'a')


@pytest.mark.parametrize('fault', ['old_schema', 'wrong_frame', 'wrong_glass', 'missing_candidate', 'duplicate_id'])
def test_trace_identity_and_inventory_fail_closed(fault):
    record = _record()
    w = record.state['oil_interface_witness']
    if fault == 'old_schema': w['schema_version'] = 'r22-2'
    if fault == 'wrong_frame': w['source_frame_index'] = 4
    if fault == 'wrong_glass': w['glass_id'] = 'other'
    if fault == 'missing_candidate': w['candidates'].pop()
    if fault == 'duplicate_id': w['candidates'].append(w['candidates'][0])
    with pytest.raises(ValueError): o2.extract_frame(record, 'a')


@pytest.mark.parametrize('fault', ['leakage', 'reviewed_holdout', 'pending', 'wrong_hash', 'dropped_candidate', 'duplicate_case', 'bad_interval', 'missing_frame', 'bool_index'])
def test_freeze_rejects_incomplete_or_contaminated_labels(tmp_path, fault):
    labels, packets = _dataset(tmp_path)
    first, second = labels['cases']
    if fault == 'leakage': second.update(partition='holdout', previously_reviewed=False)
    if fault == 'reviewed_holdout':
        first['partition'] = second['partition'] = 'holdout'
    if fault == 'pending': first['visibility'] = 'pending'
    if fault == 'wrong_hash': first['candidates'][0]['witness_sha256'] = '0' * 64
    if fault == 'dropped_candidate': first['candidates'].pop()
    if fault == 'duplicate_case': second['case_id'] = 'a'
    if fault == 'bad_interval': first['contour'][0]['source_y_interval'] = [101, 99]
    if fault == 'missing_frame': labels['cases'].pop()
    if fault == 'bool_index': first['candidates'][0]['candidate_input_index'] = False
    with pytest.raises(ValueError): o2.validate_labels(labels, packets)


def test_metrics_count_visible_empty_frame_and_wrong_support(tmp_path):
    labels, packets = _dataset(tmp_path)
    o2.validate_labels(labels, packets)
    frozen = _frozen(labels)
    report = o2.evaluate(frozen, packets, _predictions(frozen))
    stats = report['partitions']['regression']
    assert stats['visible_frame_count'] == 2
    assert stats['visible_frames_with_interface_proposal'] == 1
    assert stats['visible_frame_support_recall'] == .5
    assert stats['wrong_structure_support_count'] == 1
    assert stats['identity_recall'] == .5
    assert stats['verified_identity_precision'] == .5
    assert stats['abstention_rate'] == pytest.approx(1/3)
    assert stats['localization']['matched_sector_count'] == 2
    assert stats['localization']['mean_distance_to_review_interval_px'] == 3.5
    assert stats['localization']['full_review_interval_coverage'] == 1
    assert [r['distance_px'] for r in stats['localization']['sector_results']] == [0, 7]
    assert stats['by_measurement_status']['measured']['INTERFACE_SUPPORTED'] == 2
    assert not report['auto_acceptance']


def test_no_predictions_never_passes_and_keeps_visible_denominator(tmp_path):
    labels, packets = _dataset(tmp_path)
    report = o2.evaluate(_frozen(labels), packets)
    s = report['partitions']['regression']
    assert report['status'] == 'NOT_EVALUATED'
    assert s['missing_prediction_count'] == 3
    assert s['visible_frame_support_recall'] == 0
    assert s['verified_identity_precision'] is None
    assert report['partitions']['holdout']['identity_recall'] is None


def test_localization_mismatch_is_not_a_structure_negative(tmp_path):
    labels, packets = _dataset(tmp_path)
    frozen = _frozen(labels)
    report = o2.evaluate(frozen, packets, _predictions(frozen, ('UNOBSERVABLE', 'INTERFACE_SUPPORTED', 'INTERNAL_OR_ARTIFACT')))
    s = report['partitions']['regression']
    assert s['verified_identity_precision'] == 1
    assert s['wrong_structure_support_count'] == 0
    assert s['visible_frame_support_recall'] == 0
    assert s['negative_families']['reflection']['rejected'] == 1


def test_unreviewed_positive_cannot_inflate_conservative_precision(tmp_path):
    labels, packets = _dataset(tmp_path)
    labels['cases'][0]['candidates'][2]['label'] = 'unreviewed'
    frozen = _frozen(labels)
    s = o2.evaluate(frozen, packets, _predictions(frozen))['partitions']['regression']
    assert s['unverified_support_count'] == 1
    assert s['verified_identity_precision'] == 1
    assert s['conservative_supported_precision'] == .5
    assert s['unreviewed_candidate_count'] == 1


@pytest.mark.parametrize('fault', ['wrong_freeze', 'unknown_key', 'duplicate', 'bad_candidate_hash', 'fit_holdout', 'nan', 'wrong_extent'])
def test_prediction_provenance_and_operating_point_controls(tmp_path, fault):
    labels, packets = _dataset(tmp_path)
    frozen = _frozen(labels); predictions = _predictions(frozen)
    row = predictions['predictions'][0]
    if fault == 'wrong_freeze': predictions['frozen_labels_sha256'] = 'b'*64
    if fault == 'unknown_key': row['case_id'] = 'unknown'
    if fault == 'duplicate': predictions['predictions'].append(row)
    if fault == 'bad_candidate_hash': row['witness_sha256'] = 'c'*64
    if fault == 'fit_holdout': predictions['fit_partitions'] = ['holdout']
    if fault == 'nan': row['intervals'][0]['source_y_interval'][0] = float('nan')
    if fault == 'wrong_extent': row['intervals'][0]['source_x_range'] = [81, 120]
    with pytest.raises(ValueError): o2.evaluate(frozen, packets, predictions)


def test_freeze_is_portable_and_detects_packet_and_label_drift(tmp_path):
    labels, _ = _dataset(tmp_path)
    o2.write_new(tmp_path/'labels.json', labels)
    frozen = o2.freeze(tmp_path/'labels.json', tmp_path/'nested'/'frozen.json')
    loaded, _ = o2.load_frozen(tmp_path/'nested'/'frozen.json')
    assert frozen['content_sha256'] == loaded['content_sha256']
    loaded['content']['label_owner'] = 'changed'
    o2.write_new(tmp_path/'nested'/'changed.json', loaded)
    with pytest.raises(ValueError, match='frozen label hash'): o2.load_frozen(tmp_path/'nested'/'changed.json')
    packet_path = tmp_path/'packet.json'
    packet = o2.read_json(packet_path); packet['frames'][0]['timestamp_sec'] = 99
    packet_path.write_text(json.dumps(packet), encoding='utf-8')
    with pytest.raises(ValueError, match='packet hash'): o2.load_frozen(tmp_path/'nested'/'frozen.json')


def test_cli_from_foreign_unicode_cwd_with_no_stdin(tmp_path):
    labels, _ = _dataset(tmp_path)
    o2.write_new(tmp_path/'labels.json', labels)
    other = tmp_path/'다른 폴더';other.mkdir()
    script = Path(o2.__file__).resolve()
    for args in (['freeze', '--labels', str(tmp_path/'labels.json'), '--output', str(tmp_path/'frozen.json')],
                 ['evaluate', '--frozen', str(tmp_path/'frozen.json'), '--output', str(tmp_path/'report.json')]):
        result = subprocess.run([sys.executable, str(script), *args], cwd=other, stdin=subprocess.DEVNULL,
            capture_output=True, text=True, encoding='utf-8')
        assert result.returncode == 0, result.stderr
    assert o2.read_json(tmp_path/'report.json')['status'] == 'NOT_EVALUATED'
    with pytest.raises(FileExistsError): o2.write_new(tmp_path/'report.json', {})


def test_duplicate_json_keys_and_nonfinite_are_rejected(tmp_path):
    for payload in ('{"a":1,"a":2}', '{"a":NaN}'):
        p=tmp_path/'bad.json';p.write_text(payload, encoding='utf-8')
        with pytest.raises(ValueError):o2.read_json(p)


def test_combine_preserves_splits_and_does_not_erase_conflicting_owners(tmp_path):
    labels, _ = _dataset(tmp_path)
    o2.write_new(tmp_path/'labels.json', labels)
    combined = o2.combine([tmp_path/'labels.json'], 'combined', tmp_path/'out'/'combined.json')
    assert combined['cases'] == labels['cases']
    assert combined['label_owner'] == labels['label_owner']
    o2.freeze(tmp_path/'out'/'combined.json', tmp_path/'frozen.json')
    conflicting = {**labels, 'cases': [], 'label_owner': 'different-owner'}
    o2.write_new(tmp_path/'other.json', conflicting)
    with pytest.raises(ValueError, match='conflicting label_owner'):
        o2.combine([tmp_path/'labels.json', tmp_path/'other.json'], 'conflict', tmp_path/'conflict.json')


@pytest.fixture
def prepared_o2_review(tmp_path):
    from tests.integration.test_debug_trace_bundle_output import _inputs, _store
    from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
    from oil_tracker.adapters.storage.jsonl_debug_trace_writer import JsonlDebugTraceWriter
    from oil_tracker.domain.session import DebugTraceLevel
    from oil_tracker.domain.debug_trace import DebugCaptureDecision, DebugCaptureReason
    result, recipe, session = _inputs(tmp_path, DebugTraceLevel.FULL)
    glass = recipe.glasses[0]
    image = np.full((240, 320, 3), 170, dtype=np.uint8);image[120:] = 75
    detection, artifacts = OpenCvPhaseDetector().detect(image, glass, 0, 0, debug=True)
    writer = JsonlDebugTraceWriter(result.run_id, DebugTraceLevel.FULL, staging_parent=tmp_path)
    writer.write(glass, detection, artifacts, DebugCaptureDecision(True, (DebugCaptureReason.FIRST_SAMPLE,)))
    result.debug_trace_completion = writer.finalize()
    bundle = _store().write_bundle(result, recipe, session, tmp_path)
    selection = {'dataset_id':'real-entry-test', 'cases':[{'case_id':'actual', 'glass_id':glass.id, 'frame_index':0,
        'recording_group':'one', 'episode_id':'episode', 'physical_case_id':'physical', 'transform_id':'original',
        'partition':'regression', 'previously_reviewed':True}]}
    original_hash = o2.sha256_file(bundle/'debug'/'debug_trace.jsonl')
    draft = o2.prepare(bundle, selection, tmp_path/'review')
    return bundle, selection, draft, original_hash


def test_real_bundle_prepare_reuses_indexed_reader_and_preserves_empty_labels(tmp_path, prepared_o2_review):
    bundle, selection, draft, original_hash = prepared_o2_review
    assert draft['cases'][0]['visibility'] == 'pending'
    assert all(a['label']=='unreviewed' for a in draft['cases'][0]['candidates'])
    assert o2.sha256_file(bundle/'debug'/'debug_trace.jsonl') == original_hash
    with pytest.raises(ValueError):o2.freeze(tmp_path/'review'/'labels.json', tmp_path/'unreviewed.json')
    selection['cases'][0]['frame_index'] = 1
    with pytest.raises(ValueError, match='exact Glass/frame'):
        o2.prepare(bundle, selection, tmp_path/'wrong')
    assert not (tmp_path/'wrong').exists()


def test_partial_and_missing_predictions_remain_in_pair_denominator(tmp_path):
    labels, packets = _dataset(tmp_path)
    packet = next(iter(packets.values()))
    # Separate trace record, same constructed physical case under another transform.
    b = copy.deepcopy(packet['a']);b.update(case_id='b', frame_index=3, record_id='r3')
    b['witness']['source_frame_index'] = 3
    packet['b'] = b
    b_label = copy.deepcopy(labels['cases'][0]);b_label.update(case_id='b', transform_id='gamma')
    labels['cases'].append(b_label)
    frozen = _frozen(labels)
    stats = o2.evaluate(frozen, packets, _predictions(frozen))['partitions']['regression']
    assert stats['paired_entity_groups'] == 3
    assert stats['fully_evaluated_pair_groups'] == 0
    assert stats['paired_decision_consistency'] is None
    assert stats['missing_prediction_count'] == 3


def test_recording_alias_cannot_split_same_bundle_into_holdout(tmp_path):
    labels, packets = _dataset(tmp_path)
    labels['cases'][1].update(recording_group='renamed', partition='holdout', previously_reviewed=False)
    with pytest.raises(ValueError, match='renamed'):o2.validate_labels(labels, packets)


def test_positive_identity_cannot_coexist_with_not_visible_frame(tmp_path):
    labels, packets = _dataset(tmp_path)
    labels['cases'][0].update(visibility='not_visible', contour=[])
    with pytest.raises(ValueError, match='visible frame'):o2.validate_labels(labels, packets)
