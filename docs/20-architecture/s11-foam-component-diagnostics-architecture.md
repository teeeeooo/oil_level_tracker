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

## History Review

- Logic-map nodes: `FRAME-EVIDENCE`, `FOAM-CANDIDATE`, `FOAM-EPISODE`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F04`, `S11-F06`, `S11-F09`, `S11-F10`
- Prior mechanisms reviewed: component identity leakage, Foam/Oil evidence cross-coupling, current-versus-final confusion and threshold shortcuts; the local audit finds spatially rejected components absent from the saved trace.
- Prior mechanisms rejected: no restoration of rejected Foam authority, geometry-as-identity, blanket material veto, lowering thresholds or using human coordinates in runtime.
- Preserved contracts: independent Oil/Foam owners, same-frame source provenance, fail-closed publication and unchanged temporal/sequence decisions.
- Difference from prior failures: capture computed rejected evidence in a bounded non-authoritative sidecar; no decision owner consumes it.
- Logic-map impact: UPDATED — documents the optional component sidecar and lossless debug raster route.
- Failure-registry impact: NONE — existing failure classes and guards apply; no new behavior mechanism or efficacy claim.
