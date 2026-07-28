# Current Work Plan

- **Document status:** `VALIDATING`
- **Active milestone:** `S5-B — Oil-boundary hypothesis architecture`
- **Branch:** `feature/oil-boundary-temporal-tracking`
- **Task-start exact head:** `9dc6ff28da3524ef83ca7422218c98b9f4666763`
- **Task-start exact parent:** `5f8749e8c1a508646d04026b2f1135db1b5be369`
- **Architecture re-audit:** `AUDIT: PASS`
- **Current gate:** Independent transactional production trust-boundary source exact-head audit
- **Source implementation:** Completed on the feature head; pending independent audit
- **Controlled comparison:** Blocked until source exact-head audit `PASS`

This is the operational SSOT for the active milestone. Closeout follows the [documentation closeout policy](./closeout-policy.md). The source implementation is not formal completion, and this plan makes no `DONE` or S5-B completion claim.

## Current state

The bounded transactional source implementation is complete on the feature head:

- current observations are closed concrete boundary, positive no-interface, ambiguous and successful evidence-unavailable variants with derived classification;
- successful temporal decisions are closed accepted-boundary, no-interface, ambiguous, successful evidence-unavailable and reacquisition-pending variants with derived tracker and smoothing actions;
- successful raw/evidence frames and failed pipeline frames are structurally separate;
- canonical production outcomes are closed accepted-boundary, no-interface, ambiguous, successful evidence-unavailable, reacquisition-pending and pipeline-failure variants;
- only accepted-boundary outcomes own numeric oil Y and a selected canonical hypothesis;
- Phase A reconstructs and validates a fresh canonical evidence graph before temporal evaluation;
- Glass-local hypothesis state is an immutable bounded value and snapshot lookup does not create a live state entry;
- temporal evaluation is pure/provisional and returns a proposed decision, next state and resource metrics without live mutation;
- Phase B validates decision/current compatibility, canonical identity/content/provenance/Y coherence, actions, state identity/version, counters, beam/history and resource bounds;
- the complete canonical outcome and immutable commit payload are prepared and validated before commit;
- one transactional owner performs versioned compare-and-swap replacement exactly once while rejecting stale or replayed proposals;
- commit failure, Phase A/B failure, temporal evaluation failure and outcome preparation failure return a fresh `PipelineFailureOutcome` without hypothesis-state commit;
- repeated pipeline failure no longer progresses the successful-unavailable counter or clears compatibility smoothing;
- production consumers read only the committed canonical outcome; raw frames, current observations, provisional decisions and proposed states are not downstream authorities;
- compatibility smoothing consumes canonical `ACCEPT_BOUNDARY` / `NO_UPDATE` and `PRESERVE` / `CLEAR_BEFORE_ACCEPT` / `CLEAR_STALE_AFTER_STABLE_ABSENCE` actions directly;
- S5-A Foam evaluation remains independent when the oil pipeline fails.

## Compatibility and bounded scope

The implementation preserves:

- external `PhaseDetection` field shape;
- Recipe/settings and persistence schemas;
- benchmark, truth, fixture, result, CSV and debug schema versions;
- detector version `opencv-phase-detector-s5b-typed-production-v1`;
- observation extraction, proposal/hypothesis algorithms, likelihood formulas and thresholds;
- accepted successful temporal transition policy;
- configured observation, proposal, hypothesis, beam/history, counter, static-scalar and debug-scalar bounds;
- S5-A Foam ownership and processing;
- input raster and retained debug-image isolation;
- dependency and workflow files.

No legacy oil generation, scoring, no-interface or temporal path is used as a production fallback. The legacy modules remain outside the production call graph and are unchanged.

## Validation evidence

Executed with the project `.venv` Python `3.14.4`:

- focused transactional/consumer suite:
  - command: `PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_oil_shadow_observations.py tests/test_oil_shadow_temporal.py tests/test_oil_shadow_evidence.py tests/test_oil_transactional_boundary.py tests/test_oil_production_cutover.py tests/test_oil_detector_integration.py tests/test_oil_fill_state_classifier.py tests/test_oil_temporal_tracker.py tests/test_foam_fill_state_policy.py`;
  - result: `85 passed in 5.89s`;
- monolithic full repository attempt:
  - command: `PYTHONPATH=src .venv/bin/python -m pytest -q`;
  - result: the run reached `84%`, exposed only the two pre-recorded controlled-accuracy failures, and then aborted in unrelated `pytest-qt` / PySide6 native event processing with `Fatal Python error: Segmentation fault` after `60.53s`;
  - the crash also reproduced in isolated Qt execution under the repository's default `offscreen` platform and is not counted as a completed full-suite result;
- complete segmented repository coverage after the native Qt crash:
  - collection: `PYTHONPATH=src .venv/bin/python -m pytest --collect-only -q` -> `769 tests collected in 4.53s`;
  - non-Qt command: the full repository command with the 40 Qt-importing files generated by `rg -l 'qtbot|PySide6|QApplication|QWidget|QMainWindow|QSignalSpy' tests --glob '*.py'` passed as `547 passed, 2 failed in 33.72s`;
  - Qt command: each of those 40 files was executed in an independent process with `QT_QPA_PLATFORM=minimal QT_STYLE_OVERRIDE=Fusion PYTHONPATH=src .venv/bin/python -m pytest -q <file>`;
  - Qt result: `220 passed`, `0 failed`, and one helper module collected no tests; the four batches completed in `35s`, `51s`, `36s`, and `30s`;
  - combined result across all `769` collected nodes: `767 passed, 2 failed`; the two failures are exactly the pre-recorded deferred controlled-accuracy findings below;
- syntax/import compilation:
  - command: `PYTHONPATH=src .venv/bin/python -m compileall -q src tests`;
  - result: passed in `0.36s`;
- whitespace/error check:
  - command: `git diff --check`;
  - result: passed with no output.

The repository defines no separate lint or type-check command. No new validation tool or dependency was installed.

## Deferred controlled accuracy findings

The two controlled accuracy findings remain deferred and unchanged:

- clear-oil raw detection coverage is `0.5714285714285714`, below the expected `1.0`;
- `no-interface-to-visible` frame 3 still has no numeric raw oil recovery.

They remain detector-accuracy findings for the later controlled-comparison gate. This source implementation neither relaxes their expectations nor changes the detector algorithms or thresholds to address them.

## Remaining risks

Independent source audit must examine:

- whether the versioned immutable replacement is a sufficient atomic commit primitive under all same-Glass concurrency and injected-failure paths;
- whether per-Glass serialization and version checks preserve deterministic ordering without avoidable throughput regression;
- whether any debug consumer outside the directly tested owners assumes the former generic mutable result shape;
- whether canonical reconstruction and outcome validation add material CPU cost under controlled instrumentation;
- whether source identity/provenance validation is complete for every supported raw evidence family;
- the two deferred controlled-accuracy findings above.

Controlled base/feature comparison, canonical real-video validation, Windows/manual validation, packaging, merge and cleanup were not performed and remain unauthorized before the independent source audit passes.

## Required downstream sequence

1. Independent transactional production trust-boundary exact-head source audit.
2. Controlled base/feature comparison only after source audit `PASS`.
3. Canonical validation and later Windows/manual, packaging and merge gates only under their separate authority.

## Latest recorded closeout

- **Result:** Transactional production trust-boundary source implementation completed on the feature head; pending independent audit.
- **Task-start exact head:** `9dc6ff28da3524ef83ca7422218c98b9f4666763`.
- **Task-start exact parent:** `5f8749e8c1a508646d04026b2f1135db1b5be369`.
- **Architecture re-audit:** `AUDIT: PASS`.
- **Implemented boundary:** Closed observations, decisions, frames and outcomes; Phase A/provisional/Phase B/prepare/commit/publish ordering; exactly-once all-or-nothing Glass-local commit; canonical consumer cutover.
- **Failure behavior:** Fresh pipeline failure with hypothesis no-commit, compatibility `NO_UPDATE` and smoothing `PRESERVE`; repeated failures do not progress successful-unavailable state.
- **Validation:** Focused suite `85 passed`; monolithic full run blocked by unrelated PySide6 native crash; segmented coverage accounted for all `769` collected nodes as `767 passed, 2 deferred controlled-accuracy failures`; compileall and diff checks passed.
- **Compatibility:** External shapes/schema versions, detector version, dependencies, thresholds and S5-A Foam ownership remain unchanged.
- **Current gate:** Independent transactional production trust-boundary source exact-head audit.
- **Controlled comparison:** Blocked until source exact-head audit `PASS`.
- **Deferred findings:** The two controlled oil accuracy findings remain unchanged.
- **Resulting exact SHA:** Reported by the Worker final report, not self-recorded in this commit.
