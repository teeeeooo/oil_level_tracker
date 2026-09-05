# Current Work Plan

**Current milestone:** `S11 — Real-Field Detector Effectiveness Recovery`
**Milestone status:** `ACTIVE`
**Current gate:** active behavioral lifecycle/Foam-witness implementation and local acceptance are complete; field qualification remains outstanding
**Field disposition:** latest user-reported Windows result remains `FIELD FAIL`; no field-qualified detector is claimed

This document owns only the current engineering state and next transition. Revision-by-revision history belongs in diagnostics, evidence, historical architecture/validation records, and Git history.

## Accepted baseline

The current implementation preserves the established S11 safety and publication contracts while applying two locally accepted behavioral repairs:

1. delayed drain reacquisition does not consume its one ownerless attempt until the existing positive drain direction/agreement/progress readiness evidence is present; and
2. Foam confirmation is bounded to local four-frame / 2.0-second witness windows with actual dynamic stable support.

Local implementation, targeted/canonical validation, independent review, and documentation closeout for that behavioral slice are complete. The authoritative contract/evidence is:

- [active behavioral architecture](../20-architecture/s11-behavioral-lifecycle-and-foam-witness-architecture.md)
- [active behavioral validation/work specification](../30-validation/s11-behavioral-lifecycle-and-foam-witness-validation.md)
- [completed local evidence](../60-evidence/s11/s11-behavioral-lifecycle-and-foam-witness.md)

The predecessor R18/R19/R20 records remain historical inputs, not alternate current owners.

## Current authorization boundary

Currently authorized repository maintenance may preserve or clarify the accepted baseline and its documentation without changing detector behavior.

Not automatically authorized by the current gate:

- a new detector revision or threshold/authority change;
- automatic replay of private Windows media;
- reopening the closed Windows investigation;
- case-specific video/Glass/timestamp/coordinate behavior;
- interpolation, carry, or report-side repair of missing detector observations;
- activation of retained Base/Accum behavior surfaces or the decision-witness package without a separate approval/design gate.

Future deliberate Windows field qualification remains a valid but non-current transition. It must use the current validation/truth/procedure authorities and must not reinterpret local acceptance as field proof.

## Preserved contracts

- one generic detector serves every Glass; no private identity or reviewed coordinate enters production control flow;
- numeric Oil/Foam values remain selected same-frame candidates with exact provenance;
- Oil and Foam validity/ownership remain independent through their defined composition point;
- confirmed FULL/EMPTY state constrains lifecycle but never fabricates a coordinate;
- ambiguous, unavailable, lost, or hard-invalid evidence fails closed rather than being repaired downstream;
- current detector changes remain governed by the logic-map/failure-registry history review contract.

## Open field risks and named unknowns

The current baseline is not field-qualified. Retained uncertainty includes Base release/closure behavior, Accum entry/continuity/re-entry surfaces, and historical R18 causal unknowns where reviewed physical identity or exact Y anchors were unavailable. These facts are constraints on claims, not automatic implementation tasks.

Retained but non-current work is owned by [`retained-commitments.md`](retained-commitments.md).

## Next transition

The current repository has no automatically executable next detector revision. The next material S11 transition requires explicit authorization for one of:

1. deliberate target-Windows field qualification of the accepted behavioral baseline; or
2. activation of a separately designed/evidence-backed retained behavior or observability slice.

Until then, preserve the accepted local behavioral contract and the existing field `FAIL` boundary.

## Current authority links

- [Project roadmap](roadmap.md)
- [Repository execution policy](execution-policy.md)
- [S11 detector change governance](../30-validation/s11-detector-change-governance.md)
- [Current detector logic map](../20-architecture/s11-current-detector-logic-map.md)
- [Detector mechanism failure registry](../50-diagnostics/s11/s11-detector-mechanism-failure-registry.md)
- [Canonical Windows reviewed truth](../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md)
- [Future Windows procedure](../40-operations/manual-gui-windows-checklist.md)