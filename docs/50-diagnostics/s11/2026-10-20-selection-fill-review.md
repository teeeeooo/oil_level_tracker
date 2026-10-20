# SFR-1 — selection and fill-phase review after LBQ-1

**Status: REVIEW COMPLETE — recommendation awaits the user's choice.** Desk review
plus read-only replays of the closed LBQ-1 evidence. No detector change, run or
Windows request. Base HEAD: `68ffd75`. Current authority:
[Work Plan](../../00-project/work-plan.md). The user asked for this review after
[LBQ-1](2026-10-20-layer-bottom-qualified-authority.md#results-and-decision)
closed.

## Finding 1 — both LBQ-1 failures come from one mixed-identity owner

The baseline was replayed in memory with the frozen LBQ-1 wrapper and the kept
unit map (`units.json`), then read back. Nothing was written.

| Time | Tracklet | Rows in that tracklet | Eligible Foam row | What happens |
|---|---|---|---|---|
| 39.5–42.5 s | 79:0013 | Y805–816, continuation | Y841 → Y818 | Published at 42.5 s (Y805) |
| 43–44 s | **79:0013** | Y829–844, ordered-lower anchors (consumer 1) | Y812 | The same ID jumps 31 px down to the layer bottom |
| 45–48 s | 90:0020 | Y818–833, one Y833/829 anchor | Y812–814 | Continuation near and below the Foam row |
| 48.5 s | **90:0020** | Y805/811, continuation | Y814 | Jumps 24 px up, above the Foam row |

**Mechanism:**
- The fill chain of 79:0013 → 90:0020 carries the layer-bottom anchors as
  `independent_anchor` evidence. Its last row lies above the Foam row (Y805, in
  the entrance band).
- The `UNKNOWN_FILL_ANCHORED` profile reads this as "an anchored chain rose to
  the entrance": span ≥ 20.8 px, last row ≤ Y826, upward agreement. The result is
  `FILL_SPAN_CONFIRMED` → `filled_barrier` → `FILLED_CAP_VETO` for 49–56 s.

The ordinary run has the **same mixing** (79:0013 and 90:0020 hold the same rows).
It does no harm there only because none of its rows are anchors. So LBQ-1 did not
create the fault. It gave anchors to an identity that already mixes rows above
the Foam row with the layer bottom (F04: alias continuation within the jump
bound).

The selection layer (42.5 s) and the fill-phase layer (48.5 s) are therefore **not
two independent owners** to repair. They are two consumers of one physical-identity
error.

## Finding 2 — the unit marks a role band, not a position

The LBW-3 unit spans the same-boundary tolerance (12 px). Its top B lies **2–12 px
above** the reviewed row at every sample4 control in 40–52 s:

| Control (time, reviewed Y) | 40 s Y841 | 42 s Y839 | 42.5 s Y835 | 44 s Y844 | 49.5 s Y841 | 52 s Y833 |
|---|---|---|---|---|---|---|
| Unit top B | Y832 | Y829 | Y833 | Y836 | Y829 | Y830 |

The sample4 entrance band ends at Y826 (ellipse Y798–902, ratio 0.27). The
reviewed level is Y829–844, only 3–18 px below it. B itself reaches the band at
48.5/52.5/54.5 s (Y826/821/820).

- Any rule that takes a position from "the topmost unit row" is biased upward.
- Any anchored chain that ends at the unit top can satisfy fill confirmation in
  this Glass.
- The nearest-anchor rule (tolerance 8 px) also demotes lower rows inside one
  12 px unit.

## Options

| # | Option | Owner | Covers 42.5 s / 48.5 s | Verdict |
|---|---|---|---|---|
| E1 | **Layer-bottom topology:** in the ordered-lower context, an Oil ref above the unit top B is not Oil-eligible. It cannot join a tracklet, a fill chain or a selection. Consumers 1–2 are also limited to that context, closing LBQ-1's scope gap | `OIL-CANDIDATE`/`OIL-AUTHORITY` (eligibility) | Both: Y805–823 never join 79:0013/90:0020 | **Recommended.** A role statement the witness supports: while Foam is layered, nothing above the layer bottom is Oil. With an empty unit (Windows 678.5/679 s) it does nothing |
| E2 | Forbid one tracklet from holding rows on both sides of B | `OIL-TRACKLET` | 48.5 s only; a separate Y805 owner can still be selected at 42.5 s | Partial |
| E3 | Fill confirmation needs its last row anchored or in the unit | `OIL-PHASE-FILL` | 48.5 s only | Partial; does not touch Finding 1 |
| E4 | Selector prefers anchors over continuation | `OIL-SELECTOR` | 42.5 s only | Excluded: generic anchor privilege |

**E1 at the reviewed rows (development data, read from `layers.json` and ATG-1):**
- sample4: no reviewed positive lies above its frame's B. The removed rows
  include the opposed 42.5 s Y805 and 44 s Y822. The lower opposed rows
  (Y865.5/868/882, Y862) lie below the unit and are left to the existing
  nearest rule with consumers 1–2.
- Windows: the published Y317/Y269 and the air–Foam top anchor Y235 lie above
  the unit (673–677 s). 678.5/679 s have an empty unit and stay unchanged.

**Risk to pre-register.** Finding 2 means E1 alone may still confirm a fill:
- the reviewed level stays below Y826, but B reaches Y820–826 in three frames;
- a chain of in-unit anchors from Y844 to Y821 spans 23 px.

If that happens, it is a separate fill-geometry question: the entrance band of
a layered Glass whose level sits 3–18 px under it. It is not a reason to widen
E1. A second risk: a wrong unit would hide a true Oil row above it. The held-out
evidence for the unit is 0/24 negatives, and E1 is limited to frames with a
Foam material row.

**Excluded because of earlier results:** support-only or demotion-only repair
(TPA-1, LBQ-1), generic anchor privilege, donor history and H1/H2 (HPA-1),
cost-first association, and any change to the 0.27 entrance band or the 20 %
span ratio.

## Recommendation

One frozen protocol, **LBT-1**:
- E1, plus LBQ-1 consumers 1–2, all limited to the ordered-lower context.
- The same sample4 SOI population, rules and stop conditions as LBQ-1.
- Pre-registered outcome for the fill-geometry risk above.
- A layer report per frame: removed rows, tracklet membership, fill-chain
  profile and published row.

Windows S2 remains a separate go: review-011 held-out frames first, then the run.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `FOAM-IDENTITY`, `SEQUENCE-COMPOSITION`.
- Failure-registry entries: `S11-F04`, `S11-F05`, `S11-F06`, `S11-F10`.
- First harmful stage: `OIL-TRACKLET` — one physical ID alternates between rows above the Foam material row and the layer bottom within the jump bound. Anchors on the bottom rows then confirm a fill chain that ends above the Foam row (`OIL-PHASE-FILL`) and keep the upper row selectable (`OIL-SELECTOR`).
- Existing feature coverage: read the current tracklet builder, fill-chain advance, fill confirmation profile, filled-barrier cap and the identity-contradiction consumers, which are read only in release stages and not in fill chains. Reused the LBQ-1 wrapper and kept unit map for an in-memory read-only replay. sample4 geometry from the saved Recipe snapshot.
- Execution scope: desk review plus in-memory replay of the closed LBQ-1 baseline; no new run, managed output or Windows request.
- Logic-map impact: NONE — no source change.
- Failure-registry impact: NONE — review only; the F04 alias pattern is recorded here for the successor protocol.
