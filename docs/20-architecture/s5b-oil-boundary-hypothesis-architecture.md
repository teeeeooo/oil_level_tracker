# S5-B Oil-Boundary Hypothesis Architecture

**Status:** `ACTIVE` trust-boundary clarification contract; source implementation is blocked pending independent architecture re-audit  
**Milestone:** [S5-B](../00-project/work-plan.md)

This document governs the S5-B internal observation, proposal, semantic-hypothesis, temporal-decision, pipeline-frame and canonical production-result boundaries. The independently accepted S5-B1 typed hypothesis architecture and the S5-B2 typed production cutover remain the foundation. This clarification closes the remaining success/failure and smoothing-authority ambiguity without changing detector algorithms or external contracts.

`ACTIVE` identifies the governing architecture. It does not authorize source implementation, controlled comparison, canonical validation, Windows/manual validation, packaging, merge, cleanup or accuracy acceptance. The next gate is an independent architecture re-audit of this exact documentation head.

## Purpose

Preserve the accepted extraction and reasoning pipeline while making contradictory production states structurally unrepresentable. A closed discriminated model must carry only state-legal fields, and one fail-closed normalizer must create the sole canonical values consumed by production.

The repair is structural rather than another field-validator patch. Concrete variants determine meaning; independent optional fields or booleans must not recreate a second discriminator.

## Retained algorithmic flow

```text
masked frame evidence
→ immutable raw edge observations
→ bounded-diameter deterministic Y proposals
→ broad region-step + narrow line/pulse evidence
→ continuous boundary/artifact/ambiguity likelihoods
→ soft static prior
→ deterministic semantic deduplication
→ discriminated current observation
→ successful-frame temporal decision OR failed pipeline frame
→ trust-boundary normalizer
→ closed canonical production outcome
→ existing PhaseDetection compatibility projection
```

The clarification begins after semantic evidence is produced. Observation extraction, proposal formation, hypothesis scoring, likelihood formulas and thresholds, successful-frame temporal transition policy and Glass-local bounds remain unchanged.

## Retained evidence contracts

Raw observations remain immutable bounded scalar records with deterministic identities and provenance. Proposal construction remains input-order independent, bounded by maximum Y diameter, member count and proposal count, and cannot form a single-link chaining bridge.

Broad evidence continues to measure signed region transitions, visible support, scale/polarity consistency and glare/exclusion conflicts. Narrow evidence continues to measure peak support, paired-edge structure, pulse symmetry, center offset, scale persistence and structural/static overlap. Missing support is unavailable evidence, not scored negative evidence.

Semantic hypotheses continue to expose finite normalized boundary, artifact and ambiguity likelihoods, evidence availability, visibility, polarity, bounded representative Y and deterministic identity/content/provenance. Ambiguity remains first-class. No-interface remains positive typed evidence rather than candidate absence. Static evidence remains a bounded soft prior and never deletes current observations.

## Why the generic result model is rejected

The current generic records duplicate meaning across independent fields:

- frame availability and optional failure reason;
- temporal status and observation kind;
- current-observation class and stored kind;
- selected identity and projected Y;
- generic smoothing-clear boolean and transition meaning;
- no-interface availability and positive acceptance;
- declared resource counts and retained tuples.

That shape permits class/status/identity/Y disagreement, failure frames with successful temporal authority, forged smoothing clear, positive no-interface acceptance without evidence and other cross-field contradictions. Adding another conditional validator does not close the state space.

The replacement therefore uses closed concrete variants. A generic unavailable result with optional `failure_reason`, an `is_failure` boolean or an equivalent independent discriminator is prohibited.

## Closed current-observation model

Concrete current-observation class derives `kind`; `kind` is not a constructor argument or independently stored field.

| Variant | Legal owned fields | Structurally absent fields |
|---|---|---|
| `BoundaryObservation` | canonical hypothesis, bounded alternatives, visibility and diagnostics | failure reason, no-interface acceptance, temporal action |
| `NoInterfaceObservation` | available positive no-interface evidence, full/empty evidence inputs, visibility and diagnostics | selected boundary identity/Y, failure reason, temporal action |
| `AmbiguousObservation` | bounded competing options, optional available diagnostic no-interface evidence, reason and diagnostics | accepted boundary Y, positive no-interface acceptance, clear authority |
| `UnavailableObservation` | successful-execution evidence-unavailability reason, visibility and bounded diagnostics | boundary selection/Y, positive no-interface acceptance, failure reason, clear authority |

`UnavailableObservation` means the pipeline executed successfully but current evidence is insufficient or unavailable. It never represents execution failure.

## Closed successful-frame temporal decisions

Normal temporal decisions exist only inside `SuccessfulPipelineFrame`. Concrete decision class derives status, observation kind, tracker action and smoothing action.

| Variant | Legal owned fields | Derived authority |
|---|---|---|
| `BoundaryAcceptedDecision` | selected canonical hypothesis, accepted source Y, finite confidence/margin, diagnostics and `acceptance_mode` | boundary acceptance action from `initial`, `continuous` or `reacquired` |
| `NoInterfaceAcceptedDecision` | available positive no-interface evidence, finite confidence/margin, fill-state evidence and bounded stability mode | no tracker update; smoothing action from pending/stable mode |
| `AmbiguousDecision` | bounded diagnostic options, optional diagnostic projected Y, finite confidence/margin and reason | preserve/no update only |
| `EvidenceUnavailableDecision` | successful-execution unavailability reason, visibility, finite confidence/diagnostics and bounded stability mode | no tracker update; smoothing action from pending/stable mode |
| `ReacquisitionPendingDecision` | pending canonical identity/content, finite diagnostics and reason | preserve/no update only; no accepted numeric Y |

Status and observation kind are never independent constructor inputs. Diagnostic projected Y is not accepted oil Y and cannot become raw oil output or candidate selection.

## Closed tracker and smoothing actions

The implementation may choose exact enum names, but the legal action set and mapping are mandatory.

### Tracker action set

- `ACCEPT_BOUNDARY`: append/accept the canonical boundary value.
- `NO_UPDATE`: do not mutate oil tracker state.

### Smoothing action set

- `PRESERVE`: retain applicable oil smoothing history.
- `CLEAR_BEFORE_ACCEPT`: clear stale history before accepting a reacquired boundary.
- `CLEAR_STALE_AFTER_STABLE_ABSENCE`: clear stale oil history after a bounded successful absence transition.

No generic `clear_smoothing: bool` is accepted at the production boundary.

| Canonical situation | Tracker action | Smoothing action |
|---|---|---|
| accepted boundary, `initial` | `ACCEPT_BOUNDARY` | `PRESERVE` |
| accepted boundary, `continuous` | `ACCEPT_BOUNDARY` | `PRESERVE` |
| accepted boundary, `reacquired` | `ACCEPT_BOUNDARY` | `CLEAR_BEFORE_ACCEPT` |
| accepted no-interface, unstable/pending | `NO_UPDATE` | `PRESERVE` |
| accepted no-interface, bounded stable transition | `NO_UPDATE` | `CLEAR_STALE_AFTER_STABLE_ABSENCE` |
| successful evidence unavailable, unstable/pending | `NO_UPDATE` | `PRESERVE` |
| successful evidence unavailable, bounded stable transition | `NO_UPDATE` | `CLEAR_STALE_AFTER_STABLE_ABSENCE` |
| ambiguous | `NO_UPDATE` | `PRESERVE` |
| reacquisition pending | `NO_UPDATE` | `PRESERVE` |
| pipeline execution failure | `NO_UPDATE` | `PRESERVE` |

The successful evidence-unavailable stable clear is explicitly retained as accepted temporal behavior. Pipeline failure is not an evidence-unavailable sample and cannot advance that transition.

## Closed pipeline-frame model

The outer frame removes the generic `available`/optional-failure pair.

### `SuccessfulPipelineFrame`

Owns only:

- immutable observations, proposals and hypotheses;
- recomputable resource inputs;
- one legal current observation;
- one legal normal temporal decision;
- bounded JSON-safe diagnostics.

It has no execution-failure reason. A successful frame may legally contain `EvidenceUnavailableDecision`.

### `FailedPipelineFrame`

Owns only:

- required canonical failure reason;
- bounded failure stage/category;
- bounded visibility and debug-safe diagnostics needed for compatibility projection.

It structurally has:

- no current observation;
- no normal temporal decision;
- no observation, proposal or hypothesis tuples;
- no selected identity or numeric oil Y;
- no positive no-interface evidence;
- no tracker action other than `NO_UPDATE`;
- no smoothing action other than `PRESERVE`.

A failed frame cannot reuse `UnavailableObservation` or `EvidenceUnavailableDecision`. Execution failure never enters the successful temporal tracker and never increments no-interface, unavailable, beam, history, reacquisition or stability counters.

## Current-behavior compatibility decision

This architecture **supersedes** the current repeated-failure clear behavior.

Repeated pipeline execution failure must not mutate accepted Y, accepted velocity, beam/history, pending reacquisition, unavailable counters, tracker samples or smoothing history. It always projects `NO_UPDATE` plus `PRESERVE`.

The existing source test that expects repeated execution failure to reach stable unavailable clear is a replacement target during bounded source implementation. It must be replaced by two separate sequence families:

1. successful `EvidenceUnavailableDecision` frames prove pending preservation and bounded stable clear;
2. repeated `FailedPipelineFrame` frames prove persistent no-update/preserve behavior regardless of sequence length.

No implementation Worker decision remains open on this policy.

## Closed canonical production outcomes

The trust-boundary normalizer creates exactly one fresh concrete outcome:

- `AcceptedBoundaryOutcome`;
- `NoInterfaceOutcome`;
- `AmbiguousOutcome`;
- `EvidenceUnavailableOutcome`;
- `ReacquisitionPendingOutcome`;
- `PipelineFailureOutcome`.

Concrete outcome variant is the only classification discriminator.

### `EvidenceUnavailableOutcome`

Represents successful pipeline execution with insufficient/unavailable current evidence. It owns successful unavailable temporal semantics, including pending versus bounded stable transition. It owns no numeric oil, selected candidate, positive no-interface acceptance or pipeline failure reason.

### `PipelineFailureOutcome`

Represents pipeline execution or normalization failure. It requires a canonical bounded failure reason and may own bounded debug-safe failure diagnostics. It owns no evidence tuples, current observation, normal temporal decision, numeric oil, selected candidate or positive no-interface evidence. Its actions are fixed to `NO_UPDATE` and `PRESERVE`.

A generic outcome with optional failure fields or an independent failure boolean is prohibited.

## Canonical normalizer mapping

The normalizer pattern-matches the outer frame first and creates distinct outcomes:

| Input | Canonical output |
|---|---|
| successful + boundary accepted | `AcceptedBoundaryOutcome` |
| successful + no-interface accepted | `NoInterfaceOutcome` |
| successful + ambiguous | `AmbiguousOutcome` |
| successful + evidence unavailable | `EvidenceUnavailableOutcome` |
| successful + reacquisition pending | `ReacquisitionPendingOutcome` |
| failed frame | `PipelineFailureOutcome` |

The failed-frame arm does not construct or evaluate a normal temporal decision. A malformed successful frame or normalization exception is discarded at the boundary and converted directly to a fresh `PipelineFailureOutcome`; raw malformed evidence cannot remain authoritative.

Normalization must:

1. reject unsupported frame/variant subclasses and duplicate discriminator attributes;
2. enforce the successful/failed legal-field matrices;
3. recompute actual tuple/resource counts and validate configured limits;
4. validate every retained scalar for finiteness, declared range and JSON safety;
5. reconstruct canonical hypothesis identity/content/provenance/Y;
6. validate current-observation evidence availability;
7. validate successful temporal variant and canonical membership;
8. derive status, tracker action and smoothing action from concrete variants/modes;
9. create fresh canonical values without reusing raw mutable selections.

## Sole downstream authority

After normalization, no production consumer may directly read the raw frame result, raw current observation or raw temporal decision.

| Downstream concern | Sole authoritative input |
|---|---|
| numeric raw oil and selected candidate | `AcceptedBoundaryOutcome` |
| confidence and decision margin | validated scalars owned by the canonical outcome |
| tracker update | canonical tracker action |
| smoothing mutation | canonical smoothing action |
| fill-state oil input | canonical outcome variant and canonical no-interface evidence |
| flags and failure projection | canonical outcome variant and required variant-owned reason |
| candidate/debug projection | validated canonical provenance and bounded JSON-safe diagnostics |

Fill-state classification consumes the canonical outcome, not raw temporal status. Flags derive from the variant; no optional failure boolean participates. Candidate/debug projection cannot reread a generic raw result or feed projected values back into selection.

External compatibility may continue to expose existing flags such as unavailable and pipeline-failure flags, but they are one-way projections from distinct internal variants.

## Fail-closed projection

Every malformed or unsupported oil result projects:

- `PipelineFailureOutcome` with required bounded reason;
- no raw or smoothed numeric oil output for the current frame;
- no selected oil candidate;
- no oil tracker update;
- smoothing history preserved;
- no legacy oil fallback;
- no mutation of input raster or retained frame-owned images;
- independently valid S5-A Foam processing preserved.

Failure may cause review/failure flags and `UNKNOWN_REVIEW` compatibility projection, but it cannot impersonate positive no-interface evidence or successful evidence-unavailable stability.

## Required validation matrix

### Construction and discrimination

- every legal current observation, successful temporal decision, pipeline frame and canonical outcome constructs;
- concrete class derives every discriminator and legal action;
- successful evidence unavailable and pipeline failure normalize to different concrete outcomes;
- `PipelineFailureOutcome` cannot receive evidence, current observation or normal temporal decision;
- failure cannot receive or forge stable-clear mode, tracker acceptance or any non-preserve smoothing action;
- only `AcceptedBoundaryOutcome` owns numeric oil and selected candidate.

### Sequence behavior

- accepted boundary initial/continuous preserves applicable history;
- reacquired boundary clears before accepting;
- no-interface pending preserves and bounded stable transition clears stale history;
- successful evidence-unavailable pending preserves and bounded stable transition clears stale history;
- ambiguous and reacquisition pending always preserve/no-update;
- repeated pipeline failure always preserves/no-update and never advances successful unavailable stability;
- successful unavailable stable-transition tests and failure-sequence tests are separate.

### Trust-boundary mutation

Table-driven or deterministic property-style tests must forge independently:

- outer success/failure variant and legal fields;
- current/temporal concrete variant;
- identity, content, provenance and Y;
- confidence, margin, likelihood, visibility and support finiteness/range;
- no-interface evidence availability and positive meaning;
- tuple counts, resource counts and configured limits;
- acceptance/stability modes and derived actions;
- candidate/debug JSON safety;
- unsupported subclasses, extra discriminator attributes and post-construction mutation.

Every malformed row asserts the full fail-closed projection, not only validator rejection.

### Downstream ownership

Tests must prove:

- flags derive from canonical variant without optional failure boolean;
- fill-state consumes only canonical outcome, never raw temporal status;
- tracker and smoothing consume only canonical actions;
- candidate/debug projection does not reread a raw generic result as authoritative;
- debug/external projections cannot feed selection back into the pipeline;
- S5-A Foam candidates, confidence, metrics and debug images remain unchanged by oil failure.

## Bounded migration sequence

After independent architecture `PASS`:

1. introduce closed observation and successful temporal-decision variants;
2. introduce successful/failed pipeline-frame variants;
3. introduce closed canonical outcomes and normalizer;
4. cut detector, fill-state, tracker/smoothing, flags and debug consumers atomically to canonical outcomes;
5. remove generic result fields, stored discriminators, generic clear boolean and manual cross-product validator;
6. replace the failure-clear test and add the complete validation matrix;
7. run compatibility regression;
8. obtain an independent exact-head source audit;
9. perform controlled base/feature comparison only after that audit passes.

Old and new models must never simultaneously influence candidate selection, numeric oil, tracker/smoothing action or fill-state input. Legacy candidate generation, consensus, scoring, no-interface evaluation and `OilTemporalPath` remain prohibited as production fallback.

## External compatibility and non-goals

This clarification does not change:

- observation extraction, proposal or semantic-hypothesis algorithms;
- likelihood formulas, thresholds or successful-frame temporal transitions;
- bounded Glass-local state limits;
- external `PhaseDetection` and application-port shape;
- Recipe/settings persistence;
- benchmark, truth, fixture, result, CSV or debug schema versions;
- detector version or dependency set;
- S5-A Foam algorithm, temporal ownership or output semantics;
- controlled accuracy expectations.

Source implementation, tests, controlled comparison, canonical validation, Windows/manual validation, packaging, merge and cleanup are outside this documentation task.

## Remaining risks

Broad and narrow likelihoods may remain correlated under blur, fog and refractive motion; full/empty classification remains exposure-dependent; calibration may vary by Glass geometry; production instrumentation may affect CPU; and debug consumers may contain assumptions about old mutable results. Those implementation and detector-evidence risks must be exposed by later source audit and controlled comparison, not solved by weakening this boundary.

The two deferred controlled accuracy findings remain tracked in the [current work plan](../00-project/work-plan.md). The next gate is the independent trust-boundary redesign architecture re-audit.
