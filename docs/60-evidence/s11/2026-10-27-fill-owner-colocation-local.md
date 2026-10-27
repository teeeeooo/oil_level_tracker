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
  unchanged.
- **User decision (2026-10-27):** accept the out-of-frame changes and go on to
  the Windows SPL#4 comparison ("1번으로 진행하자. 범위 밖 변경이지만 오히려 신뢰도가 올라가는 변경으로 생각됨").
- **Windows SPL#4 comparison (2026-10-27): PASS** against the frozen
  condition ([receipt](#windows-spl4-comparison--2026-10-27)). Exactly 23.0 and
  23.5 s are co-located and publish Y781.0 and Y757.0, +13.0 and −4.5 px from
  the review-015 marks. Every other row is equal. E4 stays opt-in and default
  OFF.
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

- **Windows effect (local record):** the SPL#4 prediction was untested here;
  the [Windows comparison](#windows-spl4-comparison--2026-10-27) below now
  answers it.
- **Accuracy:** nothing beyond the user's judgments. This is not a promotion.

## User decision — 2026-10-27

**User: "1번으로 진행하자. 범위 밖 변경이지만 오히려 신뢰도가 올라가는 변경으로 생각됨".**
- The user accepts sample5's changes outside the K2 frames as a gain in
  reliability.
- E4 goes on to the Windows SPL#4 comparison.
- The local verdict stays FAIL as recorded; the frozen criteria are not
  edited.

**Next:** the [E4 SPL#4 comparison request](../../40-operations/s11-current-windows-field-qualification.md#e4-spl4-comparison-request)
is queued. E2 → E1 → E3 follow, each frozen before code.

## Windows SPL#4 comparison — 2026-10-27

**Received:** the relayed tables, kept outside Git in the closed managed run
`sample/output/s11-e4-windows-relay-20261027-001`. The bundles stay on
Windows.
- **Runs:** `SPL4_C_ref` `bfc8ed72…` (IFO v2 + top-exit v3) and
  `SPL4_C_coloc` `8b107768…` (+ E4). SPL#4 0–90 s, 2 fps, FULL debug, the
  step-7 session, run with step 7's headless runner pattern.
- **Identity:** the four source hashes match. The relayed
  sequence-resolver hash carries OCR slips (`b`/`8`, `8`/`0`, `8`/`B`), and
  the agent reported a match. The resolver versions are as required, with
  `+fill-owner-colocation-v1` only on the candidate. Video `9f494a6f…`,
  53,165,455 bytes, 30 fps, 7,800 frames; Recipe `8eb2c2fc…`, unmodified.
  181 rows per Glass on both runs; 0 duplicate, missing or timestamp
  mismatches.
- **Also in the reply:** the step-15 readout, re-returned without a rerun. Its
  JSON hash `c39edfd6…` equals the
  [recorded step-15 result](../../50-diagnostics/s11/2026-10-27-fast-rise-owner-desk-review.md#step-15-result--2026-10-27),
  so nothing new.

| Check (frozen with the design) | Result |
|---|---|
| Identity: `SPL4_C_ref` = step-7 `SPL4_B_ref` | **PASS.** 0 differing rows on BASE and Accum |
| Exactly 23.0 and 23.5 s become `FILL_OWNER_COLOCATED` (BASE) | **PASS.** f690/23.0 and f705/23.5 only; BASE `FILL_OWNER_AMBIGUOUS` 10 → 8. Accum has none (35 ambiguous in both) |
| Each publishes a numeric row within 32 px of the review-015 mark | **PASS.** 23.0 s: UNKNOWN → FILLING Y781.0 (mark 768.0, +13.0 px). 23.5 s: UNKNOWN → FILLING Y757.0 (mark 761.5, −4.5 px) |
| Every other BASE and Accum row is equal | **PASS.** BASE differs in those two rows only; Accum differs in none |

**Verdict: PASS.**

**Owner rows in the co-located frames** (allowed set = both owners
`0018` and `0035`):

| Time s | `0018` rows (Y) | `0035` rows (Y) | Selected | Mark |
|---|---|---|---|---|
| 23.0 | 781 | 758, 769, 757 | 781 (`0018`) | 768.0 |
| 23.5 | 766, 757, 765 | 742 | 757 (`0018`) | 761.5 |

At 23.0 s the selector chose `0018`'s Y781 although `0035` had a row at Y769,
1 px from the mark. Both are within the frozen 32 px; the choice is the
existing selector's, unchanged by E4.

**Events and retrospective** (not in the frozen condition; read against
review-015/016, BASE Oil FULL from 27.5 s):
- **Retrospective:** UNRESOLVED on both Glasses in both runs, same reason. No
  change, unlike sample5.
- **BASE events** (Accum unchanged):

  | Event | Reference | E4 |
  |---|---|---|
  | `REVIEW_REQUIRED` (UNKNOWN run) | 22.5–27.0 s | 24.0–27.0 s |
  | `LOW_CONFIDENCE_START` | 23.0–27.0 s | 24.0–27.0 s |
  | Coverage review at 90.0 s | 18.2 % | 19.3 % |

- **Why (from `domain/events.py`):** a `REVIEW_REQUIRED` event covers a run of
  UNKNOWN rows lasting at least 0.5 s. The two new rows split the 22.5–27.0 s
  run. The 22.5 s row stays UNKNOWN, but alone it lasts 0 s, so no event
  covers it now. The low-confidence run (below 0.35) started at 23.0 s and now
  starts at 24.0 s. Coverage rises by 2 of 181 rows.
- **Against the truth:** the two rows follow the reviewed rise (marks 768.0
  and 761.5). 22.5 s (mark 781.5) and 24.0–27.0 s remain unpublished, so FULL
  from 27.5 s is still out of reach, as the barriers in series predicted. The
  one loss is that the 22.5 s UNKNOWN row is no longer inside a review event.

**What it does not show:** a field PASS, a promotion or any FULL. E4 stays
opt-in and default OFF; FIELD FAIL / O2 OPEN and review-006 pending are
unchanged. E2 → E1 → E3 follow, each frozen before code.

## Detector Governance

- Logic-map nodes: `OIL-PHASE-FILL`, `OIL-PHASE-INITIAL`, `OIL-SELECTOR`, `PUBLICATION-PROVENANCE`
- Failure-registry entries: `S11-F04`, `S11-F05`, `S11-F07`, `S11-F08`
- First harmful stage: none found locally. sample5's K2 rows are within 32 px of the agent estimate, and its out-of-frame changes are the downstream `OIL-PHASE-INITIAL` retrospective and publication aggregates of those rows, which hit a frozen stop condition.
- Existing feature coverage: the production detector path with IFO v2 and top-exit v3 in both arms (the WP09 integrated candidate); the original sample4/base_sample_1/sample2 Recipes, the frozen October 15 interior Recipe and the frozen October 22 empty-fill Recipes; initial states as in run 003; static preparation active; cost-first, RGB, Local XY and the contested gate OFF.
- Execution scope: unit tests with mutation checks, the full suite, and one closed managed local run (six controls, 2 fps, debug NONE) at `9ee11a4`, scored against the frozen predictions. Then one Windows comparison (SPL#4 0–90 s, two runs, FULL debug), relayed as text and kept in `s11-e4-windows-relay-20261027-001`, judged on the Mac against the frozen Windows condition. No tuning or post-result rule change.
- Logic-map impact: NONE — this record adds no code; the feature row and 4.3 paragraph were committed with the implementation (`9ee11a4`).
- Failure-registry impact: NONE — co-location changes only an allowance after a recorded owner ambiguity; no new mechanism.
