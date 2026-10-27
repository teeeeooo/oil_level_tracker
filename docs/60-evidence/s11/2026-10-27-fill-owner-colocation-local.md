# Co-located fill owners (E4) — local implementation and checks

**Status:** IMPLEMENTED (opt-in, default OFF) at `9ee11a4` / **LOCAL CHECKS
FAIL on a frozen stop condition** against the
[frozen checks](../../30-validation/s11-physical-interface-evidence-repair-validation.md#co-located-fill-owner-checks--2026-10-27).
- **As predicted:** K1 identity passes on all five controls. On sample5,
  exactly 9.5, 10.0 and 11.0 s become `FILL_OWNER_COLOCATED`. Rows are added at
  9.5 s (Y798) and 10.0 s (Y792), and both lie within 32 px of the surface
  estimate (K3).
- **Stop:** sample5 events change outside the K2 frames. Every such change
  follows from the two added rows (see below). The frozen rule makes this a
  FAIL, and nothing is retuned.
- **Unchanged:** E4 stays opt-in and default OFF. O2 OPEN / FIELD FAIL is
  unchanged. The user decides the next step.
- **Authority:** the [Work Plan](../../00-project/work-plan.md).

## What was built

The [design](../../20-architecture/s11-physical-interface-evidence-repair-design.md#october-27-co-located-fill-owners-e4)
was frozen at `9c421c3` and approved at `10f7b69`, both before any code change.
It was implemented at `9ee11a4`.

**In [`OilMaterialPhaseLifecycleOwner`](../../../src/oil_tracker/adapters/vision/oil_phase_lifecycle.py)
`_transition_open`:**
- The branch that would record `FILL_OWNER_AMBIGUOUS` first asks
  `_fill_owners_colocated`.
- It is true when every dynamic owner has a row in the frame and those rows
  span at most `maximum_jump_px`.
- The frame then:
  - stays FILLING;
  - allows the dynamic-owner set;
  - records `FILL_OWNER_COLOCATED`;
  - is not marked ambiguous and adds no contest mark.
- Every other state field evolves as in the ambiguous branch.

**Switch:**
- **Flag:** `fill_owner_colocation` / GUI `--oil-fill-owner-colocation`,
  default OFF, suffix `+fill-owner-colocation-v1`.
- **Combinations:** it combines with IFO v2, top-exit v3 and the contested
  gate. The detector refuses it with cost-first, RGB or Local XY, and the
  launcher refuses the same flags.

**Other changes:**
- the comparison runner gains `--fill-owner-colocation-comparison`;
- the logic map gains a feature row and a 4.3 paragraph;
- the resolver's `OilTrackletOppositionOwner(self.config)` call is joined onto
  one line so the module stays within its 2,700-line decomposition guard. This
  is formatting only.

**Lifecycle module SHA-256:**
`39e214fe4ae038615a149d1c8106d44b830cd20ceefc376f54294b8c67b7ecfa`.

## Tests

- **New unit tests:** 9 in `tests/unit/test_oil_fill_owner_colocation.py`,
  covering each frozen unit check plus the combination with the integrated
  candidate. Every test asserts that phases, confirmation profiles, owner
  chains and lifecycle state are the same with the option OFF and ON.
- **Mutation checks:**
  - disabling the co-location branch fails 4 tests;
  - dropping the every-owner-has-a-row rule fails 5.
- **Wiring:** the GUI factory test covers E4 alone and with top-exit and the
  gate on all four detector entries. The launch tests cover the flags and the
  stacked refusals, and the constructor-surface guard covers the new
  parameter.
- **Full suite:** 3,984 passed. 12 skipped: sample3 is quarantined, as before.

## Local checks

**Run:** closed managed run `s11-fill-owner-colocation-local-20261027-001` at
`9ee11a4`.
- **Inputs:** six controls with the contested gate's Recipes, ROI inputs and
  initial states, at 2 fps with debug NONE.
- **Scorer:** the frozen script `e4_checks.py` (SHA-256 `e65034cc…`).
- **Verdict file:** `checks.json` (SHA-256 `12c6c2a5…`).

| Check | Controls | Result |
|---|---|---|
| Identity anchor | all six | **PASS.** The reference arm equals the kept top-exit arm (rows, events, report, version). On sample5 and sample7, its `FILL_OWNER_AMBIGUOUS` frames equal the FOR-1 readouts (48 and 24) |
| K1 identity | base_sample_1-full, sample2-full, sample4-interior-full, sample4-original-unknown, sample7-empty | **PASS.** No frame becomes co-located; rows, phases, events and report are equal |
| K2 prediction | sample5-empty | **Frames as predicted:** exactly 9.5, 10.0 and 11.0 s. Rows differ only at 9.5 s (UNKNOWN → Y798) and 10.0 s (UNKNOWN → Y792). 11.0 s stays UNKNOWN (the selector published no row) |
| K3 placement | sample5-empty | **Within 32 px:** 9.5 s −8.7 px and 10.0 s −17.5 px from the FOA-1 agent estimate. No K3 risk |
| Stop conditions | all six | **Fired on sample5:** events change outside the K2 frames. No row is added, removed or moved outside them; no Foam coordinate or row FULL/EMPTY state changes |

**sample5 changes outside the K2 frames** (reference → E4):

| Item | Reference | E4 |
|---|---|---|
| Initial-state retrospective | UNRESOLVED ("broke on a step above `temporal_max_jump_px`") | ACCEPTED: EMPTY 0.0–8.0 s, from evidence at 8.5, 9.0 and 9.5 s |
| Retrospective events | none | `EMPTY_NO_INTERFACE_START` 0.0–8.0 s; `OIL_BOUNDARY_APPEARED_FROM_BOTTOM` 8.5 s (Y−226 px from zero) |
| Low-confidence and review interval | starts 9.5 s | starts 10.5 s (ends 19.5 s in both) |
| Coverage review | 20.7 % | 22.5 % (still below 70 %) |
| `FOAM_START` 22.0 s and 23.5 s | — | same times and Foam positions; only the capture file index changes |
| Report | — | the same items follow: finite count 23 → 25, the gap list, landmarks and scene captures |

**Reading (facts only; the verdict stays FAIL):**
- Each change follows from the two added rows. The 9.5 s row completes two
  consecutive decisive moves after the first boundary at 8.5 s, so the
  retrospective can now accept.
- The accepted interpretation (EMPTY at the start) agrees with the user's
  sample5 truth, "starts EMPTY and never becomes full" (2026-10-22).
- The 8.5 s appearance agrees with the FOA-1 agent estimate ("thin layer at the
  base"), which is an agent reading, not user truth.
- The frozen draft predicted row changes only. It did not foresee that two
  early rows would let the initial-state retrospective accept.

## What this does not show

- **Windows effect:** the SPL#4 prediction (23.0 and 23.5 s co-located) is
  untested. The Windows pass condition compares rows; event effects like
  sample5's are possible there too.
- **Accuracy:** nothing beyond the user's judgments. This is not a promotion.

## Next (user decision)

The frozen rule ends this check as FAIL. The user decides whether E4 goes on
to the Windows SPL#4 comparison, stops, or is re-frozen. In every case E2 →
E1 → E3 follow, each frozen before code.

## Detector Governance

- Logic-map nodes: `OIL-PHASE-FILL`, `OIL-PHASE-INITIAL`, `OIL-SELECTOR`, `PUBLICATION-PROVENANCE`
- Failure-registry entries: `S11-F04`, `S11-F05`, `S11-F07`, `S11-F08`
- First harmful stage: none found locally. sample5's K2 rows are within 32 px of the agent estimate, and its out-of-frame changes are the downstream `OIL-PHASE-INITIAL` retrospective and publication aggregates of those rows, which hit a frozen stop condition.
- Existing feature coverage: the production detector path with IFO v2 and top-exit v3 in both arms (the WP09 integrated candidate); the original sample4/base_sample_1/sample2 Recipes, the frozen October 15 interior Recipe and the frozen October 22 empty-fill Recipes; initial states as in run 003; static preparation active; cost-first, RGB, Local XY and the contested gate OFF.
- Execution scope: unit tests with mutation checks, the full suite, and one closed managed local run (six controls, 2 fps, debug NONE) at `9ee11a4`, scored against the frozen predictions. No Windows execution, tuning or post-result rule change.
- Logic-map impact: NONE — this record adds no code; the feature row and 4.3 paragraph were committed with the implementation (`9ee11a4`).
- Failure-registry impact: NONE — co-location changes only an allowance after a recorded owner ambiguity; no new mechanism.
