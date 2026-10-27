# OAR-1 — is an admitted interface above the fill owner a cue for the stale low owner?

**Status: LOCAL COMPLETE 2026-10-27; Windows readout QUEUED.** This is design
input for the
[E2 draft](../../20-architecture/s11-physical-interface-evidence-repair-design.md#october-27-undercut-fill-owner-e2),
started on the user's "시작하자" (2026-10-27). It is read-only: no detector,
flag, threshold or Recipe change.

**Result in short:**
- **Candidates of any tier above the owner are no cue.** They sit above the
  owner in almost every frame on every video.
- **An admitted tracklet more than one association step (32 px) above the
  owner is a usable cue** on sample5 and sample7:
  - sample5: it catches 20 of the 21 agent-wrong rows and none of the correct
    ones;
  - sample7: it catches 9 user-judged correct rows (the oblique back arc);
  - the other controls: nothing.
- **SPL#4 and SPL#1 are unknown** until the
  [Windows readout](../../40-operations/s11-current-windows-field-qualification.md#e2-owner-above-readout-request).

## Question

The fast-rise desk review proposed E2: fail closed when candidates persist
above a low fill owner. Two things must be known before a rule can be frozen:
- which candidates above the owner separate a stale low owner from a correct
  one;
- what that cue would remove on each control.

## Method

- **Run:** closed managed run `s11-e2-owner-above-readout-20261027-001` at
  `5ade199`.
  - **Controls:** the six fill-owner controls with the contested gate's
    Recipes, ROI inputs and initial states, at 2 fps with debug NONE.
  - **Arms:** the comparison runner's E4 mode with `--owner-readout`, which
    gives both the IFO v2 + top-exit v3 arm and the +E4 arm.
- **Tool:** the new read-only
  [`tests/diagnostics/s11_owner_above_readout.py`](../../../tests/diagnostics/s11_owner_above_readout.py)
  (SHA-256 `21adc0dc…` for the local run; `5f31ad21…` after it adds the
  `--context` near-miss listing, with the frame rule unchanged), with unit
  tests in `tests/unit/test_s11_owner_above_readout.py`. It reads a comparison file
  locally or a saved FULL-debug bundle on Windows, with the same frame rule.
- **The frame rule** applies to a row that both:
  - publishes numeric Oil;
  - has a single-owner fill reason: `FILL_MOTION_OWNER`,
    `FILL_PHASE_REENTRY`, `FILL_CURRENT_ANCHOR_HANDOFF`, the single owner of
    `FILL_CHAIN_AMBIGUOUS`, or `FILL_OWNER_COLOCATED`.

  Such a row is a hit when an Oil candidate of the same frame meets all of
  these:
  - its tracklet is admitted;
  - it is outside the allowed set and the owner chain;
  - it lies more than the Recipe step (`temporal_max_jump_px`) above every
    candidate of the allowed owners.
- **Truth:**
  - sample5: the FOA-1 agent surface estimates and FOA-1's 21 wrong rows.
  - sample7: the user's judgment that 0016 (22.0–31.5 s) is correct
    (2026-10-22).

## Results

**First reading, from the kept FOR-1 readouts:** in every published frame on
sample5 and sample7, 11–26 Oil candidates lie above the published row. Most
are untracked or unadmitted, such as fixed structure near Y370–390. So "any
tier" cannot be the cue, and the rule reads admitted tracklets only.

| Control | Single-owner published rows | Hits | Reading |
|---|---:|---:|---|
| sample5 (reference arm) | 23 | 20 | 17 of 17 attrition rows; 3 of 4 fresh-low rows (24.5, 25.5, 54.0 s). 54.5 s has no admitted row above. The two agent-correct rows (8.5, 9.0 s) are not hits |
| sample5 (+E4) | 25 | 20 | the same 20; E4's two added rows (9.5, 10.0 s) are not hits |
| sample7 (both arms) | 21 | 9 | 0016's rows at 26.5–29.0 s and 30.5–31.5 s, user-judged correct. The admitted 0019, the back arc, lies 60–89 px above |
| sample4-original-unknown | 13 | 0 | — |
| base_sample_1, sample2, sample4-interior | 0 | 0 | FULL starts publish no single-owner fill row, so these controls do not exercise the cue |

**Gaps on sample5's hits** (largest per frame):
- 124–234 px in 18 frames;
- 20.0 s 34 px and 54.0 s 35 px, only 2–3 px beyond the step.

**Admitted tracklets above** sample5's wrong owners include 0060, which the
FOA-1 design notes as an admitted level that could not own the fill under the
EMPTY initial state, and 0086–0101.

## Reading

- **On these two videos the cue separates by reason, not by history.** The
  contested gate removed 17 wrong and 20 correct rows. This cue would remove
  20 wrong and 9 correct.
- **sample7's cost remains.** An oblique back arc is admitted and lies more
  than one step above the front arc (`S11-F07`). The cue cannot tell it from a
  second surface.
- **The negative evidence is thin.** Only 13 single-owner rows outside
  sample5 and sample7 exist locally, all on sample4-original-unknown.
- **SPL#4 decides the value.** At 27.5–34.0 s the glass is FULL (review-016).
  If no admitted tracklet lies above 0018 there, E2 does nothing for the
  user's case.

## Next

The read-only
[E2 owner-above readout request](../../40-operations/s11-current-windows-field-qualification.md#e2-owner-above-readout-request)
runs the same tool on the saved step-7 and E4 bundles:
- SPL#4 `SPL4_B_ref` (BASE, Accum) and `SPL4_C_coloc` (BASE);
- SPL#1 `SPL1_B_ref` (BASE, Accum).

Its result fills the draft's SPL#4 and SPL#1 predictions, and the user then
decides whether E2 is frozen.

## Detector Governance

- Logic-map nodes: `OIL-PHASE-FILL`, `OIL-TRACKLET`, `OIL-SELECTOR`
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F05`, `S11-F07`, `S11-F08`
- First harmful stage: `OIL-PHASE-FILL` publishes a single low owner while an admitted interface lies above it (sample5's 20 rows; sample7's 9 correct rows show the `S11-F07` limit). SPL#4 is not read yet.
- Existing feature coverage: the production detector path with IFO v2 and top-exit v3, with and without E4; the original sample4/base_sample_1/sample2 Recipes, the frozen October 15 interior Recipe and the frozen October 22 empty-fill Recipes; initial states as in run 003; static preparation active; cost-first, RGB, Local XY and the contested gate OFF.
- Execution scope: one closed managed local run (six controls, owner readouts, debug NONE) and a new read-only readout tool with unit tests; no detector code change, tuning or Windows execution.
- Logic-map impact: NONE — diagnostics only.
- Failure-registry impact: NONE — no new mechanism; the oblique-arc cost is `S11-F07`.
