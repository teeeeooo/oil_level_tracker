# S11-D4 Foam Support Representation / Structural Component Classification

Status: Worker implementation complete on `fix/s11-d4-foam-support-structural-classification`; fresh Lane C exact-head audit required.

## Responsibility

S11-D4 changes only the current-frame S5-A Foam owner in `foam_front_detector.py`.
The responsibility remains:

`support representation -> component formation -> component classification -> S5-A outcome`.

`FoamTemporalGate` remains downstream and unchanged. D1 Foam-to-Oil context routing remains a separate defense-in-depth owner and is not weakened or moved.

## Support representation

Absolute whiteness remains the primary support path. D4 adds a second path for darker/yellow Foam only when independent current-frame evidence supports it:

- LAB warm chroma must be present without exceeding the existing configured maximum chroma;
- local texture must provide a seed;
- the seed may grow only through the same connected warm-chromatic textured region;
- the fallback is subordinate to the existing white+texture representation: if cleaned white support already contains a material non-structural component, S5-A preserves that white support instead of expanding it with chromatic pixels;
- a material white component that is itself wide/hollow structural does not disable the fallback, so genuine warm Foam can still fill/replace structural topology;
- otherwise chromatic and white support are unioned before the existing bounded morphology cleanup.

The fallback does not lower `foam_lightness_threshold` or globally relax whiteness membership. It does not use truth, time, file identity, trajectory, or lookahead.

## Component classification

D4 promotes the D1-proven wide/hollow row-topology discriminator into a shared current-frame morphology helper. A component is structural/refractive when all of these hold:

- width ratio >= 0.70;
- bounding-box fill ratio < 0.30;
- at least 25% of component rows span at least 35% of component width;
- median occupied/span compactness on those rows is < 0.65.

That class is rejected by S5-A even when its old scalar score is high. D1 independently reuses the same helper at the Foam-to-Oil handoff so the routing defense remains in depth.

The chromatic path may compensate for a broken bottom-support raster only for a substantial non-white component. If ordinary whiteness is already sufficient, chromatic evidence cannot bypass the existing bottom-connectivity shape requirement. This prevents bright/warm upper blobs from becoming Foam solely because the new representation exists.

A filled Foam component is not rejected merely because it is wide. Once genuine support fills the component, its fill/row topology no longer matches the hollow structural class.

## Frozen diagnostic evidence

The local MP4 results below are runtime diagnostic evidence, not tracked golden truth. Inputs and blind labels are the existing `sample/output/s11-foam-bidirectional-diagnostic/` artifacts.

For sample3 blind-positive rows (18 frames, 29.9966-38.5051 s):

- before: blind-band raw/clean support 0/18, component count 0/18, current-frame publication 0/18;
- after: blind-band raw support is non-zero in 11/18 and cleaned support is non-zero in 11/18;
- after: component representation exists in 18/18;
- after: 14/18 are `accepted_strong`, 3/18 `ambiguous`, 1/18 `weak_rejected`;
- 10/18 accepted fronts are within the blind front band expanded by +/-12 px.

A second non-bottom representation is allowed only for a substantial detached white/textured Foam layer. It must have at least 3x the configured minimum Foam area, 0.26-0.45 crop height, 0.55 crop width and 0.35 bounding-box fill. For that specific layer topology, the lower occupied row is the Foam front. This preserves the physical liquid/Foam transition instead of publishing the top of the visible Foam layer. Smaller detached bright blobs remain fail-closed.

For sample4 blind-negative representatives (14 frames, 0-32.5 s):

- before: all 14 were `accepted_strong` S5-A Foam and D1 later withheld Oil-context authority;
- after: all 14 are `weak_rejected`, none publishes Foam, and none reaches authoritative D1 handoff;
- the representative structural component remains approximately 0.75 crop width with bounding-box fill approximately 0.16.

For the frozen sample4 full replay (113 scheduled frames):

- before: Foam was published 113/113 and fill state was `FULL_WITH_FOAM` 113/113;
- after: Foam is published 4/113; `weak_rejected` is 109/113;
- blind-negative 0-32.5 s: 0/66 publish Foam;
- blind-positive 35-47.5 s: 2/26 publish Foam; the accepted 44.0 s and 46.5 s components use lower-edge fronts at 844 px and 842 px rather than the old fixed rim front;
- late uncertain tail 50-56 s: 2/13 publish Foam and 11/13 remain fail-closed;
- final fill states are `UNKNOWN_REVIEW` 112/113 and `FOAMING_VISIBLE` 1/113.

The sample4 positive side is intentionally conservative: the repair demonstrates that genuine later Foam can obtain a distinct filled/non-structural component and a physically meaningful lower-edge front, while frames whose white support does not satisfy that morphology remain rejected instead of inheriting authority from the old structural rim.

For the frozen sample3 full replay (81 scheduled frames), Foam publication changes from 20/81 to 50/81. Within the blind-positive 29.5-39 s interval, publication changes from 0/18 to 14/18. Final sample3 fill-state counts are `UNKNOWN_REVIEW` 30, `FULL_WITH_FOAM` 29, `FOAMING_VISIBLE` 16, `FULL_NO_INTERFACE` 4 and `DRAINING_VISIBLE` 2.

## Retained ownership and safety

D4 does not change `FoamTemporalGate`, fill-state policy, Recipe/Result/truth/schema contracts, or S5-B Oil observation/semantic owners. D1 still independently qualifies accepted Foam before it may constrain Oil. The wide/hollow helper refactor only removes duplicate topology calculation; D1 thresholds and fail-closed meaning are unchanged.

Existing glare, shimmer, variance-only, edge-only, white-Foam, low-light-Foam, partial-Foam, temporal-gate and controlled benchmark regressions remain the retained safety anchors. Adjacent Oil and no-interface owners are validated separately by the targeted suite before handoff.

## Resource trade-off

The chromatic path adds bounded ROI-sized float/bool maps and a seeded connected-component pass when chromatic texture exists. White-support arbitration adds one bounded connected-component/row-topology inspection before the existing final component classification. There is no unbounded state, frame history, lookahead, new dependency or ML path. The expected cost is a moderate current-frame CPU/memory increase in exchange for preventing both pre-component Foam loss and high-authority structural publication.

Generated replay/debug material remains local diagnostic evidence and is not tracked as golden truth. Merge-dependent status changes are intentionally left to the independent exact-head gate.
