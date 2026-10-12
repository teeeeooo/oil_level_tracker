"""Audit retained CR-1 inputs and reference precision, without scoring pixels.

Reuse the frozen candidate inventory owner. This is a saved-record audit, not a
reference selector, model adapter, new truth packet or replay of a closed pilot.
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import importlib.util
import json
import platform
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
DIAG = ROOT / 'docs/50-diagnostics/s11'
CLEANUP = ROOT / 'docs/60-evidence/s11/2026-10-12-pre-cr1-cleanup'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def check_pins(pins):
    for relative, digest in pins.items():
        path = ROOT / relative
        if not path.is_file() or sha(path) != digest:
            raise ValueError('missing or changed input: ' + relative)
    return len(pins)


def audit():
    preflight = read(HERE / 'preflight.json')
    check_pins(preflight['inputs'])
    receipt = read(CLEANUP / 'receipt.json')
    retention = read(CLEANUP / 'retention.json')
    inventory = json.loads(gzip.decompress((CLEANUP / 'inventory.json.gz').read_bytes()))
    protection = {
        'retained_files_verified': check_pins({r['path']: r['sha256'] for r in retention['retained']}),
        'protected_pins_verified': check_pins(receipt['preservation']['protected_pin_map']),
        'original_media_hashes_verified_without_decode': check_pins({r['path']: r['sha256'] for r in inventory['media']}),
        'production_pins_verified': sum(p.startswith('src/') for p in receipt['preservation']['protected_pin_map']),
        'historical_recovery_checks': 'REUSED retirement receipt; not rerun and no retired payload requested',
    }

    owner_path = DIAG / '2026-10-12-p2-row-distributions/candidates.py'
    spec = importlib.util.spec_from_file_location('saved_candidate_inventory', owner_path)
    owner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(owner)
    original = read(DIAG / '2026-10-11-p2-shared-support/preflight.json')
    queries, captures = owner.inventory(original)
    frozen = read(DIAG / '2026-10-12-p2-row-distributions/candidates-preflight.json')
    if queries != frozen['queries'] or captures != frozen['captures']:
        raise ValueError('existing complete candidate inventory changed')

    controls = read(DIAG / '2026-10-07-sample4-a2-control-preflight.json')
    reviewed = []
    for row in controls['rows']:
        record = read(ROOT / original['images'][str(row['frame'])]['capture'])
        candidate = record['current']['candidates'][row['candidate_input_index']]
        if (candidate['source'], candidate['y']) != (row['source'], row['source_y']):
            raise ValueError('reviewed candidate binding changed')
        reviewed.append({k: row[k] for k in (
            'frame', 'candidate_input_index', 'source', 'source_y', 'target_role',
            'native_path_review_status', 'lineage_status'
        )} | {'native_sector_count': len(row['native_sectors'])})

    public = read(DIAG / '2026-10-12-public-compressor-source/position-review/position-join.json')
    public_review = read(DIAG / '2026-10-12-public-compressor-source/position-review/position-review.json')
    foam_review = read(DIAG / '2026-10-11-foam-upper-position-reply.json')
    roster = read(DIAG / '2026-10-12-scene-evaluation-roster.json')
    result = {
        'schema': 's11-cr1-reference-readiness-audit-v1',
        'execution_head': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
        'preflight_sha256': sha(HERE / 'preflight.json'),
        'runner_sha256': sha(Path(__file__)),
        'runtime': {'python': platform.python_version(), 'platform': platform.platform()},
        'protection': protection,
        'candidate_inventory': {
            'owner': str(owner_path.relative_to(ROOT)),
            'captures': captures,
            'candidate_count': sum(r['count'] for r in captures),
            'context_only_controls': sum('candidate_index' not in q for q in queries),
            'total_records': len(queries),
            'reviewed_positive_count': sum(q['label'] == 'confirmed_target' for q in queries),
            'reviewed_wrong_target_count': sum(q['label'] == 'rejected_target' for q in queries),
            'unreviewed_candidate_count': sum(q['label'] == 'UNREVIEWED' for q in queries),
            'query_ids': [q['id'] for q in queries],
            'scores': 'NOT_RUN',
        },
        'reviewed_candidate_geometry': reviewed,
        'existing_regional_references': original['references'],
        'sample4_foam_position': {
            'references': foam_review['reviewed_references'],
            'scope_verbatim': foam_review['scope'],
            'interpretation_verbatim': foam_review['interpretation'],
        },
        'public_compressor_position': {
            'join_owner': 'docs/50-diagnostics/s11/2026-10-12-public-compressor-source/position-review/position-join.json',
            'frame': public_review['frame_index'],
            'source_x': public_review['source_x'],
            'reviewed_ranges': public_review['proposed_ranges'],
            'observed_center_edge_alternatives': public['range_canny_rows'],
            'isolated_current_frame_candidates': len(public['candidates']),
            'certified_candidate_contours': sum(c['certified_fixed_column_physical_contour'] for c in public['candidates']),
            'scope_verbatim': public_review['scope'],
            'limits': 'Isolated-frame join only; its indices are not substituted for the later application-pipeline inventory.',
        },
        'p0_retained': {
            'coverage': roster['coverage'],
            'unit_ids': [u['id'] for u in roster['units']],
            'sample3': 'HASH_ONLY_NO_DECODE_NO_SCORING',
            'windows': 'NOT_RUN',
        },
        'readiness': preflight['readiness'],
        'interpretation': preflight['interpretation'],
        'model_installed': False,
        'model_downloaded': False,
        'inference_performed': False,
        'production_changed': False,
        'physical_acceptance': 'NOT_EVALUATED',
    }
    # Counts are frozen inventory assertions, never an efficacy denominator.
    assert result['candidate_inventory']['candidate_count'] == 160
    assert result['candidate_inventory']['total_records'] == 164
    assert len(reviewed) == 10
    assert len(result['p0_retained']['unit_ids']) == 25
    check_pins(preflight['inputs'])
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    result = audit()
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'protection': result['protection'], 'readiness': result['readiness']}, ensure_ascii=False))
