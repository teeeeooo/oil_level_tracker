# LCR-1 — E3: protecting the initial-state reconstruction from a late first catch

**Status: DESK REVIEW COMPLETE 2026-10-22; the user chose L2 and the step-7
Accum readout ([decision](#decision--2026-10-22)).**
Step 4 (E3) of the Mac-only order in the
[Work Plan](../../00-project/work-plan.md), started by the user on 2026-10-22.
Existing records plus one closed desk run over kept evidence. No rule, detector,
flag or threshold change and no Windows request.

**Result in short:**
- **The gap:** the continuing-run rule accepts the prior over the whole leading
  interval once the first decisive move points toward it. Where the level was
  first caught does not count, so a level caught after an unobserved transit
  still reconstructs the prior up to the catch.
- **The entrance band does not close it:** ⑩ Accum's first catch (Y515) sits
  inside the bottom band (0.787), yet Oil had been entering for 16 s.
- **Recommended, L2:**
  - FULL needs the first catch inside the top band;
  - EMPTY needs it inside the bottom band and within one
    `temporal_max_jump_px` of the effective-mask bottom.
- **Cost:** L2 changes no known real output. ⑩ BASE stays ACCEPTED, and the 24
  kept local streams are unchanged. With L2 applied as a desk patch, the full
  suite passes.

## The gap E3 closes

The limit was recorded when the rule was implemented
([architecture](../../20-architecture/initial-state-retrospective-reconstruction-architecture.md#modern-stream-continuing-run-rule--2026-10-21)):
the Accum protection comes from the Foam barrier and the continuity bound, not
from direction.

- **What ACCEPTED does:** the prior is projected over every sample before the
  first accepted boundary (`project_state_aware_samples`). Those samples become
  valid for coverage and judgment (except RECOVERY and the all-missing hold),
  and the report draws them as `초기 상태 재구성 (…)`.
- **The error leans to PASS:** the prior is the compliant state of the matching
  hold rule:
  - FULL under `HOLD_ABOVE_ZERO` (⑩ BASE);
  - EMPTY under `HOLD_BELOW_ZERO` (⑩ Accum).

  A prefix that runs past the real transition inflates coverage and labels the
  unobserved transit as compliant. It can hide a violation; it never adds one.
- **Why now:** on ⑩ Accum two incidental things blocked a wrong EMPTY prefix to
  669.5 s:
  - five published-Foam rows before the first boundary. Truth says Foam must be
    absent at entry, so this is a false ENTRY-SPLASH Foam (`S11-F07`);
  - a 33 px first step, one pixel over the 32 px limit.

  On sample5 and sample7 the runs also end only on continuity breaks. Detector
  repairs can remove both accidents: D's Accum-entry scope covers the false
  entry Foam, and any repair that tracks the level more continuously removes
  the step breaks.

## What the reconstruction can see

- **Inputs:** only published samples, with state, numeric Y, validity and
  flags. Lifecycle phase reasons such as `INITIAL_EMPTY_ENTRY_PENDING` and
  `FILL_ONSET_INTENT_NO_PREDECESSOR` are not published.
- **Before the first catch on the local fills:** UNKNOWN rows with
  `SEQUENCE_UNAVAILABLE` and R17 markers.
  - sample5 carries `FOAM_COMPONENT_REJECTED` from 0 s, as scene background.
  - sample7 carries rejected or ambiguous Foam flags from 7.5 s, 2 s before
    its catch.
  - No published flag marks a fill onset.
- **So:** the onset before a catch cannot be read from the stream. A protection
  can only use where the first catch sits and how the level moves there.

## First catches on known streams

From the desk run below. The holding region is where the prior can still hold:
- FULL: at or above the top band end (relative 0.32);
- EMPTY: below the effective-mask bottom.

| Stream | Prior | First catch | Relative | Distance to holding region | Next step | Current outcome |
|---|---|---|---:|---:|---:|---|
| ⑩ BASE (received values) | FULL | 548.5 s, Y363 | 0.196 | 0 | 4 px (at rest) | ACCEPTED |
| ⑩ Accum (received values) | EMPTY | 669.5 s, Y515 | 0.787 | 101 px (3.2 steps) | 33 px | UNRESOLVED: Foam barrier; the 33 px step also breaks the run |
| sample5 (water) | EMPTY | 8.5 s, Y819 | 0.940 | 10 px (0.3 steps) | 20 px | UNRESOLVED: a later 195 px step |
| sample7 (milk) | EMPTY | 9.5 s, Y773 | 0.785 | 106 px (3.3 steps) | 59 px | UNRESOLVED: step |
| base_sample_1 (FULL stress) | FULL | 1.0 s, Y400 | 0.615 | 87 px (2.7 steps) | 9 px | CONFLICT |
| sample4 interior (FULL stress) | FULL | 3.5 s, Y855 | 0.691 | 25 px (0.8 steps) | 2 px | UNRESOLVED: barrier |

- **Accum geometry:** taken from the existing ⑩ Accum-shape test
  (`_windows_glass(347.63…, 291.6)`, margin 0.08). The source of those two
  numbers is not recorded. Without any margin, Y515 is still 124 px above the
  ellipse bottom.
- **sample7:** the same position as Accum, inside the band and about three
  steps above the effective-mask bottom.
- **sample5:** caught at the thin layer at the base (FOA-1 estimate at 8.5 s).
- **Not truth:** the FULL-stress controls are mechanism conditions.

## Candidates

The candidates gate only an ACCEPTED continuing-run outcome. Every other
outcome is unchanged. The desk run's files name them A (L1), B (L2), C (L3)
and U (L4).

| Shape (desk run) | Current | L1 band | L2 band + entry step | L3 at rest | L4 region + step |
|---|---|---|---|---|---|
| ⑩ BASE, received | ACCEPTED | ACCEPTED | ACCEPTED | ACCEPTED | ACCEPTED |
| ⑩ Accum, received (Foam, 33 px) | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED |
| Accum without Foam, 30 px first step (synthetic) | **ACCEPTED** | **ACCEPTED** | UNRESOLVED | UNRESOLVED | UNRESOLVED |
| EMPTY caught 10 px above the mask bottom, rising | ACCEPTED | ACCEPTED | ACCEPTED | **UNRESOLVED** | ACCEPTED |
| EMPTY with a standing layer 56 px up, then rising | **ACCEPTED** | **ACCEPTED** | UNRESOLVED | **ACCEPTED** | UNRESOLVED |
| FULL emerging at the mask top, falling | ACCEPTED | ACCEPTED | ACCEPTED | **UNRESOLVED** | ACCEPTED |
| FULL 20 px below the band end, falling | ACCEPTED | UNRESOLVED | UNRESOLVED | UNRESOLVED | ACCEPTED |
| FULL first caught mid-Glass, falling | **ACCEPTED** | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED |

Bold marks a result judged wrong: a late or offset catch accepted, or a sound
catch refused. On all 24 kept local streams, no candidate changes any outcome.

- **L1, the entrance band only** (the existing 0.32/0.68 topology): it would
  reverse the 10/21 decision without closing the gap, because Accum and sample7
  sit inside the bottom band. Rejected.
- **L2, the band plus an entry step for EMPTY:** recommended; below.
- **L3, at rest at the first catch:** it protects Accum. But it refuses the
  usual FULL drain, caught while moving at the top, and accepts an EMPTY glass
  that already holds a standing layer. Rejected.
- **L4, the holding region plus one step for both priors:** close to L2. It
  also accepts a FULL catch up to one step below the band. On a small Glass one
  step is a large share of the height (sample4 interior: 32 of 68 px), and
  nothing caps it.
- **L5, keep the rule:** the protection stays incidental and the risk is
  recorded only.
- **Onset evidence (later):** end the prefix at the first published sign of an
  onset. Today no such sign is published, so this would need a detector
  publication change or Windows evidence of what Accum shows before 669.5 s.
  Without a sign it protects nothing; it is outside E3.

## Recommendation: L2

**Scope:** modern continuing-run streams only. After a first decisive move
toward the prior:
- **FULL:** the first accepted boundary lies at relative ≤ 0.32, the top band
  the rule already records as topology provenance;
- **EMPTY:** the first accepted boundary lies at relative ≥ 0.68 and no more
  than `temporal_max_jump_px` above the effective-mask bottom
  (`center_y + radius_y × (1 − margin_ratio)`);
- **otherwise:** UNRESOLVED, with a reason naming the first catch's position.

**Why the asymmetry:**
- **FULL:** a full glass can show its level inside the top band. The user
  accepted FULL at about 0.18 H below the top on BASE
  ([review-011](2026-10-21-full-observable-top-review.md#review-011-result--2026-10-21)),
  and D2 keeps FULL under the cap until a drain release. A catch there is the
  prior's own level.
- **EMPTY:** an empty glass shows no level. A level first seen more than one
  continuity step above the observable bottom must have been visible earlier.
- **No new threshold:** the step is the run's own continuity assumption, the
  same `temporal_max_jump_px` that already ends a run. The band caps it on small
  Glasses.

**Unchanged:**
- barriers, the run and the decisive move;
- CONFLICT, which is decided before position;
- NOT_APPLICABLE and the all-missing hold;
- legacy R7 streams;
- projection, event and judgment consumption.

**Effect:**
- **Known real outputs:** none change (⑩ BASE/Accum and the 24 kept local
  streams).
- **Synthetic shapes:** a late Accum-like catch, a standing low layer, a FULL
  catch below the band and a FULL catch mid-Glass become UNRESOLVED. Entry
  catches and FULL emergence stay ACCEPTED.
- **Tests:** with L2 as a desk patch, the 163 tests in the nine files that use
  the reconstruction pass unchanged, and so does the full suite (3,846 passed,
  12 skipped). The existing fixtures already catch inside the regions.

**Reverses, for modern streams only:**
- the 10/21 decision "no entrance-topology gate; topology stays provenance
  only";
- the architecture clause "the first anchor may already be mid-Glass".

The R7 contract keeps its mid-Glass case.

**Limits:**
- **Continuity assumption:** L2 relies on it. Where 32 px is a large share of
  the height, the band does the capping.
- **Exclusions:** an exclusion over the glass bottom raises the real
  observable bottom, so L2 becomes stricter (fails closed).
- **Inside the band:** a FULL catch inside the band after a slow unobserved
  fall is still accepted; the band is FULL precision under D2.
- **Accum 480–653 s:** L2 does not recover it (see question 2).

## Questions for the user

1. **The rule:** adopt L2 (recommended), or L4, L1, L3 or L5?
2. **Accum 480–653 s:** [DSR-1](2026-10-22-d-scope-review.md#accum-on-spl1-today)
   routed it to E3 because it publishes UNKNOWN, not EMPTY. L2 cannot recover
   it; that needs onset evidence.
   - **Recommended:** add a read-only item to the step-7 request: Accum rows
     640–672 s (state, flags, Y, Foam Y) and the Accum ellipse (center_y,
     radius_y, margin). Decide after the receipt.

## Decision — 2026-10-22

The user answered both questions:
1. **L2.** It is frozen as the
   [first-catch position guard](../../20-architecture/initial-state-retrospective-reconstruction-architecture.md#modern-stream-first-catch-position-guard--2026-10-22)
   with its
   [acceptance](../../30-validation/initial-state-retrospective-reconstruction-validation.md#first-catch-position-guard--2026-10-22),
   under provenance `initial_state_retrospective_v3`. The steps below follow.
2. **Step-7 readout added.** The combined Windows request reads, without a
   rerun:
   - SPL#1 Accum rows 640–672 s: state, flags, Oil Y and Foam Y;
   - the Accum Glass's center_y, radius_y and margin_ratio, plus its
     `temporal_max_jump_px`, which the guard also uses.

   The 480–653 s question (UNKNOWN, not EMPTY) is decided after the receipt.
   **Receipt (2026-10-23):** the Accum rows hold no observation until 669.5 s.
   The first catch, Y515 (0.787), lies about 124 px above the geometry bottom,
   beyond one 32 px step. So L2 refuses EMPTY, and the span stays UNKNOWN
   without new onset evidence
   ([step-7 receipt](../../60-evidence/s11/2026-10-23-step7-windows-receipt.md#what-the-readouts-answer)).

## If L2 is chosen

1. **Freeze** the rule in the
   [architecture](../../20-architecture/initial-state-retrospective-reconstruction-architecture.md)
   (the continuing-run rule and the positive-evidence clause) and in the
   [validation contract](../../30-validation/initial-state-retrospective-reconstruction-validation.md).
   Record it under a new provenance, `initial_state_retrospective_v3`, so that a
   bundle shows which rule decided.
2. **Synthetic tests:**
   - the shapes above;
   - the ⑩ BASE/Accum regressions;
   - a mutation check: removing the position check must fail the late-catch
     tests.
3. **Implement** in `_continuing_run_interpretation`, then run the
   reconstruction tests and the full suite.

No Windows run is needed. The next Windows report (step 7) will show the rule
in use.

## Desk run

Closed managed run `sample/output/s11-reconstruction-protection-desk-20261022-001`
at `19b3aee`.
- **Kept streams:** the production `reconstruct_initial_state` was replayed on
  the 24 kept row lists, 18 distinct control/arm pairs:
  - six top-exit negative controls;
  - three arms: IFO v2; + top-exit v3; + fill-owner gate.

  Identity with the kept records: 24/24. The duplicated top-exit arms are equal.
- **Shapes:** the ⑩ shapes reuse the existing test values and helpers.
- **Desk-only pytest plugin:** applies L2 or L4 to the continuing-run path.
  - A sanity test fails without the plugin and passes with it.
  - With L2 or L4, the nine reconstruction-consuming test files give 163
    passed.
  - With L2, the full suite gives 3,846 passed, 12 skipped.
- **Kept:** the scripts, the summary JSON, the table and the test outputs.

## Detector Governance

- Logic-map nodes: `PUBLICATION-PROVENANCE`, `RESULT-PRESENTATION`
- Failure-registry entries: `S11-F07`, `S11-F09`, `S11-F10`
- First harmful stage: downstream of the detector. The initial-state reconstruction, consumed by `PUBLICATION-PROVENANCE` (coverage, judgment) and `RESULT-PRESENTATION` (bands), accepts the prior without regard to where the first catch was made. On ⑩ Accum only a false entry Foam (`S11-F07`) and a continuity break prevented a wrong EMPTY prefix.
- Existing feature coverage: reuses the continuing-run rule at `139ba87` (unchanged), the confirmed-initial-state path, the kept comparisons of the six top-exit negative controls in three arms (IFO v2; + top-exit v3; + fill-owner gate) with their frozen Recipes, and the ⑩ BASE/Accum values in the existing tests. No local Recipe has exclusions, so exclusion effects on the observable bottom are not exercised.
- Execution scope: one managed desk run. The production reconstruction was replayed on 24 kept row lists (identity 24/24), candidate predicates were evaluated on first catches and synthetic shapes, and a desk-only pytest plugin applied L2/L4 to nine test files and L2 to the full suite. No detector run, video decode, rule change or Windows request. A later note (2026-10-22) records the user's decision; no run.
- Logic-map impact: NONE — review only; code and owners are unchanged. If L2 is adopted, its implementation updates the `PUBLICATION-PROVENANCE` node detail.
- Failure-registry impact: NONE — accepting a prefix past an unobserved transition is apparent coverage hiding missing evidence, already guarded by `S11-F09`/`S11-F10`; the Foam that blocked it is the known `S11-F07` class. No new mechanism failure.
