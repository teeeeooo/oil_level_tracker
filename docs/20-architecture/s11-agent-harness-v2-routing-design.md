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
- local research-output lifecycle: `docs/40-operations/experiment-artifact-lifecycle.md` + `scripts/experiment_artifacts.py`; local verification also runs from the existing pre-push hook.

## Existing features in detector research

The October 13 Artifact follow-up exposed a routing failure rather than an absent
feature or absent history. The Skill, logic map and recall index already named
Recipe exclusions, Artifact calibration, scoped reference diagnostics and the
closed D2/Local XY trials. Research nevertheless followed native detector inputs
without first accounting for the configured product path; a single-path masking
check then risked being proposed as another first test of existing defenses.

Use the existing owners to close that gap:

- The logic-map quick index now includes a compact setup/feature table, and its
  graph shows where Recipe masks, user Artifact templates, reviewed references,
  static preparation, confirmed initial state and optional Local XY enter. Source
  links own behavior; this is not a new feature registry or a new detector layer.
- The existing S11 Skill requires that table and the relevant successor history
  before choosing a hypothesis. Record actual/planned input state and the entry
  path in the existing design/preflight, including deliberate bypasses. Empty
  templates, default-OFF inputs and unavailable configuration are distinct.
- The existing governance checker requires `Existing feature coverage` and
  `Execution scope` in changed design/evidence blocks. Run it before a new
  experiment and publication. Presence/placeholder checks make omissions visible;
  they cannot verify scientific reasoning or force an agent to invoke the Skill.

The [maintenance contract](../30-validation/s11-detector-change-governance.md#maintenance-at-change-boundaries)
assigns updates to the change author and distinguishes feature-table, node/graph,
per-run record and checker impacts. The range checker now also covers the input
definitions for Recipe, geometry, scoped Artifact references, session and detector
settings; those files could previously change without a companion review. The
existing hook/CI entry remains shared. Path coverage is selective, so setup UI or
research-runner changes still require a semantic review when they change detector
inputs or claimed scope. Parameter-only changes need no artificial graph edit.

Representative routing checks: an Artifact/mask proposal must retrieve the D2 and
later Local XY dispositions; a raw native-head probe must name omitted candidate
rejection and completed resolution before making a product claim; a report-only
change may explain that runtime input features are unaffected. A read-only question
needs an answer, not a new report. Unrelated UI changes retain the existing checker
boundary. No automatic replay, option enablement, model fit, user-approval step or
global Skill installation follows. Frozen evidence is not rewritten for this rule.

The current host catalog already exposes the repository S11 Skill, and its existing
`allow_implicit_invocation: true` remains unchanged. The repository Skill stays the
single source for this workflow; no same-name global copy or new wrapper Skill is
introduced. Graphify can find callers but does not establish which Recipe options
were used by an experiment, so it remains an optional topology aid.

## Local research output closeout

The October 12 cleanup exposed a missing common closeout check: individual runners
already had temporary-directory or output-manifest patterns, but expanded traces,
source snapshots and repeated outputs accumulated across experiments. New runs now
use an exclusively created directory with declared inputs, relevant source hashes,
parameters and scratch/retained budgets. The existing witness replay's
`TemporaryDirectory` pattern remains the model for short-lived intermediate bundles;
no detector runner or application storage owner is replaced.

An explicit keep/reuse selection promotes only necessary evidence. The local tool
rejects duplicate retained payloads and removes only its own unselected intermediates.
The existing pre-push hook checks managed runs without deleting files. The operational
document owns the procedure; AGENTS and the existing S11 Skill route to it. Historical
machine records keep their bytes and verdicts. Local payloads undergo a value review:
concrete decision use, information loss, reproduction cost, smallest sufficient form
and a reassessment event. A reference or old verifier is not a retention warrant.
The tool requires the review record but cannot establish its substantive validity.
Additive retention maps explicitly retire obsolete payloads, and recovery rejects
retired or mixed selections instead of implying complete byte recovery. This gate checks storage, not scientific sufficiency,
detector acceptance or Windows field qualification.

## Optional derived code-topology pilot

Oil uses Graphify only as a local, disposable topology aid for `where`, callers, dependencies, and blast-radius discovery. `.graphifyignore` bounds the pilot to detector/application/publication owners, domain types needed to resolve those edges, and focused detector/S11 tests. `graphify-out/` is ignored and is not a repository artifact or SSOT.

The task-start freshness action is `scripts/update_graphify_s11.sh`, which performs an AST-only full build when no graph exists and an incremental AST update otherwise. Current Graphify 0.9.55 does not provide a Git-head authority field in `graph.json`; freshness therefore comes from the tool manifest/content hashes plus a task-start refresh, not from trusting a remembered commit label. `graphify watch .` is optional for long source-editing sessions and is never a required gate.

Initial smoke comparison against the current logic map found the expected relationships for `OilObservationResolver` → lifecycle owner, `ObservationSequenceResolver` → Oil/Foam resolvers, `tracking_sample_from_detection` → `TrackingSample`, and `CsvExporter` → `AnalysisResult`. The first bounded scope omitted the domain type owner for `TrackingSample`; that miss was detected and corrected by adding `src/oil_tracker/domain/**`. This is pilot evidence, not a claim that all Graphify edges are complete or authoritative.

The final bounded scope after smoke correction contains 188 code files, 2,998 nodes and 12,572 links with zero semantic/LLM extraction. The first correction added domain owners so `TrackingSample` resolved to `domain/results.py`; a second correction expanded storage owners after the benchmark showed that an overly narrow storage scope hid the direct `redetection_workspace.py` caller of `JsonlDebugTraceWriter`. A background `graphify watch .` probe detected a temporary one-file source edit and rebuilt automatically; the source was then restored and a one-shot refresh returned the graph to the clean tree. `watchdog` is an optional local Graphify dependency needed only for watch mode.

Five representative exact-symbol investigations compared `graphify affected --depth 2` with `rg`. Literal `rg` was roughly an order of magnitude faster on this host (about 0.11–0.15 s versus 1.08–1.12 s per Graphify command), while Graphify returned classified/transitive caller, test and indirect dependency relationships that literal search did not provide. The operating rule is therefore: exact symbol/literal lookup stays with source search; Graphify is used when relational topology or blast radius is the question. A broad natural-language publication query returned hundreds of nodes and was too noisy to be the default retrieval path.

Graphify's hook installer was also tested in a temporary repository configured with `core.hooksPath=.githooks`: it preserved an existing `pre-push` byte-for-byte and added only `post-commit` / `post-checkout` plus its merge driver. Those hooks remain **not installed** in this Oil checkout during the bounded pilot. Promote them only after repeated real S11 tasks show that automatic background freshness is worth the extra local hook surface.

Local tool maintenance is manual and non-blocking: Graphify is installed as the `graphifyy` uv tool with the optional `watchdog` dependency. Do not auto-upgrade it from Git hooks, Skills, or CI. When intentionally upgrading (`uv tool upgrade graphifyy`), record the new version, run `scripts/update_graphify_s11.sh`, confirm `graphify hook status` still leaves repository hooks uninstalled unless explicitly promoted, and repeat a small exact-symbol topology smoke against current source. No separate stale-marker hook is needed during the pilot because task-start refresh plus optional agent-managed watch already owns freshness.

## Documentation lifecycle routing

The [documentation router](../README.md#document-maintenance-lifecycle) owns
creation, closeout and archival rules. The [date catalog](../catalog-by-created-date.md)
is derived navigation, not a live status list or a source of active dependencies.
The Work Plan remains the single current gate; the recall index keeps short
causal routes rather than reproducing experimental chronology.

The [2026-10-03 migration record](../90-archive/00-project/2026/2026-10-03-docs-reorganization.md)
records the relocation of seven explicitly historical A–D/R2–R4 contracts.
Their safety/negative-family obligations remain in the current responsibility
architecture and cross-revision validation, while source and fixtures are unchanged.
The twenty other audit candidates remain in place where clause-level succession
is unresolved. Current operational anchors and source audit attachments are preserved.

## History Review

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-PHASE-INITIAL`, `PUBLICATION-PROVENANCE`, `TRACE-PUBLICATION`, `OIL-PHASE-DRAIN`, `FOAM-EPISODE`
- Failure-registry entries: `S11-F04`, `S11-F06`, `S11-F07`, `S11-F08`, `S11-F09`, `S11-F10`
- Prior mechanisms reviewed: the 2026-10-03 docs audit, historical A–D/R2–R4 contracts, current responsibility architecture §Historical preservation boundary and cross-revision validation §Controlled preservation surface; current logic-map quick index and affected publication/lifecycle/Foam nodes; failure-registry no-repeat rules for false Foam dynamics, lifecycle dead ends, provenance ambiguity, and case-specific escape hatches; canonical reviewed Windows truth; current cross-revision detector-effectiveness validation; historical R7–R12 Windows procedure sections.
  The October 13 extension also reviews existing Recipe/mask/Artifact callers and
  the [D2 registration](../60-evidence/s11/2026-10-08-d2-recipe-artifact-comparison.md)
  and [Local XY successor](../60-evidence/s11/2026-10-09-local-xy-implementation.md)
  records routed by the recall index.
- Prior mechanisms rejected: revision-specific R7–R12 execution routing is rejected as current procedure because it can apply obsolete detector identities and acceptance assumptions; broad historical scanning is rejected because current logic-map/failure indexes provide bounded routing.
- Preserved contracts: exact same-frame Oil/Foam provenance, independent validity/ownership, fail-closed ambiguity, reviewed physical truth as the field oracle, field FAIL until current acceptance is satisfied, and no private/case-specific detector control flow.
- Existing feature coverage: Recipe settings/spatial masks, candidate Artifact rejection, reference-only diagnostics, automatic static preparation, run/initial-state inputs, optional Local XY and completed publication were traced to the existing owners; the D2 and Local XY successor results supply the relevant failed-use history. The checker now includes their core input definitions as well as consuming code. This process change does not alter any actual Recipe or runtime option.
- Execution scope: repository Skill/map/governance maintenance, source and saved-record inspection, and checker tests only. No detector, video, training, Windows or report replay is performed; no efficacy claim follows from the new fields or diagram.
- Difference from prior failures: existing setup features and actual run coverage must now be considered before a detector hypothesis, with missing review fields and previously uncovered core input changes caught by the existing checker. The same change author maintains the affected map claims and checker boundaries. This extends bounded recall and document closeout without copying feature truth into a new Skill, adding detector authority, changing lifecycle/Foam predicates, or reopening frozen experiments. Current authorization, field disposition and immutable evidence remain preserved.
- Logic-map impact: UPDATED — feature rows now link the core input definitions and detector-setting service; update rules route to the existing governance maintenance contract. Executing control flow and Mermaid edges remain unchanged by this maintenance refinement.
- Failure-registry impact: NONE — no causal mechanism, no-repeat rule, or field-risk status changes; the migration only routes agents to the existing registry more directly.
