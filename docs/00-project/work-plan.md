# Current Work Plan

- **Document status:** `VALIDATING`
- **Active milestone:** `S5-B — Oil-boundary hypothesis architecture`
- **Branch:** `feature/oil-boundary-temporal-tracking`
- **Task-start exact head:** `faab56316acf61dd3e4838074335d77d20ae6377`
- **Task-start exact parent:** `b12cd4d51d9b6ffef7abea390ac669560f89b116`
- **Orchestrator decision:** `NEEDS_DOCUMENT_REPAIR`
- **Current gate:** Bounded trust-boundary documentation repair
- **Next gate:** Independent trust-boundary redesign architecture re-audit
- **Source implementation:** Blocked until architecture re-audit `PASS`
- **Controlled comparison:** Blocked until the implementation exact head passes independent source audit

This is the operational SSOT for the active milestone. Closeout follows the [documentation closeout policy](./closeout-policy.md). Branch-local work is not formal completion, and this plan makes no `DONE` or S5-B completion claim.

## Material findings

The Orchestrator review identified three current blockers:

1. successful evidence-unavailable and pipeline execution failure collapse into one canonical unavailable outcome;
2. the failed-frame model can inherit successful unavailable stable-clear authority, leaving tracker and smoothing behavior ambiguous;
3. the [Roadmap](./roadmap.md) still names the obsolete production-cutover audit as the next gate.

These findings require documentation repair before source implementation resumes.

## Architecture resolution

The governing [S5-B architecture](../20-architecture/s5b-oil-boundary-hypothesis-architecture.md) now requires:

- distinct concrete `EvidenceUnavailableOutcome` and `PipelineFailureOutcome` variants;
- successful current observations and normal temporal decisions only on `SuccessfulPipelineFrame`;
- a `FailedPipelineFrame` with required failure reason and bounded diagnostics, but no evidence tuples, current observation or normal temporal decision;
- a closed tracker/smoothing action set derived from concrete variant and semantic mode;
- successful unavailable pending/stable transitions separated from execution failure;
- pipeline failure fixed to no tracker update and smoothing preserve, with no temporal-counter progression;
- one canonical normalizer as the sole production authority for selection, numeric oil, confidence, actions, fill-state input, flags and debug projection.

The selected compatibility policy supersedes the current repeated-failure stable-clear behavior. Only successful evidence-unavailable may reach its bounded stable-clear transition. The existing failure-clear source test is a later bounded implementation replacement target; no source or test is changed in this task.

## Current bounded scope

Authorized changes are limited to:

- `docs/20-architecture/s5b-oil-boundary-hypothesis-architecture.md`;
- `docs/00-project/work-plan.md`;
- `docs/00-project/roadmap.md`.

Observation extraction, proposal/hypothesis algorithms, likelihood formulas, thresholds, successful-frame temporal transitions, external `PhaseDetection`, Recipe/settings persistence, benchmark/truth/fixture/result/CSV/debug schemas, detector version, dependencies and S5-A Foam ownership remain unchanged.

Source implementation, tests, controlled comparison, canonical validation, Windows/manual validation, packaging, merge and cleanup remain blocked or outside this gate.

## Required downstream sequence

After this documentation repair:

1. independent trust-boundary redesign architecture re-audit;
2. bounded source implementation only after architecture `PASS`;
3. independent exact-head source audit;
4. controlled base/feature comparison only after source audit `PASS`.

S6 cannot start before formal S5-B completion.

## Deferred controlled accuracy findings

The two controlled accuracy findings remain deferred and unchanged:

- clear-oil raw detection coverage is `0.5714285714285714`, below the expected `1.0`;
- `no-interface-to-visible` frame 3 still has no numeric raw oil recovery.

They remain detector-accuracy findings. This documentation repair neither relaxes their expectations nor uses them to justify a weaker trust boundary.

## Documentation verification contract

This GitHub-only Worker must verify before closeout:

- the resulting commit changes exactly the three authorized Markdown files;
- the complete commit diff contains no source, test, dependency or workflow delta;
- relative links and case-sensitive paths resolve to existing repository paths;
- Markdown replacements are complete and retain a final newline;
- the obsolete production-cutover-audit next gate is removed;
- no generic unavailable outcome owns both successful unavailability and execution failure;
- failed-frame tracker and smoothing semantics are consistent throughout the architecture.

No local test, Markdown checker, `git diff --check`, canonical suite, Windows check or packaging run is claimed by this GitHub-only task.

## Next action

Perform an independent trust-boundary redesign architecture re-audit against the immutable resulting documentation head. Source implementation remains prohibited until that audit returns `PASS`.

## Latest recorded closeout

- **Result:** Production-result trust-boundary clarification prepared as a bounded documentation-only repair.
- **Task-start exact head:** `faab56316acf61dd3e4838074335d77d20ae6377`.
- **Task-start exact parent:** `b12cd4d51d9b6ffef7abea390ac669560f89b116`.
- **Decision recorded:** `NEEDS_DOCUMENT_REPAIR`.
- **Architecture policy:** Distinct evidence-unavailable/failure variants; execution failure is no-update/preserve and cannot obtain successful unavailable stable-clear authority.
- **Current gate:** Bounded trust-boundary documentation repair.
- **Next gate:** Independent trust-boundary redesign architecture re-audit.
- **Deferred findings:** The two controlled oil accuracy findings remain unchanged.
