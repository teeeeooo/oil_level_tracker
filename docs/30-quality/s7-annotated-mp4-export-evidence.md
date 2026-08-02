# S7 / Phase 2C-4 Annotated MP4 Export — Worker Evidence

## Status

`IMPLEMENTATION + DECODED-TIMELINE COVERAGE REPAIR COMPLETE ON FEATURE BRANCH — AWAITING FRESH EXACT-HEAD RE-AUDIT`

This evidence is source-completing Worker evidence only. It does not mark S7 `DONE`, does not merge the feature branch, and does not replace the required fresh exact-head repair Re-Auditor gate.

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

## Incomplete-analysis-interval publication repair

The first fresh Auditor identified that both source-last-frame termination and premature sequential `EOFError` could break the decode loop and still validate/publish a partial MP4. The Worker independently reproduced the defect on starting head `90c061f2a03927102636ca2d6ab08792f1e0239f`: a same-resolution 10 fps, 6-frame source with saved interval `0.2–0.8 s` published a 4-frame / 0.4 s output, and the fake sequential EOF path published 3 frames through `0.55 s` for the same saved end.

Publication now requires decoded coverage of the saved analysis end. If sequential decode observes a next source frame after `analysis_end_sec`, that proves the saved end lies between adjacent decoded timestamps. If the source terminates by known last frame or `EOFError` before such a frame appears, the last in-range decoded timestamp must reach the saved end within one nominal source-frame cadence plus bounded timestamp tolerance. Materially shorter source coverage fails before temporary-video validation or atomic replacement.

This stricter rule belongs only to annotated MP4 publication. `SourceVideoResolver.validate_candidate()` still treats same-resolution duration differences as warnings, so shorter replacement videos remain reviewable and the general Result Review replacement-video contract is unchanged.

## Decoded-timeline coverage repair

The second fresh Auditor showed that the first repair still accepted any decoded frame after `analysis_end_sec` as sufficient evidence. The Worker independently reproduced that defect on starting head `3a6dea364ab3c750de68bbc9ec667a1f8d97d885`: for saved `0.2–0.8 s` at nominal 10 fps, decoded timestamps `0.25 → 2.00 s` published a one-frame completed-looking MP4.

Publication now validates the sequential actual decoded timeline across the saved interval. The nominal frame period is `1 / source FPS`; adjacent decoded timestamps that overlap the analysis interval must remain within `1.5×` that period, which provides a bounded 50% timestamp-jitter allowance without treating materially sparse time as covered. The first decoded timestamp must also begin within that cadence bound of the saved start. When a frame after the saved end is observed, the last in-range timestamp and first after-end timestamp must form the same cadence-plausible bracket. Without an after-end frame, EOF/known-last-frame completion remains accepted only when the final in-range timestamp reaches the saved end within that bound. Non-increasing decoded timestamps fail closed.

This accepts ordinary adjacent boundaries such as a saved `0.85 s` end bracketed by normal `0.8/0.9 s` frames and bounded codec/backend timestamp jitter, while rejecting sparse after-end jumps and materially sparse internal decoded gaps. It remains an annotated-export publication rule only; the general replacement-video duration-warning contract is unchanged.

## Destination and lifecycle contract

- The original source MP4 and official bundle tree are protected destinations.
- Protected bundle destinations are rejected before a missing nested destination directory can be created.
- Existing final output requires explicit UI overwrite confirmation; the exporter itself defaults to no overwrite.
- Encoding writes to a bounded sibling temporary `.mp4`, closes the writer, reopens the temporary video to verify decodability and frame geometry, then atomically publishes with `os.replace`.
- Failure, cooperative cancellation or incomplete saved-interval source coverage removes the temporary output and does not publish a partial final MP4; an overwrite-approved existing final remains untouched until successful atomic replacement.
- Source reader, video writer and debug repository resources are closed deterministically.
- A dedicated Qt worker thread owns long encoding work. Result Review close requests cooperative cancellation and refuses to close if the bounded worker shutdown has not completed.
- Export worker generations suppress stale terminal signals while preserving controller reuse when the Result Review window is reopened.

## Automated validation

Narrow exporter suite:

`python -m pytest -q tests/test_review_mp4_exporter.py`

Result: `8 passed` before the final immutability hardening, followed by the combined current-code exporter/controller rerun below.

Initial implementation exporter/controller rerun:

`python -m pytest -q tests/test_review_mp4_exporter.py tests/test_review_mp4_export_controller.py`

Result: `14 passed`.

Initial implementation targeted Result Review suite:

`python -m pytest -q tests/test_review_mp4_exporter.py tests/test_review_mp4_export_controller.py tests/test_review_overlay_renderer.py tests/test_review_debug_overlay_renderer.py tests/test_review_frame_presenter.py tests/test_review_png_exporter.py tests/unit/test_review_query.py tests/unit/test_result_review_playback.py tests/unit/test_result_review_replacement.py tests/gui/test_result_review_window.py tests/gui/test_result_review_debug_viewer.py tests/gui/test_result_review_png_export.py tests/gui/test_result_review_coordinator_factory.py tests/test_ui_import_boundaries.py tests/test_qt_lifecycle.py`

Result: `88 passed` on the initial implementation head before the incomplete-interval repair.

The targeted suite covers real OpenCV MP4 generation/reopenability, original geometry and interval frame count, actual decoded timestamp queries, missing-value gaps, exact stored-debug matching, debug absence, destination protection, failure/cancellation cleanup, controller thread lifecycle, Viewer readiness/preset/state preservation, existing PNG behavior, playback/replacement behavior, raster architecture boundaries and Qt lifecycle.

### Incomplete-interval repair rerun

`python -m pytest -q tests/test_review_mp4_exporter.py`

Result: `13 passed`, including real short-source rejection, premature `EOFError` rejection, known source-last-frame rejection, valid between-frame analysis-end success, overwrite preservation and temporary/resource cleanup.

The full existing Result Review targeted suite was rerun in the repository `.venv` after the repair and returned `93 passed`. The replacement-video coverage remains unchanged: same-resolution duration mismatch is still a warning for review, while MP4 publication alone enforces saved-interval completeness.

### Decoded-timeline repair rerun

`python -m pytest -q tests/test_review_mp4_exporter.py`

Result: `17 passed`, covering sparse after-end rejection, normal adjacent end-bracket acceptance, bounded realistic timestamp jitter, materially sparse internal-gap rejection, and preservation of the earlier premature EOF, known-last-frame, overwrite, temp cleanup and resource-release cases.

The existing S7 Result Review targeted suite was rerun in the repository `.venv` after this second repair and returned `97 passed`.

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

Repair smoke used production `OpenCvVideoReader`/writer behavior. A 10 fps, 6-frame same-resolution source against saved `0.2–0.8 s` failed publication with last decoded timestamp `0.500 s`, left no final and no temp file; a 20-frame source with saved end `0.850 s` succeeded across the normal `0.8/0.9 s` frame boundary as a reopenable 7-frame / 10 fps MP4. Repeating the incomplete case with an overwrite-approved existing destination preserved the previous final bytes and left no temporary file.

Second-repair smoke reproduced the sparse fake decoded timeline `0.25 → 2.00 s` at nominal 10 fps and confirmed rejection with no final and no temporary file. The production OpenCV positive source with saved end `0.850 s` still published a reopenable 7-frame / 10 fps MP4, and the sparse overwrite-approved failure preserved the existing final bytes.

## Intentional non-runs and preserved evidence

The S6 detector benchmark, one-hour soak, Windows/manual GUI validation, PyInstaller packaging and unrelated canonical acceptance suites were not rerun. S6 accepted real-video/runtime evidence remains preserved and is not invalidated by this derivative export path. Windows/manual GUI and one-folder packaging remain pending S10 obligations and no PASS is inferred from this macOS/source-tree work.

## Next gate

`S7 / Phase 2C-4 Annotated MP4 Export Repair Fresh Exact-Head Re-Auditor`
