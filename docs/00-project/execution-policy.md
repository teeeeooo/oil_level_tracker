# Repository Execution Policy

**Status:** `ACTIVE`

This policy defines repository execution states, mutation boundaries, verification, exact-head review, merge/publication, and closeout. It is role-neutral: external agent/session/delegation policy is outside this repository.

## Execution states

| State | Purpose | Repository mutation |
|---|---|---|
| `DISCOVER` | inspect repository, authority, evidence, and current worktree | none |
| `EXECUTE` | perform the authorized bounded change | allowed within requested scope |
| `VERIFY` | establish correctness with proportional checks | only repairs required by findings |
| `REVIEW_FREEZE` | independently review or validate one exact head | none on the frozen head |
| `PUBLISH` | merge, release, or otherwise make the result authoritative | only if explicitly authorized |
| `CLOSE` | record the resulting current state and next transition | documentation-only as authorized |

A task may skip states that are not needed. A documentation-only edit does not require a release-style validation chain.

## Authority and autonomy

- Perform routine reversible work already implied by the user's request without an extra approval round.
- Preserve unrelated worktree changes and keep them outside the task diff.
- Do not broaden product behavior or repository scope merely to make a check pass.
- If a materially consequential action was not authorized, stop immediately before that action and present the concrete ready-to-apply result.
- Existing explicit user authorization is sufficient; do not ask for the same approval again.

## Verification policy

Use the smallest verification tier that demonstrates the changed contract. Escalate only when the changed owner, a finding, or an acceptance contract requires it.

| Tier | Typical change | Default evidence |
|---|---|---|
| `V0` | read-only investigation | source/evidence inspection only |
| `V1` | documentation, metadata, low-risk configuration | link/policy checker as relevant + `git diff --check` |
| `V2` | bounded source repair | focused tests for changed behavior |
| `V3` | cross-owner or integration behavior | focused tests + relevant integration/contract suite |
| `V4` | detector/release acceptance gate | validation-contract-defined suite and evidence |
| `V5` | platform/release qualification | canonical/platform/package gate defined by current authority |

Do not run a broader suite only because it exists. Conversely, do not substitute a narrow test for a contractually required gate.

## Exact-head review and freeze

A `REVIEW_FREEZE` begins when an independent exact-head audit, controlled comparison, canonical validation, or final acceptance review starts. During the freeze, do not change source, tests, documentation, or metadata on that head.

If review fails, the freeze ends and the next authorized repair creates a new head. If review succeeds, preserve that exact head as the publication target unless a new authorized change intentionally invalidates the result.

Read-only review results belong in the review report/evidence; they do not mutate the frozen head merely to record success.

## Current-state closeout

Current-state documents are not execution journals.

- Update [`work-plan.md`](work-plan.md) when the active gate, accepted baseline, blockers/unknowns, or next transition changes.
- Update [`roadmap.md`](roadmap.md) only when milestone order, scope, or formal state changes.
- Route retained but non-current work to [`retained-commitments.md`](retained-commitments.md).
- Put durable product/architecture changes in their owning `10-product/` or `20-architecture/` contract and acceptance changes in `30-validation/`.
- Put completed implementation/audit/validation measurements in `60-evidence/`; investigations belong in `50-diagnostics/`.
- Do not append branch-by-branch history, reviewer chronology, or resolved findings to the Work Plan or Roadmap.

When a task changes documentation structure, update [`../README.md`](../README.md) and verify relative links, case-sensitive paths, old filename references, duplicate current-state ownership, and `git diff --check`.

## Publication boundary

Merge, release, deploy, external publication, destructive deletion, and irreversible migration are consequential actions. Perform them only when they are inside the user's granted authority. Preparing a branch, patch, local validation result, or review report is not itself publication.

Formal `DONE` means implementation, required acceptance, and required publication/merge are complete. A local feature head, successful focused test, or read-only audit is not by itself milestone completion.