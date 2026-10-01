# S11 O2 candidate identity — context semantics and sampling gap

Date: 2026-10-01. Base: `ebf858813e4de37155488a3ce6c89afa3da59974`.
Scope: source review and five additional actual-extractor counter-controls.
Production, offline scorers, packets, labels and original audit specs are unchanged.
No private image was inspected here; no Windows execution or classifier efficacy
is claimed. FIELD FAIL remains unchanged.

[W1 contract](../../20-architecture/s11-interface-observability-witness-architecture.md#w1-target-and-aggregation-contract--design-boundary)
and [controls](../../30-validation/s11-interface-observability-witness-validation.md#w1-aggregation-challenger-controls--not-yet-acceptance-evidence)
own identity semantics. [W3 Windows evidence](s11-o2-w3-target-audit-windows-run-001.md)
and [W4 local comparison](s11-o2-w4-paired-scale-windows-run-001.md) are the bounded
recall inputs. This review does not repeat their Windows experiments.

## Checked owners and actual meanings

| Evidence | Source and consumer | Meaning / limit |
|---|---|---|
| material_mean | [phase_frame_detection](../../../src/oil_tracker/adapters/vision/phase_frame_detection.py) passes foam.combined_evidence_map into [measure_oil_interfaces](../../../src/oil_tracker/adapters/vision/oil_interface_diagnostics.py); [foam_front_detector](../../../src/oil_tracker/adapters/vision/foam_front_detector.py) builds it from whiteness, texture and chromatic evidence | A band average of generic material appearance; not Oil probability or accepted Foam identity. Low/high magnitude cannot certify either side of an Oil boundary |
| static_overlap | [learn_static_artifact](../../../src/oil_tracker/adapters/vision/opencv_phase_detector.py) averages horizontal-mask persistence and thresholds at 0.75; [sample schedule](../../../src/oil_tracker/application/services/detection_processing.py) uses representative preparation times | Agreement with persistent horizontal features; neither semantic structure truth nor proof of absence of a structure. A stationary real interface can be persistent |
| normal_alignment | [_extra_channels / _band_witness](../../../src/oil_tracker/adapters/vision/oil_interface_witness.py) uses raw-gray spatial gradients with vertical approximation | Directional local edge evidence; not an estimated physical contour normal or identity certificate |
| bands / peaks / Y extent | Same witness owner retains finite sample/search ranges, per-sector geometry, peaks and availability | Evidence is local to each candidate. Candidate Y range is shape, not a human truth interval; no full region adjacency/ownership representation is added by these fields |
| W3 context medians | [context_rows / context_summary](../../../tests/diagnostics/s11_shadow_target_audit.py) preserves detailed rows but summarizes by candidate/basis over bands and scales | Descriptive summary loses side/order; detailed rows retain them. Inspect existing detail when a justified side-specific hypothesis exists; do not treat a median as physical identity |
| Production physical/authority decisions | [oil_phase_identity](../../../src/oil_tracker/adapters/vision/oil_phase_identity.py), [oil_candidate_authority](../../../src/oil_tracker/adapters/vision/oil_candidate_authority.py) combine typed phase/boundary/texture/context and gates | Existing responsibility owners. Copying their output as a training label or new independent identity cue would be circular; temporal/context provenance must be explicit |
| Packet boundary | [extract_frame](../../../tests/diagnostics/s11_interface_shadow_evaluation.py) validates raw candidate provenance and retains witness + frame identity | It does not copy every raw candidate feature, RGB crop or full production temporal state. Their absence from packet is not proof that the original bundle/video lacks them |

The raw RGB/gray/material/edge channels share image lineage. Combining their votes
does not make independent physical corroboration. W3's material-direction reversal
between reviews and overlapping static/glare values constrain an immediate global
context veto. A low static/glare value is not a positive identity signal.

No new runtime owner is needed. Existing witness extraction, review records and
W3 output/evaluation remain the reuse points. The source search covered the exact
measurement/assembly callers, material-path generator, phase identity/authority,
static preparation, packet extraction and offline consumers. No repository-wide
claim that a physical cue is impossible is made.

## New actual-extractor counterexample

The existing [target aggregation control module](../../../tests/unit/test_s11_target_aggregation_contract.py)
now adds five tests, reusing its actual O1 `measure` helper and existing scorers.
They use constructed 200x200 rasters and a fixed candidate at Y100, not private
coordinates or truth branches. Auxiliary material, static, mask and Canny inputs
are held fixed by the existing test helper to isolate the witness sampling
boundary. This is the real O1 extractor, not a complete preprocessing/Foam run;
no equality of all production-derived maps on different RGB frames is claimed:

- Step geometry continues the lower intensity region to the crop bottom.
- Returning-region geometry is identical locally but returns to the upper
  intensity at Y155 or Y175, outside every sampled candidate band and gradient
  stencil. Both contrast polarities are tested (four cases).
- Crops differ, yet the complete **candidate** witness dictionaries match exactly:
  all five center sectors, bands/context, peaks and geometry. C/A/L candidate scores
  and all profile-scale results also match. No identity decision is emitted.
- A fifth control moves the return to Y106, inside local support. The witness
  differs, showing that the extractor is sensitive within its sampling extent.

These scene names describe constructed geometry, not machine-known Oil truth.
This strengthens W1's identical-image control: distinct wider images can project
to the same candidate evidence. It isolates sampling extent, not median pooling.
It does not show that a private negative has such a return, or that a wider band
would safely classify it. A structural step and actual interface may remain
indistinguishable even in a wider image. Expanding every band can introduce other
layers and clipping; no bandwidth change or new descriptor is selected here.

## Verification

**52 tests passed in 0.89 s**, including the five new controls:

```sh
.venv/bin/python -m pytest -q \
  tests/unit/test_s11_target_aggregation_contract.py \
  tests/unit/test_oil_interface_witness.py \
  tests/unit/test_s11_identity_profile.py
```

The original W1 partial-positive/max-glare, stationary structural-step collision,
static crossing and masked-support controls remain in the same passing suite.
The tested helper also verifies diagnostic equality with/without witness capture.
This is local extraction/representation evidence, not a detector replay or field
qualification. No production algorithm or shadow score was modified. S11 governance, 146
relative document links/anchors and `git diff --check` passed.

## Decision and named next gap

A new weighted material/static/edge scalar is not justified. Neither the previous
aggregation gain nor this sampling counterexample supplies a candidate-identity
model. The open question is **which visible contextual cue supports the existing
human identity decisions and whether the saved candidate witness preserves it**.
This is narrower than requesting another video, more frames or more labels.

Before selecting one W4 identity mechanism, inspect existing review-002 and
review-003 original scene images and recorded direct-review reasons only. The
bounded inventory is review-002 idx0 (center-only positive), idx10 (partial-path
positive), idx11 (structure negative), idx20 (reflection/residue negative), and
review-003 idx10/idx15 (positive/negative native paths). These six candidates share
two already-reviewed frames; do not expand to SPL#2/3 or 780s+ footage.

Use original views first, then exact packet overlays. Separate verbatim recorded
human rationale from new agent observations. For each proposed cue name its image
extent and provenance, whether it is already measured, and a counterexample that
could share it. A candidate's proximity to the already-labeled interface, high
score, source family, phase/selection outcome or imported human label is not an
independent cue. Do not assume a bounded stripe, regional connection, meniscus or
motion without visible/recorded evidence. Missing rationale stays unknown.

[Operations](../../40-operations/s11-o2-local-shadow-evaluation.md#candidate-identity-문맥-확인--기존-두-프레임만)
contains the bounded Windows handoff. It reads existing assets, creates no labels,
and does not rerun detector/scoring. If no discriminating rationale is available,
report the named uncertainty; any subsequent direct-human question or short-window
collection is a separate W2 decision. No classifier has been implemented or accepted
in this review, and W5/O3 entry remains closed.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: in the constructed distinct-raster control, local measurement omits the remote return before scoring; the private physical-identity failure stage remains unresolved.
- Logic-map impact: NONE — only existing-extractor tests and evidence/next-action documents change; no runtime extractor, authority, selector or publication behavior changes.
- Failure-registry impact: NONE — concrete sampling/provenance limits reinforce existing no-identity-shortcut rules without claiming a new field repair.
