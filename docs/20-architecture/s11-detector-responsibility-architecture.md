# S11 Detector Responsibility Architecture

**Status:** `ACTIVE`

## Purpose and authority

This document is the durable responsibility owner for the production S11
detector. The exact current gate remains in the [work plan](../00-project/work-plan.md),
and completed measurements remain in [`../60-evidence/s11/`](../60-evidence/s11/).

The active implementation is R6. R2–R5 documents preserve the causes, controls
and failed alternatives that led here; they do not define current runtime
routing when they conflict with this document or the
[R6 architecture](s11-r6-optics-aware-observation-architecture.md).

## Production observation path

```text
Glass ROI / exclusions
  -> photometric preprocessing and optics opposition
  -> independent Oil candidates, typed no-interface evidence and raw Foam material
  -> bounded registered temporal evidence
  -> OilObservationResolver (Oil or image-supported FULL/EMPTY)
  -> FoamEpisodeResolver (independent Foam episode)
  -> ObservationSequenceResolver (one composition point)
  -> one PhaseDetection per sampled frame
  -> TrackingSample / events / judgment / report
```

The detector is evidence-preserving and fail-closed. It may retain several
same-frame candidates, but only one eligible same-frame Oil candidate can become
the canonical numeric observation for a frame. Absence of a numeric boundary is
not proof that physical Oil is absent.

## Owner map

| Responsibility | Production owner | Authority boundary |
|---|---|---|
| ROI preprocessing and optics opposition | vision preprocessing | produces evidence; cannot publish Oil, Foam or state |
| current-frame Oil proposals and semantics | S5-B observation pipeline | produces bounded eligible hypotheses and typed evidence |
| completed-window Oil/FULL/EMPTY selection | `OilObservationResolver` | sole final Oil/state selection owner |
| completed-window Foam confirmation | `FoamEpisodeResolver` | sole final Foam episode owner; runs after Oil/state |
| per-frame composition and identity checks | `ObservationSequenceResolver` | sole final composition point |
| acquisition-time continuity | serialized online Oil reducer | preview/current-frame evidence only; no completed-analysis override |
| `TrackingSample`, events and report | application/report projection | consumes final observations; cannot repair or invent them |

## Current-frame evidence responsibilities

### Oil candidates

Oil proposals are generated from the base effective ROI, without a Foam mask or
Foam-front cutoff. Region/phase, Sobel, Canny and Hough evidence may propose
competing rows; Spatial may provide bounded x-resolved positive corroboration.
Every candidate retains eligibility, material/phase support, optical opposition,
anchor provenance and any registered temporal support needed by the final owner.

Spatial is evidence, not a publication owner. It cannot override unavailable or
affirmative no-interface evidence, and it cannot turn a flat or unidentifiable
scene into numeric Oil merely to improve coverage.

### No-interface state evidence

FULL and EMPTY are typed current-raster observations, not inferred numeric
levels. Their emission uses raw no-interface likelihood for the same frame. A
previously projected fill state, Recipe value or initial-state confirmation
cannot serve as evidence for the current frame.

### Foam material evidence

Current-frame Foam processing produces raw material, topology and optics
features. Raw or rejected Foam remains diagnostic evidence only. It has no
authority to mask Oil pixels, cut off Oil candidates, select an Oil boundary,
veto an Oil candidate or establish FULL/EMPTY.

## Hard safety boundary

The following remain hard failures for the responsibility they invalidate:

- unavailable or materially insufficient image evidence;
- severe glare/optics conflict, exclusion conflict or border conflict;
- affirmative same-frame no-interface evidence opposing a numeric Oil boundary;
- proven structural/refractive invalidity; and
- unresolved competing-interface collision where no unique observation is
  defensible.

Hard-invalid evidence cannot regain authority through ranking, anchoring,
neighborhood borrowing, Spatial or temporal selection. Lesser optical/static
overlap is explicit opposition rather than a universal mask.

Foam classification is deliberately absent from this Oil hard-safety list. R6
removed the historical D5 rule that made accepted Foam topology an Oil-routing
authority. Oil and Foam are resolved independently and meet only during final
composition.

## Oil and state sequence authority

`OilObservationResolver` may select only an explicitly eligible hypothesis from
the same frame. It may compare physical continuity, material anchors, registered
exposure-compensated change, optics/static opposition and typed no-interface
evidence over a bounded completed window.

A recurring fixed row is not trusted solely because it persists. A conflicted
candidate may regain anchor authority only when independent registered internal
raster change supports material evolution. Conversely, a stationary real Oil
interface may remain eligible when its direct phase/material evidence is strong.

The resolver never interpolates, carries forward or invents an Oil coordinate.
Every numeric result must retain same-frame candidate provenance. A frame with no
defensible candidate remains image-supported FULL/EMPTY or `UNKNOWN_REVIEW`.

## Foam episode authority and composition

`FoamEpisodeResolver` receives only eligible coherent raw Foam material after the
Oil/state path is fixed. Confirmation requires layer topology plus registered,
exposure-compensated material evolution or another independent dynamic cue.
Brightness, a single bubble, component-mask jitter, global exposure change or a
static glare prelude is insufficient.

The final composition rules are:

- visible Oil plus confirmed Foam becomes `FOAMING_VISIBLE`;
- image-supported FULL plus confirmed Foam becomes `FULL_WITH_FOAM`;
- EMPTY or UNKNOWN is not promoted merely because Foam-like evidence exists;
- rejected or pending Foam remains non-public diagnostic evidence; and
- Foam cannot change the selected Oil coordinate or state path.

There is one final Foam owner and one Oil/state owner, joined once by
`ObservationSequenceResolver`. No historical current-frame Foam gate remains a
second final owner.

## Temporal and initial-state boundaries

The serialized online reducer retains acquisition-time continuity and bounded
reacquisition semantics for preview/current-frame evidence. It does not feed
coordinates into the completed-window owner and does not compete with the final
R6 projection.

The completed-window resolvers use bounded history only to select observations
already supported by their own frames. Missing intervals stay missing. A
user-confirmed initial FULL/EMPTY state affects the initial distribution and
report context only; it cannot create a valid detector sample or a numeric
coordinate. FULL/EMPTY counts as valid only with `R6_IMAGE_SUPPORTED_STATE`.

[Initial-State Retrospective Reconstruction](initial-state-retrospective-reconstruction-architecture.md)
remains a compatibility responsibility for legacy/current-frame streams. An R6
stream is not retrospectively projected a second time.

## Public projection and report boundary

Final sequence resolution occurs before `TrackingSample`, events, judgments and
report generation. Resolver failure, changed frame identity or changed result
cardinality aborts analysis. Downstream code cannot reread candidates or debug
metrics to replace the final observation.

The Oil graph may connect stored finite anchors across a missing run with a
lower-emphasis dashed display bridge. Such a bridge contains only its observed
endpoints and creates no sample, coordinate, CSV value, event evidence, capture
guide or detector history. Extrema, lifecycle events, captures and judgments use
observed samples only. Detailed presentation ownership belongs to the
[Result Observation Report Architecture](result-observation-report-architecture.md).

## Historical preservation boundary

- S5-B and S11 Slices A–D preserve proposal, ambiguity and hard-safety lessons.
- R2, R3 and R4 preserve causal diagnostics and controlled negative families,
  but their D5/Foam-to-Oil routing is not current runtime authority.
- R5 is a field-failed, superseded sequence design and must not be restored as an
  alternate owner.
- Historical exact counts and fingerprints are evidence provenance, not current
  acceptance targets.

The current preservation and holdout gates are defined by the
[R6 validation contract](../30-validation/s11-r6-optics-aware-observation-validation.md)
and the [S11 real-field validation contract](../30-validation/s11-real-field-detector-effectiveness.md).

## Non-authorities

Truth files, provisional annotations, source-video identity, Recipe identity,
frame identity and private field timestamps may validate the detector but cannot
change production behavior. Debug probes, report presentation, retrospective
interpretation and aggregate coverage likewise cannot publish a detector
observation.
