# Implementation Gaps and Constraints

The delivered project is a coherent executable MVP vertical slice. The following items require follow-up rather than being represented as complete:

1. **Real test-video calibration is not complete.** Candidate weights, intensity heuristics, foam thresholds and state-transition priors were verified with synthetic fixtures only. Real compressor sight-glass videos and manual annotations are required before production judgment use.
2. **Golden video regression contains structure/documentation but no proprietary real footage.** No actual test video was supplied. Synthetic video regression is included.
3. **Clean Windows validation was not possible in this Linux execution environment.** The one-folder spec parsed and PyInstaller dependency analysis started, but the Linux build exceeded the execution timeout and no distributable was claimed. The SSOT acceptance criterion “Python-uninstalled clean Windows PC” still requires a Windows build/test run.
4. **Python 3.14 runtime verification remains local.** Project metadata now supports Python 3.11–3.14 and pins native dependencies to releases that publish Python 3.14-compatible wheels. The implementation was originally exercised with Python 3.13.5; the owner should run the complete suite and PyInstaller smoke test on the target Windows CPython 3.14.3 machine before release.
5. **OpenCV VFR seek is approximate.** Actual decoded timestamps are recorded, but frame-accurate VFR indexing would require a timestamp-indexed backend such as FFmpeg/PyAV, outside the mandated dependency set.
6. **Interactive single-frame seek decode uses the GUI thread.** Full analysis, preview detection and export are background tasks. A pathological codec/keyframe seek can still briefly stall playback/seek; a dedicated decode thread is a follow-up hardening task.
7. **Result review is report-first.** The toolbar opens the generated offline HTML report. A fully embedded interactive Qt review screen is not implemented.
8. **Debug profiles are image/table based.** Required tabs, masks, candidates, state and export are implemented, but Sobel/texture row profiles are shown through debug images/metrics rather than interactive plots.
9. **Manual geometry acceptance remains necessary.** Automated GUI tests cover creation, binding and routing. Pixel-perfect drag/resize/overlay behavior must be verified on Windows DPI configurations using the checklist.
10. **Event capture volume is not curated.** A representative image is exported for each event; production use may need event deduplication and capture-selection limits.
11. **Cancellation discards incomplete bundles.** It does not publish a `FAILED` manifest because the staged temporary directory is removed, one of the SSOT-permitted failure policies.
12. **Detector heuristics remain configurable rather than empirically qualified.** Conservative transition gates and foam-shape filters reduce obvious artifacts, but their operational thresholds need validation against the actual camera, glass geometry, lighting and oil/foam appearance.
