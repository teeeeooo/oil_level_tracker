# Documentation Map and Authority

This file is the **documentation-routing SSOT**. It classifies documents and points to current owners; it does not duplicate project history or task execution policy.

Read this router when creating, moving, renaming, archiving, or changing document ownership, or when the correct owner/location is unclear. Editing an already-known owner does not require rereading this file merely because the path is under `docs/`.

## Fresh reading path

Read only the smallest set needed for the task:

1. If current state/authorization matters, read [`00-project/work-plan.md`](00-project/work-plan.md).
2. If broader milestone order matters, read [`00-project/roadmap.md`](00-project/roadmap.md).
3. Read the relevant durable owner under [`10-product/`](10-product/) or [`20-architecture/`](20-architecture/) and the applicable acceptance contract under [`30-validation/`](30-validation/).
4. Use [`00-project/recall-index.md`](00-project/recall-index.md) only for past-dependent work or unclear prior rationale.
5. Use [`40-operations/`](40-operations/), [`50-diagnostics/`](50-diagnostics/), [`60-evidence/`](60-evidence/), and [`70-reference/`](70-reference/) only when the task needs procedure, causal detail, completed proof, or external provenance.

The stable product specification is [`rotary_oil_level_tracker_ssot_spec.md`](rotary_oil_level_tracker_ssot_spec.md). Repository execution state and verification semantics are owned by [`00-project/execution-policy.md`](00-project/execution-policy.md).

## Directory taxonomy

| Directory | Responsibility | Authority boundary |
|---|---|---|
| `00-project/` | roadmap, current work, execution policy, compact recall routing, retained/deferred routing | project sequence/current gate; not feature design history |
| `10-product/` | user-facing/product contracts | durable behavior and UX intent |
| `20-architecture/` | durable responsibility/design contracts | accepted ownership/invariants; not execution chronology |
| `30-validation/` | validation, benchmark and test-acceptance contracts | what must be demonstrated for acceptance |
| `40-operations/` | executable Windows/package/manual procedures | how to perform operational checks; not proof they passed |
| `50-diagnostics/` | investigations, probes and machine manifests | causal/reproducibility support; never current gate authority |
| `60-evidence/` | completed implementation/audit/validation records | historical proof; contemporaneous status does not become current authority |
| `70-reference/` | external/reference provenance | supporting provenance only |
| `90-archive/` | superseded historical context | not current authority |

## Authority hierarchy

When documents disagree, use the owner for the responsibility in question:

1. stable product requirements — [`rotary_oil_level_tracker_ssot_spec.md`](rotary_oil_level_tracker_ssot_spec.md);
2. milestone order/state — [`00-project/roadmap.md`](00-project/roadmap.md);
3. exact active gate — [`00-project/work-plan.md`](00-project/work-plan.md);
4. repository execution/verification/publication semantics — [`00-project/execution-policy.md`](00-project/execution-policy.md);
5. retained non-current commitments — [`00-project/retained-commitments.md`](00-project/retained-commitments.md);
6. relevant durable product/architecture owner;
7. current validation contract;
8. operational procedure;
9. diagnostics/evidence/reference as supporting provenance;
10. archive only for historical context.

Historical status, old next-action prose, prior branch results, and old milestone labels never override current owners.

## Update rules

- Current status, gate, blockers, or next transition → `00-project/work-plan.md`.
- Milestone order, formal state, or milestone scope → `00-project/roadmap.md`.
- Retained/deferred/evidence-gated but non-current work → `00-project/retained-commitments.md`.
- Execution, verification, freeze, publication, or closeout semantics → `00-project/execution-policy.md`.
- Durable product/architecture behavior → owning `10-product/` or `20-architecture/` contract.
- Acceptance obligation → `30-validation/`; completed measurements/results → `60-evidence/`.
- Operational procedure → `40-operations/`; investigation/probe → `50-diagnostics/`.
- Superseded material → `90-archive/` only after proving every still-current contract has another active owner.

Do not copy current status into architecture, diagnostics, or evidence merely for convenience. Do not rewrite historical evidence to sound current.

## Current S11 routing

S11 remains the active detector-effectiveness milestone. Current state and authorization are owned only by the [Work Plan](00-project/work-plan.md).

For an S11 detector change, use the repository-local `s11-detector-change` Skill. It performs bounded routing through the current implementation map, relevant failure history, current architecture/validation, and the mechanical governance contract.

Current durable S11 owners:

- detector responsibilities — [`20-architecture/s11-detector-responsibility-architecture.md`](20-architecture/s11-detector-responsibility-architecture.md);
- current executing control-flow map — [`20-architecture/s11-current-detector-logic-map.md`](20-architecture/s11-current-detector-logic-map.md);
- predecessor R21 truth-preserving detector repair architecture — [`20-architecture/s11-r21-truth-preserving-detector-repair-architecture.md`](20-architecture/s11-r21-truth-preserving-detector-repair-architecture.md);
- predecessor R21 validation/work specification — [`30-validation/s11-r21-truth-preserving-detector-repair-validation.md`](30-validation/s11-r21-truth-preserving-detector-repair-validation.md);
- current R22 Oil ownership/evidence replacement design — [`20-architecture/s11-r22-oil-ownership-evidence-replacement-architecture.md`](20-architecture/s11-r22-oil-ownership-evidence-replacement-architecture.md);
- current R22 acceptance contract — [`30-validation/s11-r22-oil-ownership-evidence-replacement-validation.md`](30-validation/s11-r22-oil-ownership-evidence-replacement-validation.md);
- diagnostic-only native path contract over R22 behavior — [`20-architecture/s11-r22-2-interface-path-diagnostics-architecture.md`](20-architecture/s11-r22-2-interface-path-diagnostics-architecture.md);
- transparent-interface redesign decision and public baseline probe — [`50-diagnostics/s11/s11-transparent-interface-detector-direction-assessment.md`](50-diagnostics/s11/s11-transparent-interface-detector-direction-assessment.md);
- O1 trace-only observation-layer contract — [`20-architecture/s11-interface-observability-witness-architecture.md`](20-architecture/s11-interface-observability-witness-architecture.md);
- O2 local label/freeze/evaluation procedure — [`40-operations/s11-o2-local-shadow-evaluation.md`](40-operations/s11-o2-local-shadow-evaluation.md);
- trace/shadow acceptance contract — [`30-validation/s11-interface-observability-witness-validation.md`](30-validation/s11-interface-observability-witness-validation.md);
- broader proposed physical-interface behavior repair — [`20-architecture/s11-physical-interface-evidence-repair-design.md`](20-architecture/s11-physical-interface-evidence-repair-design.md);
- proposed behavior acceptance contract — [`30-validation/s11-physical-interface-evidence-repair-validation.md`](30-validation/s11-physical-interface-evidence-repair-validation.md);
- sequential native path measurement procedure — [`40-operations/s11-r22-2-windows-interface-measurement.md`](40-operations/s11-r22-2-windows-interface-measurement.md);
- durable causal failure history — [`50-diagnostics/s11/s11-detector-mechanism-failure-registry.md`](50-diagnostics/s11/s11-detector-mechanism-failure-registry.md);
- canonical private-Windows reviewed truth — [`30-validation/windows-sample1-heating-coldstart-reviewed-truth.md`](30-validation/windows-sample1-heating-coldstart-reviewed-truth.md);
- current-candidate target-Windows field procedure — [`40-operations/s11-current-windows-field-qualification.md`](40-operations/s11-current-windows-field-qualification.md);
- general Windows GUI/package checklist — [`40-operations/manual-gui-windows-checklist.md`](40-operations/manual-gui-windows-checklist.md);
- completed S11 evidence collection — [`60-evidence/s11/`](60-evidence/s11/).

R18–R20 predecessor architecture/validation and earlier diagnostics remain historical provenance. They are reachable through the current logic map, failure registry, evidence collection, and Git history; this router does not enumerate them.

## S11 audit specifications and execution routing

The supplemental specifications form a sequence of design rationale and
follow-up audits, not competing current authorities:

| Document | Role | How to use it |
|---|---|---|
| [2026-09-17 execution review](50-diagnostics/s11/s11-observation-redesign-execution-review.md) | Grounds the bounded observation redesign and O1–O5 sequence against `577f98a` | Preserve design rationale and constraints; use the current architecture/validation for actual implementation |
| [2026-10-01 audit/work specification](50-diagnostics/s11/s11-detector-improvement-audit-and-work-spec-2026-10-01.md) | Audits progress at `85a01cd`, identifies target/pooling risks and proposes W0–W7 | Use its named work items through the current work-plan ledger; do not treat its dated pending/completion prose as live status |
| [2026-10-01 W4 progress audit](50-diagnostics/s11/s11-w4-progress-audit-and-continuation-plan-2026-10-01-ba1bd6a.md) | Audits `ba1bd6a` and proposes W4-R0–R5 continuation within W4 | Addendum to the prior specifications; preserve the original audit and use the live ledger for the active substep |

The W4 attachment is preserved byte-for-byte under the filename above; only the
transfer prefix and trailing `-1` were removed. W4-R0–R5 are internal continuation
steps, not a new milestone or a replacement acceptance contract.

The September attachment named
`s11-detector-redesign-review-and-execution-spec-2026-09-17-1.md`
was retained under `s11-observation-redesign-execution-review.md`.
The October filename is retained. Neither source audit is rewritten as work
progresses. October supplements September's direction; it does not restart O1
or supersede preserved runtime/provenance/acceptance contracts.

Use this route for subsequent work:

1. [S11 work-item ledger](00-project/work-plan.md#s11-work-item-ledger) — O/W mapping,
   live state, dependencies, next action and completion evidence.
2. [Witness Architecture](20-architecture/s11-interface-observability-witness-architecture.md)
   — target meanings and implementation responsibilities, including W1.
3. [Witness Validation](30-validation/s11-interface-observability-witness-validation.md)
   — controls and acceptance gates. A defined contract is not a passing result.
4. [O2 operations](40-operations/s11-o2-local-shadow-evaluation.md) — execute only
   the procedure selected by the ledger/current request; retained commands do not
   mean a closed experiment must be rerun.
5. [Evidence](60-evidence/s11/) — completed local checks and transferred Windows
   results, including rejected hypotheses and their limits.

The ledger is the only live W-status list. This router owns the relationship
between documents, not another copy of progress. W0–W4 refine work within O2;
W5/W6/W7 map to O3/O4/O5. O2 acceptance remains a separate gate before W5, not
an automatic consequence of finishing an experiment.

## Supporting collection indexes

- S11 diagnostics — [`50-diagnostics/s11/`](50-diagnostics/s11/)
- completed evidence — [`60-evidence/README.md`](60-evidence/README.md)
- retained/deferred commitments — [`00-project/retained-commitments.md`](00-project/retained-commitments.md)
- implementation/reference provenance — [`70-reference/implementation-reference-log.md`](70-reference/implementation-reference-log.md)

## Archive policy

`90-archive/` preserves superseded context and decision history. Archived documents may retain their original language. Repair links when needed for navigation, but never promote an archived statement back into current authority without updating a current owner.

- Supplemental observation redesign execution review — [50-diagnostics/s11/s11-observation-redesign-execution-review.md](50-diagnostics/s11/s11-observation-redesign-execution-review.md); supporting proposal, implemented definitions belong to the Witness Architecture.
