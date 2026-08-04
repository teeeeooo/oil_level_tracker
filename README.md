# Rotary Oil Level Tracker

Windows desktop workbench for tracking oil-air boundaries and bottom-connected foam fronts in rotary-compressor sight-glass test videos. The application turns a reusable Glass geometry/detector **Recipe** and a video-specific **Analysis Session** into reviewable tracking data, events, judgments, captures, graphs, an offline HTML report and CSV files.

The authoritative product specification is [docs/rotary_oil_level_tracker_ssot_spec.md](docs/rotary_oil_level_tracker_ssot_spec.md). Use the [documentation guide](docs/README.md) for the roadmap, active work plan, architecture and validation documents.

## Requirements

- Python 3.11–3.14 (`requires-python >=3.11,<3.15`); validate the full suite and one-folder build on the target Windows interpreter
- Windows 10/11 for the target desktop build
- PySide6, NumPy, OpenCV headless, Jinja2 and matplotlib
- `opencv-python-headless` is declared. Do not install `opencv-python` in the same environment.

## Install

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e ".[dev,packaging]"
```

For Linux/macOS development, activate with `source .venv/bin/activate`. The packaged product target remains Windows.

## Run the GUI

```bat
python -m oil_tracker
```

The app opens the **Recipe Workbench** with:

- top Recipe actions and state
- left Glass list
- center video/overlay editor
- right selected-Glass settings
- bottom video transport
- optional Validation and Detector Debug docks

## Generate and run the synthetic sample

```bat
python scripts\generate_sample.py
python -m oil_tracker.cli analyze ^
  --recipe sample\synthetic_sample.oilrecipe ^
  --video sample\synthetic_oil_test.avi ^
  --output sample\output ^
  --start 0 --end 7.5 --compressor-start 0 --sampling-fps 2
```

PowerShell or POSIX shells can place the CLI command on one line.

## Create a Recipe

1. Choose **새 Recipe** and complete the wizard, or choose **Wizard 건너뛰기**.
2. Open a video and set analysis start/end, compressor start and sampling FPS.
3. Add a Glass.
4. Move/resize the ellipse around the sight glass.
5. Drag the zero line to the engineering reference height.
6. Set initial observation state, optional mm/pixel, judgment mode and margin.
7. Add exclusion rectangles over fixed scratches, labels, reflections or residue.
8. Seek several timestamps and inspect Preview/Debug results.
9. Save as `*.oilrecipe`, then run **Recipe 검증**.

The Recipe stores source-frame pixel geometry and detector/judgment settings. It does not store the current video path.

## Preview and Debug

Preview runs after seek settles or selected-Glass geometry/settings change. A single-shot debounce prevents every scrub position from launching detector work, and generation IDs suppress stale results.

Enable **Debug mode** to inspect:

- Overlay
- ROI / Preprocess
- Edges / Masks
- Foam
- Candidates
- State

Use **선택 frame debug export** to write overlay/ROI/preprocess/Canny/mask/foam PNGs plus candidate CSV and debug JSON.

## Analyze and export

1. Validation must have no readiness errors.
2. Choose **분석 실행** and an output root.
3. Analysis, graph rendering, capture generation, CSV and HTML run in a worker thread.
4. Progress displays sampled timestamp, current Glass and processing rate.
5. Cancellation discards the staged incomplete bundle.
6. **결과 보기** opens the offline `report.html`.

Output layout:

```text
oil_level_analysis_YYYYMMDD_HHMMSS/
├─ report.html
├─ tracking_data.csv
├─ events.csv
├─ recipe_snapshot.oilrecipe
├─ session.json
├─ analysis_manifest.json
├─ captures/
├─ graphs/
├─ assets/
├─ logs/
└─ debug/                 # only when supplied to bundle writer
```

`FULL_NO_INTERFACE` and `EMPTY_NO_INTERFACE` rows keep numeric oil-level columns blank. Their meaning is carried by `fill_state`.

## Tests

```bat
python -m pytest
python -m pytest -m qt_app
```

The first command is the canonical suite. The `qt_app` command is a focused selection
for tests that share the single pytest-qt `QApplication`; it is not additional
canonical coverage. Headless subprocess checks use the source tree directly and do
not inherit the GUI platform environment.

The test suite covers coordinate conversion, mask/margin/exclusion behavior, Recipe round-trip/versioning, validation, judgment, event debounce, candidate penalties, FillState behavior, foam connectivity, timestamp scheduling, synthetic detector fixtures, full analysis/reporting, multi-Glass decode behavior, cancellation and GUI smoke/routing.

Geometry drag/resize and Windows DPI behavior also require the [manual GUI and Windows checklist](docs/30-quality/manual-gui-windows-checklist.md).

## PyInstaller one-folder build

Build on Windows from the project root:

```bat
pyinstaller packaging\pyinstaller\oil_tracker.spec
```

Output:

```text
dist\RotaryOilLevelTracker\RotaryOilLevelTracker.exe
```

The spec collects package data and Jinja/style resources. Its Windows-only GUI runtime hook forces the native `windows` Qt platform before PySide6 runtime initialization and the GUI entry script, so users do not need to preconfigure `QT_QPA_PLATFORM`. Build on Windows and perform the clean-PC checklist before release.

## Architecture

```text
ui → application → domain
adapters → application ports / domain
bootstrap → concrete wiring
```

- `domain`: pure Python geometry, Recipe, session, detection/result models, validation, events and judgment
- `application`: ports, use cases and orchestration; no OpenCV/PySide6/Jinja2/matplotlib imports
- `adapters/vision`: OpenCV video, masks, preprocessing, candidates, scoring, foam and temporal detector
- `adapters/storage`: atomic Recipe and staged output bundle persistence
- `adapters/reporting`: CSV, matplotlib graphs and Jinja2 HTML
- `ui`: PySide6 widgets/controllers/workers
- `bootstrap.py`: concrete dependency wiring

## Detector design

```text
ellipse effective mask
→ preprocess
→ artifact masks
→ row features
→ Sobel/Canny/Hough/region/foam candidates
→ feature scoring and penalties
→ confidence rejection
→ FillState classification
→ temporal smoothing/state hold
→ separate oil-air and foam-front outputs
```

The strongest Sobel/Canny/Hough response is never automatically accepted. Full/empty/unknown states are allowed to return no numeric boundary.

## Directory structure

```text
src/oil_tracker/
├─ domain/
├─ application/
│  ├─ ports/
│  ├─ services/
│  └─ use_cases/
├─ adapters/
│  ├─ vision/
│  ├─ storage/
│  ├─ reporting/
│  └─ system/
├─ ui/
│  ├─ controllers/
│  ├─ widgets/
│  └─ wizard/
├─ config/
├─ resources/
├─ bootstrap.py
├─ cli.py
└─ __main__.py
```

Documentation entry points:

- [Documentation guide](docs/README.md)
- [Project roadmap](docs/00-project/roadmap.md)
- [Current work plan](docs/00-project/work-plan.md)
- [Architecture documents](docs/20-architecture/)
- [Quality and validation documents](docs/30-quality/)

## Current implementation scope and limitations

The application is not yet production-qualified for operational PASS/FAIL use. Real-video detector qualification, Windows clean-PC packaging and long-duration platform evidence remain governed by the [roadmap](docs/00-project/roadmap.md), [current work plan](docs/00-project/work-plan.md) and [real-world validation plan](docs/30-quality/real-world-validation-plan.md).
