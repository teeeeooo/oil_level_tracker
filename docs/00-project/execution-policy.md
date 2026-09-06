# Repository Execution Policy

**Status:** `ACTIVE`

This document owns only repository-specific verification, exact-head review/freeze, publication, and formal completion semantics. Generic autonomy and approval behavior come from the user-level agent harness.

## Proportional verification

Use the smallest evidence set that proves the changed contract, then broaden only when the current validation owner, a failure, cross-owner impact, or unresolved acceptance risk requires it.

- documentation/metadata: focused link/policy checks plus `git diff --check` as relevant;
- bounded source repair: focused tests for changed behavior;
- cross-owner integration: focused tests plus the relevant integration/contract suite;
- S11 detector acceptance: the current detector validation owner and governance checker;
- target-Windows/package qualification: the current operational/validation owner.

A passing local or canonical suite never substitutes for a required field/platform gate.

## Exact-head review and freeze

An independent audit, canonical validation, final acceptance review, or publication review must identify the exact repository/base/head and complete changed scope it is judging.

Once that review begins, do not mutate the frozen head. A repair ends the freeze and creates a new head; only invalidated evidence needs to be rerun. Worker/reviewer reports are navigation, not repository truth.

## Publication boundary

Merge, release, deploy, external publication, destructive deletion, and irreversible migration occur only when the user's granted authority covers that action.

Before an authorized publication, verify the intended branch/head and relevant remote state. After publication, verify the expected authoritative head and repository cleanliness when those are part of the requested outcome.

## Current-state closeout

Update `work-plan.md` only when the active gate, accepted baseline, blocker/unknown, field disposition, or next transition changes. Update `roadmap.md` only when milestone order, scope, or formal state changes. Route retained but non-current work to `retained-commitments.md`.

Completed measurements belong in `60-evidence/`; causal investigations belong in `50-diagnostics/`; durable product/architecture/validation contracts remain in their owning directories. Do not turn current-state documents into execution journals.

Formal `DONE` means implementation, required acceptance, and required merge/publication are complete. Local implementation, focused tests, or a read-only audit alone do not make a milestone `DONE`.
