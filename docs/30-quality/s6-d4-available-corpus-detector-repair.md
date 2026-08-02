# S6-D4 Available-Corpus Detector Accuracy Repair Evidence

**Status:** `PARTIAL-FOAM STRUCTURAL FALSE-OIL REPAIR WORKER COMPLETE — FRESH INDEPENDENT EXACT-HEAD RE-AUDIT REQUIRED`

**Lane:** `C — Independent Review`

**Starting main:** `e04ce64384b31643795448fb6b16e47564a3b7c3`

**Feature branch:** `feature/s6-d4-available-corpus-detector-repair`

**PR:** `#67 — fix: improve available-corpus oil boundary detection` — Draft, unmerged

**Second-repair starting PR head:** `2dc14a13cf3ae1d25b9941c3b9026cc8a224525f`

**Latest repaired detector source/test commit:** `6b2ea43e8ae62773d4ae6ce17754477d810c78c6`

**Exact next gate:** `S6-D4 Fresh Independent Exact-Head Detector Accuracy Repair Re-Audit`

This record supersedes both earlier S6-D4 feature targets. The original feature at source `6f7e3744c89852a88dab22036ba408de32ec0f65` / composite `42e7a3a8dae581d44580b500dcf27480e5a719fd5749399253a675a69bce7b93` failed audit because an accepted Foam front could authorize structural false Oil. The first repair at source `c2c58fc1b58bbade421bb032cc219a56092bd816` / composite `b2995711093b8e0ecdbeca23eae7dbebb303c37aa52add9f3119d4a9732795c0` closed the demonstrated full-Foam case but failed the second audit because partial Foam can leave the same structural evidence with low per-row Foam occupancy. Those outputs are historical navigation evidence only; the current acceptance target is the exact head containing source commit `6b2ea43e8ae62773d4ae6ce17754477d810c78c6` plus this source-completing documentation.

The result remains a bounded available-corpus result. It does **not** establish category-balanced detector accuracy, general-field detector accuracy, missing-category coverage, Windows acceptance, packaging acceptance or long-duration acceptance.

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

The four exported D3 datasets, benchmark catalogs, embedded detector settings, Recipe snapshots, original MP4s, product `.oiltruth`, provisional truth and D3 baseline evidence remained read-only.

## Two Auditor FAILs and independent second-failure reproduction

The first D4 audit established that an accepted Foam-front coordinate alone could promote otherwise ambiguous structural horizontal evidence into numeric Oil. The first repair preserved the accepted Foam component only as a per-row occupancy tuple and allowed Foam-context recovery when candidate occupancy was below `0.50`.

The second audit demonstrated why that scalar compression was insufficient: accepted **partial Foam** leaves large horizontal regions outside the component, so a structural line can have low row occupancy even while it is not evidence of a separate Oil phase. Genuine sample4 Oil-under-Foam candidates occupy overlapping low-support ranges and may also carry high artifact likelihood and paired-edge evidence. Therefore the Worker did not tune the `0.50` value, add an artifact-likelihood cutoff or replace it with another one-dimensional threshold.

The defect was reproduced independently at starting PR head `2dc14a13cf3ae1d25b9941c3b9026cc8a224525f` using the controlled accepted partial-Foam scene with no Oil truth. A diagnostic matrix varied structural-band position, height and intensity. The current route published false numeric Oil in `60` combinations. A separate narrow-partial-Foam sweep produced `8` additional numeric structural false-Oil cases at substantially lower Foam occupancy. These diagnostics confirmed that row occupancy had lost the horizontal component geometry needed to distinguish a local line from a distinct phase.

Several apparently simpler repairs were explicitly rejected during diagnosis:

- requiring accepted Foam support to disappear below Oil was false for genuine sample4;
- requiring strict near/far outer-band sign agreement rejected genuine sample4 frames;
- treating a strong paired edge as structural was invalid because genuine sample4 can retain paired-edge evidence after Foam masking;
- a single residual-contrast or artifact-likelihood cutoff overlapped genuine sample4 and would recreate a threshold cliff rather than identify a distinct phase.

## Repaired discrimination principle

The repaired route preserves full accepted S5-A component geometry as **current-frame evidence** and asks whether an Oil-like phase persists outside the local structure.

1. S5-A still independently owns Foam detection and temporal acceptance.
2. If Foam is accepted, an isolated read-only copy of the accepted current-frame Foam component mask and accepted front is copied into the serialized S5-B command.
3. Inside the sole S5-B owner, accepted Foam pixels and glare pixels are removed from the current raster support.
4. The candidate's local pulse neighborhood is excluded using existing S5-B geometry only: maximum broad-band scale, paired-edge separation and proposal diameter. No new persisted setting is introduced.
5. The remaining visible ROI is split deterministically into left/center/right sectors.
6. Each available sector compares robust median outer plateaus above and below the candidate. A sector is unavailable if an otherwise-visible row loses all residual samples.
7. Differences at or below the raster quantization step carry no phase direction. A sector is strong only when its median phase shift exceeds its own top/bottom median-absolute-deviation noise.
8. Foam-context recovery requires the **same phase ordering in at least two of three sectors**, with at least one matching sector strong versus its own noise.

This is repeated spatial phase evidence, not a corpus-fit intensity threshold. A local horizontal band can create strong edges near itself, but it does not establish the same separate phase across independent residual sectors. Genuine sample4 retains cross-sector outer-phase evidence after accepted Foam and local pulse pixels are excluded.

The normal S5-B canonical acceptance path remains first and unchanged. The Foam-absent textured low-contrast route is unchanged. A Foam front without its accepted component mask cannot authorize the D4 Foam-separated route.

The accepted Foam mask exists only in the immutable current-frame command. It is not persisted in `GlassTemporalRecord` or `TemporalStoreState`; no Foam history is added. Numeric Oil still originates only from typed `ShadowBoundaryObservation`, passes through the canonical serialized S5-B reducer and reaches `PhaseDetection` only through the existing projection path. There is no legacy fallback or post-owner numeric injection.

No persisted detector setting, Recipe field, external `PhaseDetection` field, truth/fixture/benchmark/CSV/debug schema field, detector version or dependency changed.

## Controlled structural regressions

The production-path regression set now covers more than one hand-picked structural band.

### Partial Foam neighborhood

Committed tests exercise accepted `partial-foam` with six band geometries spanning multiple Y positions and heights:

- `(y=123, height=2, value=150)`
- `(y=132, height=4, value=180)`
- `(y=138, height=5, value=180)`
- `(y=150, height=6, value=180)`
- `(y=156, height=4, value=180)`
- `(y=165, height=5, value=180)`

Every case preserves accepted Foam, publishes raw/smoothed Oil `None`, retains `OIL_EVIDENCE_AMBIGUOUS` and does not become false `FOAMING_VISIBLE`.

Additional committed narrow-partial-Foam cases use accepted Foam widths `16` and `20` pixels with the same structural band. Both remain fail-closed. The broader Worker diagnostic matrix that produced `60 + 8` false numeric cases at the starting head was re-evaluated against the proposed discriminator before implementation: all `68/68` were rejected while genuine sample4 remained `5/5` eligible.

### Full white Foam regression

The previously repaired controlled white-Foam structural case remains fail-closed:

- Foam remains accepted;
- raw Oil `None`;
- smoothed Oil `None`;
- Oil remains ambiguous;
- no false `FOAMING_VISIBLE`.

### Genuine Oil preservation

The frozen D3 production path preserves the same truth-near Oil results:

- Foam-absent sample1 frame `144`: `395.0` vs truth `386.0`, error `9.0 px`;
- sample3 frame `1035`: `245.0` vs truth `243.0`, error `2.0 px`;
- sample4 all five usable Oil+Foam cases remain numeric with errors `0.5–11.0 px` and unchanged Foam positions.

## Fresh feature benchmark identity

Because production source changed, the first-repair feature evidence `b2995711093b8e0ecdbeca23eae7dbebb303c37aa52add9f3119d4a9732795c0` is superseded. The feature side was regenerated at exact source commit `6b2ea43e8ae62773d4ae6ce17754477d810c78c6` against the same frozen D3 datasets and component baselines.

Local ignored feature evidence root:

`sample/output/s6-d4-available-corpus-detector-repair/worker-6b2ea43-20260802T033029Z/`

Composite feature evidence:

- `current-sample-feature.json`
- SHA-256: `b098a070927ffcf9230a57cd94827a8fe8eedec9a08f591591404c29271cf70c`
- schema: local composite `s6-d4-available-corpus-feature-evidence-v2`
- exact detector source/test commit: `6b2ea43e8ae62773d4ae6ce17754477d810c78c6`
- detector version: `opencv-phase-detector-s5b-typed-production-v1`
- Python: `3.14.4`
- PySide6: `6.11.1`
- NumPy: `2.5.1`
- OpenCV headless: `4.14.0.94`
- Matplotlib: `3.11.1`

Every component comparison is `comparable`; dataset/settings/run fingerprints remain identical to the frozen D3 comparison contract.

| Sample | Dataset fingerprint | Settings fingerprint | Feature run fingerprint | Feature result SHA-256 |
|---|---|---|---|---|
| sample1 | `87d78ae6ba8969a597836404464751233782755a8669168b6ec282455d6d1235` | `8025572377a917f19b3cf09189613dc659fb8c9bc9552c6b2d9aac1b53d76704` | `bbc830bbcc8bafd4a5596f6dbd833977093b8cc9414edbd420f57cbfd0c5fe5b` | `c9f1599a3ad1624efc8052f8008f93f30afe67e5bde2d31d39990a9a6cf2df8b` |
| sample2 | `389e5a1b004ab75c2632fa70267e43fbb6dfa6c8a65388e502aa5baaadb73c85` | `21f79342cae9dc9a0a518c2e7b229e19b4c14080d4f73731191ef11de6f41ee2` | `f880e5eb812b39e1ed3708882780a24f2502509c896c47454e2fe0f8b5ecc745` | `94f7cd18b16f795a78683d154350d038fe3e4e33030c04c1514cfaf5288a8e29` |
| sample3 | `15683924c9117d35b163fb20a3e5a478575742f4c67456c7d227a233e0bd3588` | `fe313352541327d0a7ef3912edf2709a0655a2e9e899de8d1ff1facec6ba3bce` | `b6387c9d003d7b5e2645a04efd145e1987504a1f01070fca6d8a9cd1cfce1f09` | `eeead60af55e7a34389254613f16242739f843f3368a2d014217026a04deedc9` |
| sample4 | `cf0b6156689567abb0dc87d39f48f2f728dc25552630f2f872ae884915a77d6f` | `08d2a41dca20b28985f9c4c7ea1303bf31c9013dfe1981fa988dec72aa7b5058` | `bdc567720a6945c5a913a1236639681f805f9ecc205ab2991f95f7689a80d637` | `d460f73b288862f439c4d9d70c312a1c5f1107e39be6976be68a3dd5473c820b` |

## D3 base → latest feature aggregate

| Metric | D3 base | Latest D4 feature | Delta / interpretation |
|---|---:|---:|---|
| raw Oil coverage | `0/13 = 0.000000` | `7/13 = 0.538462` | `+7` matched Oil boundaries |
| smoothed Oil coverage | `0/13 = 0.000000` | `7/13 = 0.538462` | `+7` matched Oil boundaries |
| raw Oil MAE | `not_evaluated` | `4.428571 px` over 7 matches | newly evaluated |
| raw Oil median / P90 / P95 | `not_evaluated` | `2.0 / 9.8 / 10.4 px` | truth-near published positions |
| smoothed Oil MAE | `not_evaluated` | `4.428571 px` over 7 matches | same independent-frame positions |
| FillState accuracy | `0/13 = 0.000000` | `6/13 = 0.461538` | material improvement |
| Foam precision | `7/7 = 1.000` | `7/7 = 1.000` | no regression |
| Foam recall | `7/10 = 0.700` | `7/10 = 0.700` | no regression |
| matched Foam-front MAE | `47.285714 px` over 7 | `47.285714 px` over 7 | identical denominator/error |
| Foam-front median / P90 / P95 | `20.0 / 134.0 / 135.5 px` | `20.0 / 134.0 / 135.5 px` | unchanged |
| review/unknown | `6/13 = 0.461538` | `4/13 = 0.307692` | below D3, denominator unchanged |

Foam denominators and all seven matched Foam-front positions are unchanged.

## Complete per-case latest delta

All D3 base Oil positions were `null`; every latest numeric position is shown explicitly.

| Sample | Frame | Use | Truth Oil | Feature Oil | Oil abs. error | Base FillState → feature FillState | Foam base → feature |
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

Cross-video improvement remains material without sample-specific logic: Foam-absent sample1 is represented, all five sample4 dual-boundary cases remain represented, and sample3 frame 1035 remains an additional non-primary recovery. Post-overlay sample1 frames remain ambiguous/reviewable. sample2 remains conservative. sample3 focus-loss cases remain unusable and do not drive tuning.

## Validation

Focused D4 evidence/integration tests including the full-Foam negative and the new partial-Foam neighborhood:

```text
53 passed in 3.77s
```

Affected-owner validation covering S5-B single-frame observability, margin and plateau contracts, production cutover, serialized owner ordering/failure/resource invariants, temporal reduction, controlled Oil, S5-A Foam integration/controlled benchmark/temporal gate:

```text
470 passed in 74.39s
```

Benchmark-contract checks covering regression export/read integrity, benchmark runner/metrics/integration, atomic result writer and CLI comparison behavior:

```text
67 passed in 7.98s
```

The source-tree frozen-D3 probe also reproduced the latest feature positions before the CLI benchmark was regenerated.

### Resource and ownership validation

The accepted Foam component mask is copied into the immutable current-frame S5-B command as an owned read-only raster. It is discarded after evidence construction and is not retained by the temporal store. `TemporalStoreState`, `GlassTemporalRecord`, reducer state and serialized owner ordering are unchanged. Existing serialized-owner/resource tests pass.

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

The D3 base benchmark was not rerun because its production source ancestry and preserved evidence hash remain valid. Only the latest feature side was regenerated.

## Residual unavailable categories and claim boundary

The available corpus still lacks real scratch/surface-defect, fogging/stain, clean rim-adjacent Oil, high-quality compressor-start fill/drain, transparent shimmer/refractive motion with authoritative Foam absence, structural/rim/paired-line **field** scenes distinct from controlled diagnostic structure, clean full/empty no-interface, dropout/reacquisition transitions and broader independent field-video coverage.

The new controlled structural regressions close the demonstrated software regression but do not convert the missing real structural field category into official accuracy coverage. Missing-category metrics remain unavailable / `not_evaluated` where authoritative denominators are absent. This D4 result claims only material improvement on the frozen available corpus and controlled fail-closed protection for the reproduced structural defect. It does **not** claim category-balanced or general-field detector-accuracy PASS.

## Next gate

Worker merge authority is absent. PR #67 must remain Draft and unmerged.

Exact next gate:

`S6-D4 Fresh Independent Exact-Head Detector Accuracy Repair Re-Audit`
