# Step-7 Windows receipt — 2026-10-23

**Status: PARTIAL RECEIPT.** The reply to the
[step-7 combined request](../../40-operations/s11-current-windows-field-qualification.md#step-7-combined-request)
came back through the user and was relayed by OCR. Most tables arrived as
agent summaries, not the verbatim rows requested. Several pre-registered items
are missing, including the gate's SPL#4 comparison, so the gate is not judged
here. The missing items are in the
[step-7 follow-up request](../../40-operations/s11-current-windows-field-qualification.md#step-7-follow-up-request).
Nothing is tuned or changed; top-exit and the gate stay default OFF; FIELD
FAIL / O2 OPEN and review-006 pending are unchanged.

## Runs and identity

| Run | Resolver suffix | Bundle (Windows) |
|---|---|---|
| SPL4_B_ref | `+top-exit-full-v3` | `oil_level_analysis_SPL4_B_ref_20261023_150316` |
| SPL4_B_gate | `+top-exit-full-v3+fill-owner-contest-v1` | `oil_level_analysis_SPL4_B_gate_20261023_150740` |
| SPL1_B_ref | `+top-exit-full-v3` | `oil_level_analysis_SPL1_B_ref_20261023_152751` |
| SPL1_B_gate | `+top-exit-full-v3+fill-owner-contest-v1` | `oil_level_analysis_SPL1_B_gate_20261023_155502` |

- **Versions (G-3):** the full resolver versions are
  `r22-oil-ownership-evidence-replacement-v1+initial-full-observation-v2` plus
  the suffix above. This is the expected set.
- **Runs:** all four exited 0 and wrote a debug trace.
- **Glasses:** the FLB-2 output files name the Glass IDs. They are SPL#1 BASE
  `8f94fb05…` and Accum `8fb6ebc7…`, and SPL#4 BASE `9c74a762…` and Accum
  `cfef5bad…`, the same Glasses as the earlier receipts.
- **Records:** 601 per Glass on SPL#1 and 181 per Glass on SPL#4, as expected.
- **Not relayed:**
  - the run IDs;
  - the six file SHA-256 values;
  - the video identity;
  - the frame correspondence.
- **Source ZIP SHA-256:** relayed with 65 hex characters (an OCR slip).
- **Session check:** each reference's `session.json` differs from its earlier
  bundle only in `run_name` and `output_directory`, and the recipe snapshots
  are identical (agent-reported). Table I, the tracking-row identity, was not
  relayed.

## Against the pre-registered readings

| Item | Pre-registered | Received | Reading |
|---|---|---|---|
| Identity | each reference equals its earlier bundle in every tracking row | session and Recipe snapshot only | **NOT RECEIVED** |
| G, SPL#4 BASE | the 14 wrong-target rows at 27.5–34.0 s lose numeric Oil, reason `FILL_OWNER_CONTESTED` | nothing | **NOT RECEIVED** |
| G, SPL#4 Accum | list every differing row | nothing | **NOT RECEIVED** |
| G, SPL#1 | list every differing row | 0 differing rows over 1,202 records; `K.gated` true on 0 frames; `FILL_OWNER_AMBIGUOUS` and `FILL_OWNER_CONTESTED` 0 | nothing to read: the gate never acted on SPL#1 (agent-reported) |
| R | BASE ACCEPTED 479.98–548.01 s, provenance `initial_state_retrospective_v3`; Accum UNRESOLVED; no legend entry without a band | card texts only | **NOT RECEIVED** |
| G-3 | resolver versions | as expected | PASS |

**Report cards (SPL1_B_ref, as relayed):**
- **BASE:** "Glass observation BASE - 합격". The card says it marked 212
  interface candidate positions and the rise/fall direction is undecided.
- **Accum:** "Glass observation Accum - 사용자 확인 필요". First observation
  669.5 s, last 724.0 s; highest at 678.5 s, lowest at 670.5 s; three main
  Foam observation spans.

**Not requested:** the agent also checked two trace keys on SPL1_B_ref.
- `top_exit_full_v3_grace` is `inactive` on every record.
- `fill_owner_witness` has no version keys on any record.

## D readouts (agent summaries)

These come from an agent-local reader (`s11_step7_gate_reader`, not in the
repository), so the counts are unverified. Table A (Accum geometry) and table K
(SPL#4 `temporal_max_jump_px`) were not relayed.

- **Table B, Accum 640.0–672.0 s (relayed as "table C"):**
  - 640.0–667.5 s: all 58 rows `UNKNOWN_REVIEW`, with no Oil or Foam Y.
  - First Oil Y at 669.5 s (Y515).
  - 671.0–671.5 s: Foam Y339/334 together with Oil Y472/461.
- **Table F, Accum 653.0–682.0 s:** the phase runs `open` /
  `FILL_EVIDENCE_ACCUMULATING` (653.5–657.9 s), then
  `INITIAL_EMPTY_ENTRY_PENDING` (658.0–668.0 s) and
  `FILL_ONSET_INTENT_NO_PREDECESSOR` (668.0 s), then `filling` /
  `FILL_MOTION_OWNER` from 668.5 s. No Foam candidate is selected as Oil.
- **Table H, Accum 680.0–700.0 s:** no `oil_air` candidate is selected in the
  whole span.
  - The tracklets 000399/000401, and later 000409, 000410, 000417, 000424 and
    000435, are refused.
  - The reasons are `INCOMPATIBLE_BRANCH`, `INSUFFICIENT_NET_PROGRESS` and
    `GLOBAL_PATH_OR_RUN_BOUND`.
- **Table J, Accum 700.0–780.0 s:**
  - Oil Y returns on 22 rows at 711.0–724.0 s (Y247 → 365, downward).
  - The drain release refuses every candidate on 13 evaluated rows at
    700.5–710.5 s (`downward_direction`, `maximum_jump`,
    `current_material_conflict`).
  - At 711.0 s it selects `oil-tracklet:000448:0233`.
  - `release_ambiguous` is false throughout.

These agree with [DSR-1](../../50-diagnostics/s11/2026-10-22-d-scope-review.md)'s
counts on ⑩: no post-Foam numeric Oil (`INCOMPATIBLE_BRANCH`), and 22 drain
rows.

## Review-012 (table V)

SPL#1 Accum 672.0–677.5 s (`WS1-ACCUM-FOAM-LAYERED`), from a raw zoom made with
`tests/diagnostics/s11_review_zoom.py`.
- **Zoom:** `zoom_source_xyxy` [1191, 48, 1669, 648], scale 2, 12 panels.
- **Marks:** one mark per panel, `changed_not_red_px` 0.
- **Files:** kept on Windows under
  `0.Windows_diagnostic\data\reviews\review-012\`. The zoom SHA-256 starts
  `5005098f`, and the marked image's starts `41bdda02`.

| Frame | Time s | Ordinary Oil Y | User mark Y (source) | Mark − output px | User's words |
|---|---:|---:|---:|---:|---|
| 16112 | 672.00 | 438.0 | 493.5 | 55.5 | foam의 최하단 |
| 16124 | 672.51 | — | 490.0 | — | foam의 최하단 |
| 16136 | 673.01 | — | 498.5 | — | foam의 최하단 |
| 16148 | 673.51 | 345.0 | 501.5 | 156.5 | foam의 최하단 |
| 16160 | 674.01 | 351.0 | 493.0 | 142.0 | foam의 최하단 |
| 16172 | 674.51 | 329.0 | 495.5 | 166.5 | foam의 최하단 |
| 16184 | 675.01 | 317.0 | 499.5 | 182.5 | foam의 최하단 |
| 16196 | 675.51 | 315.0 | 499.5 | 184.5 | foam의 최하단 |
| 16208 | 676.01 | — | 488.5 | — | foam의 최하단 |
| 16220 | 676.51 | — | 468.0 | — | foam의 최하단 |
| 16232 | 677.01 | 269.0 | 456.0 | 187.0 | foam의 최하단 |
| 16244 | 677.51 | 256.0 | 432.5 | 176.5 | foam이 무너지고 있어서 그 경계의 최하단 |

User, verbatim: "677.51s 제외하고 전부 foam의 최하단, 677.51s은 foam이 무너지고있어서 그 경계의 최하단을 표시함".

**What it shows:**
- **No dense boundary in any panel.** Every mark is the Foam region's
  bottom, the request's "최하단" case; at 677.51 s it is the bottom of the
  collapsing Foam.
- **The marked bottom holds while the output climbs.** It stays at Y488.5–501.5
  through 676.0 s and then rises (Y468 → 456 → 432.5). The ordinary output
  climbs from Y438 to Y256 while the marked bottom holds.
- **Every numeric output is far above the mark.** All 8 numeric rows lie
  55.5–187 px above it. C1 here is at most 30 px, because the zoom box spans
  600 source rows around the ellipse.
- **Score under the strict rule:** the 8 numeric rows are A and the 4 blanks
  are B (scored in [FLB-2](../../50-diagnostics/s11/2026-10-23-foam-layer-bottom-follow-2.md#held-out-result--2026-10-23)).
  Whether the output follows the Foam top, which the segment's truth
  rejects, is not established.

## What it decides

- **Gate:** not judged. The SPL#4 comparison is missing. On SPL#1 the gate
  never acted (agent-reported).
- **Review-012:** answered. It sets the `WS1-ACCUM-FOAM-LAYERED` references.
  The FLB-2 held-out case is scored, and LBT-2's Windows S2 can now be scheduled
  (the user decides).
- **Next:** the follow-up request returns the identity, the SPL#4 table G, the
  report checks, tables A/K and the FLB-2 raw lines verbatim.

## Detector Governance

- Logic-map nodes: `OIL-PHASE-FILL`, `OIL-TRACKLET`, `OIL-SELECTOR`, `FOAM-IDENTITY`
- Failure-registry entries: `S11-F04`, `S11-F05`, `S11-F06`, `S11-F08`
- First harmful stage: not claimed. Review-012 shows the production output above the marked Foam-region bottom on every numeric row at 672.0–677.5 s. The gate's effect on SPL#4 is not received.
- Existing feature coverage: the step-7 runs use the existing IFO v2, top-exit v3 and default-OFF fill-owner gate options through the headless bundle path; review-012 uses `tests/diagnostics/s11_review_zoom.py`; no Recipe or session change.
- Execution scope: four Windows runs and read-only readouts under the user-forwarded step-7 request, relayed by OCR; no Mac run.
- Logic-map impact: NONE — a receipt; no owner or edge changes.
- Failure-registry impact: NONE — no new mechanism.
