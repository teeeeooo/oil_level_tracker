# S11 R22-2 Native Path Diagnostics

R22-2 extends the [R22-1 measurement contract](s11-r22-1-interface-diagnostics-architecture.md)
with the geometry already used to generate material-path candidates. It does
not implement the [behavioral repair proposal](s11-physical-interface-evidence-repair-design.md)
or satisfy its [acceptance gates](../30-validation/s11-physical-interface-evidence-repair-validation.md).

## Identity and unchanged authority

- Detector/package: `opencv-phase-detector-r22-2-interface-path-diagnostics-v1`.
- Resolver: `r22-oil-ownership-evidence-replacement-v1`, intentionally unchanged.
- `state.oil_interface_diagnostics.schema_version`: `r22-2-interface-path-diagnostics-v1`.

Candidate generation, ranking, features, penalties, coordinates, eligibility,
tracklet association, phase ownership, selection, Foam and publication decisions
retain R22 behavior. No measured field grants authority or changes a threshold.
Tracking and events must match the R22-1 comparison except run identity.

## Reuse and ownership

`oil_material_path.py` already computes per-sector paths for `material_path`
and `raster_material_path`; the scalar candidate previously discarded their
geometry. R22-2 captures those exact selected samples when debug is requested.
It does not introduce a new path finder, rerun selection, reconstruct a contour
from diagnostic peaks, or reuse the separate spatial-fallback path as a substitute.

`MaterialPathSample` retains original sector ID, local X bounds/Y, generator
strength, signed contrast, winning contrast channel and scale. Missing sectors
are not renumbered. `MaterialPathEvidence.diagnostic_samples` is empty without
capture. Dynamic-programming ranking and tie breaks do not consult the added
sample indices. Channel provenance distinguishes blurred-gray dynamic-range
contrast from raw combined material contrast; Sobel contributes to generator
strength in either case. These values are not interchangeable with the later
unblurred gray measurements.

The generator's optional collector keys samples by original candidate identity.
`assemble_phase_candidates` transfers each retained candidate's sidecar across
its existing enrichment, then indexes it by the assembled input position.
`MaterialPathDiagnostic` records source and exact Y for a defensive join check.
Subsequent signature/template enrichment preserves count, order, source and Y.
The existing final candidate input index is therefore the trace join, not the
score-sorted trace array position or sequence witness offset.

`CurrentFrameEvidenceOwner` holds this frame-local sidecar. `PhaseDebugProjector`
passes it to the existing `measure_oil_interfaces` after detection. Neither the
sidecar nor its measurements enter `PhaseDetection` candidates, features,
resolver-facing metrics, or temporal history. Trace NONE skips capture and
measurement; BASIC and FULL include the payload on records their existing
capture policy retains. There is no new GUI setting.

## Two measurement centers, explicit spatial support

All R22-1 candidate-centered fields retain their values and meaning. Every Oil
diagnostic candidate also has `path_aligned`:

- Native material/raster-material candidates use their own captured samples.
- Other families report `unavailable / no_captured_native_path`. They never
  borrow a nearby material candidate's geometry.
- Missing samples, source/Y mismatch, invalid geometry or unavailable pixels
  have explicit reasons. Unavailable measurements are null, not zero.

Generator sectors use the effective mask's horizontal extent and rounded
fifths. R22-1 diagnostic sectors use the whole crop and integer-divided fifths.
Thus sector numbers alone do not establish equal pixel support. Each native
sample reports its actual source X range and exact local/source Y. The shared
band/gradient helper measures two centers on that *same native X range*:

1. The native sample Y, with `peak_offset_from_path_px`.
2. `candidate_center_on_same_sector`, with the original fractional candidate Y,
   the existing rounded sampling center, and `peak_offset_from_candidate_px`.

The existing half-open near/far bands, mask/glare rules, finite-value checks,
minimum pixel/fraction bounds and peak tie break are reused. Edge exclusion is
relative to the native path row, not a certified physical edge. A measured peak
does not recenter the path, the candidate or any band. Peak availability may
differ from paired-band availability because their pixel requirements differ.

The output names the generator gray channel (`pre.blurred`), measurement gray
channel (`pre.gray / 255`), generator strength formula and shared derivation.
`shared_derivation` describes generator inputs; the parent `material_channel`
describes the diagnostic raw-material measurement for both generator families.
Raw combined material is not final Foam authority. Candidate and path views
share the same frame/raster; source names and two nearby paths do not establish
independent support. `classification` and `independent_support` remain
`not_evaluated`.

## Bounds and acceptance

At most five native samples per retained path use the existing generator's
candidate limits. Prefix/gradient profiles are cached within one measurement
call by actual X extent: five old sectors plus at most five shared native
extents. Construction remains O(crop pixels) with O(crop height) prefix storage
per fixed extent/channel. Serialized native measurements are bounded by the
existing path candidate count. No raster or history is retained after the frame.

Required local checks are exact capture-on/off candidate/output equality,
preserved R22-1 fields, explicit geometry/channel provenance, non-borrowing,
unavailable/masked controls, source/crop joins and real BASIC/FULL serialization.
Four public same-runtime replays compare all tracking/event CSV columns except
`run_id`, raw candidates, completed sequence and old diagnostic fields. The
current characterization golden is preserved. Completed results belong in the
[evidence record](../60-evidence/s11/s11-r22-2-interface-path-diagnostics.md).

Windows first follows the [single-candidate procedure](../40-operations/s11-r22-2-windows-interface-measurement.md).
Native geometry may still follow reflection or have an inaccurate edge center.
No local test or diagnostic equality establishes Windows detection accuracy.

## History Review

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F06`, `S11-F09`, `S11-F10`.
- Prior mechanisms reviewed: R22 false-to-real association and texture peer exclusion; R22-1 true/false raster controls and Windows candidate-center sensitivity; existing material and spatial-fallback generators and their callers.
- Prior mechanisms rejected: a third path finder, peak-based recentering, source-family independence, scalar contrast classification, relaxed authority/ownership gates, and private-coordinate control flow.
- Preserved contracts: unchanged candidate/sequence/publication decisions, exact same-frame provenance, independent Oil/Foam ownership, bounded fail-closed diagnostics, and no coordinate carry.
- Difference from prior failures: capture the existing generator's native geometry and shared derivation solely for trace; compare centers on identical X support without promoting either to physical identity.
- Logic-map impact: UPDATED — R22-2 diagnostic identity, frame-local capture and native-sector measurement route are documented.
- Failure-registry impact: NONE — new observability does not claim a new causal failure or a field repair.
