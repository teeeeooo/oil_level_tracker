# sample4 interval candidate correspondence — 2026-10-07

## Scope and observed result

Base `ccfb6fa1421fed9e5701a61bfa652dcb315e487d`. This is a bounded,
read-only investigation of the [human-reviewed interval](../../60-evidence/s11/2026-10-07-source-report-interval-review.md#human-reply-received--2026-10-07).
The [Work Plan](../../00-project/work-plan.md) owns next execution and acceptance.
No production code, scores, selection, recipe or formal truth changed.

The existing official sample4 session ran from 0–56 seconds at 2 FPS with UNKNOWN
prior. Existing debug output was captured at only the seven reviewed frames;
all frames still passed through the real detector and completed-window resolver.
The completed tracking fingerprint matches the preceding official replay:
`e447626b5717fb5d92f4a895be783658c1b4694eb80eb6f380d032e655a35db1`.

All Y values below are source-image coordinates, not calibrated scalar truth.
“Current” is the frame-stage observation before completed-window resolution.
The user's judgments apply to the displayed completed observations only.

| Frame / seconds | Oil candidates | Current Y | Completed Y | Human judgment of completed observation |
|---|---:|---:|---:|---|
| 1140 / 38 | 23 | 844 | 844 | Correct |
| 1200 / 40 | 21 | 841 | 865.5 | Incorrect |
| 1260 / 42 | 22 | 839 | 868 | Incorrect |
| 1275 / 42.5 | 20 | unavailable | 835 | Correct |
| 1320 / 44 | 24 | unavailable | 822 | Incorrect |
| 1485 / 49.5 | 21 | unavailable | 836 | Correct |
| 1560 / 52 | 22 | 832 | 833 | Correct |

The capture preserves 153 Oil candidates. At 40 and 42 seconds, the current and
completed choices differ. This alone does not prove the current choice is Oil.
Nor does it justify bypassing sequence processing: the confirmed correct 42.5
and 49.5-second completed observations have no current-frame scalar observation.
At capture preparation, the first physically harmful stage was unknown pending
correspondence and admission tracing. The returned judgment and trace follow below.

## Candidate-bound human checkpoint

The local review presents source / rejected completed line / unreviewed alternative
side by side, with all saved Oil candidates available in a read-only selector.
The default cyan alternatives are:

| Frame | Input index | Source | Source Y | Selection basis |
|---|---:|---|---:|---|
| 1200 | 4 | `oil_hypothesis:76bed74eaefae78df5f06c37` | 841 | Current-frame selected candidate |
| 1260 | 4 | `oil_hypothesis:ab9efea5ca32565368ef129b` | 839 | Current-frame selected candidate |
| 1320 | 9 | `material_path` | 844 | Agent-proposed visible-boundary alternative; not selected current Oil |

At preparation these alternatives were **unreviewed**, not inferred labels. The
question asked whether each cyan line follows actual Oil. This distinguishes represented-but-
displaced Oil from missing/incorrect candidate support without asking the user to
repeat their judgment of the completed observations. No exact pixel annotation,
Foam attribution or judgment of the four confirmed positives is requested.

This capture does not implement A1's three support/pair/score-lineage gaps and
does not authorize an A2 behavior change before A1 lossless verification. Candidate
correspondence, scalar eligibility and physical identity remain separate.

## Human correspondence received — 2026-10-07

The user replied: “하늘색은 실제 oil을 따라감”. The preceding question named
all three default cyan alternatives at 40/42/44 seconds. The [bound reply](2026-10-07-sample4-candidate-human-reply.json)
therefore confirms their Oil correspondence without assigning exact pixel truth
or extending it to nearby candidate indices. The original review manifest is
unchanged. Correct Oil is represented at each of these frames but displaced in
completed output. The admission trace below establishes their first eligibility loss.
This closes the candidate-correspondence checkpoint; no repeated review is needed.

## Admission lineage after A1

[A1 verification](../../60-evidence/s11/2026-10-07-a1-measurement-lineage.md) preserves
final-code equality at all seven observations. The read-only admission helper
wraps the real `OilAdmissionEvidenceOwner.prepare`/`evaluate_candidate_authority`
calls, checks all 2,549 finite Oil candidates in exact ordered input identity, and
returns each original result unchanged. The full official 113-frame tracking
fingerprint remains equal. The receipt retains exact contexts and evidence.

| Confirmed candidate | Earliest observed eligibility loss | Executed reason / failed gate |
|---|---|---|
| f1200 idx4, Y841 | `OIL-AUTHORITY`, CANDIDATE_ONLY | `foam_material_identity`; `independent_from_foam_material_track` |
| f1260 idx4, Y839 | `OIL-AUTHORITY`, CANDIDATE_ONLY | `insufficient_authority`; `boundary_advantage`, `ordered_lower_cross_representation` |
| f1320 idx9, Y844 | `OIL-AUTHORITY`, CANDIDATE_ONLY | `material_layer_terminal` |

At 40 s the inferred Foam/material row is Y840 and identity support is 0.8;
phase identity is OPPOSED_MATERIAL despite representation support 0.9313.
At 42 s boundary/artifact values are 0.4493/0.6930 and representation support is
zero. At 44 s the material path has boundary 0.976 but terminal/topology values
are 1 and phase identity is CONTINUATION_ONLY. These are executed model values,
not human-confirmed Foam/material labels. Later retention/selection cannot grant
these candidates independent authority. No new threshold or family bypass follows.

Correct Oil is represented, but these rules prevent its completed selection.
The optical cause of the misleading evidence remains unresolved. The separate
pink-line review asked only the physical nature of the already rejected completed
observations (Y865.5/868/822). Their wrong-target status does not establish
`non_interface`; cyan correspondence and the four positives need no repeat review.
The review HTML, source-pixel pins and original question are retained in the A1
receipt/local artifacts. No formal scalar, contour or Foam truth is inferred.

## Pink-observation reply and A2 control preflight

The user returned the physical-subtype review:

| Completed observation | Verbatim reply | Retained interpretation |
|---|---|---|
| 40 s / f1200 / Y865.5 | 영상으로 판별 불가 | Physical subtype unresolved |
| 42 s / f1260 / Y868 | 하단 테두리를 따라가는듯 | Tentative lower-rim attribution |
| 44 s / f1320 / Y822 | 영상의 노이즈 선으로 보임 | Tentative image-noise-line attribution |

The [bound reply](2026-10-07-sample4-pink-human-reply.json) retains uncertainty,
review/source hashes and the executed selected candidate. The three observations
remain rejected Oil targets from the earlier definite correctness judgment;
none becomes a confirmed `non_interface` label. Cyan Oil correspondence and the
four correct completed observations remain protected. This review is closed;
40 s does not require a repeated identification request.

A fresh read-only replay at `df3a99b` checks all 2,549 authority calls in the
113-frame official window. It preserves the completed tracking fingerprint and
all production source hashes. The [control manifest](2026-10-07-sample4-a2-control-preflight.json)
binds ten distinct candidates: seven confirmed Oil correspondences and three
rejected targets. No per-pixel scalar tolerance, native-sector truth, new data
split or predictor accuracy is inferred. All remain exposed regression controls.
The helper, full calls and manifest are retained in
`sample/output/s11-a2-readout-preflight-20261007-001/`.

The selected source is taken from the executed sequence decision witness, then
checked against input index/source/Y and completed raw Y. In particular f1320
selects idx21 `phase_transition_scan`, not the same-Y idx2 Oil hypothesis.

| Seconds | Selected source / input index | Authority route | Reviewed target role |
|---|---|---|---|
| 38 | material_path / 9 | ANCHOR, corroborated_material_path | Correct |
| 40 | material_path / 10 | ANCHOR, ordered_lower_interface | Incorrect; subtype unresolved |
| 42 | calibrated_high_recall / 15 | ANCHOR, ordered_lower_interface | Incorrect; tentative rim |
| 42.5 | calibrated_high_recall / 12 | CONTINUATION | Correct |
| 44 | phase_transition_scan / 21 | CONTINUATION | Incorrect; tentative noise |
| 49.5 | phase_transition_scan / 19 | ANCHOR, ordered_lower_interface | Correct |
| 52 | phase_transition_scan / 20 | CONTINUATION | Correct |

Three shortcuts are contradicted by these exact controls before implementing a
new readout:

- Each selected source family occurs on both a correct and an incorrect target.
  Family rejection/privilege cannot separate them.
- A blanket continuation veto also removes the correct 42.5/52 s observations;
  ordered-lower rejection also removes correct 49.5 s. Existing authority tier
  or route name is not a physical classifier.
- The correct 42.5/49.5 s and incorrect 44 s observations share
  `oil-tracklet:000084:0017`. Its motion-confirmation witness is the same; a
  track-wide positive or negative label would overwrite one of these judgments.

This supports a **candidate-specific joint readout before authority**, preserving
actual spatial support, shared score dependencies, optical/texture opposition,
and explicit unresolved output. It does not identify a validated decision rule.
The audit's next finite challenger still needs one frozen input schema/readout/
operating-point policy and positive/negative/collision controls. Reject family,
whole-track, universal sign or broad-texture shortcuts rather than testing a
series of cutoffs against these ten reviewed Y values. Existing W3 owns later
prediction evaluation; this manifest is a binding/preflight inventory, not a
parallel evaluator, A2 predictor or efficacy result.

## Reproducibility and limits

The [manifest](2026-10-07-sample4-interval-candidate-manifest.json) preserves the
capture manifest, review selections, source/input hashes and artifact hashes.
Full JSON debug state, original ROI/mask/preprocessing rasters, capture helper,
comparison PNGs and HTML remain under
`sample/output/s11-sample4-interval-candidates-20261007-001/`.
The browser review is `review.html` in that directory. Its candidate selector was
exercised and restored to the pinned default before delivery.

All 213 captured source hashes and all 12 preceding official-run input pins were
rechecked unchanged. All capture/review artifact hashes were verified. The same
source and recipe are used; sample4 remains exposed regression material. No
independent calibration, holdout, A0Q stability, O2 acceptance or Windows field
qualification follows from this capture.

## Detector Governance

- Logic-map nodes: `OIL-AUTHORITY`, `OIL-CANDIDATE`, `OIL-TRACKLET`, `OIL-SELECTOR`, `PUBLICATION-PROVENANCE`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F01`, `S11-F03`, `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: `OIL-AUTHORITY` — all three confirmed candidates lose selection eligibility at executed authority rules; optical root cause and a safe discriminating correction remain unresolved.
- Logic-map impact: NONE — the previously adopted A1 route and existing authority/tracklet/publication owners are observed without changing source, decision ownership or authority.
- Failure-registry impact: NONE — exact candidate/source coordinates and attributed review status are preserved; no coordinate-specific rule or failed mechanism is promoted or retired.
