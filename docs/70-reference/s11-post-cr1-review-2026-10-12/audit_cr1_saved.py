"""Read-only S11 saved-evidence audit. No encoder, detector, or policy execution.
Run with the repository's existing virtual environment; JSON is printed to stdout.
Any persisted replay output must follow the repository's artifact lifecycle.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
CR = Path('docs/50-diagnostics/s11/2026-10-12-cr1-context-comparison')
BUNDLE = Path('sample/output/s11-p5-default-linkage-20261011-001/none/'
              'oil_level_analysis_Local_XY_fixed_comparison_sample4_20261011_224401')

def read_json(path: Path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)

def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'Cannot load {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(root: Path, verify_video: bool = False) -> dict:
    if not __debug__:
        raise RuntimeError('Run without -O: the original verifier uses assertions.')
    root = root.resolve(strict=True)
    sys.path[:0] = [str(root / 'src'), str(root)]
    verifier = load_module('post_cr1_original_verifier', root / CR / 'verify_followup.py')
    verified = verifier.verify(root / CR / 'followup-readout.json.gz')
    data = read_json(root / CR / 'followup-readout.json.gz')
    rows = data['results']
    known = [r for r in rows if r['query']['label'] in ('confirmed_target', 'rejected_target')
             and r['exposure'] != 'reference_self_support']
    pair = lambda r: tuple(r['measurement']['regional_context_preference'][m] for m in ('full', 'local'))
    groups = defaultdict(Counter)
    for r in known:
        groups[pair(r)][r['query']['label']] += 1
    ranges = {}
    for mode in ('full', 'local'):
        ranges[mode] = {}
        for label in ('confirmed_target', 'rejected_target'):
            values = [v['modes'][mode]['scores']['interface'] for r in known
                      if r['query']['label'] == label for v in r['measurement']['variants']]
            ranges[mode][label] = [min(values), max(values)]
    competition = []
    for frame in data['summary']['frames']:
        population = [r for r in rows if r['query']['frame'] == frame['frame']
                      and 'candidate_index' in r['query']
                      and all(v['modes'] for v in r['measurement']['variants'])]
        record = {'time_sec': frame['time_sec'], 'modes': {}}
        for mode in ('full', 'local'):
            values = [(min(v['modes'][mode]['scores']['interface'] for v in r['measurement']['variants']), r)
                      for r in population]
            best = max(value for value, _ in values)
            record['modes'][mode] = {
                'maxima': [{'id': r['query']['id'], 'y': r['query']['source_xy'][1],
                            'label': r['query']['label'], 'score': value}
                           for value, r in values if abs(value-best) <= 1e-6],
                'known_targets': [{'id': r['query']['id'], 'score': value,
                    'record_rank': 1+sum(other > value+1e-6 for other, _ in values)}
                    for value, r in values if r['query']['label'] == 'confirmed_target']}
        competition.append(record)
    controls = [{'id': r['query']['id'], 'label': r['query']['label'], 'exposure': r['exposure'],
                 'variants': [{m: v['modes'][m] for m in ('full','local')} for v in r['measurement']['variants']]}
                for r in rows if r['query']['label'] not in ('UNREVIEWED','confirmed_target','rejected_target')]
    with (root / BUNDLE / 'tracking_data.csv').open(encoding='utf-8-sig', newline='') as stream:
        tracking = list(csv.DictReader(stream))
    with (root / BUNDLE / 'events.csv').open(encoding='utf-8-sig', newline='') as stream:
        events = list(csv.DictReader(stream))
    from tests.diagnostics.s11_observation_cadence import summarize_rows
    cadence = summarize_rows(tracking)[0]
    brief_cadence = {k: v for k, v in cadence.items() if k not in ('observations', 'intervals')}
    brief_cadence['over_one_second_pairs'] = [r for r in cadence['intervals'] if r['elapsed_sec'] > 1.0]
    result = {
        'schema': 's11-post-cr1-saved-evidence-audit-v1',
        'head': subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'], text=True).strip(),
        'original_verifier': verified, 'denominators': data['denominators'],
        'joint_preferences': [{'full': k[0], 'local': k[1], 'count': n} for k,n in Counter(map(pair, rows)).items()],
        'known_nonself_signature_labels': [{'full': k[0], 'local': k[1], 'labels': dict(v)} for k,v in groups.items()],
        'categorical_information_bound': {
            'known_nonself_records': len(known),
            'max_zero_error_decided_records': sum(sum(v.values()) for v in groups.values() if len(v)==1),
            'minimum_binary_errors': sum(min(v.values()) for v in groups.values() if len(v)>1),
            'scope': 'Observed full/local categorical signatures only; not an accuracy estimate or a deployment rule.'},
        'interface_similarity_ranges': ranges, 'all_candidate_score_competition': competition,
        'additional_context_controls': controls, 'tracking_rows': len(tracking), 'event_rows': len(events),
        'foam_valid_numeric_rows': sum(r['foam_is_valid']=='True' and bool(r['raw_foam_front_y']) for r in tracking),
        'numeric_cadence_not_physical': brief_cadence,
        'extrema_events': [e for e in events if e['event_type'] in ('MINIMUM_OIL_LEVEL','MAXIMUM_OIL_LEVEL')],
        'hashes': {str(p): digest(root/p) for p in (CR/'followup-readout.json.gz', CR/'followup-preflight.json',
                                                  BUNDLE/'tracking_data.csv', BUNDLE/'events.csv')},
        'encoder_rerun': False, 'detector_rerun': False, 'production_changed': False,
        'physical_acceptance': 'NOT_EVALUATED', 'threshold_selected': False,
        'ranking_scope': 'Diagnostic order by conservative floor/ceil minimum; no label transfer, no selector.'}
    if verify_video:
        result['source_decode_checks'] = decode_sources(root)
    return result

def decode_sources(root: Path) -> dict:
    import cv2
    import numpy as np
    from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
    from tests.diagnostics.s11_corpus_access import require_corpus_access
    require_corpus_access(('sample4','public_miso_mHOS1-1ck60'))
    expected = {'sample/sample4.mp4': 'ee971b3871d806ff194117eb64960cca3ad158e8ae3d1be4097ebc20fe472892',
                'sample/public_miso_mHOS1-1ck60.mp4': '68ead21680534b7bbc06de9b556f5d3a2c4576dd7eaa85c6d50b90534daecc15'}
    for rel, wanted in expected.items():
        if digest(root/rel) != wanted:
            raise ValueError(f'Source identity mismatch: {rel}')
    prepared = read_json(root/'sample/output/s11-cr1-workspace/runs/readiness-20261012-001/evidence/prepared.json')
    checks = []
    with OpenCvVideoReader(root/'sample/sample4.mp4') as reader:
        for f, rel in sorted(prepared['images'].items(), key=lambda item:int(item[0])):
            image, index, pts = reader.read_at(int(f)/30.0)
            equal = index == int(f) and np.array_equal(image[798:902,543:647], cv2.imread(str(root/rel)))
            if not equal:
                raise ValueError(f'Saved/native sample4 raster mismatch: {f}')
            checks.append({'frame':int(f),'actual_index':index,'pts':pts,'equal':True})
    with OpenCvVideoReader(root/'sample/public_miso_mHOS1-1ck60.mp4') as reader:
        image,index,pts = reader.read_at(50.0)
        equal = np.array_equal(image,cv2.imread(str(root/'docs/50-diagnostics/s11/2026-10-12-public-compressor-source/native-at-50.png')))
        if index != 1499 or not equal:
            raise ValueError('Saved/native public raster mismatch')
    return {'sample4':checks,'public':{'actual_index':index,'pts':pts,'equal':True},'sample3_decoded':False}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--verify-video', action='store_true')
    args = parser.parse_args()
    print(json.dumps(run(args.root,args.verify_video), ensure_ascii=False, indent=2, allow_nan=False))
