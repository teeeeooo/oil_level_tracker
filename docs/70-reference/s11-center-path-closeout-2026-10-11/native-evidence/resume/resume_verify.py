"""Read-only resume verification of the existing, uncommitted P1 candidate."""
from pathlib import Path
import ast, hashlib, json, os, subprocess, sys, time
import xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent
OLD = ROOT / 'sample/output/s11-center-path-20261011-002'
MAIN = ROOT.parent / 'oil_level_tracker'
BASE = '8fea93f2cfa27c455114d0921bbeacb9f697ad13'
SOURCE = 'src/oil_tracker/adapters/vision/oil_material_path.py'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text())
def git(root, *args):
    return subprocess.check_output(['git','-C',str(root),*args], text=True).strip()
def save(name, data):
    (OUT/name).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
summary = load(OLD/'execution-summary.json')
assert git(MAIN,'rev-parse','HEAD') == git(ROOT,'rev-parse','HEAD') == BASE
assert git(MAIN,'status','--porcelain') == ''
changed = sorted(set(git(ROOT,'diff','--name-only').splitlines()) |
                 set(git(ROOT,'ls-files','--others','--exclude-standard').splitlines()))
assert changed == summary['changed_files']
before = {p:sha(ROOT/p) for p in changed}
assert before[SOURCE] == summary['source_sha256']
save('before.json', {'base':BASE,'candidate_files':before,'main_clean':True})
print('RESUMED exact candidate:',before[SOURCE],flush=True)
env = dict(os.environ, PYTHONPATH=str(ROOT/'src')+os.pathsep+str(ROOT),
           QT_QPA_PLATFORM='offscreen',PYTHONHASHSEED='0')
python = str(MAIN/'.venv/bin/python')
tree = ET.parse(OLD/'pytest.xml')
paths = sorted({t.attrib['classname'].replace('.','/')+'.py' for t in tree.iter('testcase')})
commands = []
def execute(label, command, timeout=180):
    start=time.perf_counter()
    with (OUT/(label+'.log')).open('w') as log:
        result=subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=timeout)
    record={'label':label,'command':command,'returncode':result.returncode,'seconds':time.perf_counter()-start}
    commands.append(record); print(label,record['returncode'],round(record['seconds'],3),flush=True)
    assert result.returncode == 0,(label,(OUT/(label+'.log')).read_text()[-4000:])
execute('pytest',[python,'-m','pytest','-q',*paths,'--junitxml',str(OUT/'pytest.xml')])
x=ET.parse(OUT/'pytest.xml')
counts={k:sum(int(s.attrib[k]) for s in x.iter('testsuite')) for k in ('tests','failures','errors','skipped')}
assert counts == summary['tests']
replay=OUT/'replay'
execute('prepare',[python,'scripts/s11_center_path_trial.py','prepare','--evidence-root',str(MAIN),'--out',str(replay)])
execute('replay',[python,'scripts/s11_center_path_trial.py','run','--evidence-root',str(MAIN),'--out',str(replay)])
old,new=load(OLD/'readout.json'),load(replay/'readout.json')
assert len(old['cases'])==len(new['cases'])==23
matches=[]
for a,b in zip(old['cases'],new['cases']):
    assert (a['id'],a['scale']) == (b['id'],b['scale'])
    digest=sha(replay/b['detail_file'])
    assert digest==a['detail_sha256']==b['detail_sha256']==sha(OLD/a['detail_file'])
    matches.append({'id':b['id'],'scale':b['scale'],'sha256':digest,'equal':True})
frozen=load(replay/'preflight.json')
for p,digest in frozen['inputs'].items(): assert sha(MAIN/p)==digest,p
original=(MAIN/SOURCE).read_bytes(); candidate=(ROOT/SOURCE).read_bytes()
old_nodes=ast.parse(original).body; new_nodes=ast.parse(candidate).body
assert candidate.startswith(original)
assert [ast.dump(n) for n in old_nodes]==[ast.dump(n) for n in new_nodes[:len(old_nodes)]]
old_names={n.name for n in old_nodes if hasattr(n,'name')}
assert not old_names.intersection(n.name for n in new_nodes[len(old_nodes):] if hasattr(n,'name'))
execute('governance',[python,'scripts/check_detector_governance.py','--base-ref',BASE,'--include-worktree'])
execute('diff-check',['git','diff','--check'])
execute('patch-apply-check',['git','-C',str(MAIN),'apply','--check','--whitespace=error-all',str(OLD/'implementation.patch')])
assert sha(OLD/'implementation.patch')==summary['patch_sha256']
assert before=={p:sha(ROOT/p) for p in changed}
assert git(MAIN,'status','--porcelain') == ''
assert git(MAIN,'rev-parse','HEAD') == git(ROOT,'rev-parse','HEAD') == BASE
result={'schema':'s11-p1-resume-verification-v1','date':'2026-10-11','base_head':BASE,
 'branch':git(ROOT,'branch','--show-current'),'worktree':str(ROOT),'tests':counts,
 'test_files':paths,'candidate_files':before,'source_unchanged_during_resume':True,
 'main_clean':True,'committed':False,'pushed':False,'merged':False,
 'input_hashes_matched':len(frozen['inputs']),'raw_capture_matches':matches,
 'old_source_byte_and_AST_prefix_preserved':True,'no_old_name_overrides':True,
 'patch_sha256':sha(OLD/'implementation.patch'),'patch_applies_cleanly':True,
 'raw_status_records':sum(c['records'] for c in new['cases']),
 'raw_paths_verified':sum(c['paths_verified'] for c in new['cases']),
 'commands':commands,'full_sequence_replay':False,'video_decode':False,
 'sample3_execution':False,'windows_execution':False,'report_efficacy':'NOT_TESTED',
 'disposition':'OFFLINE_IMPLEMENTATION_REVERIFIED_NOT_PROMOTED'}
save('resume-verification.json',result)
print(json.dumps({k:result[k] for k in ('tests','input_hashes_matched','raw_status_records','raw_paths_verified','disposition')},indent=2))
