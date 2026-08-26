# S11-R18 Causal Trace Observability Evidence

**Status:** `LOCAL PASS — WINDOWS SAME-VIDEO RERUN PENDING`

## Implemented scope

This change adds only completed-trace causal diagnostics:

- ordered initial-FULL and partial-fill drain-release predicates, policy/input
  values, established-fill snapshot, qualifying/selected IDs and ambiguity;
- current Foam eligibility gate results and failed-gate names;
- Foam trace-only track/segment identity, alias result, segment acceptance and
  directed/stable formation predicates; and
- JSONL sequence serialization for the nested diagnostic dictionaries.

No detector policy, threshold, Recipe, candidate authority, tracklet,
lifecycle transition, selector, projection, CSV, graph, event, or UI behavior
was changed. The existing completed-window fingerprint constant remains
unchanged; additive diagnostic keys are tested separately and excluded from
the behavior fingerprint payload.

## Local verification

| Check | Result |
|---|---|
| Python compilation | PASS — `python3 -m compileall -q src` |
| Focused Oil/Foam/trace/integration tests | PASS — 115 |
| Completed-window behavior fingerprint | PASS — existing R18 constant unchanged |
| Full repository regression | PASS — 1,672 |
| Whitespace validation | PASS — `git diff --check` |
| Detector governance | PASS — `python3 scripts/check_detector_governance.py --base-ref HEAD --include-worktree` |

The first unqualified system-Python full-suite attempt stopped at collection
because `jinja2` was not installed in that interpreter. The authoritative full
run used the repository `.venv`, which contains the declared dependencies and
completed with 1,672 passing tests.

## Remaining gate

This local pass does not qualify detector effectiveness. Windows must run the
same private sample once and audit the fields specified by the
[validation contract](../../30-validation/s11-r18-causal-trace-observability-validation.md).
R19 behavior design remains blocked until that causal report is returned.

## Detector Governance

- Logic-map nodes: `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`,
  `OIL-PHASE-DRAIN`, `FOAM-CANDIDATE`, `FOAM-EPISODE`,
  `TRACE-PUBLICATION`, `PUBLICATION-PROVENANCE`
- Failure-registry entries: `S11-F02`, `S11-F05`, `S11-F07`, `S11-F08`,
  `S11-F09`, `S11-F10`
- First harmful stage: NONE — this is diagnostic-only local evidence; the
  Windows first harmful stages and named unknowns are frozen in the linked
  causal closure.
- Logic-map impact: UPDATED — the additive causal trace surface is now mapped.
- Failure-registry impact: UPDATED — the R18 narrowed causes and required
  diagnostic rerun replace the earlier audit-pending state.
