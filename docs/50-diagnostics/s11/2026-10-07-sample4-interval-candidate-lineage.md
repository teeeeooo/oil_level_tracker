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
The first physically harmful stage remains unknown until candidate correspondence
is established and its admission/selection lineage is traced.

## Candidate-bound human checkpoint

The local review presents source / rejected completed line / unreviewed alternative
side by side, with all saved Oil candidates available in a read-only selector.
The default cyan alternatives are:

| Frame | Input index | Source | Source Y | Selection basis |
|---|---:|---|---:|---|
| 1200 | 4 | `oil_hypothesis:76bed74eaefae78df5f06c37` | 841 | Current-frame selected candidate |
| 1260 | 4 | `oil_hypothesis:ab9efea5ca32565368ef129b` | 839 | Current-frame selected candidate |
| 1320 | 9 | `material_path` | 844 | Agent-proposed visible-boundary alternative; not selected current Oil |

These alternatives are **unreviewed**, not inferred labels. The narrow question
is whether each cyan line follows actual Oil. This distinguishes represented-but-
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
completed output. The earliest admission/selection loss still requires tracing.
This closes the candidate-correspondence checkpoint; no repeated review is needed.

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

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-SELECTOR`, `PUBLICATION-PROVENANCE`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F09`, `S11-F10`.
- First harmful stage: UNKNOWN — current/completed disagreement is observed, the three alternative candidates are now human-confirmed Oil, but their earliest admission/selection loss is not yet established.
- Logic-map impact: NONE — existing diagnostic and sequence owners are observed without changing their control flow or authority.
- Failure-registry impact: NONE — exact candidate/source coordinates and unreviewed status are preserved; no coordinate-specific rule or failed mechanism is promoted or retired.
