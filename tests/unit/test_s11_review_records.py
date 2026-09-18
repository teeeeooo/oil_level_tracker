"""Durable review controls; constructed media are not human field evidence."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from tests.diagnostics import s11_interface_shadow_evaluation as o2
from tests.diagnostics import s11_review_records as records
from tests.unit.test_interface_shadow_evaluation import _dataset, prepared_o2_review


@pytest.fixture
def draft(tmp_path):
    labels, _ = _dataset(tmp_path)
    for c in labels['cases']:
        c.update(visibility='pending', reviewer='', review_note='', contour=[])
        for a in c['candidates']:
            a.update(label='unreviewed', entity_id=None)
    labels.update(label_owner='', split_owner='', split_rationale='')
    path = tmp_path/'labels.json'
    o2.write_new(path, labels)
    return path


def _reply(path):
    a = o2.read_json(path)['cases'][0]['candidates'][0]
    return {'reviewer': 'human-reviewer', 'note': 'Reviewed displayed source-frame geometry.',
            'owners': {'label_owner': 'human-reviewer', 'split_owner': 'split-owner', 'split_rationale': 'Known regression.'},
            'case_id': 'a', 'visibility': 'visible',
            'contour': [{'source_x_range': [80, 120], 'source_y_interval': [99, 101]}],
            'candidates': [{k: a[k] for k in ('candidate_input_index', 'witness_sha256')} | {'label': 'interface'}]}


def test_save_resume_old_v1_and_frozen_snapshot_survive_moves(draft, tmp_path):
    before = records.status(draft)
    reply = _reply(draft)
    saved = records.record(draft, reply, before['labels_sha256'])
    assert saved['revision_count'] == 1
    assert saved['cases'][0]['unreviewed_candidate_ids'] == [1, 2]
    assert saved['cases'][1]['visibility'] == 'pending'
    archive = draft.parent/(draft.name+'.history')/(before['labels_sha256']+'.json')
    assert o2.fingerprint_json(o2.read_json(archive)) == before['labels_sha256']
    with pytest.raises(ValueError, match='human visibility|reviewer'):
        o2.freeze(draft, tmp_path/'premature.json')
    records.record(draft, {'reviewer':'reviewer', 'note':'No visible interface.', 'case_id':'empty',
                          'visibility':'not_visible'}, saved['labels_sha256'])
    frozen = o2.freeze(draft, tmp_path/'frozen.json')
    # Move the entire data tree, without code or the original bundle.
    moved = tmp_path.parent/(tmp_path.name+' moved 한글')
    shutil.move(str(tmp_path), moved)
    assert records.status(moved/'labels.json')['revision_count'] == 2
    loaded, _ = o2.load_frozen(moved/'frozen.json')
    assert loaded['content_sha256'] == frozen['content_sha256']
    sha = records.status(moved/'labels.json')['labels_sha256']
    records.record(moved/'labels.json', {'reviewer':'reviewer', 'note':'Correction after review.',
                   'case_id':'a', 'contour':[]}, sha)
    assert o2.load_frozen(moved/'frozen.json')[0]['content_sha256'] == frozen['content_sha256']


@pytest.mark.parametrize('fault', ['stale', 'wrong_witness', 'unknown_candidate', 'unknown_case', 'unsupported', 'positive_pending', 'bad_contour', 'not_visible', 'duplicate', 'bool_id'])
def test_rejected_edits_leave_labels_and_history_untouched(draft, fault):
    original = draft.read_bytes()
    sha = records.status(draft)['labels_sha256']
    reply = _reply(draft)
    if fault == 'stale': sha = '0'*64
    if fault == 'wrong_witness': reply['candidates'][0]['witness_sha256'] = '0'*64
    if fault == 'unknown_candidate': reply['candidates'][0]['candidate_input_index'] = 999
    if fault == 'unknown_case': reply['case_id'] = 'missing'
    if fault == 'unsupported': reply['partition'] = 'holdout'
    if fault == 'positive_pending': reply.pop('visibility')
    if fault == 'bad_contour': reply['contour'][0]['source_y_interval'] = [101, 99]
    if fault == 'not_visible': reply['visibility'] = 'not_visible'
    if fault == 'duplicate': reply['candidates'] *= 2
    if fault == 'bool_id': reply['candidates'][0]['candidate_input_index'] = False
    with pytest.raises((ValueError, KeyError)):
        records.record(draft, reply, sha)
    assert draft.read_bytes() == original
    assert not Path(str(draft)+'.lock').exists()
    assert not (draft.parent/(draft.name+'.history')).exists()


def test_writer_lock_prevents_overlap_and_preserves_an_existing_lock(draft):
    lock = Path(str(draft)+'.lock'); lock.write_text('another writer', encoding='utf-8')
    with pytest.raises(ValueError, match='writer lock'):
        records.record(draft, _reply(draft), records.status(draft)['labels_sha256'])
    assert lock.read_text(encoding='utf-8') == 'another writer'


def test_interrupted_replace_keeps_original_and_retry_uses_archive(draft, monkeypatch):
    original = draft.read_bytes(); sha = records.status(draft)['labels_sha256']
    writer = records.atomic_write_text
    def fail(path, text):
        if Path(path) == draft:
            raise OSError('simulated destination write failure')
        writer(path, text)
    with monkeypatch.context() as m:
        m.setattr(records, 'atomic_write_text', fail)
        with pytest.raises(OSError): records.record(draft, _reply(draft), sha)
    assert draft.read_bytes() == original
    assert not Path(str(draft)+'.lock').exists()
    assert records.record(draft, _reply(draft), sha)['revision_count'] == 1


def test_candidate_reply_does_not_replace_scene_review_provenance(draft):
    reply = _reply(draft)
    records.record(draft, reply, records.status(draft)['labels_sha256'])
    scene = o2.read_json(draft)['cases'][0]['scene_review']
    reply.pop('visibility'); reply.pop('contour'); reply.pop('owners')
    reply['reviewer'] = 'second reviewer';reply['note'] = 'Candidate-only correction.'
    reply['candidates'][0]['label'] = 'localization_mismatch'
    records.record(draft, reply, records.status(draft)['labels_sha256'])
    current = o2.read_json(draft)['cases'][0]
    assert current['scene_review'] == scene
    assert current['candidates'][0]['reviewer'] == 'second reviewer'


def test_bundle_receipt_verifies_witnesses_and_relocates(prepared_o2_review, tmp_path):
    bundle, _, _, _ = prepared_o2_review
    video = tmp_path/'source.mp4';video.write_bytes(b'fixture media; association is test attestation')
    labels = tmp_path/'review'/'labels.json';link = labels.parent/'bundle-link.json'
    registered = records.link_bundle(labels, bundle, video, 'fixture owner', 'Constructed input.', link)
    original = records.load_link(link)
    assert original['source']['association_basis'] == 'human_attestation'
    assert original['scenes'][0]['scene_identity']['frame_index'] == 0
    assert records.status(labels, link)['bundle_link']['locator_exists'] == {'bundle':True, 'video':True}
    with pytest.raises(ValueError, match='already exists'):
        records.link_bundle(labels, bundle, video, 'owner', 'note', link)
    moved_bundle = tmp_path/'이동한 bundle';shutil.move(str(bundle), moved_bundle)
    moved_video = tmp_path/'이동한 video.mp4';shutil.move(str(video), moved_video)
    assert records.status(labels, link)['bundle_link']['locator_exists'] == {'bundle':False, 'video':False}
    records.relink(link, moved_bundle, moved_video, 'owner', 'Files moved.')
    assert records.load_link(link)['identity_sha256'] == registered['identity_sha256']
    assert records.status(labels, link)['bundle_link']['locator_exists'] == {'bundle':True, 'video':True}
    stable = link.read_bytes()
    moved_video.write_bytes(b'different media')
    with pytest.raises(ValueError, match='video bytes'):
        records.relink(link, moved_bundle, moved_video, 'owner', 'Wrong video.')
    assert link.read_bytes() == stable
    trace = moved_bundle/'debug'/'debug_trace.jsonl'
    with trace.open('ab') as f:f.write(b'\n')
    with pytest.raises(ValueError, match='changed bundle'):
        records.relink(link, moved_bundle, moved_video, 'owner', 'Changed trace.')
    assert link.read_bytes() == stable


def test_link_rejects_tampered_packet_even_when_packet_hash_is_updated(prepared_o2_review, tmp_path):
    bundle, _, _, _ = prepared_o2_review
    video = tmp_path/'source.mp4';video.write_bytes(b'fixture')
    labels = tmp_path/'review'/'labels.json';packet_path = labels.parent/'packet.json'
    packet = o2.read_json(packet_path);packet['frames'][0]['timestamp_sec'] = 999
    packet_path.write_text(json.dumps(packet), encoding='utf-8')
    label = o2.read_json(labels);new_sha = o2.fingerprint_json(packet)
    label['packets'][0]['sha256'] = new_sha
    label['cases'][0]['packet_sha256'] = new_sha
    labels.write_text(json.dumps(label), encoding='utf-8')
    with pytest.raises(ValueError, match='record mismatch'):
        records.link_bundle(labels, bundle, video, 'owner', 'note', labels.parent/'link.json')


def test_existing_packet_link_mismatch_rejected(draft, tmp_path):
    # Fully checked format but linked to another packet, never a silent cross-run join.
    link = {'schema_version': records.LINK_SCHEMA, 'packet_sha256s': ['other']}
    link['identity_sha256'] = o2.fingerprint_json(link)
    o2.write_new(tmp_path/'link.json', link)
    with pytest.raises(ValueError, match='link/packet'):
        records.status(draft, tmp_path/'link.json')


def test_cli_resume_and_record_from_nonrepo_unicode_cwd(draft, tmp_path):
    other = tmp_path/'외부 작업';other.mkdir()
    script = Path(o2.__file__).resolve()
    def run(*args):
        r = subprocess.run([sys.executable, str(script), *args], cwd=other, stdin=subprocess.DEVNULL,
                           capture_output=True, encoding='utf-8')
        assert r.returncode == 0, r.stderr
        return json.loads(r.stdout)
    before = run('status', '--labels', str(draft))
    update = tmp_path/'회신.json';o2.write_new(update, _reply(draft))
    after = run('record', '--labels', str(draft), '--update', str(update), '--expected-sha256', before['labels_sha256'])
    assert after['revision_count'] == 1
    assert run('status', '--labels', str(draft))['cases'][0]['unreviewed_candidate_ids'] == [1,2]


def test_relative_locator_falls_back_for_different_windows_drives(tmp_path, monkeypatch):
    def different_drives(*args):raise ValueError('path is on another drive')
    monkeypatch.setattr(records.os.path, 'relpath', different_drives)
    target = tmp_path/'source.mp4'
    assert Path(o2.relative_path(target, tmp_path)) == target.resolve()


def test_link_and_relink_cli_use_real_bundle_from_foreign_cwd(prepared_o2_review, tmp_path):
    bundle, _, _, _ = prepared_o2_review
    labels = tmp_path/'review'/'labels.json'; link = labels.parent/'bundle-link.json'
    video = tmp_path/'영상.mp4'; video.write_bytes(b'fixture source identity')
    other = tmp_path/'other cwd'; other.mkdir()
    script = str(Path(o2.__file__).resolve())
    for args in (
        ['link-bundle', '--labels', str(labels), '--bundle', str(bundle), '--video', str(video),
         '--output', str(link), '--reviewer', 'fixture', '--note', 'fixture association'],
        ['relink', '--link', str(link), '--bundle', str(bundle), '--video', str(video),
         '--reviewer', 'fixture', '--note', 'verify original location'],
        ['status', '--labels', str(labels), '--link', str(link)],
    ):
        result = subprocess.run([sys.executable, script, *args], cwd=other, stdin=subprocess.DEVNULL,
                                capture_output=True, encoding='utf-8')
        assert result.returncode == 0, result.stderr
        assert isinstance(json.loads(result.stdout), dict)


def test_legacy_v1_scene_attribution_survives_candidate_only_edit(tmp_path):
    labels, _ = _dataset(tmp_path)
    path = tmp_path/'labels.json';o2.write_new(path, labels)
    reply = _reply(path)
    reply.pop('visibility');reply.pop('contour');reply.pop('owners')
    records.record(path, reply, records.status(path)['labels_sha256'])
    current = o2.read_json(path)['cases'][0]
    assert current['scene_review']['reviewer'] == labels['cases'][0]['reviewer']
    assert current['scene_review']['note'] == labels['cases'][0]['review_note']
    assert current['scene_review']['at'] is None
    assert current['scene_review']['basis'] == 'legacy_v1_case'
