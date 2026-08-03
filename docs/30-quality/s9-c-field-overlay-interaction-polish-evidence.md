# S9-C Field ↔ Overlay Interaction Polish Evidence

## Scope

This is bounded Lane B implementation evidence for S9-C on branch `feature/s9-c-field-overlay-interaction-polish` from exact base `9b2f4b79a1f24fb379b256bef66554dca56af915`.

S9-C changes Workbench presentation/interaction state only. It does not change Recipe geometry schema, `.oilrecipe` persistence, `AnalysisSession`, Result Bundle, detector state, readiness validity, workflow authority or architecture ownership.

## Interaction-state ownership

`MainWindow` owns one transient active target consisting of the selected Glass id, target kind and optional exact exclusion-zone id. `GlassSettingsPanel` and `VideoOverlayCanvas` request and render that state; neither makes highlight state persistent.

Field → Overlay mappings are:

- center X/Y, width, height and geometry context → selected ellipse;
- zero-line field → zero line;
- margin field → inner detection margin;
- exclusion-list selection → exact exclusion rectangle by zone id.

Overlay → Field mappings are:

- ellipse move/resize/click → geometry group;
- zero-line interaction → zero-line field;
- exclusion interaction → exact exclusion list entry/group.

## Lifetime and coexistence

The selected Glass and active edit target are deliberately separate. Overlay interaction can make a zero line or exclusion the stronger active affordance while the selected ellipse remains selected and retains geometry handles.

Same-Glass `set_glass()` / `set_glasses()` rebuilds rebind the active target. Selecting another Glass, loading/newing a Profile, or removing the exact active exclusion clears stale target state.

Validation styling remains independently owned by the existing `validationState` property. S9-C adds an independent `interactionTarget` property, so error/warning borders, first-issue routing and active-edit context can coexist on the same field.

Highlight application does not call Recipe/session mutation, dirty marking, undo commands, validation or detector paths. Canvas target styling is updated in place, so S9-B manual zoom/pan/Fit state is not reset by highlight changes or target rebind.

## Ellipse visual polish

The selected ellipse retains eight axis-aligned resize directions and existing minimum-size/frame-bound/source-coordinate behavior. Each handle keeps an 18 px transform-independent practical hit area while rendering a restrained 6 px circular marker. Hover/geometry context strengthens markers and an active resize handle grows to a stronger marker.

Shared `VideoOverlayCanvas` consumers remain opt-in: consumers that never provide an S9-C active target continue using ordinary overlay display. ROI editor private-copy Apply/Cancel semantics and video-preview context/zoom semantics are covered by regression tests.

## Development validation

Focused development checks completed on the unmerged feature tree:

- `python -m py_compile` for the three changed UI modules and S9-C test modules: pass.
- `pytest -q tests/gui/test_field_overlay_interaction.py tests/gui/test_overlay_editor.py --maxfail=1`: `20 passed` after final pointer no-op guard stabilization.
- ROI editor private-copy, shared video-preview zoom/open behavior and UI import-boundary regression selection: `12 passed`.

## Final targeted suite

Fresh after source-completing documentation alignment:

`python -m pytest -q tests/gui/test_field_overlay_interaction.py tests/gui/test_overlay_editor.py tests/gui/test_guided_workbench_ux.py::test_advanced_settings_are_hidden_until_requested tests/gui/test_guided_workbench_ux.py::test_inline_validation_marks_related_field tests/gui/test_guided_workbench_ux.py::test_roi_editor_uses_private_copy_until_applied tests/test_ui_import_boundaries.py --maxfail=1`

Result: `33 passed`. This suite covers S9-C mappings/state lifetime and no-op pointer clicks, overlay geometry/handle behavior, S9-B view-state compatibility, validation styling and first-issue routing, ROI editor, shared preview behavior and UI import boundaries.

## Deferred/manual evidence

Windows GUI/DPI execution, PyInstaller packaging, detector benchmarks, long-duration/soak validation, unrelated canonical/E2E validation and autosave/recovery are intentionally outside this Worker run. The S9-C Windows/DPI obligations are recorded in [manual GUI and Windows acceptance](./manual-gui-windows-checklist.md).

No materially broader persisted/public/runtime/workflow or architecture boundary was discovered. Lane B remains appropriate for this unmerged change; merge-dependent status reconciliation belongs to the S9-C Lane B Orchestrator Exact-Head Gate.
