# S11 Detector Responsibility Architecture

**Status:** `R12 IMPLEMENTED — SECURE-WINDOWS VALIDATION PENDING`

## Purpose and authority

This document is the durable responsibility owner for the production S11
detector. The exact current gate remains in the [work plan](../00-project/work-plan.md),
and completed measurements remain in [`../60-evidence/s11/`](../60-evidence/s11/).

R12 is the checked-in production runtime. R5–R11 failed secure-Windows holdouts
and have no acceptance authority. Their documents preserve causes, controls and
failed alternatives; they do not define runtime routing when they conflict with
this document or the
[R12 architecture](s11-r12-phase-composition-replacement-architecture.md).

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

User-confirmed artifact templates reject only candidate geometry that matches
the reviewed point, line or region. High-recall candidates have a bounded
family reserve so stronger residue rows cannot consume all admission capacity,
but calibration does not grant authority to any unmatched row. Registered
motion may group candidates; it cannot create Oil identity or an anchor.

All candidate families expose typed evidence availability. Missing material,
phase, motion, optics or artifact evidence is unknown, not measured zero. A
candidate cannot satisfy an anchor gate through a feature its representation
never computed.

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
authority, and R12 preserves that separation. Oil and Foam are resolved
independently and meet only during final composition.

## Oil and state sequence authority

`OilObservationResolver` may select only an explicitly eligible hypothesis from
the same frame. It may compare physical continuity, material anchors, registered
exposure-compensated change, optics/static opposition and typed no-interface
evidence over a bounded completed window.

A recurring fixed row is not trusted solely because it persists. Anchor
authority requires independent same-frame phase/material identity or strong
same-frame corroboration. Motion-only bootstrap and the R11 distinct-lower
anchor route do not exist. A lower candidate may be reserved for fair
evaluation, but geometry alone cannot publish it. Conversely, a stationary real
Oil interface may remain eligible when its direct phase/material evidence is
strong.

The resolver never interpolates, carries forward or invents an Oil coordinate.
Every numeric result must retain same-frame candidate provenance. A frame with no
defensible candidate remains image-supported FULL/EMPTY or `UNKNOWN_REVIEW`.

## Foam episode authority and composition

`FoamEpisodeResolver` receives only eligible coherent raw Foam material after the
Oil/state path is fixed. Confirmation requires layer topology plus registered,
exposure-compensated material evolution or another independent dynamic cue.
Brightness, a single bubble, component-mask jitter, global exposure change or a
static glare prelude is insufficient.

Foam/residue identity is bounded by age, missing duration and cumulative drift.
It may oppose a matching row from any candidate family but cannot persist
indefinitely after the observed material disappears. The final composition
rules are:

- visible Oil plus confirmed Foam becomes `FOAMING_VISIBLE`;
- image-supported FULL plus confirmed Foam becomes `FULL_WITH_FOAM`;
- confirmed Foam may remain public and graph-valid while Oil/state is unknown;
- rejected or pending Foam remains non-public diagnostic evidence; and
- Foam cannot change the selected Oil coordinate or state path;
- normal composition uses the ordered fronts `foam_y < oil_y`; and
- the bottom of a broad raw material mask is diagnostic and cannot veto an
  otherwise ordered pair.

A previous rejected Foam/Oil alias is not sufficient to reject a later Foam
episode. Alias continuation also requires new same-frame coincidence evidence,
so vertically separated Oil and Foam layers may both remain public.

There is one final Foam owner and one Oil/state owner, joined once by
`ObservationSequenceResolver`. No historical current-frame Foam gate remains a
second final owner.

## Temporal and initial-state boundaries

The serialized online reducer retains acquisition-time continuity and bounded
reacquisition semantics for preview/current-frame evidence. It does not feed
coordinates into the completed-window owner and does not compete with the final
R12 projection.

The completed-window resolvers use bounded history only to select observations
already supported by their own frames. Missing intervals stay missing. A
user-confirmed initial FULL/EMPTY state affects the initial distribution and
report context only; it cannot create a valid detector sample or a numeric
coordinate. FULL/EMPTY counts as valid only with explicit current-image state
provenance.

[Initial-State Retrospective Reconstruction](initial-state-retrospective-reconstruction-architecture.md)
remains a separate downstream interpretation. R12 permits it to interpret only
the leading unresolved prefix after anchor-grade direction proof; it cannot
rewrite observed samples, coverage or numeric Oil.

## Public projection and report boundary

Final sequence resolution occurs before `TrackingSample`, events, judgments and
report generation. Resolver failure, changed frame identity or changed result
cardinality aborts analysis. Downstream code cannot reread candidates or debug
metrics to replace the final observation. `TrackingSample` stores independent
`oil_is_valid` and `foam_is_valid`; legacy `is_valid` remains Oil/state validity
for events, extrema, captures and judgments. The graph uses each series' own
validity.

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
- R5 through R11 are field-failed, superseded sequence designs and must not be
  restored as alternate owners.
- Historical exact counts and fingerprints are evidence provenance, not current
  acceptance targets.

The current preservation and holdout gates are defined by the
[R12 validation contract](../30-validation/s11-r12-phase-composition-replacement-validation.md)
and the [S11 real-field validation contract](../30-validation/s11-real-field-detector-effectiveness.md).
The completed local implementation evidence is
[S11-R12 Phase/Composition Replacement](../60-evidence/s11/s11-r12-phase-composition-replacement.md).

## Non-authorities

Truth files, provisional annotations, source-video identity, Recipe identity,
frame identity and private field timestamps may validate the detector but cannot
change production behavior. Debug probes, report presentation, retrospective
interpretation and aggregate coverage likewise cannot publish a detector
observation.
