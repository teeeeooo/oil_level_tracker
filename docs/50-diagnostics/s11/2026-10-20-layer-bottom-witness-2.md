# LBW-2 — layer-bottom witness without a minimum Oil-band thickness

**Status: PROTOCOL FROZEN — S0 NOT RUN.** Base HEAD: `2119e2e`. Current authority:
[Work Plan](../../00-project/work-plan.md). The user approved this successor after
[LBW-1's S0 failure](2026-10-20-layer-bottom-witness.md#s0-result). Everything not
listed below is inherited unchanged from
[LBW-1](2026-10-20-layer-bottom-witness.md): inputs, sectors, upper condition,
decision rule, the three consumers and their scope, stages S0→S1→S2, controls,
pass/stop rules and the no-tuning rule.

## Why a successor

LBW-1 required no textured row within `d` (17 px on sample4) below the boundary.
At sample4 42 s the clean Oil band is about 15 px thick before lower-structure
texture returns. The texture map's fall from layer to clean lies about 4–8 px below
the reviewed candidate rows Y835/837, beyond the ±2 test rows. Negatives were never
supported, and TPA-1's Y805 read as layer interior, so the interior-versus-bottom
distinction is measurable. The definition was wrong about thickness and localization.

## Changed definition (two changes only)

1. **Lower condition — clean onset instead of clean depth.** The `max n_s` over the
   `2·BAND+1 = 5` rows directly below the test row is `< 0.60`. Five rows is the
   shortest clean run that the ±2-row smoothing can resolve. Texture may return
   below those rows (a thin Oil band over a structure).
2. **Test rows — the existing same-boundary tolerance.** Test rows are
   `y' ∈ [y − tol, y + tol]`, where `tol = max(8, 0.375 × temporal_max_jump_px)` is
   the tolerance `_cross_representation_support` already uses to treat two rows
   as one boundary. It is 12 px for both sample4 and the Windows Accum Glass.

Sector `TERMINAL`: some test row has the upper condition (mean `n_s` over `d` rows
above ≥ 0.60, unchanged) and the clean onset. `INTERIOR`: the upper condition holds
somewhere, and no test row has a clean onset. `UNAVAILABLE`/`OTHER` and the 3-sector
decision are as in LBW-1.

**Accepted risk, recorded before running.** A wider test window also supports
candidates within 12 px of a real layer bottom on either side. This is consistent
with the existing same-boundary semantics. It could support a Foam-interior dip
with a ≥5-row clean gap; the held-out check below tests this.

## Development versus held-out data

Both changes were chosen after seeing sample4's 42 s profile. **sample4 is
therefore development data.** Its S0 run is a consistency check only. The decisive
test is the **Windows ④ trace**, which no witness definition has read. It must be
read only after this protocol and the tool are committed.

## S0 pass rules

Both recordings must satisfy LBW-1's four rules (no negative supported, decisive
pairs, ≥80 % positive frames, valid self-check). Windows controls by
`candidate_input_index` (review-009 and ATG-1 tables):

| Frame / s | Positives | Negatives |
|---|---|---|
| f16136 / 673.0 | 10, 26 | 25 (Y367), 12 (Y370), 2 (Y370), 20 (Y375), 3 (Y389) |
| f16184 / 675.0 | 10, 22, 25 | 14 (selected Y317), 24 (Y261), 11 (Y266), 18 (Y266), 17 (Y276) |
| f16232 / 677.0 | 10, 23, 25, 26 | 11 (anchor Y235), 16 (selected Y269), 24 (Y230), 18 (Y232), 1 (Y233) |
| f16268 / 678.5 | 12, 24 | 16 (anchor Y229), 21 (selected Y238) |

Decisive Windows pairs: at 677 s a positive is supported and idx11 is not; at
678.5 s idx12 or idx24 is supported and idx16 is not. The 679/684 s collapse frames
are not read.

**If sample4 passes and Windows fails,** LBW-2 closes. The definition did not
transfer, and no third definition is chosen from Windows results. **If sample4
fails,** LBW-2 closes without reading Windows. Only if both pass does S1 start,
which needs no new approval. S2 still needs a separate user go.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `FOAM-EPISODE`, `SEQUENCE-COMPOSITION`.
- Failure-registry entries: `S11-F04`, `S11-F05`, `S11-F06`, `S11-F10`.
- First harmful stage: `OIL-AUTHORITY` — texture-excluded support, then nearest-ordered-lower demotion under an upper anchor inside the Foam layer (AAT-1, TPA-1, ATG-1); LBW-1 showed a fixed clean depth fails on a thin Oil band.
- Existing feature coverage: as LBW-1. The only new references are the existing ±2 smoothing width (5-row clean run) and the existing cross-representation same-boundary tolerance. sample4 is development data; the ④ FULL+ON v2 saved trace is held out.
- Execution scope: protocol only; nothing run. S0 is a read-only witness screen with no detector consumer.
- Logic-map impact: NONE — no source change.
- Failure-registry impact: NONE — no result yet.
