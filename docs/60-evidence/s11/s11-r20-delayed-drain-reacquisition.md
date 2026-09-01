# S11-R20 Delayed Drain Reacquisition Local Evidence

**Status:** `LOCAL PASS / WINDOWS REQUIRED`

## Scope and source identity

This record covers the R20 lifecycle implementation and local validation. The
runtime implementation and focused tests were complete at
`84347a59fa6b0689e3ddf52130496089153e7a28` (`fix(detector): hold delayed
attempt across fill reentry`), on top of contract commit `c507312`, lifecycle
implementation commit `1b4459f` and focused-test commit `8713cea`. The final evidence,
current-map, responsibility and project-status edits are documentation-only
changes after those checks. The expected task-start baseline was
`e3a014f7542654b5e63353a173b8b038be34e2bf`.

R20 changes only `OilMaterialPhaseLifecycleOwner`: it keeps direct partial-fill
release first, R19 near-snapshot recovery second, and adds one post-grace,
fresh-anchor delayed attempt behind a coordinate-free ownerless barrier. No
candidate generation, authority thresholds, ordinary tracklet continuity,
selector scoring, projection, CSV, graph, event, Recipe or Foam behavior was
changed. Detector, resolver, sequence and lifecycle diagnostics advance to
`r20-delayed-drain-reacquisition-v1` while R19 fields remain readable.

## Validation commands and results

All commands below ran from the repository root with the repository `.venv`.

| Gate | Command | Result |
|---|---|---|
| R20 delayed-seam lifecycle unit slice | `.venv/bin/python -m pytest -q tests/unit/test_oil_phase_lifecycle.py` | `83 passed in 0.09s` |
| R20 lifecycle, resolver, tracklet, trace, coordinator, integration, benchmark and publication-focused suite | `.venv/bin/python -m pytest -q tests/unit/test_oil_phase_lifecycle.py tests/unit/test_oil_observation_resolver.py tests/unit/test_oil_interface_tracklets.py tests/unit/test_jsonl_debug_trace.py tests/test_detection_run_coordinator.py tests/test_foam_phase_detector_integration.py tests/test_oil_detector_integration.py tests/test_detector_benchmark_integration.py tests/test_oil_controlled_benchmark.py tests/test_foam_controlled_benchmark.py tests/test_oil_production_cutover.py` | `518 passed in 41.73s` |
| R20 characterization/version fingerprint | `.venv/bin/python -m pytest -q tests/unit/test_oil_phase_lifecycle.py tests/test_r16_refactor_characterization.py::test_r0_completed_window_stage_and_provenance_fingerprint` | `80 passed in 0.45s` |
| Full repository suite | `.venv/bin/python -m pytest -q` | `1706 passed in 152.48s` |
| Qt partition | `.venv/bin/python -m pytest -q -m qt_app -x` | `252 passed, 1453 deselected in 9.26s` |
| Compilation | `.venv/bin/python -m compileall -q src tests` | passed |
| Governance over the R20 range and worktree | `python3 scripts/check_detector_governance.py --base-ref e3a014f7542654b5e63353a173b8b038be34e2bf --include-worktree` | passed before and after implementation/documentation edits |
| Whitespace | `git diff --check` | passed |

The focused lifecycle tests cover: grace frames, a 117-frame evidence-free
ownerless interval with constant-size diagnostic state, unique fresh anchors
outside the stale snapshot jump, delayed success, sparse continuation and
cross-ID anchor handoff, consumed ambiguity, expiry without reseed, phase
identity, provisional/tracklet admission, strict material rejection of moving
residue/glare, direct-before-near-before-delayed priority, near active-chain and
ambiguity gating, same-frame provenance, and initial-FULL/EMPTY and Foam
controls. Existing R19 tests continue to cover step, jump, gap, direction,
stagnation, material, handoff, ambiguity and evidence-window bounds.

## Four-video replay and provenance

The exact local videos `base_sample_1`, `sample2`, `sample3` and `sample4` were
replayed in fresh temporary roots with the existing isolated R18 lifecycle
harness. The first run used `--skip-fingerprint-check` and did not regenerate a
golden. A second fresh run enabled the preserved fingerprint checks:

```text
.venv/bin/python -m tests.diagnostics.s11_r18_lifecycle_closure_replay \
  --root /Users/sunjaekim/Developer/oil_level_tracker \
  --output-root /tmp/r20-four-video.ZAGrSy \
  --skip-fingerprint-check

.venv/bin/python -m tests.diagnostics.s11_r18_lifecycle_closure_replay \
  --root /Users/sunjaekim/Developer/oil_level_tracker \
  --output-root /tmp/r20-four-video-final.bEVFyd
```

The checked run passed all frozen counts and fingerprints:

| Video | Rows | Numeric Oil | Foam episodes | Tracking fingerprint |
|---|---:|---:|---:|---|
| `base_sample_1` | 30 | 28 | 0 | `5879657ce71ced5970c13272867f61def7d7972195b5d264a3cf63c99f1122b7` |
| `sample2` | 5 | 4 | 0 | `85713bc131a808d81d073bec5bff8d035604cb4c1912ba6412c1b5c448fe4976` |
| `sample3` | 151 | 29 | 2 | `feb7e139269894b0aa86d692722acb4512e487dd0b71367fa88859e67745d5a1` |
| `sample4` | 113 | 101 | 1 | `0f2029475506c87aac3ec46bf118b3ae9a1ead0da45eb0d214e1d23ececf9154` |
| **Total** | **299** | **162** | **3** | — |

Same-frame provenance remained `PASS` with zero numeric rows lacking nested
same-frame provenance. The checked replay is behavior evidence: these four
videos do not exercise the transferred delayed ownerless seam, so no new field
effectiveness claim is made from them.

## Controlled performance

The existing exact-source performance harness ran against a clean detached
worktree at the implementation commit, with the four sample video files linked
from the repository's local sample directory (ignored media is not tracked).
The command was:

```text
PYTHONPATH=/tmp/r20-perf-root .venv/bin/python \
  -m tests.diagnostics.s11_r16_performance_profile \
  --root /tmp/r20-perf-root \
  --output-root /tmp/r20-performance-output-final \
  --sample sample4 --repeats 3 --behavior-owner R20 \
  --expected-numeric-oil-count 101 \
  --expected-tracking-fingerprint 0f2029475506c87aac3ec46bf118b3ae9a1ead0da45eb0d214e1d23ececf9154 \
  --source-head 84347a59fa6b0689e3ddf52130496089153e7a28
```

All three repeats retained 113 rows, 101 numeric Oil rows and the expected
fingerprint. Median end-to-end time was `11.6178 s` for the 56-second video,
real-time factor `0.2075`, mean detector latency `63.5483 ms/frame`, and
completed-window resolution `0.2023 s`. This is comparative macOS evidence,
not a Windows throughput claim.

## R20 safety and scope disposition

The positive synthetic lifecycle controls prove that the first qualifying
anchor starts exactly one R19-bounded attempt, that the current row alone is
published on delayed confirmation, and that continuation/handoff retains
distinct physical IDs. Negative controls prove ordinary grace, invalid phase
identity, provisional identity, material opposition, ambiguity, expiry,
stagnation and reseed rejection. Direct and near-snapshot routes remain ahead
of delayed evaluation. The four-video replay confirms unchanged existing Oil,
Foam, CSV/sequence fingerprint and provenance behavior where the delayed route
is not triggered.

No candidate, ordinary tracklet, selector, projection, publication, Foam,
global threshold or field-specific logic was broadened. No golden was
regenerated. The private Windows video and reviewed-Y field records are not
available in this local environment; canonical Windows replay remains the
required next gate.

## Remaining Windows gate

After the authorized push, replay `windows_sample1_heating_coldstart` and
compare all 1,202 rows and nine reviewed-truth segments against the R19/R18
baseline. The report must separate ordinary barrier grace, delayed attempt
consumption, direct/near/delayed funnel counts, Accum seed authority/phase/
material, chain/ambiguity/selection/provenance, residue controls and Base
`NOT_PROVEN` safety. Foam must remain identical and selected, sequence and CSV
Y mismatch must remain zero. Until that private replay is executed and
reviewed, S11 remains `LOCAL PASS / WINDOWS REQUIRED`, never field PASS.

## History Review

- Logic-map nodes: `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `PUBLICATION-PROVENANCE`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F05`, `S11-F08`, `S11-F09`, `S11-F10`
- Prior mechanisms reviewed: R16 reciprocal physical ownership, R17 owner-loss dead end, R18 lifecycle closure and causal rerun, and R19 bounded direct/near recovery, including their architecture, validation, diagnostics and local evidence.
- Prior mechanisms rejected: global threshold widening, motion-only bootstrap, stale-coordinate/ID transfer, selector/projection repair, unconstrained fallback, unbounded search, interpolation/carry, private field identity, Foam coupling and golden regeneration.
- Preserved contracts: one generic detector, initial EMPTY safety, coordinate-free FULL, current-row authority/material identity, distinct physical IDs, bounded chain/handoff, ambiguity/material fail-closed behavior, exact selected-candidate/sequence/CSV provenance and independent Foam.
- Difference from prior failures: R20 retains only constant-size ownerless phase context, waits through ordinary grace, permits one fresh-anchor attempt per established-fill episode and applies existing R19 bounds only to current evidence; snapshot distance and loss age remain diagnostic.
- Logic-map impact: UPDATED — the current map now records the R20 lifecycle route and additive diagnostics while retaining all prior node IDs.
- Failure-registry impact: UPDATED — current registry metadata now routes the existing F04/F05/F08/F09/F10 guards through the R20 local evidence while preserving historical R18/R19 mechanism records; F02 remains the authority-funnel guard.

## Detector Governance

- Logic-map nodes: `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `PUBLICATION-PROVENANCE`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F04`, `S11-F05`, `S11-F08`, `S11-F09`, `S11-F10`
- First harmful stage: the transferred Accum established-fill owner loss at `OIL-PHASE-FILL` is the R20 seam; local replay is invariant and canonical Windows effectiveness/reviewed-Y outcome remain unknown.
- Logic-map impact: UPDATED — the current map records R20 as the implementation-current lifecycle and diagnostic behavior.
- Failure-registry impact: UPDATED — this evidence records the registry's R20 current routing; historical F01-F10 mechanism details remain unchanged and the canonical Windows gate remains required.
