# Contested fill-owner gate — local implementation and checks

**Status:** IMPLEMENTED (opt-in, default OFF) / **LOCAL CHECKS PASS** against the
[frozen checks](../../30-validation/s11-physical-interface-evidence-repair-validation.md#contested-fill-owner-gate-checks--2026-10-22)
/ **Windows comparison PASS against its pre-registered prediction** (step 7,
[receipt](2026-10-23-step7-windows-receipt.md#spl4-gate-comparison)).
- **SPL#4:** BASE loses exactly the 14 wrong-target rows (27.5–34.0 s,
  `FILL_OWNER_CONTESTED`). Accum loses one false EMPTY sample (24.5 s). No
  numeric row is added or moved.
- **SPL#1:** no row differs; the gate never acted.
- **Local balance:** 17 wrong sample5 rows removed; 20 correct sample7 rows
  removed. The sample7 loss was pre-registered and accepted by the user.
- **Unchanged:** the gate is not promoted. O2 OPEN / FIELD FAIL is unchanged.
- **Authority:** the [Work Plan](../../00-project/work-plan.md).

## What was built

The [design](../../20-architecture/s11-physical-interface-evidence-repair-design.md#october-22-contested-fill-owner-gate)
was frozen at `8386b45` before any code change and implemented at `2cb0b52`.

**In [`OilMaterialPhaseLifecycleOwner`](../../../src/oil_tracker/adapters/vision/oil_phase_lifecycle.py):**
- **Mark:** the dynamic owners of a `FILL_OWNER_AMBIGUOUS` frame are contested.
  After `_advance_fill_chains`, a chain that lists a contested ID passes the
  mark to its current owner.
- **Gate:** suppose a frame would allow one fill owner, through a motion owner,
  a re-entry, a current-anchor handoff or a single owner under chain
  ambiguity. If that owner, its chain or the anchor successor is contested:
  - the allowed set and owner chain become empty;
  - the reason is `FILL_OWNER_CONTESTED`;
  - the frame is ambiguous;
  - a gated onset does not rewrite earlier frames.
- **State:** chains, the established fill, the barrier and the release
  evaluations proceed as without the gate.
- **End:** marks clear at `FILLED_BARRIER` or `DRAINING`. Fill-span
  completion and drain releases are not gated.
- **Diagnostics:** `fill_owner_contest` (contested IDs and `gated`) appears
  only when the option is ON.

**Switch:**
- **Flag:** `fill_owner_contest` / GUI `--oil-fill-owner-contest`, default OFF,
  suffix `+fill-owner-contest-v1`.
- **Combinations:** it combines with IFO v2 and top-exit v3. The detector
  refuses it with cost-first, RGB or Local XY, and the launcher refuses the
  same flags.

**Other changes:**
- the comparison runner gains `--fill-owner-contest-comparison`. Its
  reference arm is IFO v2 + top-exit v3; the candidate arm adds the gate;
- the [logic map](../../20-architecture/s11-current-detector-logic-map.md)
  gains a feature row and a 4.3 paragraph.

**Lifecycle module SHA-256:**
`69ea87d223139f882bb1426923112876c15691494e169361fa6ba2a7d369e2bf`.

## Tests

- **New unit tests:** 12 in `tests/unit/test_oil_fill_owner_contest.py`, one
  per frozen unit check, plus mark persistence and the integrated-candidate
  combination. Every test asserts identical phases and lifecycle state with
  the option OFF and ON.
- **Mutation checks:**
  - removing the gate fails the four gating tests;
  - removing mark propagation fails the two successor tests.
- **Wiring:** the GUI factory test covers the gate alone and with top-exit on
  all four detector entries. The launch tests cover the flags and the stacked
  refusals, and the constructor-surface guard covers the new parameter.
- **Full suite:** 3,846 passed. 12 skipped: sample3 is quarantined, as before.

## Local checks

**Run:** closed managed run `s11-fill-owner-contest-local-20261022-001` at
`2cb0b52`. Six controls with run 003's Recipes, ROI inputs and initial states,
at 2 fps with debug NONE. The frozen script `contest_checks.py` scored it.

**Failed first invocation:** zsh did not split a command variable, so no
control started. That invocation wrote only a "FAIL: missing" `checks.json`,
which was deleted before the rerun in the same managed run.

| Check | Controls | Result |
|---|---|---|
| Identity anchor | all six | Reference arm equals the kept top-exit arm of runs 001/002: rows, events, report (`run_id` aside) and version |
| C1 identity | base_sample_1-full, sample2-full, sample4-interior-full, sample4-original-unknown | **PASS.** No `FILL_OWNER_AMBIGUOUS`; rows, phases, events, retrospective and report equal between arms |
| C2 removal | sample5-empty | **PASS.** Exactly the 32 predicted frames gated and the 17 predicted wrong rows removed; the 6 other rows unchanged |
| C3 known loss | sample7-empty | **PASS as predicted.** Exactly the 24 predicted frames gated; the 20 user-judged correct rows removed; the 9.5 s row unchanged |
| Stop conditions | all six | None. No row added or moved; Foam, FULL/EMPTY and raw current-frame inputs unchanged |

**Consequences** (allowed by the frozen section, reported here):

| Item | sample5 (reference → gate) | sample7 (reference → gate) |
|---|---|---|
| Numeric Oil rows | 23 → 6 | 21 → 1 |
| Judgment coverage | 20.7 % → 5.4 %; still a user check | 23.3 % → 1.1 %; still a user check |
| Report maximum | 50.0 s → 54.5 s, both wrong targets | 30.0 s (correct) → 9.5 s, the one row left |
| `MAXIMUM_OIL_LEVEL` event | 20.0 s → 54.5 s | 30.0 s → 9.5 s |
| Retrospective | UNRESOLVED in both | UNRESOLVED in both |

- **Retrospective reason:** in both videos it changes from a step above
  `temporal_max_jump_px` to an inference barrier.
- **Other events:** sample7's `FOAM_START` keeps its time and Foam position;
  only its capture file index changes. The low-confidence and review events
  shift with the removed rows.

**Balance:**
- 17 wrong rows removed (sample5);
- 20 correct rows removed (sample7);
- 4 wrong rows kept (sample5's fresh low start, as predicted).

## What this does not show

- **Windows effect:** the SPL#4 prediction (14 rows at 27.5–34.0 s) and
  SPL#1's rows after any `FILL_OWNER_AMBIGUOUS` are untested.
- **Accuracy:** nothing beyond the user's judgments. This is not a promotion.

## Next

- **Step-7 Windows request:**
  - SPL#4 0–90 s, reference vs candidate;
  - SPL#1 under ⑩ conditions, reference vs candidate;
  - every changed row listed with its phase reason and owner.
- **Mac-only order:** continues with E3, then B.

## Detector Governance

- Logic-map nodes: `OIL-PHASE-FILL`, `OIL-PHASE-INITIAL`, `OIL-SELECTOR`, `PUBLICATION-PROVENANCE`
- Failure-registry entries: `S11-F04`, `S11-F05`, `S11-F07`, `S11-F08`, `S11-F10`
- First harmful stage: sample5, `OIL-PHASE-FILL`: a survivor of `FILL_OWNER_AMBIGUOUS` became the publishing owner by attrition (the 17 removed rows); its 4 remaining wrong rows come from a fresh lower-entrance chain, also `OIL-PHASE-FILL`, not addressed. sample7, `OIL-PHASE-FILL` owner counting: the front and back arcs of one obliquely viewed surface (user) became two owners, so the ambiguity was false and the gate removes a correct survivor.
- Existing feature coverage: production detector path with IFO v2 and top-exit v3 in both arms (the WP09 integrated candidate); the original sample4/base_sample_1/sample2 Recipes, the frozen October 15 interior Recipe and the frozen October 22 empty-fill Recipes; initial states as in run 003; static preparation active; cost-first, RGB and Local XY OFF.
- Execution scope: unit tests with mutation checks, the full suite and one closed managed local run (six controls, 2 fps, debug NONE) at `2cb0b52`, scored by the frozen predictions. No Windows execution, tuning or post-result rule change.
- Logic-map impact: NONE — this record adds no code; the logic-map row and paragraph were committed with the implementation (`2cb0b52`).
- Failure-registry impact: NONE — the attrition path is an instance of F04, F05 and F08, and sample7's false ambiguity of F07's projected-arc rule; no new mechanism.
