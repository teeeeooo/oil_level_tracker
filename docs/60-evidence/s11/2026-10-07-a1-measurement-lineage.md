# A1 measurement lineage — local adoption, 2026-10-07

## Result and scope

A1's three finite gaps are implemented and locally verified: actual upper/lower
phase support, signed narrow center/partner measurements, and score/scalar
coordinate dependencies. The existing frame-local sidecar and diagnostic owner
publish `oil-measurement-lineage-v1`; no authority, score, candidate, Foam,
completed output, detector identity or resolver identity changes. NONE skips it.
The second audit's paired scorer remains rejected. This adopts the diagnostic
subset, not the complete supplied prototype or an A2 tracking repair.

Baseline: `76a2f81`. Production implementation: `6d3cf7e`. Frozen verification
head: `025cd6532f93854d4334f99897c313edaaa2df58` (UTF-8 test read correction).
The [receipt](2026-10-07-a1-measurement-lineage.json) preserves source/input hashes,
comparison results, test provenance, final seven-frame capture, admission trace
and local artifact pins. [Architecture](../../20-architecture/s11-interface-observability-witness-architecture.md#a1-support-signed-pair-and-score-coordinate-lineage)
and [acceptance](../../30-validation/s11-interface-observability-witness-validation.md#a1-lossless-lineage-acceptance)
own the implementation and required checks.

## Verification

- Focused controls: 83 passed. Canonical non-Qt: 2,128 passed, 254 deselected.
  Externally bounded Qt: 254 passed, 2,128 deselected, 9.92 seconds under a
  180-second timeout. Qt ran at `6d3cf7e`; the only later change was explicit
  UTF-8 decoding in a non-Qt test. Production hashes are identical.
- Four official windows × NONE/Basic/Full × baseline/candidate: 24 serial fresh
  processes, identical runtime/input pins and hardlink debug-copy mode. All
  299 rows per mode (897 paired rows total) preserve raw/completed detections,
  all pre-existing diagnostic state, witness bytes, CSV and events. Only the
  new sibling namespace is excluded from old-state equality.
- Eight additional fresh NONE runs compare full report dataclasses recursively
  excluding only `run_id`. Reports are equal; their raw/tracking/event inputs
  match every mode. The first comparison included nested run IDs and failed;
  that initial result and the corrected comparison are both retained.
- All captured semantic hypotheses join by exact ID/Y/three semantic scores:
  zero unmatched records. Phase lineage stays within 15 bands per candidate.
  NONE produces no lineage. Alias, malformed-input, duplicate-index/source/Y,
  empty/clipped/disjoint-X, signed-pair and real debug-entry controls pass.
- Final-code capture at all seven human-reviewed frames exactly matches the
  previous current/completed/stored observations and all old diagnostic state.
  The four correct completed observations remain unchanged. The real Y854
  regression retains center Y853/partner Y851 and same-sign gradients; its human
  ROI remains an unadopted input experiment.

Initial failures are preserved locally: the characterization fingerprint first
included the additive namespace; its exclusion is now limited to that namespace
and old golden values stay unchanged. The first canonical non-Qt run found a
missing explicit UTF-8 test-fixture read; it was fixed before the final pass.
An initial baseline replay lacked its copied corpus manifest; the corrected
baseline comes from the same pinned Git revision. No failing production comparison
was waived.

## Resource measurements

Fresh-process single-pass FULL measurements below are descriptive Mac results,
not statistical performance or Windows qualification. Both sides use the same
hardlink mode for immutable audit staging; the application copy default is unchanged.

| Window | Seconds, before → after | Peak RSS MiB, before → after | Trace MiB, before → after |
|---|---:|---:|---:|
| Base | 13.01 → 13.64 | 229.0 → 230.5 | 45.42 → 47.59 |
| sample2 | 2.82 → 2.98 | 225.6 → 232.5 | 9.20 → 9.59 |
| sample3 | 46.35 → 48.90 | 258.9 → 257.6 | 209.85 → 219.38 |
| sample4 | 33.38 → 35.13 | 254.4 → 259.8 | 163.57 → 172.13 |

FULL elapsed increase is approximately 4.8–5.8%; trace increase 4.2–5.2%.
Maximum observed lineage is 92,793 serialized bytes/frame and 28 candidates/frame.
Storage is frame-local, with no retained raster history. Complete-column paired
availability is separate from the production pooled-support minimum floor; it
reports measurable support, not usable identity or permission to change a score.

## Interpretation and next boundary

The [candidate investigation](../../50-diagnostics/s11/2026-10-07-sample4-interval-candidate-lineage.md#admission-lineage-after-a1)
now traces all three human-confirmed alternatives to `OIL-AUTHORITY` eligibility
loss: Foam/material identity at 40 s, insufficient authority at 42 s, and material
layer terminal restriction at 44 s. These are observed executed reasons, not proof
of the optical cause or justification to bypass those guards.

The pink completed observations are confirmed wrong for Oil; their physical
nature remains unreviewed. A bounded source/pink/cyan comparison asks whether they
are structure/reflection, Foam, another real fluid boundary, or uncertain. Do not
infer `non_interface` from wrong-target status. A2 must define one discriminating
hypothesis and preserve the four positives and existing counter-controls after
that judgment. A1 does not establish A2, O2, A0Q stability or field efficacy.
`FIELD FAIL` and independent-video/Windows acceptance requirements remain unchanged.
The [Work Plan](../../00-project/work-plan.md) owns the live next transition.

Full replays, XML/logs, capture helper, final rasters, admission helper and review
HTML remain in `sample/output/s11-a1-lineage-20261007-001/`. Git retains the receipt
and real regression fixture; large local artifacts are hash-pinned, not embedded
in this evidence document. After verification, 467 byte-verified baseline files
and their source-sample symlink were removed from the temporary comparison root.
They are recoverable from `76a2f81`; unique logs/results/helpers/rasters and the
original videos remain. The receipt records cleanup ownership and scope.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-SELECTOR`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- First harmful stage: `OIL-AUTHORITY` is the earliest observed loss of selection eligibility for these three confirmed candidates; optical discrimination/root cause and a safe corrective rule remain unresolved.
- Logic-map impact: UPDATED — records the additive A1 pure spatial diagnostic reproduction route and scopes the sequence-witness no-rerun contract correctly; decision ownership is unchanged.
- Failure-registry impact: NONE — no failed scorer, guard bypass or coordinate rule is adopted and no physical efficacy is claimed.
