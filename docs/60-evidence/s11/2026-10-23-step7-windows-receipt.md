# Step-7 Windows receipt — 2026-10-23

**Status: RECEIVED (two replies) / G PASS on SPL#4 BASE, R PASS, identity
PASS.** The reply to the
[step-7 combined request](../../40-operations/s11-current-windows-field-qualification.md#step-7-combined-request)
came back through the user and was relayed by OCR. The first reply came mostly
as agent summaries. The read-only
[follow-up request](../../40-operations/s11-current-windows-field-qualification.md#step-7-follow-up-request)
then returned the identity, the gate's SPL#4 comparison, the report checks and
tables A/K verbatim ([second reply](#follow-up-reply--2026-10-23)). Nothing is
tuned or changed. Top-exit and the gate stay default OFF, and promoting the
gate is a separate decision for the user. FIELD FAIL / O2 OPEN and review-006
pending are unchanged.

## Runs and identity

| Run | Run ID | Resolver suffix | Bundle (Windows) |
|---|---|---|---|
| SPL4_B_ref | `005e0d58-024e-4c38-b5eb-becfc552e0cb` | `+top-exit-full-v3` | `oil_level_analysis_SPL4_B_ref_20261023_150316` |
| SPL4_B_gate | `5db2f690-96d7-4019-a485-6bba728b59c8` | `+top-exit-full-v3+fill-owner-contest-v1` | `oil_level_analysis_SPL4_B_gate_20261023_150740` |
| SPL1_B_ref | `b8b8403b-e4d2-43ce-9b70-f6ed37734b51` | `+top-exit-full-v3` | `oil_level_analysis_SPL1_B_ref_20261023_152751` |
| SPL1_B_gate | `668df459-b0c0-451b-9d04-65390d047213` | `+top-exit-full-v3+fill-owner-contest-v1` | `oil_level_analysis_SPL1_B_gate_20261023_155502` |

- **Versions (G-3):** the full resolver versions are
  `r22-oil-ownership-evidence-replacement-v1+initial-full-observation-v2` plus
  the suffix above. This is the expected set.
- **Run IDs:** read from the `run_id` column of `tracking_data.csv`, because
  `session.json` has no `run_id` key.
- **Runs:** all four exited 0 and wrote a debug trace.
- **Glasses:** SPL#1 BASE `8f94fb85…`, Accum `8fb6ebc7…`; SPL#4 BASE
  `9c74a762…`, Accum `cfef5bad…`. These are the same Glasses as the earlier
  receipts.
- **Rows:** 601 per Glass on SPL#1 and 181 per Glass on SPL#4, in all four
  bundles.
- **Source:**
  - **Six file SHA-256 values:** computed in the step-7 source folder, all
    equal to the request's.
  - **How it was made:** the user downloaded the GitHub ZIP and unpacked it
    (user, 2026-10-23).
  - **The ZIP file's own SHA-256 is not an identity check.** The ZIP now at
    that path hashes `c1c5b72b…aa368`. The first reply's value
    `4e51f9a7…d2d6d2` has 65 characters, an OCR slip. The six file hashes
    carry the identity.
- **Session check:** each reference's `session.json` differs from its earlier
  bundle only in `run_name` and `output_directory`, and the recipe snapshots
  are identical (agent-reported).
- **Table I, tracking identity:**
  - SPL4_B_ref equals `SPL4_A_top_exit_v3` (run `05985b7a-acee-4091-a876-95e46cb1f6ac`).
  - SPL1_B_ref equals ⑩ (run `84526e04-b989-437e-9790-668834771e50`).
  - For both, 0 rows differ in either Glass. The rows were matched on
    (glass_id, frame_index), every column except `run_id` was compared, and no
    row was left unmatched.

## Against the pre-registered readings

| Item | Pre-registered | Received | Reading |
|---|---|---|---|
| Identity | each reference equals its earlier bundle in every tracking row | 0 differing rows, both pairs, both Glasses | **PASS** |
| G, SPL#4 BASE | the 14 wrong-target rows at 27.5–34.0 s lose numeric Oil, reason `FILL_OWNER_CONTESTED`; any other differing row listed | exactly those 14 rows (Y704–739 → UNKNOWN, `FILL_OWNER_CONTESTED`); no other | **PASS** |
| G, SPL#4 Accum | no prediction; every differing row listed | one row: 24.5 s EMPTY_NO_INTERFACE → UNKNOWN_REVIEW, no numeric Oil in either | a removed false EMPTY, not a loss ([below](#spl4-gate-comparison)) |
| G, SPL#1 | no prediction; every differing row listed | 0 differing rows over 1,202 records; `K.gated` true on 0 frames; `FILL_OWNER_AMBIGUOUS` and `FILL_OWNER_CONTESTED` 0 | nothing to read: the gate never acted on SPL#1 (agent-reported) |
| R | BASE ACCEPTED 479.98–548.01 s, provenance `initial_state_retrospective_v3`; Accum UNRESOLVED; no legend entry without a band | BASE ACCEPTED [479.9795, 548.0058], v3; Accum UNRESOLVED (`AUTHORITATIVE_FOAM`), v3; every legend entry has a visible band | **PASS** |
| G-3 | resolver versions | as expected | PASS |

### SPL#4 gate comparison

- **BASE, 14 differing rows:**
  - Frames 825–1020 (27.5–34.0 s). The reference's FILLING, DRAINING and
    PARTIAL rows at Y721, 704, 710.5, 720, 721, 722, 722, 713, 717.5, 739, 739,
    738, 719 and 720 become UNKNOWN_REVIEW without numeric Oil.
  - Each has `FILL_OWNER_CONTESTED`, `K.gated` true and contested IDs
    `oil-tracklet:000025:0018` and `oil-tracklet:000042:0035`, the two owners
    of the 22.5–27.0 s ambiguity. The allowed set is empty.
- **BASE, the gate's other frames:** `K.gated` is true on 18 frames,
  27.5–36.0 s. The four at 34.5–36.0 s were already UNKNOWN.
- **BASE, reasons in the candidate:** `FILL_OWNER_AMBIGUOUS` 10, which
  matches the follow-up receipt's 22.5–27.0 s; `FILL_OWNER_CONTESTED` 18.
- **What it confirms:** the SPL#4 stale owner fits the survivor path, which
  the design table had marked "not confirmed". The gate removes exactly the
  14 A-class rows inside the reviewed FULL interval, and nothing else on BASE.
- **Accum, 1 differing row:**
  - At 24.5 s (frame 735), EMPTY_NO_INTERFACE becomes UNKNOWN_REVIEW, with
    `fill_state`, `overall_confidence` and `flags` differing.
  - It is `FILL_OWNER_CONTESTED`. The contested IDs are
    `oil-tracklet:000001:0005`, `000030:0025` and `000032:0026`.
  - `K.gated` is true on 4 frames, 23.0–24.5 s.
  - Candidate reasons: `FILL_OWNER_AMBIGUOUS` 35, `FILL_OWNER_CONTESTED` 4.
- **Reading the Accum row:**
  - The user saw inflow with Foam from 14 s, so an EMPTY state at 24.5 s is
    false.
  - It is the isolated single-sample EMPTY that produced the zero-width legend
    entry on 2026-10-22 ([E1/E2](2026-10-21-initial-state-report-local.md#combined-graph-strip-and-band-patterns-e1e2--2026-10-22)).
  - Neither arm has a numeric row, so by the pre-registered reading it is
    neither a loss nor an added output.
  - The gate's validation text expected "nothing else changes" on SPL#4. This
    row is the only change beyond that, and it removes a false state.

### Report checks (SPL1_B_ref)

- **Retrospective:**
  - BASE: ACCEPTED, [479.9795, 548.0057916666666] (frames 11508–13139),
    prior and interpretation `FULL_NO_INTERFACE`, provenance
    `initial_state_retrospective_v3`, evidence frames 13151, 13606 and 13610.
  - Accum: UNRESOLVED, prior `EMPTY_NO_INTERFACE`, barrier
    `AUTHORITATIVE_FOAM`, provenance v3, reason "Inference barrier before
    sufficient positive evidence."
- **`review_index.json`:**
  - BASE: `PASS`, observed coverage 0.692, effective state-aware coverage
    0.920.
  - Accum: `REVIEW_REQUIRED`, 0.0599 for both.
- **Cards:**
  - BASE "합격". Its judgment note says the criterion was met, the level
    stayed above the reference line within tolerance, and the span before
    the first catch was rebuilt from the confirmed initial state.
  - Accum "사용자 확인 필요". Its note says observed coverage is 6.0 %,
    against a 70.0 % criterion.
- **Legend and bands:**
  - The combined strip lists `초기 상태 재구성 (FULL)`, `직접 유면 확인
    어려움` and `FULL 판정`, all drawn in the BASE row.
  - The Accum row has only the grey band.
  - The detail graphs have no legend entry without a band.
  - Each band matches its strip row in position and pattern.
  - The reconstruction band is blue diagonal hatching, and the detector FULL
    band is a solid light blue.
- **What it confirms on Windows:**
  - the per-sample band cells (no zero-width legend entry);
  - E2 (hatching for an accepted reconstruction, solid for the detector),
    exercised here for the first time;
  - the first-catch guard (provenance v3, known outputs unchanged).

**Not requested:** the agent also checked two trace keys on SPL1_B_ref.
- `top_exit_full_v3_grace` is `inactive` on every record.
- `fill_owner_witness` has no version keys on any record.

## D readouts (agent summaries)

Tables B, F, H and J come from an agent-local reader
(`s11_step7_gate_reader`, not in the repository), so their counts are
unverified. Tables A and K came verbatim in the second reply.

- **Table A, Recipe ellipses (SPL1_B_ref):**
  - Accum: center (1429.92, 347.63), radii (230.4, 291.6).
  - BASE: center (288.55, 597.71), radii (288.55, 386.11).
  - Both have margin_ratio 0.08 and a first-record `maximum_jump_px` of 32.0.
  - Accum `geometry_top_y` is 56.03 and `geometry_height` 583.2, so C1 is
    29.16 px, as the FLB-2 header prints.
- **Table K, SPL#4 BASE:** `P.policy.maximum_jump_px` 32.0, and the Recipe's
  `temporal_max_jump_px` 32.0 for both Glasses.

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
  55.5–187 px above it, against C1 29.16 px.
- **Score under the strict rule:** the 8 numeric rows are A and the 4 blanks
  are B (scored in [FLB-2](../../50-diagnostics/s11/2026-10-23-foam-layer-bottom-follow-2.md#held-out-result--2026-10-23)).
  Whether the output follows the Foam top, which the segment's truth
  rejects, is not established.

## What the readouts answer

- **Accum 480–653 s (LCR-1 question 2):**
  - The rows hold no observation until 669.5 s: 640.0–667.5 s are UNKNOWN
    with no Oil or Foam Y.
  - The first catch, Y515, sits at 0.787 of the geometry height, as LCR-1
    computed, and about 124 px above the geometry bottom (Y639.2). That is
    beyond one `temporal_max_jump_px` (32 px).
  - So L2 refuses EMPTY there even without the Foam barrier, and the rows
    give no onset evidence. The span stays UNKNOWN; recovering it would need
    new onset evidence, which the user would have to schedule.
- **SPL#4 fast-rise admission (table K):**
  - The inferred rise of about 70 px per 2 fps sample exceeds the 32 px
    continuity limit.
  - That is consistent with each sample starting a new tracklet. It is still
    an inference, because no frame review has been done.
- **Post-Foam and drain (tables H and J):** they agree with DSR-1.

## What it decides

- **Gate:** the pre-registered SPL#4 prediction holds exactly.
  - On Windows it removes 14 wrong-target rows and one false EMPTY sample.
  - SPL#1 is unchanged.
  - Its local cost, 20 correct sample7 rows (oblique view), stands.
  - Promotion is the user's decision. The default stays OFF.
- **Report:** the band cells, E2 and the first-catch guard are confirmed on
  Windows.
- **Review-012:** answered. It sets the `WS1-ACCUM-FOAM-LAYERED` references.
  - The FLB-2 held-out case is scored.
  - LBT-2's Windows S2 can now be scheduled (the user decides).

## Follow-up reply — 2026-10-23

Read-only; no detector run. It came from the same step-7 source folder and
bundles, plus the FLB-2 logs. Its values are entered in the sections above.
The FLB-2 lines are in the
[FLB-2 result](../../50-diagnostics/s11/2026-10-23-foam-layer-bottom-follow-2.md#held-out-result--2026-10-23).

## Detector Governance

- Logic-map nodes: `OIL-PHASE-FILL`, `OIL-TRACKLET`, `OIL-SELECTOR`, `FOAM-IDENTITY`
- Failure-registry entries: `S11-F04`, `S11-F05`, `S11-F06`, `S11-F08`
- First harmful stage: not claimed. Review-012 shows the production output above the marked Foam-region bottom on every numeric row at 672.0–677.5 s. On SPL#4 the gate confirms that the 14 wrong-target rows come from the survivor of `FILL_OWNER_AMBIGUOUS` (`OIL-PHASE-FILL`).
- Existing feature coverage: the step-7 runs use the existing IFO v2, top-exit v3 and default-OFF fill-owner gate options through the headless bundle path; review-012 uses `tests/diagnostics/s11_review_zoom.py`; no Recipe or session change.
- Execution scope: four Windows runs and read-only readouts under the user-forwarded step-7 request, then a read-only follow-up on the same bundles and logs, both relayed by OCR; no Mac run.
- Logic-map impact: NONE — a receipt; no owner or edge changes.
- Failure-registry impact: NONE — no new mechanism.
