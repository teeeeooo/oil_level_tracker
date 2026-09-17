# S11 Interface Observability Witness Architecture

**Status:** proposed next implementation contract; trace-only stage is authorized
by the current S11 direction, but no runtime behavior is accepted by this
document.  
**Parent design:** [Physical Interface Evidence Repair](s11-physical-interface-evidence-repair-design.md).  
**Validation:** [Interface Observability Witness Validation](../30-validation/s11-interface-observability-witness-validation.md).  
**Assessment:** [Transparent-Interface Detector Direction](../50-diagnostics/s11/s11-transparent-interface-detector-direction-assessment.md).  
**Current runtime:** R22-2 remains unchanged until a later acceptance decision.

## Purpose

Define the smallest observation-layer redesign that can answer three questions
before another temporal repair is attempted:

1. Is the current frame capable of exposing an Oil/refrigerant interface under
   the active optical conditions?
2. Which spatial contour is supported as a material interface rather than a
   vessel reflection, fitting/wall edge, residue stripe or unresolved structure?
3. How uncertain is the contour localization in each part of the sight-glass?

The first implementation is diagnostic-only. It may measure and serialize raw
witnesses, but cannot change candidate count, score, rejection, authority,
tracklet identity, phase state, selector output, Foam output or publication.

## Non-goals

This architecture does not:

- assign a new detector revision/runtime identity before implementation review;
- activate the proposed `OBSERVED_INTERFACE` phase;
- change fill-owner handoff, initial-FULL admission or drain release;
- declare a material/raster path to be the physical interface merely because it
  exists;
- use source family, recurrence, motion or photometric sign as physical identity;
- fit operating thresholds from the 13 public truth frames or from private
  checkpoint coordinates;
- add interpolation, coordinate carry or report-side repair;
- train or deploy a neural network; or
- require export of private Windows media.

## Responsibility boundary

```text
current source frame + Glass ROI/masks + acquisition metadata
  -> bounded contour hypotheses already represented by current candidates
  -> per-sector localization and observability measurements
  -> typed OilInterfaceWitness (trace-only first)
  -> [future, gated] independent support / physical association
  -> existing authority / tracklet / lifecycle / selector / projection
```

The witness is owned at `FRAME-EVIDENCE` / `OIL-CANDIDATE`. It is normalized
once by candidate identity. Later owners consume the same immutable result;
they do not reconstruct a different interface decision from raw dictionaries.

## Core data model

The names below are proposed semantic types. Exact Python module boundaries may
change during implementation review, but their meaning and ownership may not.

### `FrameOpticalObservability`

One record per Glass and source frame:

| Field | Meaning |
|---|---|
| `frame_index`, `glass_id` | exact source identity |
| `acquisition_mode` | passive/uncontrolled, passive/fixed, structured-background, polarized pair or another explicitly configured mode |
| `exposure_identity` | available fixed/auto exposure, gain, white-balance and illumination metadata; missing remains unavailable |
| `visible_fraction` | usable effective-mask support after glare/exclusions |
| `saturation_fraction` | clipped dark/bright support in the effective ROI |
| `glare_fraction` | current optics opposition |
| `texture_reference_available` | whether the acquisition mode provides a usable reference/background channel |
| `status` | `OBSERVABLE`, `DEGRADED`, `UNOBSERVABLE`, or `NOT_EVALUATED` |
| `reasons` | evaluated predicates and unavailable mandatory channels |

`UNOBSERVABLE` means the image does not support a defensible interface decision.
It is not FULL, EMPTY, candidate absence or detector failure. In trace-only mode,
`status` remains `NOT_EVALUATED` while raw availability values are collected.

### `InterfaceContourHypothesis`

A frame-local spatial representation attached to one existing Oil candidate:

| Field | Meaning |
|---|---|
| provenance | candidate input identity, source, source Y, crop transform and generating measurement lineage |
| sector geometry | actual source X range and local/source Y for each available sector |
| localization interval | bounded Y interval or uncertainty for each sector; never inferred from another sector |
| curve summary | optional robust low-order curve/Bézier representation, residual and inlier sectors |
| support mask | which sectors/channels are measured, missing or invalid |
| competing peaks | bounded count and separation of plausible local edge centers |

Initial implementation reuses the existing five-sector material-path grid. Other
candidate families are sampled on the same actual X extents when possible. A
scalar candidate Y remains for compatibility/publication, but it is not treated
as exact truth for every sector of a curved interface.

A curve summary requires at least three valid spatially distinct sectors. It is
a compact descriptor only: fitting cannot invent missing points, recenter the
candidate, add a proposal or grant identity.

### `InterfaceSectorWitness`

One bounded descriptor per valid contour sector. Measurements are made along the
local contour normal where geometry permits; the first implementation may use a
vertical normal with the approximation recorded explicitly.

Required raw groups:

1. **availability and geometry**
   - exact band pixel ranges and valid fractions;
   - candidate/path center, local peak centers and localization uncertainty;
   - curve-normal approximation and mask clipping;
2. **relative photometry**
   - signed and absolute above/below difference at fixed small/medium/large
     scales;
   - locally normalized contrast resistant to global brightness/gain changes;
   - saturation and glare support;
3. **edge topology**
   - normal-aligned gradient magnitude and sign;
   - gradient-direction agreement with the local contour normal;
   - edge-density change above versus below, not edge count alone;
   - width/plateau and competing-peak descriptors;
4. **two-sided material context**
   - near and far material/texture summaries on both sides;
   - internal-stripe evidence when near contrast is not sustained into broader
     region context;
   - current raw material map provenance, never final Foam authority;
5. **structural opposition**
   - static-map, border, exclusion, glare and optics overlap;
   - vessel-contour curvature/fitting-risk descriptor where geometry exists;
   - explicit missing structural reference;
6. **optional acquisition-specific evidence**
   - structured-background displacement and correlation quality;
   - paired-polarization or paired-illumination difference;
   - reference-frame registration uncertainty.

All values retain channel lineage. Values derived from the same grayscale/Sobel
chain cannot be counted as independent evidence merely because they have
different field names.

### `OilInterfaceWitness`

One immutable aggregate per candidate:

| Field | Meaning |
|---|---|
| `contour` | the bounded spatial hypothesis above |
| `sectors` | exact sector witnesses, including unavailable reasons |
| `usable_sector_count` | spatially distinct usable sectors |
| `lineage_groups` | independent/shared raw derivations |
| `observability` | reference to the frame-level optical record |
| `localization_uncertainty_px` | aggregate uncertainty without discarding per-sector intervals |
| `opposition` | typed structural/optical contradictions |
| `decision` | `INTERFACE_SUPPORTED`, `INTERNAL_OR_ARTIFACT`, `UNRESOLVED`, or `NOT_EVALUATED` |
| `decision_reasons` | actual predicates, thresholds and unavailable inputs |

Trace-only implementation sets `decision=NOT_EVALUATED`. A later shadow
classifier may populate the other outcomes, still without affecting production.
Only a separately accepted behavior revision may expose the decision to authority
or association.

## Measurement semantics

### Photometric invariance is bounded, not assumed

Use ratios/local normalization only where denominators and valid support are
explicit. Global brightness/gamma/contrast stress is a robustness control, not
evidence that field illumination changes are equivalent. Sign is retained for
diagnostics, but no universal Oil-dark/Oil-bright rule is allowed.

### Interface versus internal stripe

A localized edge is insufficient. The witness must compare immediate bands with
broader two-sided context and edge-density/material changes. A thin stripe can
produce a strong near contrast yet return to the same material context on both
sides. A true interface may also have weak or inverted gray contrast, so the
classifier requires multiple complementary channels and may remain unresolved.

The existing public probe shows that `abs(near)-abs(far)` is negative for many
truth-near candidates and overlaps remote geometry. That scalar cannot become a
new veto or authority gate by itself.

### Vessel reflection and fitting risk

Where the Glass boundary/shape is known, record whether a candidate follows
high-curvature vessel regions, fixed fittings, cap/border geometry or persistent
static reflections. This is opposition, not automatic rejection: a real
interface can cross a reflective region. The decision must preserve per-sector
support and may classify the result as unresolved when physical causes overlap.

### Localization uncertainty

Uncertainty increases when:

- several comparable peaks exist inside the bounded search interval;
- peak center changes materially with scale or sampling center;
- valid support is clipped by masks/glare;
- only one or two sectors support a curve;
- a scalar median is far from one or more native sector rows; or
- registration/reference correlation is weak.

Uncertainty is not a score penalty that can be averaged away. Later association
must compare contour intervals/common sectors and may abstain.

### Explicit unobservability

A frame may contain many candidates while remaining physically unobservable.
Examples include homogeneous transparent phases with no stable refractive cue,
severe glare/saturation, unresolved vessel reflections or acquisition changes
that invalidate a reference. Such frames must not be converted into numeric Oil
through persistence, ranking or lifecycle context.

## Independence and lineage

Every raw descriptor carries a derivation identity such as:

- `gray/current-frame/local-normal`;
- `sobel-from-gray/current-frame`;
- `raw-material-map/current-frame`;
- `static-reference/prior-calibration`;
- `structured-background/reference-pair`; or
- `paired-polarization/current-cycle`.

Two candidates or fields sharing the same derivation contribute one lineage
family. Different source strings do not establish independence. A future
independent-support decision requires both physical contour agreement and the
configured lineage rule; hard-invalid peers cannot corroborate.

## Trace schema and bounded storage

Proposed schema identity:
`interface-observability-witness-trace-v1`.

The trace records:

- frame optical observability inputs;
- candidate identity and exact contour/sector coordinates;
- raw sector descriptors, availability and lineage;
- aggregate uncertainty/opposition;
- `NOT_EVALUATED` during extraction stage; and
- later shadow outcomes with evaluated predicates when enabled.

Do not serialize full rasters, unbounded peak lists or frame history. Reuse
frame-local prefix/profile caches. Bounds:

- current existing candidate limits;
- five sectors initially;
- three fixed photometric scales unless separately justified;
- a fixed small number of competing peaks per sector;
- one frame-local record per candidate; and
- no temporal witness history until a later association stage owns a fixed
  window.

Debug NONE performs no witness capture or serialization. Enabling BASIC/FULL
trace must not change detector output. Trace growth and runtime are measured on
all four public videos before acceptance.

## Acquisition modes

Software and acquisition are evaluated as separate axes.

### A — Current passive video

Use the existing camera/fixture. Record whether exposure, gain, white balance
and focus are fixed or automatic. This is the compatibility baseline, not the
assumed final sensing solution.

### B — Fixed passive acquisition

Lock focus, exposure, gain and white balance where hardware permits; use a stable
camera pose and vibration-resistant fixture. Compare observability and witness
stability without changing detector thresholds.

### C — Controlled diffuse illumination

Evaluate front/side/back diffuse illumination or bright-/dark-field pairs as
fixture constraints allow. Where camera response and sight-glass transmission
permit, compare explicitly identified visible and near-infrared illumination;
do not assume either spectrum separates Oil and refrigerant without measurement.
The goal is to create a reproducible interface cue, not simply increase global
brightness.

### D — Structured background / refractive displacement

Place a calibrated random-dot/grid reference behind the visible path when
mechanically possible. Measure local displacement/correlation rather than only
intensity edges. Glass/liquid optical layers require a reference/calibration
procedure; no raw displacement threshold is accepted without it.

### E — Polarization or dedicated sensor escalation

Cross-polarized or paired-polarization captures may suppress/specify reflections
when cycle timing permits. If required operating states remain unobservable,
compare a dedicated optical point switch, float/electronic oil control or other
independent sensor as validation/product sensing. This is an engineering
boundary decision, not a software fallback coordinate.

## Staged implementation and acceptance

### Stage O0 — Baseline probe (`COMPLETE`)

The public probe records current proposal recall and descriptor overlap under
bounded photometric transforms. It changes no behavior and selects no threshold.

### Stage O1 — Typed extraction (`NEXT`)

Implement the data types and trace-only measurements. Required checks:

- exact debug-on/off candidate and final output equality;
- source/crop/sector provenance and unavailable values;
- curved contour, clipped mask, glare, duplicate and competing-peak controls;
- photometric transform invariants without polarity assumptions;
- fixed resource bounds and strict finite JSON; and
- no resolver-facing field or candidate mutation.

### Stage O2 — Shadow discrimination

Create explicitly labeled positive, negative and unresolved controls. Select
operating points with declared development/holdout separation. The shadow
classifier writes only diagnostics. Required labels distinguish:

- physical interface;
- internal stripe/residue;
- vessel reflection/fitting/wall edge;
- localization mismatch near the interface;
- insufficient/unobservable evidence; and
- ambiguous competing structures.

Public truth Y alone supplies geometry, not all physical-negative labels. The
already selected private checkpoints are final domain checks, not ad hoc
threshold targets. Any broader private field calibration requires a predeclared
work-PC-only episode-level development/calibration/holdout partition with an
untouched holdout.

### Stage O3 — Independent support and association

Only after O2 passes may the typed result feed the parent design's independent
support and `SAME_INTERFACE`/`DIFFERENT_INTERFACE`/`UNRESOLVED` association.
R23's photometric-reversal positives and all current tracklet ambiguity controls
remain protected.

### Stage O4 — Handoff and phase behavior

Committed owner handoff and direction-neutral visible-interface phase remain
separate acceptance gates under the parent architecture. No O1/O2 result
implicitly authorizes them.

### Stage O5 — Target-Windows qualification

Run the current canonical Windows procedure. Measure by segment and reviewed
physical identity:

- interface proposal recall;
- supported/wrong-structure/unresolved witness rates;
- contour localization error and uncertainty calibration;
- association split/merge errors;
- numeric Oil accuracy/coverage;
- false numeric publication;
- throughput and trace/storage bounds.

No media export is required by the design. The work-PC runner can produce the
same bounded numeric/decision schema; any export remains subject to local data
policy. Human review on the work PC remains the authority for physical labels.

## Proposed code seams

The implementation should prefer these ownership boundaries:

- new `oil_interface_witness.py`: immutable semantic types and trace-only raw
  aggregation;
- existing `oil_material_path.py`: optional native contour samples only, without
  classification or ranking changes;
- existing/new frame-local measurement module: shared profile caches and sector
  descriptors;
- `phase_candidate_assembler.py`: preserve exact candidate identity while
  attaching a debug sidecar;
- `phase_frame_detection.py` / debug projector: serialize the sidecar after the
  production decision; and
- `oil_candidate_evidence.py`: do not consume the new witness until O3 is
  separately accepted.

Do not spread raw witness dictionary keys directly across authority, identity,
tracklet, lifecycle and selector modules. Later behavior must consume one typed
compatibility/association result.

## Rollback and promotion

O1/O2 are removable diagnostics. Rollback means deleting the sidecar/trace path
while leaving R22-2 decisions byte-equivalent. Promotion requires:

1. focused extraction and synthetic discrimination PASS;
2. four-video behavior equality during trace/shadow stages;
3. governance and full test suites PASS;
4. measured resource impact;
5. reviewed target-Windows evidence for the exact candidate runtime; and
6. an explicit acceptance record assigning the next detector identity.

Until all applicable gates pass, work-plan status remains `FIELD FAIL` and the
new witness has no production authority.

## History Review

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F02`, `S11-F03`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F08`, `S11-F09`, `S11-F10`.
- Prior mechanisms reviewed: multi-family current proposals, material paths and scalar medians, R22-1 candidate-centered bands, R22-2 native paths, broad texture gates, R16/R21 association, reviewed BASE/Accum checkpoints, and rejected R23 polarity-only association.
- Prior mechanisms rejected: edge/peak-only identity, scalar near/far threshold identity, source-family independence, generator votes, motion-only bootstrap, polarity vetoes, global jump/texture relaxation, private coordinate conditions, stale ID/coordinate transfer, interpolation/carry and downstream repair.
- Preserved contracts: one generic bounded detector, exact current-frame provenance, independent Oil/Foam, typed no-interface state, fail-closed ambiguity/unobservability, bounded history/resources and separate target-Windows qualification.
- Difference from prior failures: the new boundary first measures whether the optical scene is informative, retains contour geometry/uncertainty and derivation lineage, and postpones all temporal authority until interface-versus-structure discrimination is demonstrated.
- Logic-map impact: NONE — O1/O2 leave current R22-2 execution authoritative; a future O3 promotion must update the map.
- Failure-registry impact: NONE — this architecture refines the response to existing failures without claiming field repair.
