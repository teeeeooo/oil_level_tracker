# Top-exit FULL v2 — local implementation and controls

> **Superseded in place by [top-exit v3](2026-10-21-top-exit-v3-local.md).** The
> v2 code was replaced under the same switch after the ⑨ FAIL recorded below.
> This record is kept unchanged as the v2 evidence.

**Status:** IMPLEMENTED (default OFF) / LOCAL CONTROLS PASS /
[**Windows ⑨ FAIL against the pre-registered outcome — NOT ADOPTED**](#windows-top-exit-v2-comparison--2026-10-21).
BASE FULL started at 663.0 s, on a mid-refill frame where the human review sees
a visible interface. Top-exit stays default OFF; nothing is retuned. O2 OPEN /
FIELD FAIL, review-006 pending and ⑧ NOT RUN are unchanged. Current authority is
the [Work Plan](../../00-project/work-plan.md).

## What was built

The [frozen v2 design](../../20-architecture/s11-physical-interface-evidence-repair-design.md#october-21-top-exit-revision-v2)
(frozen at `3eb057a` before any code change) is implemented in
`oil_top_exit_full.close_top_exit_full`. The decisions behind it are in
[OTR-1](../../50-diagnostics/s11/2026-10-21-full-observable-top-review.md#decision-record--2026-10-21).
- **Switch:** same `top_exit_full` / `--oil-top-exit-full` option, default OFF.
  The version suffix is now `+top-exit-full-v2`; v1 is replaced in place.
- **1. Endpoint:** the last witness row lies inside the top `entrance_band_ratio`
  band.
- **2. Continuity:** a downward step up to the row-reversal tolerance keeps the
  witness.
- **3a. Exit row:** the owner's single publishable, allowed, unselected row may be
  the last witness row, after selected rows only. Its value is not published.
- **4. Episode (D2b):** FULL holds until the material phase reaches DRAINING or
  EMPTY evidence appears. Later selected Oil is not published. An unusable or
  opposed frame inside the episode is UNKNOWN without ending it.
- **6a. Anchor:** v1's anchor row, or the owner's `anchor_corridor` /
  `anchor_trajectory` profile plus a `direct_interface` or
  `ordered_lower_interface` window row.

Diagnostics record the version, band ratio, reversal tolerance, each row's
`selected` flag, `anchor_source` and `episode_end`.

**Other changes:**
- The comparison entry `tests.diagnostics.s11_initial_full_comparison` gains
  sample2, `--original-recipe` and `--initial-state {full,unknown}`. Its
  defaults are unchanged.
- The [logic map](../../20-architecture/s11-current-detector-logic-map.md)
  describes v2.
- No resolver, selector, phase, Recipe or GUI behaviour changed outside the
  option.

## Unit verification

- **Top-exit unit tests:** 37 passed (`tests/unit/test_oil_top_exit_full.py`).
- **New positives:**
  - a ④-shaped case: continuation rows with an `anchor_corridor` owner, a lag
    step, and an unselected publishable exit row, then FULL with
    `anchor_source = tracklet_profile`;
  - band endpoints short of the top, and a lag within tolerance;
  - an unusable frame inside the episode;
  - a drain release ending the episode.
- **New negatives:**
  - a last row just below the band;
  - no anchor profile; no interface-identity row;
  - two owner rows; another tracklet; two unselected rows;
  - an unselected row followed by an owner row; an owner outside the allowed set;
  - EMPTY ending the episode without resumption.
- **v1 cases rewritten as decided:**
  - "broad entrance" became a positive;
  - "reversal" now uses a step above the tolerance;
  - "unavailable frame" and "new numeric interface" follow D2b.
- **Seam-edited tests:** two cases cannot be produced through the real selector
  (an unselected row followed by an owner row, and DRAINING). Their tests edit
  the lifecycle result just before the top-exit seam.
- **Related suites:** resolver decomposition, production cutover, GUI launch,
  phase lifecycle and observation resolver: 225 passed together with the
  above.
- **Full unit suite** (`tests`, excluding `tests/diagnostics`): 3,792 passed,
  12 skipped. The skips are the quarantined sample3 corpus; they were not
  bypassed.

## Local controls (frozen before the run)

Managed run `sample/output/s11-top-exit-v2-20261021-001` (closed; 5 files kept):
- **Setup:** IFO v2 in both arms; top-exit v2 OFF vs ON; 2 fps; qualification
  windows; debug NONE.
- **Summary:** SHA-256
  `46929824f9c02c28156e12ddb7923eda835265783e1bfb7c1acb6032a226f26c`.

| Control | Initial state | Rows | Numeric Oil / Foam | FULL rows ON | Raw inputs, rows, events, report equal | Result |
|---|---|---:|---:|---:|---|---|
| sample4, original Recipe | UNKNOWN | 113 | 101 / 26 | 0 | Yes | PASS |
| sample4, October 15 interior Recipe | FULL (stress) | 113 | 16 / 76 | 0 | Yes | PASS |
| base_sample_1, original Recipe | FULL (stress) | 30 | 12 / 0 | 0 | Yes | PASS |
| sample2, original Recipe | FULL (stress) | 5 | 0 / 0 | 0 | Yes | PASS |

**Report equality ignores the per-run `run_id`.** The runner's `stable()`
already drops it from rows. The first summary compared the reports
without that normalization and flagged only `run_id` fields. No criterion or
detector value changed.

**Limits:**
- **No control reached a disappearance evaluation.** No witness was ever
  evaluated (reasons: `UNQUALIFIED_SELECTED_OWNER`, `CURRENT_EVIDENCE_RESET`,
  `CURRENT_INTERFACE_OR_STATE_RESET`, `NO_TOP_EXIT_WITNESS`). The controls show
  that v2 adds no FULL and changes no output here. They do not exercise the band,
  3a, 6a or D2b rules on real video; only the synthetic unit tests do.
- **sample4 G does not occur on the production path.** At 54.5–56 s the phase is
  `open / FILL_ESTABLISHED_INTERFACE` with numeric Oil at Y851–852. G appeared in
  the LBT-1 diagnostic path with its E1 topology rule, which is not production.
  The G control therefore holds trivially here, and a future E1 adoption would
  need to re-check it.
- **The October 16 v2 baselines are reproduced:** sample4 interior 16 / 76 and
  base_sample_1 12 / 0.

## Windows top-exit v2 comparison — 2026-10-21

**RECEIVED / FAIL.** The user authorized one run and relayed the Windows agent's
return for the [⑨ request](../../40-operations/s11-current-windows-field-qualification.md#top-exit-v2-comparison).
This is transferred evidence: no private file was inspected on the Mac. The
outcome was pre-registered in the
[frozen design](../../20-architecture/s11-physical-interface-evidence-repair-design.md#october-21-top-exit-revision-v2)
before the run.

**Identity and run:**
- **④:** run `a9ccece3-49bf-47af-a570-b1ca6e9777a4`, the existing bundle
  `…\bundle\oil_level_analysis_22-3_initial_ON_v2_20261015_171421`.
- **⑨:** run `56fb7228-abdb-4fb6-bc90-f1a8f8888b8a`.
  - **Source:** a fresh extract of the main ZIP in
    `C:\0.Coding\oil_level_tracker-main-20261021_run9\oil_level_tracker-main`.
    The module SHA-256 matched `7b493c1e…11a3` before the run.
  - **Version:** `r22-oil-ownership-evidence-replacement-v1+initial-full-observation-v2+top-exit-full-v2`,
    with no cost-first, RGB or Local XY suffix.
- **Path:** a headless runner, `run_top_exit_v2_headless.py`.
  - It reuses `AnalysisPipeline`, `AnalyzeVideoUseCase`, `OutputBundleStore`
    and `JsonlDebugTraceWriterFactory` as the CLI and bootstrap wire them.
  - The detector is `OpenCvPhaseDetector(initial_full_observation=True, top_exit_full=True)`.
  - Inputs match ④: video, Recipe, 480–780 s, 2 fps, FULL debug, compressor
    start 485 s, BASE FULL / Accum EMPTY.
  - One run; status `REVIEW_REQUIRED`, as in ④.
- **CSV join:** BASE 601 and Accum 601 rows; no duplicate, missing row or
  timestamp difference.

**Receipt notes (values kept as reported):**
- **Run label:** the return labels the new run "⑧" in its tables. The run ID,
  version suffix and bundle name identify ⑨, which this record uses.
- **Bundle path:** reported at two locations with the same folder name,
  `oil_level_analysis_22-3_initial_ON_v2_top_exit_20261021_154451`:
  - under `C:\0.Coding\2.Reference\Oil level tracker\0.windows_diagnostic\bundle\`
    (header);
  - under `C:\0.Coding\oil_level_tracker-R22-3\sample\output\` (closing note).

  This was not resolved here.
- **`anchor_source`:** Table Q reports none at 673.5 and 674.0 s. The code copies
  the closure, which holds `anchor_source`, into every continuing record. Reason
  and witness are present on those rows, so the gap does not bear on the
  verdict.

### Pre-registered checks

| Criterion | ⑨ | Verdict |
|---|---|---|
| BASE first FULL within 672–675 s (673.5 s expected) | f15896 at 662.996 s | **FAIL** |
| No BASE FULL before 672 s | 18 rows, 663.0–671.5 s | **FAIL** |
| FULL holds through 675–780 s with no numeric Oil | 211 rows: 202 FULL and 0 numeric Oil. The 9 others are UNKNOWN with `TOP_EXIT_FULL_FRAME_UNAVAILABLE` (768.5–772.0 s and 774.5 s). No `episode_end` | PASS. The 9 rows are D2b fail-closed frames inside the episode |
| Accum: zero FULL rows | 0 | PASS |
| Rows before closure match ④ | BASE before 662.996 s: 0 different. Accum (all rows): 0 different | PASS |

**Verdict: ⑨ FAILS as pre-registered.** Top-exit v2 is NOT ADOPTED and stays
default OFF. No rule or value is changed after the result.

### Table R (condensed)

| Interval | Rows | ④ Oil | ⑨ Oil | Lost | ④ FULL | ⑨ FULL |
|---|---:|---:|---:|---:|---:|---:|
| BASE 480–550 s | 139 | 3 | 3 | 0 | 0 | 0 |
| BASE 550–652 s | 205 | 170 | 170 | 0 | 0 | 0 |
| BASE 652–674 s | 43 | 39 | 20 | 19 | 0 | 22 |
| BASE 674–675 s | 2 | 0 | 0 | 0 | 0 | 2 |
| BASE 675–780 s | 211 | 91 | 0 | 91 | 0 | 202 |
| BASE OUTSIDE | 1 | 0 | 0 | 0 | 0 | 0 |
| Accum, all intervals | 601 | 36 | 36 | 0 | 0 | 0 |

- **Unchanged everywhere:** new Oil rows 0, Y changes on rows numeric in both 0,
  and no Foam coordinate or validity difference in any interval.
- **Accum by interval (both runs):** 480–653 s: 0 Oil; 653–672 s: 4;
  672–680 s: 10; 680–700 s: 0; 700–780 s: 22; OUTSIDE: 0.
- **The 19 lost refill rows are 663.5–672.5 s.**
  - ④ and ⑨ agree on 652.0–662.5 s, with 20 Oil rows there.
  - ⑨ is FULL from 663.0 s.
  - In ④, 663.0, 673.0 and 673.5 s are not Oil
    ([review-004](../../50-diagnostics/s11/2026-10-15-initial-full-comparison.md#corrected-segment-counts-and-review-004-closeout),
    [OTR-1 §6](../../50-diagnostics/s11/2026-10-21-full-observable-top-review.md#6-windows-trace-receipt--2026-10-21)).

### Spot checks

- **721.0 s:** ④ PARTIAL_VISIBLE Y694 (the known false anchor); ⑨ FULL.
- **723.0 s:** ④ UNKNOWN; ⑨ FULL.
- **771.0 s:** UNKNOWN in both; in ⑨ it is a frame-unavailable row inside the
  episode.
- **⑨ FULL rows with an Oil Y or without `OIL_TOP_EXIT_FULL`:** 0 of 226.
- **⑨ FULL rows whose raw `oil_no_interface_full_likelihood` differs from ④:**
  0 of 226.

### Table Q (BASE 670.0–674.0 s)

All nine records have:
- state `FULL_NO_INTERFACE` with no Oil Y;
- reason `TOP_EXIT_FULL_CONTINUING`;
- no `episode_end`;
- the closure's witness.

Six selected rows of one owner:

| Witness row | Time (s) | Y |
|---|---:|---:|
| f15824 | 660.0 | 434.0 |
| f15836 | 660.5 | 430.0 |
| f15848 | 661.0 | 437.5 |
| f15860 | 661.5 | 426.0 |
| f15872 | 662.0 | 433.5 |
| f15884 | 662.5 | 409.0 |

- **`anchor_source`:** `window_row` at 670.0–673.0 s; missing at 673.5 and
  674.0 s (see the receipt notes).
- **False predicates:**
  - 670.0–673.0 s: only `no_current_interface` (the 0319 row is present);
  - 673.5 and 674.0 s: none.

### Cause

The basis is this receipt, the frozen BASE geometry and the existing reviews:
- **Geometry:** top Y211.6, H 772.2, band end Y420.1.
- **Tolerances:** reversal tolerance 9.267 px; minimum progress
  max(4, 0.025H) = 19.3 px.

**The closure fired on a mid-refill blank frame (f15896, 663.0 s):**
- **Witness:** the six-row witness (660.0–662.5 s) sat at Y426–437.5, at
  0.28–0.29H, below the band. Its last row stepped to Y409 (0.256H), 11 px
  inside the band.
- **Closure:** at 663.0 s no admitted Oil row existed, so every predicate
  passed.
- **Rules used:** the anchor was a window row; rules 3a and 6a were not used.

**[Review-004](../../50-diagnostics/s11/2026-10-15-initial-full-comparison.md#corrected-segment-counts-and-review-004-closeout)
shows the interface was visible at 663.0 s:**
- The user allowed Y417, Y419 and Y407 there.
- Those values matched admitted-0 `INCOMPATIBLE_BRANCH` candidates that are
  excluded before IFO.
- The Y409 endpoint at 662.5 s was itself an accepted alternative.
- The user's timeline puts 652–674 s in refill, with FULL acceptable from about
  672 s.

So the blank at 663.0 s is the known harmful exclusion, not a top exit.

**The closure needed two v2 items:**
- **Item 1 (band endpoint):**
  - v1 required the last row within 9.267 px of the top;
  - Y409 is 197 px below the top.
- **Item 2 (lag continuity):**
  - The witness has two 7.5 px downward steps (430→437.5 and 426→433.5), each
    within the tolerance.
  - v1 broke the window on any downward step. That would leave 433.5→409: two
    rows, below the three-observation minimum.
  - Net progress 434→409 is 25 px. It clears the 19.3 px minimum mainly through
    the last step.

**Item 4 (D2b) kept the error in place:**
- The interface reappeared at 663.5 s: ④ Y418, an accepted review-004
  alternative.
- ④ published Oil on every row through 672.5 s.
- Under D2b those 19 rows stay FULL, and the episode never ended.

**What ⑨ does not test:**
- **The intended 673.5 s closure was never evaluated,** because the episode was
  already active. Table Q shows only that 673.5 and 674.0 s were usable,
  unopposed and without a current interface.
- **No closure fired before 663.0 s.** The rows before closure are identical.

### Options (the user decides)

| Option | What it does | Expected on ④ (from existing receipts) | Cost / risk |
|---|---|---|---|
| **A. Stop top-exit here** | v2 is NOT ADOPTED. B returns to the Work Plan for its next direction | ④ unchanged: UNKNOWN from 673 s, with the 721 s Y694 false anchor | FULL on ④ stays unresolved |
| **B. v3 = v2 + confirmed disappearance** | A disappearance becomes FULL only if the next frame is also usable, unopposed and without a current interface. A current interface on that frame cancels it and the witness restarts. FULL starts on the confirming frame; the disappearance frame stays UNKNOWN, as in ④. No new threshold | 663.0 s is cancelled, because 663.5 s has a selected row. At 673.5 s, FULL would start at 674.0 s, which had no current interface in ⑨. That is inside 672–675 s | The 673.5 s closure itself is still unproven on a run (stored values plus two inferences). A blank of two or more frames inside the band would still close. Freeze, implement, run local controls, then one ⑩ run against the same pre-registered outcome |
| **C. Remove the 663.0 s exclusion first** | Qualify the admitted-0 `INCOMPATIBLE_BRANCH` exclusion that blanks f15896 (review-004) | Removes this blank frame | Selection-side work in F04/F05 territory. Top-exit would still close on the next blank frame inside the band |

**Not offered:**
- **Narrowing the band:** threshold tuning after the result (F10).
- **Reverting item 2:** also breaks the intended window. Its 350→352 step at
  672.0–672.5 s would leave two rows.
- **Releasing FULL when the interface reappears:** 663.0 s would still be FULL,
  which already fails the criterion.

**Recommendation: B.** It targets the observed mechanism, a single blank frame
read as an exit. It adds no threshold, and the existing receipts predict both
the cancellation and a FULL start inside the window. C remains the right repair
for the blank frame itself, but it does not make top-exit safe.

## Detector Governance

- Logic-map nodes: `OIL-TRACKLET`, `OIL-SELECTOR`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-PROJECTION`, `PUBLICATION-PROVENANCE`, `CSV-PUBLICATION`
- Failure-registry entries: `S11-F04`, `S11-F05`, `S11-F08`, `S11-F10`
- First harmful stage: before v2, unchanged from [OTR-1](../../50-diagnostics/s11/2026-10-21-full-observable-top-review.md#predicate-check-receipt--2026-10-21). On ④ the last owner row is lost at `OIL-SELECTOR` (path cost), and v1's endpoint and anchor rules could not close. v2 adds a closure route at the post-selection seam; it does not change selection. In ⑨ the first harmful stage is `OIL-PHASE-FILL` (the top-exit closure) at 663.0 s. It turns an upstream blank frame into FULL; that blank is the review-004 `INCOMPATIBLE_BRANCH` exclusion before IFO, at `OIL-TRACKLET`. FULL persistence then suppresses 19 refill Oil rows.
- Existing feature coverage: production detector path with IFO v2 in both arms, on the original sample4/base_sample_1/sample2 Recipes and the frozen October 15 sample4 interior Recipe. Effective masks and margin are as configured; cost-first, RGB and Local XY are OFF. Top-exit v2 is exercised synthetically through the full resolver and CSV export, and on four local videos where it never reaches an evaluation. On Windows, ⑨ ran the production pipeline on ④'s inputs with only IFO v2 and top-exit v2 ON. Its first evaluation that passed every predicate was a false closure; the 673.5 s target was never evaluated. ④/Windows media were not accessed from the Mac.
- Execution scope: unit tests, the full unit suite and one managed local comparison run (four controls, NONE debug). One user-authorized Windows run (⑨), with values returned as transferred evidence. No private media on the Mac, no human review, tuning or post-result rule change.
- Logic-map impact: NONE — this update records the ⑨ receipt and changes no detector code. The v2 logic-map update was committed with the implementation (`1f68c46`), and top-exit stays default OFF.
- Failure-registry impact: NONE — the ⑨ failure is an existing S11-F05 mechanism: a FULL gate locks a real owner. Here it locks the visible refill interface for 663.5–672.5 s. The other v2 risks remain within F04 (drifting anchor-confirmed owner), F08 (FULL meaning) and F10 (threshold escape, avoided by reusing existing quantities).
