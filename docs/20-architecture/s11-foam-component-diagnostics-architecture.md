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

## History Review

- Logic-map nodes: `FRAME-EVIDENCE`, `FOAM-CANDIDATE`, `FOAM-EPISODE`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F04`, `S11-F06`, `S11-F09`, `S11-F10`
- Prior mechanisms reviewed: component identity leakage, Foam/Oil evidence cross-coupling, current-versus-final confusion and threshold shortcuts; the local audit finds spatially rejected components absent from the saved trace.
- Prior mechanisms rejected: no restoration of rejected Foam authority, geometry-as-identity, blanket material veto, lowering thresholds or using human coordinates in runtime.
- Preserved contracts: independent Oil/Foam owners, same-frame source provenance, fail-closed publication and unchanged temporal/sequence decisions.
- Difference from prior failures: capture computed rejected evidence in a bounded non-authoritative sidecar; no decision owner consumes it.
- Logic-map impact: NONE — the offline saved-raster probe has no production caller; previously documented component capture and decision ownership remain unchanged.
- Failure-registry impact: NONE — existing failure classes and guards apply; no new behavior mechanism or efficacy claim.
