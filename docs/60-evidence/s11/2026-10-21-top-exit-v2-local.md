# Top-exit FULL v2 — local implementation and controls

**Status:** IMPLEMENTED (default OFF) / LOCAL CONTROLS PASS / Windows NOT RUN.
A Windows comparison on ④'s inputs needs a separate go from the user. O2 OPEN /
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

## Windows (not run)

The pre-registered outcome for one comparison on ④'s inputs is in the
[frozen design](../../20-architecture/s11-physical-interface-evidence-repair-design.md#october-21-top-exit-revision-v2):
- **BASE:** FULL starts within 672–675 s (673.5 s expected), with no FULL before
  672 s, and holds through 675–780 s with no numeric Oil;
- **Accum:** no top-exit FULL;
- **Both:** rows before closure are identical.

On ④ the [predicate check](../../50-diagnostics/s11/2026-10-21-full-observable-top-review.md#predicate-check-receipt--2026-10-21)
supports the closure at 673.5 s. That rests on stored values and two
inferences, not a run. The run needs the user's go.

## Detector Governance

- Logic-map nodes: `OIL-SELECTOR`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-PROJECTION`, `PUBLICATION-PROVENANCE`, `CSV-PUBLICATION`
- Failure-registry entries: `S11-F04`, `S11-F05`, `S11-F08`, `S11-F10`
- First harmful stage: unchanged from [OTR-1](../../50-diagnostics/s11/2026-10-21-full-observable-top-review.md#predicate-check-receipt--2026-10-21). On ④ the last owner row is lost at `OIL-SELECTOR` (path cost), and v1's endpoint and anchor rules could not close. v2 adds a closure route at the post-selection seam; it does not change selection.
- Existing feature coverage: production detector path with IFO v2 in both arms, on the original sample4/base_sample_1/sample2 Recipes and the frozen October 15 sample4 interior Recipe. Effective masks and margin are as configured; cost-first, RGB and Local XY are OFF. Top-exit v2 is exercised synthetically through the full resolver and CSV export, and on four local videos where it never reaches an evaluation. ④/Windows media were not accessed.
- Execution scope: unit tests, the full unit suite and one managed local comparison run (four controls, NONE debug). No Windows execution, private media, human review, tuning or post-result rule change.
- Logic-map impact: UPDATED — the top-exit table row and the projection paragraph now describe the v2 band endpoint, lag continuity, unselected exit row, tracklet-profile anchor and FULL persistence until DRAINING or EMPTY.
- Failure-registry impact: NONE — no new failure mechanism was found. The v2 risks sit within existing entries: a drifting anchor-confirmed owner (F04), FULL persistence over later rows (F05), FULL meaning (F08) and threshold escape (F10, avoided by reusing existing quantities).
