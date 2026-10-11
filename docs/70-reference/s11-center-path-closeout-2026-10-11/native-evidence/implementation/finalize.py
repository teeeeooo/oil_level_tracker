from pathlib import Path
import ast, gzip, hashlib, json, subprocess, xml.etree.ElementTree as ET, zipfile
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).parent
EVIDENCE=ROOT.parent/"oil_level_tracker"
BASE="8fea93f2cfa27c455114d0921bbeacb9f697ad13"
SOURCE="src/oil_tracker/adapters/vision/oil_material_path.py"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())
def git(root,*args): return subprocess.check_output(["git","-C",str(root),*args],text=True).strip()
def save(name,data): (OUT/name).write_text(json.dumps(data,indent=2,allow_nan=False)+"\n")
first=ROOT/"sample/output/s11-center-path-20261011-001"
a,b=read(first/"readout.json"),read(OUT/"readout.json")
frozen=read(OUT/"preflight.json")
assert len(a["cases"])==len(b["cases"])==23
replay=[]; support_counts=[]
for left,right in zip(a["cases"],b["cases"]):
    digest=sha(OUT/right["detail_file"])
    assert digest==right["detail_sha256"]==left["detail_sha256"]==sha(first/left["detail_file"])
    detail=json.loads(gzip.decompress((OUT/right["detail_file"]).read_bytes()))
    paths=[r for r in detail["alternatives"] if r["status"]=="PATH"]
    unique={(r["polarity"],tuple(r["profile_indices"]),tuple(r["rows"])) for r in paths}
    replay.append({"id":right["id"],"scale":right["scale"],"sha256":digest,"equal":True})
    support_counts.append({"id":right["id"],"scale":right["scale"],"raw_paths":len(paths),"unique_geometry_paths":len(unique)})
for p,digest in frozen["inputs"].items(): assert sha(EVIDENCE/p)==digest,p
assert git(EVIDENCE,"rev-parse","HEAD")==BASE and git(EVIDENCE,"status","--porcelain")==""
assert git(ROOT,"rev-parse","HEAD")==BASE
original=(EVIDENCE/SOURCE).read_bytes(); candidate=(ROOT/SOURCE).read_bytes()
assert candidate.startswith(original) and sha(ROOT/SOURCE)==frozen["candidate_source_sha256"]
old_nodes=ast.parse(original).body; new_nodes=ast.parse(candidate).body
assert [ast.dump(n) for n in old_nodes]==[ast.dump(n) for n in new_nodes[:len(old_nodes)]]
old_names={n.name for n in old_nodes if hasattr(n,"name")}
assert not old_names.intersection(n.name for n in new_nodes[len(old_nodes):] if hasattr(n,"name"))
x=ET.parse(OUT/"pytest.xml").getroot()
suites=list(x.iter("testsuite"))
tests={k:sum(int(s.attrib[k]) for s in suites) for k in ("tests","failures","errors","skipped")}
new_tests=sum(t.attrib["classname"].endswith("test_center_path_diagnostics") for t in x.iter("testcase"))
assert tests=={"tests":396,"failures":0,"errors":0,"skipped":0} and new_tests==58
tracked=[SOURCE,"docs/20-architecture/s11-interface-observability-witness-architecture.md",
         "docs/30-validation/s11-interface-observability-witness-validation.md","docs/catalog-by-created-date.md"]
untracked=["scripts/s11_center_path_trial.py","tests/test_center_path_diagnostics.py",
           "docs/50-diagnostics/s11/2026-10-11-center-path-preflight.json",
           "docs/50-diagnostics/s11/2026-10-11-center-path-trial.json",
           "docs/60-evidence/s11/2026-10-11-center-path-implementation.md"]
assert set(git(ROOT,"diff","--name-only").splitlines())==set(tracked)
assert set(git(ROOT,"ls-files","--others","--exclude-standard").splitlines())==set(untracked)
git(ROOT,"diff","--check")
command=[str(EVIDENCE/".venv/bin/python"),"scripts/check_detector_governance.py","--base-ref",BASE,"--include-worktree"]
governance=subprocess.check_output(command,cwd=ROOT,text=True)
assert "passed" in governance
(OUT/"governance.log").write_text(governance)
patch=subprocess.check_output(["git","diff","--binary","--no-ext-diff"],cwd=ROOT)
for path in sorted(untracked):
    result=subprocess.run(["git","diff","--no-index","--binary","--no-ext-diff","/dev/null",path],cwd=ROOT,capture_output=True)
    assert result.returncode==1,result.stderr
    patch+=result.stdout
patch_path=OUT/"implementation.patch"; patch_path.write_bytes(patch)
apply_check=git(EVIDENCE,"apply","--check","--whitespace=error-all",str(patch_path))
assert git(EVIDENCE,"status","--porcelain")==""
save("replay-comparison.json",{"exact_matches":23,"cases":replay,"geometry_counts":support_counts})
summary={"schema":"s11-p1-implementation-closeout-v1","date":"2026-10-11","base_head":BASE,
    "candidate_branch":git(ROOT,"branch","--show-current"),"candidate_worktree":str(ROOT),
    "original_worktree":str(EVIDENCE),"original_worktree_clean":True,"committed":False,"pushed":False,
    "source_sha256":sha(ROOT/SOURCE),"baseline_source_sha256":sha(EVIDENCE/SOURCE),
    "old_source_byte_and_AST_prefix_preserved":True,"no_old_name_overrides":True,
    "patch_sha256":sha(patch_path),"patch_applies_cleanly_to_original":True,
    "changed_files":sorted(tracked+untracked),"tests":tests,"new_tests":new_tests,
    "pytest_seconds":sum(float(s.attrib["time"]) for s in suites),
    "fixed_conditions":23,"unique_native_frames":12,"recordings":4,"input_hashes_verified":29,
    "raw_status_records":sum(c["records"] for c in b["cases"]),
    "raw_paths_verified":sum(c["paths_verified"] for c in b["cases"]),
    "unique_geometry_paths":sum(c["unique_geometry_paths"] for c in support_counts),
    "repeat_exact_matches":23,"default_candidate_invariance_cases":23,
    "source_preflight_sha256":sha(OUT/"preflight.json"),"readout_sha256":sha(OUT/"readout.json"),
    "diagnostic_seconds_range_final":[min(c["seconds"] for c in b["cases"]),max(c["seconds"] for c in b["cases"])],
    "runtime":b["runtime"],"resource_measurement":read(first/"resource.json"),
    "governance":"PASS","diff_check":"PASS","sample3_execution":False,"windows_execution":False,
    "new_video_decode":False,"full_sequence_replay":False,"report_efficacy":"NOT_TESTED",
    "disposition":"OFFLINE_IMPLEMENTATION_VERIFIED_NOT_PROMOTED","field_status":"UNCHANGED_O2_OPEN_FIELD_FAIL"}
save("execution-summary.json",summary)
entries={"implementation.patch":patch_path,"execution-summary.json":OUT/"execution-summary.json",
    "preflight.json":OUT/"preflight.json","readout.json":OUT/"readout.json",
    "replay-comparison.json":OUT/"replay-comparison.json","resource.json":first/"resource.json",
    "pytest.log":OUT/"pytest.log","governance.log":OUT/"governance.log"}
entries["implementation-evidence.md"]=ROOT/"docs/60-evidence/s11/2026-10-11-center-path-implementation.md"
entries["s11_center_path_trial.py"]=ROOT/"scripts/s11_center_path_trial.py"
entries["test_center_path_diagnostics.py"]=ROOT/"tests/test_center_path_diagnostics.py"
entries["finalize.py"]=Path(__file__)
checksums="".join(f"{sha(path)}  {name}\n" for name,path in sorted(entries.items()))
archive=OUT/"delivery-payload.zip"
with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for name,path in sorted(entries.items()): z.write(path,name)
    z.writestr("PAYLOAD-SHA256SUMS.txt",checksums)
print(json.dumps(summary,indent=2))
print("DELIVERY",str(archive),archive.stat().st_size,sha(archive))
