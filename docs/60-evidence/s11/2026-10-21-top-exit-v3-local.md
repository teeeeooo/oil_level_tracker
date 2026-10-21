# Top-exit FULL v3 — local implementation and controls

**Status:** IMPLEMENTED (default OFF) / LOCAL CONTROLS PASS /
[**Windows ⑩ PASS against the pre-registered outcome**](#windows-top-exit-v3-comparison--2026-10-21).
BASE FULL starts at 674.0 s; the 663.0 s blank is cancelled. Top-exit stays
default OFF and is not promoted. O2 OPEN / FIELD FAIL and review-006 pending are
unchanged. Current authority is
the [Work Plan](../../00-project/work-plan.md).

## What was built

The [frozen v3 design](../../20-architecture/s11-physical-interface-evidence-repair-design.md#october-21-top-exit-revision-v3)
was frozen at `e88d387` before any code change. It follows the user's choice of
option B after the
[⑨ FAIL](2026-10-21-top-exit-v2-local.md#windows-top-exit-v2-comparison--2026-10-21).
It is implemented in `oil_top_exit_full.close_top_exit_full`:
- **Item 7, confirmed disappearance:**
  - **Pending:** when every v2 predicate passes, the closure is only pending, and
    that frame keeps its UNKNOWN node.
  - **Confirmation:** the next frame must have a bounded gap, a usable raster,
    clear EMPTY, no opposition, no phase-admitted Oil, an unknown node and a
    phase other than DRAINING. FULL then starts on that frame.
  - **Cancellation:** otherwise the pending closure is cancelled and the frame is
    processed normally. Nothing is back-filled.
- **Unchanged from v2:** items 1, 2, 3a, 4 (D2b) and 6a.
- **Switch:** the same `top_exit_full` / `--oil-top-exit-full` option, default
  OFF. The suffix is `+top-exit-full-v3`; v2 is replaced in place.
- **Diagnostics:** `version: v3`, `confirmation` (`PENDING`, `CONFIRMED` or
  `CANCELLED`) and `confirmation_predicates`. The closure carries
  `disappearance_frame_index` and `confirmation_frame_index`.
- **Module SHA-256:**
  `10dd3605a9ab0afb4ce4c0ae5a69477b1157318b0246ae972716d4202bb6f77d`.
- **Other changes:**
  - the [logic map](../../20-architecture/s11-current-detector-logic-map.md)
    describes v3;
  - the version strings in the resolver, detector, GUI launch test and
    comparison entry move to `+top-exit-full-v3`;
  - no resolver, selector, phase, Recipe or GUI behaviour changed outside the
    option.

## Unit verification

- **Top-exit unit tests:** 46 passed (`tests/unit/test_oil_top_exit_full.py`).
- **Rewritten v2 positives:** FULL now starts on the confirming frame, and the
  disappearance frame stays UNKNOWN with `TOP_EXIT_FULL_PENDING`. The cases are:
  - the selected rise with CSV export;
  - the band endpoints and the lag step;
  - the ④-shaped unselected exit row;
  - the lower interface with a drain release;
  - the Foam composition.
- **Episode cases moved one frame later:** the unusable frame and the EMPTY
  frame now fall inside a confirmed episode. Their expectations are unchanged.
- **New negatives:**
  - the ⑨ shape: a witness into the band, one blank frame, then the selected
    interface again. No FULL; numeric output equals OFF; the reappearing frame
    records `CANCELLED` with `no_current_interface` false;
  - a bad confirming frame: unavailable, fogged, black raster, EMPTY, time gap,
    or a current Oil row. No FULL;
  - a pending closure on the last frame. No FULL.
- **New positive (④ shape):** a cancelled pending, a continued rise, then a real
  exit. FULL starts only at the second exit's confirming frame, and every
  earlier row equals OFF.
- **Mutation check:** forcing every pending closure to confirm fails all 8 new
  cases. The code was restored before the suite run.
- **Full unit suite** (`tests`, excluding `tests/diagnostics`): 3,801 passed,
  12 skipped. The skips are the quarantined sample3 corpus; they were not
  bypassed.

## Local controls (frozen before the run)

Managed run `sample/output/s11-top-exit-v3-20261021-001` (closed; 5 files kept):
- **Setup:** the v2 entry, controls and pass criteria; IFO v2 in both arms;
  top-exit v3 OFF vs ON; 2 fps; debug NONE.
- **Summary:** SHA-256
  `cfa5876a8490d2cab5492b853b3849cbec04595cae86b5c998b452d0496533d6`.

| Control | Initial state | Rows | Numeric Oil / Foam | FULL rows ON | Raw inputs, rows, events, report equal | Result |
|---|---|---:|---:|---:|---|---|
| sample4, original Recipe | UNKNOWN | 113 | 101 / 26 | 0 | Yes | PASS |
| sample4, October 15 interior Recipe | FULL (stress) | 113 | 16 / 76 | 0 | Yes | PASS |
| base_sample_1, original Recipe | FULL (stress) | 30 | 12 / 0 | 0 | Yes | PASS |
| sample2, original Recipe | FULL (stress) | 5 | 0 / 0 | 0 | Yes | PASS |

Report equality ignores the per-run `run_id`, as in v2.

**Limits:**
- **No control reached a disappearance evaluation.** None had a pending closure.
  Item 7 and the v2 rules are exercised only by the synthetic unit tests.
- **Counts match v2:** the controls reproduce the v2 counts exactly.
- **v3 is untested on ④.** The 673.5 s pending closure and its 674.0 s
  confirmation are predictions from the ⑨ receipt and the predicate check, not
  a run. The upstream `INCOMPATIBLE_BRANCH` blank at 663.0 s is not repaired.

## Windows top-exit v3 comparison — 2026-10-21

**RECEIVED / PASS.** The user relayed the Windows agent's return for the
[⑩ request](../../40-operations/s11-current-windows-field-qualification.md#top-exit-v3-comparison).
This is transferred evidence: no private file was inspected on the Mac. The
outcome was pre-registered in the
[frozen v3 design](../../20-architecture/s11-physical-interface-evidence-repair-design.md#october-21-top-exit-revision-v3)
before the run.

**Identity and run:**
- **④:** run `a9ccece3-49bf-47af-a570-b1ca6e9777a4`, bundle
  `C:\0.Coding\2.Reference\Oil level tracker\0.windows_diagnostic\bundle\oil_level_analysis_22-3_initial_ON_v2_20261015_171421`.
- **⑩:** run `84526e04-b989-437e-9790-668834771e50`, run name
  `22-3_initial_ON_v2_top_exit_v3`.
  - **Source:** a fresh extract of the main ZIP (created 2026-10-21 16:41) in
    `C:\0.Coding\oil_level_tracker-main-20261021_run10\oil_level_tracker-main`.
    The module SHA-256 matched `10dd3605…6f77d` before the run.
  - **Versions:** sequence `r22-oil-ownership-evidence-replacement-v1+initial-full-observation-v2+top-exit-full-v3`;
    detector `opencv-phase-detector-r22-3-interface-witness-diagnostics-v1+initial-full-observation-v2+top-exit-full-v3`.
    No cost-first, RGB or Local XY suffix.
  - **Path:** headless runner `run_top_exit_v3_headless.py`, wired as for ⑨, with
    `OpenCvPhaseDetector(initial_full_observation=True, top_exit_full=True)`.
  - **Inputs:** ④'s video and Recipe, 480–780 s, 2 fps, FULL debug,
    compressor start 485 s, BASE FULL / Accum EMPTY.
  - **Result:** one run; status `REVIEW_REQUIRED`, as in ④ and ⑨.
  - **Bundle:** `C:\0.Coding\2.Reference\Oil level tracker\0.windows_diagnostic\bundle\oil_level_analysis_22-3_initial_ON_v2_top_exit_v3_20261021_170933`.
- **CSV join:** BASE 601 and Accum 601 rows; no duplicate, missing row or
  timestamp difference.

**Receipt notes (values kept as reported):**
- **Run labels shifted again.** The return calls this run "⑨" and the v2 run
  "⑧", although the request asked for "⑩". The run ID, run name, version suffix
  and bundle name identify this run as ⑩ (v3), and its "⑧" bundle as ⑨ (v2).
  This record uses ⑨ and ⑩.
- **⑨ bundle location resolved.** The Windows agent moved the ⑨ bundle into the
  common bundle folder. It reports a single location,
  `…\0.windows_diagnostic\bundle\oil_level_analysis_22-3_initial_ON_v2_top_exit_20261021_154451`,
  and nothing left at the old place. This settles the
  [two-path note](2026-10-21-top-exit-v2-local.md#windows-top-exit-v2-comparison--2026-10-21);
  the bundle contents were not reported as changed.

### Pre-registered checks

| Criterion | ⑩ | Verdict |
|---|---|---|
| BASE first FULL within 672–675 s (674.0 s expected) | f16160 at 674.007 s | PASS |
| No BASE FULL before 672 s | 0 rows | PASS |
| FULL holds through 675–780 s with no numeric Oil | 211 rows: 202 FULL and 0 numeric Oil. The 9 others are UNKNOWN with `TOP_EXIT_FULL_FRAME_UNAVAILABLE` (768.5–772.0 s and 774.5 s). No `episode_end` | PASS. The 9 rows are D2b fail-closed frames inside the episode, the same as in ⑨ |
| Accum: zero FULL rows | 0 | PASS |
| Rows before closure match ④ | BASE before 674.007 s: 0 different. Accum (all rows): 0 different | PASS |

**Verdict: ⑩ PASSES every pre-registered criterion.** Top-exit v3 stays
default OFF. Promotion or field acceptance is a separate decision. This is one
Glass of one video; it is not field qualification.

### What happened at the decision frames

| Time (s) | Frame | ⑩ state / Y | Top-exit record |
|---|---|---|---|
| 662.5 | 15884 | PARTIAL_VISIBLE 409 | `OBSERVED_OWNER` |
| 663.0 | 15896 | UNKNOWN | `TOP_EXIT_FULL_PENDING`; every predicate true; anchor `window_row`. Same witness as ⑨: 660.0–662.5 s, Y434…409, all selected |
| 663.5 | 15908 | PARTIAL_VISIBLE 418 | `CANCELLED`; false confirmation checks: `no_current_interface`, `unknown_node`; reason `UNQUALIFIED_SELECTED_OWNER` |
| 664.0 | 15920 | PARTIAL_VISIBLE 425 | `UNQUALIFIED_SELECTED_OWNER` |
| 672.5 | 16124 | PARTIAL_VISIBLE 352 | `OBSERVED_OWNER` |
| 673.0 | 16136 | UNKNOWN | `UNSELECTED_EXIT_ROW` (3a) |
| 673.5 | 16148 | UNKNOWN | `TOP_EXIT_FULL_PENDING`; every predicate true; anchor `tracklet_profile` (6a) |
| 674.0 | 16160 | FULL | `TOP_EXIT_FULL_CONFIRMED`; disappearance 16148, confirmation 16160 |
| 674.5–675.0 | 16172–16184 | FULL | `TOP_EXIT_FULL_CONTINUING` |

The closure witness is 670.5–673.0 s: Y377, 369, 362, 350, 352 (selected), then
Y329 (unselected).

The run exercises every v3 rule on real video, which the local controls could
not:
- **Item 1:** the endpoint Y329 lies inside the band (end Y420.1).
- **Item 2:** the 350→352 lag step is within the 9.267 px tolerance.
- **3a:** the unselected exit row at 673.0 s.
- **6a:** the tracklet-profile anchor.
- **Item 7:** the pending closure at 663.0 s is cancelled at 663.5 s, and the
  one at 673.5 s is confirmed at 674.0 s.
- **D2b:** fail-closed frames inside the episode.

These match the frame-by-frame
[expectations](../../20-architecture/s11-physical-interface-evidence-repair-design.md#october-21-top-exit-revision-v3)
written before the run. Over the whole BASE run the confirmation states are:
- PENDING: 663.0 and 673.5 s;
- CANCELLED: 663.5 s;
- CONFIRMED: 674.0 s.

### Table R (condensed)

| Interval | Rows | ④ Oil | ⑩ Oil | Lost | ④ FULL | ⑩ FULL |
|---|---:|---:|---:|---:|---:|---:|
| BASE 480–550 s | 139 | 3 | 3 | 0 | 0 | 0 |
| BASE 550–652 s | 205 | 170 | 170 | 0 | 0 | 0 |
| BASE 652–674 s | 43 | 39 | 39 | 0 | 0 | 0 |
| BASE 674–675 s | 2 | 0 | 0 | 0 | 0 | 2 |
| BASE 675–780 s | 211 | 91 | 0 | 91 | 0 | 202 |
| BASE OUTSIDE | 1 | 0 | 0 | 0 | 0 | 0 |
| Accum, all intervals | 601 | 36 | 36 | 0 | 0 | 0 |

- **Unchanged everywhere:** new Oil rows 0, Y changes on rows numeric in both 0,
  and no Foam coordinate or validity difference.
- **Accum by interval (both runs):** 4 / 10 / 22 Oil in 653–672 / 672–680 /
  700–780 s; 0 elsewhere.
- **Refill restored:** the 19 refill Oil rows that ⑨ lost (663.5–672.5 s) are
  all kept.
- **Lost rows are FULL-suffix output:** the 91 lost rows lie in 675–780 s.
  Under the [reviewed truth](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md#base-timeline-correction--2026-10-15)
  and the [672 s FULL acceptance](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md#base-full-acceptance--2026-10-21),
  that span is FULL. They include the 721 s Y694 false anchor.

### Spot checks

- **721.0 s:** ④ PARTIAL_VISIBLE Y694 (the known false anchor); ⑩ FULL.
- **723.0 s:** ④ UNKNOWN; ⑩ FULL.
- **771.0 s:** UNKNOWN in both; in ⑩ it is a frame-unavailable row inside the
  episode.
- **⑩ FULL rows with an Oil Y or without `OIL_TOP_EXIT_FULL`:** 0 of 204.
- **⑩ FULL rows whose raw `oil_no_interface_full_likelihood` differs from ④:**
  0 of 204.
- **BASE 675–780 s fill states different from ⑨:** 0.

### Limits

- **Scope:** one Glass on one video. Accum contributes only a negative control;
  the other local controls never reach an evaluation.
- **Longer blanks:** a blank of two or more frames inside the band after a
  qualifying witness would still close. Not exercised.
- **Drain release:** after closure, FULL ends only on DRAINING or EMPTY. A real
  drain that the lifecycle does not release would stay FULL. The reviewed
  interval ends at 780 s, so this is not scored.
- **Unchanged numeric selection:**
  - 663.0 s stays blank (the `INCOMPATIBLE_BRANCH` exclusion, option C);
  - the 673.0 s true level Y329 stays unpublished;
  - the 672.5 s Y352 reflection (review-011) is still published, as in ④.
- **The 9 fail-closed frames at 768.5–774.5 s** publish UNKNOWN, not FULL, as in
  ⑨.

## Detector Governance

- Logic-map nodes: `OIL-TRACKLET`, `OIL-SELECTOR`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-PROJECTION`, `PUBLICATION-PROVENANCE`, `CSV-PUBLICATION`
- Failure-registry entries: `S11-F04`, `S11-F05`, `S11-F08`, `S11-F10`
- First harmful stage: in ⑨ it was `OIL-PHASE-FILL` (the top-exit closure) at 663.0 s, which turned the review-004 `INCOMPATIBLE_BRANCH` blank (`OIL-TRACKLET`) into FULL ([v2 evidence](2026-10-21-top-exit-v2-local.md#windows-top-exit-v2-comparison--2026-10-21)). v3 changes only that closure: a disappearance must be repeated on the next frame. Selection and the upstream exclusion are unchanged.
- Existing feature coverage: production detector path with IFO v2 in both arms, on the original sample4/base_sample_1/sample2 Recipes and the frozen October 15 sample4 interior Recipe. Effective masks and margin are as configured; cost-first, RGB and Local XY are OFF. Top-exit v3 is exercised synthetically through the full resolver and CSV export, and on four local videos where it never reaches an evaluation. ④/Windows media were not accessed.
- Execution scope: unit tests with a mutation check, the full unit suite and one managed local comparison run (four controls, NONE debug). One user-authorized Windows run (⑩), with values returned as transferred evidence. No private media on the Mac, no human review, tuning or post-result rule change.
- Logic-map impact: NONE — this update records the ⑩ receipt and changes no detector code. The v3 logic-map update was committed with the implementation (`5971b30`), and top-exit stays default OFF.
- Failure-registry impact: NONE — no new failure mechanism was found. Item 7 narrows the existing S11-F05 risk seen in ⑨ (a FULL gate locking a real owner after a one-frame blank). A blank of two or more frames remains within F05; F04, F08 and F10 are unchanged, and no threshold was added.
