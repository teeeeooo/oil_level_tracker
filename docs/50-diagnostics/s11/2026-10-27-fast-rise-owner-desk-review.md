# FOR-2 — the rising level above the fill owners: admission and phase owner

**Status: IN PROGRESS 2026-10-27.**
- **Review-015:** OWNER-LEVEL at 22.5–24.0 s; the level is above both owners at 24.5–27.0 s ([result](#review-015-result--2026-10-27)).
- **Step 13:** coverage **ELIGIBILITY**: the level is a candidate in every frame but below the builder tier from 25.5 s. Review-016 places the Oil FULL onset at 27.5 s ([result](#step-13-result--2026-10-27)).
- **Step 14:** **RECURRENCE-LED** by the frozen rule. Every demotion reads exactly 0.80, which points to the same-frame superior-partition rule rather than height recurrence (inference; [result](#step-14-result--2026-10-27)). Step 2 of the fill-owner gate revisit in
the [Work Plan](../../00-project/work-plan.md): the questions-2/3 desk review
(A). The user chose (2026-10-27, "그렇게하자") to send review-015 to Windows
first and run this desk review from existing records while it is out. No
design is frozen before review-015 is read. Diagnostics only: no detector,
flag, threshold or Recipe change.

## Question

The revisit's questions 2 and 3 at 2 fps
([handoff](../../60-evidence/s11/2026-10-26-step8-11-speed-handoff.md#next-the-user-decides-each-step)):
- **2.** How does the rising level get admitted? (FFF-1: the association cap
  of 32 px per 2 fps sample refuses SPL#4's fast rise.)
- **3.** Which phase owner should the fast rise have?

**Starting point** ([FOR-1](2026-10-27-fill-owner-recency-local.md),
[step-12 receipt](../../60-evidence/s11/2026-10-27-step12-windows-receipt.md)):
- SPL#4 BASE 22.5–27.0 s is `FILL_OWNER_AMBIGUOUS` between a reappearing 0018
  chain on fixed fields from a confirmation that ended at 14.5 s and a freshly
  confirmed rising 0035 (22.0–24.5 s). Both rise in the window.
- An owner's own motion does not separate a low owner from the level (NO-SEP).
  The remaining cue is relational: a higher rising interface above the owners
  (inference).
- **Open premise:** no reviewed frame says where the level is in 20–27 s.
  The user's timeline gives only "FULL reached at 24–25 s". Whether 0035 is
  the level in 22.0–24.5 s, and whether the higher provisional rows (Y463 at
  22.5 s; Y462, Y534, Y651–660 at 24.5 s) are the level, is not reviewed.

## Review-015 — readings frozen 2026-10-27, before its output

**Purpose:** test the relational premise on SPL#4 before any design builds on
it. The user marks the Oil surface on a raw zoom (no detector value is drawn).
The marks are compared on the Mac with the candidate Ys already relayed.

**Material:** SPL#4 BASE, 20.0–27.0 s at 2 fps, 15 panels, source frames 600,
615, …, 810 (the step-12 rows). Video `SPL#4_Cooling_onoff_#2.mp4`
(53,165,455 bytes); Recipe = the `SPL4_B_ref` bundle's
`recipe_snapshot.oilrecipe`, Glass BASE. Tool
`tests/diagnostics/s11_review_zoom.py` (`prepare`, then `read-marks`).

**Mark Y:** a panel's mark Y is the median of its mark Ys. A panel with no
mark, or the user's "가득" or "안 보임", has no mark Y; "가득" is counted
separately. "Near" means within 32 px (FOA-1's distance unit).

**Candidate Ys compared** (as relayed; OCR):
- owners, from the step-12 readout: 0018 and 0035 rows in 22.0–27.0 s;
- higher candidates, from the
  [SPL#4 follow-up](../../60-evidence/s11/2026-10-22-top-exit-promotion-evidence.md#spl4-opposition-follow-up-receipt--2026-10-22):
  Y463 at 22.5 s; Y462, Y534 and Y651–660 at 24.5 s; Y323–325 (`…0034`)
  from 22.0 s.

**Readings:**
- **K1, owner position:** each 0018 and 0035 row in 22.0–27.0 s on a panel
  with a mark Y is *level* (its candidate Y nearest the mark Y is within 32 px of it), *low* (more
  than 32 px below) or *above*.
- **K2, the premise:** in each of the 10 ambiguous panels (22.5–27.0 s), the
  mark Y is more than 32 px above every owner row of that frame, or the user
  says "가득".
- **K3, higher candidates:** at 22.5 s and 24.5 s, which higher candidate is
  near the mark Y, if any.
- **K4, timeline:** the first "가득" panel, against the timeline's 24–25 s.
  Reported only.

**Outcome:**
- **UNREADABLE:** fewer than 5 of the 10 ambiguous panels have a mark Y or
  "가득". The desk review proceeds on the timeline alone, and this is named.
- **ABOVE:** otherwise, if K2 holds in every ambiguous panel that has a
  mark Y or "가득", and no K1 row is level. The relational premise holds on
  SPL#4.
- **OWNER-LEVEL:** otherwise. The premise fails for the named frames: the
  design may not prefer a higher interface over that owner there.

## Review-015 result — 2026-10-27

**Received:** the Windows agent's relayed table (OCR) and four phone photos
of the marked sheet (21.5–27.0 s; 20.0–21.0 s were not photographed). The
photos and the relayed marks are kept outside Git, in the closed managed run
`sample/output/s11-review-015-photos-20261027-001`. The marked PNG stays on
Windows (`…\reviews\review-015\`).

**Identity:**
- video SHA-256 `9f494a6f…`, 53,165,455 bytes;
- Glass `9c74a762…` BASE, ellipse radius_y 271.70 (H 543.4, as in step 12);
- zoom [535, 283, 679, 843] at ×2, clean sheet `95782f00…`, marked sheet
  `8d138dd7…`, `changed_not_red_px` 0;
- one mark per panel.
- The tool hash came back with `b`/`8` and `0`/`8` OCR slips; the agent
  reported a match and ran.

**Marks (source Y; the user's words abridged):**

| Time s | 20.0 | 20.5 | 21.0 | 21.5 | 22.0 | 22.5 | 23.0 | 23.5 | 24.0 | 24.5 | 25.0 | 25.5 | 26.0 | 26.5 | 27.0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Mark Y | 794.5 | 790.0 | 790.0 | 792.0 | 790.5 | 781.5 | 768.0 | 761.5 | 730.0 | 657.5 | 634.3 | 550.0 | 490.5 | 426.0 | 382.5 |
| Step px | – | 4.5 | 0.0 | −2.0 | 1.5 | 9.0 | 13.5 | 6.5 | 31.5 | 72.5 | 23.2 | 84.3 | 59.5 | 64.5 | 43.5 |

- **20.0–22.0 s:** the Oil surface is low ("차오르기 시작" at 22.0 s).
- **22.5–24.0 s:** it rises slowly, then faster.
- **From 24.5 s:** Foam forms. The mark is the strict Foam–Oil boundary,
  drawn as a diagonal at 24.5–25.5 s. From the photos, that diagonal spans
  up to about ±27 px around the centroid (about ±7 px at 24.5 s).
- **25.5 s:** the Foam top reaches the Glass top ("foam은 Full / Oil은
  차오르는중").
- **26.0–27.0 s:** the Oil pushes the Foam bottom up.

**Readings:**
- **K1, owner position** (14 owner rows in 22.0–27.0 s):
  - **level, 7 rows:** every 0018 and 0035 row in 22.5–24.0 s. The nearest
    candidate lies 1.0–28.5 px from the mark.
  - **low, 6 rows:** every row in 24.5–27.0 s, 59.5–321.5 px below the mark.
  - **above, 1 row:** 0035 at 22.0 s, Y756, which was published. It lies
    34.5 px above the mark.
- **K2, the premise:** fails at 22.5, 23.0, 23.5 and 24.0 s. It holds at
  24.5–27.0 s (6 of 10). No panel was "가득".
- **K3, higher candidates:**
  - At 24.5 s, Y651–660 is the level (−6.5 / +2.5 px).
  - At 22.5 s, Y463 is 318.5 px above the level, so it is not the level.
  - Y462 and Y534 (24.5 s) are not the level.
  - Y323–325 is never near the level; the closest is 57.5 px, at 27.0 s.
- **K4, timeline:** no "가득" panel. The Foam reaches the top at 25.5 s.
  The Oil enters the top band (Y ≤ 437.9) at 26.5 s and is still rising at
  27.0 s (Y382.5).

**Outcome: OWNER-LEVEL**, named frames 22.5, 23.0, 23.5 and 24.0 s. There the
design may not prefer a higher interface over the owners. In 24.5–27.0 s the
level is above both owners, as P1 put it.

**What this changes (inference unless stated):**
- **Question 1, the ambiguity has two parts:**
  - **22.5–24.0 s:** two owners on one surface. 0018 and 0035 are both
    within 32 px of the mark, so publishing either would have been correct.
    `FILL_OWNER_AMBIGUOUS` costs 4 frames of correct output there.
  - **24.5–27.0 s:** the fast rise leaves both owners behind at Y704–723.
    Failing closed is correct there, and the 14 wrong-target rows at
    27.5–34.0 s are the low owner 0018 outlasting it.
- **Questions 2 and 3, the fast rise is shorter and later than FFF-1
  inferred:**
  - Rise: 24.0 → 27.0 s, 347.5 px in 3 s. Five of the six steps exceed the
    32 px cap (43.5–84.3 px).
  - Up to 24.0 s every step is within the cap (≤ 31.5 px), and the owners
    tracked the level.
  - FFF-1 assumed a rise of about 70 px per sample from 21.5 s.
- **A counterexample for any "prefer the higher interface" rule:** at
  22.5 s the only higher candidate on record, Y463, is 318.5 px above the
  level. A single higher row is no evidence. D1 and D2 would need a rising
  sequence that reaches the level, not one row.
- **The SPL#4 timeline's "FULL reached at 24–25 s" was the Foam (user
  statement at 25.5 s).**
  - The Oil is not at the top by 27.0 s.
  - The frozen top-exit entry condition used that timeline. Its P window
    asked for the first FULL row in 22.0–27.0 s. The earlier P FAIL was
    judged against it and is not re-judged here.
  - Whether to correct the SPL#4 truth is the user's call.

## Step 13 — readings frozen 2026-10-27, before its output

**User (2026-10-27):** "1. review 기준으로 변경 2. review 16도 진행 약 27s에서
oil full 되고 뿌연 상태(잔여 기포)가 점점 투명해지면서 약 42s oil 투명도 회복됨
3. 확인하자". The SPL#4 BASE truth is corrected in the
[validation owner](../../30-validation/s11-physical-interface-evidence-repair-validation.md#top-exit-v3-promotion-acceptance--2026-10-22).
One Windows request carries the two items below.

**R, level coverage readout** (read-only, `SPL4_B_ref`, tool
`tests/diagnostics/s11_level_coverage_readout.py`). Marks are the review-015
marks at 24.0–27.0 s (7 rows); near ≤ 48 px is printed.
- **Covered frame:** a near group lies within 32 px of the mark. At 24.5–25.5 s
  the boundary is a diagonal up to about ±27 px around the mark; this is a
  named limit.
- **C1, coverage:** the number of covered frames, out of 7.
- **C2, eligibility:** covered frames whose covered groups include a post-track
  tier of `CONTINUATION_ELIGIBLE` or `ANCHOR_ELIGIBLE` (builder-eligible).
- **C3, continuity:** the longest run of consecutive covered frames in which
  one tracklet ID appears among the covered groups of each frame.
- **C4, admission:** covered frames with an admitted covered group. Reported
  with the tracklet failure reasons.
- **Outcome**, the first that applies:
  - **GENERATION:** C1 < 4. The level is mostly not an Oil candidate.
    Candidate generation comes before admission.
  - **ELIGIBILITY:** C2 < 4. The level is a candidate but below the builder
    tier.
  - **ASSOCIATION:** C3 < 3. Eligible level rows exist but no tracklet follows
    them; this is the FFF-1 cap, confirmed on reviewed truth.
  - **DOWNSTREAM:** C3 ≥ 3. A tracklet follows the level; the barrier is
    admission or phase, named by C4 and the fields.

**V, review-016** (the user marks SPL#4 BASE 27.0–30.0 s, 7 panels, source
frames 810–900, with the review-015 sheet settings).
- **M1, FULL onset:** the first panel the user calls "가득". If none, the
  onset is after 30.0 s.
- **M2, before the onset:** marks continue review-015's rise; reported.
- **M3, cloudiness:** the user's words on residual bubbles; reported.

## Step 13 result — 2026-10-27

**Received:** the Windows agent's relayed outputs (OCR) and three phone photos
of the review-016 sheet. Photos and the relayed outputs are kept outside Git,
in the closed managed run `sample/output/s11-review-016-photos-20261027-001`.
- **Identity:** run `005e0d58…` (`SPL4_B_ref`), the same video, Recipe and
  Glass as review-015.
- **Source hashes:** the agent reported a match for all four; the relayed
  values carry `0`/`8` OCR slips.

### R, level coverage readout (24.0–27.0 s, review-015 marks)

| Time s | Mark | Oil cands | Nearest px | Covered groups (≤ 32 px) | Builder-eligible covered group |
|---|---:|---:|---:|---|---|
| 24.0 | 730.0 | 24 | 1.0 | untracked Y731–732 (CANDIDATE_ONLY / HARD_INVALID); 0018 Y756 (+26) | 0018 only, the low owner |
| 24.5 | 657.5 | 25 | 0.5 | untracked Y657 (CANDIDATE_ONLY, `TRACK_OPPOSITION`); `0049:0040` Y651–660 | `0040` (CONTINUATION, `INSUFFICIENT_NET_PROGRESS`) |
| 25.0 | 634.3 | 28 | 9.3 | `0040` Y613–625; untracked Y606 (−28.3) | `0040` (ANCHOR / CONTINUATION, `INSUFFICIENT_NET_PROGRESS`) |
| 25.5 | 550.0 | 26 | 13.0 | untracked Y521–537 | none (CANDIDATE_ONLY / HARD_INVALID; `insufficient_authority`, `TRACK_OPPOSITION`) |
| 26.0 | 490.5 | 23 | 1.5 | untracked Y478–493 | none (same reasons) |
| 26.5 | 426.0 | 26 | 6.0 | untracked Y419.5–435 | none (CANDIDATE_ONLY; `material_path_no_corridor`, `TRACK_OPPOSITION`) |
| 27.0 | 382.5 | 24 | 1.5 | untracked Y373–381 | none (CANDIDATE_ONLY / HARD_INVALID, `TRACK_OPPOSITION`) |

**Readings:**
- **C1, coverage: 7 of 7.** A candidate lies within 13 px of the mark in
  every frame.
- **C2, eligibility: 3 of 7** (24.0, 24.5, 25.0 s). At 24.0 s the only
  eligible covered group is the low owner 0018, 26 px below the mark. So the
  level itself is builder-eligible only at 24.5 and 25.0 s, as `0040`.
- **C3, continuity: 2** (`0040` at 24.5–25.0 s).
- **C4, admission:** one covered frame, 24.0 s, which is the owner 0018. No
  level row is admitted:
  - `0040` fails with `INSUFFICIENT_NET_PROGRESS`, net 0.0.
  - The untracked rows fail with `INSUFFICIENT_AUTHORITY`.

**Outcome: ELIGIBILITY** (C1 ≥ 4; C2 < 4).
- The level is seen, so candidate generation is not the barrier.
- From 25.5 s the level rows never reach the builder tier. The recorded
  reasons are `insufficient_authority`, `TRACK_OPPOSITION` and
  `material_path_no_corridor`.
- So on reviewed truth the first barrier of the fast rise is `OIL-AUTHORITY`
  (the post-track tier), ahead of the FFF-1 association cap. The cap applies
  only at 24.5–25.0 s, where `0040` did form and gained no net progress.
- **Correction (from source, 2026-10-27):** an inference written here at
  first said the existing tracks, the low owners among them, oppose the new
  higher rows. That is wrong. `TRACK_OPPOSITION` is the recurring-row check
  (`OilTrackletOppositionOwner._apply_track_opposition`), which works by
  height, not by track:
  - It runs over the whole resolved sequence. Candidates fall into Y buckets
    of 2.4 × the tolerance (tolerance = max(3, 1.8 % of H), about 9.8 px on
    SPL#4).
  - A bucket is penalized when its best row recurs: in at least 6 frames,
    18 % of the frames, a 6-frame run, stable in Y, with an artifact or
    optics signature.
  - Every candidate in that bucket, in any frame, receives the penalty. A
    candidate is demoted to `CANDIDATE_ONLY` when the penalty is ≥ 0.60 and
    it has a candidate-local contradiction (`recurrence_hard_contradiction`).
  - So a fast level that crosses a height where some other row recurs can be
    demoted by that height's history.

### V, review-016 (27.0–30.0 s)

| Time s | 27.0 | 27.5 | 28.0–30.0 |
|---|---|---|---|
| Mark | Y380.0 | — | — |
| User | "foam이 glass 최상단 (foam full, oil은 아직 full 아님)" | "Oil full (경계 없음)" | "Oil full 유지, glass는 foam 잔여 기포로 뿌연상태" |

- **M1, FULL onset: 27.5 s.**
- **M2:** at 27.0 s the mark (Y380.0) agrees with review-015's mark (Y382.5)
  within 2.5 px.
- **M3:** from 28.0 s through 30.0 s, every panel is cloudy from residual
  Foam bubbles.
- The production output at 27.5–28.0 s (0018, Y721 and Y704) is therefore
  wrong-target numeric Oil inside reviewed FULL, as recorded at step 7.

## Step 14 — readings frozen 2026-10-27, before its output

**User (2026-10-27): "응 그렇게 진행하자"**, for a read-only readout of why the
level rows are demoted.

**Tool:** `tests/diagnostics/s11_level_authority_readout.py` on `SPL4_B_ref`.
For each candidate within 32 px of the marks, it prints:
- the initial authority, its reason and failed gates;
- the phase identity and its failed gates;
- the post-track authority, `track_opposition` and its effective value;
- the reject stage;
- the candidate-local inputs of the recurrence demotion (material-texture
  conflict, artifact likelihood, static prior, optics, registered motion);
- for each candidate with opposition, how often an Oil candidate recurs at
  that height over the whole Glass trace: frames present, the longest run,
  and its time span.

The recurrence count approximates the resolver's bucket check, which uses
shifted grids and the best row per frame. The local check passed (run
`s11-level-authority-check-20261027-001`).

**Marks:** review-015 at 24.5–27.0 s (6 rows). 24.5 and 25.0 s are the
contrast frames, where the level was eligible as `0040`. 25.5–27.0 s are the
demoted frames.

**Route of each level candidate** (|d| ≤ 32 px):
- **ELIGIBLE:** the post-track tier is `CONTINUATION_ELIGIBLE` or
  `ANCHOR_ELIGIBLE`.
- **RECURRENCE:** the initial tier is eligible, but the post-track tier is
  `CANDIDATE_ONLY`.
- **INITIAL:** the initial tier is `CANDIDATE_ONLY`; the failed gates name
  why.
- **NONE:** no tier at all (hard-invalid or pruned).

A frame takes its best route, in the order ELIGIBLE > RECURRENCE > INITIAL >
NONE.

**Readings:**
- **A1:** the route of each demoted frame (25.5, 26.0, 26.5, 27.0 s).
- **A2:** for RECURRENCE candidates, the recurrence count and run span. The
  recurrence is **outside the rise** if the longest run has at least 6 frames
  and its span does not lie inside 24.0–27.5 s.
- **A3:** for INITIAL candidates, the failed gates, by count.

**Outcome:**
- **RECURRENCE-LED:** at least 3 of the 4 demoted frames route RECURRENCE.
- **INITIAL-LED:** at least 3 route INITIAL or NONE.
- **MIXED:** otherwise.
- The contrast frames are reported only.

## Step 14 result — 2026-10-27

**Received:** the relayed stdout (kept outside Git in the closed managed run
`sample/output/s11-step14-relay-20261027-001`).
- Run `005e0d58…`, 181 trace frames, recurring tolerance 9.781 px.
- Joins: 0 missing, 0 ambiguous.
- Source hashes: the agent reported a match; the relayed values carry `0`/`8`
  OCR slips.

| Time s | Candidates ≤ 32 px | ELIGIBLE | RECURRENCE (eligible → `CANDIDATE_ONLY`) | INITIAL | NONE | Frame route |
|---|---:|---:|---:|---:|---:|---|
| 24.5 (contrast) | 7 | 4 (Y651–660) | 3 (Y657, Y631–632) | 0 | 0 | ELIGIBLE |
| 25.0 (contrast) | 4 | 3 (Y613–625) | 1 (Y606) | 0 | 0 | ELIGIBLE |
| 25.5 | 6 | 0 | 3 (Y521–528) | 2 (Y529) | 1 | RECURRENCE |
| 26.0 | 8 | 0 | 6 (Y478–492) | 2 (Y485, Y493) | 0 | RECURRENCE |
| 26.5 | 5 | 0 | 1 (Y420) | 4 | 0 | RECURRENCE |
| 27.0 | 4 | 0 | 4 (Y373–381) | 0 | 0 | RECURRENCE |

**Readings:**
- **A1:** all 4 demoted frames route RECURRENCE.
- **A2:** the RECURRENCE candidates' recurrence spans all lie outside the
  rise, at 67.5–82.0 s, which is the drain after 63 s passing the same
  heights.
  - Their longest runs reach 6 frames only at 25.5 s (Y521, 6) and 26.0 s
    (7 each).
  - At 26.5 s (4) and 27.0 s (3–4) they are shorter than 6 in this
    approximation.
- **A3:** the INITIAL candidates fail on two kinds of gates:
  - `oil_hypothesis` rows fail `material_support`, `boundary`,
    `boundary_advantage`, `localized_boundary` and
    `material_texture_conflict<0.60`;
  - `material_path` rows fail `material_path_no_corridor`.

**Outcome: RECURRENCE-LED.** In every demoted frame the level had an eligible
initial tier and lost it after tracking (post-track `CANDIDATE_ONLY`).

**After the result (source reading, inference; no rule is changed):**
- **The 0.80 value.** Every post-track demotion, in all six frames, has
  `track_opposition` exactly 0.80.
  - The height-bucket penalty is continuous: sample5's level rows read
    0.166–0.184 in the local check.
  - The same-frame superior-partition rule in `_apply_track_opposition` sets
    `max(opposition, 0.80)`. It demotes a candidate with a local
    contradiction when another candidate of the same frame is a material
    path with terminal-partition support ≥ 0.60 and layer topology < 0.5,
    lies at least 8 px away and has comparable local quality.
  - Every demoted level row here has material-texture conflict ≥ 0.60
    (0.62–0.83), so the local-contradiction condition holds.
- **So the likelier mechanism** is a same-frame peer, not the drain's height
  history. The A2 drain coincidence would then be incidental.
- **What the frozen route cannot separate.** It names post-track demotion,
  not which post-track rule fired.
- **Which peer.** A peer with terminal-partition support is a lower material
  boundary. During the rise, the lower boundary at Y700–725 that the owners
  track is the natural candidate, but this is not read.
- **The next readout would tell.** It would list, for each demoted level
  row, the same-frame peers that meet the partition conditions (material
  path, `material_terminal_partition_support`, `sequence_material_layer_topology`,
  |Δy| ≥ 8), with their Y and tracklet.

## Desk review — 2026-10-27, from existing records

### Where a fast rise is lost: two capped layers (source)

1. **`OIL-TRACKLET`** (FFF-1): a row extends a tracklet only within
   `temporal_max_jump_px` × gap (32 px per 2 fps sample on SPL#4). Beyond it,
   each row starts a new provisional tracklet that fails with
   `INSUFFICIENT_NET_PROGRESS` (27.2 px within the 6-frame window).
2. **`OIL-PHASE-FILL`** (new reading here):
   - `_advance_fill_chains` takes only admitted, upward rows.
   - A chain hands off to a new tracklet only within the same cap
     (`_compatible_handoff`: |Δy| ≤ `maximum_jump_px` × gap). The lifecycle's
     `maximum_lost_frames` is 3, so a handoff can bridge at most 4 samples,
     128 px.
   - FULL (`FILL_SPAN_CONFIRMED`) needs a chain of at least 3 observations
     whose last row is in the top band and which spans at least 20 % of the
     height (`_fill_confirmation_profile`). On SPL#4 BASE that means Y ≤ 437.9
     and a span of 108.7 px.

**So admission alone is not enough (inference).** A rise admitted at the
tracklet layer would still be linked into a fill chain at no more than 32 px
per sample. Any fix must carry the rise through both layers. This matches
step 10, where phase was a barrier at 6 fps as well.

### What is on record for SPL#4 BASE 20–27 s (no reviewed level yet)

| Family | Rows | Source |
|---|---|---|
| Three stacked rows about 50 px apart | `0025:0018` Y801–802 (20.5–21.5 s); `0042:0035` Y740–758 (21.0–23.0 s); `0025:0016` Y702–703.5 (20.5–22.5 s) | step 8 |
| The two owners, rising in the ambiguity | 0018 Y785 → Y704–714 (22.5–27.0 s); 0035 Y742–753 → Y708 (22.5–25.0 s), freshly confirmed 22.0–24.5 s | step 12 |
| Higher rows, never admitted | Y463 (22.5 s); Y462, Y534, Y651–660 (24.5 s); each a new provisional tracklet | follow-up |
| A fixed row near the top | Y323–325 (`…0034`) from 22.0 s, never admitted; at 6 fps `0057` reaches Y323 by 21.3 s | follow-up, step 10 |
| The user's timeline | Oil from about 11 s; FULL reached at 24–25 s | entry conditions |

Two pictures fit these rows, and they conflict:
- **P1, the level is above the owners.** It leaves about Y800 near 21.5 s
  and reaches the top band by 24–25 s, which is more than 360 px in about
  3 s. The higher rows are the level seen once each. The stacked rows are
  other features: foam layers or structure (inference).
- **P2, an owner is the level.** For example, 0035 rises 39 px over
  22.0–24.5 s. This conflicts with the timeline's FULL at 24–25 s unless the
  timeline is off by seconds.

Review-015 tells them apart: ABOVE supports P1, and OWNER-LEVEL supports P2
for the named frames.

### Directions by outcome (for the user's choice; nothing decided)

**If ABOVE (P1):** question 3's answer is that no current owner may hold the
fill during the rise. Three directions remain; each reuses an existing
owner:

| Direction | What it changes | What it gains | Main risk |
|---|---|---|---|
| D1, ownerless fast rise (`OIL-PHASE-FILL`) | While rising rows exist above every dynamic owner, the fill phase publishes no owner (fail closed) instead of the stale owner | removes wrong-target rows such as the 14 at 27.5–34.0 s, using a cue that names a reason (the contested gate only marks outlasting) | sample7's front arc, likely the same cost as the gate (inference); no FULL by itself |
| D2, chain-level sweep (`OIL-PHASE-FILL`, with `OIL-TRACKLET` rows as input) | The fill chain may link unadmitted rows above the owners across samples when they form a monotone rise with material evidence, bounded by the geometry | FULL through the existing top-band `FILL_SPAN_CONFIRMED` | `S11-F03`/`S11-F04`: motion or recurring Y used as identity; step 8 showed geometric triplets can stitch stacked rows |
| D3, owner-free FULL (FFF-1 option 3) | FULL from a bounded bottom-to-top sweep and an interface-free top, with no owner | FULL without identity | `S11-F05`, `S11-F06`/`S11-F07` (Foam racing up looks like a sweep), `S11-F10` |

- **Not reopened:** densification and a higher rate (user, 2026-10-26),
  option 4 (rejected), and the fast-rise seed witness (0 qualifying on SPL#4;
  no retuning).
- **D1 composes with D2 or D3.** D1 alone does not reach FULL, which the user
  requires for fast fills, so it is a first step, not an answer.
- **D2 is testable only against the marks:** do the higher rows follow the
  review-015 marks frame by frame? Today only one or two such rows are on
  record per frame (22.5 s and 24.5 s).

**If OWNER-LEVEL (P2, for the named frames):** the relational cue is wrong
there. The ambiguity is then a true level (for example 0035) against a stale
chain (0018). The question becomes how to retire a reappearing chain that
carries fixed fields from an old confirmation. FOR-1's recency test does not
retire it: 0018 passes `P` in 7 of its 8 ambiguous rows. The timeline
conflict goes back to the user.

**If UNREADABLE:** the choice goes to the user on the timeline alone.

### What the review-015 reply needs next (any outcome)

*Written before the reply; the result above narrows it to 24.0–27.0 s and to
the frames after 27.0 s that review-015 did not cover.*

- **Candidate coverage at the marks.** For D2, each mark needs a candidate row
  near it in that frame. The relayed records list the higher rows only at
  22.5 s and 24.5 s, so per-frame coverage near the marks is not on record.
- **A read-only Windows readout would supply it.** The existing
  `s11_fast_rise_readout.py` or `s11_fill_owner_trace_readout.py` on
  `SPL4_B_ref` can list every Oil candidate per frame, with no new run.
- **It is frozen after the marks are known** and judged against them. It is
  not requested before review-015 returns.

## Detector Governance

- Logic-map nodes: `OIL-TRACKLET`, `OIL-PHASE-FILL`
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F05`, `S11-F08`
- First harmful stage: SPL#4 2 fps 22.5–27.0 s is `OIL-PHASE-FILL` `FILL_OWNER_AMBIGUOUS` (step 12); upstream, the rising level is not an admitted `OIL-TRACKLET` owner (FFF-1, inferred). Review-015 tests where the level is.
- Existing feature coverage: reuses the saved step-7 `SPL4_B_ref` bundle and its Recipe snapshot, the relayed step-12 and follow-up candidate Ys, and the existing raw review zoom; no detector option is exercised.
- Execution scope: one human review on Windows (review-015, user-forwarded) and a Mac desk review of existing records; no detector run, tuning, flag or threshold change.
- Logic-map impact: NONE — diagnostics only.
- Failure-registry impact: NONE — no new mechanism.
