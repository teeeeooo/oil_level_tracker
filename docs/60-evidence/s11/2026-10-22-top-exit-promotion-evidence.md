# Top-exit v3 promotion evidence — 2026-10-22

**Status:**
- **N class (local negatives):** PASS on all six controls, and again at the
  SPL#4 request's code head `933ff49` with identical output. No control reached
  a top-exit witness or a pending closure, so the closure predicates are still
  unexercised on real video.
- **SPL#4 (Windows, [receipt](#spl4-receipt--2026-10-22)):** **P FAIL** — no
  top-exit FULL row at all, and the candidate equals the reference in every
  row. R is not evaluated (no episode); N (Accum) and U pass. Under the
  pre-registered rule the production default stays OFF.

The criteria are the
[pre-registered promotion acceptance](../../30-validation/s11-physical-interface-evidence-repair-validation.md#top-exit-v3-promotion-acceptance--2026-10-22);
nothing here changes them. Top-exit v3 stays default OFF; FIELD FAIL / O2 OPEN
are unchanged. Current authority is the [Work Plan](../../00-project/work-plan.md).

## Local negatives (N class) — 2026-10-22

**Truth and Recipes:**
- **User confirmation (2026-10-22):** sample5 (water) and sample7 (milk) start
  EMPTY and never become full, and the shown ellipses are correct. The other
  four controls keep their earlier never-FULL scope.
- **Recipes:** managed run `sample/output/s11-empty-fill-roi-20261022-001`
  froze them before any detector run. The ellipse is the vessel interior from
  the inner rim to the top of the solid base, measured with edge profiles on the
  empty first frame.

  | Control | Ellipse (cx, cy, rx, ry) | Top 27 % band end | Recipe SHA-256 |
  |---|---|---|---|
  | sample5 | 960.5, 593.0, 142.5, 257.0 | Y474.8 | `d6394f9a…2b89de` |
  | sample7 | 1130.0, 600.0, 287.0, 303.0 | Y460.6 | `effd31e1…c9ca9c9c` |

**Runs:**
- **Arms:** IFO v2 in both; top-exit v3 OFF against ON. 2 fps, debug NONE;
  cost-first, RGB and Local XY OFF.
- **Run `s11-top-exit-negatives-20261022-001`** (head `cba4067`): the four
  existing controls plus sample7.
  - sample5 failed before producing any output. Its window ended at the nominal
    duration, 54.855 s, which lies past the last decodable frame (about
    54.82 s).
  - The window end was moved to 54.8 s (`60d6a9d`) before any sample5 output
    existed.
- **Run `s11-top-exit-negatives-20261022-002`** (head `60d6a9d`): sample5
  alone.

| Control | Initial state | Rows | Numeric Oil / Foam | FULL rows OFF / ON | Top-exit FULL rows | Arms equal (raw inputs, rows, events, report) | Pending closures | N1/N2 |
|---|---|---:|---:|---:|---:|---|---:|---|
| sample4, original Recipe | UNKNOWN | 113 | 101 / 26 | 0 / 0 | 0 | Yes | 0 | PASS |
| sample4, Oct 15 interior Recipe | FULL (stress) | 113 | 16 / 76 | 0 / 0 | 0 | Yes | 0 | PASS |
| base_sample_1 | FULL (stress) | 30 | 12 / 0 | 0 / 0 | 0 | Yes | 0 | PASS |
| sample2 | FULL (stress) | 5 | 0 / 0 | 0 / 0 | 0 | Yes | 0 | PASS |
| sample7 (milk) | EMPTY | 90 | 21 / 3 | 0 / 0 | 0 | Yes | 0 | PASS |
| sample5 (water) | EMPTY | 111 | 23 / 4 | 0 / 0 | 0 | Yes | 0 | PASS |

- **The four existing controls** reproduce v3's row counts and top-exit reason
  counts exactly.
- **Summaries:** `…-001/evidence/summary.json` (`d5aca30f…3ac13`) and
  `…-002/evidence/summary.json` (`ca43c875…77b0d6`); the per-control
  `comparison.json` files are kept beside them.

**Verdict: N1/N2 PASS on all six.**

**Rerun at the frozen head (2026-10-22):** the N row requires the controls at
the head of the evidence run, so run `s11-top-exit-negatives-20261022-003`
reran all six at `933ff49`, the SPL#4 request's code head (user-authorized).
- **Verdict:** N1/N2 PASS on all six, with the same counts as above.
- **Identical to runs 001/002:** in every control and both arms, the rows,
  events, reconstruction, report, phases, raw-input hashes and detector
  versions are equal, as is each Recipe hash (`run_id` ignored).
- **Kept:** `summary.json` (`d98a7039…3fa192`) and `rerun-equality.json`
  (`476716e2…bf8ea6861`), which holds the per-control comparison-file hashes.
  The six comparison files equal the earlier ones and were not kept.

**What it does not show:**
- **No witness or pending closure anywhere.** The closure predicates, including
  the two-frame-blank risk, remain unexercised on real video, as for the
  original four controls.
- **No owner entered the band.**
  - sample5: the selected Oil spans Y604–819 against a band end of Y474.8. The
    settled surface at about Y491 is never selected; the last Oil rows
    (50.5–54.5 s) sit at Y654–696, roughly 160–200 px lower. This is a
    wrong-target observation on a development scene, not scored here.
  - sample7: the selected Oil spans Y635–773 against Y460.6. No Oil row is
    selected after 31.5 s.
- **What it adds:** the IFO-inactive EMPTY-initial path now shows that top-exit
  adds no output when no owner reaches the band.

**Reported, not scored:**
- **Fill cap:** no `FILLED_CAP_VETO` in any control.
- **Initial-state reconstruction (ON arm):**
  - sample5: UNRESOLVED. The continuing run broke on a step above the jump
    limit: the first catch is 8.5 s Y819, the next 20.0 s Y604.
  - sample7: UNRESOLVED.
  - The FULL-stress controls (base_sample_1 CONFLICT, sample2 ACCEPTED) are
    stress conditions, not truth.

## Windows SPL#4 (user alias "sample4") — 2026-10-22

`SPL#4_Cooling_onoff_#2.mp4`, a Windows recording the user calls "sample4". It
is **not** the Mac `sample/sample4.mp4`, which is 56 s long with one Glass. The
user reviewed it by eye and relayed approximate times. Recorded verbatim:

```text
BASE
11s : Oil 유입 시작하지만 glass 최 하단에 약간만 보임
18~19s : 유면은 glass 최하단, glass 표면으로 oil 쏟아지면서 흘러내리는 자국 남음
21s : Oil 빠르게 차오르면서 유면 빠른 속도로 상승
23s : 유면 상승하면서 Foam 발생 시작
24~25s : 빠른 속도로 Foam + Oil 차오르면서 Full 도달
25s 이후 : Foam이 빠른 속도로 위로 밀려 올라감 glass는 가득 찬 Oil과 잔여 Foam의 흔적으로 꽉참 (연기가 가득 찬 것 처럼 교반 작용 일어남)
50s 부근 : 투명도 회복 (25s 이후 계속 Full 유지)
63s : 상단에서 유면 내려오기 시작함 (Full 해제)
65s : 상단에서 내려오기 시작한 유면 위쪽에 Foam 발생
~85s : 상단 Foam이 두꺼워지면서 유면이 밀려 내려옴. Foam은 Full ↔ 해제 반복

Accum
14s : 유체 유입 시작되면서 Foam 발생 (최하단)
~28s : 빠른 속도로 Foam 성장하면서 glass 최상단 도달 (Foam이 Full ↔ 해제 반복)
28s : Full 해제됨 Foam이 아래로 내려오기 시작
~85s : Foam이 위아래로 출렁이면서 아래쪽으로 조금씩 내려옴 (지속적으로 유체 유입 되면서 빠른 속도로 출렁임)
```

The agent then asked five questions: identity, Recipe, window and initial
states, Foam at the top, and timing. The user's answers, verbatim:

```text
1. 아예 다른 영상임
파일명 : SPL#4_Cooling_onoff_#2.mp4
용량 : 53,165,445 바이트 (디스크 할당 53,166,080 바이트)
영상 길이 : 4분 20초
프레임 : 30
해상도 : 1920*1080

2. Recipe 있음 (artifact 포함)
3. 둘 모두 empty에서 시작
4. Full 아님이 정답임, 25~63s은 oil로 가득찬 full
5. 대략적인 구간으로 시도해보고 불충분하면 22–27 s와 61–65 s 구간만 Windows에서 사람 검토로 다듬자
```

**Size correction (2026-10-22):** the size in answer 1 is a typo. The
file is 53,165,455 bytes. The Windows request's identity check stopped on the
mismatch before any detector run, and the user confirmed 53,165,455 from the
file properties. The other answers are unchanged.

**Frozen before any output on this recording** in the
[SPL#4 entry conditions](../../30-validation/s11-physical-interface-evidence-repair-validation.md#top-exit-v3-promotion-acceptance--2026-10-22):

| Glass | Reviewed interval | Class | Frozen window |
|---|---|---|---|
| BASE | EMPTY at 0 s, Oil from about 11 s | Initial state | IFO v2 is inactive, so top-exit acts alone |
| BASE | FULL reached at 24–25 s | **P** | first FULL row in 22.0–27.0 s; none before 22.0 s |
| BASE | FULL, filled with Oil, 25–63 s | P3 hold | FULL or D2b UNKNOWN, no Oil coordinate, from the first FULL row to 61.0 s |
| BASE | Drain from FULL at 63 s | **R** | episode end in 61.0–65.0 s |
| BASE | Not FULL after the drain, including Foam at the top from about 65 s | R2 | no candidate-only FULL row in 65.0–90.0 s |
| Accum | EMPTY at 0 s, never Oil-FULL; Foam at the top from about 28 s | **N** | N1/N2 over 0–90 s |

- **Window:** 0–90 s, as proposed in question 3. The user confirmed the initial
  states and did not object to the window. The timeline ends at about 85 s,
  and 90–260 s stays unseen.
- **Timing:** the approximate windows are scored first. A miss within 2 s
  outside a window triggers a Windows review of only 22–27 s or 61–65 s.
- **Not yet known:** the recording's SHA-256 and decoded frame count, and the
  Recipe's hash and ellipses. The run records them first.

**Request (2026-10-22):** one Windows request in the
[procedure](../../40-operations/s11-current-windows-field-qualification.md#spl4-top-exit-promotion-evidence),
authorized by the user.
- **Code head:** `933ff49`, which adds the E1/E2 report bands and a ROI overlay
  mode to the comparison runner. Detector code is unchanged since `cba4067`.
  The agent checks five module SHA-256 values first.
- **Overlay first:** `--roi-overlay` draws each Glass's ellipse, effective mask
  and 27 % band end on frames at 0 s (empty) and 55 s (full, clear again). It also writes the video and
  Recipe identities, and the user confirms the ellipses before any run.
  - Regenerating the sample5/sample7 sheet with the shared drawing code
    reproduces `roi-review.png`, `roi-inputs.json` and both Recipes byte for
    byte.
  - On local `sample5.mp4` the mode wrote the expected size, fps, frame count
    and band end (Y474.78).
- **Two runs:** reference IFO v2 and candidate IFO v2 + top-exit v3; 0–90 s,
  2 fps, FULL debug, both Glasses confirmed EMPTY.
- **Returned tables:** P, N and U map to the frozen checks; Q is the top-exit
  trace at 20–28 s and 59–67 s; S holds reference values.
- **Also in the request:** the C census on the saved ⑩ bundle and the E1/E2
  check on the candidate's report.
- **First attempt:** stopped at step 0-2's size check, as designed, before
  any detector run. The expected size was corrected to 53,165,455 bytes, and
  the agent resumes at step 0-3 with the overlay it already made.

## SPL#4 receipt — 2026-10-22

Relayed by the user from the Windows agent (OCR). Judged against the
[SPL#4 entry conditions](../../30-validation/s11-physical-interface-evidence-repair-validation.md#top-exit-v3-promotion-acceptance--2026-10-22)
frozen before the run.

**Identity:**
- **Runs:** reference `71f604ca-57a6-4a72-8938-5064b126b179` (`SPL4_A_ref`);
  candidate `05985b7a-acee-4091-a876-95e46cb1f6ac` (`SPL4_A_top_exit_v3`).
- **Resolver versions:** reference
  `r22-oil-ownership-evidence-replacement-v1+initial-full-observation-v2`;
  candidate the same plus `+top-exit-full-v3`.
- **Source:** the agent reported all five module hashes as matching. The relayed
  `graph_renderer.py` value reads `…2502d0cd…` where the expected value has
  `…2502d8cd…`; read as an OCR slip, since the agent reported a match.
- **Video:** SHA-256 `9f494a6f…f918010a8`, 53,165,455 bytes, 30.0 fps,
  7,800 frames, 260.0 s, 1920×1080.
- **Recipe:** `sample4_test_artifact_R22.oilrecipe`, SHA-256
  `8eb2c2fc…13217dc8f00`, unchanged.

  | Glass | Ellipse (cx, cy, rx, ry) | Margin | Artifact templates | Band end |
  |---|---|---|---|---|
  | BASE | 606.74, 562.93, 63.71, 271.70 | 0.08 | 13 | Y437.95 |
  | Accum | 1418.26, 415.62, 150.17, 154.72 | 0.08 | 9 | Y344.45 |

  The user confirmed on the overlay that both ellipses cover the vessel
  interior.
- **Rows:** 181 per Glass in each run; pairing clean (no duplicate, missing or
  timestamp mismatch); 362 debug records per run.

**Deviations and receipt notes:**
- **Compressor start:** the request said none, but the Recipe's RECOVERY
  judgment requires one (`READY_COMPRESSOR`). The user approved 10.0 s for
  both runs. It feeds only the judgment, the `COMPRESSOR_START` event and debug
  capture marks, not detection. The request missed this.
- **Deleted attempts:** two earlier attempt bundles (13:57:31, 13:59:01) were
  deleted at the user's instruction. Their cause and content were not reported.
- **A mislabelled total:** the "whole BASE" `T.reason` distribution sums to
  362, the record count of both Glasses, so it is read as both Glasses.

**Results:**

| Glass | Check | Observed | Verdict |
|---|---|---|---|
| BASE | P1: first FULL in 22.0–27.0 s | no top-exit FULL row in 0–90 s | **FAIL** |
| BASE | P2: no candidate-only FULL before 22.0 s | none | PASS |
| BASE | P3: FULL or D2b UNKNOWN to 61.0 s, no Oil coordinate | no episode; the reviewed FULL interval has UNKNOWN and numeric Oil rows (27.5 s Y721, 28.0 s Y704) | **FAIL** |
| BASE | P4: rows before closure equal | no closure; all 181 rows equal | PASS (vacuous) |
| BASE | R1: episode end in 61.0–65.0 s | no episode | NOT EVALUATED |
| BASE | R2: no candidate-only FULL in 65.0–90.0 s | none | PASS (vacuous) |
| Accum | N1: no top-exit FULL row | 0 | PASS |
| Accum | N2: rows, events, report card equal | 0 differing rows; 52 = 52 events; card equal | PASS |
| Both | U1: rows equal outside pending/episode | 0 differing rows in either Glass | PASS |

- **Near-miss rule:** not applicable; there was no transition to time.
- **No pending ever:** neither Glass has a `T.confirmation` key. Three
  disappearance evaluations ended `TOP_EXIT_NOT_PROVEN`.

**Verdict: SPL#4 FAILS the P class; R is not evaluated; N and U pass.** The
candidate equals the reference in every row: top-exit added nothing and changed
nothing. The minimum evidence (one unseen positive, one release) is not met,
and a failure blocks the default under the decision rule. Top-exit v3 stays
default OFF. No tuning or rule change follows; a new rule would be a new version
with its own freeze.

**First harmful stage (BASE): before the top-exit closure.**
- **The witness ended low:** the owner held Y801–802 through 21.0 s, near the
  glass bottom (band end Y437.95). At 21.5 s it vanished there:
  `TOP_EXIT_NOT_PROVEN`, with `independent_anchor`, `upward_progress`,
  `recent_upward_direction` and `top_band_reached` false.
- **A new owner, unqualified:** at 22.0 s a Y756 owner was selected,
  `UNQUALIFIED_SELECTED_OWNER`.
- **Every frame opposed during the rise:** 22.5–27.0 s are all
  `CURRENT_EVIDENCE_RESET` with `ambiguity_clear` and `no_current_interface`
  false. An interface existed, but each frame was opposed. The rows published
  UNKNOWN and the witness reset on every frame. The user's review puts the fast
  rise, Foam from 23 s and FULL at 24–25 s inside this span, so the level
  crossed the band unseen.
- **Source, resolved by the
  [follow-up](#spl4-opposition-follow-up-receipt--2026-10-22):** the fill
  lifecycle (`OIL-PHASE-FILL`), reason `FILL_OWNER_AMBIGUOUS`, between two low
  owners. The real level was never admitted as an owner (inference).
- **The known limit is now a demonstrated gap:** on an EMPTY-start, fast
  Foam + Oil fill, top-exit acting alone produced no FULL.
- **Follow-up (user, 2026-10-22):** a read-only
  [opposition follow-up](../../40-operations/s11-current-windows-field-qualification.md#spl4-opposition-follow-up)
  on the saved bundles names the opposing source and completes the Accum
  census.

**Reported, not scored:**
- **Production default, both arms:** numeric Oil inside the reviewed FULL
  interval (27.5 s Y721, 28.0 s Y704), far beyond C1's ±5 % (±27 px) of a full
  glass. The full count in 25–63 s is not in the receipt. BASE 59–67 s is
  UNKNOWN throughout.
- **Accum:** one `EMPTY_NO_INTERFACE` row at 24.5 s in both arms while fluid
  is present. A one-sample false EMPTY is below C5's two-sample A threshold.
- **Reconstruction:** both Glasses UNRESOLVED (`AUTHORITATIVE_FOAM`) in both
  arms; effective coverage BASE 18.2 %, Accum 12.7 %; REVIEW_REQUIRED.

**C census (saved ⑩ bundle, read-only):**

| Glass | Band end | Blank rows | With an `INCOMPATIBLE_BRANCH` candidate | Runs of ≥ 2 inside the band |
|---|---|---:|---:|---|
| BASE | Y420.10 | 185 | 4 | 0 |
| Accum | Y213.50 | 565 | 64 | 4 (after regrouping all 64 rows in the follow-up) |

- **BASE:** 608.98 s (Y404), 610.99 s (Y409), 617.99 s (Y387) and 663.00 s (Y393)
  are single rows, each inside the band. 663.0 s is the review-004 blank that
  v3's next-frame confirmation cancelled in ⑩. v3 already covers this pattern.
- **Accum grouping corrected:** the agent reported 64 single-row runs, but its
  own timestamps are consecutive 2-fps samples. SPL#1's steps are 0.4588 or
  0.5005 s, never exactly 0.5 s. Regrouping the 30 listed rows:
  - 518.5–523.0 s (10 rows), 524.0–525.0 s (3), 529.5–530.5 s (3) and
    532.5–534.0 s (4) stay below the band, with minimum Y307–332;
  - **679.5–680.5 s (3 rows, minimum Y208) and 681.5–682.5 s (3 rows, Y210)
    reach the band.**
  - The [follow-up](#spl4-opposition-follow-up-receipt--2026-10-22) listed all
    64 rows (to 736.5 s) and completes this census.
- **Meaning:** multi-frame blanks inside the band, the precondition of the
  two-frame-blank risk, do occur on real data (Accum, ⑩). Top-exit did not
  close there in ⑩, because no qualifying witness preceded them.

**E1/E2 on Windows (candidate report):**
- **E1 confirmed:** the combined graph shows the strip with rows BASE then
  Accum, and each row matches its detail graph.
- **E2 not exercised:** no FULL, EMPTY or reconstruction band had width in this
  run; only the grey UNKNOWN bands rendered.
- **Legend defect:** the single-sample Accum EMPTY run (24.5 s) has zero width.
  It is invisible, yet `EMPTY 판정` appears in the strip legend. This is the
  zero-width limit named in the E1/E2 verification, now seen as a misleading
  legend entry.

## SPL#4 opposition follow-up receipt — 2026-10-22

Read-only, relayed by OCR, from the
[follow-up request](../../40-operations/s11-current-windows-field-qualification.md#spl4-opposition-follow-up).
- **SPL#4 candidate bundle:** run `05985b7a-…`; 181 records per Glass (BASE
  `9c74a762…`, Accum `cfef5bad…`).
- **⑩ bundle:** run `84526e04-b989-437e-9790-668834771e50`; 601 records per
  Glass.

Both identities match the earlier receipts.

**Which source opposed BASE 22.5–27.0 s: the fill lifecycle (`OIL-PHASE-FILL`),
reason `FILL_OWNER_AMBIGUOUS`.**
- **Every record in 22.5–27.0 s:** phase `filling`, reason
  `FILL_OWNER_AMBIGUOUS`, ambiguity flag 1, an empty owner chain, no allowed
  tracklet, and all four path stages unknown.
- **What the reason means:** the lifecycle sets it when more than one dynamic
  fill owner exists. It then empties the allowed set, so the frame publishes
  UNKNOWN.
- **Identity contradictions are not the source:** `non_nearest_ordered_lower`
  appears on non-selected candidates in only 4 of the 10 frames (23.0, 23.5,
  25.0, 26.5 s).
- **Against the readings fixed beforehand:** this is not the anticipated
  `FILL_CHAIN_AMBIGUOUS`. It is another `OIL-PHASE-FILL` branch, recorded as
  it is.
- **Around it:** 21.0–22.0 s and 27.5–28.0 s are `FILL_MOTION_OWNER`, each with
  one owner.

**The two owners and the other candidates (table E, 22.0–24.5 s):**
- **Two owners, both low:**
  - `oil-tracklet:000025:0018`: continuing, admitted, upward; Y781–785 at
    22.5–23.0 s and Y756–766 at 23.5–24.0 s.
  - `oil-tracklet:000042:0035`: provisional, admitted, upward; Y742–769.
  - The chain handed off 0018 → 0035 at 22.0 s (selected Y756), and 0018
    reappeared at 22.5 s.
- **Higher candidates, never admitted:** Y463 (`…0037`) at 22.5 s; Y462, Y534
  and Y651–660 (`…0038`–`…0040`) at 24.5 s. Each is a new provisional tracklet
  with `INSUFFICIENT_NET_PROGRESS` and direction 0.
- **A candidate fixed near the top:** Y323–325 (`…0034`) from 22.0 s, before the
  glass was full; never admitted.
- **Inference, not verified:** the user's review places the fast rise here, so
  the higher candidates are the likelier level positions.
  - A rise of about 500 px in 3–4 s is about 70 px per 2 fps sample.
  - Each frame then starts a new tracklet that never accumulates progress.
  - The BASE `temporal_max_jump_px` and a frame review would confirm it.

**Refined first harmful stage:** admission at `OIL-TRACKLET` during the fast
rise (inference). The level never became an admitted owner while two low
owners kept fill ownership. `OIL-PHASE-FILL` then failed closed between them
(UNKNOWN). Top-exit needs an owner in the band, so it had nothing to act on.

**The three failed disappearance evaluations (table F) all refused low
witnesses, as designed:**
- **19.0 s:** two rows at Y793–795; too few observations, among other false
  keys.
- **21.5 s:** four rows at Y799–802; no anchor, no upward progress or
  direction, not in the band.
- **34.5 s:** five rows of owner 0018 at Y739→720; `independent_anchor`,
  `recent_upward_direction` and `top_band_reached` false.

**Wrong-target numeric Oil in the reviewed FULL interval (table G, production
default):**
- **Rows:** 14, all in 27.5–34.0 s, Y704–739, from the re-adopted owner 0018.
- **States:** the fill state alternates FILLING, DRAINING and PARTIAL.
- **Class:** against a full glass this is far beyond C1's ±27 px for 14
  consecutive samples, so it is A-class false output.
- **After it:** BASE is UNKNOWN from 34.5 to 63 s.

**⑩ Accum census, complete (table H regrouped at adjacent 2 fps samples):**
- **Runs:** the 64 rows form 25 runs.
- **Inside the band (Y ≤ 213.50):** four 3-row runs, at 679.5–680.5,
  681.5–682.5, 698.5–699.5 and 700.5–701.5 s, plus a single row at 697.5 s.
- **No witness at any row:** each row is `CURRENT_EVIDENCE_RESET`,
  `CURRENT_INTERFACE_OR_STATE_RESET` or `NO_TOP_EXIT_WITNESS` with an empty
  witness, so no closure could start there.
- **Meaning:** the two-frame-blank precondition occurred four times on real
  Accum data, never after an active witness. The risk stays a named limit; this
  evidence does not call for the option C repair.

**What it decides:** nothing is tuned or changed.
- **FULL on fast fills:** the obstacle is upstream of top-exit. The level must
  be tracked as an owner, or FULL must come from evidence that needs no owner.
- **A separate defect:** the stale-owner numeric Oil at 27.5–34.0 s is a
  production-default false output on an unseen recording.
- Both are for the user to schedule.
- **Later (2026-10-22):** the local fills reproduce the fill-owner ambiguity
  and, on sample5, the stale-owner wrong target, but not the unadmitted fast
  rise ([FOA-1](../../50-diagnostics/s11/2026-10-22-fill-owner-ambiguity-local.md)).

## Detector Governance

- Logic-map nodes: `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-PROJECTION`, `PUBLICATION-PROVENANCE`
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F08`, `S11-F10`
- First harmful stage: local negatives, none observed (no witness or pending closure; the closure stage is NOT_EVALUATED on real video; the sample5 wrong-target Oil rows are a selection observation outside these criteria). SPL#4 BASE: before the top-exit closure. The follow-up names `OIL-PHASE-FILL` `FILL_OWNER_AMBIGUOUS` in 22.5–27.0 s, between two low admitted owners. Upstream of it, the fast-rising level never became an admitted `OIL-TRACKLET` owner (inference: new provisional tracklets each frame with `INSUFFICIENT_NET_PROGRESS`). So no witness reached the band. The later re-adopted low owner published 14 wrong-target numeric rows (27.5–34.0 s) in both arms.
- Existing feature coverage: reuses the initial-FULL/top-exit comparison runner. Its extension adds frozen empty-fill Recipes, an EMPTY initial state and an N1/N2 summary. Also reused: the IFO v2 and top-exit v3 options, production default detector settings and the four existing control Recipes. The EMPTY-initial path, where IFO is inactive, is exercised for the first time. Windows "sample4" is a user visual timeline only.
- Execution scope: two local managed runs (`cba4067`, `60d6a9d`) over six controls at 2 fps with debug NONE, plus a frozen-ROI run before them. No Windows execution, private media, human review beyond the user's confirmations, tuning or post-result rule change. sample5's window end was corrected before any sample5 output existed. SPL#4 is recorded from the user's visual timeline and answers only; its windows were frozen before any detector run on it. The six controls were rerun at `933ff49` (run 003) with identical output. On Windows, one user-forwarded request at `933ff49`: two SPL#4 runs (0–90 s, 2 fps, FULL debug, compressor start 10.0 s by the user's approval), the user's overlay check, the read-only C census on the saved ⑩ bundle and an E1/E2 look; relayed by OCR and judged against the frozen entry conditions. A read-only follow-up then read the saved SPL#4 candidate and ⑩ bundles (no run). No tuning or post-result rule change.
- Logic-map impact: NONE — evidence only; detector code and owners are unchanged, and the runner is diagnostics.
- Failure-registry impact: NONE — no new mechanism or failure. The unexercised closure is a named limit, not a result. The SPL#4 findings fit existing entries: the level is not admitted (F02/F04), fill ownership fails closed without an exit (F05/F08), and a stale owner publishes wrong-target Oil (F04).
