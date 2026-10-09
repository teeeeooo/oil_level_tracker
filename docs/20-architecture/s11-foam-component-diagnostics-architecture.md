# S11 rejected Foam component diagnostics

This trace-only extension closes the evidence gap identified by the
[local owner audit](../50-diagnostics/s11/2026-10-06-local-oil-foam-owner-audit.md).
It changes no threshold, proposal, selection, Foam persistence, Oil authority,
sequence composition or public validity. Detector/resolver identifiers remain
R22-3/R22; exact source hashes and the new diagnostic schema identify this addition.

## Ownership and coordinates

`CurrentFrameEvidenceOwner` forwards its existing debug capture flag to
`detect_bottom_connected_foam`. The existing `_component_evidence` records the
actual computed shape/appearance/structure predicates, values and thresholds
alongside the original branch result. No serializer recomputes a gate. Metadata
includes original connected-component label, half-open ROI bounding box, front Y,
material phenotype and selected-component status. This is spatial component
selection, not confirmed Foam episode or physical identity.

`FoamDetectionResult` carries optional frame-local diagnostics and a uint16 label
raster. Its existing rejection behavior still clears candidate/publication mask;
the diagnostic raster never restores either. Existing material support remains
separate from accepted Foam. `PhaseDebugProjector` adds source coordinates using
crop origin, plus frame/Glass identity, under `state.foam_component_diagnostics`
(schema `s11-foam-components-v1`). Neither candidate features nor resolver-facing
`PhaseDetection.debug_metrics` receives these diagnostics.

BASIC/FULL records include the metadata. FULL additionally saves
`foam_component_labels` and the already-computed `foam_material_support_mask`.
Only the label image takes an explicit uint16-preserving PNG path; all existing
image normalization semantics remain unchanged. Raster pixel IDs join the
metadata's `diagnostic_id`, not original label or Oil candidate index.

## Bounds and unavailable meaning

Capture retains at most 256 components using the exact existing component sort
key (status, descending score, front Y, label). Selected component is therefore
retained whenever one exists. Total/retained counts and truncation are explicit;
no omitted component becomes negative evidence. Label 0 means outside retained
support, including omitted components when truncated. Empty support/no valid
pixels produce count 0, null selected label, empty components and zero raster.

Metadata memory is bounded by 256 entries (one transient entry during insertion).
One extra uint16 ROI raster is allocated only with capture, plus a temporary
ROI-sized boolean during each retained-label projection; construction is bounded
by 256 raster passes. No raster/history is retained across frames. Existing
component detection/storage is unchanged. Debug disabled creates neither rows
nor label raster. No new UI setting or decision owner is introduced.

## Verification and use

Required checks: debug-on/off full detection equality on controlled scenes;
rejected-mask/candidate preservation; selected-component retention under truncation;
empty-support semantics; source/ROI joins; actual BASIC/FULL writer round-trip;
lossless label 256 preservation. A new local three-frame capture must match the
prior capture's candidates, positions, flags, confidence, state and old image
pixels while retaining new component diagnostics. Do not overwrite old receipts.

This is not O2 identity acceptance or W5/O3 entry. Geometry and predicate failure
explain what the detector computed, not which component is actual Foam. Human
correspondence can remain unresolved, and a changed classifier requires its own
plan and acceptance.

## Offline retained-support column probe

`tests/diagnostics/s11_foam_support_geometry.py` adds an offline read-only probe
of two retained raster IDs and the same ROI's effective mask. It is not imported
by production code. Existing detector helpers still own substrate decisions; this
probe records actual pixel geometry rather than implementing a replacement gate.
It validates a nonempty uint16 label raster, same-shape boolean visible mask,
distinct nonzero IDs and an integer source origin, and rejects support outside
the supplied mask. The input bound is 4,194,304 pixels; state is frame-local.

For every target-bearing column it records target/reference extents, reference
pixels within the target Y extent, nearest reference below the target's final
pixel and above its first pixel, strict intervening-row counts, and corridor
visibility. Interleaving is retained separately; a same-column outer gap is not
proof of no inner support. Source boxes are half-open; pixel coordinates and
gaps remain exact. Translation changes source coordinates only; nearest-neighbour
raster scaling scales geometric gaps, without creating an invariant classifier.

Missing reference/target IDs and missing same-column endpoints remain explicit;
null gaps are never zero. Geometric gaps across masked corridors are retained
but excluded from fully-visible summaries. No support in a retained column is
not proof of physical absence; a complete effective-mask corridor is not proof
of optical transparency. Truncation/provenance remain the saved-capture loader's
responsibility. The bounded local runner rejects truncated captures and validates
raster IDs, boxes, pixel counts and before/after input hashes.

All outputs carry NOT_EVALUATED, UNRESOLVED physical identity and unassigned
substrate/front. No winner, threshold, physical association, material segment or
scalar is produced. Optional display of each column's first support pixel is a
human-review aid, not a contour fitted between columns. No raster-top or bottom
becomes a Foam front by appearing in the diagnostic. Reuse this probe only with
explicit capture provenance; it does not decode media or reopen the detector.

Validation: same-box U-shaped references with distant versus close internal arms;
translated/scaled placements; masked corridors; lateral/missing references;
interleaving and zero gaps; crop-edge support; uint16 PNG round-trip and malformed
inputs. These are geometry controls, not synthetic physical identity labels.
The three saved Mac frames provide attributed regression context, not holdout
validation or a behavior promotion.

## Offline boundary-alternative prototype

`tests/diagnostics/s11_foam_front_alternatives.py` separates a retained material
support's upper extent from potential image edges near it. It reuses the O1
raw-gray central-difference owner, with center plus four visible neighbours,
where visible means effective and not glare. It has no production caller.

For every retained component and every occupied column, inspect fixed ±4 and
±8 saved-pixel windows around the first support pixel. Preserve every positive,
fully bracketed vertical-gradient local maximum and its half-open plateau range.
Recover exact byte-difference numerators by rounding the owner's magnitude times
510; use those integers for equality/order, avoiding floating subtraction splitting
an equal-slope plateau. Report magnitude in the existing normalized units. There
is no amplitude cutoff, tolerance, smoothing, winner, cross-column interpolation,
component ranking or scalar. The inspection radii are not acceptance thresholds
or calibrated physical scales. Weak texture/noise maxima remain in the inventory.

Each column/window records valid samples (null for unavailable), all maxima and
an appearance state: censored, no bracketed peak, single peak or multiple peaks.
A plateau touching the window/validity boundary is not fully bracketed. A complete
window with no bracketed peak does not mean no boundary outside it. Even a single
peak is not unique physical identity. Every component keeps physical identity
UNRESOLVED and a null Foam front; no unobserved or ambiguous interval is bridged.
Missing retained support cannot be recovered by this support-conditioned probe.

The dedicated saved-capture runner verifies a pinned receipt and every registered
output, validates raw-gray/original RGB equality and component IDs/counts/boxes,
rejects truncated captures, and checks preservation after reading. It only writes
a new directory outside the capture. Report/summary/local viewer have their own
receipt; exact code hashes and runtime versions are recorded. Inputs are bounded
by the existing 4,194,304-pixel probe limit and 256 retained components. The viewer
keeps original pixels next to independently toggleable support/edge marks.

Validation includes step plateaus, competing ribbon edges, equal byte slopes,
slanted/translated boundaries, masked stencils, crop/window censoring, missing
support, identical-image material/reflection counterexamples, uint16 IDs, input
mutation and real runner receipt/no-overwrite checks. These validate representation
and abstention, not Foam classification. The saved three-frame regression results
are recorded in [local boundary alternatives](../60-evidence/s11/2026-10-06-foam-front-alternatives.md).

### Optional ordered dark-gap brackets

`measure(..., include_gap_brackets=True)` adds a separate signed photometric
observation to the existing offline alternatives. The default remains byte-for-
byte equivalent as a JSON object, and no production caller is added. This
addresses the [visible narrow-space reply](../50-diagnostics/s11/2026-10-09-foam-upper-visibility-reply.json)
without selecting the component upper extreme or labelling any dark pixel air.

Use the same raw central-difference stencil and visibility as the existing
O1 measurement, retaining exact signed byte differences. Find fully bracketed
local maxima separately on positive and negative magnitudes with the existing
plateau helper and unchanged ±4/±8 inspection windows. This preserves adjacent
opposite slopes that an absolute-magnitude plateau can merge around a two-pixel
trough. Merge the two ordered peak lists; every adjacent negative/positive pair
whose complete corridor/flanks are valid and whose raw intermediate minimum is
strictly darker than both outer raw samples becomes a photometric bracket.

Retain both edge plateau intervals, the intermediate sampling interval, every
equal-minimum row, and the raw above/minimum/below values. The lower rising edge
is an unselected alternative. No amplitude/width threshold, gap-ratio cutoff,
ranking, continuity fit, interpolation or air/Foam decision is introduced.
Physical gap identity stays `UNRESOLVED` and selected Foam front stays null.
Component-conditioned windows cannot recover unsupported/censored regions.

A partly censored inspection window may contain a complete local bracket;
record the existing window censoring and never bridge an invalid corridor.
Mask/glare and resource/type bounds remain unchanged. Counterexamples with
identical pixels representing air, internal Foam texture or glass must produce
identical unresolved results. Step/ribbon direction, one-/two-pixel troughs,
ties, multiple gaps, clipping, polarity and opt-in/default equality are checked.
This is a representation tool, not a classifier or an accepted runtime change.

## Offline registered boundary residuals

`tests/diagnostics/s11_boundary_temporal_probe.py` reuses `_translation` and
`_exposure_fit` from `temporal_raster_evidence.py`; it has no production caller.
The existing translation helper accepts an optional diagnostics dictionary that
records raw finite estimates and the existing acceptance/fallback reason. All
legacy tuples and gates remain unchanged. A rejected estimate returning zero
shift must not become observed stationarity, even with a high response.

The probe takes two same-shape uint8 gray images and a geometric effective mask,
bounded to 4,194,304 pixels. Both registration directions must pass the owner's
existing gates. Reciprocal translation error is reported, not thresholded or
interpreted as camera-motion truth. Warp pixels and the mask with identical linear
interpolation; common support requires every contributing donor pixel and the
anchor pixel to be geometrically valid. Fewer than 32 geometric/common pixels or
failed registration yield unavailable residuals, not zeros. This diagnostic
support bound is not a runtime detector threshold.

Four absolute gray residual arrays use the same common support: direct,
exposure-only, registered, and registered-plus-exposure. Exposure fitting uses
that same domain. No anchor glare or Foam mask is transferred to another frame;
glare validity remains NOT_MEASURED. A fixed source-coordinate query is not a
material track. At most 4,096 integer query points and radii 0–16 produce square
window means with explicit valid/requested counts; incomplete support stays
separate. No flow, candidate winner, motion threshold or physical front is fitted.

The bounded local experiment reads only verified saved captures, includes every
retained component top column and every stored native Oil path column, and keeps
radii 2 and 4 as inspection scales. Source hashes, input preservation and unchanged
legacy helper tuples are recorded with results. Large residual can arise around
a stationary structure due to Foam/illumination/occlusion; small residual is not
structure identity. The ROI translation can absorb material movement and is not
independently verified camera motion. Correlated windows and frames are not
independent samples. Use attributed path correspondence to investigate overlap;
do not infer a circular exclusion mask from a scene-level structure statement.

Validation covers unchanged helper returns, rejected high-response fallback,
OpenCV/nonfinite failures, flat/textured images, translation plus exposure,
localized appearance changes and fully supported interpolation around mask holes.
The [local measurement](../60-evidence/s11/2026-10-06-boundary-temporal-residuals.md)
records the bounded saved-sequence result and remaining human checkpoint.

## Offline two-sided ordered appearance transport

`s11_boundary_temporal_probe.compare_split_sides` compares actual ordered BGR
strips above and below an excluded raw-gradient plateau. It reuses this offline
correspondence owner; production imports and older probe APIs stay unchanged.
The [fixed-glass reply and relative-gap result](../50-diagnostics/s11/2026-10-09-foam-gap-local-context.md#human-fixed-structure-reply-and-relative-gap-check)
motivate retaining side-specific correspondence before assigning physical roles.

The two image-formation alternatives are one common integer 2D displacement and
two independent displacements. Each has an additive BGR offset per side. Fit
with alternating local patch columns and evaluate the other columns, then swap
the split. Exact int64 moments compare mean-centered training-error numerators;
held-out moments are scaled with Python integers to avoid int64 overflow on
large valid patches. Test residuals use only the training offset. No texture is replaced by a plane,
pooled band mean or white/chromatic union. There is no speed/direction prior.

Every completely observed current placement is considered. Both complete strip
rectangles and the intervening excluded plateau must be effective and nonglare.
Outside-crop/masked anchors or no visible current rectangle are unavailable, not
negative physical evidence. Equal minima abstain. `SPLIT_BETTER` requires a unique
minimum for both sides and the common competitor in each fold, strictly smaller
held-out split error in both folds, and the same upper/lower shifts across folds.
The outperformed common competitor need not pick the same shift in both folds.
`COMMON_BETTER` and `SHARED_MATCH` require common-shift agreement; other outcomes
retain ties, fit ambiguity or fold disagreement. The adjacent columns and folds
are correlated; this is not independent validation or a confidence estimate.

Input is same-shape uint8 BGR with boolean visibility, integer half-open local
X/plateau intervals, at least three patch columns and positive integer side depth.
The inherited input bound is 4,194,304 array elements. Pre-allocation search caps
are 65,536 placements and 8,000,000 side sample values. No state survives a call.
Patch scales in a real probe must be frozen before observing its outcomes.

The returned `transport_pattern` is an appearance comparison, **not physical
Foam identity or flow**. A piecewise optical warp of fixed texture can produce
the same split advantage as two material regions. Even unique, repeatable fits
therefore leave physical identity UNRESOLVED and the front unset. A physical
challenger still requires independent side-role/opposition evidence; the joint
measurements may only establish whether this observable is useful on the fixed
controls. Never transfer a regional review to all matched patch pixels.

Focused checks cover common translation plus exposure, independently transported
sides, a fixed-pattern optical counterexample, ambiguous flat fits, masked gaps,
poisoned target placements, exact arithmetic against brute-force centering,
crop/type/shape/resource limits and unchanged inputs. Existing ordered-patch and
registered-residual tests protect the unchanged old entry points.

## Offline observed-edge fragments

`s11_contour_contact_probe.measure_edge_fragments` extends the existing saved-edge
topology owner with an exact graph of `edges AND visible`. It preserves curved
local support without the material-path generator's same-row seed/global-band
assumption. This is a diagnostic representation, not a new proposal selector or
the previously rejected connectivity-to-material identity rule. Existing local
arm/contact and clearance APIs retain their semantics.

Every observed edge pixel is a row-major vertex with source X/Y. Every pair of
8-neighbour vertices supplies one canonical undirected link. All links, including
diagonal links around thick or staircase corners, are preserved. Maximal paths
whose interior vertices have degree two become fragments. Endpoints and junctions
stop traversal; no turn is preferred at a junction. Isolated vertices, pure
cycles and paths returning to a junction are retained. Cycles repeat their
starting vertex. Each link belongs to exactly one fragment; shared junction
vertices intentionally belong to several fragments. No thinning, smoothing,
ranking, joining across a gap or scalar reduction is performed.

Coordinates are in the supplied raster's units, translated by `origin`. For a
resized diagnostic raster, the caller must retain its working-to-source mapping;
an integer origin alone does not convert reduced pixels into native source X/Y.

Per-vertex crop-edge and unavailable-neighbour flags record incomplete context.
They do not prove occlusion, a physical endpoint, or absence of material. Edges
under the visibility mask have no effect on the graph. An observed empty graph
is MEASURED with unresolved identity; no visible pixels is UNAVAILABLE. All
outputs keep physical identity UNRESOLVED, decision NOT_EVALUATED and no selected
front. Eight-neighbour raster connectivity is not subpixel contact or object
ownership, so a curved fluid-looking trace and an identical glass trace remain
indistinguishable by this representation alone.

Input is a nonempty boolean 2-D edge raster and same-shape boolean visibility,
with integer origin coordinates bounded by absolute value 2^52. Work is bounded
by 4,194,304 input pixels and 250,000 observed vertices, checked before graph
allocation. There are at most four undirected links per vertex; CSR adjacency
and visited-link traversal keep storage and traversal linear in vertices/links,
apart from deterministic link sorting. Resource overflow raises an explicit
error; it never drops shorter/weaker fragments to fit a cap. All output arrays
are independently owned and inputs are unchanged.

Fixed real controls use the previous public-video crops at native/height-200
resolution plus the saved sample4 real-front, rim and internal-texture contexts.
Read existing preprocessing edges and visibility; recomputation for public
crops must use the unchanged pinned preprocessing/settings and disclose that
these are isolated rectangular diagnostic views, not application runs. Verify
exact pixel/link reconstruction independently and inspect the resulting
fragment overlays. No exact contour recall can be inferred from regional human
judgments. A successful lossless graph may still be fragmented, dominated by
texture, or ambiguous at junctions; none is a successful physical detector.

## History Review

- Logic-map nodes: `FRAME-EVIDENCE`, `FOAM-CANDIDATE`, `FOAM-EPISODE`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F02`, `S11-F03`, `S11-F04`, `S11-F06`, `S11-F07`, `S11-F09`, `S11-F10`
- Prior mechanisms reviewed: motion-only identity and episode confirmation, component identity leakage, Foam/Oil evidence cross-coupling, current-versus-final confusion and threshold shortcuts; missing rejected components; discarded chromatic support and support-extreme fronts; the rejected strongest/lowest/nearest/smoothest rules, ordered-patch drift, shared-plane temporal region-exchange failure, signed-gap representation and relative-gap ambiguity.
- Prior mechanisms rejected: no restoration of rejected Foam authority, geometry-as-identity, blanket material veto, lowering thresholds, naive white/chromatic union, automatic upper-edge substitution, polarity-as-identity or using human coordinates in runtime.
- Preserved contracts: independent Oil/Foam owners, same-frame source provenance, fail-closed publication and unchanged temporal/sequence decisions.
- Difference from prior failures: optional ordered opposite-slope brackets and two-side transport remain diagnostic only. Observed-edge fragments now retain every visible raw edge pixel and adjacency, with junction alternatives/cycles and explicit crop/mask context, without a shared seed height or choosing a branch. This adds lossless local shape representation, not connectivity-as-identity, a joined physical contour or temporal authority. No decision owner consumes these measurements.
- Logic-map impact: NONE — offline probes have no production caller; optional registration reasons do not change tuples, thresholds or decision ownership.
- Failure-registry impact: UPDATED — F02 records the observed-edge fragment representation result and separates exact raster conservation from physical boundary recall; existing F07 appearance/correspondence counterexamples remain in force.
