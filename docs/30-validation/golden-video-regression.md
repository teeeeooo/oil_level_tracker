# Golden Video and Detector Benchmark Regression

## Authority and scope

This document is the execution guide for the detector benchmark and regression obligations referenced by the [real-world validation plan](real-world-validation-plan.md). Product, truth and architecture decisions remain subordinate to the [product SSOT](../rotary_oil_level_tracker_ssot_spec.md), while current milestone state and gate belong to the [roadmap](../00-project/roadmap.md) and [work plan](../00-project/work-plan.md).

S1 builds a repeatable baseline around the existing Phase 2C-3 regression fixture
export. It does **not** change detector algorithms, thresholds, `.oiltruth`, the
regression fixture export schema or the official result bundle.

## S5-B controlled observability truth

The S5-B single-frame observability contract uses a dedicated test-only owner,
`tests/oil_observability_fixtures.py`. It does not extend exporter schema version 1,
`.oiltruth`, the benchmark catalog or any external result schema.

Each controlled collision records latent scene cause, whether numeric physical oil
geometry exists, latent oil Y when present, current detector identifiability and the
expected canonical outcome family as separate fields. An oil-bearing scene may be
unidentifiable from the effective current raster; its expected detector outcome is
then ambiguity rather than a fabricated no-oil truth.

Observationally equivalent latent glare/oil pairs must have the same canonical
`AmbiguousOutcome`, no raw or smoothed numeric oil, `NO_UPDATE`, `PRESERVE` and
review-required projection. Repeated identical unresolved observations do not become
positive temporal evidence. See the [S5-B architecture contract](../20-architecture/s5b-oil-boundary-hypothesis-architecture.md).

## Deterministic controlled comparison datasets

Repository-owned synthetic oil and Foam comparison generators use the same exporter, reader, truth and catalog schemas as ordinary datasets, but their test owner must make every exported byte reproducible across temporary roots and Python processes. `tests/controlled_dataset_identity.py` owns controlled contract version `v1`, fixed timestamps and namespace-based UUID5 derivation for the dataset, annotation set and per-case annotations. The derivation includes dataset kind, recipe and session snapshots, bundle identity, category and sequence metadata, truth fields and each raster SHA-256. Oil and Foam therefore have distinct stable identities, and a contract-version or raster change produces a different identity rather than silently reusing an old one.

The only production seam is the optional exporter `dataset_id_factory`. Its default remains a new UUID4 on every export. The UI and user truth/export workflow do not pass the seam and retain runtime UUID uniqueness and wall-clock timestamps. Controlled fixture code supplies the deterministic factory and constructs an explicit fixed-time `UserTruthSet`; it does not modify `UserTruthSet.create()` or annotation defaults.

Controlled recipe creation/update timestamps and session source paths are normalized only inside generated test snapshots. Geometry, detector settings, truth, rasters, categories, sequence membership/order and schema versions are not normalized or inferred. Reader fingerprint composition, SHA-256 verification, traversal/symlink protection and atomic export finalization remain load-bearing and unchanged. Generated datasets remain outside the repository.

The former oil and Foam fingerprints `0528deb1…` and `a091165d…` were one-off runtime identities whose bytes were not preserved and are retired. Historical exact fingerprints and their audit state belong in completed evidence; this validation contract requires deterministic logical identity and repeatable reader verification rather than carrying an old audit-pending status forward.

## Dataset source

Create annotations in Result Review and export them with the Phase 2C-3 regression
fixture action. Keep real compressor videos, exported datasets and benchmark outputs
outside the repository.

An exporter schema-version 1 dataset contains:

```text
oil_regression_dataset_YYYYMMDD_HHMMSS/
├─ dataset_manifest.json
└─ fixtures/
   └─ <fixture-id>/
      ├─ fixture_manifest.json
      ├─ frame.png
      ├─ roi_crop.png
      ├─ truth.json
      ├─ official_reference.json
      ├─ recipe_snapshot.oilrecipe
      └─ session_snapshot.json
```

The benchmark reader verifies the dataset, fixture and truth schema versions; all
manifest SHA-256 values; source-frame, recipe, session and annotation identity; and
safe relative paths. Absolute paths, `..` traversal, root escape, symlink escape,
duplicate IDs/manifest entries and unsupported future schemas are rejected.

## Benchmark categories

Machine-readable keys are stable and the Korean meanings are:

| Key | 의미 |
|---|---|
| `clear_oil_boundary` | 뚜렷한 유면 |
| `transparent_oil_full` | 투명 오일 가득 참 |
| `transparent_oil_shimmer` | 투명 오일 교반·아지랑이 |
| `white_foam` | 실제 흰색 Foam |
| `reflection_or_blur` | 반사광·흐림 |
| `structural_horizontal_edge` | 구조물 수평 경계 |
| `rapid_oil_flow` | 빠른 오일 유입·배출 |
| `no_interface` | full/empty no-interface |

Exporter schema version 1 does not contain a category or sequence field. The reader
therefore uses only conservative mappings that are authoritative from existing truth
fields: Foam presence, Foam misclassification, glare/reflection, structural edge,
visible interface and full/empty no-interface. It does not silently map an unknown
case to `other`.

Use an optional dataset-root `benchmark_catalog.json` for ambiguous categories,
`transparent_oil_full`, `rapid_oil_flow`, or temporal sequences:

```json
{
  "schema_version": 1,
  "dataset_id": "the-id-from-dataset_manifest.json",
  "fixtures": [
    {
      "fixture_id": "glass-1-0123456789abcdefabcd",
      "category": "rapid_oil_flow",
      "sequence_id": "fill-sequence-01",
      "sequence_order": 0
    }
  ]
}
```

`benchmark_catalog.json` is benchmark metadata. It does not extend or replace the
Phase 2C-3 fixture or `.oiltruth` schemas. Every listed fixture ID and category is
validated. A sequence is executed in canonical timestamp/frame order with one fresh
detector instance; independent cases and different sequences never share tracker
state.

## Collection procedure

1. Keep category balance visible while selecting annotations. Include both successful
   and failed detector cases.
2. Record `confirmed_correct`, `corrected` or `unusable` using the existing truth
   workflow. Do not use the official detector result as implicit truth.
3. For `unusable`, record a specific error type and useful note. These fixtures are
   excluded from accuracy denominators but retained in total and reason counts.
4. For Foam precision/recall, explicitly confirm whether Foam is present. Add a Foam
   front only when an authoritative position is visible.
5. For no-interface cases, use `FULL_NO_INTERFACE` or `EMPTY_NO_INTERFACE` and do not
   fabricate a numeric oil boundary.
6. Add catalog entries when category meaning or sequence membership cannot be derived
   from existing truth fields.
7. Export to an external, user-writable directory. Preserve the dataset bytes used for
   a baseline so future detector runs use the same dataset fingerprint.

## Run the current detector baseline

```text
python -m oil_tracker.cli benchmark \
  --dataset <regression-dataset-directory> \
  --output <output-root>
```

Compare with a previous result from the same dataset fingerprint:

```text
python -m oil_tracker.cli benchmark \
  --dataset <regression-dataset-directory> \
  --output <output-root> \
  --baseline <previous-benchmark-result.json>
```

A malformed dataset, hash mismatch, unsupported schema or non-comparable baseline
returns a non-zero exit code. The command is headless and does not initialize Qt.

## Output

A successful run is atomically finalized only after every file is written:

```text
detector_benchmark_<dataset-id>_<timestamp>/
├─ benchmark_result.json
├─ benchmark_cases.csv
├─ benchmark_categories.csv
├─ benchmark_summary.csv
└─ benchmark_comparison.md
```

The JSON records dataset/run fingerprints, app and detector identity, Python and major
package versions, source revision when available, complete detector settings snapshots,
case results, category summaries, micro aggregate, macro category aggregate, warnings
and comparison deltas. Absolute machine paths and runtime timestamps are excluded from
the fingerprints.

## Metric semantics

- Oil and Foam position errors are reported separately for raw and smoothed outputs.
- Normalized error divides by the effective canonical Glass analysis-region height,
  not the source-frame height.
- A missing detector boundary is a missed detection, never an arbitrary large error.
- Coverage distinguishes truth-present/detected, truth-present/missing,
  truth-absent/absent and truth-absent/false-boundary.
- Fill-state accuracy reports evaluated/correct counts and a confusion matrix.
- Foam precision/recall use only fixtures with authoritative Foam presence.
- Shimmer Foam false-positive rate uses shimmer cases with authoritative Foam absence.
- No-interface false-boundary rates are reported for raw/smoothed values and separately
  for `FULL_NO_INTERFACE` and `EMPTY_NO_INTERFACE` when data exists.
- Every metric records numerator, denominator, evaluated, excluded and unavailable
  counts. Empty denominators are `not_evaluated`, not zero scores.
- Micro aggregate pools usable cases. Macro category aggregate gives equal weight only
  to categories where the metric is evaluated.
- Exporter schema version 1 has no authoritative event truth. Event timestamp metrics
  are explicitly `not_evaluated`; official-versus-rerun event differences are not
  presented as truth accuracy.

Percentiles use deterministic linear interpolation at rank `(n - 1) × q` for median,
P90 and P95.

## Baseline comparison

Comparison requires the same benchmark schema, dataset fingerprint and category
contract. Dataset or schema mismatch is rejected rather than silently compared.
Settings or detector identity may differ and are recorded. Error and false-positive
metrics are lower-is-better; coverage, accuracy, precision and recall are
higher-is-better. S1 introduces no acceptance threshold or automatic tuning.

## Manual follow-up

- Collect and review a balanced real compressor dataset.
- Review annotation quality with a second engineer where practical.
- Exercise Unicode and long Windows paths from the packaged CLI.
- Measure large/long dataset runtime and memory.
- Archive the first accepted current-detector baseline before algorithm changes.

Legacy short redistributable golden clips may still be stored under
`tests/golden/<case>/` with `video.*`, `recipe.oilrecipe`, `annotations.json` and a
source/license README. Real production video or generated benchmark outputs must not
be committed.
