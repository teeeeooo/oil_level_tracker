# Saved-sequence boundary temporal residuals — 2026-10-06

Status: MEASUREMENT_COMPLETE_NOT_EVALUATED; FIELD FAIL. This is a bounded Mac
regression diagnostic, not a Foam selector, Windows qualification or O2 acceptance.

## Source and measurement

Base source: `7bbf71480a7b0f9855f36b513b32bf10e993cd4e` plus the exact diagnostic
source hashes below. The [architecture](../../20-architecture/s11-foam-component-diagnostics-architecture.md#offline-registered-boundary-residuals)
owns support and abstention semantics. Existing translation/exposure math is
reused; optional translation reasons prevent a rejected zero-shift fallback from
being mistaken for observed stationarity. Runtime decision consumers are unchanged.

- Case `sample4:450`; record `f000000450_fb759bff9e59`;
  run `26b0eaed-5cdf-4eb8-a416-18b30936902d`;
  Glass `ecb6e1ec-0259-5982-a35f-7cb1f7075af2`.
- Anchor frame450 (15s); source origin [543,798], shape104×104.
- Saved frames390–510 inclusive (13–17s), excluding the anchor self comparison:
  120 pairs. No new decode, detector, tracker, label or recipe execution.
- 683 fixed anchor-coordinate points: all top columns of five retained components
  and all native-path columns of Oil candidates idx9–14. Radii2/4 give 163,920
  query rows. These are fixed pixel neighbourhoods, not temporal material tracks.
- Capture receipt plus87 outputs and motion-review receipt plus124 outputs:
  213 inputs preserved. No new physical Foam mask or glare mask is propagated.
- NumPy2.5.1 / OpenCV4.14.0. Detailed arrays, runner and hashes remain locally in
  `sample/output/s11-local-boundary-temporal-001/`.

## Observations and limits

All120 pairs passed the existing numerical registration gates. Current-to-anchor
shift spans dx −0.133749..0.097982 and dy −0.140829..0.558423 px; maximum reciprocal
translation error is 7.33e−08 px. Reciprocal agreement does not establish a correct
physical camera model: both estimates use the same changing ROI.

The following are medians of fully observed window-mean absolute gray differences
(raw code values), not MSE, displacement, detection rates or independent samples.
All four alternatives share pixel support; radius is a fixed inspection scale.

| Anchor group | Radius | Fully observed / all frame-queries | Direct | Exposure only | Registered | Registered + exposure |
|---|---|---|---|---|---|---|
| C1_support_top | 2 | 9360/9360 | 4.1600 | 4.9502 | 4.0500 | 4.5004 |
| C1_support_top | 4 | 9360/9360 | 4.0556 | 4.6891 | 3.8184 | 4.3569 |
| C2_support_top | 2 | 5760/5760 | 16.9600 | 17.4072 | 16.1591 | 16.6399 |
| C2_support_top | 4 | 5760/5760 | 18.6667 | 19.2160 | 17.7752 | 18.3729 |
| C4_support_top | 2 | 0/2400 | null | null | null | null |
| C4_support_top | 4 | 0/2400 | null | null | null | null |

C1 is the human-attributed lower rim; C2 is a Foam-region support with known
central circular structure involvement. C2 neighbourhood change is larger, but a
fixed structure can be surrounded or covered by changing Foam. High residual is
therefore not sufficient evidence that its saved top is a Foam–air boundary.
Exposure fitting does not uniformly reduce residuals. C4 has no fully observed
query windows; its summary is null, not zero or proof of a stationary structure.

Geometric mask validity does not exclude glare or identify visible material.
Registered interpolation, finite crop, overlapping queries and shared frames
limit interpretation. No structure geometry, exact contamination interval,
Foam front, motion-only identity or repaired public output is established.

## Human correspondence checkpoint

The prior [human clarification](2026-10-06-foam-front-alternatives.md#human-clarification--regularly-spaced-circular-structures)
identifies fixed, regularly spaced circular structures. Do not ask that identity
question again or use it to label all C2 pixels.

A local original-RGB/stored-top viewer divides all48 C2 columns into four equal
12-column segments, chosen by geometry rather than residual magnitude:
A [571,583), B [583,595), C [595,607), D [607,619). Each keeps the actual stored
per-column Y; no fitted contour or interpolation is introduced. The user is asked
which parts follow Foam–air, structure, mixed or unclear features. No answer has
been recorded at publication of this measurement; no formal truth is auto-assigned.

Local viewer: `sample/output/s11-local-boundary-temporal-001-notes/segment-review.html`.
Its manifest SHA-256 is
`302825b70fae4e3783d76023904646cdc8286e9c11018c70cedfe6caa119140d`.
Plain/path panels, toggle and browser rendering were checked. Enlargement adds no
information beyond the original104×104 pixels. Separate residual plots are
measurement illustrations, not the primary human identity display.

## Verification and provenance

Focused tests: 22 passed across `tests/unit/test_s11_boundary_temporal_probe.py`
and `tests/test_temporal_raster_evidence.py`. Synthetic controls include exposure
and translation, mask-hole interpolation, localized appearance change, numerical
failure and rejected high-response registration. They validate measurement
semantics, not material identity.

On the saved120 pairs, all240 forward/reverse translation tuples exactly match
the helper from base source. Output hashes and all213 input hashes were rechecked.
The optional diagnostic dictionary changes no production tuple or gate. No full
runtime detector replay or Windows validation is claimed.

| File | SHA-256 |
|---|---|
| `sample/output/s11-local-boundary-temporal-001/run.py` | `8d5d9d08c9c66107f8863b92aaa092ca890c4a0b8f2eed0bf21f9ca8e643c445` |
| `tests/diagnostics/s11_boundary_temporal_probe.py` | `6dcbc3c805fefd7c3eb9349d156d2e00a769530cde3bc35f3cf1fcd133b389ba` |
| `src/oil_tracker/adapters/vision/temporal_raster_evidence.py` | `c2d6a4222e06cbffb3c32b8bc6b13f6142d810b9febabfa86afd6542107b9f15` |
| local `report.json` | `60fd9986688c3043f9bc68fc475850a1c3d35f55a7a1e3f9bd26569ffdcf0088` |
| local `summary.md` | `8f2dd66c184f2c4a75db3d19db72b0cb3fa4c2024d1fd1d1b27c5ba14f1176ae` |
| local `residuals.npz` | `ad3718dcb4dcde8d9f5e50b22020efea5b78ca775b77a9289bc754d476100245` |
| local `queries.csv` | `9568a028b8fc1d93f4e48e50b86d7fb7202c17cb251f97e7e99961ddac9f3605` |
| local `receipt.json` | `fc8722173d87827665f33e0e2b7a3826165cd59dc3cab92154d86473c66fec1f` |

## Windows connection and disposition

Windows passive-review truth remains 75 candidates with10 target/65 non-target;
physical identity and uppermost-target role stay separate. This Mac experiment
investigates a Foam failure mode with its own source lineage. Neither its motion
observations nor any later A–D answer transfer labels to Windows candidates.
A future behavior candidate must separately evaluate the pinned Windows controls
and independent recording roles under the [O2 acceptance owner](../../30-validation/s11-interface-observability-witness-validation.md#o2-shadow-acceptance).
No predictions, W4-R2 entry, field PASS or W5/O3 promotion result from this probe.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `FOAM-CANDIDATE`, `FOAM-EPISODE`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F06`, `S11-F07`, `S11-F09`, `S11-F10`
- First harmful stage: exact structure-versus-Foam front attribution remains unknown; saved support-top geometry can include fixed structures and residual change does not resolve it.
- Logic-map impact: NONE — an offline probe reuses existing registration/exposure owners; optional reasons leave runtime gates and return tuples unchanged.
- Failure-registry impact: NONE — motion-only identity, component identity leakage and threshold shortcuts remain rejected; no new behavior or efficacy claim.
