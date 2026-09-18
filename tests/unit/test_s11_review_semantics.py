"""Scoped human review and explicit migration controls, never field truth."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from tests.diagnostics import s11_interface_shadow_evaluation as o2
from tests.diagnostics import s11_review_records as records
from tests.unit.test_interface_shadow_evaluation import _dataset, _frozen, _predictions, prepared_o2_review


def _migrate(source, destination):
    return records.migrate(source, destination, records.status(source)['labels_sha256'],
                           'migration operator', 'Format conversion only; no new human judgment.')


@pytest.fixture
def migrated(tmp_path):
    labels, _ = _dataset(tmp_path)
    labels['review_history'] = [{'at': 'old time', 'update': {'note': 'original reply'}}]
    labels['cases'][0]['candidates'][0].update(reviewer='original reader', review_note='Holistic interface, partial offset.')
    source = tmp_path/'labels.json'
    o2.write_new(source, labels)
    destination = tmp_path/'new'/'labels-v2.json'
    _migrate(source, destination)
    return source, destination


def _change(path, index=0, **fields):
    a = o2.read_json(path)['cases'][0]['candidates'][index]
    return {'candidate_input_index': a['candidate_input_index'], 'witness_sha256': a['witness_sha256'], **fields}


def _record(path, changes, **fields):
    return records.record(path, {'reviewer': 'new reader', 'note': 'Explicit judgment on the displayed geometry.',
        'case_id': 'a', 'candidates': changes, **fields}, records.status(path)['labels_sha256'])


def _path(x=(0, 40), y=100, judgment='near_interface', basis='candidate_center'):
    return {'geometry_basis': basis, 'source_x_range': list(x), 'source_y': y, 'judgment': judgment}


def test_migration_preserves_legacy_judgments_attribution_and_all_artifacts(migrated):
    source, dest = migrated
    original = o2.read_json(source)
    converted = o2.read_json(dest)
    assert converted['schema_version'] == o2.LABEL_SCHEMA
    assert converted['review_history'] == original['review_history']
    assert converted['cases'][0]['contour'] == original['cases'][0]['contour']
    for old, new in zip(original['cases'][0]['candidates'], converted['cases'][0]['candidates']):
        assert new['legacy_annotation'] == old
        assert new['witness_sha256'] == old['witness_sha256']
        assert new['entity_id'] == old['entity_id']
        assert new['path_reviews'] == []
    a, b, c = converted['cases'][0]['candidates']
    assert [a['identity'], b['identity'], c['identity']] == ['interface', 'interface', 'non_interface']
    assert b['legacy_annotation']['label'] == 'localization_mismatch'
    assert a['identity_review']['reviewer'] == 'original reader'
    assert a['identity_review']['at'] is None
    assert c['artifact_tags'] == ['reflection']
    migration = converted['migration']
    assert o2.read_json(dest.parent/migration['snapshot_path']) == original
    assert migration['source_file_sha256'] == o2.sha256_file(source)
    assert records.status(dest)['revision_count'] == 1
    assert o2.load_packets(converted, dest.parent) == o2.load_packets(original, source.parent)
    frozen_old = o2.freeze(source, source.parent/'old-frozen.json')
    old_bytes = (source.parent/'old-frozen.json').read_bytes()
    _record(dest, [_change(dest, identity='uncertain')])
    assert o2.read_json(source) == original
    assert (source.parent/'old-frozen.json').read_bytes() == old_bytes
    assert o2.load_frozen(source.parent/'old-frozen.json')[0] == frozen_old


@pytest.mark.parametrize('label,expected', [(l, ('interface' if l in o2.POSITIVES else 'non_interface' if l in o2.NEGATIVES
                                                 else 'unreviewed' if l == 'unreviewed' else 'uncertain')) for l in o2.LABELS])
def test_all_v1_labels_migrate_without_inventing_geometry(tmp_path, label, expected):
    labels, _ = _dataset(tmp_path)
    labels['cases'][0]['candidates'][0]['label'] = label
    source = tmp_path/'old.json';o2.write_new(source, labels)
    dest = tmp_path/'v2.json';_migrate(source, dest)
    a = o2.read_json(dest)['cases'][0]['candidates'][0]
    assert a['identity'] == expected
    assert a['legacy_annotation']['label'] == label
    assert a['path_reviews'] == []


def test_sparse_path_reviews_do_not_replace_identity_scene_or_other_paths(migrated):
    _, path = migrated
    before = o2.read_json(path)
    _record(path, [_change(path, path_reviews=[_path()])], review_basis='prior_direct_review_exact_geometry_checked')
    _record(path, [_change(path, path_reviews=[_path((40, 80), judgment='off_interface')])])
    after = o2.read_json(path)
    a = after['cases'][0]['candidates'][0]
    assert a['identity_review'] == before['cases'][0]['candidates'][0]['identity_review']
    assert a['identity'] == 'interface'
    assert after['cases'][0]['reviewer'] == before['cases'][0]['reviewer']
    assert a['path_reviews'][0]['review']['basis'] == 'prior_direct_review_exact_geometry_checked'
    summary = records.status(path)['cases'][0]['candidate_reviews'][0]['path_review']['candidate_center']
    assert summary['near_interface'] == 1 and summary['off_interface'] == 1
    assert summary['unreviewed'] == 3 and summary['review_coverage'] == .4
    assert summary['full_path_localization_pass'] is None
    _record(path, [_change(path, path_reviews=[_path(judgment='uncertain')])])
    assert len(o2.read_json(path)['cases'][0]['candidates'][0]['path_reviews']) == 2


@pytest.mark.parametrize('fault', ['wrong_x', 'wrong_y', 'invent_native', 'duplicate', 'label', 'tags', 'bool_y', 'wrong_witness', 'near_not_visible'])
def test_bad_scoped_edits_are_atomic_and_fail_closed(migrated, fault):
    _, path = migrated
    reply = _change(path, path_reviews=[_path()])
    extra = {}
    if fault == 'wrong_x': reply['path_reviews'][0]['source_x_range'] = [1, 40]
    if fault == 'wrong_y': reply['path_reviews'][0]['source_y'] = 108
    if fault == 'invent_native': reply['path_reviews'][0]['geometry_basis'] = 'native_path'
    if fault == 'duplicate': reply['path_reviews'] *= 2
    if fault == 'label': reply['label'] = 'interface'
    if fault == 'tags': reply['artifact_tags'] = ['reflection', 'reflection']
    if fault == 'bool_y': reply['path_reviews'][0]['source_y'] = True
    if fault == 'wrong_witness': reply['witness_sha256'] = '0'*64
    if fault == 'near_not_visible': extra = {'visibility': 'not_visible', 'contour': []}
    before = path.read_bytes()
    history = sorted(p.name for p in Path(str(path)+'.history').iterdir())
    with pytest.raises(ValueError): _record(path, [reply], **extra)
    assert path.read_bytes() == before
    assert sorted(p.name for p in Path(str(path)+'.history').iterdir()) == history
    assert not Path(str(path)+'.lock').exists()


def test_overlapping_artifact_tags_are_not_extra_identity_votes(migrated):
    _, path = migrated
    _record(path, [_change(path, 2, identity='non_interface', artifact_tags=['structure', 'reflection'],
                          artifact_note='Scratch with reflected light; both descriptions supplied.')])
    labels, packets = records._load_labels(path)
    frozen = _frozen(labels)
    stats = o2.evaluate(frozen, packets, _predictions(frozen))['partitions']['regression']
    assert stats['wrong_non_interface_support_count'] == 1
    assert stats['negative_families']['reflection']['wrong_support'] == 1
    assert stats['negative_families']['structure']['wrong_support'] == 1
    assert stats['verified_identity_precision'] == .5
    _record(path, [_change(path, 2, artifact_tags=[], artifact_note='Subtype not specified.')])
    assert o2.read_json(path)['cases'][0]['candidates'][2]['identity'] == 'non_interface'


def test_identity_and_all_near_paths_without_contour_never_certify_localization(migrated):
    _, path = migrated
    paths = [_path((i*40, (i+1)*40)) for i in range(5)]
    _record(path, [_change(path, path_reviews=paths)], contour=[])
    labels, packets = records._load_labels(path)
    frozen = _frozen(labels)
    report = o2.evaluate(frozen, packets, _predictions(frozen))
    assert report['schema_version'] == 's11-o2-shadow-report-v2'
    stats = report['partitions']['regression']
    assert stats['visible_frame_identity_support_recall'] == .5
    assert 'visible_frames_with_localized_support' not in stats
    assert 'visible_frame_support_recall' not in stats
    localization = stats['localization']['all_interface_proposals']
    assert localization['status'] == 'not_measured'
    assert localization['mean_distance_to_review_interval_px'] is None
    assert localization['reviewed_contour_coverage'] == 0
    assert localization['eligible_sector_count'] == 10
    assert stats['localization']['full_path_localization_pass'] is None
    assert stats['qualitative_path_review']['candidate_results'][0]['by_geometry_basis']['candidate_center']['near_interface'] == 5
    # Partial geometry agreement also cannot change candidate identity metrics.
    _record(path, [_change(path, path_reviews=[_path(judgment='off_interface')])])
    labels, packets = records._load_labels(path)
    after = o2.evaluate(_frozen(labels), packets, _predictions(_frozen(labels)))['partitions']['regression']
    assert after['identity_recall'] == stats['identity_recall']
    assert after['localization']['full_path_localization_pass'] is None


def test_numeric_proposal_quality_is_separate_from_model_support(migrated):
    _, path = migrated
    labels, packets = records._load_labels(path);frozen = _frozen(labels)
    stats = o2.evaluate(frozen, packets, _predictions(frozen))['partitions']['regression']
    all_rows = stats['localization']['all_interface_proposals']
    supported = stats['localization']['supported_interface_proposals']
    assert [r['distance_px'] for r in all_rows['sector_results']] == [0, 7]
    assert all_rows['eligible_sector_count'] == 10
    assert all_rows['reviewed_contour_coverage'] == .2
    assert [r['distance_px'] for r in supported['sector_results']] == [0]
    assert supported['eligible_sector_count'] == 5
    report = o2.evaluate(frozen, packets)
    assert report['status'] == 'NOT_EVALUATED'
    stats = report['partitions']['regression']
    assert stats['visible_frame_count'] == 2  # Includes the empty-candidate frame.
    assert stats['missing_prediction_count'] == 3
    assert stats['localization']['supported_interface_proposals']['status'] == 'not_measured'
    assert stats['localization']['supported_interface_proposals']['reviewed_contour_coverage'] is None
    assert stats['localization']['all_interface_proposals']['matched_sector_count'] == 2
    _record(path, [], contour=[{'source_x_range': [81, 120], 'source_y_interval': [99, 101]}])
    labels, packets = records._load_labels(path)
    assert o2.evaluate(_frozen(labels), packets)['partitions']['regression']['localization']['all_interface_proposals']['matched_sector_count'] == 0


def test_native_and_candidate_geometry_are_independent_review_scopes(tmp_path):
    labels, _ = _dataset(tmp_path)
    packet = o2.read_json(tmp_path/'packet.json')
    candidate = packet['frames'][0]['witness']['candidates'][0]
    # Constructed witness geometry; no real physical labels inferred.
    candidate['sectors'][0]['path_source_y'] = 90
    packet_sha = o2.fingerprint_json(packet)
    (tmp_path/'packet.json').write_text(json.dumps(packet), encoding='utf-8')
    labels['packets'][0]['sha256'] = packet_sha
    for case in labels['cases']: case['packet_sha256'] = packet_sha
    labels['cases'][0]['candidates'][0]['witness_sha256'] = o2.fingerprint_json(candidate)
    source = tmp_path/'old.json';o2.write_new(source, labels)
    path = tmp_path/'v2.json';_migrate(source, path)
    _record(path, [_change(path, path_reviews=[_path(y=90, basis='native_path'), _path(judgment='off_interface')])])
    summary = records.status(path)['cases'][0]['candidate_reviews'][0]['path_review']
    assert summary['native_path']['near_interface'] == 1
    assert summary['candidate_center']['off_interface'] == 1
    with pytest.raises(ValueError, match='exact witness'):
        _record(path, [_change(path, path_reviews=[_path(y=90, basis='candidate_center')])])


def test_migration_failure_and_retry_preserve_source_and_archived_snapshot(tmp_path, monkeypatch):
    labels, _ = _dataset(tmp_path)
    source = tmp_path/'old.json';o2.write_new(source, labels)
    dest = tmp_path/'new'/'v2.json'
    before = source.read_bytes(); sha = records.status(source)['labels_sha256']
    writer = records.atomic_write_text
    def fail(path, text):
        if Path(path) == dest: raise OSError('simulated interrupted destination')
        writer(path, text)
    with monkeypatch.context() as m:
        m.setattr(records, 'atomic_write_text', fail)
        with pytest.raises(OSError): _migrate(source, dest)
    assert source.read_bytes() == before and not dest.exists()
    assert o2.read_json(Path(str(dest)+'.history')/(sha+'.json')) == labels
    assert not Path(str(source)+'.lock').exists()
    assert not Path(str(dest)+'.lock').exists()
    _migrate(source, dest)
    stable = dest.read_bytes()
    with pytest.raises(ValueError, match='already exists'): _migrate(source, dest)
    assert dest.read_bytes() == stable
    with pytest.raises(ValueError, match='new destination'): _migrate(source, source)
    with pytest.raises(ValueError, match='stale'):
        records.migrate(source, tmp_path/'stale.json', '0'*64, 'reader', 'note')
    with pytest.raises(ValueError, match='already current'): _migrate(dest, tmp_path/'again.json')


def test_v1_new_fields_rejected_until_explicit_migration(migrated):
    source, _ = migrated
    with pytest.raises(ValueError, match='migration'):
        _record(source, [_change(source, identity='interface')])


def test_cli_migrate_record_freeze_evaluate_and_resume_after_move(migrated, tmp_path):
    source, _ = migrated
    other = tmp_path/'다른 작업 폴더';other.mkdir()
    script = str(Path(o2.__file__).resolve())
    def run(*args):
        r = subprocess.run([sys.executable, script, *map(str, args)], cwd=other,
                           stdin=subprocess.DEVNULL, capture_output=True, encoding='utf-8')
        assert r.returncode == 0, r.stderr
        return json.loads(r.stdout) if r.stdout else None
    target = tmp_path/'재개'/'labels.json'
    result = run('migrate', '--labels', source, '--output', target,
                 '--expected-sha256', records.status(source)['labels_sha256'], '--reviewer', 'operator', '--note', 'Explicit conversion.')
    reply = tmp_path/'답변.json'
    o2.write_new(reply, {'reviewer':'reader', 'note':'Exact previously reviewed geometry.', 'case_id':'a',
                        'candidates':[_change(target, path_reviews=[_path()])]})
    run('record', '--labels', target, '--update', reply, '--expected-sha256', result['labels_sha256'])
    frozen = target.parent/'frozen.json'
    run('freeze', '--labels', target, '--output', frozen)
    report = target.parent/'report.json'
    run('evaluate', '--frozen', frozen, '--output', report)
    assert o2.read_json(report)['status'] == 'NOT_EVALUATED'
    moved = tmp_path.parent/(tmp_path.name+' relocated')
    shutil.copytree(tmp_path, moved)
    assert records.status(moved/'재개'/'labels.json')['revision_count'] == 2
    assert o2.load_frozen(moved/'재개'/'frozen.json')[0]['schema_version'] == o2.FREEZE_SCHEMA


def test_migration_reuses_real_bundle_receipt_without_detector_rerun(prepared_o2_review, tmp_path):
    bundle, _, draft, trace_sha = prepared_o2_review
    labels_path = tmp_path/'review'/'labels.json'
    # Simulate pre-upgrade packet/labels while using the real bundle writer/reader.
    draft['schema_version'] = o2.LEGACY_LABEL_SCHEMA
    for case in draft['cases']:
        for a in case['candidates']:
            for key in ('identity', 'artifact_tags', 'artifact_note', 'path_reviews'): a.pop(key)
            a['label'] = 'unreviewed'
    labels_path.write_text(json.dumps(draft), encoding='utf-8')
    video = tmp_path/'source.mp4';video.write_bytes(b'fixture media association')
    link = labels_path.parent/'bundle-link.json'
    records.link_bundle(labels_path, bundle, video, 'reader', 'Fixture association.', link)
    original_link = link.read_bytes()
    target = tmp_path/'converted'/'labels-v2.json';_migrate(labels_path, target)
    assert records.status(target, link)['bundle_link']['locator_exists'] == {'bundle':True, 'video':True}
    assert link.read_bytes() == original_link
    assert o2.sha256_file(bundle/'debug'/'debug_trace.jsonl') == trace_sha


def test_combine_rejects_mixed_versions_but_supports_explicit_v2(migrated, tmp_path):
    source, path = migrated
    with pytest.raises(ValueError, match='mixed label schemas'):
        o2.combine([source, path], 'mixed', tmp_path/'mixed.json')
    out = tmp_path/'combined'/'labels.json'
    o2.combine([path], 'v2-combined', out)
    assert records.status(out)['schema_version'] == o2.LABEL_SCHEMA
    assert o2.freeze(out, tmp_path/'combined-frozen.json')['schema_version'] == o2.FREEZE_SCHEMA


def test_scene_scope_attribution_survives_independent_contour_update(migrated):
    _, path = migrated
    before = o2.read_json(path)['cases'][0]
    visibility_review = copy.deepcopy(before['visibility_review'])
    _record(path, [], contour=[])
    after = o2.read_json(path)['cases'][0]
    assert after['visibility_review'] == visibility_review
    assert after['contour_review']['reviewer'] == 'new reader'
    assert after['candidates'] == before['candidates']


def test_supported_unreviewed_v2_candidate_remains_unverified(migrated):
    _, path = migrated
    _record(path, [_change(path, 2, identity='unreviewed', artifact_tags=[])])
    labels, packets = records._load_labels(path);frozen = _frozen(labels)
    stats = o2.evaluate(frozen, packets, _predictions(frozen))['partitions']['regression']
    assert stats['unverified_support_count'] == 1
    assert stats['verified_identity_precision'] == 1
    assert stats['conservative_supported_precision'] == .5
    assert stats['qualitative_path_review']['supported_proposals']['candidate_count'] == 2
    assert stats['qualitative_path_review']['supported_proposals']['by_geometry_basis']['candidate_center']['unreviewed'] == 10


def test_freeze_and_combine_reuse_cross_drive_locator_fallback(migrated, tmp_path, monkeypatch):
    _, path = migrated
    def different_drives(*args): raise ValueError('different drives')
    monkeypatch.setattr(o2.os.path, 'relpath', different_drives)
    frozen_path = tmp_path/'cross-drive'/'frozen.json'
    frozen = o2.freeze(path, frozen_path)
    assert Path(frozen['packets'][0]['path']).is_absolute()
    assert o2.load_frozen(frozen_path)[0] == frozen
    out = tmp_path/'cross-drive'/'combined.json'
    combined = o2.combine([path], 'combined', out)
    assert Path(combined['combined_sources'][0]['path']) == path.resolve()
    assert combined['combined_sources'][0]['labels_sha256'] == records.status(path)['labels_sha256']
    assert records.status(out)['schema_version'] == o2.LABEL_SCHEMA


def test_fresh_prepare_v2_records_scoped_reply_and_freezes(prepared_o2_review, tmp_path):
    _, _, draft, _ = prepared_o2_review
    path = tmp_path/'review'/'labels.json'
    assert draft['schema_version'] == o2.LABEL_SCHEMA
    assert draft['cases'][0]['candidates']
    a = draft['cases'][0]['candidates'][0]
    out = records.record(path, {'reviewer':'fixture reviewer', 'note':'Constructed frame; no field evidence.',
        'case_id':'actual', 'visibility':'visible',
        'owners': {'label_owner':'fixture', 'split_owner':'fixture', 'split_rationale':'Constructed regression.'},
        'candidates':[{'candidate_input_index':a['candidate_input_index'], 'witness_sha256':a['witness_sha256'],
                       'identity':'interface'}]}, records.status(path)['labels_sha256'])
    assert out['revision_count'] == 1
    assert out['cases'][0]['candidate_reviews'][0]['identity'] == 'interface'
    frozen = o2.freeze(path, tmp_path/'frozen-v2.json')
    assert frozen['schema_version'] == o2.FREEZE_SCHEMA
    loaded, packets = o2.load_frozen(tmp_path/'frozen-v2.json')
    report = o2.evaluate(loaded, packets)
    assert report['status'] == 'NOT_EVALUATED'
    assert report['partitions']['regression']['localization']['all_interface_proposals']['status'] == 'not_measured'
