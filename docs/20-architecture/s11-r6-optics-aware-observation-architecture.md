# S11-R6 Optics-Aware Observation Architecture

**Status:** `ACTIVE`

## Purpose

R6 replaces the field-failed R5 final-analysis owners and repairs the detector
at the evidence boundary. Its output should let a user understand the observed
Oil history without presenting fixed optics, a prior-only state or raw Foam as
physical truth.

R6 is not another layer over R4/R5. The accepted runtime has one vocabulary and
one composition point:

```text
ROI raster
  -> photometric normalization + optics opposition
  -> independent Oil hypotheses / no-interface evidence / raw Foam material
  -> bounded registered temporal evidence
  -> Oil-or-state observation resolver
  -> independent Foam episode resolver
  -> one public PhaseDetection per sampled frame
  -> TrackingSample / event / report
```

## Replacement and deletion map

| R5 runtime behavior | R6 owner | Disposition |
|---|---|---|
| sequence Oil/state lattice with repeated prior emissions | Oil observation resolver | replace; prior applies only at sequence start and has no validity authority |
| sequence Foam resolver that resurrects raw candidates | Foam episode resolver | replace; rejected/ineligible evidence never enters an episode |
| current-frame accepted Foam masking Oil | independent Oil raster path | remove; Foam may constrain composition only after both observations exist |
| saturation-only glare | optics evidence | replace with saturation plus relative bright-ridge/caustic opposition |
| projected `fill_state` reused as evidence | typed raw no-interface metrics | remove circular read |
| prior-only FULL/EMPTY counted valid | detection-to-sample projection | mark invalid unless current raster provides affirmative state support |

Once migrated callers and tests no longer reference the R5 modules, those
modules are deleted rather than retained as dormant alternate owners.

## Optics evidence

The detector distinguishes a pixel being bright from an optical pattern being a
credible material observation. In addition to absolute saturation, the bounded
optics map may use:

- local brightness residual relative to a large illumination field;
- low-chroma bright support for white specular reflection;
- vertically elongated/ridge-like bright structure and its halo; and
- learned recurrence in representative static frames.

The map is opposition, not a universal hard mask. A candidate becomes hard
invalid only when visibility/availability or severe conflict crosses the
existing hard-safety boundary. Lesser overlap remains an explicit candidate
feature available to temporal selection.

## Oil evidence and temporal selection

Oil hypotheses are generated from the base effective ROI without a Foam mask or
Foam-front cutoff. Each projected candidate explicitly carries:

- whether it is eligible for later comparison;
- current-frame material, ambiguity and optical-opposition terms;
- direct selection/anchor provenance; and
- registered temporal support when available.

Temporal selection may choose only an eligible same-frame hypothesis. It may use
continuity and independent anchor clusters, but it cannot create, interpolate or
carry a coordinate. A recurring fixed row is opposed only when it is both
optically/static-like and lacks registered material evolution. Stationary real
Oil remains possible when phase/material evidence is strong.

### Material-texture conflict

A wide bright or textured layer is deliberately not synonymous with Foam, but a
row inside that layer also cannot become an Oil anchor merely because it repeats.
R6 therefore separates candidate existence from anchor authority:

- a low-conflict cross-ROI phase path may anchor directly;
- a terminal supplemental path without semantic anchors requires broad support
  across the ROI sectors;
- a moderately conflicted material boundary may recover anchor authority only
  when registered, exposure-compensated internal raster change independently
  proves material evolution; and
- an identical/static conflicted raster remains unanchored even when repeated.

Registered material change is an Oil-anchor feature, not accepted Foam and not a
permission for Foam to mask or select Oil. This distinction preserves the late
sample4 material boundary while keeping pixel-identical Oil/glare latent-cause
collisions fail-closed.

## FULL/EMPTY and initial state

FULL/EMPTY nodes receive emission only from typed current-raster no-interface
likelihood. A current or previously projected `fill_state` is never evidence for
itself.

A user-confirmed initial state affects only the initial distribution and report
context. Prior-only continuation is explicitly unobserved and cannot count as
valid detector coverage. A sustained eligible Oil path may release the prior at
any Glass position when the entry itself was missed; edge proximity is positive
support, not an absolute lock.

## Foam evidence and composition

Raw Foam must be material-, topology- and time-supported. Brightness, one bubble,
one component or component-mask jitter alone is insufficient. Confirmation
requires a coherent layer and exposure-compensated internal non-rigid change or
another independent material-evolution cue. Fixed glare/static overlap cannot be
overridden by unregistered turnover.

Foam is resolved after Oil/state and cannot select, mask or veto Oil. Composition
is the only meeting point:

- visible Oil + confirmed Foam -> `FOAMING_VISIBLE`;
- image-supported FULL + confirmed Foam -> `FULL_WITH_FOAM`;
- EMPTY or UNKNOWN + Foam-like evidence -> unchanged state/UNKNOWN unless Foam
  itself passes the independent episode contract; and
- rejected Foam remains debug evidence only.

## Public validity and report boundary

A numeric point is valid only with a selected eligible same-frame Oil candidate.
FULL/EMPTY is valid only with affirmative same-frame state evidence. Initial
context may be displayed as context but is not a detector sample.

Graphs may keep display-only dashed connections between observed anchors, but
events, extrema, captures, CSV and judgments use observed samples only. Detector
debug scores remain outside the primary user report.

## Resource and compatibility boundary

The implementation remains CPU/OpenCV based, bounded per Glass and deterministic.
It adds no video/truth identity branch, network/model dependency, Recipe schema or
unbounded raster history. Preview/redetection and completed analysis share the
same current-frame evidence; completed analysis adds only the bounded temporal
selection step.

## Stop conditions

Stop or revert a mechanism if it creates a long wrong-interface path, publishes
Foam on a checked Foam-absent interval, loses retained sample2 Oil or genuine
sample3/sample4 Foam, turns a controlled glare/no-interface negative numeric, or
improves only aggregate coverage without better source-image agreement.
