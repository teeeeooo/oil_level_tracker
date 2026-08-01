# S6-D4 Available-Corpus Detector Accuracy Repair Evidence

**Status:** `WORKER COMPLETE — FRESH INDEPENDENT EXACT-HEAD RE-AUDIT REQUIRED`

**Lane:** `C — Independent Review`

**Starting main:** `e04ce64384b31643795448fb6b16e47564a3b7c3`

**Feature branch:** `feature/s6-d4-available-corpus-detector-repair`

**PR:** `#67 — fix: improve available-corpus oil boundary detection` — Draft, unmerged

**Auditor-failed head:** `71af3205e4e1242ccc1a323e3cac174296366210`

**Repaired detector source/test commit:** `c2c58fc1b58bbade421bb032cc219a56092bd816`

**Exact next gate:** `S6-D4 Fresh Independent Exact-Head Detector Accuracy Repair Re-Audit`

This record supersedes the pre-repair D4 feature benchmark generated at source commit `6f7e3744c89852a88dab22036ba408de32ec0f65`. That prior feature result demonstrated available-corpus accuracy improvement, but the fresh Auditor found a load-bearing Foam-context structural false-Oil regression. The prior feature composite SHA-256 `42e7a3a8dae581d44580b500dcf27480e5a719fd5749399253a675a69bce7b93` is therefore historical failed-head evidence and is not the acceptance target.

The repaired result remains a bounded available-corpus result. It does **not** establish category-balanced detector accuracy, general-field detector accuracy, missing-category coverage, Windows acceptance, packaging acceptance or long-duration acceptance.

## Frozen D3 authority reused

The accepted S6-D3 base remains valid and was not rerun. Direct Git verification again found zero `src/oil_tracker` changes between D3 detector source revision `47a5516e49872bcb6ffcd9c8147b2dcaa8640218` and S6-D4 starting `main @ e04ce64384b31643795448fb6b16e47564a3b7c3`.

Frozen D3 evidence root:

`sample/output/s6-d3-official-accuracy-baseline/worker-47a5516-20260801T160903Z/`

Authoritative identities:

- D3 composite result SHA-256: `fbfc7aa34e00eeb002098f5d79a0f83288bd06aec014ecae3ebd9f177e207692`
- composite dataset fingerprint: `a6845fcf225c99bae8032ae55003aadbd37352b62153395bb9d406450909d92b`
- combined detector-settings assignment fingerprint: `9b8a0065a45d9231c136ffdb086964a002378470e90bc0b98d2078c97eadbc38`
- denominator: `15 total / 13 usable / 2 unusable`
- baseline Oil raw/smoothed coverage: `0/13`
- baseline FillState accuracy: `0/13`
- baseline Foam precision: `7/7 = 1.000`
- baseline Foam recall: `7/10 = 0.700`
- baseline matched Foam-front MAE: `47.285714 px`
- baseline review/unknown: `6/13`

The four exported D3 datasets, benchmark catalogs, embedded detector settings, Recipe snapshots, original MP4s, product `.oiltruth`, provisional truth and D3 evidence remained read-only.

## Auditor FAIL reproduction

The fresh Auditor reported that accepted Foam context could bypass the structural/artifact ambiguity contract: structural horizontal evidence that was ambiguous without Foam became numeric Oil after an accepted Foam front was supplied.

The Worker reproduced the defect independently at starting PR head `71af3205e4e1242ccc1a323e3cac174296366210` in two forms.

### Typed evidence reproduction

The same structural hypothesis with strong paired-edge/pulse evidence produced:

- without Foam context: `ShadowAmbiguousObservation`;
- with only an accepted Foam front: `ShadowBoundaryObservation`.

No Oil evidence changed between those evaluations. The optional Foam front was therefore acting as a route authorization that bypassed the pre-existing structural ambiguity protection.

### Production-path reproduction

A controlled `white-foam` frame was augmented with one horizontal structural band and no Oil phase. At the failed head:

- Foam: accepted strong at `120 px`;
- false raw Oil: `128 px`;
- false smoothed Oil: numeric;
- FillState: `FOAMING_VISIBLE`;
- Oil decision: `boundary_accepted`.

The false selected Oil hypothesis was strongly artifact-dominant (`artifact_likelihood ≈ 0.841`) while still satisfying the first D4 Foam-separated route. Globally requiring low artifact likelihood or a low paired-edge score was rejected as the repair because genuine sample4 Oil-under-Foam hypotheses also carry high grayscale artifact/pulse evidence under real white Foam.

## Root cause and bounded repair

The original D4 Foam-separated route used only the accepted S5-A Foam **front coordinate** as positive context. It required a candidate to be below that front, but did not prove that the candidate was spatially separated from the accepted Foam component. A structural band inside the Foam body could therefore create a broad transition and be reinterpreted as Oil.

The repaired path keeps all prior S5-B evidence guards and adds one current-frame spatial-separation requirement from the already accepted S5-A component:

1. S5-A still independently owns Foam detection and temporal acceptance.
2. If Foam is accepted, the detector derives an immutable per-row support profile: for each ROI row, the fraction of effective pixels belonging to the accepted Foam component.
3. The accepted Foam front and row-support tuple are copied into the serialized S5-B command as current-frame context only.
4. Foam-separated Oil recovery is unavailable when only a Foam front is supplied without the support profile.
5. A candidate below the Foam front may use the bounded recovery only when its own proposal interval is **not majority occupied by the accepted Foam component**. The `0.50` boundary is the literal majority-occupancy definition, not a corpus accuracy threshold.
6. The existing broad phase, narrow/horizontal, visibility/availability, glare/exclusion/border and static-prior guards still apply unchanged.
7. The normal S5-B canonical acceptance path remains first and unchanged.

The accepted Foam profile is not persisted in `GlassTemporalRecord` or `TemporalStoreState`; it is an immutable tuple of finite unit scalars that exists only in the current command. No Foam raster, mask, candidate object or history is retained by S5-B.

This structure does not use filename, hash, Recipe ID, Glass ID, frame number, sample identity or truth coordinate. No persisted detector setting or external schema changes.

## Structural+Foam regression after repair

The new production integration regression uses accepted controlled white Foam plus a horizontal structural band and no Oil phase.

Repaired production result:

- Foam: `120.0 px`, `accepted_strong`;
- raw Oil: `None`;
- smoothed Oil: `None`;
- Oil decision: `ambiguous`;
- FillState: `FULL_WITH_FOAM`, not false `FOAMING_VISIBLE`;
- flags retain `FOAM_STRONG_EVIDENCE` and `OIL_EVIDENCE_AMBIGUOUS`.

The typed regression also proves that the same structural hypothesis remains ambiguous with accepted Foam when the candidate interval is occupied by the accepted Foam component, while spatially separated broad-phase evidence can still use the bounded recovery path.

## Repaired feature benchmark identity

The source repair invalidated the previous D4 feature benchmark, so the feature side was regenerated at exact source commit `c2c58fc1b58bbade421bb032cc219a56092bd816` against the same frozen D3 component datasets and baselines.

Local ignored repaired feature evidence root:

`sample/output/s6-d4-available-corpus-detector-repair/worker-c2c58fc-20260801T184338Z/`

Composite repaired feature evidence:

- `current-sample-feature.json`
- SHA-256: `b2995711093b8e0ecdbeca23eae7dbebb303c37aa52add9f3119d4a9732795c0`
- exact detector source/test commit: `c2c58fc1b58bbade421bb032cc219a56092bd816`
- detector version: `opencv-phase-detector-s5b-typed-production-v1`
- Python: `3.14.4`
- PySide6: `6.11.1`
- NumPy: `2.5.1`
- OpenCV headless: `4.14.0.94`
- Matplotlib: `3.11.1`

Every component comparison is `comparable`; dataset fingerprints, detector-settings fingerprints and run fingerprints match the frozen D3 comparison contract.

| Sample | Dataset fingerprint | Settings fingerprint | Repaired run fingerprint | Repaired result SHA-256 |
|---|---|---|---|---|
| sample1 | `87d78ae6ba8969a597836404464751233782755a8669168b6ec282455d6d1235` | `8025572377a917f19b3cf09189613dc659fb8c9bc9552c6b2d9aac1b53d76704` | `bbc830bbcc8bafd4a5596f6dbd833977093b8cc9414edbd420f57cbfd0c5fe5b` | `0f98f788897313fb481678fde9b9daf4b53c41c3a00c212f34141f0fe8288ca7` |
| sample2 | `389e5a1b004ab75c2632fa70267e43fbb6dfa6c8a65388e502aa5baaadb73c85` | `21f79342cae9dc9a0a518c2e7b229e19b4c14080d4f73731191ef11de6f41ee2` | `f880e5eb812b39e1ed3708882780a24f2502509c896c47454e2fe0f8b5ecc745` | `84871f1923e069b756a6159922bedd0c6dd66a812d0011919bf0050eeb1e993b` |
| sample3 | `15683924c9117d35b163fb20a3e5a478575742f4c67456c7d227a233e0bd3588` | `fe313352541327d0a7ef3912edf2709a0655a2e9e899de8d1ff1facec6ba3bce` | `b6387c9d003d7b5e2645a04efd145e1987504a1f01070fca6d8a9cd1cfce1f09` | `80291c2d9b7cd2452f9bbb83a025cabf62533e6e947434da9b681a2557d51f0c` |
| sample4 | `cf0b6156689567abb0dc87d39f48f2f728dc25552630f2f872ae884915a77d6f` | `08d2a41dca20b28985f9c4c7ea1303bf31c9013dfe1981fa988dec72aa7b5058` | `bdc567720a6945c5a913a1236639681f805f9ecc205ab2991f95f7689a80d637` | `63d1b6b657892d6a27c16275d5164982b96ba2e604d49eb0c835204a18d13d29` |

The repaired 15-case detector outputs are exactly equal to the previous failed-head feature outputs on the frozen D3 corpus. The safety repair therefore removes the demonstrated structural false-Oil path without purchasing safety by deleting the available-corpus gains.

## D3 base → repaired feature aggregate

| Metric | D3 base | Repaired D4 feature | Delta / interpretation |
|---|---:|---:|---|
| raw Oil coverage | `0/13 = 0.000000` | `7/13 = 0.538462` | `+7` matched Oil boundaries |
| smoothed Oil coverage | `0/13 = 0.000000` | `7/13 = 0.538462` | `+7` matched Oil boundaries |
| raw Oil MAE | `not_evaluated` | `4.428571 px` over 7 matches | newly evaluated |
| raw Oil median / P90 / P95 | `not_evaluated` | `2.0 / 9.8 / 10.4 px` | newly evaluated |
| smoothed Oil MAE | `not_evaluated` | `4.428571 px` over 7 matches | same independent-frame positions |
| FillState accuracy | `0/13 = 0.000000` | `6/13 = 0.461538` | `+6` correct cases |
| Foam precision | `7/7 = 1.000` | `7/7 = 1.000` | no regression |
| Foam recall | `7/10 = 0.700` | `7/10 = 0.700` | no regression |
| matched Foam-front MAE | `47.285714 px` over 7 | `47.285714 px` over 7 | identical denominator/error |
| Foam-front median / P90 / P95 | `20.0 / 134.0 / 135.5 px` | `20.0 / 134.0 / 135.5 px` | unchanged |
| review/unknown | `6/13 = 0.461538` | `4/13 = 0.307692` | improved, denominator unchanged |

Foam denominators and all seven matched Foam-front positions are unchanged.

## Complete per-case repaired delta

All D3 base Oil positions were `null`; every repaired numeric position is shown explicitly.

| Sample | Frame | Use | Truth Oil | Repaired Oil | Oil abs. error | Base FillState → repaired FillState | Foam base → repaired |
|---|---:|---|---:|---:|---:|---|---|
| sample1 | 240 | usable | 386.0 | null | not matched | `UNKNOWN_REVIEW → UNKNOWN_REVIEW` | `null → null` |
| sample1 | 156 | usable | 386.0 | null | not matched | `UNKNOWN_REVIEW → UNKNOWN_REVIEW` | `null → null` |
| sample1 | 144 | usable | 386.0 | 395.0 | 9.0 px | `UNKNOWN_REVIEW → PARTIAL_VISIBLE` | `null → null` |
| sample2 | 30 | usable | 592.0 | null | not matched | `FULL_WITH_FOAM → FULL_WITH_FOAM` | `452.0 → 452.0` |
| sample2 | 0 | usable | 592.0 | null | not matched | `UNKNOWN_REVIEW → UNKNOWN_REVIEW` | `null → null` |
| sample2 | 60 | usable | 592.0 | null | not matched | `FULL_WITH_FOAM → FULL_WITH_FOAM` | `457.0 → 457.0` |
| sample3 | 1035 | usable | 243.0 | 245.0 | 2.0 px | `UNKNOWN_REVIEW → PARTIAL_VISIBLE` | `null → null` |
| sample3 | 2848 | unusable | null | null | excluded | `UNKNOWN_REVIEW → UNKNOWN_REVIEW` | `null → null` |
| sample3 | 900 | usable | 316.0 | null | not matched | `UNKNOWN_REVIEW → UNKNOWN_REVIEW` | `null → null` |
| sample3 | 3147 | unusable | null | null | excluded | `UNKNOWN_REVIEW → UNKNOWN_REVIEW` | `null → null` |
| sample4 | 1680 | usable | 858.5 | 866.0 | 7.5 px | `FULL_WITH_FOAM → FOAMING_VISIBLE` | `843.0 → 843.0` |
| sample4 | 450 | usable | 852.5 | 853.0 | 0.5 px | `FULL_WITH_FOAM → FOAMING_VISIBLE` | `848.0 → 848.0` |
| sample4 | 0 | usable | 860.5 | 861.0 | 0.5 px | `FULL_WITH_FOAM → FOAMING_VISIBLE` | `849.0 → 849.0` |
| sample4 | 900 | usable | 848.5 | 848.0 | 0.5 px | `FULL_WITH_FOAM → FOAMING_VISIBLE` | `845.0 → 845.0` |
| sample4 | 1470 | usable | 855.0 | 866.0 | 11.0 px | `FULL_WITH_FOAM → FOAMING_VISIBLE` | `844.0 → 844.0` |

Cross-video improvement remains material without sample-specific logic:

- Foam-absent Oil: sample1 frame 144, `395.0` vs truth `386.0`, error `9.0 px`;
- Oil+Foam dual boundary: all five usable sample4 cases, errors `0.5–11.0 px`, with Foam outputs unchanged;
- additional non-primary recovery: sample3 frame 1035, `245.0` vs truth `243.0`, error `2.0 px`.

Post-overlay sample1 frames remain ambiguous/reviewable. sample2 remains conservative. sample3 focus-loss cases remain unusable and do not drive tuning.

## Focused validation

Focused D4 red/green pair after the repair:

```text
45 passed in 2.91s
```

Affected S5-A/S5-B suite including exact observability collisions, margin regressions, plateau performance, serialized owner ordering/failure/resource invariants, production cutover, Foam integration, Foam controlled benchmark and Foam temporal gate:

```text
172 passed in 34.63s
```

Additional controlled Oil plus benchmark export/read/runner/metric/result/CLI validation:

```text
357 passed in 49.00s
```

The new structural+Foam production regression is included in these passing results.

### Resource and ownership validation

The repair adds no retained raster or temporal history. The per-row Foam support profile is copied into the immutable current-frame command as a finite tuple and discarded after the command. `TemporalStoreState`, `GlassTemporalRecord`, reducer state, owner ordering and retained-resource bounds are unchanged. Serialized-owner/no-retained-raster tests and the plateau performance suite pass.

## Immutable inputs and intentional non-runs

Unchanged and untouched:

- all four product `.oiltruth` files;
- D3 dataset bytes and benchmark catalogs;
- embedded/persisted detector settings and Recipe snapshots;
- original MP4s;
- provisional truth;
- D3 baseline evidence root.

Intentionally not rerun:

- one-hour soak;
- Windows/manual GUI acceptance;
- packaging/PyInstaller acceptance;
- unrelated canonical acceptance suite.

The D3 base benchmark was not rerun because its production source ancestry and preserved evidence hash remain valid. Only the repaired feature side was regenerated.

## Residual unavailable categories and claim boundary

The current available corpus still lacks real scratch/surface-defect, fogging/stain, clean rim-adjacent Oil, high-quality compressor-start fill/drain, transparent shimmer/refractive motion with authoritative Foam absence, structural/rim/paired-line field scenes distinct from explanatory overlays, clean full/empty no-interface, dropout/reacquisition transitions and broader independent field-video coverage.

Their metrics remain unavailable / `not_evaluated` where authoritative denominators are absent. This repaired D4 result claims only a material base-to-feature improvement on the frozen available corpus. It does **not** claim `Category-Balanced Official Detector-Accuracy Evidence: PASS` and does **not** claim general-field detector-accuracy PASS.

## Next gate

Worker merge authority is absent. PR #67 remains Draft and unmerged.

Exact next gate:

`S6-D4 Fresh Independent Exact-Head Detector Accuracy Repair Re-Audit`
