# Current Work Plan

**Current milestone:** `S11 — Real-Field Detector Effectiveness Recovery`
**Milestone status:** `ACTIVE`
**Current gate:** R21 truth-preserving detector repair implementation and local acceptance are complete; deliberate Windows field qualification remains outstanding
**Field disposition:** latest user-reported Windows result remains `FIELD FAIL`; no field-qualified detector is claimed

This document owns only the current engineering state and next transition. Revision-by-revision history belongs in diagnostics, evidence, historical architecture/validation records, and Git history.

## Accepted local candidate

R21 is the current locally accepted candidate on top of the established S11 safety and publication contracts. Its bounded changes are:

1. initial-`FULL` slow-drain release may use bounded recent physical trajectory evidence without weakening the existing release threshold or the R19 absolute recovery expiry;
2. an established drain may close a rapid refill through the same physical owner or one unique independently confirmed fresh topward owner only after the old drain owner is absent, with physical tracklet IDs remaining distinct;
3. Foam stable-layer confirmation restores the reviewed bounded three-observation witness while retaining at least two dynamic observations, the four-frame / 2.0-second horizon and all material/static/opposition gates;
4. initial-`EMPTY` continuity remains on the existing lifecycle path and is covered by controlled current-frame evidence without an Accum-specific relaxation; and
5. additive Oil/Foam decision witnesses serialize already-computed decisions without becoming detector, selector or publication authority.

The R21 runtime identity is `opencv-phase-detector-r21-truth-preserving-detector-repair-v1`. Local implementation, canonical/focused validation, four-video replay, provenance checks and repeated performance comparison are complete. The current contract/evidence is:

- [R21 architecture](../20-architecture/s11-r21-truth-preserving-detector-repair-architecture.md)
- [R21 validation/work specification](../30-validation/s11-r21-truth-preserving-detector-repair-validation.md)
- [R21 completed local evidence](../60-evidence/s11/s11-r21-truth-preserving-detector-repair.md)

R18–R20 remain predecessor evidence and accepted-baseline history, not alternate current owners.

## Current authorization boundary

Ordinary repository maintenance may preserve or clarify the accepted R21 local candidate and its documentation without changing detector behavior.

Not automatically authorized by the current gate:

- another detector revision, threshold/authority change or widening of candidate generation;
- weakening or removal of the R19 absolute recovery expiry without new physical evidence and a deliberate contract change;
- regeneration or silent replacement of a checked tracking fingerprint/golden merely to fit the current environment;
- automatic replay of private Windows media or reinterpretation of local controls as field proof;
- case-specific video/Glass/timestamp/coordinate behavior, interpolation, carry or report-side repair; or
- speculative Accum-specific behavior changes without reviewed physical identity and two-sided controls.

The local Sample4 replay currently produces `e447626b...` rather than the historical checked `0f202947...`. A clean detached `d50c143` baseline produces the same current `e447626b...`, and its tracking rows are identical to R21 apart from run identity. The R20-era sample authority records the same Sample4 media SHA-256 (`ee971b...`) as the current file, so the evidence does not support media replacement as the cause. The historical golden was not changed; the unresolved provenance gap is the exact historical Python/OpenCV/video-decoder runtime, now guarded for future runs by the [R21 replay runtime provenance diagnostic](../50-diagnostics/s11/s11-r21-replay-runtime-provenance-diagnostic.md).

## Preserved contracts

- one generic detector serves every Glass; no private identity or reviewed coordinate enters production control flow;
- numeric Oil/Foam values remain selected same-frame candidates with exact provenance;
- Oil and Foam validity/ownership remain independent through their defined composition point;
- confirmed FULL/EMPTY state constrains lifecycle but never fabricates a coordinate;
- physical tracklet identities are not copied across a rapid-refill phase handoff;
- ambiguous, unavailable, lost, or hard-invalid evidence fails closed rather than being repaired downstream; and
- detector changes remain governed by the current logic-map/failure-registry history-review contract.

## Open field risks and named unknowns

R21 is not field-qualified. The controlled Base cycle proves generic local behavior for bounded slow drain and rapid refill, but it does not prove that the private Windows Base failure had the same cause or is repaired. Accum initial entry, continuity/layered/post-Foam ownership and drain re-entry remain field uncertainties. Historical R18 causal unknowns remain constraints where reviewed physical identity or exact Y anchors were unavailable.

Retained but non-current work is owned by [`retained-commitments.md`](retained-commitments.md).

## Next transition

There is no automatically executable R22 detector revision. The next material S11 transition is deliberate target-Windows qualification of the R21 local candidate using the canonical reviewed truth and Windows procedure. If that replay remains `FIELD FAIL`, any subsequent behavior change must begin from the newly observed failing stage rather than from synthetic success alone.

Until a deliberate Windows replay is executed and reviewed, preserve the existing field `FAIL` boundary.

## Current authority links

- [Project roadmap](roadmap.md)
- [Repository execution policy](execution-policy.md)
- [S11 detector change governance](../30-validation/s11-detector-change-governance.md)
- [Current detector logic map](../20-architecture/s11-current-detector-logic-map.md)
- [R21 architecture](../20-architecture/s11-r21-truth-preserving-detector-repair-architecture.md)
- [R21 validation](../30-validation/s11-r21-truth-preserving-detector-repair-validation.md)
- [R21 local evidence](../60-evidence/s11/s11-r21-truth-preserving-detector-repair.md)
- [Detector mechanism failure registry](../50-diagnostics/s11/s11-detector-mechanism-failure-registry.md)
- [Canonical Windows reviewed truth](../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md)
- [Future Windows procedure](../40-operations/manual-gui-windows-checklist.md)
