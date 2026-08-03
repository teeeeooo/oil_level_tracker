# S9-B Workbench Analysis-Area Zoom, Pan & Fit — Worker Evidence

**Status:** `IMPLEMENTATION COMPLETE — AWAITING LANE B ORCHESTRATOR EXACT-HEAD GATE`

- Starting exact `main`: `80b65298b1ac7948cd3d6c54fa77396afb9d7857`
- Worker branch: `feature/s9-b-workbench-zoom-pan-fit`
- Lane: `B — Bounded Change`
- Next gate: `S9-B Lane B Orchestrator Exact-Head Gate`

## View-state ownership

Zoom and pan remain presentation-only state owned by `VideoOverlayCanvas`. They are not serialized into `InspectionRecipe`, `AnalysisSession`, `.oilrecipe` or result bundles and do not participate in Profile dirty truth or the Workbench undo stack. `QGraphicsScene` remains the canonical source-frame coordinate space; the view transform only changes how that scene is presented.

The Workbench `VideoPlaybackPanel` exposes explicit `확대`, `축소`, `맞춤` and `100%` controls. `Ctrl`+wheel provides equivalent canvas zoom and middle-button drag provides pan, leaving existing left-button ellipse, resize-handle, zero-line and exclusion editing gestures unchanged.

## Transform lifetime

A new canvas starts in Fit mode. Explicit Fit resets the view to the complete frame with aspect ratio preserved, and Fit mode refits on viewport resize. Manual zoom, pan and 100% switch to manual mode; ordinary frame/timestamp refresh and viewport resize then preserve the user's scale rather than silently returning to Fit.

Actual context replacement explicitly requests a Fit reset. This is wired for normal video replacement, wizard/new-video entry, placeholder/new/load transitions and same-Profile new-video commit. The shared wizard/video preview similarly resets on opening a new video while preserving manual transform across frames from the same video.

## Geometry and shared consumers

Ellipse move/eight-direction resize, minimum size, frame bounds, zero-line bounds, exclusion geometry and Glass selection retain their existing scene-coordinate authority. Automated coverage verifies scene/view round-trip under manual transform and that view-only actions do not mutate Recipe state.

The ROI editor continues to use its private Glass copy until Apply/acceptance. The preview consumer continues to display frames with the same shared canvas without inheriting stale transform across a new video context. No new shared workflow or persistence authority was introduced.

## Worker validation

Development coverage first stabilized the canvas behavior and then the Workbench/context seams. The final fresh Lane B targeted suite was:

`QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q tests/gui/test_overlay_editor.py tests/gui/test_workbench_usability_stabilization.py::test_workbench_layout_places_summary_left_and_separates_canvas_transport tests/gui/test_workbench_usability_stabilization.py::test_workbench_view_controls_are_ephemeral_and_explicit tests/gui/test_workbench_usability_stabilization.py::test_video_context_reset_and_same_context_frame_preserve_view_semantics tests/gui/test_workbench_usability_stabilization.py::test_wheel_safe_controls_do_not_change_values_and_keep_keyboard_editing tests/gui/test_same_profile_analysis_coordinator.py tests/gui/test_guided_workbench_ux.py::test_roi_editor_uses_private_copy_until_applied tests/gui/test_gui_smoke.py::test_wizard_has_preview_time_pickers_and_skip tests/test_ui_import_boundaries.py`

Result: `29 passed in 4.52s`.

This covers Fit/zoom/pan and viewport lifetime, same-context frame preservation, normal and same-Profile context reset, view-only Recipe/session/dirty/undo behavior, settings-panel wheel safety, ROI editor private-copy semantics, wizard/video preview compatibility and UI import boundaries.

Two development aggregation runs were intentionally terminated after pytest-qt teardown reached the existing unsaved-Profile close modal on dirty MainWindow cases. The failing assertions discovered before that teardown were isolated: one test incorrectly called `to_dict()` on a Glass object and was corrected to compare the owning Recipe snapshot; one Workbench layout test exposed the added control row exceeding the previous 340 px canvas minimum, so the Workbench-specific minimum was reduced to the already-required 300 px usability floor. Both corrected boundaries pass in the final targeted suite.

Detector benchmarks, soak/long-duration workloads, Windows/manual GUI execution, Windows DPI execution, PyInstaller and unrelated canonical/E2E suites were intentionally not run. The new Windows/DPI obligations are recorded in the manual checklist for the later S10 release gate.
