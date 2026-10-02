# S11 W2 — saved BASE frame 14865 scene review

Date of intake: 2026-10-02. Local baseline: `4415d3df2ad26cc75aece93888f6bc3406a6eb21`.
Source: user-transferred Windows preparation and direct-human-review report.
Private original image, reply JSON and index were not inspected on this host.
This is scene evidence, not a new candidate label or shadow evaluation result.

## Reported exact selection and image binding

| Field | Transferred value |
|---|---|
| Record | `f000014865_0c5e1375725c` |
| Source frame / timestamp | 14865 / 619.994375 s |
| Glass | BASE; only abbreviated `8f94fb85..` supplied in this return |
| Run | `a24c8fe9-3166-4c17-b69f-d9b4458711bd` |
| Selection | First of 20 eligible records by abs(source_time-620), frame_index, record_id |
| Crop | origin (0,211), width 578, height 773, resize=false |
| Original ROI SHA-256 | `e335338b959c5440614ea9f9309593e848108a5c6f270722b8ac5007f4bb4614` (reported, not locally rehashed) |
| Presentation | Original unannotated view and separate grid overlay shown |

Timestamp 619.994375 is arithmetically consistent with 14865 at rational FPS
24000/1001. Dividing by the rounded display value 23.976 instead gives
619.994994995; the transfer's “exactly equal using 23.976” is not literal exact
arithmetic. Retain the indexed timestamp, not a replacement derived from rounded
FPS. This arithmetic check does not independently verify media metadata or decode.

## Human scene answer, approximate geometry

| Observed boundary | ROI coordinates | Source coordinates | Qualification |
|---|---|---|---|
| Boundary 1 | X approximately 178–483, Y approximately 174 | X approximately 178–483, Y approximately 385 | Horizontal; could be the interface |
| Boundary 2 | X approximately 140–467, Y approximately 208–218 | X approximately 140–467, Y approximately 419–429 | Slightly inclined; could also be the interface |

The human reported both plausible and visually difficult to distinguish. This
establishes an **unresolved alternative-boundary scene**, not two independently
confirmed Oil interfaces, a preferred winner, exact contour or scalar truth.
Ranges and single Y estimates remain approximate; do not invent x/y interpolation,
a tolerance, per-sector judgments or a shared entity ID from them.

Other scene observations were attributed to the human in the transferred report:
left crescent reflection; lower-right yellow-white rectangular reflection;
vertical condensation/residue streaks; a right-edge ruler/structure. Upper-rim
white spots were described as possible Foam/foreign material, so that interpretation
remains tentative, not a confirmed Foam label or a change to the canonical BASE
no-Foam interval truth. These observations have no exact coordinates or candidate
bindings in the supplied summary. They are potential scene-level negative/context
examples, not evidence that any particular Oil candidate tracks them.

Private reply reported at `joint-context-001-notes/w2-f14865-scene-review-reply-001.json`,
3,556 bytes, schema `w2-scene-review-v1`, visibility=visible,
basis=direct_human_review. Treat this custom JSON as an attributed source note,
not a second authoritative label format or an importable v2 review transaction.
The existing [review-record owner](../../../tests/diagnostics/s11_review_records.py)
requires exact case/packet/witness bindings and revision checks for formal labels.
No label transaction or new packet is reported here.

## Result and bounded next action

**One-frame W2 preparation and human scene review COMPLETE on transferred evidence.**
The requested new frame was actually reviewed; its main boundary identity remains
unresolved. R1 stays CLOSED_WITHOUT_PROMOTION and R2 has no justified identity rule.
Shared approximate Y with f14386 does not establish a persistent object, motion,
tracklet or a correspondence of candidate indices across frames.

The next useful step is a **read-only correspondence of this scene note to all
stored Oil candidates at this exact record**, using the original native geometry
and original scalar centers separately. It asks whether candidate proposals cover
either/both described alternatives, not which alternative is true. It also records
whether any negative scene observations have an existing exact spatial binding;
missing binding stays missing. This can distinguish missing proposal coverage from
unresolved identity without more image collection or a new score.

[Operations](../../40-operations/s11-o2-local-shadow-evaluation.md#w2--frame14865-scene-to-candidate-correspondence)
uses existing storage and witness extraction owners without `prepare`/`record` or
new labels. The source raw/witness candidate index space must be checked, not
inferred from score-sorted lists or old review indices. Do not force a nearest
candidate match to an approximate human coordinate. If witness or exact provenance
is unavailable, report that limitation and stop. No additional human answer is
requested before this correspondence; any subsequent label step must preserve the
human's uncertainty rather than request a forced winner.

## Verification and limits

Read existing `extract_frame()` provenance checks and the review-record transaction
contract. Checked the two coordinate translations (+211) and the rational-FPS
arithmetic locally. File existence/hash preservation and the reported presentation
remain transferred evidence. No runtime changes, tests, detector execution,
classifier/threshold fitting or physical image validation were performed locally.
Document links, governance and diff whitespace are the relevant checks.
Acceptance remains [O2 shadow acceptance](../../30-validation/s11-interface-observability-witness-validation.md#o2-shadow-acceptance);
FIELD FAIL / NOT_EVALUATED, existing labels and independent-recording constraints
are preserved. This same-SPL#1 scene is development evidence, not holdout success.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: physical identity remains unresolved in the human scene observation; no candidate-generation or downstream detector failure is newly established.
- Logic-map impact: NONE — attributed evidence and read-only correspondence handoff only; no scoring, labels or runtime change.
- Failure-registry impact: NONE — no new physical mechanism or field repair claimed; approximate geometry and alternative explanations stay explicit.
