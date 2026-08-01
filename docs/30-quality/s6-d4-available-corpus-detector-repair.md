# S6-D4 Available-Corpus Detector Accuracy Repair Evidence

**Status:** `WORKER COMPLETE — FRESH INDEPENDENT EXACT-HEAD AUDIT REQUIRED`

**Lane:** `C — Independent Review`

**Starting main:** `e04ce64384b31643795448fb6b16e47564a3b7c3`

**Feature branch:** `feature/s6-d4-available-corpus-detector-repair`

**Validated detector source/test commit:** `6f7e3744c89852a88dab22036ba408de32ec0f65`

**Exact next gate:** `S6-D4 Fresh Independent Exact-Head Detector Accuracy Repair Audit`

This record is a bounded available-corpus repair result. It does **not** establish category-balanced detector accuracy, general-field detector accuracy, missing-category coverage, Windows acceptance, packaging acceptance or long-duration acceptance.

## Frozen D3 authority reused

The accepted S6-D3 baseline was reused rather than rerun. Direct Git verification found no `src/oil_tracker` change between D3 source revision `47a5516e49872bcb6ffcd9c8147b2dcaa8640218` and starting `main @ e04ce64384b31643795448fb6b16e47564a3b7c3`.

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

The four exported D3 datasets, their benchmark catalogs and embedded detector settings were used read-only. Recipe, MP4, `.oiltruth`, provisional truth and D3 baseline evidence were not modified.

## Root cause

The production path was already generating Oil hypotheses on the usable real frames, but `evaluate_typed_current_observation` classified all 13 usable D3 cases as ambiguity before canonical publication.

Two distinct failure families were demonstrated:

1. **Foam-absent weak phase evidence:** sample1's pre-overlay weak Oil transition had a truth-near hypothesis, but normal single-frame canonical candidacy was dominated by no-interface/low semantic strength. The existing identifiability evidence showed strong texture relief with no near-ceiling collision pressure. Post-overlay sample1 frames contained much stronger paired horizontal structure and correctly remain ambiguous rather than being promoted merely because one hypothesis happens to lie near user truth.
2. **Oil beneath accepted Foam:** sample4 contained truth-near Oil hypotheses below the independently accepted Foam front, but white-Foam texture drove the grayscale plateau artifact likelihood high enough to prevent normal Oil candidacy. Globally lowering artifact acceptance would also weaken glare/structural protection, so that approach was rejected.

The defect was therefore repaired in typed positive-evidence ownership, not by modifying truth, benchmark denominators, Recipe settings or a general detector threshold until every frame became numeric.

## Production architecture change

Normal S5-B boundary acceptance remains first and unchanged. Only after that path fails, two conservative current-frame positive-evidence routes are available:

- **Foam-absent textured low-contrast phase:** requires a real broad transition, multiple broad scales, narrow support and horizontal coverage, high visibility/availability, bounded spatial/static conflicts, strong texture relief, low near-ceiling pressure, low collision pressure and reliable evidence. It does not use repetition as positive evidence.
- **Oil/Foam separated phase:** only an already accepted S5-A Foam front may supply the current-frame local-Y context. A candidate must lie below that front and still carry broad Oil phase support, narrow/horizontal evidence, visibility/availability and bounded spatial/static conflict. Foam presence by itself cannot create an Oil boundary.

S5-A Foam is evaluated independently before the S5-B Oil command so only the accepted current-frame Foam scalar can be copied into the immutable Oil command. That scalar is not persisted in `GlassTemporalRecord` or `TemporalStoreState`. All recovered numeric Oil values are still produced as typed `ShadowBoundaryObservation`, pass through the one serialized S5-B owner/reducer, and become numeric only through the existing canonical outcome/projection path. There is no legacy Oil fallback and no post-owner numeric injection.

No persisted detector-setting field, Recipe schema, truth schema, fixture schema, benchmark schema, CSV/debug schema, `PhaseDetection` schema, detector version or dependency changed.

## Final feature benchmark identity

Local ignored feature evidence root:

`sample/output/s6-d4-available-corpus-detector-repair/worker-6f7e374-20260801T175157Z/`

Composite feature evidence:

- `current-sample-feature.json`
- SHA-256: `42e7a3a8dae581d44580b500dcf27480e5a719fd5749399253a675a69bce7b93`
- exact detector source/test commit: `6f7e3744c89852a88dab22036ba408de32ec0f65`
- benchmark-reported detector version: `opencv-phase-detector-s5b-typed-production-v1`
- CLI generic `source_revision` field: `unavailable`; the exact Git commit above is therefore the source identity for this D4 feature evidence
- Python: `3.14.4`
- PySide6: `6.11.1`
- NumPy: `2.5.1`
- OpenCV headless: `4.14.0.94`
- Matplotlib: `3.11.1`

Every feature component run used its frozen D3 dataset and D3 component baseline via `--baseline`; every comparison reported `comparable` with an identical dataset fingerprint and detector-settings fingerprint.

| Sample | Dataset fingerprint | Settings fingerprint | Feature run fingerprint | Feature result SHA-256 |
|---|---|---|---|---|
| sample1 | `87d78ae6ba8969a597836404464751233782755a8669168b6ec282455d6d1235` | `8025572377a917f19b3cf09189613dc659fb8c9bc9552c6b2d9aac1b53d76704` | `bbc830bbcc8bafd4a5596f6dbd833977093b8cc9414edbd420f57cbfd0c5fe5b` | `89a000d5fb67145253efc89c5154ede09b33e8113ab15be7a29b9d21f0040c07` |
| sample2 | `389e5a1b004ab75c2632fa70267e43fbb6dfa6c8a65388e502aa5baaadb73c85` | `21f79342cae9dc9a0a518c2e7b229e19b4c14080d4f73731191ef11de6f41ee2` | `f880e5eb812b39e1ed3708882780a24f2502509c896c47454e2fe0f8b5ecc745` | `7d02413ac6c4c6fd6aac1381fcf5739880886ea7f5067add6964bb9b01109aa3` |
| sample3 | `15683924c9117d35b163fb20a3e5a478575742f4c67456c7d227a233e0bd3588` | `fe313352541327d0a7ef3912edf2709a0655a2e9e899de8d1ff1facec6ba3bce` | `b6387c9d003d7b5e2645a04efd145e1987504a1f01070fca6d8a9cd1cfce1f09` | `cf885a47501579af798e714226b8af42ffe0a04162216187e9b731bdaacad4eb` |
| sample4 | `cf0b6156689567abb0dc87d39f48f2f728dc25552630f2f872ae884915a77d6f` | `08d2a41dca20b28985f9c4c7ea1303bf31c9013dfe1981fa988dec72aa7b5058` | `bdc567720a6945c5a913a1236639681f805f9ecc205ab2991f95f7689a80d637` | `dd94b6aea5ac23368bf6200410e80c8c649816cdb941fbc9401fb417c823c076` |

## Base to feature aggregate delta

| Metric | D3 base | D4 feature | Delta / interpretation |
|---|---:|---:|---|
| raw Oil coverage | `0/13 = 0.000000` | `7/13 = 0.538462` | `+7` matched Oil boundaries |
| smoothed Oil coverage | `0/13 = 0.000000` | `7/13 = 0.538462` | `+7` matched Oil boundaries |
| raw Oil MAE | `not_evaluated` | `4.428571 px` over 7 matches | newly evaluated |
| raw Oil median / P90 / P95 | `not_evaluated` | `2.0 / 9.8 / 10.4 px` | newly evaluated |
| smoothed Oil MAE | `not_evaluated` | `4.428571 px` over 7 matches | newly evaluated; same positions on these independent fixtures |
| FillState accuracy | `0/13 = 0.000000` | `6/13 = 0.461538` | `+6` correct cases |
| Foam precision | `7/7 = 1.000` | `7/7 = 1.000` | no regression |
| Foam recall | `7/10 = 0.700` | `7/10 = 0.700` | no regression |
| matched Foam-front MAE | `47.285714 px` over 7 | `47.285714 px` over 7 | identical denominator and error |
| Foam-front median / P90 / P95 | `20.0 / 134.0 / 135.5 px` | `20.0 / 134.0 / 135.5 px` | unchanged |
| review/unknown | `6/13 = 0.461538` | `4/13 = 0.307692` | reduced by 2; not hidden by denominator change |

Foam denominators and all seven matched front positions are unchanged, so the Oil improvement is not purchased by weakening Foam publication or hiding a Foam-front regression.

## Complete per-case delta

All D3 base Oil positions were `null`; the table therefore reports each new feature Oil position explicitly rather than treating increased coverage alone as success.

| Sample | Frame | Accuracy use | Truth Oil | Feature Oil | Oil abs. error | Base FillState → feature FillState | Foam position base → feature |
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

The required cross-video scope is satisfied without sample identity logic:

- user-confirmed Foam-absent Oil: sample1 frame 144, `395.0` vs truth `386.0`, `9.0 px` error;
- user-confirmed Oil+Foam dual boundary: all five usable sample4 cases, Oil error `0.5–11.0 px`, with the independently accepted Foam positions unchanged;
- additional non-primary robustness improvement: sample3 frame 1035, `245.0` vs truth `243.0`, `2.0 px` error. sample3 remains lower-priority and did not drive the primary repair structure.

Post-overlay sample1 frames 156 and 240 remain ambiguity/review rather than promoting strong explanatory horizontal structure. sample2 remains conservative because accepted Foam context alone is insufficient without the required broad Oil phase support.

## FillState and review result

Feature FillState confusion on the 13 usable cases:

- truth `PARTIAL_VISIBLE` (3): `1 PARTIAL_VISIBLE`, `2 UNKNOWN_REVIEW`;
- truth `FOAMING_VISIBLE` (10): `5 FOAMING_VISIBLE`, `2 FULL_WITH_FOAM`, `1 PARTIAL_VISIBLE`, `2 UNKNOWN_REVIEW`.

The six correct cases are the recovered sample1 Foam-absent case plus all five sample4 dual-boundary cases. sample3 frame 1035 gains a truth-near Oil boundary but remains FillState-wrong because S5-A does not publish the authoritative Foam front in that frame; this is reported as residual behavior rather than counted as a FillState win.

Review/unknown falls from `6/13` to `4/13`. The four remaining review cases are sample1 frames 156/240, sample2 frame 0 and sample3 frame 900.

## Focused and targeted validation

Final source commit validation:

```text
170 passed in 35.52s
```

The targeted set covers:

- S5-B typed evidence and the new focused recovery regressions;
- exact latent glare/Oil collision fail-closed behavior and historical glare negatives;
- observability margin neighborhoods;
- plateau-evidence performance;
- serialized Oil owner ordering, resets, failure preservation and no-retained-raster/resource invariants;
- S5-B temporal reducer behavior;
- production cutover / sole numeric owner / external `PhaseDetection` compatibility;
- S5-A Foam integration, controlled benchmark and temporal gate;
- a focused negative proving accepted low-light Foam texture does not invent an Oil boundary.

A first targeted run exposed one test-seam compatibility issue: a legacy three-argument monkeypatch of `evaluate_typed_current_observation` received the new optional keyword even when Foam context was absent. The pipeline was repaired to preserve the old three-argument call whenever the context is `None`; the final targeted set then passed `170/170`.

Benchmark-contract suite:

```text
67 passed in 8.01s
```

This covers regression export/read integrity, benchmark runner/metrics/integration, atomic result writing and CLI comparison behavior.

`git diff --check` passed before the source/test commit. Final documentation validation and final-head `git diff --check` are part of the Worker closeout before Draft PR handoff.

### Resource/performance bound

No retained image, map, mask or Foam object was added to S5-B temporal state. The only new cross-detector input is one optional current-frame finite `float`, copied into the immutable prepared command and discarded after that command. The serialized owner and `TemporalStoreState`/`GlassTemporalRecord` shapes are unchanged. The targeted serialized-owner and retained-raster tests pass, as does the existing plateau-evidence performance suite.

No one-hour soak was rerun because this bounded scalar current-frame context and observation-selection change does not invalidate the already audited S6-F one-hour process/resource evidence. No official CPU-throughput claim is made here.

## Immutable inputs and intentional non-runs

Unchanged and untouched:

- all four product `.oiltruth` files;
- D3 dataset bytes and benchmark catalogs;
- embedded/persisted detector settings and Recipe snapshots;
- original MP4s;
- provisional truth;
- D3 baseline evidence root.

Intentionally not run:

- one-hour soak;
- Windows/manual GUI acceptance;
- packaging/PyInstaller acceptance;
- unrelated canonical suite.

Those gates were not invalidated by this bounded detector repair and remain outside D4 Worker authority.

## Residual unavailable categories and claim boundary

The current available corpus still does not cover the missing validation categories identified by D3: real scratch/surface defects, fogging/stain, clean rim-adjacent Oil, high-quality compressor-start fill/drain, transparent shimmer/refractive motion with authoritative Foam absence, structural rim/paired-line scenes distinct from explanatory overlays, clean full/empty no-interface, dropout/reacquisition transitions and broader independent field-video coverage.

Their metrics remain unavailable / `not_evaluated` where the authoritative denominator is absent. This D4 result claims only a material base-to-feature improvement on the frozen available corpus. It does **not** claim `Category-Balanced Official Detector-Accuracy Evidence: PASS` and does **not** claim general-field detector-accuracy PASS.

## Next gate

Worker merge authority is absent. The branch must remain Draft and unmerged.

Exact next gate:

`S6-D4 Fresh Independent Exact-Head Detector Accuracy Repair Audit`
