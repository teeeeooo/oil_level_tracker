# ARV-1 — approach review after the layer-bottom witness line

**Status: REVIEW COMPLETE — recommendation awaits the user's choice.** Desk review
only: no detector change, run, tuning or Windows request. Base HEAD: `8e97de2`.
Current authority: [Work Plan](../../00-project/work-plan.md). The user asked for
this review after [LBW-3](2026-10-20-layer-bottom-witness-3.md#windows-held-out-result)
closed.

## Split the problem by Foam state

LBW-1–3 tried to cover the whole Accum Foam interval with one witness. The
held-out result shows the interval has at least two cases with different
evidence and different targets
([reviewed truth](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md#accum-foam-collapse-target--2026-10-20)).

| State | Frames (④) | Target | What blocks it today | Evidence that sees it |
|---|---|---|---|---|
| Layered Foam | 673–677 s | Oil/Foam layer bottom (Y493–498, Y444–453) | Texture-excluded support = 0 ([ATG-1](2026-10-20-accum-texture-gate.md#decision)); at 677 s, demotion under the Foam-interior anchor Y235. Published Oil is none/Y317/Y269 | LBW-3 unit: boundary first in 3/3 frames, 0/24 negatives (held-out) |
| Collapse onset | 678.5–679 s | Best: air–liquid top **and** liquid–liquid layer. Fallback: air–liquid top | 678.5 s: Y392/403 anchors (12–23 px above Y415) demoted under upper anchor Y229. Published Y238. 679 s: nothing published | Texture: none (O5 at Y415). Air–liquid top: R22 review Y213 at 679 s |
| After Foam | 684 s → | `WS1-ACCUM-POST-FOAM` Oil boundary | Not studied | User: only a slight colour difference; recorded "not visible" |

**Open truth question (decisive for the collapse row).** The product publishes one
Oil level, so during collapse the acceptable fallback is the air–liquid top. The
liquid–liquid layer alone was not ranked by the user. ATG-1 did not review what
the published Y238 and anchor Y229 at 678.5 s are. The nearby facts are an
air–liquid top near Y213 at 679 s and a stored anchor Y205 at 684 s. If Y229/Y238
is the air–liquid top, today's 678.5 s output already meets the fallback. LBW-3's
678.5 s failure would then concern only the best case, and the remaining gap is
the layered-Foam case. If they are Foam interior, the collapse case is a real
second gap. Only the user's review can settle this.

## Candidate approaches

| # | Approach | Prior evidence | Verdict |
|---|---|---|---|
| A | Reuse the LBW-3 unit as a fail-closed role witness in layered Foam | Held-out: 3/3 layered frames, 0/24 negatives. Sample4 (development): 6/6, 0 negatives. At 678.5 s it returns `UNRESOLVED`, never a wrong support | **Keep as the witness.** It closed under its frozen pass rule, and reuse is the user's decision. Same definition, no new parameter; `UNRESOLVED` changes nothing |
| B | Gray/colour two-sided evidence (non-texture) | Measurable without new media: every trace stores `oil_interface_diagnostics` (per-candidate, per-sector gray contrast); ④ FULL also stores `original_roi` (BGR, lossless PNG) and `grayscale`. As a discriminator: CRW-1 partition counts tie or reverse on sample4 oppositions; PWC-1 profile jumps admit oppositions; the RGB trial accepts glass rims | **Not now.** A standalone gray/colour discriminator repeats three closed failures. Its 678.5 s target (Y415) is the unranked liquid–liquid layer. Possible later use: secondary evidence for the best case, scoped to collapse |
| C | Change nearest-ordered-lower demotion | TPA-1: each local authority repair exposes the next layer (admission, selection, fill chain) unless a qualified role witness exists. "Generic anchor privilege" is excluded | **Only as A's consumer:** an anchor that A reads as `INTERNAL_OR_ARTIFACT` must not demote a lower A-supported boundary. This is LBW-1 consumer 2. Not as a standalone rule |
| D | Explicit Foam-collapse phase | No phase signal exists. Reading the Foam owner couples Oil to Foam (F06). At 678.5 s the eligible Foam is already gone | **Defer** until the truth question above is answered; it may be unnecessary for the fallback |
| E | Temporal continuity (carry the last confirmed bottom) | HPA-1: donor history is not deployable; cost-first association failed; F03 motion overreach | **Excluded** beyond the existing tracklet machinery |

## Held-out data for the next experiment

Windows 673–678.5 s has now been read by the witness and can no longer be held
out. 679/684 s were read by ATG-1 but not by the witness. Options:
1. **Other ④ frames in 672–680 s.** ATG-1 captured 20 frames in 671–681 s; the
   witness read 4. The rest need a new human review (O2 ping-pong). Same
   recording, so this is weaker independence.
2. **Local target-domain `sample2`/`sample3`.** Both have Recipes and Oil/Foam
   context ([source audit](../../60-evidence/s11/2026-10-10-local-truth-and-evaluation-audit.md)),
   but no witness has read them. Whether they contain a layered Foam with a
   visible lower boundary is unreviewed; a short review would decide it. The
   public beer/milk recordings (`sample6`/`sample7`) have no Recipe, and their
   lower Foam–liquid boundary is unestablished or hard to see.
3. A new Windows recording with layered Foam (none known).

## Recommendation

1. **Review first (cheap, decisive).** Use review-010 through the existing O2
   workflow on the saved ④ bundle. At 678.5 s and 679 s, ask whether the
   published/anchor rows (Y238, Y229; Y391/392) are the air–liquid top, Foam
   interior or something else. Ask also where the air–liquid top is at 678.5 s.
   No run.
2. **Then one experiment, A + C, scoped to layered Foam.** The unchanged LBW-3
   unit qualifies ordered-lower demotion. It runs through the full pipeline,
   because TPA-1 showed admission and selection can still pick an older owner.
   Freeze the protocol, test sample4 (development) and then held-out option 1.
   `UNRESOLVED` leaves today's behaviour unchanged.
3. **Collapse handling (B or D) waits for step 1.** If Y229/Y238 is the air–liquid
   top, the fallback is already met and B becomes optional best-case work.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-SELECTOR`, `FOAM-EPISODE`, `SEQUENCE-COMPOSITION`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F10`.
- First harmful stage: `OIL-AUTHORITY` — texture-excluded support, then nearest-ordered-lower demotion under an upper anchor inside the Foam layer (AAT-1, TPA-1, ATG-1). At collapse onset the texture witness is unavailable (LBW-3).
- Existing feature coverage: reviewed the stored `oil_interface_diagnostics` and witness trace, the FULL debug images (`original_roi`, `grayscale`), and the closed CRW-1/PWC-1/RGB/colour-side, TPA-1, HPA-1 and LBW-1–3 results. No new mechanism is proposed outside these owners.
- Execution scope: desk review of source and closed evidence; no run, no Windows request, no human review yet.
- Logic-map impact: NONE — no source change.
- Failure-registry impact: NONE — review only.
