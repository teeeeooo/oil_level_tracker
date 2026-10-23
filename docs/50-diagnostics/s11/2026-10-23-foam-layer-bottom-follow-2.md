# FLB-2 — bounded Foam-layer-bottom follow, held out on Windows Accum (desk emulation)

**Status: FROZEN 2026-10-23, before the held-out data is read.** Frozen in the
commit that adds this file. The user holds the step-7 Windows results,
including review-012 (table V) and the SPL#1 Accum tables F/H, and chose to
share them only after this freeze ("고정 먼저하자", 2026-10-23). Successor to
[FLB-1](2026-10-23-foam-layer-bottom-follow.md), which closed without design.
This is a read-only desk emulation, not a detector change; a result only
decides whether a frozen detector design is worth writing.

## What changes from FLB-1

FLB-1's FOLLOW state worked on sample4; its controls failed on the hand-off and
the witness. FLB-2 changes exactly those two parts, plus an entry guard:

| Part | FLB-1 | FLB-2 |
|---|---|---|
| Witness | any eligible Foam front with a component bottom | only `foam_material_phenotype` = `detached_layer` |
| Hand-off memory | never expires | expires 3.0 s after the last witness |
| Entry (from NONE or HANDOFF) | always (HANDOFF: within T of the last output) | only with no rule output in the last 3.0 s, or B within T of the most recent one |

## Rule (frozen)

Per Glass and frame, on the detector's own same-frame values. Tool:
`tests/diagnostics/s11_foam_layer_bottom_follow.py` (`layer_witness`, `follow2`).

- **Witness:** an eligible (`sequence_foam_eligible`) Foam front candidate with
  phenotype `detached_layer` and a recorded `material_component_bottom_y` B;
  with several, the one with the highest front.
- **Parameters, existing only:**
  - T = `foam_material_identity_tolerance(glass)`;
  - J = the Recipe `temporal_max_jump_px`;
  - M = 3.0 s, the existing `ORDERED_LOWER_INTERFACE` Foam seed-age limit
    (`oil_phase_identity`).
- **Acceptance of a witness:**
  - in FOLLOW, only within J of the last B;
  - otherwise, only if the rule published no number in the last M, or B lies
    within T of its most recent number.

  A rejected witness counts as no witness.
- **States:**
  - **NONE:** the ordinary output stands.
  - **FOLLOW:** publish the same-frame eligible Oil row nearest to B within T,
    a tie going to the lower row; with no such row, nothing (`FOLLOW_NO_ROW`).
  - **HANDOFF** (no accepted witness after FOLLOW): publish the ordinary output
    only if it lies at or below (last B − T); otherwise nothing. HANDOFF
    returns to NONE once the last accepted witness is more than M old.
- **Provenance:** every published value is an existing same-frame Oil
  candidate row or the ordinary output; nothing is interpolated or carried.

## Seen cases (design, not evidence)

These shaped the rule and are stated as seen. Design readout:
`sample/output/s11-flb2-design-readout-20261023-001` (closed;
`flb2-design-readout.json` SHA-256
`db758947f5d6be44a928c7a562d127086837e933cb5567ce8e2fff75d10de2c3`).

**sample4** (saved P5 capture, LBT-2 ordinary arm; T 5.0 px, J 32 px), scored
as in FLB-1:

| Arm | C | A | B | U |
|---|---:|---:|---:|---:|
| Ordinary | 10 | 4 | 1 | 0 |
| FLB-2 | 14 | 0 | 1 | 1 |

- **Same as FLB-1:** 40.0, 42.0, 54.0 and 54.5 s become C; 55.0–56.0 s stay C
  through the hand-off; 51.0 s publishes Y834 (U).
- **Differs from FLB-1:**
  - 44.0 s: the wrong Y822 becomes nothing (B), not Y844 (C);
  - 51.5 s publishes nothing (FLB-1: Y829, U).
- **Changed rows:** 18 frames at 39.5–54.5 s; 17 are `FOLLOW_LAYER_BOTTOM`, and
  44.0 s is a hand-off removal. Layer witness on 25 frames, rule active on 34.

**Controls** (the four FLB-1 controls, ordinary entry):

| Control | T px | Any eligible witness | Layer witness | Active | Changed |
|---|---:|---:|---:|---:|---|
| base_sample_1 | 5.0 | 0 | 0 | 0 | none |
| sample2 | 5.0 | 1 | 1 | 0 | none |
| sample5 (water) | 6.168 | 18 | 0 | 0 | none |
| sample7 (milk) | 7.272 | 7 | 3 | 0 | none |

The phenotype removes sample5's witnesses. The entry guard rejects the
sample2 and sample7 layer witnesses, which lie far from the recent output.
These controls are now design cases too.

## Bundle reader check

The held-out case runs on saved Windows bundles, so the tool reads a FULL
debug trace instead of a live capture (`bundle_frames`, CLI `--bundle`).
The check ran `--bundle-check`: one FULL-debug sample4 0–56 s analysis through
the headless bundle path (AnalysisPipeline + OutputBundleStore +
JsonlDebugTraceWriterFactory).

- **Result, 113 frames:** no differing field between the bundle reader and
  the run's own capture; parameters equal; `follow2` identical (25 witness
  frames, 34 active).
- **CLI:** `--bundle` on the same bundle prints the 18 changed rows above.
- **Runs:** `sample/output/s11-flb2-bundle-check-20261023-001` and `-002`
  (closed). In -002, `flb2-bundle-check.json` is reused from -001
  (byte-identical, SHA-256
  `39c84be838fdfd7398fc0b1bc0b4b1addb7e1fb3cfbf17a49e8d6599df4b4ca1`), and the
  CLI output and log are kept.
- **Later edits:** only the Mac-side scoring (`review_references`,
  `held_out` and the `not_visible` class), with 10 focused unit tests.

## Held-out case and inputs

- **Primary, held out:** SPL#1 Accum review-012, 672.0–677.5 s
  (`WS1-ACCUM-FOAM-LAYERED`), from the step-7 `SPL1_B_ref` bundle (IFO v2 +
  top-exit v3, FULL debug). Unseen by this design: no Accum frame, table or
  mark was read for FLB-2.
- **Controls:** SPL#1 BASE (`SPL1_B_ref`), and SPL#4 BASE and Accum
  (`SPL4_B_ref`). Every changed row is listed.
- **Windows step:** the [FLB-2 request](../../40-operations/s11-current-windows-field-qualification.md#flb-2-held-out-request)
  runs `--bundle` on the saved bundles (no detector run) and returns text only.

## Scoring (frozen)

- **References:** review-012 table V, transcribed from the OCR'd reply and
  checked against its listed marks. Per frame:
  - with marks, the y range widened by C1 on both sides, where C1 = 5 % of
    the Accum Recipe diameter (2 × `radius_y`, printed by the tool);
  - the user's words set the class: 대략 = approximate, 최하단 =
    Foam-region bottom, none = clear;
  - "안 보임" (not visible): no output is C and a number is A;
  - neither marks nor words: not scored.
- **Arms:** ordinary (`SPL1_B_ref` `raw_oil_air_level_y`) and FLB-2, as printed.
- **Classes:** C right, A wrong value, B miss, U a value without a reference
  (`outcome`, `held_out`).

## Reading, fixed before the held-out data is read

- **R1, no harm:** no clear-mark frame turns from C to A or B.
- **R2, benefit:** FLB-2 has fewer A+B than the ordinary arm on the scored
  frames.
- **R3, tested:** at least one scored frame is `FOLLOW_*`.
- **R4, controls:**
  - SPL#1 BASE has no changed row;
  - the other changed rows are read against the reviewed truth: SPL#1 against
    `windows_sample1_heating_coldstart.reviewed-truth.json`, SPL#4 against the
    user's 2026-10-22 review in the top-exit promotion evidence;
  - a removed numeric row inside a visible-interface segment is a loss, and an
    added numeric row inside a FULL, EMPTY or wrong-target span is a false
    output; R4 fails on either;
  - changed rows in unreviewed spans are listed for the user and neither pass
    nor fail.

**Outcomes:**
- **Worth a frozen detector design:** R1–R4 all hold.
- **NOT TESTED:** R3 fails. Record it and close FLB-2; no design.
- **Closed without design:** any other failure.
- **Either way:** no tuning of T, J, M, the witness, the guard or the states
  after the data is read, and no detector change. A pass is not adoption; a
  design would cross `FOAM-IDENTITY` and `OIL-AUTHORITY` (`S11-F06`) and needs
  its own frozen protocol and Windows qualification.

## Detector Governance

- Logic-map nodes: `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-SELECTOR`
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F06`
- First harmful stage: not claimed; SBD-1 records the sample4 events. FLB-2 tests whether a layer-specific Foam-bottom witness with a bounded hand-off keeps one Oil owner through a Foam layer (`S11-F04` explicit hand-off) without Foam masking or replacing Oil (`S11-F06`): the published value stays a same-frame Oil candidate row or the ordinary output.
- Existing feature coverage: reuses the Foam front candidate's existing eligibility, `foam_material_phenotype` and `material_component_bottom_y`; `foam_material_identity_tolerance`; the Recipe `temporal_max_jump_px`; the existing 3.0 s `ORDERED_LOWER_INTERFACE` seed-age limit; the saved P5 sample4 capture, the FLB-1 controls and their readout; the FULL debug trace and tracking rows of saved bundles; review-012 through `s11_review_zoom`. Top-exit stays as recorded in the step-7 reference runs; the fill-owner gate and LBT-1/LBT-2 consumers are not involved; no Recipe or session change.
- Execution scope: local design readout and two bundle reader checks (managed runs, closed) and focused unit tests before the freeze; one Windows text request that only reads saved bundles. No detector change, rerun on Windows, tuning or field disposition change.
- Logic-map impact: NONE — a diagnostic emulation under tests/diagnostics; no production owner or edge changes.
- Failure-registry impact: NONE — no runtime mechanism; any later design would state its difference from `S11-F04`/`S11-F06`.
