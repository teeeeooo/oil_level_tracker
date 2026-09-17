# S11 R22-3 O1 Interface Witness — Local Acceptance

Date: 2026-09-17. Scope: trace-only extraction, not detector effectiveness.
The [work plan](../../00-project/work-plan.md) owns the next transition and
retains `FIELD FAIL`. The [architecture](../../20-architecture/s11-interface-observability-witness-architecture.md)
and [validation](../../30-validation/s11-interface-observability-witness-validation.md)
own the measurement and acceptance contracts.

## Identity and scope

- Comparison base: `8842bf11ee33623670fac6381c5448524ae5b080`, R22-2 source.
- Candidate detector: `opencv-phase-detector-r22-3-interface-witness-diagnostics-v1`.
- Resolver remains `r22-oil-ownership-evidence-replacement-v1`.
- Old diagnostic schema remains `r22-2-interface-path-diagnostics-v1`.
- New sibling: `state.oil_interface_witness`, schema
  `interface-observability-witness-trace-v1`.
- Source and harness identities, frozen input hashes, runtime provenance and
  comparison digests are retained in the accompanying
  [machine summary](s11-r22-3-interface-witness-local-summary.json).

The supplemental proposal was moved from the docs root to the
[diagnostic review](../../50-diagnostics/s11/s11-observation-redesign-execution-review.md).
Its historical measurements remain intact. Applicable definitions were integrated
into the existing architecture/validation owners rather than creating a competing
design authority.

## Implementation and reuse

Frozen typed records preserve actual sector geometry, candidate identity,
two-sided context at three widths, local peak alternatives, channel availability
and shared-RGB derivation. Contour shape variation is separate from localization
ambiguity. Peak hulls are descriptive, not calibrated confidence intervals.
No classifier, independent-support decision or physical-label inference is added.

The existing `measure_oil_interfaces` owns gray/material/static profile caches,
band geometry and native-path provenance. The new module reuses those owners;
it adds typed aggregation and extra current-raster channel prefixes. The existing
debug projector alone serializes the result. NONE bypasses extraction entirely.
Scores, features, authority, association, phase, selector and output coordinates
do not consume the new namespace.

The replay harness reuses existing public sessions, frozen-input checks, decoder
provenance, fingerprinting and real pipeline/bundle writers. A separate audit
entry point is needed because the timing profiler does not retain raw/completed
detection and old-diagnostic equality across NONE/BASIC/FULL. Each run owns and
removes its temporary bundle after recording hashes and resource measurements.

## Verification

- Focused extraction, integration and original characterization: **30 passed**.
- Canonical non-Qt suite: **1,544 passed**, 254 deselected.
- Canonical Qt suite: **254 passed**, 1,544 deselected.
- The initial broad run exposed seven old detector-version assertions. Only
  expected diagnostic version strings were updated; numeric expectations and
  original characterization hash were not changed. The final full runs above
  passed after those updates.
- Public probe v2: **91 measurements**, four runtime records; summary statistics
  exactly match v1. Missing material conflict is now null rather than invented
  zero. The full v2 result hash is in the machine summary. These are seven
  transforms of 13 frames, not 91 independent scenes or a classifier evaluation.
- Governance, 155 local Markdown link targets and whitespace checks passed.
  Direct source/integration review found no production consumer of the witness.
  No independent-agent review was requested or claimed.

## Replay and resources

All **12 sample/mode runs** passed. Each mode covers 299 sampled detections
(30/5/151/113 by sample), **897 baseline/candidate pairs** overall. Exact raw
and completed detection hashes, old diagnostic hashes, tracking fingerprints,
tracking/event CSV fields (excluding run_id), input hashes and runtime
provenance match. NONE/BASIC/FULL also match each other for production outputs.
No report HTML byte-equivalence claim is made; diagnostic version/identity
metadata legitimately differ. Report behavior is covered by the canonical suite.

| Public sample | Frames/mode | FULL trace MiB: R22-2 → R22-3 | FULL peak RSS MiB: R22-2 → R22-3 |
|---|---:|---:|---:|
| base_sample_1 | 30 | 11.5 → 45.3 | 216.8 → 230.5 |
| sample2 | 5 | 2.2 → 9.2 | 215.5 → 221.9 |
| sample3 | 151 | 53.0 → 209.4 | 249.1 → 263.1 |
| sample4 | 113 | 40.8 → 163.0 | 247.8 → 257.1 |

Debug trace size increases **3.92–4.09×** across these windows. In comparable
copy-mode BASIC runs, elapsed time increases from 9.27/1.98/29.14 seconds to
13.53/3.03/45.72 seconds (base/sample2/sample3). NONE performs no witness work.
This diagnostic runtime is accepted for bounded evidence capture, not as a
zero-cost logging option or a Windows performance qualification.

Timing/RSS are one-pass descriptive observations on this Mac, including debug
serialization and bundle writing. They are not a throughput guarantee or a
statistically controlled performance benchmark. Baseline and candidate use
separate fresh processes, identical input/decoder dependencies and serial sample
execution. The baseline bootstrap harness and retained harness use the same
pipeline, hashing and CSV comparison; their identities are recorded separately.

The copy-mode sample4 BASIC attempt hit ENOSPC with about 800 MiB free. The
retry and FULL runs used the audit harness's `--debug-copy-mode hardlink`: only
immutable finalized staging in its own temporary directory was linked. No
production storage change or user-file deletion was made. Those bundle I/O
timings must not be compared directly to the copy-mode baseline. Original trace
content/size, detections and CSV comparisons are unaffected by this audit option.

## Limits and next transition

O1 provides measurements only. O2 must freeze positive, negative, localization-
mismatch and unresolved labels, and episode-level evaluation partitions before
choosing a shadow classifier or operating point. Repeated reviewed checkpoints
remain regression cases, not untouched holdout. A human-visible miss remains in
the evaluation denominator even if the detector calls it unobservable.

BASE native contour variation is not a negative label. The reviewed BASE
f14362 offset is a localization mismatch, not a certified artifact identity.
Accum support and owner handoff, and initial-FULL direction-neutral observation,
remain separate O3/O4 work. No polarity-only veto, threshold relaxation or
source-family vote has been promoted. Public sample4's historical runtime/golden
discrepancy is not rewritten by this same-runtime equality check.

No target-Windows replay, private-label evaluation, O2 discrimination acceptance
or O5 qualification was performed. Private media, labels and full traces need
not leave the work PC. Local extraction acceptance does not repair field misses.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `OIL-CANDIDATE`, `OIL-PROJECTION`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F02`, `S11-F03`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F08`, `S11-F09`, `S11-F10`.
- First harmful stage: unchanged and case-dependent; this diagnostic-only change establishes no new causal or physical classification. Earlier observation/localization and owner-eligibility failures remain unresolved.
- Logic-map impact: UPDATED — new debug-only typed witness and unchanged production owners are recorded.
- Failure-registry impact: NONE — local measurement/equality evidence does not establish a new field mechanism or resolve the recorded failures.
