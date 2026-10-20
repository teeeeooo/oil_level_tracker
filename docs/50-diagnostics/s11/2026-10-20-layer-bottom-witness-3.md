# LBW-3 — first supported layer bottom

**Status: PROTOCOL FROZEN — S0 NOT RUN.** Base HEAD: `a5b21e5`. Current authority:
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

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `FOAM-EPISODE`, `SEQUENCE-COMPOSITION`.
- Failure-registry entries: `S11-F04`, `S11-F05`, `S11-F06`, `S11-F10`.
- First harmful stage: `OIL-AUTHORITY` — texture-excluded support, then nearest-ordered-lower demotion under an upper anchor inside the Foam layer (AAT-1, TPA-1, ATG-1); LBW-1/2 showed thickness and lower-structure limits of a standalone row witness.
- Existing feature coverage: as LBW-2; the only new element is the frame-level ordering, mirroring the existing nearest-ordered-lower rule. sample4 is development data; the ④ FULL+ON v2 saved trace is held out.
- Execution scope: protocol only; nothing run.
- Logic-map impact: NONE — no source change.
- Failure-registry impact: NONE — no result yet.
