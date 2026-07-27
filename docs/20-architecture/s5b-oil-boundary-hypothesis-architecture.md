# S5-B Oil-Boundary Hypothesis Architecture

**Status:** `ACTIVE` transactional trust-boundary contract; source implementation is blocked pending independent architecture re-audit  
**Milestone:** [S5-B](../00-project/work-plan.md)

This document governs the S5-B internal observation, proposal, semantic-hypothesis, temporal-state, temporal-decision, pipeline-frame and canonical production-result boundaries. The independently accepted S5-B1 typed hypothesis architecture and the S5-B2 typed production cutover remain the foundation. This repair closes the remaining temporal mutation-before-normalization ambiguity without changing detector algorithms, accepted successful temporal transition mathematics or external contracts.

`ACTIVE` identifies the governing architecture. It does not authorize source implementation, controlled comparison, canonical validation, Windows/manual validation, packaging, merge, cleanup or accuracy acceptance. The current gate is an independent architecture re-audit of this exact documentation head.

## Purpose

Preserve the accepted extraction and reasoning pipeline while making contradictory production states structurally unrepresentable and preventing rejected provisional work from changing live Glass-local temporal state. One transactional trust-boundary owner must validate canonical evidence, evaluate temporal behavior provisionally, validate the proposed transition and publishable outcome, then commit the proposed next state exactly once.

The repair is structural rather than another field-validator patch. Concrete variants determine meaning; independent optional fields or booleans must not recreate a second discriminator. Frozen dataclasses and constructor checks remain useful local guards, but they are not a substitute for canonical trust-boundary validation or transactional state ownership.

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
→ Phase A canonical evidence validation
→ immutable prior Glass-local temporal-state snapshot
→ provisional temporal decision + proposed next state + proposed resources
→ Phase B temporal proposal/final outcome validation
→ prepared publishable canonical outcome + validated commit payload
→ exactly-once atomic Glass-local temporal-state commit
→ canonical outcome publication
→ existing PhaseDetection compatibility projection
```

Observation extraction, proposal formation, hypothesis scoring, likelihood formulas and thresholds, accepted successful-frame temporal transition policy and Glass-local bounds remain unchanged. The mandatory change is mutation timing and authority: temporal evaluation is provisional until the single trust-boundary owner validates and commits it.

## Retained evidence contracts

Raw observations remain immutable bounded scalar records with deterministic identities and provenance. Proposal construction remains input-order independent, bounded by maximum Y diameter, member count and proposal count, and cannot form a single-link chaining bridge.

Broad evidence continues to measure signed region transitions, visible support, scale/polarity consistency and glare/exclusion conflicts. Narrow evidence continues to measure peak support, paired-edge structure, pulse symmetry, center offset, scale persistence and structural/static overlap. Missing support is unavailable evidence, not scored negative evidence.

Semantic hypotheses continue to expose finite normalized boundary, artifact and ambiguity likelihoods, evidence availability, visibility, polarity, bounded representative Y and deterministic identity/content/provenance. Ambiguity remains first-class. No-interface remains positive typed evidence rather than candidate absence. Static evidence remains a bounded soft prior and never deletes current observations.

## Why the generic result and direct-mutation model are rejected

The current generic records duplicate meaning across independent fields:

- frame availability and optional failure reason;
- temporal status and observation kind;
- current-observation class and stored kind;
- selected identity and projected Y;
- generic smoothing-clear boolean and transition meaning;
- no-interface availability and positive acceptance;
- declared resource counts and retained tuples.

That shape permits class/status/identity/Y disagreement, failure frames with successful temporal authority, forged smoothing clear, positive no-interface acceptance without evidence and other cross-field contradictions. Adding another conditional validator does not close the state space.

A second defect exists when temporal evaluation changes live state before the trust boundary has validated the complete result. A malformed successful frame, mutated provisional decision, resource mismatch or normalization exception can then become `PipelineFailureOutcome` while beam/history/counters or accepted/pending state have already changed.

The accepted target architecture therefore rejects both defects:

- a generic unavailable result with optional `failure_reason`, an `is_failure` boolean or an equivalent independent discriminator is prohibited;
- a temporal `evaluate()` operation that changes live `_GlassState` while constructing a decision is not an accepted production architecture;
- a raw or provisional object that the trust-boundary owner may reject cannot authorize earlier live-state mutation;
- constructor validation or frozen dataclasses alone cannot establish temporal transaction integrity;
- snapshot rollback, rollback-only handling or best-effort restore is not the default architecture and cannot be selected independently by an implementation Worker;
- pure/provisional evaluation followed by explicit validated commit is mandatory.

Exact Python class, module and helper names remain an implementation choice. The ordering and ownership contract does not.

## Closed current-observation model

Concrete current-observation class derives `kind`; `kind` is not a constructor argument or independently stored field.

| Variant | Legal owned fields | Structurally absent fields |
|---|---|---|
| `BoundaryObservation` | canonical hypothesis, bounded alternatives, visibility and diagnostics | failure reason, no-interface acceptance, temporal action |
| `NoInterfaceObservation` | available positive no-interface evidence, full/empty evidence inputs, visibility and diagnostics | selected boundary identity/Y, failure reason, temporal action |
| `AmbiguousObservation` | bounded competing options, optional available diagnostic no-interface evidence, reason and diagnostics | accepted boundary Y, positive no-interface acceptance, clear authority |
| `UnavailableObservation` | successful-execution evidence-unavailability reason, visibility and bounded diagnostics | boundary selection/Y, positive no-interface acceptance, failure reason, clear authority |

`UnavailableObservation` means the evidence pipeline executed successfully but current evidence is insufficient or unavailable. It never represents execution or normalization failure.

## Transactional temporal-state ownership

### Hypothesis temporal state

The Glass-local hypothesis temporal state includes, at minimum:

- bounded beam and beam history;
- accepted Y and accepted velocity;
- pending reacquisition Y, velocity and count;
- no-interface and successful-unavailable stability counters;
- static temporal diagnostics retained across frames;
- any other bounded scalar needed by the accepted successful temporal transition policy.

This state is owned transactionally by the trust-boundary owner. The stateful temporal component may calculate with an immutable snapshot, but it cannot commit or expose live mutation authority.

### Compatibility smoothing and fill-state tracker

The downstream compatibility tracker is a separate state owner. It may contain:

- the smoothed oil sample deque;
- the last smoothed accepted oil value;
- external fill-state stabilization and pending state;
- existing Foam-owned compatibility state, which remains independently governed by S5-A.

This tracker consumes only canonical outcome actions after successful canonical publication. It never consumes raw observations, raw temporal status, a provisional decision or a proposed next hypothesis state.

`NO_UPDATE` and `PRESERVE` have explicit two-owner meaning on failure:

- the hypothesis temporal-state owner commits no proposed state and leaves beam/history/counters/accepted/pending/static state unchanged;
- the compatibility tracker receives no oil update, performs no oil clear and preserves smoothing/fill-state oil history.

The term “tracker” must not be used ambiguously to merge these owners. Documentation, source and tests must identify whether they refer to hypothesis temporal state or the compatibility smoothing/fill-state tracker.

## Provisional temporal evaluation contract

Temporal evaluation receives:

- one fresh canonical evidence view produced by Phase A;
- one immutable Glass-local prior-state snapshot;
- the unchanged accepted bounds and successful transition policy.

It returns provisional immutable values only:

- a proposed temporal decision;
- a proposed next Glass-local hypothesis temporal state;
- proposed resource metrics derived from that proposed state;
- bounded diagnostics required for final validation.

Provisional evaluation must not:

- create or mutate the live state entry for a new Glass;
- replace or mutate the existing live state entry;
- increment counters in live state;
- append to live beam/history;
- alter accepted or pending values;
- clear live state;
- update the compatibility smoothing/fill-state tracker;
- publish a production outcome.

An exception during provisional evaluation discards all provisional values and leaves both state owners unchanged.

## Closed successful-frame temporal decisions

Normal temporal decisions exist only inside a successful provisional frame. Concrete decision class derives status, observation kind, tracker action and smoothing action.

| Variant | Legal owned fields | Derived authority |
|---|---|---|
| `BoundaryAcceptedDecision` | selected canonical hypothesis, accepted source Y, finite confidence/margin, diagnostics and `acceptance_mode` | boundary acceptance action from `initial`, `continuous` or `reacquired` |
| `NoInterfaceAcceptedDecision` | available positive no-interface evidence, finite confidence/margin, fill-state evidence and bounded stability mode | no compatibility tracker update; smoothing action from pending/stable mode |
| `AmbiguousDecision` | bounded diagnostic options, optional diagnostic projected Y, finite confidence/margin and reason | preserve/no update only |
| `EvidenceUnavailableDecision` | successful-execution unavailability reason, visibility, finite confidence/diagnostics and bounded stability mode | no compatibility tracker update; smoothing action from pending/stable mode |
| `ReacquisitionPendingDecision` | pending canonical identity/content, finite diagnostics and reason | preserve/no update only; no accepted numeric Y |

Status and observation kind are never independent constructor inputs. Diagnostic projected Y is not accepted oil Y and cannot become raw oil output or candidate selection.

A successful `EvidenceUnavailableDecision` may advance the successful-unavailable stability counter only through a validated proposed next state and the single commit boundary. A pipeline failure cannot enter this decision family or advance that counter.

## Closed tracker and smoothing actions

The implementation may choose exact enum names, but the legal action set and mapping are mandatory.

### Compatibility tracker action set

- `ACCEPT_BOUNDARY`: append/accept the canonical boundary value in the compatibility smoothing tracker.
- `NO_UPDATE`: do not mutate compatibility oil tracker state.

### Compatibility smoothing action set

- `PRESERVE`: retain applicable oil smoothing history.
- `CLEAR_BEFORE_ACCEPT`: clear stale history before accepting a reacquired boundary.
- `CLEAR_STALE_AFTER_STABLE_ABSENCE`: clear stale oil history after a bounded successful absence transition.

No generic `clear_smoothing: bool` is accepted at the production boundary.

| Canonical situation | Compatibility tracker action | Smoothing action |
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
| pipeline execution, validation, normalization, outcome-construction or commit failure | `NO_UPDATE` | `PRESERVE` |

The successful evidence-unavailable stable clear is explicitly retained as accepted temporal behavior. Pipeline failure is not an evidence-unavailable sample and cannot advance that transition.

## Closed pipeline-frame model

The outer frame removes the generic `available`/optional-failure pair.

### `SuccessfulPipelineFrame`

Before Phase A canonicalization, a successful raw frame may carry only the raw inputs needed to reconstruct:

- immutable observations, proposals and hypotheses;
- recomputable resource inputs;
- one legal current observation;
- bounded JSON-safe diagnostics.

A raw successful frame does not own committed temporal state. Its provisional decision, proposed next state and proposed resources are produced only after Phase A creates a fresh canonical evidence view.

### `FailedPipelineFrame`

Owns only:

- required canonical failure reason;
- bounded failure stage/category;
- bounded visibility and debug-safe diagnostics needed for compatibility projection.

It structurally has:

- no current observation;
- no normal temporal decision;
- no proposed next hypothesis state;
- no observation, proposal or hypothesis tuples;
- no selected identity or numeric oil Y;
- no positive no-interface evidence;
- no compatibility tracker action other than `NO_UPDATE`;
- no smoothing action other than `PRESERVE`.

A failed frame cannot reuse `UnavailableObservation` or `EvidenceUnavailableDecision`. Execution failure never enters successful temporal evaluation and never increments no-interface, successful-unavailable, beam, history, reacquisition or stability counters.

## One transactional trust-boundary owner

The trust-boundary owner is the sole production truth and temporal commit authority. It performs two integrity phases inside one operation; the phases do not create separate production authorities.

### Phase A — Canonical evidence validation

Phase A occurs before temporal evaluation. It validates the raw successful evidence payload and reconstructs a fresh canonical evidence view.

It must validate:

- outer successful evidence payload shape and supported concrete variants;
- observation, proposal and hypothesis immutable tuples;
- deterministic identity, content, provenance and Y coherence;
- finiteness, declared range and JSON safety of retained scalars and diagnostics;
- positive no-interface evidence availability and legal meaning;
- actual tuple/resource counts against configured limits;
- legal current-observation concrete variant and canonical membership;
- absence of duplicate discriminator attributes or unsupported subclasses.

If Phase A fails, temporal evaluation is not called. The owner returns a fresh `PipelineFailureOutcome` and commits no hypothesis temporal state.

### Phase B — Temporal proposal and final outcome validation

After Phase A, the owner obtains the immutable prior-state snapshot and requests provisional evaluation. Phase B then validates:

- proposed temporal decision concrete variant;
- selected canonical membership and complete canonical content;
- selected/source Y agreement;
- acceptance mode or successful-absence stability mode;
- compatibility tracker and smoothing actions derived from the concrete decision/mode;
- proposed beam/history/counter bounds and Glass-local identity;
- proposed resource summary recomputed from the proposed next state;
- action/outcome compatibility;
- bounded JSON-safe diagnostics and projection inputs;
- the complete prepared canonical outcome;
- the complete immutable commit payload.

The owner must reconstruct fresh canonical decision/outcome values rather than reusing mutable raw selections.

### Prepare, commit and publish ordering

The mandatory order is:

1. produce raw observations, proposals, hypotheses and current observation;
2. complete Phase A and create a fresh canonical evidence view;
3. read the current immutable Glass-local temporal-state snapshot;
4. calculate provisional decision, proposed next state and proposed resources without live mutation;
5. complete Phase B validation;
6. construct and validate the complete publishable canonical outcome and immutable commit payload;
7. commit the proposed next state exactly once with an all-or-nothing replacement operation;
8. publish/return the already prepared canonical outcome from the same boundary.

No observable production state may exist between a successful commit and canonical outcome publication. Canonical outcome construction is not permitted after state commit. The commit implementation must be all-or-nothing; a partial field-by-field live-state mutation followed by rollback is prohibited.

A commit failure retains the prior immutable state and returns `PipelineFailureOutcome`. The implementation must use a commit primitive whose failure cannot leave a partially applied state. Best-effort restoration is insufficient.

Old direct-mutation temporal APIs and the new transactional path cannot both modify production state. During migration, only one path may have production commit authority at any exact head.

## Closed canonical production outcomes

The trust-boundary owner prepares exactly one fresh concrete outcome:

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

Represents pipeline execution, canonical evidence validation, provisional temporal evaluation, temporal proposal validation, proposed state/resource validation, canonical outcome construction or temporal commit failure. It requires a canonical bounded failure reason and may own bounded debug-safe failure diagnostics. It owns no evidence tuples, current observation, normal temporal decision, proposed next state, numeric oil, selected candidate or positive no-interface evidence. Its actions are fixed to `NO_UPDATE` and `PRESERVE`.

A generic outcome with optional failure fields or an independent failure boolean is prohibited.

## Failure timing semantics

Every failure point below has the same oil-state result.

| Failure point | Required handling before return |
|---|---|
| observation/proposal/hypothesis/current-evidence construction failure | discard partial evidence; do not call or commit temporal evaluation |
| Phase A canonical evidence validation failure | discard raw frame; do not call temporal evaluation |
| provisional temporal evaluation exception | discard provisional values; retain prior state |
| provisional temporal decision validation failure | discard decision and proposed state; retain prior state |
| proposed next-state or resource validation failure | discard decision and proposed state; retain prior state |
| canonical outcome construction or prepared-outcome validation failure | discard prepared values before commit; retain prior state |
| temporal state commit failure | all-or-nothing commit leaves prior state intact; discard prepared success outcome |

The common result is:

- fresh `PipelineFailureOutcome`;
- no numeric oil;
- no selected candidate;
- no positive no-interface projection;
- no hypothesis temporal-state change, including beam/history/counters/accepted/pending/static diagnostics;
- compatibility tracker `NO_UPDATE`;
- smoothing `PRESERVE`;
- no legacy fallback;
- independently valid S5-A Foam processing preserved;
- input raster and retained frame-owned images unchanged.

A malformed successful frame cannot change state and then be reclassified as failure. A failure cannot impersonate positive no-interface evidence or successful evidence-unavailable stability.

## Sole downstream authority

After successful transactional normalization and commit, no production consumer may directly read a raw frame result, raw current observation, provisional temporal decision, proposed next state or raw resource summary.

| Downstream concern | Sole authoritative input |
|---|---|
| numeric raw oil and selected candidate | `AcceptedBoundaryOutcome` |
| confidence and decision margin | validated scalars owned by the canonical outcome |
| compatibility tracker update | canonical tracker action |
| smoothing mutation | canonical smoothing action |
| fill-state oil input | canonical outcome variant and canonical no-interface evidence |
| flags and failure projection | canonical outcome variant and required variant-owned reason |
| candidate/debug projection | validated canonical provenance and bounded JSON-safe diagnostics |

Fill-state classification consumes the canonical outcome, not raw temporal status. Flags derive from the variant; no optional failure boolean participates. Candidate/debug projection cannot reread a generic raw result or feed projected values back into selection.

External compatibility may continue to expose existing flags such as unavailable and pipeline-failure flags, but they are one-way projections from distinct internal variants.

## Current-behavior compatibility decision

This architecture supersedes the current repeated-failure clear behavior.

Repeated pipeline execution or normalization failure must not mutate accepted Y, accepted velocity, beam/history, pending reacquisition, unavailable counters, static diagnostics, compatibility tracker samples or smoothing history. It always projects `NO_UPDATE` plus `PRESERVE`, regardless of sequence length.

The existing source test that expects repeated execution failure to reach stable unavailable clear is a replacement target during bounded source implementation. It must be replaced by separate sequence families:

1. successful `EvidenceUnavailableDecision` frames prove pending preservation and bounded stable clear through validated commits;
2. repeated `FailedPipelineFrame`/`PipelineFailureOutcome` frames prove persistent no-update/preserve behavior and invariant hypothesis temporal state;
3. successful unavailable stable clear followed or preceded by pipeline failure proves the two sequences do not share counters or authority.

No implementation Worker decision remains open on this policy.

## Required validation matrix

### Construction and discrimination

- every legal current observation, provisional temporal decision, pipeline frame and canonical outcome constructs;
- concrete class derives every discriminator and legal action;
- successful evidence unavailable and pipeline failure normalize to different concrete outcomes;
- `PipelineFailureOutcome` cannot receive evidence, current observation, normal temporal decision or proposed next state;
- failure cannot receive or forge stable-clear mode, tracker acceptance or any non-preserve smoothing action;
- only `AcceptedBoundaryOutcome` owns numeric oil and selected candidate.

### Transaction and mutation timing

Tests must prove:

- provisional temporal evaluation does not create or mutate live prior state;
- a legal successful outcome commits the proposed next state exactly once;
- Phase A evidence normalization failure prevents temporal evaluation from running;
- a provisional decision mutation rejected by Phase B leaves live hypothesis temporal state unchanged;
- post-construction non-finite decision or resource mutation leaves live state unchanged;
- canonical identity/content/provenance/Y mismatch leaves live state unchanged;
- proposed beam, history or counter limit excess leaves live state unchanged;
- canonical outcome construction or prepared-outcome validation failure leaves live state unchanged;
- commit is exactly once with no replay or duplicate commit after return/retry handling;
- a failed commit leaves the complete prior state unchanged;
- old direct-mutation and new transactional APIs cannot both own production commit authority;
- a failure in one Glass cannot change another Glass's temporal state.

### Sequence behavior

- accepted boundary initial/continuous preserves applicable history;
- reacquired boundary clears before accepting;
- no-interface pending preserves and bounded stable transition clears stale history;
- successful evidence-unavailable pending preserves and bounded stable transition clears stale history only through valid commits;
- ambiguous and reacquisition pending always preserve/no-update;
- repeated `FailedPipelineFrame` sequences leave hypothesis temporal state and compatibility smoothing state unchanged regardless of length;
- successful unavailable stable-clear and pipeline-failure preserve are verified as separate sequence tests;
- interleaving failure with successful unavailable does not advance the successful-unavailable counter on failure frames.

### Trust-boundary adversarial inputs

Table-driven or deterministic property-style tests must forge independently:

- outer success/failure variant and legal fields;
- current/provisional temporal concrete variant;
- identity, content, provenance and Y;
- confidence, margin, likelihood, visibility and support finiteness/range;
- no-interface evidence availability and positive meaning;
- actual tuple counts, proposed resource counts and configured limits;
- acceptance/stability modes and derived actions;
- candidate/debug JSON safety;
- unsupported subclasses, extra discriminator attributes and post-construction mutation;
- outcome-construction and commit failure injection.

Every malformed row asserts the full fail-closed projection and both state-owner invariants, not only validator rejection.

### Downstream ownership

Tests must prove:

- flags derive from canonical variant without optional failure boolean;
- fill-state consumes only canonical outcome, never raw/provisional temporal status;
- compatibility tracker and smoothing consume only canonical actions;
- pipeline failure supplies no positive no-interface evidence;
- candidate/debug projection uses only canonical identity/content/provenance/Y;
- no raw/provisional result can regain production selection or state authority;
- S5-A Foam candidates, confidence, metrics and debug images remain unchanged by oil failure;
- input raster isolation is retained.

## Bounded migration sequence

After independent architecture `PASS`:

1. introduce/complete closed observations and Phase A canonical evidence validation;
2. introduce immutable temporal-state snapshot and provisional next-state types;
3. replace live direct mutation with pure/provisional temporal evaluation;
4. introduce final trust-boundary validation and the atomic temporal commit owner;
5. introduce closed pipeline frames and canonical outcomes;
6. cut detector, fill-state, compatibility smoothing, flags and debug consumers atomically to canonical outcomes;
7. remove generic result fields and the direct-mutation temporal API;
8. replace the failure-clear test and add the complete mutation/transaction validation matrix;
9. run compatibility regression;
10. obtain an independent exact-head source audit;
11. perform controlled base/feature comparison only after that audit passes.

Old direct-mutation and new transactional temporal paths must never simultaneously change production state. Legacy candidate generation, consensus, scoring, no-interface evaluation and `OilTemporalPath` remain prohibited as production fallback.

## External compatibility and non-goals

This repair does not change:

- observation extraction, proposal or semantic-hypothesis algorithms;
- likelihood formulas, thresholds or accepted successful temporal transitions;
- bounded Glass-local state limits;
- external `PhaseDetection` and application-port shape;
- Recipe/settings persistence;
- benchmark, truth, fixture, result, CSV or debug schema versions;
- detector version or dependency set;
- S5-A Foam algorithm, temporal ownership or output semantics;
- controlled accuracy expectations.

Source implementation, tests, controlled comparison, canonical validation, Windows/manual validation, packaging, merge and cleanup are outside this documentation task.

## Remaining risks

Broad and narrow likelihoods may remain correlated under blur, fog and refractive motion; full/empty classification remains exposure-dependent; calibration may vary by Glass geometry; production instrumentation may affect CPU; and debug consumers may contain assumptions about old mutable results. The source migration must also prove that its all-or-nothing commit primitive cannot partially mutate a Glass state under injected failure. Those implementation and detector-evidence risks must be exposed by later source audit and controlled comparison, not solved by weakening this boundary.

The two deferred controlled accuracy findings remain tracked in the [current work plan](../00-project/work-plan.md). The current gate is the independent trust-boundary redesign architecture re-audit.
