# Manual GUI and Windows Acceptance Checklist

This document owns manual GUI, real-video, Windows and packaging obligations. It does not own milestone status; use the [roadmap](../00-project/roadmap.md) and [current work plan](../00-project/work-plan.md).

## Workbench and video
- Launch the packaged app on a 100%, 125%, and 150% Windows display scale.
- At 1280 px window width, verify all five Workbench progress steps remain identifiable on one line without overlap or clipping.
- On a small laptop display, verify the center video remains large enough to edit the selected Glass.
- Verify the video canvas and transport bar have a clear boundary and never overlap during resize.
- Open MP4, MKV, AVI and MOV samples supported by the deployed OpenCV backend.
- Verify play/pause, step, seek and 0.5×/1×/1.5×/2×/4× behavior.
- Verify start/end/compressor markers numerically through session fields and report.
- Verify Korean labels do not clip or wrap awkwardly at 100%, 125%, and 150% display scale.

## Glass and analysis region editor
- Add three Glass items and alternate selection.
- Confirm the current-scene detection summary remains readable above the Glass list without hiding its add/delete/copy actions.
- Open **분석 영역 편집** and drag the ellipse from center; confirm it cannot leave the frame.
- Resize with left/right/top/bottom/corner handles; confirm minimum size and no inverted geometry.
- Drag the zero line to top/bottom and confirm it remains inside the ellipse.
- Add, move, resize and delete multiple exclusion rectangles.
- Verify stored `.oilrecipe` coordinates match source pixels after window resizing.
- Scroll the settings panel while the pointer is over spin boxes and combo boxes; confirm values do not change and the panel continues scrolling.
- Verify keyboard arrows, direct entry and arrow buttons still edit wheel-safe controls.
- Toggle **실제 길이 환산 — 선택 사항** off/on and confirm px-only operation, valid mm display and saved `None` behavior.
- Confirm Foam guidance separates detection interpretation and recommended action.
- Use **초기 상태 설정으로 이동** and confirm the selected Glass remains selected, the initial-state field receives focus and the Recipe is not changed automatically.

## S9-B Workbench zoom, pan and fit
- At 100%, 125% and 150% Windows display scale, open a small sight-glass scene and confirm **확대**, **축소**, **맞춤** and **100%** remain visible without reducing the canvas below a usable editing area.
- Confirm the initial Workbench frame and every actual video/Profile context replacement enter Fit mode with the complete source frame visible at the correct aspect ratio.
- Use **확대**/**축소** and `Ctrl`+wheel on the canvas; confirm scale changes smoothly while ellipse, zero-line and exclusion overlays remain registered to the same source-frame coordinates.
- In a zoomed view, drag with the middle mouse button to pan and confirm ordinary left-button ellipse move/resize, zero-line drag and exclusion move/resize remain unambiguous.
- Seek, step and play through multiple frames while manually zoomed/panned; confirm the same-context view transform is retained rather than returning to Fit on every frame.
- Resize the Workbench while Fit is active and confirm the frame refits to the viewport. Repeat while manually zoomed and confirm the manual scale is preserved instead of collapsing back to Fit.
- Replace the current test video, load/new a Profile, and enter the same-Profile new-video workflow; confirm the old context transform is discarded and the replacement starts in Fit.
- At high zoom, edit all eight ellipse resize directions plus ellipse position, zero line and exclusion geometry; save/reload and confirm persisted coordinates still match source pixels with existing minimum-size and frame-bound rules.
- Exercise zoom/pan/fit without editing geometry and confirm Profile dirty state, undo/redo availability, Analysis Session values, readiness/preflight state and saved Result data do not change.
- Scroll the settings panel over spin/combo controls after using canvas zoom shortcuts and confirm its wheel-safe behavior still prevents accidental value changes.
- Open **분석 영역 편집** and the wizard/video preview consumers and confirm their frame display and existing private-copy/apply/cancel behavior remain intact.

## S9-C field ↔ overlay interaction polish
- At 100%, 125% and 150% Windows display scale, focus center X/Y, width and height controls; confirm the selected ellipse is clearly the active geometry target while the selected Glass identity remains visible.
- Focus the zero-line and margin controls; confirm only the corresponding zero line or inner detection margin receives the stronger active affordance and the ellipse remains the selected Glass geometry.
- Add at least two exclusion zones, select each list entry in turn and confirm the exact matching rectangle is highlighted with no cross-zone ambiguity.
- Click/drag/resize the ellipse, zero line and each exclusion overlay; confirm the settings panel reveals the matching geometry/zero-line/exact-exclusion context without repeatedly stealing keyboard focus during drag.
- Trigger existing error and warning validation on a field that is also an active interaction target; confirm validation border/meaning remains visible and first-issue routing/focus still works.
- Cause benign preview/validation/panel refreshes while geometry, margin, zero-line and an exclusion are active; confirm the same target is rebound after overlay rebuild without resetting the current manual zoom/pan transform.
- Change the selected Glass, then add/delete exclusions; confirm old Glass targets and deleted exclusion ids are cleared rather than highlighting stale overlays or list entries.
- Exercise highlight-only field/overlay interaction without changing values and confirm Profile dirty truth, undo/redo count, Analysis Session, readiness/preflight and detector state do not change.
- Inspect the normally selected ellipse at Fit and high zoom: confirm all eight resize directions remain available but handle markers are restrained circular affordances rather than dominant squares.
- At each Windows display scale, acquire all eight resize handles comfortably; confirm the small visual marker still has a practical hit target, active resize handle is obvious, minimum size/frame bounds hold and saved source-pixel coordinates remain accurate.
- Repeat the shared-canvas check in **분석 영역 편집** and wizard/video preview consumers; confirm consumers that do not provide an active target retain their existing display and ROI private-copy/Apply/Cancel behavior.

## Multiple-point preflight
- Open the modeless **여러 시점 점검** window and confirm the Workbench video geometry does not shrink.
- Resize the preflight window and its result table columns.
- Operate the Workbench and preflight window at the same time.
- Run, cancel and rerun without duplicate signal handling.
- Select a result row and confirm the Workbench selects the correct Glass and seeks to the correct timestamp.
- Change profile, video, analysis time, Glass or detector settings and confirm the prior result becomes stale.
- Close and reopen the preflight window; confirm the last result/stale state is retained appropriately.
- Close the Workbench while preflight is open or running; confirm the window closes and no video file lock or orphan process remains.

## Preview/debug
- Rapidly scrub seek bar and verify only latest preview appears.
- Change margin, confidence, Canny and foam settings and verify preview refresh.
- Inspect all six debug tabs and candidate reject reasons.
- Export selected-frame debug artifacts and open every PNG/CSV/JSON.

## S5-A Foam and transparent-oil discrimination
- Validate real diffuse white Foam, low-light Foam and partial Foam fronts against user-recorded truth.
- Validate transparent-oil agitation, refractive shimmer and heat-haze-like motion without Foam.
- Include compressor startup immediately after energizing, when fluid motion is fastest.
- Include clipped glare, moving Glass reflection, blur and fogging.
- Run Glass 1, 2 and 3 independently and together; verify Foam temporal state never crosses Glass boundaries.
- Verify a one-sample transient shimmer is rejected and sustained Foam remains accepted.
- Verify a moving Foam front remains continuous within the configured jump limit and a discontinuous jump restarts persistence.
- In Workbench preview and modeless preflight, inspect Foam decision flags without changing the official Recipe unintentionally.
- Run full analysis, then inspect Foam whiteness, texture, glare-excluded, combined-evidence and accepted-component images in Result Review debug.
- Run partial re-detection with changed Foam settings and confirm every additive setting appears in the comparison.
- Record user truth for representative Foam and shimmer scenes and run the external S1 benchmark dataset.
- Measure median Windows CPU frame time with debug disabled and compare against the accepted exact-head baseline.
- Run a long-duration 1–3 Glass analysis and confirm memory remains bounded and no frame history accumulates in the Foam gate.
- Build and run the one-folder package on a general office Windows PC without CUDA or any GPU-compute runtime dependency.
- Repeat with Unicode and long paths, active file locking, cancellation and application close; confirm video/output/debug resources are released.

## S5-B oil boundary and temporal tracking
- Validate a real, visually clear oil boundary and a weak transparent-oil boundary against user-recorded truth.
- Validate transparent-oil agitation, shimmer and heat-haze-like motion without forcing a numeric boundary.
- Validate structural horizontal lines, Glass rim, glare and reflection separately and together with a real oil boundary.
- Include low lighting, blur and fogging; verify conflicting evidence produces review rather than a forced position.
- Validate full no-interface and empty no-interface scenes; raw and smoothed numeric positions must remain blank.
- Validate rapid filling, rapid draining and the immediate compressor-startup transient without permanent jump rejection.
- Validate one-sample and multi-sample oil-boundary dropout; a missing current sample must not display a stale smoothed number.
- Insert a deliberately misleading strong line, then verify bounded recovery to the true oil path.
- Validate visible-to-no-interface and no-interface-to-visible transitions, including stale smoothing removal and bounded reacquisition.
- Run Glass 1, 2 and 3 independently and together; verify oil path, smoothing, polarity and reacquisition state remain isolated.
- Exercise Workbench preview, modeless preflight, full analysis and partial re-detection with the same representative scenes.

### Legacy pre-cutover inspection
- Before S5-B2 cutover, inspect the current production path's consensus source support, signed contrast/polarity, static overlap, no-interface decision, path margin, tracker update and reacquisition metrics to understand legacy behavior.
- Treat these legacy metrics as cutover-context and compatibility/debug evidence only; they are not the acceptance owner for the new typed hypothesis pipeline.

### S5-B1 typed foundation evidence
- Inspect immutable raw-observation identity and provenance from source evidence through every derived view.
- Inspect proposal Y span/diameter, members per proposal and total proposal count.
- Confirm proposal construction does not create a transitive-chaining bridge between otherwise separate evidence groups.
- Inspect broad region-step evidence separately from narrow line/pulse evidence.
- Inspect continuous boundary likelihood, continuous artifact likelihood and ambiguity likelihood with its reason.
- Inspect the soft static-prior contribution and confirm it does not erase contradictory current evidence.
- Inspect typed boundary, no-interface, ambiguous and unavailable projection outcomes.
- Inspect raw-observation, proposal, hypothesis and temporal-state resource counts and confirm each remains bounded.

### S5-B2 cutover audit
- Confirm the typed hypothesis pipeline exclusively owns production oil selection, no-interface and temporal decisions.
- Confirm official `PhaseDetection`, candidate rows and debug metrics are one-way projections from the accepted typed temporal decision.
- Confirm legacy generator, consensus, scorer, no-interface and `OilTemporalPath` metrics or state do not exercise production selection authority or provide fallback.

### Cross-stage validation
- Record user truth and run an external S1 regression dataset containing real oil boundary, reflection, structure, no-interface, dropout and rapid-flow categories.
- Measure Windows CPU median and long-duration memory with debug disabled; compare against the accepted exact-head baseline and verify bounded path state.
- Build and run the Windows one-folder package on a general office PC with an integrated/basic GPU and with no CUDA or dedicated GPU compute runtime.
- Repeat with Unicode and long paths, active file locking, cancellation and application close; confirm video, output and debug resources are released.

## Analysis lifecycle and cancellation
- Run 1-, 2- and 3-Glass analyses with a long real compressor video.
- Confirm the dialog displays all six stages in order: 영상 분석, 이벤트와 판정 계산, 결과 이미지 생성, CSV와 snapshot 저장, graph와 보고서 생성, bundle 마무리.
- Confirm frame analysis completion remains below overall 100% and stages 2–6 stay visible.
- On a slow disk, confirm graph/report and bundle-finalization progress remains visible rather than appearing frozen.
- Cancel separately during each of the six stages and confirm no completed bundle is exposed before atomic finalization.
- Confirm cancellation or failure removes the temporary result directory and debug staging directory.
- Confirm the completion dialog appears only after the final result directory and manifest are visible.
- Cancel immediately before finalization, then test a late cancel after finalization; confirm only the pre-finalization case is discarded.
- Close the Workbench while analysis is running and confirm the worker thread exits without an orphan thread, process, video lock or output lock.
- Exercise a long Unicode output path and a deeply nested Windows path.
- Open report offline with network disconnected.
- Confirm full/empty rows have blank numeric levels in CSV.
- Open Result Review from a Foam/review case and use **사용자 정답으로 확인**; confirm Glass, frame and timestamp context are retained and the official result bundle is unchanged.

## Result visualization
- Open Result Review on Windows with Malgun Gothic available and verify Korean title, axes, legend, annotations and empty-state text.
- Open the partial re-detection comparison and verify Korean graph labels and table headers: 공식/재검출 유면 and 공식/재검출 거품 경계.
- Open the offline HTML report and verify every combined/detail graph renders Korean text without repeated missing-glyph warnings.
- Verify negative y-axis tick labels and minus signs remain readable.
- Test Glass 1–3 with different ellipse positions, vertical radii, margin ratios and zero-line positions.
- Confirm each Glass detail graph includes the full inner-ellipse analysis area, 기준선 0 and both analysis boundaries even when observed values occupy a narrow band.
- Confirm exclusion rectangles do not reduce the graph's full vertical analysis range.
- Verify a Glass with valid `mm_per_pixel` uses mm on its detail graph and a px-only Glass stays in source pixels.
- Verify a mixed-scale combined graph remains in px and covers the union of all included Glass analysis ranges.
- Verify full/empty no-interface data, all-missing series and intermittent missing values remain gaps rather than zero-valued lines.
- Repeatedly open and close Result Review and re-detection windows; confirm Matplotlib callbacks, fonts and file handles do not accumulate.

## Packaging
- Run the Windows canonical suite with Python 3.14.
- Before packaged startup, confirm the user/system does not require a preconfigured `QT_QPA_PLATFORM`; clear any inherited value in the validation shell and do not persist a user/system environment change.
- Build and verify the one-folder distribution on Windows in the supported Python 3.14 environment used as the project release baseline.
- Confirm `RotaryOilLevelTracker.exe` opens the native Windows GUI without external QPA setup; the package runtime bootstrap must select the `windows` Qt platform before the GUI entry script.
- For one bounded conflict probe, launch once with only the child-process environment set to `QT_QPA_PLATFORM=offscreen` and confirm the packaged GUI still opens normally, proving the package-owned Windows selection overrides a bad inherited value. Remove the probe value immediately afterward; it is not an installation prerequisite.
- Record the interpreter actually used; do not claim an unexecuted patch version or Windows result.
- Copy `dist/RotaryOilLevelTracker` to a clean machine without Python or separately bundled font files.
- Run the complete Workbench, preflight, analysis and Result Review workflow from the one-folder package.
- Confirm Windows Malgun Gothic is selected on a clean PC and the application does not require a repository font binary.
- Generate HTML/CSV in a user-writable output folder.
- Confirm Jinja template, Qt plugins and matplotlib resources resolve after relocation.
- Repeat output generation with file-locking software active and confirm resources are released after close.

> These are manual follow-up items. A GitHub-only validation run does not claim that they were performed.
