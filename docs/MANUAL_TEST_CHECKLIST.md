# Manual GUI and Windows Acceptance Checklist

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
- Run the full test suite on Windows with Python 3.14.3.
- Build one-folder distributions on Windows with both the release baseline interpreter and Python 3.14.3 when possible.
- Copy `dist/RotaryOilLevelTracker` to a clean machine without Python or separately bundled font files.
- Run the complete Workbench, preflight, analysis and Result Review workflow from the one-folder package.
- Confirm Windows Malgun Gothic is selected on a clean PC and the application does not require a repository font binary.
- Generate HTML/CSV in a user-writable output folder.
- Confirm Jinja template, Qt plugins and matplotlib resources resolve after relocation.
- Repeat output generation with file-locking software active and confirm resources are released after close.

> These are manual follow-up items. A GitHub-only validation run does not claim that they were performed.
