# OAR-1 — is an admitted interface above the fill owner a cue for the stale low owner?

**Status: COMPLETE 2026-10-27** (local, then the [Windows readout](#windows-readout--2026-10-27), then [review-017](#review-017-result--2026-10-27)). This is design
input for the
[E2 draft](../../20-architecture/s11-physical-interface-evidence-repair-design.md#october-27-undercut-fill-owner-e2),
started on the user's "시작하자" (2026-10-27). It is read-only: no detector,
flag, threshold or Recipe change.

**Result in short:**
- **Candidates of any tier above the owner are no cue.** They sit above the
  owner in almost every frame on every video.
- **An admitted tracklet more than one association step (32 px) above the
  owner is a usable cue** on sample5 and sample7:
  - sample5: it catches 20 of the 21 agent-wrong rows and none of the correct
    ones;
  - sample7: it catches 9 user-judged correct rows (the oblique back arc);
  - the other controls: nothing.
- **Windows: the cue never fires on SPL#4's 14 wrong-target BASE rows.**
  In 27.0–34.5 s no admitted tracklet other than 0018 has any candidate.
  On SPL#1 Accum it fires 7 times; 4 of those remove rows 142–187 px above
  the review-012 marks.
- **Review-017: the other three SPL#1 hits are correct rows (COST).** The
  owner lies within 10 px of the user's marks; the admitted rows above are
  65–89 px above the level. SPL#4 Accum 66.0 s shows no Oil boundary (all
  Foam). By user truth E2 would remove 4 wrong rows against 12 correct ones.

## Question

The fast-rise desk review proposed E2: fail closed when candidates persist
above a low fill owner. Two things must be known before a rule can be frozen:
- which candidates above the owner separate a stale low owner from a correct
  one;
- what that cue would remove on each control.

## Method

- **Run:** closed managed run `s11-e2-owner-above-readout-20261027-001` at
  `5ade199`.
  - **Controls:** the six fill-owner controls with the contested gate's
    Recipes, ROI inputs and initial states, at 2 fps with debug NONE.
  - **Arms:** the comparison runner's E4 mode with `--owner-readout`, which
    gives both the IFO v2 + top-exit v3 arm and the +E4 arm.
- **Tool:** the new read-only
  [`tests/diagnostics/s11_owner_above_readout.py`](../../../tests/diagnostics/s11_owner_above_readout.py)
  (SHA-256 `21adc0dc…` for the local run; `5f31ad21…` after it adds the
  `--context` near-miss listing, with the frame rule unchanged), with unit
  tests in `tests/unit/test_s11_owner_above_readout.py`. It reads a comparison file
  locally or a saved FULL-debug bundle on Windows, with the same frame rule.
- **The frame rule** applies to a row that both:
  - publishes numeric Oil;
  - has a single-owner fill reason: `FILL_MOTION_OWNER`,
    `FILL_PHASE_REENTRY`, `FILL_CURRENT_ANCHOR_HANDOFF`, the single owner of
    `FILL_CHAIN_AMBIGUOUS`, or `FILL_OWNER_COLOCATED`.

  Such a row is a hit when an Oil candidate of the same frame meets all of
  these:
  - its tracklet is admitted;
  - it is outside the allowed set and the owner chain;
  - it lies more than the Recipe step (`temporal_max_jump_px`) above every
    candidate of the allowed owners.
- **Truth:**
  - sample5: the FOA-1 agent surface estimates and FOA-1's 21 wrong rows.
  - sample7: the user's judgment that 0016 (22.0–31.5 s) is correct
    (2026-10-22).

## Results

**First reading, from the kept FOR-1 readouts:** in every published frame on
sample5 and sample7, 11–26 Oil candidates lie above the published row. Most
are untracked or unadmitted, such as fixed structure near Y370–390. So "any
tier" cannot be the cue, and the rule reads admitted tracklets only.

| Control | Single-owner published rows | Hits | Reading |
|---|---:|---:|---|
| sample5 (reference arm) | 23 | 20 | 17 of 17 attrition rows; 3 of 4 fresh-low rows (24.5, 25.5, 54.0 s). 54.5 s has no admitted row above. The two agent-correct rows (8.5, 9.0 s) are not hits |
| sample5 (+E4) | 25 | 20 | the same 20; E4's two added rows (9.5, 10.0 s) are not hits |
| sample7 (both arms) | 21 | 9 | 0016's rows at 26.5–29.0 s and 30.5–31.5 s, user-judged correct. The admitted 0019, the back arc, lies 60–89 px above |
| sample4-original-unknown | 13 | 0 | — |
| base_sample_1, sample2, sample4-interior | 0 | 0 | FULL starts publish no single-owner fill row, so these controls do not exercise the cue |

**Gaps on sample5's hits** (largest per frame):
- 124–234 px in 18 frames;
- 20.0 s 34 px and 54.0 s 35 px, only 2–3 px beyond the step.

**Admitted tracklets above** sample5's wrong owners include 0060, which the
FOA-1 design notes as an admitted level that could not own the fill under the
EMPTY initial state, and 0086–0101.

## Reading

- **On these two videos the cue separates by reason, not by history.** The
  contested gate removed 17 wrong and 20 correct rows. This cue would remove
  20 wrong and 9 correct.
- **sample7's cost remains.** An oblique back arc is admitted and lies more
  than one step above the front arc (`S11-F07`). The cue cannot tell it from a
  second surface.
- **The negative evidence is thin.** Only 13 single-owner rows outside
  sample5 and sample7 exist locally, all on sample4-original-unknown.
- **SPL#4 decides the value.** At 27.5–34.0 s the glass is FULL (review-016).
  If no admitted tracklet lies above 0018 there, E2 does nothing for the
  user's case.

## Next

The read-only
[E2 owner-above readout request](../../40-operations/s11-current-windows-field-qualification.md#e2-owner-above-readout-request)
runs the same tool on the saved step-7 and E4 bundles:
- SPL#4 `SPL4_B_ref` (BASE, Accum) and `SPL4_C_coloc` (BASE);
- SPL#1 `SPL1_B_ref` (BASE, Accum).

Its result fills the draft's SPL#4 and SPL#1 predictions, and the user then
decides whether E2 is frozen.

## Windows readout — 2026-10-27

**Received:** the relayed stdout, kept outside Git in the closed managed run
`sample/output/s11-e2-windows-relay-20261027-001`.
- **Identity:** the tool hash matches. The relayed `s11_cadence_field.py`
  hash carries OCR slips (`8`/`0`); the agent ran, which the request allowed
  only on a match.
- **Runs (saved bundles, no detector run):**
  - `SPL4_B_ref` `005e0d58…`;
  - `SPL4_C_coloc` `8b107768…`;
  - `SPL1_B_ref` `b8b8403b…`, relayed with OCR as `b0b8403b`.
- **Step:** 32 px in every run.

| Run | Single-owner published rows | Hits |
|---|---:|---|
| SPL#4 BASE (`SPL4_B_ref`) | 31 | **0** |
| SPL#4 Accum (`SPL4_B_ref`) | 18 | 1: 66.0 s, owner 0103 Y505 under admitted 0078 Y444–447 (58–61 px) |
| SPL#4 BASE (`SPL4_C_coloc`, E4) | 33 | 0 |
| SPL#1 BASE (`SPL1_B_ref`) | 0 | 0, not exercised |
| SPL#1 Accum (`SPL1_B_ref`) | 14 | 7: 669.5, 670.5, 671.5 s (owner 0147 Y515/482/461 under 0143 Y406–418); 674.0, 675.0, 675.5, 677.0 s (owner 0181 Y351/317/315/269 under 0186 Y230–313, 33–56 px) |

**Context listings:**
- **SPL#4 BASE 27.0–34.5 s:** every admitted Oil candidate in every row
  belongs to 0018 itself. Its rows lie at Y704–739. Nothing admitted is above
  it, near or far.
- **SPL#4 BASE 22.5–24.0 s (E4 arm):** only 0018 and 0035 are admitted. The
  two co-located frames are not undercut.

**Against the truth:**
- **SPL#4 BASE 27.5–34.0 s** is FULL (review-016). E2 leaves all 14
  wrong-target rows in place: the level gives no admitted tracklet in a full,
  stirred glass.
- **SPL#1 Accum 674.0–677.0 s**, compared with the review-012 marks
  (Foam-region bottom):

  | Time s | Published Y | Mark Y | Above the mark |
  |---|---:|---:|---:|
  | 674.0 | 351 | 493.0 | 142 px |
  | 675.0 | 317 | 499.5 | 182.5 px |
  | 675.5 | 315 | 499.5 | 184.5 px |
  | 677.0 | 269 | 456.0 | 187 px |

  These 4 hits remove wrong rows. The admitted rows above them are higher
  still, so they are not the level either.
- **SPL#1 Accum 669.5–671.5 s** is before review-012's first mark (672.0 s,
  Y493.5). The published Y515, Y482 and Y461 lie 22 px below to 32 px above
  that later mark (inference across time, not reviewed). So these 3 hits may
  remove correct rows.
- **SPL#4 Accum 66.0 s** is not reviewed. The user's timeline has Foam
  sloshing in Accum from 28 s.

**Reading:**
- **On the user's case, E2 has nothing to act on.** The 14 rows are the same
  stale owner with nothing admitted above it. Only history separates them,
  which is the contested gate's cue (HELD).
- **In a FULL interval, a FULL decision would also end them.** Once
  `FILLED_BARRIER` holds, the single-owner fill path no longer publishes, and
  that is E3's route (inference from the lifecycle's phase order).
- **Elsewhere the cue works as on sample5.** On SPL#1 Accum it removes rows
  far above a reviewed Foam-region bottom, with 3 unreviewed possible costs.
  Its known costs are sample7's 9 correct rows and up to 4 unreviewed rows.

## Review-017 — readings frozen 2026-10-27, before its output

**Why:** the user asked (2026-10-27): "review017 진행하고 확인해서 E2가
구현 할 의미가 있는지 한번 확인해보자". Four E2 hits have no reviewed truth.
The user marks the Oil boundary on raw zooms of those frames.
- **H1–H3:** SPL#1 Accum 669.5, 670.5 and 671.5 s. The owner 0147 publishes
  Y515, Y482 and Y461; the admitted 0143 lies at Y406–418.
- **H4:** SPL#4 Accum 66.0 s. The owner 0103 publishes Y505; the admitted
  0078 lies at Y444–447.

**Material:**
- **SPL#1 Accum:** the rows at 669.0–672.0 s, 7 panels (frames 16040–16112).
  - 672.0 s is the anchor: review-012 marked it at Y493.5.
  - The same question as review-012 is used, so the two reviews mean the same
    boundary.
- **SPL#4 Accum:** 65.0–67.0 s, 5 panels (frames 1950–2010).

**Band:** the mark ± C1. C1 is 5 % of the Glass diameter (2 × `radius_y` of
the prepare output's ellipse): 29.16 px on SPL#1 Accum, as in review-012.

**Class of each hit frame:**

| Class | When | Meaning for E2 |
|---|---|---|
| COST | the published Y lies in the band | E2 would remove a correct row |
| GAIN | the published Y lies outside the band, or the user says the Glass is full (`가득`) | E2 would remove a wrong row |
| UNREAD | the user says no boundary is visible (`안 보임`) | neither |

Each hit frame also records whether the admitted row above lies in the band.

**Anchor:** the 672.0 s mark against review-012's Y493.5. The difference is
reported; it is not a condition.

**Tally, read by the user (no automatic verdict):**
- **User truth:**
  - gains: 4 (SPL#1 Accum 674.0–677.0 s, review-012) + review-017 GAIN;
  - costs: 9 (sample7, the user's 0016 judgment) + review-017 COST.
- **Agent truth:** sample5's 20 removed rows, which are wrong against the
  FOA-1 agent surface estimates. Reported separately.
- **For comparison:** the contested gate's tally was 17 agent-truth gains
  against 20 user-truth costs. Its promotion is HELD ("승격 보류 -> 얻는거 잃는게
  비슷한 수준으로 보임", 2026-10-23).

**Not in this review:** SPL#4 BASE, which E2 does not change, and any change
to the draft rule or its 32 px step.

## Review-017 result — 2026-10-27

**Received:** tables R1 and R4, relayed, and the user's four screen photos of
the panels. They are kept outside Git in the closed managed run
`sample/output/s11-review017-relay-20261027-001`.
- **R1:** the marked-image SHA-256 starts `422219d1`, and
  `changed_not_red_px` is 0.
- **R4:** the user answered in words and left the panels unmarked: "spl4는
  모두 foam이어서 빨간선 표시 안함". The zoom header and prepare excerpts stay
  on Windows.

**SPL#1 Accum (R1):**

| Time s | Mark Y | User's words | Published Y (owner 0147) | Published − mark | Admitted above (0143) | 0143 − mark | Class |
|---|---:|---|---:|---:|---:|---:|---|
| 669.0 | 501.0 | Oil 경계면을 빛반사로 구분 | — (not a hit) | | | | |
| 669.5 | 506.0 | Oil 경계면을 빛반사로 구분 | 515 | +9 | 417 | −89 | **COST** |
| 670.0 | 513.0 | Oil 경계면을 빛반사로 구분 | — (not a hit) | | | | |
| 670.5 | 492.0 | 유체 추가 유입되면서 경계면 흔들리기 시작 | 482 | −10 | 418 | −74 | **COST** |
| 671.0 | 476.0 | 유체 추가 유입되면서 경계면 흔들림 | — (not a hit) | | | | |
| 671.5 | 471.0 | 유체 추가 유입되면서 경계면 흔들림 | 461 | −10 | 406 | −65 | **COST** |
| 672.0 (anchor) | 492.5 | foam 형성 시작 | | | | | review-012 Y493.5: 1.0 px apart |

- **Band:** C1 = 29.16 px. Each published row lies within 10 px of the mark.
- **The admitted rows above** lie 65–89 px above the mark, outside the band.
- **Anchor:** the 672.0 s mark agrees with review-012 within 1 px, so both
  reviews mark the same boundary.

**SPL#4 Accum (R4):** at 65.0–67.0 s the user saw no Oil boundary in any panel:
"Oil 경계 없음, 이미지에 보이는 모두가 foam임".
- **By the letter:** 66.0 s is **UNREAD**. The frozen GAIN wording was
  `가득`, and the user said there is no Oil boundary.
- **Reading (not frozen):** the published Oil Y505 has no Oil boundary to
  follow, so its removal would be a gain.

**Tally (user truth):**

| | Rows |
|---|---|
| Gains (wrong rows removed) | 4: SPL#1 Accum 674.0–677.0 s (review-012). 5 if SPL#4 Accum 66.0 s is read as a gain |
| Costs (correct rows removed) | 12: sample7 9 (0016) and SPL#1 Accum 3 (review-017) |
| Unread | 1: SPL#4 Accum 66.0 s |
| Separate, agent truth | sample5: 20 gains |

**Reading:**
- **By user truth E2 removes about three correct rows for every wrong one.**
  For comparison, the contested gate's tally was 17 agent-truth gains against
  20 user-truth costs, and its promotion is HELD.
- **The costs share one pattern.** The owner is the true level, and the
  admitted tracklet above it is something else:
  - sample7: the back arc of an obliquely viewed surface;
  - SPL#1 Accum 669.5–671.5 s: a row 65–89 px above an Oil surface that the
    user saw by its light reflection, as inflow begins to shake it.

  So "an admitted interface above the owner" is not evidence of a stale owner
  in fills with structure or Foam above the level.
- **The current output was right here.** On SPL#1 Accum 669.5–671.5 s the
  existing published rows are within 10 px of the user's marks. This is new
  reviewed truth for that span.

## Detector Governance

- Logic-map nodes: `OIL-PHASE-FILL`, `OIL-TRACKLET`, `OIL-SELECTOR`
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F05`, `S11-F07`, `S11-F08`
- First harmful stage: `OIL-PHASE-FILL` publishes a single low owner while an admitted interface lies above it (sample5's 20 rows, SPL#1 Accum 674.0–677.0 s; sample7's 9 correct rows show the `S11-F07` limit). On SPL#4 BASE 27.5–34.0 s the same stage publishes the stale owner with nothing admitted above it, so this cue does not reach it.
- Existing feature coverage: the production detector path with IFO v2 and top-exit v3, with and without E4; the original sample4/base_sample_1/sample2 Recipes, the frozen October 15 interior Recipe and the frozen October 22 empty-fill Recipes; initial states as in run 003; static preparation active; cost-first, RGB, Local XY and the contested gate OFF.
- Execution scope: one closed managed local run (six controls, owner readouts, debug NONE) and a new read-only readout tool with unit tests; then one Windows readout of three saved bundles (five runs of the tool, no detector run), relayed as text and kept in `s11-e2-windows-relay-20261027-001`. Review-017 (a human frame review on Windows, user-forwarded) had its readings frozen here before its output; its tables and the user's screen photos are kept in `s11-review017-relay-20261027-001`. No detector code change or tuning.
- Logic-map impact: NONE — diagnostics only.
- Failure-registry impact: NONE — no new mechanism. The oblique-arc cost is `S11-F07`; review-017's costs are a correct level with an admitted row above it, an instance of the vertical-order-as-identity risk already in `S11-F03`/`S11-F04`.
