# Fast-rise association — local implementation and checks

**Status: IMPLEMENTED (opt-in, default OFF) / LOCAL CHECKS FAIL against the
[frozen checks](../../30-validation/s11-physical-interface-evidence-repair-validation.md#fast-rise-association-checks--2026-10-23).**
- **F1 and F4 pass:** no change on any control.
- **F2 and F3 fail:** the seed never fired on the stand-ins.
- **Unchanged:** nothing is retuned. The option stays default OFF and is not
  adopted. O2 OPEN / FIELD FAIL is unchanged.
- **Authority:** the [Work Plan](../../00-project/work-plan.md).

## What was built

The [design](../../20-architecture/s11-physical-interface-evidence-repair-design.md#october-23-fast-rise-association)
was frozen at `663e1e9` and implemented at `4f0665b`.
- **Code:** `DirectedInterfaceTrackletBuilder._fast_rise_seeds` and the
  marked-tracklet branch in `_match_cost`.
- **Witness:** `_independent_witness`, factored out of
  `_representation_bridge` without a behaviour change.
- **Plumbing:** the GUI flag `--oil-fast-rise-association`, the version
  `+fast-rise-association-v1`, and the refusals of cost-first, RGB and
  Local XY.
- **Diagnostics:** `sequence_fast_rise_seed_frames` appears only when the
  option is ON.
- **Tests:**
  - 13 synthetic tracklet and wiring tests in
    `tests/unit/test_oil_fast_rise_association.py`;
  - extended GUI launch and production-signature tests;
  - the full suites: unit 2487, GUI launch 33, other 1224 passed and 12
    skipped.

## Local checks

One closed managed run, `sample/output/s11-fast-rise-local-20261023-001`, at
`4f0665b`. `checks.json` has SHA-256
`d3072765c6d3a4031dd70257012082364a009ec0a3a36a046d6884063ee0f9f7`.

| Check | Input | Result | Verdict |
|---|---|---|---|
| F1 no change | six top-exit negative controls, 2 fps, IFO v2 + top-exit v3 with and without the option | rows, phases, events and report equal; no seed; each reference arm equals the gate local run's kept top-exit arm | **PASS** (6/6) |
| F2 stand-in, cadence | sample5 at 0.5 fps | no seed; L 0.400 → 0.400 (needs ≥ 0.494); no row changed | **FAIL** |
| F3 stand-in, cap | sample5 at 2 fps, cap 9 px | no seed; L 0.059 → 0.059; no row changed | **FAIL** |
| F4 under the cap | sample7 at 0.5 fps | identical to the cause-check arm; no seed | **PASS** |

## Why no seed fired (post-result diagnosis, no tuning)

`seed_stages.py` counts each seed condition in the same runs. It writes
stdout only, kept as `seed-stages.txt`.

| Stand-in | Frames with a single-row A, B and a leftover row | Rows considered | Anchor-eligible | Motion ≥ 0.5 / 0.5 | Witnessed | Upward beyond-cap triplets | Constant velocity |
|---|---:|---:|---:|---:|---:|---:|---:|
| sample5 0.5 fps | 2 of 29 | 88 | 1 | 74 | 0 | 0 | 0 |
| sample5 cap9 | 40 of 111 | 450 | 34 | 359 | 26 | 2 | 2 (neither witnessed) |

- **The witness is the main blocker.** Registered motion is plentiful, but
  the stand-in rows are almost never anchor-eligible. That is the authority
  the witness requires.
- **The rows rarely form a line.** sample5 is turbulent water (±40–50 px,
  FOA-1). At 0.5 fps no upward triplet beyond the cap forms at all. With the
  9 px cap only two constant-velocity triplets form, at about 10–23 px per
  sample.
- **So the stand-ins do not test the design.** The design is safe on every
  local control (F1, F4), but there is no local evidence that it admits a fast
  rise.

## What it means

- **No retuning:** loosening the witness after seeing the stand-ins would be
  a post-result change. A weaker witness would also raise the `S11-F04` risk
  the design rests on.
- **The question is SPL#4.** The frozen Windows step starts with a read-only
  readout of every Oil candidate in SPL4_B_ref at 20.5–25.5 s, with the
  witness fields. That shows whether a witnessed triplet exists. It joins the
  held LBT-2 S2 request.
- **Choices for the user:**
  1. keep the option inert and default OFF, and wait for the SPL#4 readout;
  2. write a successor protocol with a different witness (the stand-ins are now
     seen);
  3. close option 2 and accept UNKNOWN on fast fills (FFF-1 option 4).

## Windows readout tool — 2026-10-26

Added before the SPL#4 readout. The frozen checks are unchanged.

`tests/diagnostics/s11_fast_rise_readout.py --bundle` serves their first
Windows step, the read-only SPL#4 readout.
- **What it reads:** it rebuilds each frame's row hypotheses from the FULL
  debug trace. These are the builder-eligible Oil candidates (post-track tier
  ≥ CONTINUATION) in their `row_hypothesis_id` groups, joined to their
  detector features on source and Y.
- **What it applies:** the seed's row conditions, with the production
  tracklet policy and the `_independent_witness` minima:
  - both steps upward, beyond the cap and within 3× it;
  - constant velocity;
  - a shared representation;
  - the witness on all three rows.
- **What it cannot test:** the seed's tracklet conditions (single-row,
  unassigned A and B; uniqueness), which only a run can. A qualifying
  triplet is therefore necessary for a seed, not sufficient.
- **Local check, PASS** (managed run
  `sample/output/s11-fast-rise-readout-check-20261026-001`): on a sample5 2 fps
  FULL-debug bundle (IFO v2 + top-exit v3), the reader rebuilt all 722 live
  builder rows with zero differences, the witness included.
  - 46 rows were witnessed, and 0 triplets qualified.
  - The tool's own unit tests are in `tests/unit/test_s11_fast_rise_readout.py`.
- **The rule for the next step, fixed before the readout** (user:
  "그렇게 진행하자", 2026-10-26):
  - one or more qualifying triplets on SPL#4 BASE: the Mac proposes the
    SPL#4 run to the user;
  - none: no SPL#4 run. The user chooses between a successor witness
    protocol and closing option 2 (accept UNKNOWN on fast fills).
  - The stage counts name the blocker (witness or geometry), as on the
    stand-ins.
- **Request:** the
  [step-8 combined request](../../40-operations/s11-current-windows-field-qualification.md#step-8-combined-request),
  together with LBT-2 S2.

## Detector Governance

- Logic-map nodes: `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`
- Failure-registry entries: `S11-F02`, `S11-F03`, `S11-F04`, `S11-F05`
- First harmful stage: unchanged from FFF-1. The association cap at `OIL-TRACKLET` stops level admission, confirmed locally. The fast-rise route does not reach it on the stand-ins because their rows lack the anchor-eligible witness and rarely form a constant-velocity line.
- Existing feature coverage: the six top-exit negative controls with their frozen Recipes, ROI inputs and initial states (IFO v2 + top-exit v3 as the reference arm), the FFF-1 cause-check arms and surface estimates, the comparison runner and cadence tool with their new fast-rise modes, and the existing `_independent_witness` predicate. No Recipe or session change.
- Execution scope: one closed local managed run at `4f0665b` (six controls at 2 fps and three stand-ins, debug NONE), the frozen F1–F4 check script and a post-result stdout stage count; no Windows run, no tuning. Readout tool (2026-10-26): `s11_fast_rise_readout.py` with unit tests and one closed local managed run (`s11-fast-rise-readout-check-20261026-001`, sample5 2 fps FULL debug, reader against the live builder); the Windows readout waits in the step-8 request.
- Logic-map impact: NONE — this record adds results; the feature row and 4.2 paragraph were committed with the implementation (`4f0665b`).
- Failure-registry impact: NONE — the option changes nothing on the local runs; the stand-in finding is an availability limit of the witness, not a new failure mechanism.
