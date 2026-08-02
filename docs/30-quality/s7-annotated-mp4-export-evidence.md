# S7 / Phase 2C-4 Annotated MP4 Export — Worker Evidence

## Status

`IMPLEMENTATION COMPLETE ON FEATURE BRANCH — AWAITING FRESH EXACT-HEAD AUDIT`

This evidence is source-completing Worker evidence only. It does not mark S7 `DONE`, does not merge the feature branch, and does not replace the required fresh exact-head Auditor gate.

## Identity and scope

- Repository: `teeeeooo/oil_level_tracker`
- Starting authoritative `main`: `3f8b8672509fb14eb047cc0360fcb05c50c9b1d8`
- Worker branch: `feature/s7-annotated-mp4-export`
- Owned slice: selected-Glass annotated MP4 export from Result Review using saved official result state and optional stored debug evidence.
- Official result bundles, source MP4s, Recipes, `.oiltruth`, detector algorithms/thresholds and S5/S6 evidence are not mutated.

## Implemented contract

The general export opens an independent source-video reader, begins at the saved analysis start, decodes sequential source frames only through the saved analysis end, and calls `ReviewQueryModel.overlay_at()` with each actual decoded timestamp. The existing final Result Review renderer therefore owns FillState, confidence, timing, review-state and saved Oil/Foam boundary presentation. Missing numeric values remain missing rather than being interpolated or fabricated.

The optional debug preset renders on top of that same official final-result frame. Candidate evidence is loaded only when a stored debug record matches the selected Glass, exact decoded frame index and timestamp tolerance for that source frame. No-trace frames display an explicit debug-preset no-trace notice and receive no candidate geometry.

Encoding uses the repository's existing OpenCV dependency and adds no FFmpeg or other external executable. Audio preservation is not an S7 acceptance claim.

## Destination and lifecycle contract

- The original source MP4 and official bundle tree are protected destinations.
- Protected bundle destinations are rejected before a missing nested destination directory can be created.
- Existing final output requires explicit UI overwrite confirmation; the exporter itself defaults to no overwrite.
- Encoding writes to a bounded sibling temporary `.mp4`, closes the writer, reopens the temporary video to verify decodability and frame geometry, then atomically publishes with `os.replace`.
- Failure or cooperative cancellation removes the temporary output and does not publish a partial final MP4.
- Source reader, video writer and debug repository resources are closed deterministically.
- A dedicated Qt worker thread owns long encoding work. Result Review close requests cooperative cancellation and refuses to close if the bounded worker shutdown has not completed.
- Export worker generations suppress stale terminal signals while preserving controller reuse when the Result Review window is reopened.

## Automated validation

Narrow exporter suite:

`python -m pytest -q tests/test_review_mp4_exporter.py`

Result: `8 passed` before the final immutability hardening, followed by the combined current-code exporter/controller rerun below.

Current-code exporter/controller rerun:

`python -m pytest -q tests/test_review_mp4_exporter.py tests/test_review_mp4_export_controller.py`

Result: `14 passed`.

Final targeted Result Review suite:

`python -m pytest -q tests/test_review_mp4_exporter.py tests/test_review_mp4_export_controller.py tests/test_review_overlay_renderer.py tests/test_review_debug_overlay_renderer.py tests/test_review_frame_presenter.py tests/test_review_png_exporter.py tests/unit/test_review_query.py tests/unit/test_result_review_playback.py tests/unit/test_result_review_replacement.py tests/gui/test_result_review_window.py tests/gui/test_result_review_debug_viewer.py tests/gui/test_result_review_png_export.py tests/gui/test_result_review_coordinator_factory.py tests/test_ui_import_boundaries.py tests/test_qt_lifecycle.py`

Result: `88 passed` on the final current-code implementation.

The targeted suite covers real OpenCV MP4 generation/reopenability, original geometry and interval frame count, actual decoded timestamp queries, missing-value gaps, exact stored-debug matching, debug absence, destination protection, failure/cancellation cleanup, controller thread lifecycle, Viewer readiness/preset/state preservation, existing PNG behavior, playback/replacement behavior, raster architecture boundaries and Qt lifecycle.

## Bounded MP4 smoke

A local synthetic source-only smoke used a 160x120, 10 fps, 20-frame MP4 and exported the saved 0.2-0.8 second analysis interval.

Observed result:

- reopenable: `true`
- first frame decode: `true`
- output size: `160x120`
- output FPS: `10.000`
- output frames: `7`
- output duration: `0.700 s`
- exporter-reported duration: `0.700 s`
- residual temporary MP4 files: `0`

This smoke validates the derivative encoding path only. It is not detector-accuracy evidence.

## Intentional non-runs and preserved evidence

The S6 detector benchmark, one-hour soak, Windows/manual GUI validation, PyInstaller packaging and unrelated canonical acceptance suites were not rerun. S6 accepted real-video/runtime evidence remains preserved and is not invalidated by this derivative export path. Windows/manual GUI and one-folder packaging remain pending S10 obligations and no PASS is inferred from this macOS/source-tree work.

## Next gate

`S7 / Phase 2C-4 Annotated MP4 Export Fresh Exact-Head Auditor`
