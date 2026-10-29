# V2-2 draft comparison — Windows result (2026-10-29)

**Verdict:** the run is valid. No method is best on every Glass, and none
follows the Oil line on SPL#1, so the decision goes back to the user, as
the request's table says.

- **Request:** [2026-10-29-v2-2-draft-comparison-windows-request.md](../40-operations/2026-10-29-v2-2-draft-comparison-windows-request.md).
- **Diagnostic:** [2026-10-29-draft-method-comparison.md](../50-diagnostics/2026-10-29-draft-method-comparison.md).
- **Source run:** commit `4f58ead`, confirmed by `checked=25 mismatched=0`.
  The agent used an existing local ZIP of `main` whose files matched; its
  note's `4f50ead` is a relay slip.
- **Result file:** on the Windows PC only, at
  `C:\0.Coding\v22_draft_compare_20261029\result.md`.
- **Environment:** Python 3.14.3, OpenCV 4.14.0.94 (headless), NumPy 2.5.4.
- **Recipes read:** `SPL#4_test1_607bccb.recipe.json` (Glasses `BASE`,
  `ACCUM`) and `SPL#1_test1_607bccb.recipe.json` (`BASE`).
- The user also shared photos of all three pictures (the SPL#1 one is the
  overview).

## Script output (relayed)

| Glass | Context | Build | Draft time per method (A / B / D / F) | "Cannot judge" (B / D / F) |
|---|---|---|---|---|
| SPL#4 BASE | 520 × 484 | 4.2 s | 0.5 / 84 / 77 / 81 ms | 5 / 0 / 5 % |
| SPL#4 ACCUM | 520 × 298 | 4.8 s | 0.4 / 34 / 35 / 46 ms | 51 / 3 / 51 % |
| SPL#1 BASE | 8,210 × 728 | **202.1 s** | 21 / 5,449 / 5,392 / 5,348 ms | 88 / 90 / 88 % |

## The user's judgment

| Glass | Best | Ranking | Comment |
|---|---|---|---|
| SPL#4 BASE | A (spike) | A, B, F, D | "그나마 가장 잘 표현하지만 실제 Oil의 선을 따라가기보다는 Foam의 경계를 표현하는 것에 가까움" |
| SPL#4 ACCUM | F | F, B, A, D | "실제 움직임에 가장 가까움. 주로 Foam만 발생해서 그런 듯" |
| SPL#1 BASE | none | — | "550~675초 구간의 유면의 움직임을 아무것도 캐치 못함" |

"Cannot judge" stretches: suitable on SPL#4 (too many with F), too many on
SPL#1.

## What the photos show (agent's reading)

- **SPL#4 BASE:** a large white region shaped like a V in the middle of the
  video, with horizontal bands above and below it. A, B and F follow the
  lower edge of the white region and, outside it, the edges of the bands;
  D stays on one low band from start to end.
- **SPL#4 ACCUM:** a white region that rises from the bottom at the start
  and falls away, and a smaller one later. A, B and F follow the top of
  the white region and lie at the bottom elsewhere; D lies at the bottom
  throughout.
- **SPL#1 BASE (overview):** mostly an even grey, with a white region from
  about 20 % to 30 % of the width (roughly 14–20 min) and darker vertical
  stripes before it. Around 550–675 s (about 13–16 % of the width) the
  overview shows vertical stripes, not a horizontal boundary that moves.
  All four lines lie near the bottom for most of the video.
- **The white regions read as Foam.** Where Foam is present, the strongest
  edge is the Foam boundary; elsewhere it is a fixed band or the bottom.

## Against the fixed decision table

- **Valid run:** yes.
- **One method best on all three Glasses:** no (A, F, none).
- **Path taken:** "Glass마다 가장 나은 방식이 다르다" and, for SPL#1,
  "없음": the draft method goes back to the user.
- F is best only on ACCUM, where the user says the movement is mostly
  Foam; the "F가 가장 낫다" row (bringing back fixed-structure marking)
  does not apply on its own.

## Facts for V2-2

- **No edge-based draft followed the Oil line on the acceptance videos.**
  The best one on SPL#4 follows the Foam boundary, and none catches the
  SPL#1 level change at 550–675 s. Spike against dynamic programming,
  and the edge source, are secondary to this.
- **A4 risk confirmed.** Building one Glass's context image for SPL#1 took
  202.1 s with the spike's method (sequential decode of every frame, then
  a row median per sampled frame). A4 allows 180 s for the whole
  analysis; the spike measured 165.9 s on 2026-10-28.
- Dynamic programming takes about 0.65 ms per column at 728 rows on this
  PC: 5.4 s for SPL#1.
