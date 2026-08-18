# Documentation Map and Authority

This file is the **documentation-routing SSOT**. Before creating, moving, renaming or editing anything under `docs/`, classify the document by responsibility and follow the authority/update rules below.

## Reading path for a fresh agent

Follow this path unless a task names a more specific authoritative owner:

1. [`00-project/roadmap.md`](00-project/roadmap.md) — milestone status and durable project sequence.
2. [`00-project/work-plan.md`](00-project/work-plan.md) — exact current gate, accepted baseline and next executable engineering action.
3. the relevant product or architecture owner under [`10-product/`](10-product/) or [`20-architecture/`](20-architecture/).
4. the applicable validation contract under [`30-validation/`](30-validation/).
5. only then use [`50-diagnostics/`](50-diagnostics/) and [`60-evidence/`](60-evidence/) for causal detail and historical proof.

The stable product specification is [`rotary_oil_level_tracker_ssot_spec.md`](rotary_oil_level_tracker_ssot_spec.md). It owns durable product requirements, not current milestone sequencing.

## Directory taxonomy

| Directory | Responsibility | Authority boundary |
|---|---|---|
| `00-project/` | roadmap, current work, lifecycle policy, retained/deferred routing | owns project sequencing; `retained-commitments.md` owns only non-current retained/deferred/evidence-gated work |
| `10-product/` | user-facing/product contracts | durable behavior and UX intent, not milestone status |
| `20-architecture/` | durable responsibility/design contracts | accepted ownership and invariants; no Worker/Auditor chronology |
| `30-validation/` | validation, benchmark and test-acceptance contracts | what must be demonstrated for acceptance; not execution history |
| `40-operations/` | executable Windows/package/manual procedures | how to perform operational checks; not proof that they passed |
| `50-diagnostics/` | investigations, probes and machine manifests | causal/reproducibility support; never current gate or architecture authority |
| `60-evidence/` | completed implementation/audit/validation records by milestone | historical proof; contemporaneous status prose is provenance, not current authority |
| `70-reference/` | external/reference and implementation-reference provenance | supporting provenance only |
| `90-archive/` | superseded historical context | not current authority; preserve for history/navigation |

## Authority hierarchy

When documents disagree, use this routing order for the responsibility in question:

1. stable product requirements: [`rotary_oil_level_tracker_ssot_spec.md`](rotary_oil_level_tracker_ssot_spec.md);
2. milestone status/sequence: [`00-project/roadmap.md`](00-project/roadmap.md);
3. exact active gate: [`00-project/work-plan.md`](00-project/work-plan.md);
4. retained but non-current commitments: [`00-project/retained-commitments.md`](00-project/retained-commitments.md);
5. durable product/architecture owner under `10-product/` or `20-architecture/`;
6. current acceptance contract under `30-validation/`;
7. operational procedure under `40-operations/`;
8. diagnostics/evidence/reference as supporting provenance;
9. archive only for historical context.

A historical Worker/Auditor “next gate”, old frame count or old milestone label never overrides the current roadmap/work plan.

## Update rules

- **Current status or next engineering action:** update `roadmap.md` and/or `work-plan.md`; do not duplicate the status into product/architecture/evidence files.
- **Retained, deferred or evidence-gated work that is not executable now:** route it to `retained-commitments.md`. Do not leave it as a pseudo-current backlog in architecture or product plans.
- **Durable product/architecture change:** update the owning `10-product/` or `20-architecture/` contract and its relevant validation owner.
- **Validation expectation:** update `30-validation/`; completed run/audit numbers belong in `60-evidence/`.
- **Operational procedure:** update `40-operations/`; the evidence that it passed belongs in `60-evidence/`.
- **Investigation/probe:** use `50-diagnostics/`; machine manifests are semantic evidence artifacts and must not be rewritten merely for taxonomy changes.
- **Completed evidence:** preserve contemporaneous facts. Link/classification repairs are allowed; do not rewrite history to sound current.
- **Superseded material:** move to `90-archive/` only after proving any still-current contract has another active owner.

## Current project routing

### Active authority and gate

- Current milestone/gate: [`00-project/work-plan.md`](00-project/work-plan.md)
- Current target-Windows procedure: [`40-operations/manual-gui-windows-checklist.md`](40-operations/manual-gui-windows-checklist.md)
- S11 durable detector responsibilities: [`20-architecture/s11-detector-responsibility-architecture.md`](20-architecture/s11-detector-responsibility-architecture.md)
- Active S11-R11 detector reset architecture: [`20-architecture/s11-r11-detector-architecture-reset.md`](20-architecture/s11-r11-detector-architecture-reset.md)
- Active S11-R11 validation contract: [`30-validation/s11-r11-detector-architecture-reset-validation.md`](30-validation/s11-r11-detector-architecture-reset-validation.md)
- S11-R10 secure-Windows root cause: [`50-diagnostics/s11/s11-r10-windows-path-and-residue-diagnostic.md`](50-diagnostics/s11/s11-r10-windows-path-and-residue-diagnostic.md)
- S11-R10 historical local implementation/replay evidence: [`60-evidence/s11/s11-r10-calibrated-path-and-layer.md`](60-evidence/s11/s11-r10-calibrated-path-and-layer.md)
- S11-R9 secure-Windows root cause: [`50-diagnostics/s11/s11-r9-windows-calibrated-observation-diagnostic.md`](50-diagnostics/s11/s11-r9-windows-calibrated-observation-diagnostic.md)
- S11-R9 historical local baseline: [`60-evidence/s11/s11-r9-calibrated-observation.md`](60-evidence/s11/s11-r9-calibrated-observation.md)
- S11-R8 secure-Windows root cause: [`50-diagnostics/s11/s11-r8-windows-calibrated-observation-diagnostic.md`](50-diagnostics/s11/s11-r8-windows-calibrated-observation-diagnostic.md)
- S11-R7 secure-Windows root cause: [`50-diagnostics/s11/s11-r7-windows-observation-recovery-diagnostic.md`](50-diagnostics/s11/s11-r7-windows-observation-recovery-diagnostic.md)
- S11-R7 checked-video direct-image reconciliation: [`50-diagnostics/s11/s11-r7-checked-video-direct-image-reconciliation.md`](50-diagnostics/s11/s11-r7-checked-video-direct-image-reconciliation.md)
- S11-R7 local implementation/replay evidence: [`60-evidence/s11/s11-r7-evidence-tiered-trajectory.md`](60-evidence/s11/s11-r7-evidence-tiered-trajectory.md)
- Active detector-baseline validation: [`30-validation/s11-real-field-detector-effectiveness.md`](30-validation/s11-real-field-detector-effectiveness.md)
- S11-R6 secure-Windows field failure: [`50-diagnostics/s11/s11-r6-secure-windows-field-failure.md`](50-diagnostics/s11/s11-r6-secure-windows-field-failure.md)
- Active user observation report architecture: [`20-architecture/result-observation-report-architecture.md`](20-architecture/result-observation-report-architecture.md)
- Active user observation report validation: [`30-validation/result-observation-report-validation.md`](30-validation/result-observation-report-validation.md)
- S11 legacy/current-frame retrospective sequence responsibility: [`20-architecture/initial-state-retrospective-reconstruction-architecture.md`](20-architecture/initial-state-retrospective-reconstruction-architecture.md)
- Legacy/current-frame retrospective implementation validation: [`30-validation/initial-state-retrospective-reconstruction-validation.md`](30-validation/initial-state-retrospective-reconstruction-validation.md)
- S5-B base observability architecture: [`20-architecture/s5b-oil-boundary-hypothesis-architecture.md`](20-architecture/s5b-oil-boundary-hypothesis-architecture.md)

### Historical detector provenance

- Accepted S11-R1 report evidence: [`60-evidence/s11/s11-user-observation-report-repair.md`](60-evidence/s11/s11-user-observation-report-repair.md)
- Historical pre-R6 subtractive detector design/evidence provenance: [`20-architecture/s11-subtractive-detector-simplification-architecture.md`](20-architecture/s11-subtractive-detector-simplification-architecture.md)
- Historical pre-R6 S11-R2 Foam/Spatial repair: [`20-architecture/s11-foam-spatial-authority-repair-architecture.md`](20-architecture/s11-foam-spatial-authority-repair-architecture.md)
- Historical pre-R6 S11-R2 detector validation: [`30-validation/s11-foam-spatial-authority-repair-validation.md`](30-validation/s11-foam-spatial-authority-repair-validation.md)
- Accepted S11-R2 implementation/replay evidence: [`60-evidence/s11/s11-r2-foam-spatial-authority-repair.md`](60-evidence/s11/s11-r2-foam-spatial-authority-repair.md)
- Accepted post-R2 baseline repair review: [`60-evidence/s11/s11-post-r2-baseline-validation-repair-review.md`](60-evidence/s11/s11-post-r2-baseline-validation-repair-review.md)
- Historical pre-R6 S11-R3 sequence/static-observability architecture: [`20-architecture/s11-sequence-observability-integrity-architecture.md`](20-architecture/s11-sequence-observability-integrity-architecture.md)
- Historical pre-R6 S11-R3 contract: [`30-validation/s11-sequence-observability-integrity-validation.md`](30-validation/s11-sequence-observability-integrity-validation.md)
- S11-R3 root-cause diagnostic: [`50-diagnostics/s11/s11-r3-sequence-observability-root-cause.md`](50-diagnostics/s11/s11-r3-sequence-observability-root-cause.md)
- S11-R3 local implementation/replay evidence: [`60-evidence/s11/s11-r3-sequence-observability-integrity.md`](60-evidence/s11/s11-r3-sequence-observability-integrity.md)
- Historical pre-R6 S11-R4 field-residual architecture: [`20-architecture/s11-r4-field-residual-authority-architecture.md`](20-architecture/s11-r4-field-residual-authority-architecture.md)
- Historical pre-R6 S11-R4 contract: [`30-validation/s11-r4-field-residual-authority-validation.md`](30-validation/s11-r4-field-residual-authority-validation.md)
- S11-R4 secure-Windows residual diagnostic: [`50-diagnostics/s11/s11-r4-windows-residual-authority-diagnostic.md`](50-diagnostics/s11/s11-r4-windows-residual-authority-diagnostic.md)
- S11-R4 local implementation/replay evidence: [`60-evidence/s11/s11-r4-field-residual-authority.md`](60-evidence/s11/s11-r4-field-residual-authority.md)
- Superseded S11-R5 sequence-first observation architecture: [`20-architecture/s11-r5-sequence-first-trajectory-architecture.md`](20-architecture/s11-r5-sequence-first-trajectory-architecture.md)
- Failed S11-R5 validation contract: [`30-validation/s11-r5-sequence-first-trajectory-validation.md`](30-validation/s11-r5-sequence-first-trajectory-validation.md)
- S11-R5 current-frame authority root cause: [`50-diagnostics/s11/s11-r5-current-frame-authority-root-cause.md`](50-diagnostics/s11/s11-r5-current-frame-authority-root-cause.md)
- S11-R5 secure-Windows field failure: [`50-diagnostics/s11/s11-r5-secure-windows-field-failure.md`](50-diagnostics/s11/s11-r5-secure-windows-field-failure.md)
- S11-R5 local implementation/replay evidence: [`60-evidence/s11/s11-r5-sequence-first-observation.md`](60-evidence/s11/s11-r5-sequence-first-observation.md)
- Superseded S11-R6 optics-aware observation architecture: [`20-architecture/s11-r6-optics-aware-observation-architecture.md`](20-architecture/s11-r6-optics-aware-observation-architecture.md)
- Failed S11-R6 validation contract: [`30-validation/s11-r6-optics-aware-observation-validation.md`](30-validation/s11-r6-optics-aware-observation-validation.md)
- S11-R6 checked-video diagnostic: [`50-diagnostics/s11/s11-r6-checked-video-reconciliation.md`](50-diagnostics/s11/s11-r6-checked-video-reconciliation.md)
- S11-R6 local implementation/replay evidence: [`60-evidence/s11/s11-r6-optics-aware-observation.md`](60-evidence/s11/s11-r6-optics-aware-observation.md)
- S11-R7 historical local baseline before its failed field gate: [`60-evidence/s11/s11-r7-evidence-tiered-trajectory.md`](60-evidence/s11/s11-r7-evidence-tiered-trajectory.md)
- S11-R8 historical local baseline before its failed field gate: [`60-evidence/s11/s11-r8-observation-recovery.md`](60-evidence/s11/s11-r8-observation-recovery.md)

### Supporting collections

- S11 diagnostics: [`50-diagnostics/s11/`](50-diagnostics/s11/)
- S11 historical evidence: [`60-evidence/s11/`](60-evidence/s11/)
- Retained/deferred commitments: [`00-project/retained-commitments.md`](00-project/retained-commitments.md)

## Archive policy

`90-archive/` preserves superseded context and decision history. Archived documents may keep their original language. Repair inbound/outbound links when needed for navigation, but do not promote archived statements back into current authority without an explicit current owner update.
