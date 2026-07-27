# Current Work Plan

- **Document status:** `VALIDATING`
- **Active milestone:** `S5-B — Oil-boundary hypothesis architecture`
- **Branch:** `feature/oil-boundary-temporal-tracking`
- **Task-start exact head:** `5f8749e8c1a508646d04026b2f1135db1b5be369`
- **Task-start exact parent:** `faab56316acf61dd3e4838074335d77d20ae6377`
- **Orchestrator decision:** `NEEDS_DOCUMENT_REPAIR`
- **Current gate:** Independent trust-boundary redesign architecture re-audit
- **Source implementation:** Blocked until architecture re-audit `PASS`
- **Controlled comparison:** Blocked until implementation exact-head source audit `PASS`

This is the operational SSOT for the active milestone. Closeout follows the [documentation closeout policy](./closeout-policy.md). Branch-local documentation repair is not formal completion, and this plan makes no `DONE` or S5-B completion claim.

## Current state

The bounded documentation repair is complete on the feature head:

- distinct successful evidence-unavailable and pipeline-failure outcomes are defined;
- pipeline failure is fixed to hypothesis-state no-commit, compatibility tracker `NO_UPDATE` and smoothing `PRESERVE`;
- Glass-local hypothesis temporal evaluation is provisional and cannot mutate live state before trust-boundary validation;
- one transactional trust-boundary owner validates canonical evidence, provisional decision, proposed next state, resources, actions and the prepared publishable outcome;
- only that owner may commit the proposed next Glass-local temporal state, exactly once and only after all validation succeeds;
- hypothesis temporal state and the downstream compatibility smoothing/fill-state tracker are explicitly separate owners;
- successful evidence-unavailable may progress its stability counter only through a valid transactional commit;
- every execution, validation, normalization, outcome-construction or commit failure preserves both state owners;
- the [Roadmap](./roadmap.md) is already aligned and remains unchanged by this repair.

The architecture contract is recorded in the [S5-B architecture](../20-architecture/s5b-oil-boundary-hypothesis-architecture.md). Exact Python class, module and helper names remain available to the later implementation Worker, but provisional evaluation, validation and atomic commit ordering are mandatory.

## Compatibility and bounded scope

This documentation repair changes mutation timing and authority only. It does not change:

- observation extraction, proposal or hypothesis algorithms;
- likelihood formulas, thresholds or accepted successful temporal transition behavior;
- bounded Glass-local state limits;
- external `PhaseDetection`;
- Recipe/settings persistence;
- benchmark, truth, fixture, result, CSV or debug schema versions;
- detector version or dependencies;
- S5-A Foam ownership or behavior;
- controlled accuracy expectations.

The completed change is limited to:

- `docs/20-architecture/s5b-oil-boundary-hypothesis-architecture.md`;
- `docs/00-project/work-plan.md`.

Source, tests, dependencies, workflows, the Roadmap, controlled comparison, canonical validation, Windows/manual validation, packaging, merge and cleanup remain unchanged or outside this gate.

## Required downstream sequence

1. Independent trust-boundary redesign architecture re-audit of the immutable documentation head.
2. Bounded source implementation only after architecture re-audit `PASS`.
3. Independent exact-head source audit of the transactional implementation.
4. Controlled base/feature comparison only after source audit `PASS`.

Old direct-mutation and new transactional temporal paths must not simultaneously own production state. S6 cannot start before formal S5-B completion.

## Deferred controlled accuracy findings

The two controlled accuracy findings remain deferred and unchanged:

- clear-oil raw detection coverage is `0.5714285714285714`, below the expected `1.0`;
- `no-interface-to-visible` frame 3 still has no numeric raw oil recovery.

They remain detector-accuracy findings. This documentation repair neither relaxes their expectations nor uses them to justify a weaker trust boundary.

## Documentation verification contract

This GitHub-only Worker verifies before closeout that:

- the resulting commit changes exactly the two authorized Markdown files;
- the complete diff contains no source, test, dependency, workflow or Roadmap delta;
- relative links and case-sensitive paths resolve to existing repository paths;
- Markdown replacements retain final newlines;
- no wording permits live hypothesis temporal mutation before canonical evidence and final proposal validation;
- malformed successful results cannot change state before conversion to `PipelineFailureOutcome`;
- one transactional owner and exactly-once commit semantics are consistent;
- the Current gate is independent architecture re-audit.

No local `git diff --check`, Markdown checker, test, benchmark, application, canonical suite, Windows check or packaging run is claimed by this GitHub-only task.

## Next action

Perform an independent trust-boundary redesign architecture re-audit against the immutable resulting documentation head. Source implementation remains prohibited until that audit returns `PASS`.

## Latest recorded closeout

- **Result:** Bounded temporal commit-boundary documentation repair completed on the feature head.
- **Task-start exact head:** `5f8749e8c1a508646d04026b2f1135db1b5be369`.
- **Task-start exact parent:** `faab56316acf61dd3e4838074335d77d20ae6377`.
- **Decision recorded:** `NEEDS_DOCUMENT_REPAIR`.
- **Completed architecture:** Distinct evidence-unavailable/failure outcomes, failure `NO_UPDATE`/`PRESERVE`, provisional temporal evaluation and one exactly-once atomic Glass-local state commit boundary.
- **Bookkeeping:** Roadmap alignment remains current; the Work Plan gate is no longer the repair stage.
- **Current gate:** Independent trust-boundary redesign architecture re-audit.
- **Source implementation:** Blocked pending architecture re-audit `PASS`.
- **Deferred findings:** The two controlled oil accuracy findings remain unchanged.
- **Resulting exact SHA:** Reported by the Worker final report, not self-recorded in this commit.
