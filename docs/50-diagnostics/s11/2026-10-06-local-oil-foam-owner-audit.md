# Local Oil/Foam candidate owner audit

Date: 2026-10-06. Source inspected: `f801268504e579e4c179216aeadb058670a17c48`.
Scope: read the three saved current-frame traces and source; no new detector run,
video decode, classifier, threshold or label change. `FIELD FAIL / NOT_EVALUATED`.

## Result

The six [human-reviewed paths](../../60-evidence/s11/2026-10-06-local-corpus-target-reuse.md#base-sample-human-correspondence-received)
survive proposal generation. All six are `material_path`, `kind=oil_air`,
`selected=false`, `rejected=false`, `sequence_eligible=1`. This is a proposal
type, not a physical identity certificate. Human Oil surfaces, Foam gaps and
Foam–air boundaries coexist in that proposal pool.

Oil's saved `ambiguous` decision is **not a rejection decision on these six
paths**: current Oil hypothesis projection happens before their assembly.
Completed-window Oil admission/tracklets/selection were not run by this capture.
The missing final physical discrimination therefore cannot be located in a
particular completed-window gate from these records.

Foam has a more specific observed loss: all three selected component results are
spatially rejected/ambiguous before temporal confirmation. `FoamDetectionResult`
clears its candidate and publication mask for those statuses. No `foam_front`
candidate reaches the trace. This is not solely a fresh-state persistence delay.
The saved scalar metrics do not establish whether that selected component
corresponds to either human-marked Foam boundary, or which other components lost.

## Stored observations

| Case | idx / Y | Human observation | Trace rank / score | Material texture conflict feature / penalty |
|---|---|---|---|---|
| base_sample_1:156 | 9 / 387 | Near Oil, slightly above; exact target unresolved | 1 / 0.7680 | 0.4267 / 0 |
| base_sample_1:156 | 10 / 375 | Foam–air | 3 / 0.6720 | 0.1241 / 0 |
| sample2:30 | 10 / 420 | Gap inside Foam, not Oil | 4 / 0.7726 | 0.9741 / 0 |
| sample2:30 | 12 / 590 | Actual Oil surface / target | 13 / 0.6831 | 0.7043 / 0 |
| sample4:450 | 10 / 853 | Actual Oil surface / target | 4 / 0.9011 | 0.5852 / 0 |
| sample4:450 | 11 / 845 | Foam–air | 8 / 0.7731 | 0.8691 / 0 |

Rank is only trace score ordering. In sample2 the Foam gap ranks above the Oil
surface; in sample4 the Oil surface ranks above Foam–air. Neither ordering is a
production selection or a general decision rule. Native paths are retained by
the diagnostic sidecar; scalar canonical Y does not certify every sector.

| Case | Oil status | Foam status | Selected Foam component height / width ratio | Foam score | Foam candidates in trace |
|---|---|---|---|---|---:|
| base_sample_1:156 | ambiguous | weak_rejected | 0.01351 / 0.01379 | 0.62589 | 0 |
| sample2:30 | ambiguous | ambiguous | 0.03824 / 0.02647 | 0.42204 | 0 |
| sample4:450 | ambiguous | weak_rejected | 0.39423 / 0.75000 | 0.90355 | 0 |

All three records have null raw/smoothed Oil/Foam positions, no selected Oil
hypothesis and Foam pending count 0 (required count 3). Oil reason is
`competing_boundary_artifact_or_no_interface_evidence`; Foam layer reason is
`foam_layer_not_currently_accepted`. A high sample4 Foam score does not override
the spatial status. Exact failed shape/structural predicates are not serialized.
Base and sample2 component heights are below the source's 0.075 `shape_ok`
minimum, but this alone is not a complete rejection explanation or evidence that
the tiny selected component represents the human-observed boundary.

## Source responsibility and evidence limits

1. [`CurrentFrameEvidenceOwner.observe`](../../../src/oil_tracker/adapters/vision/phase_frame_detection.py)
   runs Oil hypotheses and obtains `selected_candidate` first; then independent
   Foam evidence, motion and `assemble_phase_candidates`. The displayed material
   paths do not feed back into this current Oil hypothesis decision.
2. [`oil_material_path._candidate_from_path`](../../../src/oil_tracker/adapters/vision/oil_material_path.py)
   constructs geometric/material proposals with `OIL_AIR`, `selected=False` and
   boundary score. It does not classify Oil versus Foam–air versus Foam gap.
   [`assemble_phase_candidates`](../../../src/oil_tracker/adapters/vision/phase_candidate_assembler.py)
   adds texture/context features. The material-path texture penalty is conditional
   on white-material texture presence, false for these six rows. Their nonzero
   texture features and zero penalties are different fields, not a serialization
   contradiction or grounds to enable a blanket material veto.
3. [`OilAdmissionEvidenceOwner`](../../../src/oil_tracker/adapters/vision/oil_observation_resolver.py)
   and [`evaluate_candidate_authority`](../../../src/oil_tracker/adapters/vision/oil_candidate_authority.py)
   provide the later eligibility/authority/physical-owner route. Their result for
   these fresh single-frame proposals has not been measured. Do not replace that
   route with highest score, minimum Y, maximum Y, contrast sign or human indices.
4. [`detect_bottom_connected_foam`](../../../src/oil_tracker/adapters/vision/foam_front_detector.py)
   builds support components, evaluates appearance/shape/structure and sorts by
   status priority, score, front Y and label. It retains component records in the
   in-memory result. `FoamDetectionResult.__post_init__` sets `candidate=None` and
   zeroes `mask` for weak/ambiguous/glare statuses, retaining other evidence fields.
   [`FoamTemporalGate.evaluate`](../../../src/oil_tracker/adapters/vision/foam_temporal_gate.py)
   passes these rejected statuses through with no candidate and pending count 0.
5. `CurrentFrameResultProjector.project` can append a raw `FOAM_FRONT` candidate
   with explicit eligibility predicates, but only if `foam.candidate` exists.
   It does not convert a material-path Oil proposal into a Foam candidate.
   Thus the human-identified Foam–air paths remain visible in the Oil pool while
   this independent Foam route supplies no candidate in these captures.
6. `PhaseDebugProjector` exposes selected scalar Foam metrics and images, but not
   the complete component inventory or exact spatial predicate outcomes. Its
   non-authoritative `foam_material_support_mask` is not in the FULL writer image
   key set, and the saved `foam_mask` is the cleared publication mask. The trace
   cannot recover rejected-component geometry merely by inspecting that mask.
7. [`ObservationSequenceResolver.resolve`](../../../src/oil_tracker/adapters/vision/observation_sequence_resolver.py)
   runs Oil resolution then independent Foam episodes. The capture calls only
   `detect` with a new detector per frame; it does not exercise this composition,
   final CSV or UI. There is no evidence here of a display-only bug or final
   Oil/Foam alias rejection.

## Next bounded implementation

Extend the existing Foam diagnostic projection/trace seam to preserve rejected
component geometry and spatial predicate outcomes without restoring rejected
candidate authority. Reuse existing `FoamComponentEvidence` and selected label;
capture predicate values at their actual computation rather than recomputing a
second gate in the serializer. Retain source/ROI coordinates and all component
alternatives; store masks only through the existing debug image path with an
explicit resource bound. Keep this evidence unavailable to decision owners.

Verify debug-on/off detector equality, unchanged rejected candidate behavior,
source-coordinate joins and JSONL round-trip. Only then perform a new separately
identified capture of these same three approved frames, preserving the original
87-file capture and replies. That next capture must answer whether a human Foam
boundary lacks support, belongs to a rejected component, or loses component
selection, and identify the actual first failing predicate. No new human judgment
or Windows execution is needed to implement this trace-only step.

This does not establish a new identity mechanism. Oil target selection remains a
separate unresolved W4 question; the Foam visibility repair is evidence gathering,
not a substitute for O2 or permission to enter W5/O3. The current
[O2/O3 validation owner](../../30-validation/s11-interface-observability-witness-validation.md#o2-shadow-acceptance)
continues to govern promotion. Independent recording is future calibration/test
material, not a prerequisite for this local source/trace work.

## Reproducibility and verification

Local read-only extraction: `sample/output/s11-local-candidate-owner-audit-001/audit.py`
and `audit.json`. JSON SHA-256:
`0e30161fb40b23444477345140071d10fcd17ebe9fe999888fa8e456000c9157`.
It joins all six reply candidate indices to exact run/record/source Y, retains
unrounded saved values and records input hashes. All 87 receipt outputs are
unchanged; all 213 production Python source files match the capture's source pins.
No measurements were regenerated. Focused document links, diff and detector
governance checks cover this source investigation; no runtime behavior changed.

## Trace extension implemented and same-frame capture verified

Implementation source: `b559a11`. The [diagnostic contract](../../20-architecture/s11-foam-component-diagnostics-architecture.md)
is implemented through the existing component evaluator, debug projector and
JSONL writer. Selected/rejected status and actual gate inputs are preserved,
with a 256-component cap and an exact uint16 component-ID image. A writer
round-trip test caught normalization of IDs by the old display-image serializer;
the new explicit label-image path preserves IDs, including 256. Other images
retain their existing serialization behavior.

Focused validation: **100 tests passed** across Foam evidence, temporal gate,
phase integration, new component capture, JSONL serialization and bundle output.
Tests cover debug-on/off full detection equality on controlled scenes, rejected
candidate/mask behavior, truncation/selected retention, empty support and real
BASIC/FULL round-trip. No full-video or Windows effectiveness is claimed.

New output: `sample/output/s11-local-foam-component-capture-001/` (87 hashed
outputs plus `receipt.json`), status `CAPTURE_COMPLETE_NOT_EVALUATED`.
`capture.json` SHA-256:
`eff6fba700f55e6e339710bf5c95fd73e698626cb68892a04f3bd18971ffd1d2`.
`comparison.json` SHA-256:
`39755e3360e4f0288cde60ef06e925460861fb1004964e9ffc967fe10c52a750`.

Only the same approved three frames were decoded. All 76 Oil candidates,
positions, confidence, flags, fill state and all pre-existing trace state are
exactly equal to the prior capture. All 63 existing trace image arrays are equal.
The 12 input hashes and original 87-output receipt are unchanged. New source,
run and output identity are separate; no reply or original output was rewritten.

| Case | Components / retained | Selected component in source coordinates | Recorded rejection evidence |
|---|---|---|---|
| base_sample_1:156 | 5 / 5 | C1 box [620,476,624,480), front 476, 10 pixels | area_ok=false, height_ok=false; shape_ok=false |
| sample2:30 | 4 / 4 | C1 box [495,452,504,465), front 452, 87 pixels | shape_ok=false; strong appearance false, texture true; ambiguous branch true |
| sample4:450 | 5 / 5 | C1 box [553,848,631,889), front 848, 514 pixels | structural=true; wide-row fraction 0.5122, compactness 0.2241, fill 0.1607; weak rejection |

The new data narrows the earlier unknowns:

- Base has only five small support components, all below the user-marked Foam
  path's Y range (361–377); none geometrically supports that marked boundary.
  This does not override the user's observation or settle historical no-Foam truth.
- Sample2 also has unselected C2, box [199,340,464,543), 37,300 pixels, score
  0.7901. It passes area/height/white/texture predicates, but is neither bottom
  connected nor assigned an accepted detached phenotype, so shape_ok is false.
  Component status priority places the tiny ambiguous C1 ahead of weak C2 despite
  C2's higher score. No claim is made that C2 is physically all Foam.
- Sample4 has unselected C2, box [571,839,619,852), 335 pixels, score 0.7174,
  intersecting the previously marked boundary region. It passes area/height/white/
  texture predicates, but bottom_connected=false, material_phenotype=none and
  shape_ok=false; structural_substrate_present=true. This is an alternative
  support region, not an automatically correct Foam mask. C1's structural flag
  is the recorded algorithmic judgment, not newly established physical truth.

All 14 components are retained without truncation. Component masks are now
available to distinguish support/shape loss from selection ordering. Exact
physical attribution still requires the human review described next; no threshold
or material-identity repair follows from these flags alone.

## Human checkpoint after implementation

Component-guided views are stored outside the immutable capture in
`sample/output/s11-local-foam-component-capture-001-notes/`:
`base_sample_1-components.svg`, `sample2-components.svg`, `sample4-components.svg`
and their generator. Each juxtaposes unchanged RGB, the already-reviewed native
paths, selected component C1 and alternative C2. Colored support pixels are exact
row runs from the saved uint16 label raster; no contour interpolation or physical
classification is performed. The sample4 four-panel guide was rendered with
Quick Look and visually checked; the final view shows all four panels. This is
static guide QA, not browser UI validation.

The next requested reply is **sample4/450 C1 versus C2 material attribution**:
what the orange lower curved support and purple boundary-adjacent support contain,
including mixed regions or uncertainty. Existing cyan Oil / pink Foam–air path
judgments are not requested again. C1/C2 are diagnostic region IDs, not Oil
candidate indices. At that checkpoint the step awaited the user; the received answer is recorded
below. Windows execution is not currently needed. `FIELD FAIL`, O2 open and W5 gated remain.

## Sample4 component reply and first failing predicate established

The user answered the component guide on 2026-10-06:

> 주황 : 글래스 테두리 구조물
> 보라 : foam

This binds **orange C1 to glass rim structure** and **purple C2 to Foam**, at
sample4 frame 450, record `f000000450_fb759bff9e59`, run
`26b0eaed-5cdf-4eb8-a416-18b30936902d`, Glass
`ecb6e1ec-0259-5982-a35f-7cb1f7075af2`. Diagnostic IDs are not Oil candidate
indices. The previous cyan Oil / pink Foam–air path reply is unchanged. This is
whole-component material attribution, not exact segmentation, front Y, bottom
connectivity, temporal validity or formal O2 target truth.

The attributed reply is outside the immutable capture:
`sample/output/s11-local-foam-component-capture-001-notes/reply-001-sample4-components.json`.
SHA-256: `3d77a1fc09962170c52baf55288741342e9505aa9adc3c93ad9bb8694e0a7492`.
It retains the exact quote, complete captured C1/C2 records and hashes of the
capture, receipt, trace, label raster, displayed guide, source and prior reply.

Read-only replay of existing geometry helpers, using the saved uint16 raster and
captured statistics, confirms the following chain on source `d94054d`:

1. C1 is independently `structural=true` and weak-rejected. The human answer
   supports excluding this rim from Foam; C1 is a negative regression control.
2. C2 is **not** structurally classified: `structural=false`. Its source box is
   [571,839,619,852), while C1 is [553,848,631,889). The substrate helper uses
   bounding boxes. Their X overlap covers all 48 C2 columns; its signed vertical
   gap is **−4 pixels**. This satisfies `gap <= max_gap` (12), so the helper
   returns `structural_substrate_present=true`, `front_from_lower_edge=false`.
   Overlapping boxes do not establish physical contact or substrate identity.
3. `_detached_material_phenotype` returns provisional `detached_droplet` for C2.
   Its area 0.04536, height 0.125, width 0.46154 and fill 0.53686 meet that
   existing geometric route. This is an internal phenotype name, not a human
   claim that the region is a droplet. The detached-layer route fails its area
   and width requirements.
4. In `_component_evidence`, the droplet-retention texture (1.0) and whiteness
   (0.82090) tests pass; **only `not structural_substrate_present` fails**.
   Phenotype becomes `none`. With no bottom-connected route, `shape_ok=false`,
   so score 0.71740 (above the 0.68 strong-score threshold) still yields
   `weak_rejected`. The rejected result supplies no Foam candidate to temporal
   confirmation. The loss is spatial qualification, not the temporal gate or UI.

The replay calls the current structural-box, substrate-relation and detached
phenotype helpers only. It does not rerun segmentation, detector, video decode,
new gradients or a counterfactual production decision. Output:
`sample/output/s11-local-foam-component-capture-001-notes/sample4-causal-replay.json`,
SHA-256 `2b022efbd17e42c6265af992da4285bb9b2686cd60009c0e796fa3ccfe1acded`.
All seven read inputs and all 87 capture outputs retain their hashes. Runtime
code, thresholds and formal labels are unchanged.

This establishes a human-positive Foam region lost through the structural
substrate veto. It does **not** establish that removing the veto, changing the
sign of its gap condition, or accepting every detached region is safe. A future
mechanism must preserve the rim negative, actual structure-associated artifacts,
small/noisy supports and independent Oil/Foam authority (F06/F10). No sample ID,
coordinate or human-selected component may become a runtime exception.

## Next bounded human checkpoint — sample2 components

The already saved sample2/30 guide is ready in the same notes directory:
`sample2-components.svg`. Its four panels were rendered and visually checked;
no new detector run or video decode was needed. Orange C1 is a small support on
the right rim (source box [495,452,504,465)); purple C2 covers a large interior
region (source box [199,340,464,543)). C1 is ambiguous; C2 is weak-rejected by
shape qualification. Neither material identity is assigned here.

Ask what each displayed component contains, allowing mixed or uncertain regions.
The previous sample2 pink Oil-surface and cyan internal-Foam-gap answers remain
valid and are not requested again. This distinct component attribution determines
whether the large-region rejection supplies another physical Foam control before
choosing a general shape/substrate repair. It is not a new-frame search or an
acceptance test. After the answer, trace that component's existing predicate and
prepare two-sided local mechanism controls. No Windows execution is needed for
this checkpoint. O2 remains open and W5/O3 entry remains gated.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `FOAM-CANDIDATE`, `FOAM-EPISODE`, `SEQUENCE-COMPOSITION`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F04`, `S11-F06`, `S11-F09`, `S11-F10`
- First harmful stage: sample4 human-positive C2 loses its detached phenotype through the bounding-box structural-substrate veto, then fails spatial shape qualification before temporal confirmation. C1 is a human-confirmed rim negative. Other component identities and completed-window Oil first loss remain unmeasured.
- Logic-map impact: NONE — this follow-up attributes saved components and identifies an existing predicate; the previously documented diagnostic seam and runtime decision owners are unchanged.
- Failure-registry impact: NONE — existing identity, independent-series and current-versus-final guards apply; no new failed mechanism or threshold repair is asserted.
