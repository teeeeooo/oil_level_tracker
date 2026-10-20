# LBW-3 — first supported layer bottom

**Status: CLOSED WITHOUT PROMOTION — WINDOWS HELD-OUT CHECK FAILED** ([held-out result](#windows-held-out-result)); sample4 development check passed. Protocol base HEAD: `a5b21e5`. Current authority:
[Work Plan](../../00-project/work-plan.md). The user approved LBW-3 as the last
witness definition in this line. Whatever its result, the next step is to review
other approaches. Everything not listed below is inherited from
[LBW-2](2026-10-20-layer-bottom-witness-2.md) and
[LBW-1](2026-10-20-layer-bottom-witness.md).

## Why

[LBW-2](2026-10-20-layer-bottom-witness-2.md#s0-result) supported every sample4
positive (6/6). It also supported the 42 s lower-structure bottom Y868, because the
row witness finds the bottom of *any* textured band. Only ordering separates the
Foam layer from structure below it. The reviewed boundary is the first supported
bottom from the top; structures lie lower.

## Changed unit (one change only)

The row witness is LBW-2's, unchanged. The judged unit becomes the frame's
**first supported bottom**: take the topmost Oil candidate whose witness is
`INTERFACE_SUPPORTED`, at Y = B. The unit is every supported candidate with
`Y ≤ B + tol`, where tol is the same-boundary tolerance (12 px for both recordings).
Supported candidates below that are not accepted.

No Foam front or Foam material row is used. The Windows 678.5 s frame has no
eligible Foam row, and reading the Foam owner would couple this test to it (F06).
The consumer design is unchanged in intent: consumer 2 ("topmost supported
anchor") is this unit.

**Accepted risks, recorded before running:**
- a supported bottom **above** the Foam layer would become the unit and displace
  the real boundary;
- a Foam-interior clean gap of ≥5 rows would do the same.

The held-out Windows check tests both.

## Data roles and rules

sample4 is development data (now seen for the third time); the Windows ④ trace is
held out and unread. The pass rules are LBW-1's four, applied to the unit:
- no negative is in the unit;
- decisive pairs: sample4 42 s, Y835/837 in and Y805/Y868 out; Windows 677 s, a
  positive in and idx11 out; Windows 678.5 s, idx12 or idx24 in and idx16 out;
- at least 80 % of positive frames have a reviewed candidate in the unit;
- valid self-check.

Windows controls are LBW-2's table. If sample4 fails, LBW-3 closes without reading
Windows. If sample4 passes, the read-only Windows extraction is requested; S1 starts
only if Windows also passes. In every case no further definition is drawn from
these results. The next step is the user's review of other approaches.

## S0 sample4 result

Tool `87817ad`, committed before the run. Managed run
`sample/output/s11-layer-bottom-witness-3-20261020-001` (closed). Evidence:
`evidence/sample4-s0-lbw3.json`, 19,584 bytes, SHA-256
`ae7952269272e536bda1d2c8bc39536ae82141b055873469d00ef22ec9b20916`. The fingerprint
equals P5, and the self-check has 0/196 mismatches.

| Rule | Result |
|---|---|
| 1. No negative in the unit | PASS: Y805 and Y821/822 are `INTERNAL`; Y868 is supported but below the unit; Y865.5/867/861.5–862 are `UNRESOLVED` |
| 2. Decisive 42 s | PASS: Y835/837/838/839 are in the unit; Y805 and Y868 are out |
| 3. Positive frames ≥ 80 % | PASS: 6/6 |
| 4. Self-check | PASS |

At 42 s, the supported Y844 lies just outside the unit (the topmost supported
candidate is at or above Y831). That positive frame still holds four reviewed
candidates in the unit. This is a development-data pass on its third viewing.
It does not show transfer.

## Windows held-out result

Relayed from the Windows work PC. The frozen tool `87817ad` ran read-only on ④
(`a9ccece3-…`, `trace=full`, Accum, tol 12.0). No private file was inspected locally.

| Frame / s | Reviewed positives (unit = `first`) | Negatives in unit |
|---|---|---|
| f16136 / 673.0 | idx10 Y493 **first** (T3); idx26 Y490 `INTERNAL` (T1 I4) | none |
| f16184 / 675.0 | idx22 Y496, idx10 Y497, idx25 Y498 all **first** (T3 I2) | none |
| f16232 / 677.0 | idx23 Y449, idx10 Y451, idx26 Y453 **first** (T3–4); idx25 Y444 `UNRESOLVED` (T2) | none (idx11 anchor Y235 out) |
| f16268 / 678.5 | idx12, idx24 Y415 both `UNRESOLVED` (**T0 I0 O5**) | none (idx16 anchor Y229 out) |

Self-check: 0/108 mismatches (valid).

| Rule | Result |
|---|---|
| 1. No negative in the unit | PASS: 0 of 24 |
| 2. Decisive 677 s | PASS |
| 2. Decisive 678.5 s | **FAIL**: neither idx12 nor idx24 is in the unit |
| 3. Positive frames ≥ 80 % | **FAIL**: 3/4 (75 %) |
| 4. Self-check | PASS |

**Decision.** Under the frozen rule, LBW-3 closes without promotion. No consumer
is built, and no definition is drawn from this result. The user's agreed next
step is a review of other approaches.

**What the held-out data shows (for that review):**
- **673–677 s, clear layered Foam: the witness transfers.** The reviewed boundary
  is the first supported bottom in all three frames. All 24 interior rows, Foam
  anchors and wrong selections stay out, including the 677 s anchor Y235 that
  demotes the boundary today. This is the first held-out support for the
  layer-bottom idea.
- **678.5 s, Foam fading: the witness sees nothing.** Every sector at Y415 is
  `OTHER` (O5): the texture above the boundary is no longer at the layer level.
  This is the onset of the collapse the user described: Foam turns to liquid
  (see the [Foam-collapse target](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md#accum-foam-collapse-target--2026-10-20)).
  Here the second blocker (upper anchor Y229 demoting Y415) acts with no texture
  evidence available. A material-texture witness cannot address it by
  construction.
- The 75 % figure rests on four frames. The point is not the rate but which frame
  fails, and why.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `FOAM-EPISODE`, `SEQUENCE-COMPOSITION`.
- Failure-registry entries: `S11-F04`, `S11-F05`, `S11-F06`, `S11-F10`.
- First harmful stage: `OIL-AUTHORITY` — texture-excluded support, then nearest-ordered-lower demotion under an upper anchor inside the Foam layer (AAT-1, TPA-1, ATG-1); LBW-1/2 showed thickness and lower-structure limits of a standalone row witness.
- Existing feature coverage: as LBW-2; the only new element is the frame-level ordering, mirroring the existing nearest-ordered-lower rule. sample4 is development data; the ④ FULL+ON v2 saved trace is held out.
- Execution scope: S0 sample4 development check (existing production analysis, witness on detector-artifact rasters, no consumer) and the relayed read-only Windows held-out check on the saved ④ trace; S1/S2 not run.
- Logic-map impact: NONE — no source change.
- Failure-registry impact: NONE — a closed diagnostic screen with no runtime mechanism; held-out counterexample (678.5 s) recorded here.
