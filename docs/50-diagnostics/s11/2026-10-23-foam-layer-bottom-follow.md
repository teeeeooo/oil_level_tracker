# FLB-1 — Oil follows the dense-Foam layer bottom, then hands off explicitly (desk emulation)

**Status: PROTOCOL FROZEN 2026-10-23 before any run.** Asked by the user on
2026-10-23 after [SBD-1](2026-10-23-strict-boundary-early-drop.md): can one
track follow the boundary down, instead of a lower-structure tracklet taking
over? This is a read-only desk emulation, not a detector change; a result
only decides whether a frozen design is worth writing.

## Why

- **Strict rule (user, 2026-10-23):** inside a Foam layer the Oil boundary is
  the dense-Foam bottom.
- **The detector already measures it:** every Foam front candidate records the
  Foam component's bottom (`material_component_bottom_y`). A first readout
  (2026-10-23, stdout only) put it within 3 px of every strict sample4
  reference at 40–54.5 s, including frames where the output is wrong
  (40/42/44 s, 54.0–54.5 s).
- **The signal ends at 55 s:** the Foam candidate turns ineligible (Y883) and
  then reads Y837–838 (the 2026-10-09 internal-texture rows), while the user
  marks the Foam region's bottom at Y854–858, where the rough boundary already
  lies. So the descent itself is a disappearance plus a handoff, not one
  continuous track.

**Not unseen:** that readout and SBD-1 shaped the rule, so sample4 is a design
case. The four controls are not yet read. Windows Accum 672–680 s
(review-012, in the
[step-7 request](../../40-operations/s11-current-windows-field-qualification.md#step-7-combined-request))
is the intended held-out case.

## Rule (frozen)

Per Glass and frame, on the detector's own same-frame values. Tool:
`tests/diagnostics/s11_foam_layer_bottom_follow.py` (`follow`).

- **Witness:** an eligible Foam front candidate (`sequence_foam_eligible`) with
  a recorded component bottom B; with several, the one with the highest front.
- **Parameters, existing only:** T = `foam_material_identity_tolerance(glass)`
  (5.0 px on sample4) and J = the Recipe `temporal_max_jump_px` (32 px).
- **States:**
  - **NONE:** no witness yet. The ordinary output stands.
  - **FOLLOW:** a witness exists. Publish the same-frame eligible Oil row
    nearest to B within T, a tie going to the lower row. With no such row,
    publish nothing (`FOLLOW_NO_ROW`).
  - **HANDOFF:** the witness is gone, or B moved more than J from the last B.
    Publish the ordinary output only if it lies at or below (last B − T);
    otherwise publish nothing.
  - **Re-entry:** from HANDOFF, FOLLOW resumes only when B lies within T of
    the last published Oil Y (else of the last B).
- **Provenance:** every published value is an existing same-frame Oil
  candidate row or the ordinary output; nothing is interpolated or carried.

## Inputs

- **sample4:** the saved P5 capture replayed through the SOI entry (the LBT-2
  ordinary arm), 38.0–56.0 s.
- **Controls, descriptive:** base_sample_1, sample2, sample5 and sample7
  through LBT-2's ordinary analysis entry, with a read-only copy of each
  detection's candidates. No reference exists; every changed row is listed.

## Scoring (frozen)

Strict sample4 references, each matched within C1 (5.2 px):
- P0/LBT-1 accepted and wrong values at 38.0, 40.0, 42.0, 42.5, 44.0, 49.5 and
  52.0 s;
- LBQ-1 42.5 s Y805 (wrong); CAF-1 51.0–52.0 s Y861.5–862 (wrong);
- review-014 bands at 52.0–56.0 s, tagged clear (52.0–53.5 s), approximate
  (54.0–54.5 s) or Foam-region bottom (55.0–56.0 s).

Classes per frame and arm: C right, A wrong value, B miss (nothing published
where a positive reference exists), U a value without a matching reference.

## Reading, fixed before the run

- **Worth a frozen design** if all hold:
  1. no clear reference frame turns from C to A or B;
  2. the 54.0–54.5 s frames become C, and 55.0–56.0 s stay C;
  3. every control change is listed and either absent or explained by a
     visible Foam layer in that frame.
- **Otherwise:** record why and close FLB-1 without a design.
- **Either way:** no tuning of T, J, the witness or the states after the
  results; no detector code changes.

## Detector Governance

- Logic-map nodes: `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-SELECTOR`
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F06`
- First harmful stage: not claimed here; SBD-1 records the 54.0–54.5 s events. FLB-1 tests whether a Foam-bottom witness could keep one Oil owner through them (`S11-F04` explicit handoff) without Foam masking or replacing Oil (`S11-F06`): the published value stays a same-frame Oil candidate row.
- Existing feature coverage: reuses the Foam front candidate's existing eligibility and `material_component_bottom_y`, `foam_material_identity_tolerance`, the Recipe `temporal_max_jump_px`, the saved P5 sample4 capture with the SOI replay entry, LBT-2's ordinary analysis entry for the four descriptive controls, and the strict references (P0/LBT-1 controls, LBQ-1, CAF-1, review-014). Top-exit, the fill-owner gate and LBT-1/LBT-2 consumers stay off; no Recipe or session change.
- Execution scope: planned — one managed local run: the sample4 replay (no video decode) and four control analyses through the ordinary entry at 2 fps with debug BASIC, each with a read-only candidate copy; result JSON kept. Focused unit tests run before the freeze. No detector change, tuning or Windows run.
- Logic-map impact: NONE — a diagnostic emulation under tests/diagnostics; no production owner or edge changes.
- Failure-registry impact: NONE — no runtime mechanism; any later design would state its difference from `S11-F04`/`S11-F06`.
