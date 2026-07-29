# Current Work Plan

- **Document status:** `ACTIVE`
- **Active milestone:** `S6 — Real-video and Windows validation gate`
- **Authoritative branch:** `main`
- **S6 task-start main:** `aa27a2d65c29ddcb6c6cf7aa0fe6879d8d228f02`
- **Previous milestone:** `S5-C — Canonical/Qt validation stabilization` — `DONE`
- **Current gate:** define and execute the controlled S6 evidence set without reopening accepted S5-B or S5-C contracts
- **Current blocker:** none
- **Next action:** fix the representative real-video dataset, target Windows environment, long-duration measurement procedure and one-folder clean-PC acceptance sequence
- **S6 execution evidence:** not started

S6 must preserve the merged S5-B typed oil-boundary architecture, observability contract, serialized temporal owner, S5-A Foam independence, external schemas and the S5-C canonical/Qt lifecycle and headless-import boundaries.

## S6 scope

The controlled S6 gate owns:

- representative real-video benchmark and engineering review;
- long-duration CPU, memory and retained-resource observation;
- canonical and manual GUI validation on the target Windows environment;
- one-folder packaging, relocation and clean-PC workflow validation;
- Unicode/long-path, cancellation, close and file-lock cleanup evidence.

S6 does not silently change detector thresholds, Oil/Foam semantics, temporal ownership, validation architecture or external schemas. A source finding requires a separately classified bounded task and cannot be repaired inside validation evidence collection.

## Latest recorded closeout

### S5-C — merged and closed

- **Result:** `DONE`
- **Pull request:** `#57 — test: stabilize canonical Qt validation lifecycle`
- **Accepted PR head:** `77d539c2d5b112460be66db9cfae784be5bee3c1`
- **Exact base:** `a6f0a95c862ebeaeabc25ad140172dfc7b37d3e1`
- **Squash merge / source main:** `aa27a2d65c29ddcb6c6cf7aa0fe6879d8d228f02`
- **Independent decision:** `AUDIT: PASS`
- **Changed scope:** seven test/configuration/documentation files; no production source, detector, schema, threshold or dependency mutation
- **Lifecycle result:** one session pytest-qt `QApplication`, temporary offscreen platform injection and non-mutating post-test visible-widget/global-thread-pool verification
- **Headless result:** source-tree subprocess imports use explicit `PYTHONPATH`, exclude Qt platform state and do not import PySide6 or application bootstrap
- **Coverage ownership:** `python -m pytest` remains the sole canonical suite; `python -m pytest -m qt_app` is a diagnostic selection of the same tests
- **Reused canonical evidence:** `1166 passed in 131.68s`
- **Reused focused Qt evidence:** `161 passed, 1005 deselected`
- **Auditor focused validation:** `27 passed in 14.34s`
- **Order validation:** GUI-before-headless and headless-before-GUI each reported `2 passed`
- **Skips, xfails, retries and conditional acceptance introduced by S5-C:** `0`
- **Diff hygiene:** `git diff --check` passed before merge
- **Reviews and threads:** no review, requested change or unresolved thread; mergeability was clean

The first guarded-merge call rejected a multiline commit message before remote mutation (`merge_attempted=false`, `changed=false`). The same accepted exact head was then merged once through the native exact-base/head guard with a valid single-line message. No source evidence or audit conclusion was invalidated.

### Intentional non-runs at S5-C Close

- representative real-video qualification;
- Windows/manual GUI acceptance;
- packaging and clean-PC execution;
- long-duration CPU/memory qualification;
- S7 annotated MP4 export.

These are S6 or later obligations and were not inferred from macOS canonical/Qt validation.

### S5-B retained contract

S5-B remains `DONE`. Its accepted typed observability and canonical ambiguity contract, one serialized temporal-state owner, one immutable store replacement boundary, non-rejecting projection, S5-A Foam independence and `1.5×` controlled CPU limit remain unchanged by S5-C.

## Open risks and successor boundary

S5-C has no unresolved source, test, merge or synchronization blocker. S6 still needs representative capture evidence for blur, fog, refractive motion, exposure, Glass calibration, long-duration resources, Windows behavior and packaged relocation. Those findings must be evaluated without weakening the accepted S5-B observability/Foam contracts or the S5-C lifecycle/headless boundaries.

The active sequence is:

`S6` → `S7 / Phase 2C-4` → Phase 2D reassessment.
