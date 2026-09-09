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
- durable causal failure history — [`50-diagnostics/s11/s11-detector-mechanism-failure-registry.md`](50-diagnostics/s11/s11-detector-mechanism-failure-registry.md);
- canonical private-Windows reviewed truth — [`30-validation/windows-sample1-heating-coldstart-reviewed-truth.md`](30-validation/windows-sample1-heating-coldstart-reviewed-truth.md);
- current-candidate target-Windows field procedure — [`40-operations/s11-current-windows-field-qualification.md`](40-operations/s11-current-windows-field-qualification.md);
- general Windows GUI/package checklist — [`40-operations/manual-gui-windows-checklist.md`](40-operations/manual-gui-windows-checklist.md);
- completed S11 evidence collection — [`60-evidence/s11/`](60-evidence/s11/).

R18–R20 predecessor architecture/validation and earlier diagnostics remain historical provenance. They are reachable through the current logic map, failure registry, evidence collection, and Git history; this router does not enumerate them.

## Supporting collection indexes

- S11 diagnostics — [`50-diagnostics/s11/`](50-diagnostics/s11/)
- completed evidence — [`60-evidence/README.md`](60-evidence/README.md)
- retained/deferred commitments — [`00-project/retained-commitments.md`](00-project/retained-commitments.md)
- implementation/reference provenance — [`70-reference/implementation-reference-log.md`](70-reference/implementation-reference-log.md)

## Archive policy

`90-archive/` preserves superseded context and decision history. Archived documents may retain their original language. Repair links when needed for navigation, but never promote an archived statement back into current authority without updating a current owner.
