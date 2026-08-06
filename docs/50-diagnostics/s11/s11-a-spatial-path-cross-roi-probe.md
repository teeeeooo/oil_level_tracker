# S11-A Spatial Path / Cross-ROI Consistency Probe

## Status and authority

- Role: S11-A Spatial Path / Cross-ROI Consistency Probe Worker
- Lane: B — Bounded Change
- Starting `main`: `3305cb8268fd4e1612105cba6144c2083066ff8c`
- Probe branch: `feature/s11-a-spatial-path-probe`
- Scope: diagnostic implementation, tests, and evidence only
- Production `src/` mutation: none
- Product truth: existing S6 repository-local `.oiltruth` corpus only
- Truth denominator: `15 reviewed / 13 usable / 2 unusable`

This probe asks whether current-frame cross-ROI spatial relationships add positive Oil evidence
that is not already present in the strongest-row/scalar representation. It does not implement
P2 no-interface repair, production cutover, temporal trajectory inference, new dependencies,
or schema changes.

The deterministic native-corpus manifest is
`docs/50-diagnostics/s11/s11-a-spatial-path-cross-roi-probe-manifest.json`.
Its timing-free canonical result fingerprint is:

`0ba7a8c8f1fd9352479cba86557416bab9055eebf9e7ce991ff4cfaa47ce8382`

Manifest SHA256:

`b9be0960eb2a1f25d343242f1f992c455d270d8fa153006ec53305606b0ffdd4`

## Owner and boundary inspection

The directly inspected production path remains:

1. `geometry_masks.build_mask_bundle`
2. `preprocessing.preprocess`
3. S5-A `detect_bottom_connected_foam` + `FoamTemporalGate`
4. `oil_shadow_observations.extract_raw_observations`
5. `build_bounded_proposals`
6. `evaluate_semantic_hypotheses`
7. `evaluate_typed_current_observation`
8. serialized `OilHypothesisPipeline` / fixed canonical reducer
9. `oil_hypothesis_projection.project_production_result`

Adjacent owners inspected were the S5-A Foam detector/gate, the S5-B observational-equivalence
fixtures, retained glare negatives, and the S6-D4 Foam-separated Oil recovery path.

S6-D4 already uses spatial evidence, but only after accepted Foam context: glare/Foam pixels are
removed and three horizontal sectors must preserve the same outer-phase ordering. That mechanism
is intentionally not a generic no-Foam fallback. The new probe therefore remains outside
production ownership and reuses the same current-frame raster inputs only diagnostically.

No evidence required a production observability semantic change, temporal-owner transfer,
public/persisted contract change, dependency change, or new shared architecture owner during this
probe. A future production cutover would itself be a new mutation gate for the Orchestrator.

## Selected spatial mechanism

The diagnostic variant is a conservative gate around the previously explored relative-phase
candidate route. It runs only when P0 is Ambiguous and the relative-phase route has already
produced a canonical numeric boundary candidate.

For that candidate it:

1. removes current-frame glare and, when independently accepted, S5-A Foam pixels;
2. splits the effective ROI width into five sectors;
3. searches at most `±12 px` around the candidate in each sector;
4. compares robust top/bottom outer-phase medians using the existing maximum broad scale;
5. selects each sector's strongest local phase row relative to its own MAD/quantization noise;
6. requires at least three consecutive sectors with the same strong phase ordering;
7. requires the resulting local path to vary by more than one integer row;
8. bounds adjacent path motion by `2 × maximum_proposal_diameter_px = 12 px`; and
9. requires the path median to remain within the existing narrow search radius of the candidate.

The `>1 row` non-degeneracy condition is architectural, not a truth/frame special case. A perfectly
flat sector path collapses back to the same single-row fact already represented by scalar/row
features, so it cannot be claimed as genuinely new cross-ROI evidence. Such a path remains
fail-closed in this fallback even if its scalar phase contrast is extremely strong.

This differs from a row-score weight or threshold change because acceptance depends on the ordered
relationship among independently optimized local rows at different x positions. No sample name,
frame number, truth y, Recipe identity, or file hash participates in scoring.

## Native corpus result

Current-main P0 was re-executed on all 13 usable truth rows rather than inferred from the older
manifest:

- P0 numeric Oil coverage: `7 / 13`
- P0 matched MAE: `4.428571 px` (`31 / 7`)
- spatial-gated numeric Oil coverage: `9 / 13`
- spatial-gated matched MAE: `4.888889 px` (`44 / 9`)
- regression among the seven P0 numeric anchors: `0 / 7`

The two added native recoveries are:

| case | truth y | spatial result y | error | accepted sector path |
| --- | ---: | ---: | ---: | --- |
| `sample2:30` | `592` | `599` | `7 px` | `277 → 273 → 267` |
| `sample2:60` | `592` | `598` | `6 px` | `283 → 279 → 272` |

The aggregate MAE rises by about `0.46 px` because two newly numeric rows with `7 px` and `6 px`
errors enter the denominator. No previously numeric P0 row moves, so this is coverage/error tradeoff
rather than a matched-anchor regression.

Residual misses after the variant remain `base_sample_1:156`, `base_sample_1:240`, `sample2:0`, and
`sample3:900`. This probe therefore does not establish general-field or complete S11 accuracy.

## Protection evidence

### S5-B observational-equivalence collision

The prior scalar relative-phase route produced numeric Oil on `14 / 16` collision scenes. The same
14 candidates reach the spatial gate, but all 14 are rejected as `degenerate_scalar_row` because
their independently optimized sector path spans only `0–1 px`.

- scalar P1 collision numeric: `14 / 16`
- spatial-gated collision numeric: `0 / 16`
- pair-output divergence: none

The latent-glare and latent-Oil members of every collision pair therefore remain observationally
identical and fail closed with no numeric Oil.

### Retained glare / structure / Foam

- historical retained glare negatives: `0 / 21` false numeric Oil
- structural/Foam stress set: `0 / 9` false numeric Oil
- S5-A Foam result preserved on structural/Foam set: `9 / 9`

The spatial probe consumes accepted Foam only as current-frame exclusion context; it does not
create, persist, or reinterpret Foam ownership.

### Targeted low-light warning

Because the mechanism reuses the P1 candidate route, the known P1 photometric warning was rerun
proportionally rather than repeating the full 416-result matrix. On `sample4:450`, P1 again proposes
`804 px` at brightness `0.60` and `0.45`. Both are rejected because the candidate is local `y=6`
and lacks the symmetric outer-phase window required for path evidence.

## Resource and compute evidence

The path evidence is current-frame only and retains no additional history or per-Glass state.
The deterministic scan bound is:

- sectors: `5`
- local rows per sector: at most `2 × 12 + 1 = 25`
- maximum sector-row evaluations per candidate: `125`
- top/bottom phase windows: bounded by existing maximum broad scale `10 px`
- retained temporal state added by probe: `0`

A one-pass native diagnostic run measured median P0 wall time `110.10 ms` and median spatial-wrapper
wall time `276.61 ms` on the development machine. The wrapper intentionally reruns existing P0/P1
helpers for isolation, so that number is diagnostic implementation cost rather than a production
optimization claim. Any production candidate should share already-owned preprocessing/evidence
where possible while preserving the same deterministic spatial bound.

## Decision

**Conclusion: sufficient spatial candidate for the next production-repair design gate.**

The deciding evidence is not coverage alone. The same scalar relative-phase candidate family that
was unsafe in PR #79 becomes selectively useful when a genuinely cross-ROI, non-degenerate local
path is required: native coverage improves by two rows, existing P0 anchors do not move, all retained
observational-equivalence collisions remain non-numeric, and retained glare/structure/Foam
protections remain closed.

This is not production approval and does not establish detector/general-field accuracy. It only
answers the bounded S11-A architecture question positively enough to justify Orchestrator review of
a future production mutation. Four native residual misses remain, so the Orchestrator may still
choose to limit production scope or proceed later to the separately owned offline temporal
trajectory question.

## Validation and intentional non-runs

Executed during development:

- direct native 13-row P0 and spatial diagnostic runs
- direct S5-B 8-pair / 16-scene collision comparison
- direct 21-case retained glare-negative comparison
- direct 9-case structural/Foam stress comparison
- targeted `sample4:450` brightness `0.60` and `0.45` warning replay
- `python -m pytest -q tests/test_s11_spatial_path_probe.py` → `7 passed`

The stabilized Worker gate additionally requires one relevant targeted suite and `git diff --check`;
those exact final-head results are recorded in the Worker handoff rather than predeclared here.

Intentionally not run because they are outside this bounded probe:

- full canonical / E2E validation
- full prior 416-result photometric matrix
- Windows packaging or installer validation
- private company field-video validation
- P2 production no-interface repair
- production detector cutover
- temporal photometric/component history
- offline trajectory reconstruction / graph interpolation
- optical flow, background subtraction, ML, or new dependency experiments

## Next gate

The next authority is **Lane B Orchestrator exact-head bounded review**. The Orchestrator owns the
decision whether this evidence is sufficient to authorize a production repair, what Lane that
production mutation requires, or whether the remaining residuals warrant the separately scoped
offline temporal trajectory probe instead. This Worker does not merge, synchronize `main`, Close
S11-A, or claim detector/general-field accuracy PASS.
