# Step-8 Windows receipt — 2026-10-26

**Status: RECEIVED / F: 0 qualifying triplets, so no SPL#4 run / L: LBT-2 S2
CLOSED WITHOUT A DESIGN (S2 and S3 fail; S1, S4 and S5 hold).** The reply to
the
[step-8 combined request](../../40-operations/s11-current-windows-field-qualification.md#step-8-combined-request)
came back through the user as verbatim stdout, relayed by OCR. The readings
below apply the rules fixed before the run:
- F uses the
  [readout rule](2026-10-23-fast-rise-local.md#windows-readout-tool--2026-10-26).
- L uses the
  [S2 protocol](../../50-diagnostics/s11/2026-10-22-layer-bottom-topology-2.md#windows-s2-protocol-frozen-2026-10-26).

Nothing is tuned or changed. Top-exit, the fill-owner gate and the fast-rise
association stay default OFF. FIELD FAIL / O2 OPEN and review-006 pending are
unchanged.

## Runs and identity

| Run | Run ID | Bundle (Windows) |
|---|---|---|
| SPL4_B_ref (step 7, read only) | `005e0d58-024e-4c38-b5eb-becfc552e0cb` | `oil_level_analysis_SPL4_B_ref_20261023_150316` |
| SPL1_B_ref (step 7, read only) | `b8b8403b-e4d2-43ce-9b70-f6ed37734b51` | `oil_level_analysis_SPL1_B_ref_20261023_152751` |
| SPL1_S2_ref (L-1) | `de838a68-e08a-4e4b-8cb1-994fad591048` | `C:\step8_out\s2\oil_level_analysis_SPL1_S2_ref_20261026_105442` |
| SPL1_S2_lbt2 (L-2) | `0a83d452-ef74-4743-97ae-37a4c012384e` | `C:\step8_out\s2\oil_level_analysis_SPL1_S2_lbt2_20261026_115042` |

- **Versions:** every run and readout prints
  `r22-oil-ownership-evidence-replacement-v1+initial-full-observation-v2+top-exit-full-v3`.
  The runner checks both suffixes.
- **Source:** the six SHA-256 values came back with OCR-like slips in a few
  characters (`0`/`8`, `a`/`e`, `d`/`0`).
  - Example: the readout tool's value reads `…ca48f0a7…ceffe088…` against
    the request's `…ca48f0e7…ceffde88…`.
  - The request told the agent to stop on any mismatch, and every step ran.
  - So the slips are read as OCR errors, not a source difference. That is an
    inference; the files were not re-hashed.
- **SPL1_B_ref run ID:** the reply reads `b0b8403b…`; the step-7 receipt reads
  `b8b8403b…`. The rest of the ID matches, so this is read as the same
  `0`/`8` OCR slip.
- **Glasses:** the F readout JSON names carry `9c74a762…` (SPL#4 BASE) and
  `cfef5bad…` (SPL#4 Accum), the step-7 Glasses.
- **Rows:** 601 per Glass in both L runs over 480.0–780.0 s at 2 fps with
  FULL debug, the source session's window.

## F — SPL#4 fast-rise readout

| Glass | Frames | Rows | Anchor | Physical | Motion | Witnessed | Upward beyond cap | Constant velocity | Same representation | Qualifying |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BASE | 11 | 40 | 7 | 29 | 15 | 4 | 4 | 2 | 2 | **0** |
| Accum | 11 | 51 | 1 | 31 | 22 | 0 | 2 | 0 | 0 | **0** |

- **Ambiguous joins:** 0 on both Glasses.
- **Policy as read:** cap 32.0, bound 96.0, row tolerance 12.0, motion and
  coverage minima 0.5.
- **The two constant-velocity BASE triplets fail only the witness.** Neither
  has a witnessed row:

| Times s | Y | Steps px | Tracklets |
|---|---|---|---|
| 20.5, 21.0, 21.5 | 801.0, 749.0, 702.0 | −52.0, −47.0 | `0025:0018`, `0042:0035`, `0025:0016` |
| 21.5, 22.0, 22.5 | 802.0, 756.0, 703.5 | −46.0, −52.5 | `0025:0018`, `0042:0035`, `0025:0016` |

- **The four witnessed rows come later, not on the rise.** They are 22.5 s
  Y785, 23.0 s Y758 and Y781, and 23.5 s Y765, on tracklets `0042:0035` and
  `0025:0018`.
- **Each triplet takes one row from three rows that each stay near one Y.**
  Observed in the rows list:
  - `0025:0018`: Y801–802 at 20.5–21.5 s.
  - `0042:0035`: Y740–758 at 21.0–23.0 s.
  - `0025:0016`: Y702–703.5 at 20.5 s and 21.5–22.5 s (Y613.5 at 21.0 s).
- **Inference, no frame review:** the two lines are made of three stacked,
  near-stationary rows about 50 px apart, not one rising interface. A weaker
  witness would join them across rows, which is the `S11-F04` owner transfer
  that the witness exists to prevent.

**Reading by the rule: no qualifying BASE triplet, so no SPL#4 run.** The
blocker is the witness: geometry and representation pass on two triplets.
By the rule, the user chooses between a successor witness protocol and closing
option 2 (accepting UNKNOWN on fast fills). That choice is open.

## L — LBT-2 S2

**Operations (L-2):**
- E1 668, support 173, F 0, unit frames Accum 192.
- The F guard never fired on SPL#1.
- In 668–682 s the Accum units are non-empty on 672.0–675.5 s and
  676.5–677.5 s, with unit tops Y436–538. They are empty at 676.0 s and from
  678.0 s on.
- Every BASE unit is empty.

**Segments (S2 compare, reference → LBT-2):**

| Segment | Rows | Oil | Foam | Changed |
|---|---:|---:|---:|---:|
| WS1-ACCUM-EMPTY | 346 | 0 → 0 | 0 → 0 | 0 |
| WS1-ACCUM-ENTRY-SPLASH | 37 | 4 → 1 | 7 → 7 | 5 |
| WS1-ACCUM-FOAM-LAYERED | 16 | 10 → 11 | 11 → 11 | 14 |
| WS1-ACCUM-POST-FOAM | 41 | 0 → 17 | 0 → 0 | 17 |
| WS1-ACCUM-DRAIN | 160 | 22 → 0 | 22 → 22 | 22 |
| WS1-BASE-FULL-PREFIX | 139 | 3 → 3 | 0 → 0 | 0 |
| WS1-BASE-DRAIN | 205 | 170 → 170 | 0 → 0 | 0 |
| WS1-BASE-RAPID-REFILL | 45 | 39 → 39 | 0 → 0 | 0 |
| WS1-BASE-FULL-SUFFIX | 211 | 0 → 0 | 0 → 0 | 0 |
| None (outside any segment) | 2 | 0 → 0 | 0 → 0 | 0 |

The total is 58 changed rows, all in Accum.

**Held-out frames (review-012 table V; C within mark ± 29.16 px, A a number
outside, B no number):**

| Time s | Mark Y | Ordinary | LBT-2 | LBT-2 − mark | Class |
|---:|---:|---:|---:|---:|:---:|
| 672.00 | 493.5 | 438.0 | — | — | B |
| 672.51 | 490.0 | — | — | — | B |
| 673.01 | 498.5 | — | — | — | B |
| 673.51 | 501.5 | 345.0 | — | — | B |
| 674.01 | 493.0 | 351.0 | 485.0 | −8.0 | C |
| 674.51 | 495.5 | 329.0 | 491.0 | −4.5 | C |
| 675.01 | 499.5 | 317.0 | 498.0 | −1.5 | C |
| 675.51 | 499.5 | 315.0 | 493.0 | −6.5 | C |
| 676.01 | 488.5 | — | 485.0 | −3.5 | C |
| 676.51 | 468.0 | — | 459.5 | −8.5 | C |
| 677.01 | 456.0 | 269.0 | 453.0 | −3.0 | C |
| 677.51 | 432.5 | 256.0 | 438.0 | +5.5 | C |

The score moves from C0 A8 B4 to **C8 A0 B4**. Every numeric LBT-2 value is
within 8.5 px of the mark. The four B frames lost the ordinary output's Oil
(672.0 s and 673.5 s) or never had any.

**Against the frozen readings:**

| Reading | Received | Result |
|---|---|---|
| S1, same source | identity compare: 0 changed rows | **holds** |
| S2, no harm on the controls | 26 numeric Oil rows removed in visible-interface segments: ENTRY-SPLASH 4 (669.5, 670.5, 671.0, 671.5 s) and ACCUM-DRAIN all 22 (711.0–724.0 s); no Oil added in FULL/EMPTY segments; no Foam added anywhere | **fails** |
| S3, 678.5/679 s unchanged | 678.5 s Y238 → Y415; 679.0 s — → Y414 | **fails** |
| S4, A+B below 12 | A+B = 4 | **holds** |
| S5, tested | non-empty units on 11 of 12 held-out frames (all but 676.0 s) | **holds** |
| Foam in FOAM-LAYERED, option (b) | no Foam value added or removed | nothing to score |

**Outcome by the protocol: "any other failure", so S2 closes without a
design.** No tuning, widening or time, Y or Glass exception follows.

**Limits, listed for the record (no reading attached):**
- **BASE:** unchanged, as expected.
- **ENTRY-SPLASH:** besides the 4 removals, 670.0 s gains Y504.
- **FOAM-LAYERED outside the held-out frames:**
  - 678.0 s loses Y248;
  - 678.5/679.0/679.5 s read Y415/Y414/Y414 against Y238/—/—.
  - These frames have no reviewed mark.
- **POST-FOAM:** 17 rows gain Y346–402 at 681.0–692.5 s. The truth has no
  positional reference there, so they neither pass nor fail. Their fill
  states alternate between FILLING, DRAINING and PARTIAL.
- **ACCUM-DRAIN:** this was not expected. Before the run, E1 was expected to
  act only while a Foam seed is under 3 s old. The units are empty from
  678.0 s, and the truth has no Foam after 680 s. So the drain removals are
  not a direct unit act. Inference: they follow from the sequence state that
  the changed Oil track left. The mechanism is unknown; the operations JSON
  stays on Windows.
- **What S4 shows:** on SPL#1, a unit-based reading reached the reviewed
  Foam-region bottom on every numeric held-out frame. This is a finding for a
  possible successor, not a design. A successor would be a separate user
  decision and would have to answer the S2 and S3 failures.

## What it decides

- **SPL#4 fast-rise run:** not proposed (rule F). Option 2's next step is
  the user's choice: a successor witness protocol, or closing it and
  accepting UNKNOWN on fast fills.
- **LBT-2:** closed without a design. The held-out benefit is recorded with
  its limits.
- **Unchanged:** no production default changed. FIELD FAIL / O2 OPEN and
  review-006 pending.

## Detector Governance

- Logic-map nodes: `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `FOAM-IDENTITY`, `SEQUENCE-COMPOSITION`
- Failure-registry entries: `S11-F04`, `S11-F05`, `S11-F06`
- First harmful stage: not claimed. F: SPL#4 BASE shows no witnessed constant-velocity triplet at `OIL-TRACKLET`. The only geometric triplets join three near-stationary rows (`S11-F04` risk). L: LBT-2's held-out change reaches the marked Foam-region bottom, but it removes Oil in ENTRY-SPLASH and in all of ACCUM-DRAIN (mechanism unknown) and changes 678.5/679 s.
- Existing feature coverage: F reads the step-7 `SPL4_B_ref` FULL debug trace with the production tracklet policy and `_independent_witness` minima (IFO v2 + top-exit v3). L reruns the step-7 `SPL1_B_ref` session and Recipe snapshot unchanged through the headless bundle path, as a reference arm and as LBT-2 as frozen at `1447cd6`. No Recipe or session change.
- Execution scope: two read-only readouts and two Windows runs with two comparisons under the user-forwarded step-8 request, relayed by OCR; no Mac run; scored on the Mac against the frozen rules and review-012 table V.
- Logic-map impact: NONE — a receipt; no owner or edge changes.
- Failure-registry impact: NONE — the readout limit maps to `S11-F04`. The LBT-2 limits are diagnostic-wrapper results with no runtime mechanism.
