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

## Optional derived code-topology pilot

Oil uses Graphify only as a local, disposable topology aid for `where`, callers, dependencies, and blast-radius discovery. `.graphifyignore` bounds the pilot to detector/application/publication owners, domain types needed to resolve those edges, and focused detector/S11 tests. `graphify-out/` is ignored and is not a repository artifact or SSOT.

The task-start freshness action is `scripts/update_graphify_s11.sh`, which performs an AST-only full build when no graph exists and an incremental AST update otherwise. Current Graphify 0.9.55 does not provide a Git-head authority field in `graph.json`; freshness therefore comes from the tool manifest/content hashes plus a task-start refresh, not from trusting a remembered commit label. `graphify watch .` is optional for long source-editing sessions and is never a required gate.

Initial smoke comparison against the current logic map found the expected relationships for `OilObservationResolver` → lifecycle owner, `ObservationSequenceResolver` → Oil/Foam resolvers, `tracking_sample_from_detection` → `TrackingSample`, and `CsvExporter` → `AnalysisResult`. The first bounded scope omitted the domain type owner for `TrackingSample`; that miss was detected and corrected by adding `src/oil_tracker/domain/**`. This is pilot evidence, not a claim that all Graphify edges are complete or authoritative.

The corrected local graphifyy 0.9.55 baseline contains 173 scoped code files, 2,721 nodes and 11,489 links with zero semantic/LLM extraction. A background `graphify watch .` probe detected a temporary one-file source edit and rebuilt automatically; the source was then restored and a one-shot refresh returned the graph to the clean tree. `watchdog` is an optional local Graphify dependency needed only for watch mode.

Graphify's hook installer was also tested in a temporary repository configured with `core.hooksPath=.githooks`: it preserved an existing `pre-push` byte-for-byte and added only `post-commit` / `post-checkout` plus its merge driver. Those hooks remain **not installed** in this Oil checkout during the bounded pilot. Promote them only after repeated real S11 tasks show that automatic background freshness is worth the extra local hook surface.

## History Review

- Logic-map nodes: `PUBLICATION-PROVENANCE`, `TRACE-PUBLICATION`, `OIL-PHASE-DRAIN`, `FOAM-EPISODE`
- Failure-registry entries: `S11-F07`, `S11-F08`, `S11-F09`, `S11-F10`
- Prior mechanisms reviewed: current logic-map quick index and affected publication/lifecycle/Foam nodes; failure-registry no-repeat rules for false Foam dynamics, lifecycle dead ends, provenance ambiguity, and case-specific escape hatches; canonical reviewed Windows truth; current cross-revision detector-effectiveness validation; historical R7–R12 Windows procedure sections.
- Prior mechanisms rejected: revision-specific R7–R12 execution routing is rejected as current procedure because it can apply obsolete detector identities and acceptance assumptions; broad historical scanning is rejected because current logic-map/failure indexes provide bounded routing.
- Preserved contracts: exact same-frame Oil/Foam provenance, independent validity/ownership, fail-closed ambiguity, reviewed physical truth as the field oracle, field FAIL until current acceptance is satisfied, and no private/case-specific detector control flow.
- Difference from prior failures: this migration changes only instruction/procedure routing; it does not add detector authority, alter lifecycle/Foam predicates, reinterpret field evidence, or make historical output an oracle.
- Logic-map impact: NONE — detector implementation ownership and executing control flow are unchanged by the harness/procedure migration.
- Failure-registry impact: NONE — no causal mechanism, no-repeat rule, or field-risk status changes; the migration only routes agents to the existing registry more directly.
