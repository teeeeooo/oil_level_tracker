# S5-B Oil-Boundary Hypothesis Architecture

**Status:** `ACTIVE` trust-boundary redesign contract; source implementation is blocked pending independent architecture audit
**Milestone:** [S5-B](../00-project/work-plan.md)
**Redesign input head:** `b12cd4d51d9b6ffef7abea390ac669560f89b116`
**Redesign input parent:** `e937a4b77319377598c6927a9967559bf249e631`

This document governs the S5-B internal observation, proposal, semantic-hypothesis, temporal-decision and production-result boundaries. The independently accepted S5-B1 typed hypothesis architecture remains authoritative. The S5-B2 production cutover exposed a separate cross-field coherence defect in the generic result records; this redesign replaces that result boundary without changing the accepted algorithms.

`ACTIVE` identifies the governing architecture. It does not authorize source implementation, controlled comparison, canonical validation, merge, cleanup or accuracy acceptance. The next gate is an independent exact-head architecture audit of this redesign.

## Purpose

Preserve the accepted extraction and reasoning pipeline while making illegal production-result states difficult to construct and impossible for normal downstream consumers to observe. A closed discriminated internal model must carry only state-legal fields, and one fail-closed trust-boundary normalizer must reconstruct the canonical values used by production.

The redesign is structural rather than another field-level validator patch. Constructor validation remains useful, but production integrity must not depend on every caller remembering an expanding cross-product of optional-field invariants.

## Failure analysis: generic production-result model

The current `OilShadowFrameResult` and `ShadowTemporalDecision` duplicate the same semantics across independent fields:

- result availability and failure reason;
- temporal status and temporal observation kind;
- current-observation class and stored internal kind;
- selected hypothesis identity and projected source Y;
- smoothing-clear boolean and transition meaning;
- no-interface evidence availability and positive acceptance;
- resource summary counts and actual evidence tuples.

Three independent S5-B2 audits successively showed that the narrow validator still admitted malformed combinations. Confirmed blockers and probes include:

- current class, temporal status, selected identity and projected Y disagreeing;
- a forged current internal `kind` disagreeing with its concrete class;
- `available=False` combined with `BOUNDARY_ACCEPTED`;
- `available=True` combined with `UNAVAILABLE` without coherent failure semantics;
- failure frames producing numeric oil or a selected candidate;
- ambiguous or reacquisition-pending decisions forged to clear smoothing;
- unavailable no-interface evidence accepted as positive evidence;
- resource summaries disagreeing with actual hypothesis tuple lengths;
- post-construction non-finite confidence, margin or likelihood values;
- selected identity/content/Y not resolving to the canonical hypothesis tuple.

The root cause is not insufficient conditional coverage. It is a generic record whose stored discriminators, booleans and status-dependent optional fields make contradictory states representable. Adding another `if` branch leaves the same failure mode in place.

## Retained algorithmic reasoning flow

```text
masked frame evidence
→ immutable raw edge observations
→ bounded-diameter deterministic Y proposals
→ broad region-step + narrow line/pulse evidence
→ continuous boundary/artifact/ambiguity likelihoods
→ soft static prior
→ deterministic semantic deduplication
→ discriminated current observation
→ discriminated temporal decision
→ successful/failed pipeline frame
→ trust-boundary normalizer
→ canonical production outcome
→ existing PhaseDetection compatibility projection
```

The redesign begins after semantic evidence is produced. Observation extraction, proposal formation, hypothesis scoring, likelihood thresholds and temporal transition behavior remain unchanged.

## Immutable raw observations and bounded proposals

A raw edge observation remains a frozen scalar record derived from one bounded measurement operation. It contains source family and scale, local and canonical source Y, signed polarity when available, response strength, horizontal support, visibility support, measurement metadata and a deterministic source-local identity.

Raw observations never carry selected/rejected state and are never mutated with downstream scores. Selection, rejection and compatibility projection belong to later immutable values. The same ordered observations must produce byte-equivalent proposal content.

Proposal construction remains deterministic and bounded:

1. sort by canonical scalar keys independent of input order;
2. enforce an explicit maximum Y diameter with no single-link bridge chaining;
3. cap proposals, members and retained observation identities;
4. choose representative Y by a fixed semantic rule rather than mutable score order;
5. retain member observations and proposal span;
6. emit separate proposals when two edge groups cannot fit one bounded transition.

The pre-evidence seed remains a deterministic center or median used only to locate broad and narrow measurements. After evidence evaluation, representative Y continues to prefer internally consistent broad region-transition evidence and otherwise retains the bounded seed projection. Integer/source-coordinate projection occurs only at the compatibility boundary; internal likelihood calculations may retain finite sub-pixel scalars.

## Broad, narrow and static evidence

Broad evidence continues to measure multi-scale signed above/below contrast, visible support, scale and polarity consistency, transition localization, glare/exclusion conflict and broad-step strength independent of narrow peak height. Missing support is unavailable evidence, not zero-strength negative evidence.

Narrow evidence continues to measure local peak support, signed lobe order, paired-edge separation, line/pulse symmetry, center offset, narrow-scale persistence and structural/glare/static overlap. A narrow pulse raises an artifact explanation likelihood but does not automatically reject a nearby real boundary.

Static maps remain a bounded candidate-local soft prior. They do not mask pixels, delete observations or directly select/reject proposals. The prior remains neutral when unavailable, is capped, preserves contradictory current evidence and can be overcome by sufficiently strong current broad-step evidence.

## Continuous semantic hypotheses and deduplication

Each semantic hypothesis continues to expose finite normalized boundary, artifact and ambiguity likelihoods; evidence availability and visibility; polarity confidence; broad/narrow component scores; bounded static-prior contribution; deterministic identity/content/provenance; and a bounded representative Y.

Ambiguous evidence remains first-class. Close competing likelihoods, conflicting polarity or insufficient visible support must survive into temporal comparison and cannot be coerced into acceptance or candidate absence.

Semantic deduplication still occurs only after evidence is available. Hypotheses may combine only when they describe the same bounded Y transition and carry compatible semantic evidence. Fixed scalar keys provide deterministic tie-breaking; input ordering, dictionary ordering and mutable selected/rejected state cannot affect the result.

No-interface remains positive typed evidence rather than the absence of a surviving boundary candidate. Full/empty projection remains compatible fill-state reasoning based on image evidence and prior Glass-local state.

## Retained temporal behavior and bounds

Temporal reasoning remains Glass-local and consumes only immutable bounded scalar observations. It retains no frame, crop, mask, raster profile or unbounded candidate history.

The redesign preserves:

- separate boundary, no-interface, ambiguous and unavailable transitions;
- bounded reacquisition after genuine rapid movement;
- stable stale-smoothing removal after accepted no-interface/unavailable evidence;
- no clear authority during ambiguity or reacquisition pending;
- bounded beam width, history window, candidate count and per-Glass state;
- current evidence authority over a soft prior when sufficiently strong.

## Accepted foundation and production ownership

S5-B1 remains the independently accepted foundation for immutable observations, bounded proposals, continuous semantic evidence, deterministic identities, ambiguity preservation, raster ownership isolation and finite scalar debug output. Its prior `AUDIT: PASS` authorized production cutover, not accuracy acceptance or merge readiness.

S5-B2 retains the typed pipeline as the single production oil-boundary/no-interface/temporal owner. Official candidate/debug projection remains deterministic and one-way, and legacy generation, consensus, scoring, no-interface evaluation and `OilTemporalPath` remain outside production authority. The trust-boundary redesign corrects representation and consumption coherence without restoring a second decision engine.

## Accepted discriminated internal model

The implementation may choose exact Python names, modules and helper placement, but the closed variants and ownership below are mandatory. Concrete variant class determines the discriminator. A stored constructor field must not duplicate a discriminator already implied by the variant.

### Current observation variants

| Variant | Legal owned fields | Derived read-only property | Structurally absent fields |
|---|---|---|---|
| `BoundaryObservation` | canonical hypothesis reference/value, bounded alternatives, visibility and current diagnostics | `kind = BOUNDARY` | no-interface acceptance, unavailable reason, temporal action |
| `NoInterfaceObservation` | available positive no-interface evidence, full/empty evidence inputs, visibility and diagnostics | `kind = NO_INTERFACE` | selected boundary identity/Y, failure reason, temporal action |
| `AmbiguousObservation` | bounded boundary options, optional available no-interface evidence, ambiguity reason and diagnostics | `kind = AMBIGUOUS` | accepted boundary Y, positive no-interface acceptance, clear authority |
| `UnavailableObservation` | unavailability reason, visibility and bounded diagnostics | `kind = UNAVAILABLE` | boundary selection/Y, positive no-interface evidence, clear authority |

`kind` is never accepted as a constructor argument and is not independently stored. Normal construction therefore cannot forge a class/kind mismatch. Runtime normalization still checks the concrete variant and reconstructs its canonical kind rather than trusting an object attribute.

### Temporal decision variants

A generic optional-field `ShadowTemporalDecision` is replaced by status-specific variants. Each variant contains only fields legal for that temporal state.

| Variant | Legal owned fields | Derived properties | Structurally absent fields |
|---|---|---|---|
| `BoundaryAcceptedDecision` | selected canonical hypothesis, accepted source Y, finite confidence/margin, transition diagnostics, `acceptance_mode` | `status = BOUNDARY_ACCEPTED`, `observation_kind = BOUNDARY`, smoothing action from mode | failure reason, no-interface acceptance |
| `ReacquisitionPendingDecision` | pending canonical identity/content, finite diagnostics and reason | `status = REACQUISITION_PENDING`, `observation_kind = BOUNDARY`, smoothing action = preserve | accepted numeric Y, selected production candidate, clear authority |
| `NoInterfaceAcceptedDecision` | available positive no-interface evidence, finite confidence/margin, fill-state evidence and `stable_clear_mode` | `status = NO_INTERFACE_ACCEPTED`, `observation_kind = NO_INTERFACE`, smoothing action from stable-clear mode | boundary identity/Y |
| `AmbiguousDecision` | bounded diagnostic options, optional diagnostic projected Y, finite confidence/margin and reason | `status = AMBIGUOUS`, `observation_kind = AMBIGUOUS`, smoothing action = preserve | selected production boundary, clear authority |
| `UnavailableDecision` | reason, visibility, finite confidence/diagnostics and `stable_clear_mode` | `status = UNAVAILABLE`, `observation_kind = UNAVAILABLE`, smoothing action from stable-clear mode | selected boundary identity/Y, positive no-interface acceptance |

`status` and `observation_kind` are derived from the concrete variant and are never stored constructor inputs. Diagnostic projected Y on an ambiguous decision is not accepted oil Y and cannot be exposed as raw oil output or candidate selection.

### Smoothing authority

A generic `clear_smoothing: bool` is not shared by all decisions.

- Boundary acceptance owns semantic `acceptance_mode`: `initial`, `continuous` or `reacquired`.
- Smoothing clear is derived only from `reacquired`; `initial` and `continuous` preserve the applicable tracker semantics.
- No-interface and unavailable variants may own their bounded stable-clear semantic mode because those states already have accepted stale-state clearing behavior.
- Ambiguous and reacquisition-pending variants have no clear field, mode or constructor path. Their smoothing action is structurally fixed to preserve.

The normalizer derives one canonical smoothing action from the decision variant. Downstream code cannot override it with a second boolean.

### Pipeline frame variants

The outer frame result removes the generic `available: bool` and `failure_reason` pair.

| Variant | Legal owned fields | Prohibited combinations |
|---|---|---|
| `SuccessfulPipelineFrame` | immutable observations/proposals/hypotheses, actual resource summary inputs, current observation and temporal decision | no pipeline failure reason; evidence-shortage `UnavailableDecision` remains legal |
| `FailedPipelineFrame` | explicit failure reason, bounded visibility/debug-safe diagnostics and unavailable production decision | no observations, proposals, hypotheses, selected identity, numeric oil Y, positive no-interface acceptance or tracker update |

A failed frame can normalize only to an unavailable/failure production outcome. A successful frame cannot acquire failure semantics merely because its temporal outcome is unavailable; evidence insufficiency and pipeline execution failure remain distinct states.

## Canonical production outcomes

`OpenCvPhaseDetector` and downstream owners must not assemble production truth by reading raw frame and temporal fields independently. The trust-boundary normalizer creates exactly one fresh canonical outcome:

- `AcceptedBoundaryOutcome`;
- `NoInterfaceOutcome`;
- `AmbiguousOutcome`;
- `UnavailableOutcome`;
- `ReacquisitionPendingOutcome`.

Only `AcceptedBoundaryOutcome` may own numeric accepted oil Y and a selected oil candidate. All other outcomes structurally omit those values. Pipeline failure is represented by an `UnavailableOutcome` carrying canonical failure semantics rather than by combining a boolean with another outcome.

### Downstream ownership

| Downstream concern | Sole authoritative input |
|---|---|
| raw oil Y and candidate selection | canonical accepted-boundary outcome |
| confidence and margin | validated canonical outcome scalars |
| smoothing/tracker action | canonical outcome action derived from variant semantics |
| fill-state input | canonical no-interface/boundary/unavailable semantics |
| flags and failure projection | canonical outcome classification and reason |
| candidate/debug metrics | validated canonical provenance and JSON-safe scalar projections |

Raw typed result objects are not reused directly for production selection. Compatibility adapters consume the canonical outcome one way; debug or external projections cannot feed a selection back into the typed pipeline.

## Trust-boundary normalization

The normalizer is the single production integrity boundary between raw typed pipeline output and all detector/fill-state/debug consumers. It pattern-matches the closed outer and inner variants, validates the complete reachable object graph and constructs fresh canonical values or validated immutable scalars. It does not trust that `__post_init__()` once ran, that a frozen object was never forged, or that summary fields agree with retained tuples.

Normalization proceeds in this order:

1. identify the concrete frame variant and reject unsupported subclasses or discriminator attributes;
2. validate success/failure coherence and the failure-frame empty-evidence contract;
3. recompute actual observation, proposal and hypothesis counts from immutable tuples;
4. validate counts against declared resource metrics and configured limits;
5. validate each retained scalar for finiteness, normalization/range and JSON safety;
6. reconstruct canonical hypothesis identities/content/Y from validated evidence;
7. validate current-observation variant and evidence availability;
8. validate temporal-decision variant and its canonical membership/provenance;
9. derive status, observation kind and smoothing action from concrete variants/modes;
10. construct a fresh canonical production outcome without reusing mutable raw selections.

### Minimum runtime integrity checks

- all normalized confidence, margin, likelihood, support and diagnostic scalars are finite and within their declared ranges;
- hypothesis identity, deterministic content, provenance and representative Y agree;
- accepted identity exists exactly in the validated canonical hypothesis tuple;
- accepted source Y equals the canonical selected hypothesis projection;
- positive no-interface acceptance owns available positive evidence;
- frame success/failure semantics agree with retained evidence and temporal outcome;
- actual tuple lengths agree with resource summary metrics;
- all observation/proposal/hypothesis/debug counts remain within configured bounds;
- failed frames retain no evidence tuples and cannot request tracker mutation;
- candidate and debug projections contain only schema-compatible JSON-safe values;
- non-accepted outcomes cannot produce numeric oil Y or a selected candidate;
- the canonical smoothing action is the only action visible downstream.

Unsupported, malformed, subclass-forged or post-construction-mutated input fails closed. The normalizer must not partially accept one field while discarding a contradictory field.

### Required malformed-result projection

Every normalization failure has one production projection:

- unavailable/pipeline-failure semantics;
- no raw or smoothed numeric oil output;
- no selected oil candidate;
- no oil tracker update;
- no unauthorized smoothing clear;
- no legacy oil fallback;
- no mutation of the input raster or retained frame-owned images;
- S5-A Foam processing, candidates, confidence and debug ownership preserved.

A malformed oil result must not prevent independently valid Foam processing. Existing detector exception isolation remains the compatibility mechanism, while the canonical unavailable outcome is the only oil result exposed downstream.

## Bounded migration sequence

Implementation must occur in this order after independent architecture `PASS`:

1. introduce internal current-observation variants and derived `kind` properties;
2. introduce temporal-decision variants and derived status/kind/action properties;
3. introduce successful/failed pipeline frame variants;
4. implement the canonical production normalizer and fresh value reconstruction;
5. cut detector, fill-state, smoothing/tracker, flags and debug consumers over to canonical outcomes;
6. remove old generic result fields, stored discriminators and manual cross-product validator;
7. replace narrow adversarial patches with systematic mutation/property tests;
8. run external-contract, Foam, resource and performance compatibility regression;
9. obtain an independent immutable exact-head source audit;
10. perform controlled base/feature comparison only after that audit passes.

Old and new models must never simultaneously influence production selection. Temporary compile-time adapters may support an atomic migration commit sequence, but only one path may own candidate selection, numeric oil, tracker action and fill-state input at every committed exact head. Legacy candidate/scorer/no-interface/temporal code must not return as production fallback.

## Systematic validation strategy

The test design must demonstrate closure of the model rather than accumulate one assertion per audit finding.

### Variant construction matrix

| Family | Required evidence |
|---|---|
| Current observations | every legal variant constructs; concrete class derives the correct kind; forbidden fields/constructor parameters do not exist |
| Temporal decisions | every legal status variant constructs; status, observation kind and smoothing action derive correctly |
| Pipeline frames | successful and failed variants construct only with their legal payloads; failure evidence is structurally empty |
| Canonical outcomes | only accepted boundary owns numeric Y/candidate; all other outcomes omit them |

### Trust-boundary mutation matrix

Table-driven tests independently forge or replace each axis:

- outer success/failure frame variant and failure reason;
- current-observation and temporal-decision concrete variant;
- hypothesis identity, content, provenance and Y;
- confidence, margin, likelihood, visibility and support finiteness/range;
- no-interface evidence availability and positive/negative meaning;
- resource tuple counts, summary counts and configured limits;
- selected candidate provenance and canonical membership;
- acceptance/stable-clear modes and derived smoothing action;
- candidate/debug scalar JSON safety;
- unsupported subclasses, extra discriminator attributes and post-construction mutation.

Each malformed row must assert the complete fail-closed projection, not only validator rejection: no numeric oil, no selected candidate, no tracker update, no unauthorized clear, no legacy fallback, unchanged input raster and preserved Foam processing.

### Deterministic property-style invariants

Use seeded deterministic generation or exhaustive bounded tables for legal variant combinations, scalar boundary values, tuple sizes and mutation positions. Required invariants include:

- concrete variant uniquely determines status/kind/action;
- every accepted identity resolves to exactly one canonical hypothesis;
- only accepted boundary can project numeric oil and selection;
- failed frame implies empty evidence and unavailable outcome;
- positive no-interface acceptance implies available positive evidence;
- actual tuple counts equal canonical resource metrics and remain within limits;
- input permutation does not change canonical proposal/hypothesis/outcome content;
- adding a new variant or field requires extending one closed matcher/table, not remembering unrelated validators.

The existing algorithm regression families remain required alongside the new integrity matrix:

| Area | Required evidence |
|---|---|
| Observation/proposal | immutability, input-order determinism, bounded diameter, no chaining bridge and finite values |
| Broad/narrow evidence | clear/weak region steps, structural lines, glare pulses, paired edges and adjacent real boundaries |
| Ambiguity/no-interface | conflicting evidence remains explicit; full/empty evidence competes without candidate-absence coercion |
| Temporal | dropout, rapid fill/drain, reacquisition, visible↔no-interface, stable clear and Glass isolation |
| Compatibility | existing `PhaseDetection`, recipe, truth, benchmark, fixture, result, CSV and debug contracts |
| Foam non-regression | S5-A Foam and shimmer behavior remains independently owned and preserved |
| Performance/resources | CPU median, retained scalar counts, long-duration memory and packaging obligations |
| Real evidence | controlled external fixture comparison and later S6 real-video/Windows validation |

The repository sample video remains an architecture evidence probe only. It can expose deterministic or structural conflicts but is not annotated canonical truth and cannot establish detector accuracy.

## External compatibility and ownership

The redesign must not change:

- observation extraction, proposal or semantic-hypothesis algorithms;
- likelihood formulas, thresholds or temporal transition behavior;
- bounded Glass-local temporal state;
- external `PhaseDetection` and application-port shape;
- persisted Recipe/settings schemas;
- benchmark, truth, fixture, result, CSV or debug schema versions;
- detector version or dependency set;
- S5-A Foam algorithm, temporal ownership or output semantics.

`OpenCvPhaseDetector.detect` continues to return the existing `PhaseDetection` shape. A one-way compatibility adapter maps only canonical production outcomes into existing oil-level, confidence, fill-state, flag, candidate and debug fields. External or debug representations never feed selection back into the internal model.

S5-A Foam remains independently processed and owned. Oil normalization failure cannot rewrite Foam candidates, confidence, metrics, debug images or temporal state. The input frame, masks and debug rasters retain their existing ownership and mutation contracts.

## Legacy ownership status

The following historical owners remain outside production authority:

- source-count `oil_candidate_consensus`;
- monolithic `candidate_scorer` boundary/static pair suppression;
- raw oil candidate generators;
- scored-candidate no-interface evaluation;
- mutable-candidate `OilTemporalPath` state.

Historical module deletion is not required by this redesign, but no legacy owner may be imported, constructed, called or used as fallback by production detection. Broad cleanup is a later separately authorized scope.

## CPU, memory and resource bounds

The implementation retains finite bounds for raw observations per source/scale, broad/narrow scales, proposal diameter/members, proposals/hypotheses, temporal beam/history, static-prior state and debug rows. The normalizer additionally verifies actual retained tuple counts against canonical resource metrics and configured limits.

Frame-sized preprocess maps may exist only for the current call and existing bounded static map. No frame, crop, mask, raster profile or unbounded proposal history accumulates across frames. Complexity remains linear in current-frame pixel count plus bounded proposal, temporal and normalization work; it must not grow quadratically with video duration.

## Explicit non-goals

- Changing detector accuracy, thresholds, likelihood calibration or temporal transition policy.
- Adding another field-level validator as the accepted structural solution.
- Changing persisted or external schemas, detector version or dependency set.
- Reintroducing the legacy oil pipeline as fallback or comparison truth.
- Redesigning S5-A Foam, fill-state product semantics or Result Review.
- Adding learned models, checkpoints, CUDA or dedicated-GPU compute.
- Scene-, filename- or fixture-specific exceptions or automatic tuning from one video.
- Performing source implementation, controlled comparison, canonical validation, merge or cleanup in this documentation task.

## Unresolved risks

Broad and narrow likelihoods may remain correlated under blur, fog and refractive motion; short static samples may conflict with moving reflections or a stationary real boundary; full/empty classification remains exposure-dependent; and likelihood calibration may vary by Glass geometry. These are detector-evidence risks, not reasons to weaken the trust boundary.

Production instrumentation may affect CPU measurements, and existing debug consumers may contain assumptions about mutable legacy candidates. The implementation migration and compatibility regression must expose those risks before independent source audit and controlled comparison.

These risks and the two known controlled accuracy failures remain tracked in the [work plan](../00-project/work-plan.md). They do not authorize source work before the independent architecture audit passes.
