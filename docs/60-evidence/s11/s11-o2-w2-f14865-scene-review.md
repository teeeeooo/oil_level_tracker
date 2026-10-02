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

## Initial result and handoff (before correspondence return)

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

## Correspondence return received — 2026-10-02

Source: user-transferred Windows scene-to-candidate report. The private record
and reply JSON remain unread on this host. The reported `extract_frame()` pass
checks frame/Glass, index space, Oil inventory and scalar candidate provenance;
it does **not** validate the report's sector tables or contour interpretation.

The return supplies full Glass ID `8f94fb85-d98e-4c71-9c97-3085168be1b2` and the
same record/run/frame/time as above. It reports 23 raw Oil candidates = 23 witness
candidates, `fill_state=UNKNOWN_REVIEW`, `oil_decision_status=ambiguous`, reason
`competing_boundary_artifact_or_no_interface_evidence`, selected hypothesis=null,
`oil_tracker_action=NO_UPDATE`, and raw/smoothed Oil Y=null. These are recorded
outputs, not proof that abstention was physically correct.

Reported scalar inventory, in candidate-input order (no score/range filtering):

| idx | Source family | Source canonical Y | Rejected |
|---|---|---|---|
| 0 | oil_hypothesis | 400 | yes |
| 1 | oil_hypothesis | 417 | yes |
| 2 | oil_hypothesis | 425 | yes |
| 3 | oil_hypothesis | 670 | yes |
| 4 | oil_hypothesis | 675 | yes |
| 5 | oil_hypothesis | 701 | yes |
| 6 | oil_hypothesis | 925 | yes |
| 7 | oil_hypothesis | 949 | yes |
| 8 | oil_hypothesis | 953 | yes |
| 9 | material_path | 418.5 | no |
| 10 | material_path | 399 | no |
| 11 | material_path | 925 | no |
| 12 | material_path | 376 | no |
| 13 | distributed_sobel_path | 863 | no |
| 14 | calibrated_high_recall | 418 | no |
| 15 | calibrated_high_recall | 399 | no |
| 16 | calibrated_high_recall | 926 | no |
| 17 | calibrated_high_recall | 425 | no |
| 18 | calibrated_high_recall | 672 | yes |
| 19 | calibrated_high_recall | 904 | yes |
| 20 | phase_transition_scan | 419 | no |
| 21 | phase_transition_scan | 534 | no |
| 22 | phase_transition_scan | 907 | no |

The five negative/context observations remain unlocated and unbound. No formal
label, new image, decode, detector, score or R2 entry is reported.

### Geometry conclusions not established by this return

The report says every candidate has five identical sectors, constant Y and no
native path. Its bw8 table instead gives total band counts 16 for idx9 and 12 for
idx10/11/12, versus 20 for other candidates. With four bands per scale/center,
these do not substantiate the claimed uniform five-sector geometry. A different
counting scope could also explain the table; neither geometry claim is accepted
from these counts alone.

Local source at `5fffb2e2d4bf47776f2e251adf8fe19f2b2a78e1`:
[build_interface_witness](../../../src/oil_tracker/adapters/vision/oil_interface_witness.py)
uses `path_aligned.sectors` when present, sets `native_generator_path` and
`path_source_y`, and otherwise uses candidate-center sectors. The
[diagnostic owner](../../../src/oil_tracker/adapters/vision/oil_interface_diagnostics.py)
builds five default crop strips separately from captured native samples. Thus a
candidate family's name or default strip table cannot replace reading its actual
nested contour/sectors. This source inspection does not establish what is in the
private f14865 record or which code produced it.

Other limits requiring correction in the correspondence note:

- The added ±50/±10 px listing cutoffs were not part of the procedure. Retain all
  candidates and actual geometry; do not introduce an eligibility threshold.
- Human Y approximately 385 is not an exact anchor. No scalar candidate exactly
  at 385 does not prove proposal starvation. Even confirmed absence of a captured
  path would establish a stored-geometry limitation, not absence in the generator.
- B's approximate Y span and “slightly inclined” description do not establish
  endpoint assignments or a left-to-right 419→429 contour. Do not interpolate it.
- For the *reported default* five-strip partition, A and B each intersect sector1
  and sector4 partially, sector2 and sector3 fully, and not sector0. The report's
  “partial 0/4” shorthand is incorrect. Native candidates may use other strips;
  their overlap must be computed from their own stored X ranges.

**Disposition:** scalar inventory and unbound scene observations received;
exact geometry correspondence remains unresolved. One machine-generated nested
witness projection is the bounded next action in
[operations](../../40-operations/s11-o2-local-shadow-evaluation.md#w2--frame14865-geometry-report-reconciliation).
No repeated human judgment or new image/measurement is needed. Preserve the
original note and append corrections with field paths, then stop. Do not promote
this report to a proposal-coverage failure or identity improvement.

### Reported source hashes

- Scene reply: `1c5c31ae2d15039d996fd2fe8da14a39e205cf0be77844dbbbdfc519cf24f87`.
- Bundle debug index: `90270bac3ea98596d8c52b6594cb767e030a1d5f64e23588558d9a6cc2740861`.
- Prior version of this evidence file: `0bdc3320a660081f78daaed636cdbd9d06e42b34bfa3d88f682defcb9de9511a`.

The last hash identifies the prior document, not this appended revision. These
hashes are transferred references, not locally rehashed private files or an
independently verified before/after preservation receipt.

## Geometry reconciliation received and bounded W2 closed — 2026-10-02

Source: transferred Appendix A including the 23 candidate JSON projections.
These projections are inspectable here; private bundle bytes, images and output
files have not been independently read. The original Windows note is reported
preserved byte-for-byte with an appended correction. Scene reply/index hashes
are reported unchanged. No new measurement, decode, detector, label or human
review was performed.

**Geometry conflict resolved on transferred structured evidence:** 19 candidates
(idx0–8 and idx13–22) have `candidate_center_only`, five default crop sectors and
null path Y. Four candidates, idx9–12, have `native_generator_path`:

| idx | Canonical source Y | Exact source X sectors, in order | Native source Y, in order | Stored center objects per sector |
|---|---|---|---|---|
| 9 | 418.5 | [130,236), [236,343), [343,449), [449,555) | 420, 416, 417, 421 | 2, 2, 2, 2 |
| 10 | 399 | [130,236), [236,343), [343,449) | 399, 399, 399 | 1, 1, 1 |
| 11 | 925 | [130,236), [236,343), [343,449) | 906, 926, 925 | 2, 2, 1 |
| 12 | 376 | [130,236), [236,343), [343,449) | 394, 376, 370 | 2, 1, 2 |

Coincident native/center Y is stored once as a native center; it is not a missing
candidate-center geometry. idx10 is a captured flat path, whereas idx9/11/12
have X-varying path Y. Absence of native capture for the other 19 candidates is
not proof of missed proposals or a generator defect. Null `curve_summary` and
`localization_uncertainty_px` remain unavailable derived fields, not contradictions.

### Local reconciliation of the supplied appendix

No additional Windows request is needed for the following corrections:

- idx9's path Y420 and Y421 fall within B's approximate Y419–429 span over
  X intersections 96 and 18 pixels. Y416/417 are 3/2 pixels **above** its smaller
  Y bound, because source Y increases downward. This is numerical overlap with
  a rough region, not an exact contour intersection or first acquisition of a
  path: the path already existed and the report has now recovered it.
- idx12's Y394 and Y376 are equally distant (9 px) on opposite sides of A's
  approximate Y385; Y370 is 15 px above. The sequence moves upward as X increases,
  not downward. Y394 is not closer than canonical Y376. No nearest winner or
  proposal miss follows from these offsets.
- idx9 alone reaches X555; idx10–12 stop at X449. Do not give all native candidates
  the same coverage. Approximate A/B endpoints do not become exact truth.
- Native-only and all-stored-center band inventories are different scopes.
  idx9's 16/16 native-only and 32/32 all-center counts can both be valid. The
  latter is not additional independent support or a replacement native score.

Counting `true` values in the supplied A10 bw8 arrays gives:

| idx | Native stored centers | Additional candidate-center objects | All stored centers |
|---|---|---|---|
| 9 | 16/16 | 16/16 | 32/32 |
| 10 | 12/12 | none (coincident) | 12/12 |
| 11 | 8/12 | 6/8 | **14/20** |
| 12 | 12/12 | 8/8 | 20/20 |

idx11 native sectors have 2,4,2 available bands; its two additional center
objects have 2,4. Thus A5's 15/20 and the prior 9/12 do not match A10. Other
A5/A10 discrepancies are idx6 and idx16 (**4/20**, not 6/20), and idx19 and idx22
(**6/20**, not 10/20). Counts were recomputed locally from a compact transcription
of the supplied boolean arrays; this does not verify the private output file.
The supplied structured arrays are the basis of these arithmetic corrections;
no measured band or label is altered. These count differences do not reopen
geometry reconciliation or establish identity/support quality.

### Evidence-document hash difference resolved locally

Git file bytes give:

| Repository revision | SHA-256 of this evidence document at that revision |
|---|---|
| `5fffb2e` | `0bdc3320a660081f78daaed636cdbd9d06e42b34bfa3d88f682defcb9de9511a` |
| `8c4d918` | `702f4b6772bb0b0cd33383c94db49387221cdb196268a92c75f8cc7fe5d057fb` |

These match the two reported hashes. Commit `8c4d918` appended the earlier
correspondence intake and changed its historical heading. This is an identified
document-version change, not an unresolved input-record conflict. The current
appendix changes the document again; neither historical hash describes this
new revision. No private source-file hash conclusion is implied.

### Disposition and next-entry condition

**Bounded W2 scene review and stored-geometry correspondence COMPLETE on
transferred evidence; no identity promotion.** The original all-center-only
claim is withdrawn. Both scene alternatives remain unresolved, negative/context
observations remain unbound, and detector ambiguous/NO_UPDATE output is preserved.
There is no new independently justified positive/negative identity contrast.

Close this Windows handoff. No further extraction, recount request, image,
relabeling or forced human choice is scheduled. W4-R2 entry remains unmet:
a conditional challenger needs a distinct input-based discriminator and justified
opposing controls, as specified in the
[continuation plan](../../50-diagnostics/s11/s11-w4-progress-audit-and-continuation-plan-2026-10-01-ba1bd6a.md#w4-r2--재사용형-conditional-identity-challenger의-사전-명세).
This scene supplies geometry and an unresolved case, not those controls. Reopen
implementation/collection only with a concrete mechanism/control or acquisition
decision addressing that gap; do not automatically review another nearby frame.
R1 remains closed without promotion; O2 open, W5/O3 gated, SPL#2/3 deferred,
FIELD FAIL / NOT_EVALUATED unchanged. This is not a general impossibility claim.

Local verification: current-source geometry semantics, supplied-boolean arithmetic,
Git historical file hashes, documentation links, governance and diff checks.
Private file preservation and human observations remain attributed evidence.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: physical identity remains unresolved in the human scene observation; no candidate-generation or downstream detector failure is newly established.
- Logic-map impact: NONE — attributed evidence and read-only correspondence handoff only; no scoring, labels or runtime change.
- Failure-registry impact: NONE — no new physical mechanism or field repair claimed; approximate geometry and alternative explanations stay explicit.
