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

## Analysis/export
- Run 1-, 2- and 3-Glass analyses.
- Cancel in the middle and verify no completed bundle is exposed.
- Open Result Review from a Foam/review case and use **사용자 정답으로 확인**; confirm Glass, frame and timestamp context are retained and the official result bundle is unchanged.
- Open report offline with network disconnected.
- Confirm full/empty rows have blank numeric levels in CSV.
- Confirm graph distinguishes oil-air, foam, zero, unknown and low-confidence intervals.
- Exercise a long video and long output path on Windows.

## Packaging
- Run the full test suite on Windows with Python 3.14.3.
- Build one-folder distributions on Windows with both the release baseline interpreter and Python 3.14.3 when possible.
- Copy `dist/RotaryOilLevelTracker` to a clean machine without Python.
- Run the complete Workbench, preflight, analysis and Result Review workflow from the one-folder package.
- Generate HTML/CSV in a user-writable output folder.
- Confirm Jinja template, Qt plugins and matplotlib resources resolve after relocation.

> These are manual follow-up items. A GitHub-only validation run does not claim that they were performed.
