# S11-R2 Foam/Spatial Authority Diagnostic

**Date:** `2026-08-09`

**Diagnosed head:** `86937d4f3dd55396b3ecf39efaa4e9a6ec4fb8ab`

**Status:** `CAUSE ISOLATED — bounded repair authorized by current work plan`

## Question

Can the detector provide a more faithful observed Oil trajectory without lowering global thresholds, interpolating missing samples or tuning to one repository video?

The review compared the production `OpenCvPhaseDetector`, matching Recipes, frozen truth/provisional annotations and direct Glass-ROI inspection across all four real videos. Generated replay bundles are diagnostic support only; source, Recipe and retained truth remain authority.

## Reproduced baseline

The exact 2 FPS qualification replay reproduced the accepted Slice D baseline:

| Video | Numeric Oil | Coverage |
|---|---:|---:|
| `base_sample_1` | 3 / 30 | 10.0% |
| `sample2` | 2 / 5 | 40.0% |
| `sample3` | 42 / 151 | 27.8% |
| `sample4` | 62 / 113 | 54.9% |
| **Total** | **109 / 299** | **36.5%** |

The retained 13-frame user-confirmed truth surface remained `8/13` numeric with `5.4375 px` MAE. Coverage is not accuracy: unclear, no-interface, blur and overlay frames remain in the replay denominator.

## Earliest demonstrated loss

Direct review did not identify one safe global threshold reduction. It isolated a composition seam in accepted-Foam context:

1. the current-frame D5 selector can accept a narrow bottom structure as the incumbent Oil boundary;
2. `oil_shadow_pipeline` asks Spatial for a fallback only when the current result is ambiguous, so an accepted but artifact-dominant incumbent cannot be challenged;
3. inside the fallback, a preliminary relative boundary whose own Spatial path fails returns immediately, preventing the existing textured 5/5 selector from evaluating another candidate.

At `sample4` frame `1080` (`36.0 s`), the accepted-Foam incumbent was approximately `y=868` with boundary/artifact likelihood `0.290/0.726` and only `2` supporting sectors. The same raster contained a relative candidate near `y=842` with boundary/artifact likelihood `0.486/0.522` and an accepted `5/5` cross-ROI path. Visual inspection places the material interface near the latter candidate. The higher-quality proof existed but had no bounded route to replace a numeric incumbent.

Two later sample4 observations near `y=884/883` were also visibly bottom-structure excursions. Their Foam-separated narrow horizontal support was `0.261/0.232`, below the support expected of the material interface but above the existing `0.20` admission floor.

## Rejected ablations

The following probes are explicitly rejected:

- relaxing weak paired-edge opposition from `0.80` to `0.95`: it recovered sample4 anchors but created six false numeric observations on the explanatory overlay in `base_sample_1`;
- admitting general three-sector weak paths: a census exposed repeated overlay candidates in `base_sample_1`;
- applying the ordinary `paired_edge_strength <= 0.80` ceiling to every D5 Foam-separated candidate: it removed the user-confirmed `sample4:1680 -> y=866` Oil anchor and therefore cannot distinguish the retained Foam/Oil phase from the misleading structure class;
- globally lowering boundary, artifact or ambiguity thresholds;
- forcing a top-ranked candidate, filling graph gaps or publishing temporal interpolation;
- using sample, frame, Recipe or truth identity in production.

These failures show that more permissive Spatial eligibility is not a safe corpus-wide fix.

## Selected bounded repair

The selected repair transfers authority only where stronger existing proof is already present:

1. raise Foam-separated narrow horizontal support from `0.20` to `0.30`;
2. under authoritative accepted-Foam context, when a preliminary relative boundary fails its own Spatial path, continue to the existing full-path textured selector instead of ending the search;
3. allow a Spatial challenger to an accepted boundary only under authoritative accepted-Foam context, when the incumbent is artifact-dominant by at least `0.20` and fails its own Spatial path;
4. replace the incumbent only when the challenger passes unchanged Spatial safety and improves the semantic boundary-minus-artifact margin by at least `0.08`.

If any condition fails, the incumbent is preserved exactly. Temporal state, hard no-interface, glare/exclusion/border safety, Foam topology and canonical publication remain unchanged.

## Pre-implementation probe result

An in-memory composition probe predicted the following qualification delta without relaxing Spatial thresholds:

- `base_sample_1`, `sample2` and `sample3`: exact numeric stream unchanged;
- `sample4`: `62 -> 63` numeric observations;
- added visually consistent anchors near frames `1080`, `1320` and `1590`;
- removed bottom-structure excursions near frames `1275` and `1455`;
- corrected frame `1635` from approximately `y=866` to `y=853`.

The purpose is not the net `+1`. The material gain is replacing misleading extrema and restoring several real interface anchors while keeping the known overlay negative unchanged.

## Claim boundary

This diagnostic authorizes only the bounded Foam/Spatial authority repair specified above. It does not establish general detector accuracy, authorize further threshold tuning or make every visible-looking frame numeric. Final claims require exact-source replay, retained truth metrics, controlled negatives and report-output inspection under the companion validation contract.
