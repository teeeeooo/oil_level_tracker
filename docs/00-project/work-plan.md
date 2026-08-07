# Current Work Plan

**Current milestone:** `S11 — Real-Field Detector Effectiveness Recovery`
**Milestone status:** `ACTIVE`
**Current engineering gate:** `Lane C — Initial-State Retrospective FULL/EMPTY Reconstruction implementation`
**Source lane:** `Lane C — shared analysis/result-semantics and versioned compatibility change`

## Current decision

The S11 detector baseline is stable for sequencing purposes. Accepted current-frame D1–D5/S5-B authority and the serialized ambiguity-gated reacquisition repair remain the detector baseline to preserve; detector source tuning is no longer the current gate.

The active responsibility is now **Initial-State Retrospective FULL/EMPTY Reconstruction**. Its durable owner is [the retrospective reconstruction architecture](../20-architecture/initial-state-retrospective-reconstruction-architecture.md), and implementation acceptance is owned by [the dedicated validation contract](../30-validation/initial-state-retrospective-reconstruction-validation.md).

This implementation is Lane C because it changes shared analysis workflow, official event/judgment/coverage semantics, result/review compatibility and introduces a new downstream sequence-level responsibility. It must not move retrospective authority into S5-B, D1–D5 or the serialized online temporal owner.

## Accepted detector baseline to preserve

Observed detector state remains immutable historical observation. Numeric Oil still originates only from an accepted canonical boundary outcome, and hard no-interface, unavailable, glare/exclusion/border, structural and authoritative-Foam safety remain unchanged.

The accepted serialized temporal owner remains the only online detector temporal owner. Canonical ambiguity may preserve an already-pending reacquisition path only under the accepted compatibility rule, never publish numeric Oil or advance confirmation. No retrospective implementation may rewrite that owner or its history.

## Active sequence-level contract

A final analysis run requires explicit current-run initial-state confirmation for every enabled Glass. Recipe `initial_state` remains the selected prior; persisted/copied values do not establish current-run confirmation, and `AUTO` cannot satisfy final readiness. Explicitly confirmed `UNKNOWN_REVIEW` may satisfy readiness but grants no retrospective FULL/EMPTY authority.

Retrospective FULL/EMPTY is a separate official interpretation of only an eligible leading unresolved interval. It requires explicitly confirmed `FULL_NO_INTERFACE` or `EMPTY_NO_INTERFACE` plus later real accepted sequence evidence; barriers, direct contradiction and insufficient evidence retain the fail-closed outcomes defined by the architecture owner. Observed samples and numeric Oil are never synthesized or rewritten.

New official retrospective semantics must preserve legacy observed-only bundle readability while using an explicit newer result/review semantics version so older v1-only consumers cannot silently misrepresent the result.

## Closure boundary

S11 closure remains unapproved. The final Windows field-workflow check is still retained and becomes executable only after this retrospective reconstruction implementation and its required validation are accepted and the resulting S11 output semantics are stable.

## Next handoff

Compose one focused **Lane C Initial-State Retrospective FULL/EMPTY Reconstruction implementation Worker handoff** from the exact documented `main` baseline produced by the documentation-authority commit. Do not return to detector source tuning without new causal evidence, and do not advance directly to the final Windows field-workflow check.
