# S5-B Oil-Boundary Hypothesis Architecture

**Status:** `VALIDATING` design contract
**Milestone:** [S5-B](../00-project/work-plan.md)

The contract is awaiting independent documentation and planning audit. After audit `PASS`, the next authorized mutation-capable owner changes the document status to `ACTIVE`; the read-only Auditor does not mutate the audited head.

## Purpose

Define the replacement architecture for oil-boundary and no-interface reasoning before S5-B1 implementation. This document owns the internal evidence, proposal, likelihood and temporal boundaries. The external `PhaseDetection` contract, persisted recipe/truth/result schemas and S5-A Foam behavior remain compatible.

## Root cause of repeated failure

The current path generates scalar peaks, clusters them as consensus candidates, scores those clusters and then applies pair/static suppression before temporal selection. That sequence assigns boundary semantics too early:

- a broad oil region transition and a narrow structural line can both appear as nearby edge peaks;
- source-count consensus measures generator agreement, not semantic truth;
- single-link/local grouping can merge distinct edges or preserve only part of a static structure;
- hard suppression destroys evidence before competing explanations are compared;
- repair exceptions become dependent on intermediate candidate layout rather than image meaning;
- temporal logic receives already-collapsed candidates and cannot recover discarded ambiguity.

The architecture correction is to preserve observations, construct bounded semantic proposals, evaluate competing continuous explanations, and defer selection to typed current/temporal hypotheses.

## Required flow

```text
masked frame evidence
→ immutable raw edge observations
→ bounded-diameter deterministic Y proposals
→ broad region-step + narrow line/pulse evidence
→ continuous boundary/artifact/ambiguity likelihoods
→ soft static prior
→ deterministic semantic deduplication
→ typed boundary / no-interface observations
→ bounded temporal interface
→ external PhaseDetection projection
```

## Immutable raw edge observation

A raw observation is a frozen scalar record derived from one bounded measurement operation. It contains enough information for traceability without retaining a frame or raster map:

- source family and scale;
- local Y and canonical source Y;
- signed polarity when available;
- response strength and horizontal support;
- valid-mask and glare-visible support;
- measurement width/band metadata;
- deterministic source-local identity.

Raw observations are never marked selected/rejected and are never mutated with downstream score fields. Rejection, selection and debug projection belong to later hypothesis/result types. The same ordered observations must produce byte-equivalent scalar proposal content.

## Bounded-diameter deterministic Y proposals

Proposal construction groups only observations that can describe one local transition within an explicit maximum Y diameter. It must not use unbounded single-link chaining: every member must remain within the proposal diameter, even when adjacent observations form a bridge.

Determinism requirements:

1. sort by canonical scalar keys independent of input order;
2. apply fixed eligibility and tie-break rules;
3. cap proposal count and observations per proposal;
4. choose representative Y by a fixed semantic rule, not mutable score order;
5. retain the member observations and proposal span;
6. emit separate proposals when two edge groups cannot fit within one bounded diameter.

Representative Y uses broad region-transition evidence when that evidence is available and internally consistent. Otherwise it uses the deterministic center/median projection of the bounded narrow evidence. Integer/source-coordinate projection occurs only at the compatibility boundary; internal likelihood calculations may retain finite sub-pixel scalars.

## Broad multi-scale region-step evidence

Broad evidence asks whether image regions above and below a proposed Y have a persistent signed intensity transition. It is evaluated across a small fixed set of bounded band scales.

Required evidence includes:

- signed above/below contrast at each scale;
- visible valid-pixel support at each scale;
- scale consistency and polarity consistency;
- transition localization around the proposal;
- glare/exclusion conflict;
- broad-step strength independent of narrow edge peak height.

No single scale is authoritative. Missing support remains unavailable evidence rather than zero-strength negative evidence. A true weak transparent-oil boundary may have moderate but scale-consistent region evidence even when its narrow peak is weak.

## Bounded narrow line/pulse evidence

Narrow evidence asks whether the proposal is better explained by a thin line, rim, scratch, reflection pulse or paired structural edges.

Required evidence includes:

- local edge peak strength and horizontal coverage;
- signed lobe order around the proposal;
- paired-edge separation within a bounded width;
- line/pulse symmetry and center offset;
- persistence across narrow scales;
- overlap with border, exclusion, glare and static evidence;
- support that is independent from broad region-step evidence.

A narrow pulse is not automatically an artifact, and a paired edge is not automatically rejected. It raises an artifact explanation likelihood that competes with boundary evidence. A real boundary near a structural line must keep both explanations available.

## Continuous likelihood contract

Each semantic proposal produces finite normalized likelihoods or scores for at least:

- `boundary_likelihood`;
- `artifact_likelihood`;
- `ambiguity_likelihood`;
- evidence availability/visibility;
- signed polarity confidence;
- broad-step and narrow-pulse component scores.

These values remain continuous through current-frame reasoning. An explanatory enum may be projected for logs, UI or tests, but it is never a hard gate that discards the underlying likelihoods. In particular, labels such as “boundary-like,” “line-like” or “ambiguous” are descriptions of the score relationship, not selection commands.

Ambiguous evidence is first-class output. Close boundary/artifact likelihoods, conflicting polarity or insufficient visible support must survive into no-interface and temporal comparison. The pipeline must not coerce ambiguity into either a selected line or candidate absence.

## Soft static prior

Static maps contribute a bounded prior derived from repeated horizontal evidence. They do not mask pixels, delete observations or hard-reject proposals.

The prior must:

- be candidate/proposal local;
- include coverage and confidence in the learned static evidence;
- be capped so strong current broad-step evidence can overcome it;
- preserve contradictory current evidence;
- remain neutral when the static sample is unavailable or undercovered;
- avoid treating a short learned sample as permanent scene truth.

Static evidence affects `artifact_likelihood` and/or temporal transition cost. It does not directly set `selected`, `rejected` or no-interface.

## Deterministic semantic deduplication

Deduplication occurs after semantic evidence is available. Two hypotheses may be combined only when they describe the same bounded Y transition and have compatible semantic evidence. Source identity alone is insufficient, and spatial proximity alone must not merge opposite explanations.

The deduplicated hypothesis retains:

- deterministic representative Y and diameter;
- all contributing raw observation identities;
- broad/narrow evidence summaries;
- boundary, artifact and ambiguity likelihoods;
- polarity availability/confidence;
- static prior contribution;
- deterministic provenance for debug projection.

Tie-breaking uses fixed scalar keys. Input ordering, dictionary ordering and mutable selected/rejected fields must not influence the result.

## Typed no-interface and temporal interface

Current-frame output to temporal reasoning is a typed union, conceptually:

```text
BoundaryObservation(hypothesis, likelihoods, visibility)
NoInterfaceObservation(likelihood, full_empty_evidence, visibility)
AmbiguousObservation(boundary_options, no_interface, reason)
UnavailableObservation(reason, visibility)
```

No-interface is positive typed evidence, not the absence of a surviving boundary candidate. Full/empty projection remains the responsibility of compatible fill-state reasoning using image evidence and prior state.

The temporal interface consumes immutable scalar observations and returns a typed decision containing selected hypothesis identity, accepted raw Y when any, confidence/margin, transition reason, smoothing-clear instruction and bounded diagnostic scalars. It retains no frame, crop, mask, raster profile or unbounded candidate history.

Temporal reasoning must preserve:

- separate boundary, no-interface, ambiguous and unavailable transitions;
- bounded reacquisition after genuine rapid movement;
- stale smoothing removal after stable no-interface/unavailable evidence;
- Glass-local state isolation;
- bounded beam/window/count state;
- current evidence authority over a soft prior when sufficiently strong.

## External PhaseDetection compatibility

`OpenCvPhaseDetector.detect` continues to return the existing `PhaseDetection` shape through the application port. S5-B maps the typed decision to the existing oil-level, confidence, fill-state, flags, candidate trace and debug-metric fields.

The cutover must not require a persisted recipe, user-truth, regression fixture, result bundle or CSV schema change. Internal raw observations and hypotheses may be projected into existing debug structures or runtime-only shadow evidence, but they do not redefine the external product contract.

## S5-B1 shadow implementation

S5-B1 adds the new observation/proposal/likelihood pipeline beside production behavior.

Requirements:

- production `PhaseDetection` values remain controlled by the legacy path;
- shadow results are runtime/test evidence and do not mutate official result bundles;
- the same preprocess/mask inputs may be shared, but shadow types cannot mutate legacy candidates;
- comparison records deterministic proposal identities, likelihood components, no-interface evidence, resource counts and projected decision;
- focused tests prove input-order determinism, bounded diameter/counts and ambiguity preservation;
- an independent architecture/evidence audit is required before cutover.

## S5-B2 production cutover

S5-B2 switches oil-boundary/no-interface/temporal ownership to the audited typed pipeline.

Requirements:

- external detector and persisted contracts remain compatible;
- S5-A Foam pipeline remains independently owned and non-regressing;
- official candidate/debug projection is generated from immutable hypothesis provenance;
- old and new paths are not both allowed to influence production selection;
- controlled base/feature comparison, exact-head audit and canonical validation follow the cutover.

## Legacy removal plan

After production cutover and focused compatibility tests, remove or reduce the replaced ownership in:

- source-count `oil_candidate_consensus` as semantic selection authority;
- monolithic `candidate_scorer` boundary/static pair suppression logic;
- candidate pair/group exceptions that infer semantics from local layout;
- duplicate no-interface comparisons based on surviving scored candidates;
- legacy oil-path inputs that depend on mutable `BoundaryCandidate` selection state.

Compatibility adapters may remain only where required to project new hypotheses into existing debug or `PhaseDetection` fields. Dead parallel decision paths are not retained as fallback.

## CPU and memory bounds

The implementation must define and test finite bounds for:

- raw observations per source and scale;
- number of broad and narrow scales;
- proposal diameter and members per proposal;
- proposals/hypotheses passed to temporal reasoning;
- temporal beam width and history window;
- static-prior state per Glass;
- debug scalar rows produced per frame.

Frame-sized preprocess maps may exist only for the current call and existing bounded static map. No frame, crop, mask, profile array or proposal list accumulates across frames. Complexity must remain linear in current-frame pixel count plus bounded proposal/temporal work; it must not become quadratic in video duration.

## Validation matrix

| Area | Required evidence |
|---|---|
| Observation/proposal | Immutable types, input-order determinism, bounded diameter, no chaining bridge, finite values |
| Broad boundary | Clear and weak transparent-oil steps across scales; polarity and unavailable-support handling |
| Narrow artifact | Structural line, rim, glare pulse, paired edges and real boundary adjacent to structure |
| Ambiguity | Conflicting broad/narrow evidence remains explicit and does not force numeric output |
| Static prior | Persistent structure raises artifact likelihood without erasing a contradictory real boundary |
| No-interface | Full and empty no-interface, glare conflict, boundary/no-interface competition |
| Temporal | Dropout, rapid fill/drain, reacquisition, visible↔no-interface, stale smoothing clear, Glass isolation |
| Compatibility | Existing `PhaseDetection`, recipe, truth, benchmark and result-bundle contracts |
| Foam non-regression | S5-A Foam and shimmer controlled cases unchanged or within accepted gate |
| Performance | CPU median, retained scalar counts, long-duration memory and packaging obligations |
| Real evidence | Controlled external fixture comparison and later S6 real-video/Windows validation |

The repository sample video is an architecture evidence probe only. It can demonstrate deterministic behavior and expose obvious conflicts, but it is not annotated canonical truth and cannot establish detector accuracy.

## Non-goals

- Large learned models, checkpoints, CUDA or dedicated-GPU compute.
- A new persisted schema or breaking `PhaseDetection` interface.
- A broad Foam redesign.
- Automatic threshold tuning from one video or fixture.
- File-name, fixture-ID or scene-specific exceptions.
- Annotated MP4, Result Review expansion or S6 platform qualification.
- Preserving legacy candidate/scorer code as an indefinite second production engine.

## Unresolved risks

- Broad transition and narrow pulse likelihoods may remain correlated under blur, fog and refractive motion.
- Static evidence learned from limited timestamps may conflict with moving reflections or a stationary true boundary.
- Full versus empty classification remains difficult when visible intensity is camera/lighting dependent.
- Likelihood calibration may vary across Glass geometry and camera exposure while settings remain shared.
- Shadow instrumentation can bias CPU measurements unless production-equivalent and shadow-only costs are reported separately.
- Existing debug consumers may assume mutable `BoundaryCandidate` semantics and require a compatibility projection audit.

These risks remain in the [work plan](../00-project/work-plan.md) until evidence closes them.
