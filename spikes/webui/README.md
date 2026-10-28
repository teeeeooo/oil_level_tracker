# Web UI spike (2026-10-28)

**Status:** throwaway spike on branch `spike/webui`. Nothing here is product
code, and `src/oil_tracker` does not import it. It answers one question: can
v2 build its editor and report as a web UI (pywebview, WebView2 on Windows)
instead of Qt?

## Why

The user's 2026-10-28 interview decided the v2 direction:
- The editor extends the result review screen: graph on top, context image
  below, edited lines drawn over both.
- The report uses the same layout as the editor.

A web UI lets the editor and the report share one drawing code. Qt would
need two. The spike checks the parts that only target Windows can answer.

## What the spike contains

- `app.py`, `context.py`, `server.py`: the Python side.
  - Builds a full-resolution context image for one Glass. Each column is
    one time; each row is the RGB median of one source row inside the
    central 40% of the ellipse.
  - Builds a background-subtracted view (per-row temporal median removed).
  - Builds a naive draft line: the strongest vertical edge per column,
    thinned to about one point per 2 s. It is a placeholder for the
    planned context-image extraction, not that extraction.
  - Decodes source frames on request.
  - Saves versioned edits and writes a self-contained HTML report.
  - Everything runs on a local server bound to `127.0.0.1`. The window
    (pywebview) opens that address.
- `static/`: plain JavaScript with no build step, so Windows needs only
  Python.
  - `render.js` draws the panels. The editor and the report both use it.
  - `editor.js` handles editing.
- `spike.spec`: the PyInstaller one-folder build.
- `check_ui.py`: an automated Mac/Chromium smoke check (Playwright). It
  makes no Windows claim.

The spike reads a v1 `.oilrecipe` only for the Glass ellipse and the zero
line. That is a spike convenience. v2 stays incompatible with v1 Recipes
(decided 2026-10-28).

**Out of scope:** judgment, events, draft quality, multi-Glass, Recipe
editing, the S11 detector.

## Pass criteria (frozen before the first Windows run)

| ID | Check | Pass |
|---|---|---|
| W1 | Build | The PyInstaller one-folder build succeeds on Windows, Python 3.14. Record the `dist` folder size (MB) and file count |
| W2 | Launch | The exe opens a native window that shows the UI. The diagnostics panel shows the engine as `Edg/…` (WebView2) |
| W3 | Local server | The app serves on `127.0.0.1` with no firewall prompt and no policy block |
| W4 | Context image | A field video and its v1 Recipe Glass give a context image. Record the build time and the columns × rows |
| W5 | Editing | Add, drag, corner toggle and delete points; add Oil/Foam/reference lines; add a FULL/EMPTY/unknown segment; add a memo; undo/redo; zoom/pan. The user judges the feel usable |
| W6 | Snap | With snap on, a dragged point lands on the nearby edge in the context image |
| W7 | Frame | Clicking the graph shows that time's source frame with the lines overlaid. Record the median seek time (ms) |
| W8 | Report | The saved report opens offline in Edge, and Print → Save as PDF gives a readable page |
| W9 | Draft scale | With the naive draft (hundreds of points), dragging stays smooth |

**Go:** W1–W4, W7 and W8 pass, and the user rates W5 and W9 usable.
**No-go:** any of W1–W3 fails with no simple fix, or the user rates the
editing unusable. Then v2 returns to Qt (QML / `QGraphicsView`).

## Run

```bash
python -m venv .venv-spike
.venv-spike/Scripts/pip install -r spikes/webui/requirements.txt   # Windows
python spikes/webui/app.py --video <video.mp4> --recipe <recipe.oilrecipe> --glass-index 0
```

- Options:
  - `--glass-name`: the exact Glass name in the Recipe (for example
    `BASE`). It overrides `--glass-index`.
  - `--start` / `--end`: the analysis range in seconds.
  - `--rate`: context columns per second (default 2).
  - `--out`: the output folder.
  - `--no-window`: serve only. Open the printed URL in a browser.
- Build:
  `pyinstaller --noconfirm spikes/webui/spike.spec`
  → `dist/oil-webui-spike/oil-webui-spike.exe`. It takes the same options.
- Lines starting with `SPIKE ` on stdout are the values to report.

## Mac result (2026-10-28, local only)

These results come from macOS. They say nothing about W1–W3 or W8 on
Windows.

- **Chromium check:** `check_ui.py` with Google Chrome 156 on
  `sample/sample4.mp4` (113 × 104 context, built in 1.1 s) gives
  **23/23 PASS**. The run covers:
  - drag, corner toggle, undo/redo, a new Foam line, a segment, a memo,
    delete, wheel zoom, pan, snap and the background view;
  - frame seek: median 60 ms (decode 54 ms);
  - save v001, then resume from it;
  - report v001 (48 KB), which renders offline from `file://` and prints
    to PDF in Chromium.
- **Scale (W9):** at `--rate 10 --draft-spacing 0.1` (564 points), the
  render time while dragging is median 3.9 ms, max 7.5 ms.
- **Native window:** pywebview opens the app in WKWebView (WebKit 605.1.15),
  both from source and from the PyInstaller build.
- **Mac build:** 138 MB, 217 files. This is not the Windows size.

**Defects the Mac run found and fixed:**
- `HTTPServer` did a reverse DNS lookup on bind and stalled for over 30 s.
  The server now skips it. The same stall could hit a company Windows PC.
- The frame cursor sat on top of the point just pressed and swallowed the
  next press.
- Every press redraws the panels, so the browser's `dblclick` never fired.
  The editor now detects a second press on the same point itself. Only a
  press that moved nothing counts as the first half.
- The memo box lost focus on each redraw.
