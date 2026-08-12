# S11-R7 Evidence-Tiered Trajectory Architecture

> Historical architecture. The secure-Windows R7 holdout failed; current
> authority is [R8 observation recovery](s11-r8-observation-recovery-architecture.md).

**Status:** `IMPLEMENTED — LOCAL VALIDATION PASSED`

## Purpose

R7 is the production replacement for the field-failed R6 final observation authority. It preserves R6's
independent Oil/Foam rasters, optics evidence and same-frame provenance, but
removes the remaining hidden dependence on the old current-frame temporal
selection.

The product objective is a physically supportable observation story: initial
FULL/EMPTY context, visible entry, rise/fall/hold, bounded Foam and meaningful
extrema. It is not maximum frame coverage and it is not exact per-frame truth.

The causal authority is the
[R6 secure-Windows failure](../50-diagnostics/s11/s11-r6-secure-windows-field-failure.md).
External transparent-vessel work is recorded in the
[implementation reference log](../70-reference/implementation-reference-log.md)
and supports relative/multi-line/path evidence plus explicit optical controls;
it supplies no transferable field thresholds.

## Replacement, not stacking

R7 keeps one completed-window resolver and one final composition point. It does
not add a third tracker over R6.

| R6 behavior | R7 disposition |
|---|---|
| current-frame `candidate.selected` grants direct/semantic anchor authority | remove from completed-window decisions |
| one binary `sequence_eligible` bit covers every non-hard-invalid candidate | replace with typed authority tier |
| direct-anchor and anchor-support bonuses can derive from the same old selection | remove duplicate authority |
| fixed 2–3-frame anchor censor deletes long same-frame candidate runs | replace with anchor-bounded continuation semantics |
| every R6 stream bypasses retrospective initial-state interpretation | restore separate leading-prefix inference |
| one dynamic Foam frame can confirm a grouped episode | require multi-frame onset/material evolution |
| every numeric sample can independently create an extremum/event | restrict landmark authority to trusted trajectory evidence |

The existing serialized current-frame reducer remains preview/debug compatibility
only. Its selected row, confidence, decision margin, acceptance mode, tracker
action and reason are preserved for diagnostics but are prohibited inputs to the
R7 final path.

## Observation pipeline

```text
registered Glass rasters
  -> independent raw Oil hypotheses / state evidence / Foam material
  -> hard visual safety
  -> typed Oil authority tiers
  -> anchor-cluster construction
  -> same-frame candidate trajectory selection
  -> anchor-bounded continuation classification
  -> image-supported Oil/FULL/EMPTY observations
  -> independent multi-frame Foam episode resolver
  -> one final composition
  -> immutable TrackingSamples
  -> separate initial-state retrospective interpretation
  -> trusted events / report
```

## Oil authority tiers

Every finite Oil hypothesis receives exactly one final-analysis tier before path
selection.

### `HARD_INVALID`

The candidate is unavailable to every later owner when visibility/evidence is
materially unavailable or severe optics, exclusion, border or structural
conflict proves the row invalid. It cannot anchor, continue, oppose or borrow
authority.

### `CANDIDATE_ONLY`

The row is a retained same-frame alternative with insufficient independent
identity. It may participate in diagnostics and competing-interface reasoning,
but cannot publish numeric Oil.

### `CONTINUATION_ELIGIBLE`

The row has enough direct same-frame material evidence to represent the already
established physical interface, but not enough independent proof to establish
one. It may publish only when it lies on a bounded physically consistent path
between or immediately adjacent to trusted anchor clusters.

Continuation evidence cannot:

- start a trajectory;
- release FULL/EMPTY by itself;
- reacquire after an unsupported long gap;
- become an anchor because it repeats;
- create an extremum or lifecycle transition without anchor confirmation; or
- gain authority from the old current-frame `selected` bit.

### `ANCHOR_ELIGIBLE`

The row independently identifies the material boundary through either:

1. boundary-dominant current-frame phase/material evidence with bounded artifact
   and ambiguity opposition; or
2. strong cross-ROI material-path evidence supported by registered,
   exposure-compensated evolution that distinguishes the path from fixed optics.

An ambiguous-labeled hypothesis may become an anchor only through the second
independent proof. Current-frame temporal continuity is never independent proof.

## Anchor clusters and trajectory selection

One frame does not establish a reusable anchor. Anchor-eligible rows must form a
bounded cluster across multiple nearby frames with physically compatible Y
motion, or be part of a stronger registered material path whose proof already
spans the required temporal support.

The completed-window path may select only a same-frame candidate. It may use:

- anchor strength and cluster support;
- phase/material quality and optical/static opposition;
- bounded velocity/acceleration continuity;
- FULL/EMPTY transition topology; and
- candidate competition at the same timestamp.

It may not use current-frame tracker selection or interpolate a coordinate.

Between trusted anchor clusters, continuation-eligible candidates may keep the
observed line readable for as long as same-frame support and physical continuity
remain present. A missing candidate remains missing. A one-sided continuation is
bounded by evidence decay and physical motion, not by a fixed universal 2–3
frame deletion horizon.

A recurring fixed track is opposing evidence only when static/optical support is
present and registered material evolution is absent. Stationary real Oil remains
possible when direct phase evidence is independently anchor-grade.

## Confidence and provenance

Numeric Oil confidence is derived from the selected candidate's final R7 tier,
material proof, competition and trajectory support. It has no unconditional
minimum unrelated to source evidence. Visibility and Foam confidence cannot
inflate Oil confidence.

Every final numeric observation carries:

- same-frame candidate identity;
- `R7_OIL_ANCHOR` or `R7_OIL_CONTINUATION`;
- anchor-cluster support and trajectory opposition diagnostics; and
- no current-frame tracker authority flag.

The final debug/review surface must expose the R7 selected kind/tier. Old
`continuous_shadow_boundary` fields may remain as current-frame diagnostics but
must not be presented as the reason for the official final observation.

## FULL/EMPTY and initial-state interpretation

Current detector FULL/EMPTY remains valid only with affirmative same-frame raw
no-interface evidence. A confirmed initial state never creates numeric Oil and
never counts as observed detector coverage.

After final observations are immutable, the separate retrospective owner may
interpret the leading unresolved prefix as the explicitly confirmed initial
`FULL_NO_INTERFACE` or `EMPTY_NO_INTERFACE` when:

- the confirmation is current-run/session scoped;
- at least two anchor-grade Oil observations establish one consistent transition
  trajectory;
- the observed direction agrees with the confirmed state; and
- no direct contradictory image-supported state occurs first.

The first trusted boundary may already be in the middle of the Glass. Entrance
topology is retained as explanatory provenance, but is not a prerequisite that
would discard a real transition simply because acquisition occurred after the
interface crossed the top/bottom entrance band. Opposite anchor motion remains a
conflict.

Ordinary UNKNOWN frames and raw/rejected Foam do not block this interpretation.
Hard decode failure remains recorded but does not turn the prior into detector
truth. The inferred interval is separately persisted and shown in the report;
original samples and observed coverage remain unchanged.

For a confirmed FULL run followed by a trusted descending trajectory, the
prefix before the first trusted Oil observation is interpreted as
`FULL_NO_INTERFACE`. The EMPTY/rising case is symmetric.

## Foam episode authority

Foam remains independent of Oil selection. A public episode requires:

- eligible coherent layer material;
- at least two registered dynamic frames in one bounded onset group;
- spatially distributed internal/non-rigid change rather than one front shift;
- sufficient dynamic support across the group, not only among the changed
  frames; and
- static/glare opposition below the episode-level limit.

A single dynamic disturbance, global exposure change, component-mask jitter,
one bubble or persistent start-of-video glare cannot confirm Foam. Confirmation
does not backfill a static prelude and cannot mask, select or veto Oil.

## Event and report authority

Anchor observations own independent lifecycle landmarks. Continuation samples
may improve graph readability and trend timing inside an anchor-supported run,
but they cannot alone create:

- `MAXIMUM_OIL_LEVEL` or `MINIMUM_OIL_LEVEL`;
- `OIL_DROP_START`, recovery or zero crossing;
- an event immediately after a long unsupported gap; or
- a capture guide presented as a trusted landmark.

Trend events require a bounded sequence with anchor support on the relevant
side. Extrema select from anchor-grade observations. The graph may display
continuation observations distinctly and retain dashed display-only bridges
over truly missing samples. Initial-state interpretation appears as a state band
or narrative, never a fabricated Oil coordinate.

## Resource and compatibility boundary

R7 remains deterministic, CPU/OpenCV based and bounded by sampled frame count
and candidate top-K. It adds no network/model dependency, video/truth identity
branch or Recipe schema change. Existing result-version support remains; any new
provenance flag is additive.

Legacy/fake detectors without R7 candidate tiers retain their compatibility
projection but cannot silently claim R7 authority. R6 exact fingerprints become
historical evidence and are not golden outputs.

## Implementation and cleanup boundary

R7 is a vertical replacement at the final-authority seam, not another revision
branch layered over R4/R5/R6. `ObservationSequenceResolver` calls one R7 Oil/state
owner and one R7 Foam owner. The old online reducer remains upstream diagnostic
compatibility only.

Candidate-local raster evolution is isolated in `temporal_raster_evidence.py`,
and ordinary/supplemental proposal families share hard terminal-cap topology
through `oil_phase_topology.py`. The raw feature key `r6_material_path` is retained
for compatible candidate/debug schema only; it grants no R6 authority. Larger
mechanical package splitting remains the separately gated S11-M maintainability
work and must not be mixed with the private field qualification.

Local implementation evidence is recorded in
[S11-R7 Evidence-Tiered Trajectory](../60-evidence/s11/s11-r7-evidence-tiered-trajectory.md).

## Stop conditions

Stop or narrow the implementation when any of the following occurs:

- selected-old-tracker identity changes R7 output;
- a continuation-only row starts/reacquires a trajectory or creates an extremum;
- sample2's clear stationary Oil is lost;
- checked sample3 inflow/Foam/full or sample4 retained Oil/Foam behavior becomes
  less faithful to direct images;
- a controlled empty/reflection/glare scene becomes numeric;
- a one-dynamic-frame/static Foam sequence becomes public; or
- Windows direct review shows the true interface absent from the candidate
  lattice over clear transitions.

The last case is a representation/acquisition failure. It must not trigger more
score tuning; the next options are registered temporal representation,
controlled illumination/polarization or user-authored artifact regions.
