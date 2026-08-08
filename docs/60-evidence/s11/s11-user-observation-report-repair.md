# S11-R1 User Observation Report Comprehension Repair

Date: 2026-08-09

Detector/result baseline: `e27b2cca93bf261c6d56528f21f5d260cd40b37d`

Status: `ACCEPTED — source-tree report repair complete; final target-Windows field-workflow validation remains open`

## Objective

Make the finalized report explain what the sight glass appeared to do over time rather than foregrounding detector-debug volume. The accepted S11 detector, canonical numeric Oil publication, serialized temporal owner and fail-closed missing values had to remain unchanged.

The implemented contract is the [`Result Observation Report Architecture`](../../20-architecture/result-observation-report-architecture.md); acceptance criteria are in the [`Result Observation Report Validation Contract`](../../30-validation/result-observation-report-validation.md). The causal reconstruction and pre-change bundle inspection are recorded in the [`S11 User Report Observability Diagnostic`](../../50-diagnostics/s11/s11-user-report-observability-diagnostic.md).

## Implemented result

- Added one application-owned report presentation model derived only from stored TrackingSamples, domain events and Recipe geometry.
- Split the Oil path into solid consecutive-observation runs and dashed endpoint-only bridges across missing runs. No missing timestamp receives a numeric value.
- Added deterministic observed highest/lowest Oil landmarks and plain-language movement summaries.
- Consolidated stored Foam observations into at most three report-only episodes, ignoring single-sample flicker and claiming disappearance only at a later non-Foam observation.
- Replaced all-event capture expansion with at most twelve selected physical landmarks per Glass.
- Generated source-video captures cropped around the configured Glass with ellipse, zero, stored Oil and stored Foam guides.
- Reorganized `report.html` around the overall graph, per-Glass observation summary, annotated detail graph and inline key-moment captures. Raw tracking/events and detector debug remain separate audit surfaces.
- Centralized Korean event labels and extended the event vocabulary with `MAXIMUM_OIL_LEVEL` without changing existing event columns or meanings.

## Four-video production replay

The reproducible runner is `tests/diagnostics/s11_report_observability_replay.py`. It uses the production `AnalysisPipeline`, `OpenCvPhaseDetector`, static-artifact learning, serialized owner, matching Recipes and the accepted 2 FPS qualification windows. Run-only initial state is explicitly confirmed as `UNKNOWN_REVIEW`, so retrospective FULL/EMPTY cannot create report observations.

```text
PYTHONPATH=src .venv/bin/python -m tests.diagnostics.s11_report_observability_replay
```

| Sample | Window | Tracking rows | Numeric Oil | Report landmarks | Capture files | Foam episodes |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `base_sample_1` | `0.0–14.4 s` | 30 | 3 | 5 | 5 | 1 |
| `sample2` | `0.0–2.0 s` | 5 | 2 | 4 | 3 | 1 |
| `sample3` | `30.03–105.0 s` | 151 | 42 | 11 | 10 | 3 |
| `sample4` | `0.0–56.0 s` | 113 | 62 | 9 | 9 | 2 |
| **Total** |  | **299** | **109** | **29** | **27** | **7** |

Two landmarks may share one capture when they occur on the same Glass/timestamp. This accounts for the 29-landmark/27-file difference.

The pre-change inspected bundles created one capture per event: `13`, `11`, `73` and `60` files respectively. The repaired report therefore reduces sample3 from 73 equal-weight captures to 10 selected source moments and sample4 from 60 to 9, while leaving complete event rows in `events.csv`.

Generated replay bundles and `sample/output/s11-report-r1/replay_manifest.json` are ignored local evidence, not Git truth or golden fixtures.

## Exact detector/tracking preservation

The same four windows were also executed from a separate archive of exact baseline `e27b2cca`. The current replay matched baseline row count, numeric Oil count and a canonical fingerprint over timestamp, frame, fill state, raw/smoothed Oil, raw/smoothed Foam, validity and flags for every TrackingSample:

| Sample | Baseline/current fingerprint |
| --- | --- |
| `base_sample_1` | `87166f357d7c962fb16a9a27a4def3329b587e27a74efd0671dce981046f3654` |
| `sample2` | `912225deb00b1a33504d7541be9a61727049a2a845c29ebd8b7badd7197f06aa` |
| `sample3` | `544744f950861af265ae07554aedf998e9f0959a8d16052b7416faa656df0cfb` |
| `sample4` | `372abf6e2e64580c06bbae63901ea471254594ed8c31e525c23228f22574d16e` |

The replay runner asserts these fingerprints as well as the accepted `30/5/151/113` row and `3/2/42/62` numeric-Oil counts. This proves the report repair does not alter detector/history output on the available corpus.

## Visual and structural inspection

All four generated detail graphs were inspected at source resolution.

- Direct consecutive Oil observations are solid blue runs with visible stored anchors.
- Every edge crossing missing samples is a lower-emphasis dashed blue bridge; long sample3 gaps remain visibly distinct from direct observation.
- There is no extrapolated line before the first or after the last finite anchor.
- Highest/lowest Oil are labeled at their stored source times.
- Selected Foam/physical transitions are labeled without restoring the former all-event line volume.
- Restrained gray unavailable-state bands remain visible behind, rather than dominating, the movement path.

Representative highest, lowest, Foam-start and Foam-end captures were inspected from every ROI scale, including the small sample4 Glass. The crop centers the configured Glass; very small crops are display-upscaled for legibility; ellipse/zero guides remain registered; Oil/Foam guides appear only when the selected stored sample has the corresponding value. Foam-end captures correctly omit a Foam guide when disappearance is the selected evidence.

Each generated HTML report was parsed offline. All relative graph/capture links resolved, each report contained both extrema, and neither the `LOW_CONFIDENCE_START` debug enum nor the raw English valid-coverage percentage judgment appeared in main content. The latter is replaced by plain-language Korean judgment guidance while exact audit data remains outside the narrative. Target-browser/DPI and print-layout confirmation remains part of the final Windows checklist and is not claimed by this source-tree inspection.

## Automated validation

Focused report, graph, capture, HTML, bundle-lifecycle and Result Review validation:

```text
44 passed in 5.15 s
```

Complete repository run:

```text
1434 passed, 7 failed in 89.21 s
```

The seven failures are not introduced by S11-R1. The exact same seven tests fail from the separately extracted `e27b2cca` baseline on this environment: one initial-state readiness expectation, four detector/Foam fixture expectations, one stale S11 truth-count expectation and the existing test-authoring policy finding for two baseline files. All S11-R1 focused tests pass, and the four report-adapter test-double regressions found during implementation were repaired.

## Decision and claim boundary

S11-R1 is accepted as a downstream report-comprehension repair. It materially improves the user's ability to read observed movement and inspect important source moments without increasing detector publication coverage or inventing a trajectory.

This does not establish general-field detector/Foam accuracy, validate the seven pre-existing baseline failures, or close S11. The exact next gate is final target-Windows field-workflow validation using the updated manual checklist, including offline report assets, Korean fonts, DPI/layout, solid/dashed semantics and Glass-focused landmark captures.
