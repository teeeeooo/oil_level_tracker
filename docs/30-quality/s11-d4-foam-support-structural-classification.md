# S11-D4 Foam Support Representation / Structural Component Classification

Status: Lane C FAIL findings repaired on `fix/s11-d4-foam-support-structural-classification`; fresh independent exact-head audit required.

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

The fallback does not lower `foam_lightness_threshold` or globally relax whiteness membership. It does not use truth, time, file identity, trajectory, or lookahead. Support membership alone is not publication authority: every non-bottom component must separately satisfy the physical detached-layer classifier described below.

## Component classification

D4 promotes the D1-proven wide/hollow row-topology discriminator into a shared current-frame morphology helper. A component is structural/refractive when all of these hold:

- width ratio >= 0.70;
- bounding-box fill ratio < 0.30;
- at least 25% of component rows span at least 35% of component width;
- median occupied/span compactness on those rows is < 0.65.

That class is rejected by S5-A even when its old scalar score is high. D1 independently reuses the same helper at the Foam-to-Oil handoff so the routing defense remains in depth.

Publication authority now uses one non-bottom detached-layer contract for both white and chromatic support. A detached component must have at least 2.5x the configured minimum Foam area, 0.15-0.68 crop height, at least 0.55 crop width, bounding-box fill from 0.30 through 0.80, material texture, and white or chromatic appearance evidence. Its row occupancy must also be one-sided: the more occupied outer third must average at least 0.20 occupancy and exceed the opposite outer third by at least 1.30x. Uniform stripes, grids and random mottling may therefore enter support representation but cannot obtain S5-A publication merely from color and texture.

Front semantics are representation-independent. Bottom-connected Foam keeps the upper supported edge. A qualified detached layer normally uses its upper supported edge; when an independently rejected wide/hollow structural substrate is below it, S5-A requires the layer to be spatially separate from that substrate by at least three rows and uses the layer's lower supported edge as the physical transition front. A component whose bounding box still overlaps or nearly touches that structural substrate is not treated as detached Foam. A filled Foam component is still not rejected merely because it is wide once its own topology no longer matches the hollow structural class.

## Frozen diagnostic evidence

The local MP4 results below are runtime diagnostic evidence, not tracked golden truth. Inputs and blind labels are the existing `sample/output/s11-foam-bidirectional-diagnostic/` artifacts.

The FAIL finding was reproduced with generic detached warm structures. Vertical stripes, horizontal stripes, a grid and deterministic random mottling could previously obtain strong component authority; a full production warm-grid probe reached accepted Foam, D1 authority and Foam-derived fill-state authority. After the repair all four deterministic structure classes are `weak_rejected` with no candidate and no D1 authority. The full production warm-grid probe is `weak_rejected`, has no raw or smoothed Foam, D1 authority is false, and fill state remains `UNKNOWN_REVIEW`.

For sample3 blind-positive rows (18 frames, 29.9966-38.5051 s):

- pre-D4 baseline: blind-band raw/clean support 0/18, component count 0/18, current-frame publication 0/18;
- FAIL head `b2e934e`: blind-band support 11/18, component representation 18/18 and publication 14/18;
- repaired head working evidence: blind-band raw/clean support remains 11/18 and component representation remains 18/18;
- repaired classification publishes 12/18 as `accepted_strong`, with 4/18 `ambiguous` and 2/18 `weak_rejected`;
- 10/18 accepted fronts remain within the blind front band expanded by +/-12 px.

For sample4 blind-negative structural evidence:

- the 14 frozen 0-32.5 s representatives remain 14/14 `weak_rejected`, with zero Foam publication and zero D1 authority;
- the denser 0.5 s replay over the same blind-negative interval is also 0/66 published Foam, all 66 `weak_rejected`, and zero numeric Oil;
- the old 113/113 structural Foam publication behavior does not return.

For the frozen sample4 full replay (113 scheduled frames), the repaired head publishes Foam on 27/113 rows and leaves 86/113 `weak_rejected`. The blind-positive 35-47.5 s interval publishes 14/26 rows instead of the FAIL head's 2/26. At representative frames 37.5, 40, 42.5, 45 and 47.5 s, the separately represented non-structural layer publishes lower-edge fronts at 837, 840, 837, 836 and 836 px while the wide/hollow substrate remains independently rejected. The 35 s representative remains fail-closed because only two rows separate its candidate support from the structural substrate; the interval is therefore no longer explained away as one structural weak-rejection class while retaining a conservative separation boundary.

The later blind-uncertain 50-56 s interval publishes 10/13 rows and leaves 3/13 fail-closed. Those rows are not promoted by a time rule or count target; they satisfy the same current-frame detached-layer topology as the positive interval. This diagnostic remains intentionally non-golden and does not convert the blind uncertain label into truth.

For the frozen sample3 full replay (81 scheduled frames), Foam publication is 47/81. Within the blind-positive 29.5-39 s interval, publication is 12/18. Final sample3 fill-state counts are `UNKNOWN_REVIEW` 38, `FULL_WITH_FOAM` 23, `FOAMING_VISIBLE` 16 and `FULL_NO_INTERFACE` 4. The two-frame reduction from the FAIL head's 14/18 publication is the cost of removing generic non-bottom chromatic authority rather than returning toward the original 0/18 support failure.

## Retained ownership and safety

D4 does not change `FoamTemporalGate`, fill-state policy, Recipe/Result/truth/schema contracts, or S5-B Oil observation/semantic owners. D1 still independently qualifies accepted Foam before it may constrain Oil. The wide/hollow helper refactor only removes duplicate topology calculation; D1 thresholds and fail-closed meaning are unchanged.

Existing glare, shimmer, variance-only, edge-only, white-Foam, low-light-Foam, partial-Foam, temporal-gate and controlled benchmark regressions remain the retained safety anchors. Adjacent Oil and no-interface owners are validated separately by the targeted suite before handoff.

## Resource trade-off

The chromatic path adds bounded ROI-sized float/bool maps and a seeded connected-component pass when chromatic texture exists. White-support arbitration and classification add bounded connected-component, row-occupancy and structural-substrate relation scans over the current ROI. There is no unbounded state, frame history, lookahead, new dependency or ML path. The expected cost is a moderate current-frame CPU/memory increase in exchange for preventing both pre-component Foam loss and unqualified structural/colored-texture authority.

Generated replay/debug material remains local diagnostic evidence and is not tracked as golden truth. Merge-dependent status changes are intentionally left to the independent exact-head gate.
