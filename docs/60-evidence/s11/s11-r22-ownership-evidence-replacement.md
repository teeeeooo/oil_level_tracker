# S11 Oil ownership/evidence replacement evidence

Status: LOCAL ACCEPTED on 2026-09-10; Windows qualification remains outstanding.

## Protected baseline

Baseline source: `0ad13ea645ca97c7f416e0c30bb3f8375e6b3927`. Intake worktree was clean.
The four checked-in `.oiltruth` files contain 15 annotations, 13 usable and two
unusable. The usable cohort is preserved, as are all 11 currently numeric cases
individually. User-transferred Windows coordinates are approximate annotations,
not new checked-in pixel truth or executable production constants.

The 2026-09-09 baseline replay covered all four local videos: 299 rows, 162 numeric
Oil observations (28 / 4 / 29 / 101). It reproduced all four current fingerprints,
including the previously explained Sample4 `e447626b...` runtime baseline; the
historical Sample4 golden was not replaced. The existing replay's historical
fingerprint enforcement was disabled explicitly for this measurement because
that historical golden is already known not to describe this environment.
Current fingerprints were checked against R21 and remain frozen for comparison.

Checked truth: 13 cases, 11 numeric, MAE 9.6363636364 px, maximum error 24.5 px,
coverage-adjusted MAE 11.9230769231 px. Remaining misses: Sample2 frame 0 and
Sample4 frame 0. Sample3 completed-fill numeric count 0, late-drain count 12,
same-frame provenance PASS. New acceptance must check cases individually, not
trade one successful case for a different numeric observation.

## Completed replacement and review

Main completed implementation and direct source review without further sub-agents,
as requested. The production lifecycle now uses explicit runtime state, separate
open/barrier/draining transitions, one per-frame diagnostic record and immutable
completed decisions. `BoundedOilReleaseEvidenceEngine` owns recovery admission,
advancement and qualification rather than callbacks into the lifecycle. Replaced
parallel-array orchestration and transitional recorder/buffer wrappers are removed;
there is no legacy execution fallback.

Typed non-nearest ordered-lower contradictions reach the phase owner even when
current admission removes a row. They reset delayed evidence; ordinary sparse
continuation without contradiction remains supported. Initial-FULL recovery may
renew once with fresh same-owner identity evidence, retains its original origin,
and expires within twice the original horizon. A renewed lease cannot transfer
to a different physical owner. Existing movement/material/gap gates remain.
Confirmation evidence is cached per endpoint without changing continuation motion
aggregation or the meaning of historical confirmation witnesses.

## Final verification

- Canonical suite: **1763 passed**, 162.29 s.
- Qt suite: **252 passed**, 1511 deselected, 9.71 s (overlaps canonical coverage).
- Fifteen new evidence controls cover gradual drain, absolute renewal bounds,
  cross-owner transfer, contradiction/mixed-member and missing-row behavior,
  current-frame provenance and immutable decisions.
- All four final replay tracking fingerprints equal the clean R21 comparison;
  all 13 truth cases retain their exact output and error, including two existing
  misses. This proves non-regression on that cohort, not improved field accuracy.
- Compilation, detector governance and whitespace checks passed.
- Six integration identity assertions were advanced to R22. Characterization
  normalizes only enumerated additive telemetry/version fields before checking
  unchanged R21/R20 goldens. No coordinate, admission, phase, score or selected
  member is normalized. No truth, historical golden, skip/xfail or tolerance was
  changed to manufacture acceptance.

Runtime version: `opencv-phase-detector-r22-oil-ownership-evidence-replacement-v1`.
Base HEAD: `0ad13ea645ca97c7f416e0c30bb3f8375e6b3927`; candidate is a modified
worktree identified by source content, not that clean HEAD. Final source-content
SHA-256 (`src/**/*.py` and `tests/diagnostics/*.py`):
`4874a1e6eea82052fb82df053593c46bb6f5ee78dcfa8affa0dd0eec2b38b2fa`.
It matched before/after replay and all three candidate performance processes.

The durable [verification summary](s11-r22-verification-summary.json) records all
13 cases, input/runtime/source hashes and raw timing/memory samples.

## Final performance comparison

Host: Darwin arm64; Python 3.14.4, OpenCV 4.14.0, NumPy 2.5.1. Runtime fingerprint
`7b14134e3f811d06e45ea2cd44686b5ffedd22dc7e2848fd2e04bd838f8aa20d`.
Sample4, 56-second range, 2 fps, 113 rows, trace NONE, official bundle output.
Three serial alternating baseline/candidate pairs, fresh processes, identical
inputs/runtime/output fingerprint and no competing test/replay processes:

| Metric (median) | R21 | R22 |
|---|---:|---:|
| End-to-end | 11.96372 s | 12.00716 s |
| Reader read | 3.85539 s | 3.84724 s |
| Detect | 7.32405 s | 7.35219 s |
| Completed-window resolve | 0.20766 s | 0.21885 s |
| Bundle output | 0.51183 s | 0.51129 s |
| Peak process RSS | 253,100,032 bytes | 258,965,504 bytes |

End-to-end increased 0.36%, resolve increased 5.39% (about 11 ms), and peak RSS
increased 2.32% (5.59 MiB). There is no measured speedup. This modest measured
cost is retained with explicit state/identity safety; three runs on one sample
are not a broad performance guarantee. Reader and detect dominate (~93% of
baseline end-to-end), so meaningful throughput work belongs in their separately
measured pipeline. These macOS results cannot explain or certify Windows speed.

## Remaining field boundary

The existing FIELD FAIL disposition remains. Private Base repair and Accum
physical owner correctness require target-Windows evidence. The Base 650-second
candidate-generation gap is outside this core replacement and remains unresolved.
Approximate annotations are not exact pixel truth. Local generic controls prove
bounded behavior, not a repair of every observed Windows failure.

## Reproducible comparison tools

- `tests/diagnostics/s11_resolver_replacement_compare.py`: protects each of the
  13 truth cases, checks runtime and sample alignment, reports full tracking
  fingerprint equality separately.
- `tests/diagnostics/s11_resolver_replacement_profile.py`: profiles one sample
  in a fresh process with reviewed expected output, full source-content identity
  before/after, runtime/input hashes, stage timings and process peak RSS where
  available. An uncommitted candidate is explicitly identified by content, not
  mislabeled as its clean Git HEAD. Profiling is serial with no other benchmark
  or test process competing for CPU.

Raw local artifacts currently reside under `/tmp/s11-resolver-replacement/`.
They are reproducible working evidence, not a claim that private Windows bundles
were transferred or that temporary artifacts are permanent repository owners.

## Detector Governance

- Logic-map nodes: `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F04`, `S11-F05`, `S11-F08`, `S11-F09`, `S11-F10`
- First harmful stage: transferred Base sampled rows fail admitted release displacement and intermittently lose admission; Accum delayed identity qualification retains a demoted owner. Full physical identity and Base candidate recall remain named unknowns.
- Logic-map impact: UPDATED — the current map and R22 architecture describe the completed ownership/evidence replacement.
- Failure-registry impact: NONE — existing identity leakage, phase lock and provenance entries already route these measured boundaries; this record does not declare field repair.
