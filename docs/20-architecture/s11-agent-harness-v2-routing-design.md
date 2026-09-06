# S11 Agent Harness V2 Routing Design

**Status:** `ACTIVE ROUTING DESIGN` — repository process only; no detector behavior change.

## Decision

Move generic execution posture to the user-level harness and keep S11-specific procedure in repository-local Skills. `s11-detector-change` owns bounded current-owner/failure recall; `windows-qualification` owns candidate-current target-Windows routing. The mechanical History Review / Detector Governance schema remains in `docs/30-validation/s11-detector-change-governance.md` and the existing checker remains authoritative.

The active Windows field route is separated from revision-specific R7–R12 instructions. Historical R7–R12 procedures move to `docs/90-archive/s11/windows-r7-r12-field-procedures.md`; the current procedure resolves whichever candidate `docs/00-project/work-plan.md` names and never hard-codes a revision.

This change does not alter detector source, thresholds, candidate authority, lifecycle, Foam/Oil composition, publication, reviewed truth, or field disposition. The harness commit is based directly on the accepted R21 exact head, so R21 is immediately usable before main integration while the Work Plan remains the authority for whichever candidate is current later.

## Ownership after migration

- repository overlay/routing: `AGENTS.md`;
- current gate/candidate: `docs/00-project/work-plan.md`;
- past-dependent routing: `docs/00-project/recall-index.md`;
- S11 task procedure: `.agents/skills/s11-detector-change/SKILL.md`;
- Windows qualification procedure: `.agents/skills/windows-qualification/SKILL.md` + `docs/40-operations/s11-current-windows-field-qualification.md`;
- governance record/checker contract: `docs/30-validation/s11-detector-change-governance.md` + `scripts/check_detector_governance.py`;
- current detector/failure truth: existing logic map and failure registry.

## History Review

- Logic-map nodes: `PUBLICATION-PROVENANCE`, `TRACE-PUBLICATION`, `OIL-PHASE-DRAIN`, `FOAM-EPISODE`
- Failure-registry entries: `S11-F07`, `S11-F08`, `S11-F09`, `S11-F10`
- Prior mechanisms reviewed: current logic-map quick index and affected publication/lifecycle/Foam nodes; failure-registry no-repeat rules for false Foam dynamics, lifecycle dead ends, provenance ambiguity, and case-specific escape hatches; canonical reviewed Windows truth; current cross-revision detector-effectiveness validation; historical R7–R12 Windows procedure sections.
- Prior mechanisms rejected: revision-specific R7–R12 execution routing is rejected as current procedure because it can apply obsolete detector identities and acceptance assumptions; broad historical scanning is rejected because current logic-map/failure indexes provide bounded routing.
- Preserved contracts: exact same-frame Oil/Foam provenance, independent validity/ownership, fail-closed ambiguity, reviewed physical truth as the field oracle, field FAIL until current acceptance is satisfied, and no private/case-specific detector control flow.
- Difference from prior failures: this migration changes only instruction/procedure routing; it does not add detector authority, alter lifecycle/Foam predicates, reinterpret field evidence, or make historical output an oracle.
- Logic-map impact: NONE — detector implementation ownership and executing control flow are unchanged by the harness/procedure migration.
- Failure-registry impact: NONE — no causal mechanism, no-repeat rule, or field-risk status changes; the migration only routes agents to the existing registry more directly.
