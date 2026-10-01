"""Synthetic real bundle/video entry controls; never private efficacy evidence."""
import copy
from pathlib import Path
import subprocess
import sys

import cv2
import numpy as np
import pytest

from tests.diagnostics import s11_spatial_context_run as run
from tests.diagnostics import s11_interface_shadow_evaluation as o2
from tests.diagnostics import s11_review_records as records
from tests.unit.test_interface_shadow_evaluation import prepared_o2_review


@pytest.fixture
def source(prepared_o2_review, tmp_path):
    bundle, _, labels, _ = prepared_o2_review
    labels.update(label_owner='fixture', split_owner='fixture', split_rationale='regression control')
    labels['cases'][0].update(visibility='not_visible', reviewer='fixture', review_note='synthetic only')
    path = tmp_path/'review'/'ready.json'
    o2.write_new(path, labels)
    video = tmp_path/'원본 영상.avi'
    writer = cv2.VideoWriter(str(video), cv2.VideoWriter_fourcc(*'MJPG'), 30, (320, 240))
    assert writer.isOpened(), 'test requires OpenCV MJPG writer'
    image = np.full((240, 320, 3), 170, np.uint8)
    image[120:] = 75
    for _ in range(3):
        writer.write(image)
    writer.release()
    link = path.parent/'bundle-link.json'
    records.link_bundle(path, bundle, video, 'fixture', 'Synthetic video association.', link)
    return bundle, path, video, link


def execute(source, out, **kw):
    bundle, path, video, _ = source
    return run.run([path], out, bundle_path=bundle, video_path=video, expected_revisions=[0], **kw)


def test_real_cli_from_unicode_nonrepo_cwd_provenance_outputs_and_input_preservation(source, tmp_path):
    bundle, path, video, link = source
    before = {p: p.read_bytes() for root in (bundle, path.parent) for p in root.rglob('*') if p.is_file()}
    before[video] = video.read_bytes()
    out = tmp_path/'공간 결과'
    cwd = tmp_path/'다른 폴더'; cwd.mkdir()
    cli = [sys.executable, str(Path(run.__file__).resolve()), '--labels', str(path),
           '--expected-revisions', '0', '--bundle', str(bundle), '--video', str(video), '--output', str(out)]
    result = subprocess.run(cli, cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8')
    assert result.returncode == 0, result.stderr
    report = o2.read_json(out/'experiment.json')
    receipt = o2.read_json(out/'complete.json')
    assert report['schema_version'] == receipt['schema_version'] == run.SCHEMA
    assert receipt['status'] == 'COMPLETE'
    assert all(o2.sha256_file(out/name) == sha for name, sha in receipt['outputs'].items())
    assert receipt['artifact_sha256'] == report['artifact']['sha256']
    assert all(p.read_bytes() == raw for p, raw in before.items())
    assert all(r['before_sha256'] == r['after_sha256'] for r in report['input_preservation'])
    assert len(report['input_preservation']) == 9  # five bundle + labels/packet/link/video
    case = report['cases'][0]
    assert case['decode']['decoded_frame_index'] == 0
    original = o2.read_json(path.parent/'packet.json')['frames'][0]['witness']
    assert case['baseline_witness'] == original
    expected = [{**g, 'candidate_input_index': c['candidate_input_index']}
                for c in original['candidates'] for g in o2.review_geometry(c)]
    assert [{k:v for k,v in p.items() if k != 'profile_id'} for p in case['measurement']['points']] == expected
    for raster in case['rasters'].values():
        decoded = cv2.imdecode(np.frombuffer((out/raster['file']).read_bytes(), np.uint8), cv2.IMREAD_UNCHANGED)
        assert run.raster_identity(decoded) == {k:v for k,v in raster.items() if k != 'file'}
    assert list(out.glob('*.svg')) and 'NOT_EVALUATED' in (out/'summary.md').read_text(encoding='utf-8')
    assert report['decision'] == 'NOT_EVALUATED' and not report['production_decisions_emitted']
    with pytest.raises(ValueError, match='already exists'):
        execute(source, out)


@pytest.mark.parametrize('fault', ['video', 'bundle', 'revision', 'link', 'scene', 'packet', 'writer_lock'])
def test_bound_input_mismatch_rejected_without_complete(source, tmp_path, fault):
    bundle, path, video, link_path = source
    if fault == 'video': video.write_bytes(video.read_bytes()+b'changed')
    if fault == 'bundle':
        with (bundle/'debug'/'debug_trace.jsonl').open('ab') as f: f.write(b'\n')
    if fault in ('link', 'scene'):
        link = o2.read_json(link_path)
        if fault == 'link': link['source']['sha256'] = '0'*64
        else:
            link['scenes'][0]['scene_identity']['frame_index'] = 999
            link['identity_sha256'] = o2.fingerprint_json({k:v for k,v in link.items() if k not in ('identity_sha256','locators','history')})
        link_path.write_text(__import__('json').dumps(link), encoding='utf-8')
    if fault == 'packet':
        packet = path.parent/'packet.json'
        packet.write_text('{}', encoding='utf-8')
    if fault == 'writer_lock': Path(str(path)+'.lock').touch()
    out = tmp_path/'failure'
    with pytest.raises((ValueError, KeyError)):
        if fault == 'revision':
            run.run([path], out, bundle_path=bundle, video_path=video, expected_revisions=[999])
        else: execute(source, out)
    assert not (out/'complete.json').exists()


@pytest.mark.parametrize('fault', ['dimensions', 'frame', 'crop', 'during_measure', 'during_publish'])
def test_decode_geometry_and_midrun_mutation_fail_closed(source, tmp_path, monkeypatch, fault):
    _, _, video, _ = source
    decode = run.decode_exact
    if fault in ('dimensions', 'frame'):
        def wrong(reader, frame):
            if fault == 'frame':
                changed = {**frame, 'frame_index': 999}
                return decode(reader, changed)
            image, info = decode(reader, frame)
            return image[:100], info
        monkeypatch.setattr(run, 'decode_exact', wrong)
    if fault == 'crop':
        build = run.geometry_masks.build_mask_bundle
        def wrong_crop(*args):
            masks = build(*args); masks.crop_origin = (999, 999); return masks
        monkeypatch.setattr(run.geometry_masks, 'build_mask_bundle', wrong_crop)
    if fault == 'during_measure':
        measure = run.probe.measure_context
        def mutate(*args, **kw):
            video.write_bytes(video.read_bytes()+b'changed')
            return measure(*args, **kw)
        monkeypatch.setattr(run.probe, 'measure_context', mutate)
    if fault == 'during_publish':
        encode = run.cv2.imencode
        def mutate(*args, **kw):
            video.write_bytes(video.read_bytes()+b'changed')
            return encode(*args, **kw)
        monkeypatch.setattr(run.cv2, 'imencode', mutate)
    out = tmp_path/'failure'
    with pytest.raises((ValueError, EOFError)):
        execute(source, out)
    assert not (out/'complete.json').exists()


def test_decoder_forward_exact_and_overshoot_rejected():
    class Reader:
        def read_at(self, _): return np.zeros((1,1), np.uint8), 9, 0.9
        def read_next(self): return np.zeros((1,1), np.uint8), 10, 1.0
    _, info = run.decode_exact(Reader(), {'frame_index': 10, 'timestamp_sec': 1.0})
    assert info['forward_decodes'] == 1
    with pytest.raises(ValueError, match='exact frame mismatch'):
        run.decode_exact(Reader(), {'frame_index': 8, 'timestamp_sec': .8})


def test_output_inside_review_is_rejected(source):
    with pytest.raises(ValueError, match='outside bundle/review'):
        execute(source, source[1].parent/'output')


def test_baseline_arithmetic_parity_and_reconstruction_drift_are_explicit():
    from dataclasses import asdict
    from tests.unit.test_oil_interface_witness import measure
    gray = np.full((200,200), 180, np.uint8); gray[100:] = 80
    mask = np.ones_like(gray); glare = np.zeros_like(gray)
    witness = asdict(measure(gray))
    good = run.baseline_check(gray, mask, glare, witness)
    assert good['band_count'] > 0 and good['status'] == 'MATCH'
    changed = gray.copy(); changed[90:99] = 0
    bad = run.baseline_check(changed, mask, glare, witness)
    assert bad['status'] == 'DIFFERENT' and bad['mismatched_band_count'] > 0
    assert all(r['original'] == s['original'] for r,s in zip(good['rows'],bad['rows'],strict=True))


def test_two_frames_same_bundle_real_entry(tmp_path):
    from tests.integration.test_debug_trace_bundle_output import _inputs, _store
    from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
    from oil_tracker.adapters.storage.jsonl_debug_trace_writer import JsonlDebugTraceWriter
    from oil_tracker.domain.session import DebugTraceLevel
    from oil_tracker.domain.debug_trace import DebugCaptureDecision, DebugCaptureReason
    result, recipe, session = _inputs(tmp_path, DebugTraceLevel.FULL)
    glass = recipe.glasses[0]
    video = tmp_path/'two.avi'
    encoder = cv2.VideoWriter(str(video), cv2.VideoWriter_fourcc(*'MJPG'), 30, (320,240))
    assert encoder.isOpened()
    writer = JsonlDebugTraceWriter(result.run_id, DebugTraceLevel.FULL, staging_parent=tmp_path)
    for index in range(2):
        image = np.full((240,320,3),170,np.uint8); image[120+index*5:] = 75
        encoder.write(image)
        detection, artifacts = OpenCvPhaseDetector().detect(image, glass, index, index/30, debug=True)
        writer.write(glass, detection, artifacts, DebugCaptureDecision(True, (DebugCaptureReason.FIRST_SAMPLE,)))
    encoder.release()
    result.debug_trace_completion = writer.finalize()
    bundle = _store().write_bundle(result, recipe, session, tmp_path)
    paths = []
    for index in range(2):
        folder = tmp_path/f'review{index}'
        selection = {'dataset_id':f'two{index}', 'cases':[{'case_id':f'case{index}', 'glass_id':glass.id,
                     'frame_index':index, 'recording_group':'one','episode_id':'episode', 'physical_case_id':f'p{index}',
                     'transform_id':'original','partition':'regression','previously_reviewed':True}]}
        labels = o2.prepare(bundle,selection,folder)
        labels.update(label_owner='fixture',split_owner='fixture',split_rationale='control')
        labels['cases'][0].update(visibility='not_visible',reviewer='fixture',review_note='synthetic')
        path = folder/'ready.json'; o2.write_new(path,labels)
        records.link_bundle(path,bundle,video,'fixture','synthetic association',folder/'bundle-link.json')
        paths.append(path)
    report = run.run(paths,tmp_path/'two-out',bundle_path=bundle,video_path=video,expected_revisions=[0,0])
    assert [c['decode']['decoded_frame_index'] for c in report['cases']] == [0,1]
    assert len(report['input_preservation']) == 12
    assert (tmp_path/'two-out'/'complete.json').exists()
    assert len({c['rasters']['source']['sha256'] for c in report['cases']}) == 2
