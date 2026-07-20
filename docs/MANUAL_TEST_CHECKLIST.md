# Manual GUI and Windows Acceptance Checklist

## Workbench and video
- Launch the packaged app on a 100%, 125%, and 150% Windows display scale.
- Open MP4, MKV, AVI and MOV samples supported by the deployed OpenCV backend.
- Verify play/pause, step, seek and 0.5×/1×/1.5×/2×/4× behavior.
- Verify start/end/compressor markers numerically through session fields and report.

## Geometry editor
- Add three Glass items and alternate selection.
- Drag ellipse from center and confirm it cannot leave the frame.
- Resize with left/right/top/bottom/corner handles; confirm minimum size and no inverted geometry.
- Drag zero line to top/bottom and confirm it remains inside ellipse.
- Add, move, resize and delete multiple exclusion rectangles.
- Verify stored `.oilrecipe` coordinates match source pixels after window resizing.

## Preview/debug
- Rapidly scrub seek bar and verify only latest preview appears.
- Change margin, confidence, Canny and foam settings and verify preview refresh.
- Inspect all six debug tabs and candidate reject reasons.
- Export selected-frame debug artifacts and open every PNG/CSV/JSON.

## Analysis/export
- Run 1-, 2- and 3-Glass analyses.
- Cancel in the middle and verify no completed bundle is exposed.
- Open report offline with network disconnected.
- Confirm full/empty rows have blank numeric levels in CSV.
- Confirm graph distinguishes oil-air, foam, zero, unknown and low-confidence intervals.

## Packaging
- Run the full test suite on Windows with Python 3.14.3.
- Build one-folder distributions on Windows with both the release baseline interpreter and Python 3.14.3 when possible.
- Copy `dist/RotaryOilLevelTracker` to a clean machine without Python.
- Run the sample workflow and generate HTML/CSV in a user-writable output folder.
- Confirm Jinja template, Qt plugins and matplotlib resources resolve after relocation.
