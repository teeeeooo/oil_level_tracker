# S11 Detector Responsibility Architecture

**Status:** `R20 IMPLEMENTED — LOCAL PASS / WINDOWS REQUIRED`

## Purpose and authority

This document is the durable responsibility owner for the production S11
detector. The exact current gate remains in the [work plan](../00-project/work-plan.md),
and completed measurements remain in [`../60-evidence/s11/`](../60-evidence/s11/).

R20 is the checked-in production runtime at the local implementation head;
canonical secure-Windows validation remains required. R5–R19 preserve failed
holdouts, accepted local contracts and causal history as applicable, but have no
current runtime routing when they conflict with this document or the
[R20 architecture](s11-r20-delayed-drain-reacquisition-architecture.md).

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
| completed-window Oil/FULL/EMPTY selection | `OilObservationResolver` / `OilMaterialPhaseLifecycleOwner` | sole final Oil/state selection owner; R20 owns the coordinate-free partial-fill ownerless barrier and one delayed reacquisition attempt |
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

### R20 partial-fill ownerless context and delayed reacquisition

`OilMaterialPhaseLifecycleOwner` is the sole owner of the R20 adaptation inside
the existing lifecycle boundary. After confirmed initial `EMPTY` establishes a
genuine fill chain and that dynamic owner is lost before `DRAINING`, its
`PartialFillOwnerlessBarrier` retains only constant-size episode provenance and
ordinary loss grace. It does not accumulate rows, coordinates, motion, scores or
lookahead; the retained fill snapshot Y/frame is diagnostic context only.

After `maximum_lost_frames + 1` grace frames, one unique same-frame
`ANCHOR_ELIGIBLE` row may start the episode's single delayed R19-shaped attempt
when its existing phase identity is `DIRECT_INTERFACE` or
`ORDERED_LOWER_INTERFACE`, its tracklet is confirmed/continuing and compatible,
and strict material support passes. Direct partial-fill release remains first;
R19 near-snapshot recovery remains second; delayed reacquisition is third. A
qualifying anchor set consumes the attempt even when ambiguous or unable to
confirm, and it cannot reseed until a new fill episode is established. Existing
R19 step, loss, stagnation, handoff, material and evidence-window bounds apply
after seeding. The current row on confirmation is the only row that can be
selected and published. Snapshot distance and loss age are diagnostics, never
identity or authority inputs.

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
provenance. R20's ownerless barrier is phase context, not physical identity;
it cannot publish a snapshot coordinate or authorize a delayed row without the
current row's independent authority, phase identity, tracklet and material
evidence.

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

R18 and R19 remain preserved as the historical direct/near-snapshot lifecycle
contracts. R20 is the current bounded delayed-reacquisition adaptation; its
implementation and local evidence are routed through the [R20 architecture](s11-r20-delayed-drain-reacquisition-architecture.md),
[R20 validation contract](../30-validation/s11-r20-delayed-drain-reacquisition-validation.md)
and [R20 local evidence](../60-evidence/s11/s11-r20-delayed-drain-reacquisition.md).

## History Review

- Logic-map nodes: `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `PUBLICATION-PROVENANCE`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F05`, `S11-F08`, `S11-F09`, `S11-F10`
- Prior mechanisms reviewed: R16 reciprocal physical ownership, R17 owner-loss dead end, R18 lifecycle closure and causal rerun, and R19 bounded direct/near recovery with their current architecture, validation and evidence records.
- Prior mechanisms rejected: motion-only bootstrap, stale-coordinate or stale-ID transfer, global threshold widening, selector/projection repair, unbounded lookahead, interpolation/carry, private field identity and Foam-to-Oil coupling.
- Preserved contracts: one generic detector, initial EMPTY safety, coordinate-free FULL, same-frame authority/material identity, distinct physical IDs, bounded handoff and evidence, ambiguity/material fail-closed behavior, exact selected-candidate/sequence/CSV provenance and independent Foam.
- Difference from prior failures: R20 retains only constant-size ownerless phase context, waits through ordinary grace, starts one fresh-anchor attempt per established-fill episode and applies existing R19 bounds only to current evidence; snapshot distance and loss age are not identity.
- Logic-map impact: UPDATED — the current lifecycle and diagnostic owner now includes R20's bounded ownerless barrier and delayed route, while all downstream owner boundaries remain unchanged.
- Failure-registry impact: NONE — R20 closes existing F04/F05/F08/F09/F10 guards without establishing a new durable causal mechanism; F02 remains the authority-funnel guard.

## Detector Governance

- Logic-map nodes: `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F04`, `S11-F05`, `S11-F08`, `S11-F09`, `S11-F10`
- First harmful stage: Accum's established partial-fill owner loss at `OIL-PHASE-FILL` remains the R20 adaptation seam; canonical Windows effectiveness and reviewed-Y outcome are still unknown pending the required field replay.
- Logic-map impact: UPDATED — the current map records the R20 lifecycle route and additive diagnostics.
- Failure-registry impact: NONE — the implementation preserves the existing guarded mechanisms and does not add a new registry entry.

The current R20 preservation and canonical Windows holdout gates are defined by
the [R20 validation contract](../30-validation/s11-r20-delayed-drain-reacquisition-validation.md)
and the [manual Windows procedure](../40-operations/manual-gui-windows-checklist.md),
with reviewed field truth in
[windows-sample1-heating-coldstart-reviewed-truth.md](../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md).
The R12/R18 contracts and local evidence remain historical failed-holdout
context; R19 remains the historical near-snapshot baseline and none is a
current runtime owner.

## Non-authorities

Truth files, provisional annotations, source-video identity, Recipe identity,
frame identity and private field timestamps may validate the detector but cannot
change production behavior. Debug probes, report presentation, retrospective
interpretation and aggregate coverage likewise cannot publish a detector
observation.
