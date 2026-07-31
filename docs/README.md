# Documentation Guide

`docs/` contains the product specification, project planning, feature contracts, quality gates and historical records for Rotary Oil Level Tracker. Start here before changing implementation or project status.

## Start here

1. Read the [product SSOT](./rotary_oil_level_tracker_ssot_spec.md) for product scope, user workflow, domain and baseline architecture.
2. Read the [roadmap](./00-project/roadmap.md) for long-term milestone order and state.
3. Read the [current work plan](./00-project/work-plan.md) for the active milestone, current gate, evidence and next action.
4. Read the active feature design and the quality documents linked from the work plan.
5. Apply the [closeout policy](./00-project/closeout-policy.md) whenever implementation, audit or validation work closes.

## Document classification

| Directory | Ownership |
|---|---|
| `00-project/` | Long-term roadmap, current work, status transitions and closeout procedure |
| `10-product/` | User flow, UX and feature requirements |
| `20-architecture/` | System boundaries, feature architecture and design decisions |
| `30-quality/` | Benchmark, validation, regression and manual acceptance obligations |
| `40-operations/` | Packaging, deployment and release operation documents when present |
| `90-archive/` | Superseded or historical planning records; never current authority |

Directories are created only when they contain a meaningful document. File names use lower-kebab-case except this index and the unchanged top-level product SSOT.

## Authoritative hierarchy

When documents disagree, use this order:

1. [Product SSOT](./rotary_oil_level_tracker_ssot_spec.md) for product and persisted-contract requirements.
2. [Roadmap](./00-project/roadmap.md) for milestone scope, sequence and long-term status.
3. [Work plan](./00-project/work-plan.md) for the active milestone, exact current gate and next action.
4. Approved architecture or product detail documents for feature-specific contracts.
5. Quality documents for acceptance evidence and validation obligations.
6. Historical implementation records and archived documents for context only.

A feature document must not maintain a competing project-wide “current next work” list. It links to the roadmap or work plan instead.

## Active documents

- Active S6 state and gate: [current work plan](./00-project/work-plan.md)
- Long-term status: [project roadmap](./00-project/roadmap.md)
- Current validation contract: [real-world validation plan](./30-quality/real-world-validation-plan.md)
- S6-A repository sample evidence: [base sample qualification](./30-quality/s6-base-sample-1-evidence.md)
- S6-B additional real-video evidence: [additional sample qualification](./30-quality/s6-additional-real-samples-evidence.md)
- Manual platform gate: [manual GUI and Windows checklist](./30-quality/manual-gui-windows-checklist.md)
- Detector benchmark guide: [golden video regression](./30-quality/golden-video-regression.md)

## Document status

The only project status values are `PLANNED`, `ACTIVE`, `BLOCKED`, `VALIDATING`, `DONE`, `DEFERRED` and `SUPERSEDED`. `DONE` requires implementation, required validation and merge completion; an unmerged feature head is never `DONE`.

## Update rules

- Every implementation, audit and validation closeout result must be reflected in the work plan. A mutation-capable Worker includes the update in its resulting head; a read-only Auditor or Validator reports against the immutable head and does not mutate it during an exact-head freeze. Deferred results are incorporated by the next authorized mutation-capable owner or an explicit post-merge documentation closeout.
- The roadmap changes only for milestone start/completion, order or scope change, or defer/supersede decisions.
- Architecture documents change when responsibility boundaries, domain types, interfaces or confirmed design decisions change.
- Quality documents change when metrics, fixture categories, manual obligations or runtime/packaging gates change.
- This index changes whenever a document is added, moved, renamed or archived, or the authority hierarchy changes.

## Bounded planning documents

The Roadmap and Work Plan are bounded current-state documents, not cumulative journals. Roadmap milestones are updated in place, while the Work Plan replaces obsolete gates, findings, risks, stage summaries and its single latest-closeout block. Detailed evidence belongs in linked architecture or quality documents, external artifacts or Git history.

Archive snapshots require explicit approval for exceptional historical value. They are not created automatically at every milestone or closeout. Each mutation-capable closeout must remove obsolete planning content as well as add the new current state.

See the [closeout policy](./00-project/closeout-policy.md) for replacement, compaction, exact-head and actor-specific closeout rules.

## Archive policy

Archive documents preserve meaningful history that no longer describes current operation. Each archived document must state why it is superseded and link to its replacement. Archived content is not used to determine current milestone status, gate or next action.

Current historical records:

- [Initial implementation gaps](./90-archive/initial-implementation-gaps.md)
- [Real-world stabilization snapshot](./90-archive/real-world-stabilization-plan-2026-07.md)
- [UX improvement backlog snapshot](./90-archive/ux-improvement-backlog-2026-07.md)
