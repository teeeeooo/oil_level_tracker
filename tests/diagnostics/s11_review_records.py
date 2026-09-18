"""Durable, work-PC-only O2 records; no detector or physical inference.

The evaluator owns packet/label semantics. This companion owns relocatable bundle
receipts and serialized human edits. It reuses product IO and atomic writing.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict
from datetime import datetime, timezone
import copy
import json
import os
from pathlib import Path

from oil_tracker.adapters.storage.json_recipe_repository import atomic_write_text
from oil_tracker.adapters.storage.result_bundle_reader import ResultBundleReader
from oil_tracker.adapters.storage.debug_trace_repository import DebugTraceRepository
from oil_tracker.application.services.truth_identity import build_truth_bundle_identity
from tests.diagnostics import s11_interface_shadow_evaluation as o2

LINK_SCHEMA = 's11-o2-bundle-link-v1'


def _now():
    return datetime.now(timezone.utc).isoformat()


def _relative(target, parent):
    # relpath raises on different Windows drives. Absolute locators remain usable;
    # content identities never include either form of the locator.
    try:
        return Path(os.path.relpath(Path(target).resolve(), Path(parent).resolve())).as_posix()
    except ValueError:
        return str(Path(target).resolve())


def _load_labels(path):
    path = Path(path)
    labels = o2.read_json(path)
    packets = o2.load_packets(labels, path.parent)
    o2.validate_labels(labels, packets, allow_pending=True)
    return labels, packets


@contextmanager
def _lock(path):
    lock = Path(str(path) + '.lock')
    try:
        handle = lock.open('x', encoding='utf-8')
    except FileExistsError:
        raise ValueError(f'writer lock exists: {lock}; verify no writer is running before removing a stale lock') from None
    try:
        with handle:
            handle.write(f'pid={os.getpid()}\n')
            handle.flush()
            os.fsync(handle.fileno())
        yield
    finally:
        lock.unlink()


def _replace_with_history(path, before, after):
    """Caller holds lock. Archive before replace; interruption leaves old or new JSON."""
    path = Path(path)
    payload = json.dumps(after, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
    o2.require(len(payload.encode('utf-8')) <= 128 * 1024**2, 'review exceeds 128 MiB; start a new bounded review')
    digest = o2.fingerprint_json(before)
    history = path.parent / (path.name + '.history') / (digest + '.json')
    if history.exists():
        o2.require(o2.fingerprint_json(o2.read_json(history)) == digest, 'history snapshot mismatch')
    else:
        atomic_write_text(history, json.dumps(before, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    atomic_write_text(path, payload)


def _bundle_identity(bundle):
    o2.require(bundle.debug_trace_path is not None and bundle.debug_index_path is not None, 'indexed debug trace required')
    return {'run_id': bundle.run_id,
            'files': {name: o2.sha256_file(path) for name, path in {
                'manifest': bundle.files['manifest'], 'recipe': bundle.files['recipe_snapshot'],
                'session': bundle.files['session'], 'trace': Path(bundle.root) / bundle.debug_trace_path,
                'trace_index': Path(bundle.root) / bundle.debug_index_path}.items()},
            'truth_identity': asdict(build_truth_bundle_identity(bundle))}


def _verify_packets(bundle, labels, label_dir):
    """Compare actual indexed witnesses, not just manifest strings or run names."""
    repo = DebugTraceRepository(bundle, record_cache_size=1)
    frames = []
    try:
        for ref in labels['packets']:
            packet = o2.read_json(Path(label_dir) / ref['path'])
            o2.require(packet.get('manifest_sha256') == o2.sha256_file(bundle.files['manifest']) and
                       packet.get('recipe_sha256') == o2.sha256_file(bundle.files['recipe_snapshot']),
                       'packet belongs to a different bundle; link each review before combining')
            for frame in packet['frames']:
                o2.require(frame['run_id'] == bundle.run_id, 'packet run mismatch')
                actual = o2.extract_frame(repo.load_record(frame['record_id']), frame['case_id'])
                o2.require(actual == frame, 'packet/trace record mismatch')
                frames.append(frame)
    finally:
        repo.close()
    return frames


def link_bundle(labels_path, bundle_path, video_path, reviewer, note, output):
    labels_path, output, video_path = Path(labels_path), Path(output), Path(video_path)
    o2.require(not output.exists(), 'link output already exists; use relink for relocation')
    o2.text(reviewer, 'reviewer'); o2.text(note, 'source attestation note')
    labels, _ = _load_labels(labels_path)
    bundle = ResultBundleReader().read(bundle_path)
    root = Path(bundle.root).resolve()
    o2.require(output.resolve() != root and root not in output.resolve().parents, 'link must be outside bundle')
    identity = _bundle_identity(bundle)
    frames = _verify_packets(bundle, labels, labels_path.parent)
    # Hash binds selected bytes. The reviewer attests they are the source of this
    # older bundle; an old filename or absent source hash cannot prove that.
    video_sha = o2.sha256_file(video_path)
    geometry = {g['id']: g['geometry'] for g in bundle.recipe.to_dict()['glasses']}
    coordinate_frame = {'width': identity['truth_identity']['source_width'],
                        'height': identity['truth_identity']['source_height'],
                        'coordinate_space': 'source_frame_y', 'positive_direction': 'down'}
    scenes = []
    for frame in frames:
        key = {'video_sha256': video_sha, 'frame_index': frame['frame_index'],
               'coordinate_frame': coordinate_frame, 'glass_geometry': geometry[frame['glass_id']]}
        scenes.append({'case_id': frame['case_id'], 'glass_id': frame['glass_id'],
                       'scene_identity': key, 'scene_sha256': o2.fingerprint_json(key)})
    link = {'schema_version': LINK_SCHEMA, 'bundle_identity': identity,
            'packet_sha256s': [p['sha256'] for p in labels['packets']],
            'source': {'sha256': video_sha, 'association_basis': 'human_attestation',
                       'reviewer': reviewer, 'note': note},
            'scenes': scenes}
    link['identity_sha256'] = o2.fingerprint_json(link)
    link['locators'] = {'bundle': _relative(bundle.root, output.parent), 'video': _relative(video_path, output.parent)}
    link['history'] = [{'action': 'register', 'at': _now(), 'reviewer': reviewer, 'note': note}]
    o2.write_new(output, link)
    return {'link': str(output), 'identity_sha256': link['identity_sha256'], 'scene_count': len(scenes)}


def load_link(path):
    link = o2.read_json(path)
    o2.require(link.get('schema_version') == LINK_SCHEMA, 'unsupported bundle link schema')
    identity = {k: v for k, v in link.items() if k not in ('identity_sha256', 'locators', 'history')}
    o2.require(o2.fingerprint_json(identity) == link['identity_sha256'], 'bundle link identity mismatch')
    return link


def relink(link_path, bundle_path, video_path, reviewer, note):
    path = Path(link_path)
    o2.text(reviewer, 'reviewer'); o2.text(note, 'note')
    with _lock(path):
        link = load_link(path)
        bundle = ResultBundleReader().read(bundle_path)
        o2.require(_bundle_identity(bundle) == link['bundle_identity'], 'different bundle or changed bundle content')
        o2.require(o2.sha256_file(video_path) == link['source']['sha256'], 'different source video bytes')
        updated = copy.deepcopy(link)
        updated['locators'] = {'bundle': _relative(bundle.root, path.parent), 'video': _relative(video_path, path.parent)}
        updated['history'].append({'action': 'relink', 'at': _now(), 'reviewer': reviewer, 'note': note,
                                   'previous_locators': link['locators']})
        _replace_with_history(path, link, updated)
    return {'identity_sha256': updated['identity_sha256'], 'locators': updated['locators']}


def status(labels_path, link_path=None):
    labels, _ = _load_labels(labels_path)
    rows = []
    for c in labels['cases']:
        rows.append({'case_id': c['case_id'], 'visibility': c['visibility'],
                     'reviewer': c['reviewer'],
                     'unreviewed_candidate_ids': [a['candidate_input_index'] for a in c['candidates'] if a['label'] == 'unreviewed'],
                     'unresolved_candidate_ids': [a['candidate_input_index'] for a in c['candidates'] if a['label'] == 'unresolved']})
    report = {'labels_sha256': o2.fingerprint_json(labels),
              'revision_count': len(labels.get('review_history', [])),
              'missing_owners': [k for k in ('label_owner', 'split_owner', 'split_rationale') if not labels[k].strip()],
              'cases': rows, 'bundle_link': 'not_checked', 'classifier_status': 'NOT_EVALUATED'}
    if link_path is not None:
        link = load_link(link_path)
        o2.require(set(link['packet_sha256s']) == {p['sha256'] for p in labels['packets']}, 'link/packet mismatch')
        report['bundle_link'] = {'identity_sha256': link['identity_sha256'],
                                 'association_basis': link['source']['association_basis'],
                                 'locator_exists': {k: (Path(link_path).parent / p).exists() for k, p in link['locators'].items()},
                                 'live_content_rehashed': False}
    return report


def record(labels_path, update, expected_sha256):
    """One human reply per transaction; frozen files are never edited."""
    path = Path(labels_path)
    with _lock(path):
        before, packets = _load_labels(path)
        o2.require(o2.fingerprint_json(before) == expected_sha256, 'stale labels revision; run status again')
        allowed = {'reviewer', 'note', 'owners', 'case_id', 'visibility', 'contour', 'candidates'}
        o2.require(set(update) <= allowed, 'unsupported update fields')
        reviewer, note = o2.text(update['reviewer'], 'reviewer'), o2.text(update['note'], 'note')
        after = copy.deepcopy(before)
        owners = update.get('owners', {})
        o2.require(isinstance(owners, dict) and set(owners) <= {'label_owner', 'split_owner', 'split_rationale'}, 'unsupported owner fields')
        for k, v in owners.items():
            after[k] = o2.text(v, k)
        case_fields = {'visibility', 'contour', 'candidates'} & set(update)
        o2.require(bool(owners or case_fields), 'empty review update')
        if case_fields:
            cases = o2.unique(after['cases'], 'case_id', 'cases')
            case = cases[update['case_id']]
            if 'scene_review' not in case and case['visibility'] != 'pending':
                # Preserve existing v1 scene attribution before a candidate-only
                # reply changes the legacy case-wide reviewer/note fields.
                case['scene_review'] = {'reviewer': case['reviewer'], 'note': case['review_note'],
                                        'at': None, 'basis': 'legacy_v1_case'}
            case.update(reviewer=reviewer, review_note=note)
            for k in ('visibility', 'contour'):
                if k in update:
                    case[k] = copy.deepcopy(update[k])
            if {'visibility', 'contour'} & set(update):
                case['scene_review'] = {'reviewer': reviewer, 'note': note, 'at': _now()}
            candidates = o2.unique(case['candidates'], 'candidate_input_index', 'candidates')
            changes = o2.unique(update.get('candidates', []), 'candidate_input_index', 'candidate updates')
            for i, change in changes.items():
                o2.integer(i, 'candidate_input_index')
                o2.require(set(change) <= {'candidate_input_index', 'witness_sha256', 'label', 'entity_id'}, 'unsupported candidate update')
                a = candidates[i]
                o2.require(change['witness_sha256'] == a['witness_sha256'], 'candidate witness mismatch')
                a['label'] = change['label']
                if 'entity_id' in change:
                    a['entity_id'] = change['entity_id']
                a.update(reviewer=reviewer, review_note=note)
        o2.validate_labels(after, packets, allow_pending=True)
        after.setdefault('review_history', []).append({'at': _now(), 'previous_sha256': expected_sha256,
                                                       'update': copy.deepcopy(update)})
        _replace_with_history(path, before, after)
    return status(path)


def add_commands(commands):
    p = commands.add_parser('link-bundle', help='register exact bundle and human-attested source video for a review')
    p.add_argument('--labels', type=Path, required=True)
    p.add_argument('--bundle', type=Path, required=True)
    p.add_argument('--video', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--reviewer', required=True); p.add_argument('--note', required=True)
    p = commands.add_parser('relink', help='verify content before replacing moved bundle/video locators')
    p.add_argument('--link', type=Path, required=True)
    p.add_argument('--bundle', type=Path, required=True)
    p.add_argument('--video', type=Path, required=True)
    p.add_argument('--reviewer', required=True); p.add_argument('--note', required=True)
    p = commands.add_parser('status', help='resume pending review; JSON on stdout')
    p.add_argument('--labels', type=Path, required=True)
    p.add_argument('--link', type=Path)
    p = commands.add_parser('record', help='validate and atomically save one human reply with history')
    p.add_argument('--labels', type=Path, required=True)
    p.add_argument('--update', type=Path, required=True)
    p.add_argument('--expected-sha256', required=True)


def dispatch(args):
    if args.command == 'link-bundle':
        return link_bundle(args.labels, args.bundle, args.video, args.reviewer, args.note, args.output)
    if args.command == 'relink':
        return relink(args.link, args.bundle, args.video, args.reviewer, args.note)
    if args.command == 'status':
        return status(args.labels, args.link)
    return record(args.labels, o2.read_json(args.update), args.expected_sha256)
