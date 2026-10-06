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

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `FOAM-CANDIDATE`, `FOAM-EPISODE`, `SEQUENCE-COMPOSITION`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F04`, `S11-F06`, `S11-F09`, `S11-F10`
- First harmful stage: selected Foam spatial result becomes unavailable before temporal confirmation; exact human-component correspondence and first failed spatial predicate remain unknown. Oil proposals survive; completed-window first loss is not measured by this capture.
- Logic-map impact: NONE — existing owner/control flow verified; no runtime responsibility or behavior changed.
- Failure-registry impact: NONE — existing identity, independent-series and current-versus-final guards apply; no new failed mechanism or threshold repair is asserted.
