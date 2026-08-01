# S6-D2 User-Confirmed Product Truth Materialization

## Status

- **Audited feature head:** `f35f2abfc98511cdfaba85ce23374882819b8e30` over base `e261e7b4f4b31c5af89faaac3bfc9ccc35ae1bcc`
- **Merged PR/main:** `#65 @ 1e593364c36a5a30117e86816b1b94cfd52531f5`
- **Accepted result:** `S6-D2 USER-CONFIRMED PRODUCT TRUTH: AUDITED AND ACCEPTED`
- **Review count:** `15` exact D1 frames (`3 / 3 / 4 / 5` by sample)
- **Product truth:** `13 corrected`, `2 unusable`, `0 confirmed_correct`
- **Milestone:** S6 remains `ACTIVE`; S7 remains `PLANNED`
- **Next gate:** `Category-Balanced Official Detector-Accuracy Evidence`

This evidence materializes the user's S6-D1 frame decisions through the existing product truth domain and repository contract. D1 agent candidates are used only where the user explicitly approved them. Official detector snapshots remain comparison provenance and are never promoted to truth authority. Fresh independent exact-head audit and native guarded squash merge are complete; acceptance remains limited to this product-truth artifact.

## Fresh exact-head audit and acceptance

The independent Auditor verified the complete eight-file PR at exact feature head `f35f2abfc98511cdfaba85ce23374882819b8e30` over base `e261e7b4f4b31c5af89faaac3bfc9ccc35ae1bcc`. The PR was same-repository, one-commit and cleanly mergeable, and `main` still matched the exact base before mutation.

The preserved D1 provenance was recomputed independently. The current derivative ZIP is `8aefcf78beac62be7166d9bfd3338a5e3f1c3054990c857159f2c3d6bb7d2c10`; after excluding `.DS_Store`, `__MACOSX` and `._*`, only the user-edited `review-response-template.md` differs from the preserved root. The other `38` review payload members are byte-identical, and all `149` original non-ZIP SHA-manifest entries reproduce exactly. Source videos, Recipes and provisional-truth files retain their frozen S6 identities.

All 15 explicit user decisions were re-derived against the D1 candidate manifest and current product contract. Candidate approvals map to candidate coordinates rather than detector output; sample2 `80% / 0%` reproduces `Oil 592.0 / Foam 320.0`, and S3-02 `20% / 0%` reproduces `Oil 243.0 / Foam 195.0`. The result is `13 corrected + 2 unusable + 0 confirmed_correct`. S3-03 and S3-04 retain no fill state, Oil coordinate, Foam coordinate or `foam_present` after unusable normalization.

Each preserved production bundle reopened through `ResultBundleReader`, and every committed truth file loaded through `JsonTruthRepository` with exact run, Recipe, Recipe-snapshot, Glass, frame and timestamp identity. All stored coordinates reproduced through `coordinate_from_source_y`, and every stored official tracking reference core matched a fresh reference generated from its exact production tracking row.

Fresh focused validation passed `64` tests in `6.22s`. Changed-document Markdown validation checked `37` relative links with no missing target, and `git diff --check` passed on the audited head. No analyzer, detector benchmark, Windows/package validation, long-duration rerun or threshold tuning was performed.

PR #65 was marked Ready and native exact-base/head guarded-squash-merged as `main @ 1e593364c36a5a30117e86816b1b94cfd52531f5`. Acceptance establishes the product-owned, exact-bundle-bound user truth only; it does not establish category-balanced detector accuracy or an accuracy PASS.

## Adjusted D1 provenance contract

The preserved D1 root remains authoritative for `review-candidates.json`, assets, bundles and manifests:

`sample/output/s6-d1-mobile-truth-review-pack/worker-0f0bf70-20260731T151330Z/`

The current `s6-d1-mobile-review-pack.zip` is a user-reviewed derivative, not the original immutable ZIP. Its SHA-256 is `8aefcf78beac62be7166d9bfd3338a5e3f1c3054990c857159f2c3d6bb7d2c10`.

The preserved candidate manifest remains `2dcf7190fd143716045ed6cddc7f2d166fd07d46c7819a84691d477094e67aee`. The original D1 manifest still records the earlier ZIP hash `fd06ce5e464f6a9f0ec3a72d4c0c1be047b715721fb28ce0ef93a76ccb350855`; that difference is intentionally non-blocking under the user-authorized derivative-ZIP contract.
ZIP inspection excluded `.DS_Store`, `__MACOSX` and `._*` metadata. Outside those entries and the intentionally edited `review-response-template.md`, all `38` review payload members are byte-identical to the preserved D1 root. The user response member SHA-256 is `03c952c9d6ea7ade82908a77c9c1218c1c598bcb4d4c3f4605f1073ace32f0f6`. `S3-03` and `S3-04` are both present distinctly, so no duplicate-ID correction is applied.

All `149` original SHA-manifest entries other than the derivative ZIP still reproduce their recorded digest. The tracked source videos, Recipes and four provisional-truth files also reproduce their frozen S6 identities.

## Product truth artifacts

| Product truth | Bound run ID | Annotations | SHA-256 |
|---|---|---:|---|
| `sample/base_sample_1.oiltruth` | `bbf0f0d6-e8b6-4c52-b15b-ff48a402a75e` | 3 | `a4d29b523c9a56ee43f920c9df7e14fb8e957d48fb391ce2ffad7c03e79ebc6a` |
| `sample/sample2.oiltruth` | `1369af1a-9e41-4f85-bfc7-a43d344436c0` | 3 | `f45479f7bb5f4216cb9c6920ac994d2d690942f2ed432d5d8a8647af030c731f` |
| `sample/sample3.oiltruth` | `84119a59-0c4c-445e-8653-913bfcabf579` | 4 | `8cb2b917eede7708894fa90f59f96f1d9eac272813af6d457dcbc292496dd8ab` |
| `sample/sample4.oiltruth` | `c9989828-9bc5-4d03-9885-f1adf25b8dc6` | 5 | `f02575ac2379b4d135567f1835aa772803af13a20413b8aa58175d890f5241bd` |

Each file uses current product truth schema version `1`, one exact `TruthBundleIdentity`, the exact Recipe snapshot hash and exact Glass identity from its preserved D1 production bundle. Files are stored outside result bundles and no `.oiltruth` exists inside the D1 bundle trees.

## User response normalization

`승인` means approval of the D1 agent candidate, not approval of detector output. Physical truth was constructed first from the explicit user response, then compared against the exact official tracking snapshot. `confirmed_correct` is therefore used only if fill state and both boundary coordinates are exactly equal to official output; no reviewed frame met that contract.

The fresh product comparison produces `13 corrected + 2 unusable`. This is derived from the actual bundle snapshots rather than forced to an expected count.
| Review IDs | User truth | Product disposition |
|---|---|---|
| `S1-01–S1-03` | Oil `386.0`, Foam absent, `PARTIAL_VISIBLE` | corrected |
| `S2-01–S2-03` | Oil ruler `80% → 592.0`, Foam ruler `0% → 320.0`, `FOAMING_VISIBLE` | corrected |
| `S3-01` | Oil `316.0`, Foam `286.0`, `FOAMING_VISIBLE` | corrected |
| `S3-02` | Oil ruler `20% → 243.0`, Foam ruler `0% → 195.0`, `FOAMING_VISIBLE` | corrected |
| `S3-03–S3-04` | unusable because of focus loss | unusable |
| `S4-01` | Oil `860.5`, Foam `850.0`, `FOAMING_VISIBLE` | corrected |
| `S4-02` | Oil `852.5`, Foam `845.0`, `FOAMING_VISIBLE` | corrected |
| `S4-03` | Oil `848.5`, Foam `840.0`, `FOAMING_VISIBLE` | corrected |
| `S4-04` | Oil `855.0`, Foam `824.0`, `FOAMING_VISIBLE` | corrected |
| `S4-05` | Oil `858.5`, Foam `810.0`, `FOAMING_VISIBLE` | corrected |

The ruler conversion was freshly reproduced from the D1 builder formula `ellipse_top + 2 * radius_y * percent / 100`: sample2 ellipse top `320.0`, radius `170.0`; sample3 ellipse top `195.0`, radius `120.0`. The S3-02 user note about the perceived physical Glass span is preserved in the annotation note; Recipe ROI/Glass geometry is not changed.

For `S3-03` and `S3-04`, the note preserves that the candidate Oil line looked physically plausible while focus loss made the frame unusable. Product normalization removes fill state, Oil coordinate, Foam coordinate and `foam_present`; neither frame is revived as numeric accuracy truth.

## Official comparison and error semantics

Official snapshots for the usable frames differ from the user-confirmed physical truth. Sample1 and the two usable sample3 frames publish `UNKNOWN_REVIEW` with no Oil boundary. Sample2 publishes missing Oil and either missing or different Foam; S2-03 is `FULL_WITH_FOAM`. Sample4 publishes `FULL_WITH_FOAM`, no Oil boundary and Foam coordinates different from the approved candidate coordinates.

Error-type totals are: `fill_state_misclassified=13`, `oil_boundary_missing=13`, `foam_misclassified=3`, `glare_or_reflection=3`, `wrong_candidate=7`, `video_unusable=2`. Sample1 overlay meaning has no dedicated enum and is preserved losslessly in notes rather than inventing a new schema value.
## Validation

All four bundle roots reopen with production `ResultBundleReader`. All four truth files load through `JsonTruthRepository` with exact expected identity and full bundle validation. Counts are exactly `3 / 3 / 4 / 5`, all 15 annotation keys are unique, and every stored coordinate reproduces exactly through `coordinate_from_source_y`.

Corrected annotations have a non-`UNKNOWN_REVIEW` truth state and at least one error type. Unusable normalization removes numeric truth. JSON serialization rejects NaN/Infinity and the committed payloads reproduce product `to_dict()` serialization exactly.

Targeted existing suite:

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/test_user_truth_domain.py \
  tests/test_json_truth_repository.py \
  tests/test_truth_export_controller.py \
  tests/unit/test_result_bundle_reader.py \
  tests/unit/test_source_video_resolver.py
```

Result: `64 passed in 6.97s`.

Changed-document Markdown validation passed with `37` relative links checked and no missing target. `git diff --check` also passed. No analyzer, detector benchmark, Windows/package validation or new accuracy run is part of this materialization.

## Remaining scope and next gate

This 15-frame truth set is intentionally not category-balanced official accuracy evidence. Remaining sample gaps include scratch, fogging/stain, clean rim-adjacent Oil boundary, high-quality field fill/drain, clean full/empty no-interface and broader independent field-video coverage.

Detector source/settings, tests, dependencies, Recipes, original MP4s and provisional truth remained unchanged by the S6-D2 artifact work and audit. No detector accuracy PASS is claimed. S6 remains `ACTIVE`; S7 remains `PLANNED`.

The exact next gate is **`Category-Balanced Official Detector-Accuracy Evidence`**. This Close records that gate without starting a benchmark, detector repair or threshold-tuning task.
