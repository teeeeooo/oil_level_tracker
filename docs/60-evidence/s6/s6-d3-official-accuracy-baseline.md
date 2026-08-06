# S6-D3 Official Current-Sample Detector Accuracy Baseline

## Status and boundary

- **Audited feature head:** `049d0eb49222b904c688686267acb01bf95374a9` over base `47a5516e49872bcb6ffcd9c8147b2dcaa8640218`
- **Merged PR/main:** `#66 @ 0a3cf34b8d4e0fbd9725a2de24612e62da910e50`
- **Accepted result:** `CURRENT-SAMPLE OFFICIAL BASELINE AND AVAILABLE-CORPUS POLICY: AUDITED AND ACCEPTED`
- **Truth authority:** audited S6-D2 product `.oiltruth` only
- **Truth count:** `15 total / 13 usable / 2 unusable`
- **Available-corpus constraint:** the current four real videos are the representative real-video corpus available at this stage; further representative acquisition is externally infeasible
- **Milestone:** S6 remains `ACTIVE`; S7 remains `PLANNED`
- **Next gate:** `S6-D4 Available-Corpus Detector Accuracy Repair`

This evidence measures the current production detector against the exact audited S6-D2 user truth. It is an official baseline for the existing four-video sample set, not a category-balanced S6 accuracy PASS. Fresh independent exact-head audit and native guarded squash merge are complete. Missing categories remain explicit unavailable/`not_evaluated` residual validation risk and are not reclassified as covered; the accepted policy permits only bounded improvement claims on the frozen available corpus.

## Fresh exact-head audit and acceptance

The independent Auditor verified PR #66 at exact feature head `049d0eb49222b904c688686267acb01bf95374a9` over base `47a5516e49872bcb6ffcd9c8147b2dcaa8640218`, with exactly two commits and the four expected documentation files. Before mutation, remote `main` still matched the exact base and the PR was same-repository and cleanly mergeable.

The preserved composite result reproduces SHA-256 `fbfc7aa34e00eeb002098f5d79a0f83288bd06aec014ecae3ebd9f177e207692`. All four exported datasets map exactly to the 15 audited S6-D2 annotations, preserve their truth payloads, and reload through the production dataset reader with the recorded fingerprints. Re-aggregating all 15 production case evaluations through `summarize_by_category` reproduces the stored category, micro and macro summaries exactly.

The material baseline is confirmed independently: `15 total / 13 usable / 2 unusable`; raw and smoothed Oil coverage `0/13`; fill-state accuracy `0/13`; Foam precision `7/7 = 1.000`; Foam recall `7/10 = 0.700`; matched Foam-front MAE `47.285714 px`. With no matched detector Oil positions, Oil positional errors remain `not_evaluated`; no-interface, shimmer false-positive and event metrics likewise remain `not_evaluated` where authoritative denominators are absent.

The coverage ledger does not promote production bucket names into unsupported field evidence. S1 remains weak-boundary evidence rather than a clear-boundary case, the two S3 focus-loss frames remain unusable, and missing clear, shimmer, structural/rim, rapid fill/drain, full/empty no-interface, transition and broader independent field-video evidence remain residual validation risk. The available-corpus exception requires identical frozen dataset bytes, benchmark catalog, detector settings and runtime environment for D4 base/feature comparison and permits improvement claims only for this available corpus.

Fresh focused benchmark-contract validation passed `67` tests in `8.03s`. Changed-document Markdown validation checked `41` relative links with no missing target, and `git diff --check` passed on the audited head. The Auditor did not start a new analyzer or detector benchmark, tune detector settings, or run Windows, packaging, GUI or long-duration validation.

PR #66 was marked Ready and native exact-base/head guarded-squash-merged as `main @ 0a3cf34b8d4e0fbd9725a2de24612e62da910e50`. Acceptance establishes the current available-corpus baseline and bounded repair policy only; it does not establish category-balanced or general-field detector-accuracy PASS.

## Production benchmark construction

The existing exporter schema binds one regression dataset to one exact result-bundle identity. Because S6-D2 truth spans four independent D1 production bundles with different run and Recipe identities, this Worker does not merge them into a synthetic multi-bundle dataset or change the schema.

Instead, the production `RegressionFixtureExporter`, `FilesystemRegressionDatasetReader`, CLI `benchmark`, benchmark metric domain and atomic result writer are reused four times, once per exact bundle. The 15 production case evaluations are then pooled through the existing `summarize_by_category` metric semantics into a local-only composite current-sample baseline. This composite does not replace any product/benchmark schema.

Local evidence root:

`sample/output/s6-d3-official-accuracy-baseline/worker-47a5516-20260801T160903Z/`

Composite current-sample dataset fingerprint: `a6845fcf225c99bae8032ae55003aadbd37352b62153395bb9d406450909d92b`.
## Exact component datasets and outputs

| Sample | Dataset fingerprint | Production benchmark result SHA-256 | Run fingerprint |
|---|---|---|---|
| sample1 | `87d78ae6ba8969a597836404464751233782755a8669168b6ec282455d6d1235` | `79ff95eed98e6e18933203fc0f0e45a547352f629a17a2bdbb3510e52f657dc6` | `edf0f66e291926153d04f064eb8a5456a38fce1038cccec31daacd9d03ef9ff7` |
| sample2 | `389e5a1b004ab75c2632fa70267e43fbb6dfa6c8a65388e502aa5baaadb73c85` | `e13108c1efe45a5a62234f6cf2260a4b761f2049119fb63cdac6e56663d36a05` | `210f38e5dc133123134753cc4fd7cbb8fc2522c92a3fb0ae5f356409b173218b` |
| sample3 | `15683924c9117d35b163fb20a3e5a478575742f4c67456c7d227a233e0bd3588` | `ab0d56a8ba4b6537f0633535a90a8f55c28efbd4db3f4f3af94d4b6978023d2b` | `95520abbc61b8b36ac9f16fd894e10147f352fe5706c7709e93fcf9b293232e3` |
| sample4 | `cf0b6156689567abb0dc87d39f48f2f728dc25552630f2f872ae884915a77d6f` | `db72203b3c7343c5158e4eefae101c519199843cd2cff399011ac327f2ed6c51` | `67834133584b70e9bd6eb3b6e90990a4eee4596050b5c9c676eef4b202431c8b` |

The four dataset paths are under `datasets/sample1` through `datasets/sample4` in the evidence root. The four production benchmark outputs are under `benchmarks/sample1` through `benchmarks/sample4`; each atomically contains exactly `benchmark_result.json`, `benchmark_cases.csv`, `benchmark_categories.csv`, `benchmark_summary.csv` and `benchmark_comparison.md` with no remaining staging directory.

Composite evidence:

- `current-sample-official-baseline.json`
- SHA-256: `fbfc7aa34e00eeb002098f5d79a0f83288bd06aec014ecae3ebd9f177e207692`
- composite run fingerprint: `75d3b34372f6c2d53461d16c18214ab69373c3c0ea49fa15152b08d9882df95a`
- combined detector-settings fingerprint: `9b8a0065a45d9231c136ffdb086964a002378470e90bc0b98d2078c97eadbc38`

All four CLI benchmark commands exited `0`.
## Current production identity

- Detector: `opencv-phase-detector-s5b-typed-production-v1`
- Source revision: `47a5516e49872bcb6ffcd9c8147b2dcaa8640218`
- Python: `3.14.4`
- PySide6: `6.11.1`
- NumPy: `2.5.1`
- OpenCV headless: `4.14.0.94`
- Matplotlib: `3.11.1`

All component runs used the exact detector settings embedded in their audited Recipe snapshots. The composite settings fingerprint covers the unique settings snapshots plus per-review assignment. No benchmark-time threshold override is used.

## Denominators and benchmark categories

The fixture denominator is `15 total`, with `13 usable` and `2 unusable`. `S3-03` and `S3-04` remain present as `reflection_or_blur` provenance/reason cases but are excluded from every accuracy denominator.

| Production benchmark category | Total | Usable | Meaning in this baseline |
|---|---:|---:|---|
| `clear_oil_boundary` | 3 | 3 | schema bucket for S1 weak visible Oil truth; not evidence that the scene is visually "clear" |
| `reflection_or_blur` | 5 | 3 | S2 reflection usable; S3 focus-loss two cases unusable |
| `white_foam` | 7 | 7 | S3/S4 Oil+Foam plus Foam metrics |
| `transparent_oil_full` | 0 | 0 | not covered |
| `transparent_oil_shimmer` | 0 | 0 | not covered |
| `structural_horizontal_edge` | 0 | 0 | not covered |
| `rapid_oil_flow` | 0 | 0 | not qualified as a temporal benchmark sequence |
| `no_interface` | 0 | 0 | not covered |
## Official current-sample metrics

### Oil boundary

All `13` usable truths contain an authoritative Oil boundary. The current detector publishes no raw or smoothed Oil boundary for any of them.

- raw Oil detection coverage: `0 / 13 = 0.000`
- smoothed Oil detection coverage: `0 / 13 = 0.000`
- raw Oil MAE / median / P90 / P95: `not_evaluated`
- smoothed Oil MAE / median / P90 / P95: `not_evaluated`
- raw/smoothed normalized Oil error: `not_evaluated`

The position-error metrics are not reported as a large invented penalty. Their denominator is `0 matched truth+detector positions`, with `13` usable truth positions unavailable because the detector boundary is missing and `2` unusable cases excluded.

There is no truth-absent Oil denominator. Therefore general truth-absent false-boundary rate and the required full/empty no-interface false-boundary rates are `not_evaluated`, not zero.

### Fill state and review ambiguity

Fill-state accuracy is `0 / 13 = 0.000`.

- truth `PARTIAL_VISIBLE`: `3` → detector `UNKNOWN_REVIEW` for all `3`
- truth `FOAMING_VISIBLE`: `10` → detector `FULL_WITH_FOAM` for `7`, `UNKNOWN_REVIEW` for `3`

Using the explicit current-sample criterion `usable and (predicted fill state == UNKNOWN_REVIEW or REVIEW_REQUIRED flag)`, the ambiguous/review-required rate is `6 / 13 = 0.461538`.
The six review-required usable cases all carry `LOW_CONFIDENCE`, `OIL_EVIDENCE_AMBIGUOUS` and `REVIEW_REQUIRED`; three also carry `FOAM_COMPONENT_REJECTED`, and one carries `FOAM_EVIDENCE_AMBIGUOUS`.

### Foam

Across the `13` usable cases, authoritative Foam presence is true in `10` and false in `3`. Smoothed detector Foam presence gives:

- true positive `7`
- false positive `0`
- false negative `3`
- true negative `3`
- precision `7 / 7 = 1.000`
- recall `7 / 10 = 0.700`

Seven authoritative Foam fronts have a matched detector front. Raw and smoothed front results are identical on this dataset:

- MAE: `47.285714 px`
- median absolute error: `20.0 px`
- P90: `134.0 px`
- P95: `135.5 px`
- normalized MAE: `0.214086`
- truth Foam-front positions unavailable from detector: `3`
- unusable exclusions: `2`

The shimmer Foam false-positive rate is `not_evaluated` because no usable shimmer fixture has authoritative Foam absence.
## Micro and macro category summaries

Micro aggregation pools all `13` usable cases. Macro aggregation uses equal weight only across production benchmark categories where a metric is evaluated.

| Metric | Micro | Macro |
|---|---:|---:|
| raw Oil detection coverage | `0.000` | `0.000` across 3 evaluated categories |
| smoothed Oil detection coverage | `0.000` | `0.000` across 3 evaluated categories |
| fill-state accuracy | `0.000` | `0.000` across 3 evaluated categories |
| Foam precision | `1.000` | `1.000` across 2 evaluated categories |
| Foam recall | `0.700` | `0.690476` across 2 evaluated categories |
| raw Foam-front MAE | `47.285714 px` | `73.45 px` across 2 evaluated categories |
| smoothed Foam-front MAE | `47.285714 px` | `73.45 px` across 2 evaluated categories |
| raw Foam normalized MAE | `0.214086` | `0.278774` across 2 evaluated categories |
| smoothed Foam normalized MAE | `0.214086` | `0.278774` across 2 evaluated categories |

Within populated production benchmark buckets, reflection/blur Foam recall is `2/3 = 0.666667` with matched-front MAE `134.5 px`; white-Foam recall is `5/7 = 0.714286` with matched-front MAE `12.4 px`. Oil coverage and fill-state accuracy are `0` in every populated usable bucket.

Event timestamp accuracy is `not_evaluated` because regression fixture schema v1 contains no authoritative event truth. No temporal reacquisition/dropout metric is claimed because the selected D2 frames are not promoted into an invented dense sequence.

## Authoritative validation-category coverage ledger

The validation-plan category matrix is stricter than the eight-key benchmark catalog. A production catalog bucket is therefore not automatically treated as authoritative coverage of every similarly named field scenario.
| Validation-plan category | Current status | Current evidence |
|---|---|---|
| clear Oil boundary | not covered | S1 is explicitly weak rather than clear |
| weak transparent-Oil boundary | covered for current sample | `S1-01–S1-03` |
| transparent-Oil full/no-interface | not covered | none |
| transparent-Oil agitation/shimmer/refractive motion | not covered | no usable truth with authoritative Foam absence |
| real white Foam | covered for current sample | `S2-01–S2-03`, `S3-01–S3-02`, `S4-01–S4-05` |
| glare/reflection/blur/fogging | partial | usable reflection `S2-01–S2-03`; blur only as unusable `S3-03–S3-04`; fogging absent |
| structural horizontal edge/rim/paired line | not covered | S1 explanatory overlay is not reinterpreted as structural evidence |
| rapid Oil fill/drain/compressor-start transient | not covered | no dense authoritative sequence; S3-04 drain context is unusable |
| full and empty no-interface | not covered | none |
| dropout/reacquisition/visible↔no-interface transitions | not covered | none |

The existing four-video set therefore does not satisfy category-balanced official detector-accuracy eligibility. sample3 focus-loss remains lower-priority robustness evidence only. sample4 remains the primary current Oil-under-Foam dual-boundary evidence and is not used to claim missing temporal/no-interface categories.

## Available-corpus repair policy alignment

The domain owner has recorded the current four real videos as the representative corpus available at this stage and further representative acquisition as externally infeasible. This constraint changes the executable sequence, not the D3 baseline or coverage ledger. Bounded detector repair may proceed only after this baseline/policy head passes fresh independent audit, using the exact frozen D3 dataset bytes, benchmark catalog, detector settings and runtime environment for base/feature comparison.

User-confirmed/corrected truth remains mandatory authority for tuning. Missing categories remain residual risk and unavailable/`not_evaluated`; synthetic or current-frame substitutes cannot satisfy them. The resulting repair may establish improvement on the available corpus only and cannot establish category-balanced or general-field detector-accuracy PASS.

## Residual unavailable categories and historical acquisition ledger

The following acquisition list records the exact missing evidence identified by the D3 baseline. It is retained as historical coverage evidence and is **not** the current executable gate because the domain owner has recorded further representative real-video acquisition as externally infeasible at this stage. None of these categories is reclassified as covered; absent-category metrics remain unavailable/`not_evaluated`, and category-balanced/general-field accuracy PASS remains unavailable.

If future external evidence becomes feasible, the original identified acquisition needs remain:

1. real scratch/surface-defect video with usable truth;
2. fogging/stain video with usable truth;
3. clean rim-adjacent visible Oil boundary;
4. high-quality fill and drain sequence with compressor-start context and dense sequential truth;
5. clean `FULL_NO_INTERFACE` and `EMPTY_NO_INTERFACE` cases;
6. transparent-Oil agitation/shimmer/refractive-motion cases with authoritative Foam absence;
7. structural rim/paired-line cases distinct from explanatory overlays;
8. dropout/reacquisition and visible↔no-interface transition sequences;
9. broader independent field-video coverage beyond the current four videos.

## Reproducibility and validation

Each component dataset was benchmarked a second time using the first `benchmark_result.json` as `--baseline`. All four reruns exited `0`, were reported `comparable`, reproduced the exact dataset, settings and run fingerprints, and reproduced the complete case payload, category summaries, micro aggregate and macro aggregate. Every comparable evaluated metric delta was unchanged; unavailable metrics remained `not_evaluated`.

Focused existing suite:

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/test_regression_fixture_exporter.py \
  tests/test_regression_dataset_reader.py \
  tests/test_detector_benchmark_runner.py \
  tests/test_detector_benchmark_metrics.py \
  tests/test_detector_benchmark_integration.py \
  tests/test_benchmark_result_writer.py \
  tests/test_benchmark_cli.py
```

Result: `67 passed in 7.93s`.

The four audited `.oiltruth` files loaded against their exact preserved D1 bundles before export. All component dataset readers passed integrity/fingerprint validation, all four benchmark outputs passed atomic five-file completeness, and unusable denominator exclusion remained exactly `2`.

## Acceptance boundary and next gate

**Current-sample official baseline produced; category-balanced gate remains unsatisfied because required field categories and broader independent video coverage are unavailable.** The low Oil coverage `0/13`, fill-state accuracy `0/13`, Foam recall `0.700` and every other D3 metric remain unchanged. Additional representative acquisition is externally infeasible at this stage; this does not convert any missing category into covered evidence.

No detector source/settings/threshold, Recipe, MP4, `.oiltruth`, provisional-truth or local D3 evidence bytes were modified by the D3 baseline/policy work or fresh audit. The policy-alignment Worker did not rerun the baseline; the Auditor ran only the focused benchmark-contract test suite and direct read-only evidence recomputation, not a new detector benchmark or analyzer. Windows, packaging, GUI, canonical-suite, long-duration validation and detector tuning were not performed. This evidence does not declare `Category-Balanced Official Detector-Accuracy Evidence: PASS` or general-field accuracy PASS, does not close S6 and does not start S7.

The exact next gate is **`S6-D4 Available-Corpus Detector Accuracy Repair`**, using the same frozen D3 dataset bytes, benchmark catalog, detector settings and runtime environment. This Close records that gate without starting D4. The current-sample baseline remains preserved as the comparison baseline; missing categories remain residual unavailable/`not_evaluated` risk.
