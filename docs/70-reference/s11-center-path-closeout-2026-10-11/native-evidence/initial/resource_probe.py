"""Descriptive allocation probe; frozen P1 algorithm and inputs remain unchanged."""
from pathlib import Path
import sys, tracemalloc, time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/"scripts"))
import s11_center_path_trial as trial
out=Path(__file__).parent
frozen=trial.load(out/"preflight.json")
readout=trial.load(out/"readout.json")
# Select maximum recorded output count, not a favourable performance example.
index=max(range(len(readout["cases"])),key=lambda i:readout["cases"][i]["records"])
case=frozen["cases"][index]
evidence=Path(sys.argv[1]).resolve()
assert trial.sha(ROOT/trial.SOURCE)==frozen["candidate_source_sha256"]
case,pre,mask,material,profiles=trial.read_case(evidence,case,trial.DetectorSettings())
tracemalloc.start(); start=time.perf_counter()
result=trial.owner.diagnose_center_path_alternatives(profiles)
current,peak=tracemalloc.get_traced_memory(); elapsed=time.perf_counter()-start
tracemalloc.stop()
assert len(result.alternatives)==readout["cases"][index]["records"]
data={"case":case["id"],"scale":case["scale"],"records":len(result.alternatives),
      "allocation_current_bytes":current,"allocation_peak_bytes":peak,"instrumented_seconds":elapsed,
      "peak_live_states":result.peak_live_states,"source_sha256":trial.sha(ROOT/trial.SOURCE),
      "qualification":"Python traced allocations for the largest-record real case; not RSS or a universal worst-case guarantee."}
trial.save(out/"resource.json",data)
print(data)
