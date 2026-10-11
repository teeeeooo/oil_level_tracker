"""Read-only S11 program audit; writes only to its own ignored output directory."""
from pathlib import Path
import collections, hashlib, json, subprocess, sys
ROOT = Path('/Users/sunjaekim/Developer/oil_level_tracker')
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from tests.diagnostics.s11_corpus_access import require_corpus_access

def sha(path):
    return hashlib.file_digest(Path(path).open('rb'), 'sha256').hexdigest()
def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True).strip()
def inspect_tree(value, prefix='', depth=0):
    if depth > 2:
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if any(word in key.lower() for word in ['script', 'code', 'runner', 'verifier']):
                continue
            print(prefix + str(key), type(item).__name__, len(item) if isinstance(item, (dict,list,str)) else item)
            if isinstance(item, dict):
                inspect_tree(item, prefix + str(key) + '.', depth + 1)
tracked = git('ls-files').splitlines()
record = {'head': git('rev-parse','HEAD'), 'status_before': git('status','--short')}
record['tracked_counts'] = {kind: sum(p.startswith(kind + '/') for p in tracked) for kind in ['src','tests','docs']}
record['tracked_total'] = len(tracked)
record['src_diff_since_cc17924'] = git('diff','--name-only','cc17924','HEAD','--','src')
record['source_pins'] = {p: sha(ROOT/p) for p in tracked if p.startswith('src/')}
record['media_pins'] = {str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT/'sample').glob('*.mp4'))}
record['protected_pins'] = {str(p.relative_to(ROOT)): sha(p) for pattern in ['*.oilrecipe','*.oiltruth'] for p in sorted((ROOT/'sample').glob(pattern))}
files = [
 '2026-10-10-b-material-path-interval.json',
 '2026-10-10-abc-source-interval-comparison.json',
 '2026-10-10-water-foam-representation.json',
 '2026-10-10-sample4-center-interval-comparison.json',
 '2026-10-10-current-boundary-reference/preflight.json',
 '2026-10-09-public-scene-controls.json',
]
checks = {}
def scan_pins(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(item, str) and len(item)==64 and all(c in '0123456789abcdef' for c in item) and '/' in key:
                p = Path(key) if key.startswith('/') else ROOT/key
                checks[(str(p),item)] = {'exists': p.is_file(), 'matches': p.is_file() and sha(p)==item}
            elif isinstance(item, (dict,list)):
                scan_pins(item)
        if isinstance(value.get('path'),str) and isinstance(value.get('sha256'),str):
            p = Path(value['path']) if value['path'].startswith('/') else ROOT/value['path']
            h = value['sha256']
            checks[(str(p),h)] = {'exists':p.is_file(),'matches':p.is_file() and sha(p)==h}
    elif isinstance(value, list):
        for item in value:
            scan_pins(item)
for name in files:
    p = ROOT/'docs/50-diagnostics/s11'/name
    value = json.loads(p.read_text())
    print('\nRECORD',name)
    inspect_tree(value)
    scan_pins(value)
record['pin_checks'] = [{'path':p,'expected_sha256':h,**result} for (p,h),result in checks.items()]
record['pin_summary'] = {'total':len(checks),'match':sum(v['matches'] for v in checks.values()),'missing':sum(not v['exists'] for v in checks.values())}
record['pin_summary']['mismatches'] = [p for (p,h),v in checks.items() if v['exists'] and not v['matches']]
record['status_after'] = git('status','--short')
(OUT/'audit_identity.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('\nAUDIT SUMMARY',json.dumps({k:v for k,v in record.items() if k not in ['source_pins','media_pins','protected_pins','pin_checks']},ensure_ascii=False))
print('FOCUSED TEST PATHS')
for p in (ROOT/'tests').rglob('test_*.py'):
    if any(s in p.name for s in ['observation_cadence','material_path','foam_support_geometry','boundary_temporal','local_xy','contour_contact','replacement_compare']):
        print(p.relative_to(ROOT))
