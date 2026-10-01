# S11 O2 unpooled O1 spatial context — local verification

Base: `eab4155c0eaae23042d93770a6f09f61fc23f679`.
Scope: existing-pixel information controls and a stored-output Windows adapter.
No private source image, new Windows execution, physical label or production change.

## Result and mechanism boundary

The known joint row/column marginal collision from the
[column-side prototype](s11-o2-lateral-context-prototype-local.md) produces distinct
unpooled O1 gradients under both polarities. The existing `_extra_channels`
operator already computes these quantities at joint X/Y; the diagnostic now
retains them before pooling. No additional gradient, path or region classifier
was implemented. This is not an independent observation or demonstrated new
information beyond the entire O1 packet. Saved pixels already contain it.

The physical hypothesis is deliberately conditional: lateral arrangement of a
transition may help describe a candidate boundary versus broken highlights or
terminal structures. Such appearance can also be shared by real interfaces,
reflections and structures. Coherence is not identity. Identical pixels, hidden
differences, inverted polarity and central-difference checkerboard aliases remain
counterexamples. Raw crop/gray panels stay alongside the gradients so the reduced
representation cannot silently replace source appearance. No score follows.

## Implemented boundary and reuse

- `s11_spatial_context_probe.measure_joint_context` reuses existing raster/point
  validation and O1's five-pixel stencil. It returns magnitude, absolute vertical
  derivative and explicit validity arrays, preserving crop/source geometry.
- `s11_joint_context_run.py` owns reading the existing spatial output directory.
  The original source runner continues to own video/bundle/label reconstruction.
  Reuse its baseline-band check and raw raster hashing; reuse O2 JSON/fingerprint
  and geometry owners. No production control-flow node changes.
- The adapter checks every source output in COMPLETE, a caller-pinned artifact,
  PNG byte/raw identities, frame/Glass/crop/points, regenerated row observations
  and original band reconstruction. Baseline MATCH is mandatory. Source inputs
  are checked again before a new COMPLETE receipt is written last.
- Output is a new directory with NPZ arrays, fixed-scale PNGs, JSON, automatic
  summary and offline HTML viewer. Two cases produce 13 hashed files plus receipt.
  The original 31 outputs plus receipt are rehashed; the previous 12 source
  video/bundle/label inputs are not reopened or claimed freshly verified.
- Recorded native and candidate-center points remain distinct. Integration
  controls caught O1's deliberate center deduplication: exactly coincident
  candidate/native centers share one native measurement. The adapter records
  `band_binding=coincident_recorded_native_center` and the actual recorded role;
  noncoincident or missing native centers are never substituted.

No source case/Glass/time/coordinate branch selects a decision or pixels.
The viewer's supplied source line is a marker, not an inferred contour. Requested
and clipped O1 intervals remain separate with availability/reasons. It never
fills their gaps or treats an interval envelope as a union. Analytic display
ranges are magnitude 0..sqrt(0.5) and vertical magnitude 0..0.5, with magenta for
invalid stencils. Quantized previews do not own numeric values; NPZ float arrays
and validity do. Stencils may cross strip edges as in O1, not invalid neighbours.

## Verification

`tests/unit/test_s11_joint_context.py` adds 24 cases covering:

- Joint marginal collision under both polarities; masked/glared differences stay
  indistinguishable; exact input preservation and nonzero source origins.
- Stencil neighbours, borders, valid zero, orientation, identical-pixel ambiguity,
  polarity invariance and checkerboard aliasing; no physical decision.
- Actual O1 native and candidate-center measurements, coincident aliases, absent
  noncoincident center failure, PNG/raw/NPZ identities and exact source bands.
- Real CLI subprocess from a Unicode non-repository directory, UTF-8/closed stdin;
  complete receipt/output hashes, old-file preservation and two frame/Glass cases.
- Byte/raster/artifact/schema/inventory/frame/baseline failures, traversal,
  dimension checks, existing/nested output and mutations during measurement or
  publication without COMPLETE. Viewer JSON is escaped before script embedding.

Focused suite (joint, lateral, row context, original source adapter, target contract):

```bash
.venv/bin/python -m pytest -q \
  tests/unit/test_s11_joint_context.py \
  tests/unit/test_s11_lateral_context_probe.py \
  tests/unit/test_s11_spatial_context_probe.py \
  tests/unit/test_s11_spatial_context_run.py \
  tests/unit/test_s11_target_aggregation_contract.py
```

**104 passed in 3.46 s** after the native/coincident-center integration repair.
Headless Chrome rendered all four panels on synthetic saved output. DOM checks
passed native-first selection, coincident-role display, scale switching, overlay
removal and full-crop switching; initial and updated screenshots were inspected.
This is local browser validation, not Windows rendering or private image review.
The document link checker passed 168 links; detector governance and whitespace
checks passed. Source artifact/report validation was tested independently of
current code hashes, so historical receipts are not rewritten after a code change.
No canonical detector efficacy suite or Windows field acceptance is claimed;
production source is unchanged. The existing source-adapter regression tests
cover the shared module import/receipt entry path.

## Next boundary

The [Windows procedure](../../40-operations/s11-o2-local-shadow-evaluation.md#unpooled-o1-spatial-context--existing-saved-outputs)
is executable with only `spatial-context-001`. It pairs the new numeric/viewer
output with one bounded appearance inspection over the already selected X strips.
No more manual UUID/hash reconciliation or source-video rerun is required.
Return the automatic summary, receipt checks and compact observations together.
Private appearance is not independently inspected locally; Windows saved data is
now the concrete dependency. Human idx0/idx20 ambiguity remains, so no forced
human verdict, relabeling, threshold or classifier promotion is requested.
FIELD FAIL / NOT_EVALUATED / EXPLORATORY_UNCALIBRATED remains in force.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `OIL-CANDIDATE`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: marginal pooling loses joint arrangement in constructed controls; the private physical identity cause is not established by restoring that arrangement.
- Prior mechanisms reviewed: existing O1 stencil/masked bands, material/path generation, row/column summaries and their collisions; source adapter, uncertainty control and prior failed profile scores.
- Prior mechanisms rejected: new gradient duplication, polarity/peak/shape-only identity, missing-as-zero interpretation, case-specific selection and manual coordinate/image-text transfer.
- Preserved contracts: source provenance, explicit masks/ambiguity, unchanged labels/history and production, independent Oil/Foam, separate Windows field qualification.
- Logic-map impact: NONE — offline diagnostics only; no detector extraction, admission, selection or publication behavior changes.
- Failure-registry impact: NONE — no physical identity or field repair is established.
