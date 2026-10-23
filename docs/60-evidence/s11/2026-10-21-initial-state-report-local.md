# Initial-state continuing-run rule and report bands — local implementation

**Status:** IMPLEMENTED / LOCAL VERIFICATION PASS / Windows report
confirmation **PASS** (one run, 2026-10-22,
[receipt](#windows-report-confirmation--2026-10-22)). These changes are
downstream of the detector; detector output and the top-exit v3 option are
unchanged. O2 OPEN / FIELD FAIL and review-006 pending are unchanged. Current
authority is the [Work Plan](../../00-project/work-plan.md).

**2026-10-22 addition:** the combined-graph state strip and source band
patterns (E1/E2) are IMPLEMENTED / LOCAL VERIFICATION PASS
([section](#combined-graph-strip-and-band-patterns-e1e2--2026-10-22)). On
Windows (SPL#4 run) E1 is confirmed and E2 was not exercised; a zero-width
band added a legend entry. That defect is fixed by
[per-sample band cells](#per-sample-band-cells--2026-10-22), IMPLEMENTED /
LOCAL VERIFICATION PASS, including the dot pattern on a local CLI report.
**Windows (step 7, 2026-10-23):** band cells, E2 and the first-catch guard
confirmed on the SPL1_B_ref report
([receipt](2026-10-23-step7-windows-receipt.md#report-checks-spl1_b_ref)).

**2026-10-22 addition:** the
[first-catch position guard](#first-catch-position-guard-l2--2026-10-22)
(E3, L2) is IMPLEMENTED / LOCAL VERIFICATION PASS. It amends the continuing-run
rule below; the next Windows report will show it in use.

## What was built

The rules were frozen at `67f1484` before any code change, from the
[⑩ report receipt](2026-10-21-top-exit-v3-local.md#report-and-judgment-receipt--2026-10-21)
and the user's decisions:
- **B, [continuing-run rule](../../20-architecture/initial-state-retrospective-reconstruction-architecture.md#modern-stream-continuing-run-rule--2026-10-21)**
  (`initial_state_reconstruction.py`):
  - **Scope:** modern streams only; legacy R7 anchor streams keep their path.
  - **Barriers:** the sequence resolvers' ordinary-UNKNOWN markers are no longer
    barriers. Hard failures and published Foam still are.
  - **Run:** it starts at the first accepted boundary and ends at a step above
    `temporal_max_jump_px` or at a barrier.
  - **Decisive move:** two consecutive boundaries beyond the existing tolerance
    on the same side. If that move is toward the prior's direction the result is
    ACCEPTED; if it goes the other way, CONFLICT. Otherwise UNRESOLVED.
  - **Topology:** stays provenance only.
  - **Provenance:** `initial_state_retrospective_v2`, with three evidence frames.
- **A, [state bands](../../20-architecture/s11-report-context-presentation-design.md#fullempty-bands-and-judgment-reason--2026-10-21)**
  (`graph_renderer.py`):
  - every FULL/EMPTY band is drawn at alpha 0.09 and labelled by source:
    `FULL 판정` / `EMPTY 판정`, `초기 상태 재구성 (…)` or
    `확정 초기 상태 유지 가정 (…)`;
  - the combined graph is unchanged.
- **C, judgment reason** (`report_presentation.py`):
  - `판정 안내` appends plain-Korean reasons for the known note forms;
  - unknown forms add nothing, and the raw English note is never shown.
- **Logic map:** the `RESULT-PRESENTATION` row records A and C.

**Module SHA-256:**

| Module | SHA-256 |
|---|---|
| `initial_state_reconstruction.py` | `9fd04d25a10860fb5ba506311170209e71a9cfb09803f6166a1de5a4f93e1eed` |
| `graph_renderer.py` | `a4776e06ff95f0ad44acd308f18e417d2645ffb2189ddac11ff870dd1217ebf5` |
| `report_presentation.py` | `6a1b0b512f8008bda71de4ae6bcb452e0c7a9295753b4edff06f446a10d6469f` |
| `oil_top_exit_full.py` | unchanged, `10dd3605…6f77d` |

## Verification

- **Reconstruction tests:** 51 passed
  (`tests/test_initial_state_retrospective_reconstruction.py`).
  - **Fixtures rewritten:** the modern fixtures now show a confirmed move with a
    third boundary. Under the frozen rule a single beyond boundary is not
    decisive, so evidence becomes three frames.
  - **New cases:**
    - ordinary UNKNOWN markers do not block;
    - hard failures inside the run do (frame unavailable, fog/glare, detection
      lost, no-interface evidence unavailable);
    - one beyond, stationary and end-after-one stay unresolved;
    - a fall followed by a rise, and the EMPTY mirror, are accepted;
    - a first move against the prior is a conflict;
    - a step above the jump limit stays unresolved.
  - **⑩ BASE shape** (the received Y values for 548.5–568.0 s, the received
    geometry and the 32 px limit): ACCEPTED, with evidence at the first boundary
    and Y374/375. Relative position 0.196.
  - **⑩ Accum shape:** UNRESOLVED, both with a Foam row before the first boundary
    (`AUTHORITATIVE_FOAM`) and without it (the 33 px step).
- **Mutation checks:**
  - treating the ordinary-UNKNOWN markers as barriers again fails 12 cases;
  - deciding on the first beyond boundary fails 9 cases.

  The code was restored before the suite run.
- **Renderer and presentation tests:**
  - **State bands:** a reconstructed prefix is labelled `초기 상태 재구성 (FULL)`
    and a top-exit FULL block `FULL 판정`, both at alpha 0.09. The existing hold
    label test passes.
  - **Judgment guidance:** coverage, retrospective provenance, a violation
    duration with a conflict, and an unknown note all produce the expected
    guidance without the raw English text.
- **Full unit suite** (`tests`, excluding `tests/diagnostics`): 3,821 passed,
  12 skipped. The skips are the quarantined sample3 corpus; they were not
  bypassed.
- **Rendered check:**
  - **Input:** a scratch script built a ⑩-like BASE sequence from the receipt:
    - 137 UNKNOWN rows with the R17 markers;
    - the received Y values for 548.5–581.5 s, with their UNKNOWN gaps;
    - a 30-row top-exit FULL block.
  - **Outcome assembler:** ACCEPTED, with the prefix at 479.98–547.98 s and the
    decisive move at 567.48/567.98 s. `HOLD_ABOVE_ZERO` then passes on the
    level.
  - **Rendered detail graph:** both labelled bands are visible.

  This is a visual check of the code path. The synthetic sequence is not ⑩'s
  output and creates no evidence about its later rows.

## Limits

- **Windows: one confirmation run, PASS**
  ([below](#windows-report-confirmation--2026-10-22)). The ⑩ bundle's own
  judgment and report stay as written.
- **The Accum protection is incidental.** It comes from the Foam barrier and the
  continuity bound, not from direction. A late first catch with neither would be
  accepted. On Windows the Foam barrier acted. (2026-10-22: the
  [first-catch position guard](#first-catch-position-guard-l2--2026-10-22)
  now refuses such a catch.)
- **No visual difference between sources.** Bands from different sources share
  one colour and emphasis; only the legend tells them apart.
- **Combined graph unchanged.** It still draws no state bands.

## Windows report confirmation — 2026-10-22

**RECEIVED / PASS against the expectation written before the run.** The user
relayed the Windows agent's return for the
[report confirmation request](../../40-operations/s11-current-windows-field-qualification.md#report-confirmation-run)
by OCR transcription. This is transferred evidence: no private file was
inspected on the Mac. The expectation and failure conditions were written in
that request before the run, and nothing was changed after the return.

**Identity and run:**
- **Run:** `ddc36bbc-945e-47e4-810e-d911c7d8e2d7`, run name
  `22-3_initial_ON_v2_top_exit_v3_report_v2`. It is a new run: ⑩ is
  `84526e04-…` and ④ is `a9ccece3-…`.
- **Module SHA-256:** the four values were checked on Windows before the run and
  reported as matching. Each equals the requested value and the `139ba87` blob,
  checked on the Mac; `src` is unchanged from `139ba87` to the current head.
  Between ⑩'s source and `139ba87`, `src` changed only in the three report-side
  modules, so the four values cover every source difference from ⑩ plus the
  top-exit module.
- **Version:** sequence
  `r22-oil-ownership-evidence-replacement-v1+initial-full-observation-v2+top-exit-full-v3`
  on both Glasses, as in ⑩. The detector version was not requested.
- **Path:** a programmatic runner equivalent to the CLI headless analyze path,
  kept outside the repository
  (`C:\Users\teeoo.kim\AppData\Local\Temp\oil_s11_report_v2_runner.py`).
  - Detector: `OpenCvPhaseDetector(initial_full_observation=True, top_exit_full=True)`,
    debug trace FULL.
  - Runtime: the existing global Windows Python (cv2 4.13.0) with "the
    editable-installed source repository".
  - Duration: about 20 minutes.
- **Inputs:** reported equal to ⑩'s `session.json`: 480.0–780.0 s, 2.0 fps,
  compressor start 485.0 s, BASE `FULL_NO_INTERFACE`, Accum
  `EMPTY_NO_INTERFACE`.
  - Video as transcribed:
    `C:\0.Coding\oil_level_tracker-R22-3\sample\SPl#1_Heating_coldstart.mp4`.
  - The identical tracking data below corroborates the same video and Recipe.
- **Bundle:** `C:\0.Coding\2.Reference\Oil level tracker\0.Windows_diagnostic\bundle\oil_level_analysis_22-3_initial_ON_v2_top_exit_v3_report_v2_20261022_084509`
  (about 2 GB with the debug trace), kept on Windows.

**Receipt notes (values kept as reported):**
- **Circled labels:** the transcription writes "0" where the request says ⑩:
  the diff base, `session.json` and the closing note. Content fixes the diff
  base as ⑩:
  - BASE has no differing rows, and this run's BASE FULL starts at 674.007 s;
  - ④ has no FULL rows, and ⑨'s FULL starts at 663.0 s.
- **Third evidence frame:** transcribed as `13610`, with timestamp
  567.9840833 s.
  - At the video's 24000/1001 fps that timestamp is exactly f13618.
  - f13610 would be 567.650 s, which is not a 2 fps sample.

  This record reads it as f13618, an OCR digit error.
- **Source folder:** the field returned the video path, not the source folder,
  and the import path was not reported; ⑩ named a fresh ZIP extract. Two things
  tie the executed code to the hashed modules:
  - the agent's pre-run hash check;
  - behavior that exists only from `139ba87`: provenance
    `initial_state_retrospective_v2` with its reason text, both new legend
    labels and the new guidance sentence.

  Named unknown: the exact import path.
- **Overall status:** not requested and not returned. Under the unchanged
  `_overall_result` rule (`analysis_pipeline.py`), BASE `PASS` with Accum
  `REVIEW_REQUIRED` gives `REVIEW_REQUIRED`.
- **The paragraph quoted after BASE's `판정 안내`** is, by inference, Accum's
  movement summary. The template closes each Glass card with `판정 안내` and
  opens the next card with its movement summary.
  - Its values fit Accum: observations 669.5–724.0 s, all below zero, inside
    ⑩'s Accum Oil intervals.
  - They do not fit BASE, whose first observation is 548.5 s and whose minimum
    is +113.6 px.

  It is outside the expectation and is not used in the verdict.

### Checks against the written expectation

| Item | Written before the run | Received | Verdict |
|---|---|---|---|
| Tracking data | Equals ⑩ in every compared field | 1,202 / 1,202 rows with the same `(glass_id, frame_index)` keys; 0 differing rows in BASE and in Accum over the seven fields | PASS |
| BASE reconstruction | `ACCEPTED`, `initial_state_retrospective_v2`, 479.98–548.006 s | `ACCEPTED`, `initial_state_retrospective_v2`, 479.9795–548.0058 s (f11508–f13139), no barriers. The reason is the code's accepted continuing-run text, ending "edge-compatible." | PASS |
| BASE evidence | f13151 / f13606 / f13618 (548.51 / 567.48 / 567.98 s) | 548.5063 / 567.4836 / 567.9841 s; frames 13151 / 13606 / "13610" | PASS; the third frame is read from its timestamp |
| BASE coverage | Effective 553/601 ≈ 0.920; observed 0.692 | 0.9201331 (= 553/601); 0.6921797 (= 416/601) | PASS |
| BASE judgment | Decided by the level; the note ends with `provenance=retrospective_initial_state` | `PASS`. `JUDGMENT_PASS` note: "Oil level remained above zero within configured tolerance.; provenance=retrospective_initial_state". Minimum valid smoothed level +113.603 px at f15632 (651.98 s) | PASS, decided by the level |
| BASE `판정 안내` | The level sentence plus `첫 검출 이전 구간은 확정한 초기 상태로 재구성해 판정에 포함했습니다.` | "설정된 판정 기준을 충족했습니다. 유면이 허용 범위 안에서 기준선 위를 유지했습니다. 첫 검출 이전 구간은 확정한 초기 상태로 재구성해 판정에 포함했습니다." | PASS |
| BASE graph | Legend `초기 상태 재구성 (FULL)` and `FULL 판정`; blue bands at 480–548 s and 674–780 s | Both labels in the legend; both bands: yes | PASS |
| Accum | `UNRESOLVED`, `AUTHORITATIVE_FOAM`; `REVIEW_REQUIRED` at 6.0 %; the guidance names 6.0 % / 70.0 % | `UNRESOLVED` (`initial_state_retrospective_v2`), barrier `AUTHORITATIVE_FOAM`, "Inference barrier before sufficient positive evidence."; `REVIEW_REQUIRED`, coverage 0.0599 (= 36/601); "…확인한 시점이 전체의 6.0%로, 설정 기준 70.0%보다 적습니다." | PASS |
| Overall | `REVIEW_REQUIRED`, because of Accum | Not returned; derived `REVIEW_REQUIRED` | Consistent; not observed |

**Failure conditions: none occurred.**
- **Tracking rows:** no difference.
- **BASE:** accepted, with the written interval and evidence.
- **Accum:** not accepted.
- **Raw English note text:** none in the returned report text. The English notes
  appear only in `events.csv` and `retrospective_interpretation.json`. The full
  HTML was not returned, so this covers the two `판정 안내` blocks and the
  paragraph after BASE's.
- **Bands and labels:** none missing.

**Verdict: PASS.** On real Windows output:
- the continuing-run rule reconstructs BASE's FULL prefix and leaves Accum
  unresolved;
- BASE moves from ⑩'s coverage-limited `REVIEW_REQUIRED` (69.2 %) to `PASS`,
  decided by its level;
- both band sources are labelled, and `판정 안내` gives plain Korean reasons;
- detector output is unchanged.

This confirms a downstream report and judgment change on one video. It is not
field qualification; FIELD FAIL / O2 OPEN are unchanged.

### Event and graph detail

`FULL_NO_INTERFACE_START` rows (all BASE):

| Start (s) | End (s) | Frames | Note |
|---|---|---|---|
| 479.9795 | 548.0058 | 11508–13139 | `provenance=retrospective_initial_state` |
| 674.0067 | 768.0173 | 16160–18414 | empty |
| 772.4800 | 773.9815 | 18521–18557 | empty |
| 774.9825 | 779.9875 | 18581–18701 | empty |

- **Detector FULL blocks:** ⑩'s nine D2b fail-closed UNKNOWN rows (768.5–772.0 s
  and 774.5 s) split them into three.
- **Legend, as returned:** 관측 유면 / 관측 공백 연결 / 기준선 / 분석 영역 위쪽 경계 /
  분석 영역 아래쪽 경계 / 초기 상태 재구성 (FULL) / 직접 유면 확인 어려움 / FULL 판정 /
  관측 최저 유면 / 관측 최고 유면.
- **Band extent:** the agent describes the later band as "about 675–760 s plus
  thin bands near 765–775 s". This is an eye reading of the PNG.
  `_state_bands` draws one span per contiguous FULL run, which gives the three
  detector intervals above. The reading does not affect the yes/no check.
- **Reviewed truth (consistency only):** the reconstructed 479.98–548.01 s lies
  inside `WS1-BASE-FULL-PREFIX` (480 to about 550 s). The BASE minimum at
  651.98 s falls at the reviewed drain end (about 652 s). Neither the detector
  output nor the reconstruction is truth.
- **Segment accounting:** the tracking data equals ⑩'s, so ⑩'s
  [Table R](2026-10-21-top-exit-v3-local.md#table-r-condensed) still holds. This
  run adds only the reconstructed prefix, the judgment and the report.

### Limits of this receipt

- **One video:** BASE exercises one accepted shape (a fall as the first decisive
  move) and Accum the Foam barrier. CONFLICT, EMPTY-direction acceptance and the
  jump-limit end are covered only by unit tests.
- **Accum protection:** a row with a Foam state or Foam evidence and no Oil
  boundary, before Accum's first accepted boundary, stopped the reconstruction.
  The second protection seen locally, a 33 px step above the jump limit, was not
  reached. A change to Accum Foam publication before that boundary could change
  this outcome.
  - **Named unknown:** the barrier row's frame was not requested. The report's
    first Accum observation is 669.5 s. If no earlier valid numeric row exists
    (the movement summary skips direction-unconfirmed rows), the Foam row lies
    before 669.5 s. That is earlier than the reviewed Accum Foam interval
    (672–680 s), so the row would be a Foam publication the truth does not
    support.
- **Judgment scope:** BASE `PASS` is the configured `HOLD_ABOVE_ZERO` criterion
  applied to detector output. It is not reviewed-truth or field acceptance.
- **Identity:** the import path is unreported, the overall status is derived,
  and one evidence frame is read from its timestamp.
- **Report:** only the requested strings and the legend were returned; the full
  HTML was not inspected.

## Combined-graph strip and band patterns (E1/E2) — 2026-10-22

**Status: IMPLEMENTED / LOCAL VERIFICATION PASS; on Windows E1 CONFIRMED;
E2 CONFIRMED in step 7 (2026-10-23): the reconstruction band is hatched and
the detector FULL band solid
([receipt](2026-10-23-step7-windows-receipt.md#report-checks-spl1_b_ref)).** Frozen at `db83c59` in the
[report design](../../20-architecture/s11-report-context-presentation-design.md#combined-graph-state-strip-and-source-patterns--2026-10-22)
before any code change.
- **Windows (SPL#4 candidate report, 2026-10-22):** the strip rendered with
  rows BASE then Accum, each matching its detail graph. Only grey UNKNOWN
  bands had width, so no pattern could be compared
  ([receipt](2026-10-22-top-exit-promotion-evidence.md#spl4-receipt--2026-10-22)).
- **Defect seen there:** a single-sample run has zero width, yet its label
  enters the legend (`EMPTY 판정`, Accum 24.5 s).

**What changed (`graph_renderer.py` only):**
- **E2, both graphs:** each FULL/EMPTY band keeps its state colour and draws
  its source as a pattern.
  - Solid for the detector, top-exit FULL included; `///` hatching for an
    accepted reconstruction; dots for the all-missing hold.
  - The detail graph keeps alpha 0.09 (UNKNOWN 0.065). Hatching uses the state
    colour at alpha 0.5, with no outline.
- **E1, combined graph:** when any Glass has a band, a strip sits under the
  lines.
  - One row per Glass, in result order, labelled with its name.
  - Each row draws the same runs as that Glass's detail graph, at three times
    the fill alpha. The strip legend sits under the figure.
  - Without any band, the combined graph keeps its earlier single-axes layout.
- **Shared runs:** one helper builds the contiguous (start, end, state, source)
  runs for both graphs, so the strip cannot disagree with the detail graph.

**Verification:**
- **Renderer tests, 6 pass:**
  - the detail graph draws a reconstructed FULL hatched and a detector FULL
    solid, both at alpha 0.09; the hold draws dots;
  - the combined graph puts every band on the strip and none on the line axes;
    rows follow the result order, each with its Glass's labels and patterns;
  - without a band, the combined figure has one axes and no span.
- **Full suite:** 3,823 passed, 12 skipped (sample3 quarantine).
- **Rendered checks** (scratch, synthetic values):
  - an SPL#4-like pair: BASE reconstructed EMPTY, a rise, top-exit FULL and a
    drain; Accum mostly UNKNOWN;
  - a ⑩-like pair: a reconstructed FULL prefix and a top-exit FULL suffix,
    with an Accum hold;
  - a run with no band.

  Each strip row matches its detail graph, and the no-band run keeps the old
  layout.

**Limits:**
- **Versions:** matplotlib is pinned at ≥3.11 on both platforms. The hatch
  takes the edge colour, which older releases also honour.
- **Single samples:** a one-sample run still has zero width in both graphs, as
  before. Fixed later the same day by
  [per-sample band cells](#per-sample-band-cells--2026-10-22).
- **Not yet seen:** Windows rendering and real data.

## Per-sample band cells — 2026-10-22

**Status: IMPLEMENTED / LOCAL VERIFICATION PASS; Windows CONFIRMED in step 7
(2026-10-23): no legend entry without a visible band
([receipt](2026-10-23-step7-windows-receipt.md#report-checks-spl1_b_ref)).** Frozen at `0b5d234` in the
[report design](../../20-architecture/s11-report-context-presentation-design.md#per-sample-band-cells--2026-10-22)
before any code change. The user chose option A after a scratch rendered
comparison with option B, which drops zero-width runs.

**What changed (`graph_renderer.py`, `_state_band_runs` only):**
- Each sample owns the time halfway to its neighbours, at most 1 s
  (`REPORT_MAX_CONTEXT_GAP_SEC` / 2), and never before the first or after the
  last sample. A run covers its samples' cells.
- A gap over 2 s splits a run and stays blank. A Glass with a single sample
  draws no band.
- Both graphs and the strip read these runs. Grouping, labels, colours,
  patterns and emphasis are unchanged.

**Verification:**
- **Renderer tests, 9 pass (3 new):**
  - cells meet halfway, a numeric sample leaves its own cell blank, and the
    ends stop at the first and last sample;
  - a gap over 2 s leaves 1 s on each side and splits the run; a lone sample
    draws nothing;
  - a one-sample `EMPTY 판정` is drawn 24.25–24.75 s in both the detail graph
    and the strip, and no span has zero width.
- **Mutations:** each new test fails on the previous renderer. Removing the
  gap split or the lone-sample guard fails the gap test.
- **Full suite:** 3,826 passed, 12 skipped (sample3 quarantine).
- **Same as the chosen option:** on all 47 unique local `tracking.csv` files
  (47 Glass, 260 runs), the new runs equal the scratch option A the user saw.
  The largest local sample spacing is 0.534 s, so the gap rule never acted.
- **Production CLI report:** managed run
  `sample/output/s11-band-cells-report-20261022-001` (`summary.json`
  `662046d2…`), at `0b5d234` plus this renderer. Its recorded source hashes
  match the committed files.
  - `oil-tracker-cli analyze` with the production default detector, 2 fps,
    compressor start 0.0 s.
  - **sample4 0–56 s, confirmed UNKNOWN** (the qualification replay
    condition): 6 UNKNOWN bands per graph, the narrowest 0.5 s (one sample).
    The cells sit under the dashed bridge segments.
  - **sample2 0–2 s, confirmed FULL** (the negatives-run stress condition, not
    physical truth): retrospective `ACCEPTED` hold over 0–2 s, drawn with dots
    in both graphs under the legend entry `확정 초기 상태 유지 가정 (FULL)`.
  - In every saved graph no band has zero width, and every legend band entry
    has a drawn band. PASS.

**Limits:**
- **E2 hatching:** no local run examined accepts a reconstruction. In the six
  negatives controls (run 003) sample2 accepts only the hold, and the other
  five end CONFLICT, UNRESOLVED or NOT_APPLICABLE. The `///` pattern is still
  seen only in unit tests and synthetic renders.
- **Long graphs:** one cell can be narrower than a pixel and shows only as a
  faint line.
- **Not yet seen:** Windows rendering.

## First-catch position guard (L2) — 2026-10-22

**Status: IMPLEMENTED / LOCAL VERIFICATION PASS; Windows not yet seen.** The
user chose L2 from
[LCR-1](../../50-diagnostics/s11/2026-10-22-reconstruction-late-catch-review.md#decision--2026-10-22).
The rule and its acceptance were frozen at `875c0f2` before any code change
([architecture](../../20-architecture/initial-state-retrospective-reconstruction-architecture.md#modern-stream-first-catch-position-guard--2026-10-22),
[validation](../../30-validation/initial-state-retrospective-reconstruction-validation.md#first-catch-position-guard--2026-10-22)).

**What changed (`initial_state_reconstruction.py`, modern streams only):**
- **Guard:** after a first decisive move toward the prior, `_late_first_catch`
  checks the first accepted boundary.
  - FULL: relative ≤ 0.32.
  - EMPTY: relative ≥ 0.68, and at most `temporal_max_jump_px` above the
    effective-mask bottom (`center_y + radius_y × (1 − margin_ratio)`, as
    `graph_axis` draws it).
- **Otherwise UNRESOLVED:** no interval. The reason names the position, and the
  evidence is the first boundary plus the decisive pair, as for CONFLICT.
- **Provenance:** every continuing-run outcome records
  `initial_state_retrospective_v3`.
- **Unchanged:** CONFLICT (decided first), barriers, the run, the all-missing
  hold and legacy R7. The renderer, presentation and Result Review read only
  the hold provenance, so v3 needs no consumer change.

**Module SHA-256:**

| File | SHA-256 |
|---|---|
| `initial_state_reconstruction.py` | `eceac0e8b594f3d9aa761b0ad4bbf9ca6b0e75a71b50a8a4542ace10420fd82f` |
| `test_initial_state_retrospective_reconstruction.py` | `100d43357e1eadb40688e790b760b810e8400a65384a5a6e58a616113ef6d42f` |

**Verification:**
- **Before the code:** the new and updated tests ran against the unchanged
  module; 18 failed (late catches accepted, provenance v2).
- **Reconstruction tests:** 64 passed (51 earlier, 13 new). Every validation
  item has a case:
  - **Accepted:** FULL emerging below the mask top and at the band end (Y84,
    0.32); EMPTY 10 px and exactly 32 px above the mask bottom.
  - **Unresolved, with no interval and the decisive evidence:** FULL just below
    the band (0.325), 20 px below it and mid-Glass; EMPTY 33 px up; a standing
    layer 56 px up that later rises.
  - **⑩ Accum without Foam and with a 30 px first step:** UNRESOLVED, first
    catch relative 0.787.
  - **Small Glass** (radius_y 34): an EMPTY catch within one step of the mask
    bottom but above the band is UNRESOLVED; one inside the band is accepted.
  - **Conflict first:** a mid-Glass FULL catch that rises, and a high EMPTY
    catch that falls, stay CONFLICT.
  - **Unchanged:** the ⑩ BASE shape is accepted and the ⑩ Accum shape stays
    unresolved. The R7 mid-Glass case is still accepted under its v1
    provenance.
- **Mutation checks:** scratch pytest plugins replaced the guard; no source
  was edited.
  - Without the guard, 7 cases fail, exactly the late-catch ones.
  - Without the EMPTY band, 1 fails (small Glass).
  - Without the EMPTY step, 3 fail (33 px, the standing layer, Accum).
- **Frozen control:** the reconstruction was replayed on the LCR-1 desk run's
  24 kept local row lists. This was a scratch replay with stdout only and no
  kept output.
  - 8 are identical: the sample2 holds and the sample4 UNKNOWN-prior cases.
  - 16 differ only in provenance, v2 → v3: the base_sample_1 CONFLICTs and
    the UNRESOLVED results of sample4 interior, sample5 and sample7.
  - Status, interval, reason, barriers and evidence are unchanged. PASS.
- **Full suite:** 3,859 passed, 12 skipped (the sample3 quarantine).

**Limits:**
- **No real accepted reconstruction is exercised locally.** None of the kept
  local runs reaches the guard, so its acceptances and refusals are synthetic.
  ⑩ BASE is checked only through its received values.
- **Windows:** the next report shows the rule in use. The step-7 request adds
  the Accum readout (640–672 s rows and the Accum Glass geometry).
- **Accum 480–653 s:** still UNKNOWN, not EMPTY; the guard does not address it.

## Detector Governance

- Logic-map nodes: `RESULT-PRESENTATION`, `PUBLICATION-PROVENANCE`
- Failure-registry entries: `S11-F05`, `S11-F07`, `S11-F09`, `S11-F10`
- First harmful stage: none in the detector. The ⑩ report problems arose downstream of `PUBLICATION-PROVENANCE`: the retrospective owner treated the resolver's ordinary-UNKNOWN marker as a barrier and required a move between the first two boundaries; `RESULT-PRESENTATION` drew FULL bands at alpha 0.035 without labels and gave no judgment reason. Both were fixed at `139ba87`, and the Windows confirmation run passed. The zero-width band seen on Windows (2026-10-22) came from the `RESULT-PRESENTATION` run extent (first to last sample); per-sample cells fix it. The late-catch gap (LCR-1) is in the same downstream owner: the continuing-run rule accepted the prior wherever the first catch lay, and on ⑩ Accum only a false entry Foam (`S11-F07`) and a 33 px step blocked it. The first-catch position guard closes it (2026-10-22).
- Existing feature coverage: the existing confirmed initial state, retrospective projection, `HOLD_ABOVE_ZERO`/`HOLD_BELOW_ZERO` judgment consumption, Recipe `radius_y` tolerance and `temporal_max_jump_px`, and the existing hold band label are reused. Detector output, top-exit v3 and the event, CSV and bundle code are unchanged; RECOVERY still receives observed samples only. The Windows run reported ⑩'s session and detector options, and its tracking data equals ⑩'s; the accepted prefix reached `events.csv` through the existing retrospective event. The first-catch guard reuses the 0.32/0.68 entrance constants, `temporal_max_jump_px` and the Recipe ellipse and `margin_ratio`; it does not read exclusions, and no local Recipe has any.
- Execution scope: locally, unit tests with two mutation checks, the full unit suite and one scratch rendered check built from transferred ⑩ values. On Windows, one user-authorized run under ⑩'s conditions, returned as transferred OCR evidence and judged against the expectation written before it. No private media on the Mac, no human review, tuning or post-result rule change. E1/E2 (2026-10-22): renderer unit tests, the full suite and three scratch rendered checks from synthetic values, then a look at the SPL#4 candidate report's graphs on Windows (relayed by OCR). Band cells (2026-10-22): renderer unit tests with mutation checks, the full suite, a scratch equality check on 47 local `tracking.csv` files and one managed production-CLI run on two local videos; no Windows run. First-catch guard (2026-10-22): reconstruction unit tests with three mutation checks, the full suite, and a scratch stdout-only replay of the LCR-1 desk run's 24 kept local row lists (the frozen control); no detector run, video decode or Windows run.
- Logic-map impact: NONE — this update records the step-7 Windows confirmation (2026-10-23) of the band cells, E2 and the first-catch guard, and changes no code, owner or control flow. The `PUBLICATION-PROVENANCE` row was updated with the first-catch guard (`55726fd`) and the `RESULT-PRESENTATION` row with the band cells (`b49ed07`); the earlier updates (`139ba87`, `5e5c8bc`) match what the runs showed.
- Failure-registry impact: NONE — no detector mechanism changed, and the receipt adds no failure. The rule narrows a downstream F05-shaped risk (a confirmed state hidden by soft UNKNOWN markers) without adding a threshold (F10); report wording still adds no measurement (F09). The first-catch guard narrows an F09/F10-shaped risk (coverage from a prior projected past an unobserved transit) with existing constants only; the false entry Foam is the known F07 class.
