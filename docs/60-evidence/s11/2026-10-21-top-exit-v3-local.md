# Top-exit FULL v3 — local implementation and controls

**Status:** IMPLEMENTED (default OFF) / LOCAL CONTROLS PASS / Windows ⑩ NOT RUN.
The ⑩ request is in the
[Windows procedure](../../40-operations/s11-current-windows-field-qualification.md#top-exit-v3-comparison).
O2 OPEN / FIELD FAIL and review-006 pending are unchanged. Current authority is
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

## Detector Governance

- Logic-map nodes: `OIL-TRACKLET`, `OIL-SELECTOR`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-PROJECTION`, `PUBLICATION-PROVENANCE`, `CSV-PUBLICATION`
- Failure-registry entries: `S11-F04`, `S11-F05`, `S11-F08`, `S11-F10`
- First harmful stage: in ⑨ it was `OIL-PHASE-FILL` (the top-exit closure) at 663.0 s, which turned the review-004 `INCOMPATIBLE_BRANCH` blank (`OIL-TRACKLET`) into FULL ([v2 evidence](2026-10-21-top-exit-v2-local.md#windows-top-exit-v2-comparison--2026-10-21)). v3 changes only that closure: a disappearance must be repeated on the next frame. Selection and the upstream exclusion are unchanged.
- Existing feature coverage: production detector path with IFO v2 in both arms, on the original sample4/base_sample_1/sample2 Recipes and the frozen October 15 sample4 interior Recipe. Effective masks and margin are as configured; cost-first, RGB and Local XY are OFF. Top-exit v3 is exercised synthetically through the full resolver and CSV export, and on four local videos where it never reaches an evaluation. ④/Windows media were not accessed.
- Execution scope: unit tests with a mutation check, the full unit suite and one managed local comparison run (four controls, NONE debug). No Windows execution, private media, human review, tuning or post-result rule change.
- Logic-map impact: UPDATED — the top-exit table row and the projection paragraph now describe the v3 pending closure, its confirmation on the next frame and FULL from the confirming frame.
- Failure-registry impact: NONE — no new failure mechanism was found. Item 7 narrows the existing S11-F05 risk seen in ⑨ (a FULL gate locking a real owner after a one-frame blank). A blank of two or more frames remains within F05; F04, F08 and F10 are unchanged, and no threshold was added.
