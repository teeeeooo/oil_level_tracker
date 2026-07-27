# Implementation Decisions

This is a historical baseline decision log, not a project-status document. The [product SSOT](../rotary_oil_level_tracker_ssot_spec.md) remains authoritative, and an active feature architecture overrides an older detector implementation note where they differ. In particular, detector items 8, 11 and 12 describe the pre-cutover baseline; current S5-B authority is the [oil-boundary hypothesis architecture](./s5b-oil-boundary-hypothesis-architecture.md).

1. **Source coordinates are scene coordinates.** `QGraphicsScene` uses original frame pixel coordinates. `QGraphicsView` performs display scaling only, eliminating persistent display/source conversion drift.
2. **Ellipse remains axis-aligned.** Eight resize handles are implemented; rotation is intentionally unsupported per SSOT.
3. **Crop ROI is always derived.** No independent crop rectangle exists in the domain or UI.
4. **Margin uses a proportionally smaller ellipse.** This is deterministic across ellipse sizes and equivalent to an inward elliptical margin for the MVP.
5. **Recipe/session remain separate.** `.oilrecipe` contains no source video path. The session lives only in the active workbench and exported `session.json`.
6. **Single OpenCV distribution in project metadata.** `opencv-python-headless` is the only OpenCV dependency declared. The execution environment happened to contain both OpenCV distributions before this project was created; neither is vendored in the ZIP.
7. **Timestamp sampling is best-effort.** Schedule targets use seconds and `CAP_PROP_POS_MSEC`; actual backend timestamps are stored. Exact-end seeks are clamped to the last nominal frame period.
8. **Detector is evidence fusion, not strongest-edge selection.** Sobel, Canny coverage, Hough segments and region contrast produce candidates; scoring and penalties decide selection. Confidence failure returns no boundary.
9. **Full/empty inference is conservative.** Uniform dark/bright evidence plus prior state can classify out-of-range states. Numeric level remains null in those states.
10. **Foam is topology constrained.** Texture components must intersect the bottom band and exceed minimum area before defining a foam front.
11. **Static artifacts are penalties.** Three schedule locations are sampled and persistent horizontal evidence is accumulated; it is not a hard rejection mask.
12. **Temporal smoothing uses a median window.** State changes use configurable hold frames; short candidate loss does not invent numeric data.
13. **Analysis and export share one worker.** The UI does not block while video processing, CSV, graph, capture or HTML generation runs.
14. **Output is staged.** A unique temporary bundle directory is populated and renamed only after all required artifacts are written.
15. **Offline HTML uses embedded CSS and relative paths.** No CDN or web service is required.
16. **Synthetic sample uses MJPG AVI.** This minimizes codec variability for repository smoke tests; user footage can remain MP4/MKV/AVI/MOV subject to OpenCV backend support.
17. **Python 3.14 support is explicit.** Per the repository owner's 2026-07-20 instruction, project metadata accepts Python `>=3.11,<3.15`; native dependency minimums are raised to PySide6 6.11, NumPy 2.5, OpenCV headless 4.13, matplotlib 3.11 and PyInstaller 6.21 so Python 3.14 installations do not resolve to pre-support releases.
