# FER-1 — where does the image FULL evidence stop? (path F readout)

**Status: READINGS FROZEN 2026-10-27, before any output.** Nothing has run.
This is the read-only readout that
[OFF-1](2026-10-27-owner-free-full-review.md#what-must-be-read-before-any-design-proposed-readout-not-frozen)
proposes, run on the user's "시작하자" (2026-10-27). It changes no detector,
flag, threshold or Recipe.

## Question

Path F (OFF-1's candidate F1) would publish an ownerless FULL from the
existing per-frame `full` state node. The
[OFF-1 correction](2026-10-27-owner-free-full-review.md#correction-after-compaction-an-earlier-gate-source-desk-check-2026-10-27)
found that this node is gated three times before selection:
1. **Gate 1:** the frame outcome is no-interface. Absence must be ≥ 0.58 and
   ≥ 0.10 above the best boundary hypothesis. Otherwise the traced FULL
   likelihood is 0.0.
2. **Gate 2:** the FULL likelihood is ≥ 0.58 (the state evidence threshold),
   which creates the `full` node.
3. **Gate 3:** the lifecycle's allowed set is not empty (`allowed_mode` is
   not `hard_gate`).

F1 lifts only gate 3. **Does the user's case (SPL#4 BASE, Oil FULL
27.5–63 s) pass gates 1 and 2?** And where would an F1 fire on cases that are
not full?

## Method

- **Tool:** the new read-only
  [`tests/diagnostics/s11_full_evidence_readout.py`](../../../tests/diagnostics/s11_full_evidence_readout.py),
  with unit tests in `tests/unit/test_s11_full_evidence_readout.py`.
- **Per frame it reads:**
  - the raw outcome status and reason;
  - absence, boundary, and their difference;
  - the outcome Y, as traced (`oil_temporal_projected_source_y`);
  - the FULL and EMPTY likelihoods and whether a `full` node exists;
  - **the first gate that fails** (`gate1:<status or cause>`,
    `gate2:full_below`, `gate3:hard_gate`, `selection:<kind>`, `selected`);
  - the phase, its reason and `allowed_mode`;
  - the resolved kind and the published fill state;
  - the source of a published FULL (image node or top-exit);
  - eligible Foam fronts and admitted Oil rows.
- **Limit:** for a boundary-accepted frame the outcome reports absence as 0.0,
  so absence is not traced there.
- **Sources:**
  - **Windows:** the saved step-7 FULL-debug bundles `SPL4_B_ref` and
    `SPL1_B_ref`, the same as the E1 rerun. The tool reads each record's frame
    metrics and its sequence snapshot.
  - **Local:** the six fill-owner controls, reference arm, as in FPC-1.
- **Correctness check before the Windows request:** on a scratch local
  FULL-debug bundle of one control, the bundle path must equal the local path
  in every row. This tests the tool, not the question.

## Frozen readings

**The sustained unit** is a run of at least 3 consecutive rows with a `full`
node (1.5 s at 2 fps). OFF-1's K is open; 3 is the reading unit, not a
choice of K. The tool also prints the longest run.

**R1, the user's case: SPL#4 BASE 27.5–63.0 s, a run of its own.**

| Reading | Condition |
|---|---|
| **E-PRESENT** | A sustained run starts at or before 30.0 s, and `full` nodes are present in at least 50 % of the window's rows |
| **E-PARTIAL** | At least one sustained run in the window, but not E-PRESENT |
| **E-ABSENT** | No sustained run in the window |

**R2, exposure on cases that are not Oil FULL.** Every sustained run is
listed with whether any of its rows has an eligible Foam front. A run with no
eligible Foam front in any row is an **F1 exposure**: F1's Foam guard would
not stop it.
- **Windows:** SPL#4 Accum 20–90 s (all Foam, review-017) and SPL#1 Accum
  650–700 s (Foam-layered, review-012).
- **Local:** sample5 and sample7, which never become full.

**R3, gate-1 cause on SPL#4 BASE 27.5–63.0 s.** The counts of
`gate1:boundary_accepted`, `gate1:absence_margin`, `gate1:absence_low` and
the other statuses. The boundary-accepted outcome Ys are listed, with no
frozen threshold. The agent reads them against the stale edge (Y693–721,
step 15). The coordinate frame is the trace's.

**R4, gate 3 and selection (information).** For `full`-node rows in the
window: how many are `hard_gate`, and the resolved kind of the rest.

**Information only:**
- SPL#1 BASE 650–700 s: FULL accepted from 672 s, and top-exit FULL from
  674.0 s;
- the whole-recording summaries;
- the other local controls: sample2, base_sample_1 and sample4-interior
  (FULL starts) and sample4-original (initial state unknown).

**What each reading leads to (agreed before output):**
- **E-PRESENT with no R2 exposure:** F1 stays a candidate. A design draft
  follows only after the user settles OFF-1's open questions.
- **E-PRESENT with an R2 exposure:** F1 needs a further guard. The exposures
  are reported, and the user decides.
- **E-PARTIAL:** F1 would have to carry over gaps, which is new. Reported,
  and the user decides.
- **E-ABSENT:** F1 as drafted has no existing evidence on the user's case.
  Path F would need new FULL evidence, a new image feature. The result goes
  back to the user with the peer-side desk check of barrier 1 as the
  alternative.

No reading is tuned after output, and no threshold here changes.

## Detector Governance

- Logic-map nodes: `OIL-PHASE-FILL`, `OIL-SELECTOR`, `OIL-PROJECTION`, `OIL-PHASE-INITIAL`
- Failure-registry entries: `S11-F05`, `S11-F06`, `S11-F07`, `S11-F10`
- First harmful stage: on SPL#4 BASE 27.5–63 s no FULL is published. Which of gate 1 (frame outcome), gate 2 (FULL likelihood) or gate 3 (`_constrain_layer`) stops the `full` node is the question; not read.
- Existing feature coverage: the production detector path with IFO v2 and top-exit v3 (the step-7 reference bundles and the local reference arm); the original sample4/base_sample_1/sample2 Recipes, the frozen October 15 interior Recipe and the frozen October 22 empty-fill Recipes; static preparation active; cost-first, RGB, Local XY, the contested gate, E4 and fast-rise OFF in the arm read.
- Execution scope: a new read-only readout tool with unit tests; planned: one closed managed local run (six controls, debug NONE), a scratch FULL-debug bundle check of the tool, and one Windows readout of saved bundles relayed as text; no detector code change or tuning.
- Logic-map impact: NONE — diagnostics only.
- Failure-registry impact: NONE — a readout of existing gates.
