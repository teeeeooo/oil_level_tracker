# Current Work Plan

**Current milestone:** `S11 — Real-Field Detector Effectiveness Recovery`
**Milestone status:** `VALIDATING`
**Current engineering gate:** `Lane B — Workbench exclusion / ellipse interaction isolation repair`
**Source lane:** `Lane B — bounded Workbench canvas interaction/presentation repair`

## Current decision

The S11 detector baseline and Initial-State Retrospective FULL/EMPTY Reconstruction are accepted for sequencing. Current-frame D1–D5/S5-B authority, the serialized ambiguity-gated reacquisition owner, immutable observed samples, explicit current-run confirmation authority and versioned retrospective result semantics are the baseline to preserve.

Before spending the final Windows field-validation pass, S11 must complete two bounded functional repairs in order. First, the existing Workbench canvas interaction/presentation owner must ensure that dragging or resizing an exclusion mutates only that exclusion and leaves the selected Glass ellipse geometry unchanged unless the ellipse itself is intentionally manipulated. Second, the existing Result Review presentation owner must ensure that repeated playback/cursor updates remain graph-layout stable over sustained playback; cursor movement does not require rebuilding graph series, while the exact causal source repair remains Worker-owned.

After both repairs are accepted, execute the **final Windows field-workflow check** using the [manual Windows checklist](../40-operations/manual-gui-windows-checklist.md), including its initial-state confirmation and retrospective reconstruction obligations. Detector tuning and retrospective architecture are not reopened by this sequence.

## Accepted detector baseline to preserve

Observed detector state remains immutable historical observation. Numeric Oil still originates only from an accepted canonical boundary outcome, and hard no-interface, unavailable, glare/exclusion/border, structural and authoritative-Foam safety remain unchanged.

The accepted serialized temporal owner remains the only online detector temporal owner. Canonical ambiguity may preserve an already-pending reacquisition path only under the accepted compatibility rule, never publish numeric Oil or advance confirmation. No retrospective implementation may rewrite that owner or its history.

## Accepted sequence-level contract

A final analysis run requires explicit current-run initial-state confirmation for every enabled Glass. Recipe `initial_state` remains the selected prior; persisted/copied values do not establish current-run confirmation, and `AUTO` cannot satisfy final readiness. Explicitly confirmed `UNKNOWN_REVIEW` may satisfy readiness but grants no retrospective FULL/EMPTY authority.

Retrospective FULL/EMPTY is a separate official interpretation of only an eligible leading unresolved interval. It requires explicitly confirmed `FULL_NO_INTERFACE` or `EMPTY_NO_INTERFACE` plus later real accepted sequence evidence; barriers, direct contradiction and insufficient evidence retain the fail-closed outcomes defined by the architecture owner. Observed samples and numeric Oil are never synthesized or rewritten.

Official retrospective semantics preserve legacy observed-only bundle readability while using the accepted newer result/review semantics version so older v1-only consumers cannot silently misrepresent the result.

## Closure boundary

S11 closure remains unapproved. The final Windows field-workflow check remains the last S11 acceptance gate, but it is executable only after both bounded pre-Windows functional repairs are accepted. Do not advance to S12 before the target-Windows field workflow is accepted.

## Next handoff

Execute **Lane B — Workbench exclusion / ellipse interaction isolation repair** from synchronized `main` on one focused branch/PR. After that repair is accepted, execute **Lane B — Result Review playback graph layout-stability repair**; only after both repairs are accepted proceed to the final Windows field-workflow validation.
