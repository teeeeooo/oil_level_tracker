# Current Work Plan

**Current milestone:** `V2-3 — Editor` / `ACTIVE` (started 2026-10-29).
**Last completed:** `V2-2 — Analysis` / `DONE` (2026-10-29).

This is the sole owner of the current state, authorization and next action.
Rewrite it; do not append to it.

## Accepted baseline

- **Product SSOT:** [product.md](../10-product/product.md).
  - Goal and the acceptance criteria A1–A9.
  - Acceptance videos: SPL#1 and SPL#4.
  - **Where the time limits are judged** (user, 2026-10-30, §2): A4–A6
    pass or fail on the workstation. The slowest PC is the worst case,
    for reference only: its timings point to simple speed-ups, and a miss
    there holds nothing up.
  - All product decisions. On 2026-10-29 the user settled the Recipe (§3),
    the judgment rule (§5) and the data folder (§8) at the V2-1 start, and
    the inspection flow, the analysis setup (§3), the draft method (§4)
    and the editing aids and snap (§6) at the V2-2 start.
- **Architecture:** [architecture.md](../20-architecture/architecture.md).
  The judgment lives only in Python. Since 2026-10-29 it uses v1-style
  layers:
  - `domain` ← `application` (use cases and ports) ← `adapters`
    (`video`, `storage`, `report`, `http`, `desktop`);
  - `bootstrap.py` is the only wiring point;
  - there is no NumPy in `domain` or `application`;
  - during a drag, the bands and the judgment update from the API after
    release.
  - A test enforces the dependency rule (`tests/test_architecture.py`).
- **Visual rules:** [DESIGN.md](../../DESIGN.md), Fluent 2 light.
  - The editor layout in [design/mockup/editor.html](../../design/mockup/editor.html)
    is **confirmed by the user** (2026-10-28), and its V2-3 update too
    (2026-10-29).
  - The inspection list and analysis setup in
    [design/mockup/inspection.html](../../design/mockup/inspection.html)
    are **confirmed by the user** (2026-10-29).
  - The Recipe layout in [design/mockup/recipe.html](../../design/mockup/recipe.html)
    is **confirmed by the user** (2026-10-29). The Glass editing follows v1.
- **V2-1 result:** the Recipe screen and the `.recipe.json` file
  ([recipe-file.md](../20-architecture/recipe-file.md)) passed the Windows
  run; see
  [2026-10-29-v2-1-recipe-windows-result.md](../60-evidence/2026-10-29-v2-1-recipe-windows-result.md).
  - The user's Recipes `SPL#4_test1_607bccb` (BASE, ACCUM) and
    `SPL#1_test1_607bccb` (BASE) stay on the Windows workstation.
  - **Not yet shown on Windows:** a save at a frame other than the first,
    a redirected Documents folder, and the wording of the resolution
    refusal.
- **V2-2 result:** the inspection list, the new-inspection flow, the
  analysis setup, the progress dialog and the read-only result passed the
  Windows run on source `0df5ce6`; see
  [2026-10-29-v2-2-analysis-flow-windows-result.md](../60-evidence/2026-10-29-v2-2-analysis-flow-windows-result.md).
  - **The analysis:** one software-decoded pass for every Glass, with the
    row medians on worker threads; the drafts by dynamic programming
    (method B); the cache as PNG pieces in
    [inspection-folder.md](../20-architecture/inspection-folder.md).
    Why: the [draft comparison](../60-evidence/2026-10-29-v2-2-draft-comparison-windows-result.md)
    and the [slowest-PC timing](../60-evidence/2026-10-29-v2-2-slowest-pc-timing-windows-result.md).
  - **A4 so far:** SPL#1 takes 60.6 s in the app on the workstation (with
    another job at about 50 % CPU), 46.4 s for the adapter alone, and
    169.7 s for the adapter on the slowest PC (limit 180 s).
  - **Three inspections stay on the workstation** for V2-3: SPL#4 (an
    ACCUM correction of `cx +1`), and SPL#1 twice. Their folders and
    SHA-256 values are in the result.
  - The web screens share `web/frame.js` (frame view and Glass editing)
    and `web/render.js` (drawing, also for the report).
- **V2-2 follow-up** (user, 2026-10-29, after the Windows run; not yet seen
  on Windows):
  - the analysis range band on the scrub bar is yellow (`--range-fill`,
    `--range-edge`);
  - a time field shows a typed value as `mm:ss.s` once entered;
  - **the inspection name** (Product SSOT §3, §8): optional in the setup,
    shown in the list and the result, and naming the folder; without one,
    the folder is named as before. It is fixed once the folder exists;
  - **fixed:** the local server's listen queue was 5, so a page load
    sometimes lost a JavaScript module to a reset connection and stayed
    blank (seen as a flaky browser smoke test). It is now 64.
- **Documentation:** the v1 conventions, per [docs/README.md](../README.md).
  - numbered folders;
  - the date catalog and its pre-push check;
  - the roadmap and the execution policy;
  - the recall index.
- **The repository holds only v2.**
  - v1 is at tag `v1-final` and branch `archive/v1`.
  - v1 local evidence is at `~/Developer/oil_level_tracker-v1-evidence/`.
  - Branch `spike/webui` is kept for porting.

## V2-3 — Editor

**Scope** (roadmap; Product SSOT §4 and §6): editing on the result screen.
- grab-and-drag, the pencil, range delete and the point line, with a snap
  that can be switched off;
- "cannot judge" stretches, Foam and reference lines, memos;
- zoom, pan and time-axis input;
- the video, cropped to the Glass with the lines over it;
- the compressor-start marker; re-analysis; saving and resuming;
- the warning when a reopened video's SHA-256 differs (A9).
The judgment, the override, the report and submitting are V2-4.

**Start decisions** (user, 2026-10-29), in the Product SSOT §6:
- **re-analysis after editing** keeps the edited lines where the new range
  overlaps the old one, drafts only the new stretches, and says first which
  edits will be dropped;
- **saving:** the "저장" button, and a question before leaving the editor
  or closing the window with unsaved changes;
- **A5 and A6 on the slowest PC** are measured as soon as grab-and-drag,
  the pencil and the video work, before the other tools are built.

**Left to the agent** (2026-10-28 interview): the edit document's schema,
the undo depth and the shortcuts.

**Steps:**
1. **Mock-up — confirmed by the user** (2026-10-29):
   [editor.html](../../design/mockup/editor.html), written into DESIGN.md
   §2, §4 and §5 and the Product SSOT §6.
   - the snap is on by default and reaches 8 source px;
   - one range tool: Delete empties the Oil line, U marks "cannot judge";
   - the grab shape is smooth, or pointed with Alt (the "corner");
   - empty stretches are `--empty-mark` bars on the time axis, with
     "다음 빈 구간" (N); a selected range is `--selection-band`;
   - the tool buttons carry their names: the user could not find the
     range tool among icons alone.
2. **`domain` — done** (`domain/edits.py`): the edit document (an Oil,
   a Foam and a reference line per Glass, as samples with their origins;
   "cannot judge" stretches; memos; the compressor start), FULL and EMPTY
   from the line position (1 px from the Glass top or bottom), the
   coverage, and the re-analysis merge. The merge keeps every old sample
   whose time the new range still has (within half a step) and reports
   what falls outside, for the warning.
3. **`adapters/storage` — done:** `edits.json` beside `inspection.json`,
   written atomically on "저장", with its format in
   [inspection-folder.md](../20-architecture/inspection-folder.md). It lies
   outside `cache\`, so the cache swap of a re-analysis leaves it alone.
   The port gained `save_edits` and `load_edits`.
4. **`application` and `adapters/http` — done:**
   - **`application/editing.py`:** opening the edits (the saved ones, or
     the drafts), saving, and what follows from any edits, saved or not:
     the FULL/EMPTY runs, the empty runs and the coverage.
   - **Re-analysis:** an analysed inspection can be set up again.
     - The check also returns what the saved edits would lose
       (`dropped`), from the times the new range will have
       (`domain.inspection.analysis_times`).
     - The previous analysis and setup stay until the new analysis is
       stored, so a cancel, a failure or closing the app leaves the
       inspection as it was (agent's choice, for A9). Then the edits are
       merged and saved.
   - **The point line:** `adapters/video/trace.py`, the draft's path pinned
     through the user's points. The edge strength is kept for two Glasses.
     At SPL#1's size on macOS, the first click takes 0.16 s and later
     ones 0.03 s per 100 columns.
   - **The snap stays in the browser,** on the context image's luma, as in
     the spike (architecture.md).
   - **The source video:** `/media/inspections/<id>/source?token=…`, with
     HTTP Range.
   - **A9:** `source-check` hashes the source on a thread.
   - **Routes,** under `/api/inspections/<id>/`: `edits` (GET to open, POST
     to save; refused while that inspection is re-analysed),
     `edits/states`, `point-line` and `source-check` (GET reads, POST
     checks again).
   - **Not known yet: the codec of SPL#1 and SPL#4.** The videos are only on
     Windows. WebView2 plays H.264, but not necessarily HEVC. Step 6's
     request checks the codec.
5. **`web`, the core — done:** the result screen became the editor
   (`editor.js`, `lines.js`, `player.js`; `render.js` draws in layers, so a
   drag redraws only the lines).
   - grab-and-drag (smooth or pointed with Alt; the grab width with `[`
     `]`), the pencil, the range tool with Delete; the snap on the context
     luma; undo and redo;
   - zoom (wheel; Shift+wheel for height), pan (the pan tool, Shift-drag or
     the middle button), the time-axis numbers, the playhead; "다음/이전 빈
     구간" (N);
   - after each change the API returns FULL/EMPTY, the empty stretches and
     the coverage for the bands, the axis bars and the Glass panel;
   - "저장" (Ctrl+S), and a question before leaving with unsaved changes
     through "검사 목록". The window close comes in step 7.
   - **The video:** `<video>` over HTTP Range for playback; a paused frame
     is the exact OpenCV frame. A file the `<video>` cannot decode plays as
     exact frames (the smoke video, MJPG AVI, does).
   - **Agent's choices:** undo keeps 200 changes, each the samples it
     replaced; the snap needs a luma step of 6 to settle; a press within
     8 px of a drawn line grabs it.
   - On macOS with an H.264 sample, a lines redraw while dragging took
     about 0.5 ms; SPL#1 on the slowest PC is step 6.
   - The point line came in step 7.
6. **A5 and A6 on the slowest PC — done** (2026-10-30):
   [the result](../60-evidence/2026-10-30-v2-3-editor-slowest-pc-windows-result.md),
   judged against
   [the request](../40-operations/2026-10-29-v2-3-editor-slowest-pc-windows-request.md)'s
   fixed criteria.
   - **A5 passes:** the lines redraw takes 5.9 ms at the median and 23.9 ms
     at most with three lines over SPL#1's 8,210 samples. The drawing needs
     no lightening.
   - **1× playback passes** in the `<video>`; SPL#1 is H.264, which Edge
     plays.
   - **The exact frame took 230 ms** at the median (413 ms at most), over
     the 100 ms limit; the `<video>`'s seek is slower (352 ms). SPL#1 has a
     key frame every 250 frames, and a seek decodes from the previous one
     (1.6–1.8 ms a frame there). On the workstation, which decodes about
     7.5× faster, the same path should take about 30 ms (not measured).
     **The user's call** (2026-10-30): usable, so reference only; the time
     limits are judged on the workstation (Product SSOT §2). Nothing waits
     on it.
   - **The cheaper median passes (A4-m2):** the `uint8` partition is in
     `_Band.median` (`908f624`), with identical values.
   - The analysis through the app's server took 163.0 s.
7. **`web`, the rest:** the point line, the snap, "cannot judge", Foam and
   reference lines, memos, the compressor marker, re-analysis, the save
   question and the SHA-256 warning.
   - **Done before the A5/A6 result** (user, 2026-10-29: the parts that do
     not depend on the drawing or the video):
     - **The window-close question** (`117f98b`): the editor tells the API
       when it holds unsaved edits (`POST /api/editor/unsaved`); `Editing`
       passes it to the `Desktop` port and app.py sets pywebview's
       `confirm_close`, with the question in Korean through pywebview's
       localization. Not yet seen on Windows (WinForms shows it with OK and
       Cancel).
     - **The SHA-256 warning (A9)** (`a79f8f2`): each time the editor opens
       it checks the source again in the background; DIFFERENT, MISSING and
       UNREADABLE show a message bar under the toolbar with "다시 확인"
       (DESIGN.md §2.7 and §5).
     - **Re-analysis from the editor** (`a6f7fcb`): "범위 바꿔 다시 분석…"
       saves unsaved edits after asking, opens the setup with "← 편집기"
       and "다시 분석", shows what the new range drops and asks before it
       starts, and opens the editor again.
     - **"Cannot judge"** (`0d7ae43`): U and "판단 불가 풀기" on the
       selected range; stretches join where they meet and split when
       cleared; the undo history records them.
   - **Also done before the result** (user, 2026-10-30: they leave the
     lines layer alone, which A5 measures):
     - **The compressor marker** (`8ec20d4`): the grab tool drags it when
       no line is under the pointer, in 0.1 s steps inside the analysis
       range. It moves to the marks while dragged. Undo covers it; the 분석
       panel shows the time it was moved from; a re-analysis starts from
       the moved time. The judgment it recomputes is V2-4.
     - **Memos** (`fdd9d9f`): the memo tool (M), numbered pins on the
       graph (`render.memoPinAt`), the memo dialog and the memo list;
       undoable like the stretches.
   - **The point line** (`9aa6382`, 2026-10-30): L; points on the context
     image **or the graph** (user, 2026-10-30, Product SSOT §6); the path
     between them from the API, dashed on the marks layer, so the lines
     layer is not redrawn; the preview shows the joins a click at the
     pointer would add. Enter writes the path into the chosen line from
     the first point to the last as one undoable change; Backspace takes
     the last placed point off; Esc, another tool or another Glass cancels.
8. **Checks — the Windows run is requested, waiting on the user:**
   [the request](../40-operations/2026-10-30-v2-3-editor-windows-request.md),
   pinned to `3cbe46e` (`checked=86`), criteria fixed in it.
   - **First try (2026-10-30) stopped at the tests:** `2 failed` on Windows
     only. The range-serving test deleted the source while its frame
     session held it open (WinError 32); the source-check test keyed a fake
     by a POSIX path string. Both fixed in `3cbe46e`; the request was
     re-pinned there, the app and the measure script unchanged.
   - **On macOS:** 208 tests pass, the editor's smoke checks among them.
   - **The run, on the workstation with its agent:**
     - the tests (`198 passed, 4 skipped`);
     - **A4, A5 and A6 judged there** with `scripts/measure_editor.py` in
       Edge (`source=4f9cb83ac6d9 files=54`), as on the slowest PC;
     - the editor on one SPL#1 inspection of V2-2 in the real window: every
       tool, undo, saving, the questions on leaving and on closing the
       window (WinForms), and resuming after a restart;
     - a new inspection named `V2-3 확인` from a copy of SPL#4 (the V2-2
       follow-up: the yellow range band, `mm:ss.s`, the name), re-analysed
       to 03:30 to drop an edit, and the source warning (A9) with the copy
       renamed and back;
     - `scripts/inspection_summary.py` now counts the saved edits
       (`3ac76ce`), which the criteria R2–R4 read.
   - If it passes, V2-3 closes.

## Session handoff — 2026-10-30 (second)

**The session closed after `69a3be0`.** The working tree is clean, and
`main` and the remote are in sync.
- V2-3 steps 1 to 7 are done; the point line closed step 7 (`9aa6382`).
- The slowest PC's A5/A6 result is judged in
  [its result](../60-evidence/2026-10-30-v2-3-editor-slowest-pc-windows-result.md);
  the user then moved the time limits to the workstation (Product SSOT §2).
- **Waiting on the user:** the workstation run of
  [the V2-3 editor request](../40-operations/2026-10-30-v2-3-editor-windows-request.md)
  (step 8), re-pinned to `3cbe46e` after the first try stopped at two
  Windows-only test failures. It starts again from §0 in a new folder.
  Later commits do not change that ZIP. The first try showed
  `checked=86 mismatched=0` and WebView2 156.0.4314.50.

**Resume:** read this file and the request (its criteria S1–S2, M1–M3, A4,
A5, A6-s, A6-p, E1–E17, N1–N11, R1–R4), then as needed:
- `scripts/inspection_summary.py`: its `edits` lines count each line's
  samples as `draft/edited/drawn/empty`, which R2–R4 read;
- `scripts/measure_editor.py`: the result file that §4 returns, judged as
  in the [slowest-PC result](../60-evidence/2026-10-30-v2-3-editor-slowest-pc-windows-result.md);
- the editor code: `web/editor.js` (tools, the point line, keys, the
  unsaved flag), `web/lines.js`, `web/player.js`, `web/render.js`,
  `web/inspections.js` (setup, re-analysis), `application/editing.py`,
  `app.py` (the close question).

**When the result comes:** judge it row by row against the request's fixed
criteria, write `60-evidence/<the day it arrives>-v2-3-editor-windows-result.md`
and add it to the catalog. If everything passes, close V2-3 (roadmap and
this file) and start V2-4; a failed row gets a fix and a re-check of what
it touches only.
- **Watch N9:** renaming the video copy while the app runs works only if
  no frame session or capture still holds it (Windows refuses an open
  file). If it fails, look at where the app closes its video sessions
  (`frame.closeVideo`, `player.close`, `Videos.close`).
- The user's notes (E2, E11, the overall remarks) may ask for changes:
  those inside the decided scope go to a fix; anything that changes a
  decision goes to the user.

**Done before the result, with the user's leave** (2026-10-29 evening and
2026-10-30): the review fixes (`890b5ea`), the draft search (`ae4873c`),
the median comparison in the request (`8a96b22`), and in step 7 the close
question, the SHA-256 warning, re-analysis from the editor, "cannot
judge", the compressor marker and memos (step 7 above lists the commits).
A closing review found three ordering bugs in the unsaved state and fixed
them (`8bec4fb`): an edit made while a save ran was marked saved; the
window flag's calls could arrive swapped; a reload left the flag set.

**Agent's choices to show the user if asked:** the source-warning bar
(DESIGN.md §2.7 tokens), the source check on every editor open (about 5 s
of background hashing on the slowest PC), the compressor in 0.1 s steps,
memo pins on the graph only, and the memo dialog. All are in DESIGN.md §5.
The point line's: points kept in time order, a click at a sample that has
a point replaces it, the snap settles a point as it does a drag, and
straight dotted guides until a path arrives.

**Learned these sessions:**
- Tests that pass on macOS can fail on Windows: an open file cannot be
  deleted or renamed there (close every video session first), and
  `str(Path)` uses backslashes (compare paths as `Path`).
- zsh does not split an unquoted variable: a re-pin wrote
  `source=766d5e5886c9 52 files=` until it was caught. Grep pinned values
  after writing them.
- Playwright's `get_by_title` and `get_by_label` match hidden elements:
  scope locators to the screen (the editor repeats the transport labels).
- `typing()` counts only text fields; a clicked switch or picker must not
  turn the shortcut keys off.
- Exact frames on macOS take 60–80 ms, nearly all of it OpenCV seeking and
  decoding; the page adds little.
- The user wants parallel progress when Windows is out of reach, inside
  the decisions already made; ask before crossing one.
- `pytest | tail -1 && git commit` commits whatever the tests say:
  `8ec20d4` went out with a failing smoke test (fixed in `942dc55`).
  Check pytest's exit code before committing.
- The editor's panels update at once, but the plots and the time axis
  redraw on the next animation frame: smoke checks wait for the drawn
  marks instead of counting them at once.
- Async ordering in the page: a `<dialog>`'s "close" event comes a task
  later than `close()`, parallel fetches can arrive swapped, and a save's
  response can come after newer edits. Keep such state where it is
  changed, send in order, and count changes across an await.
- A check written for a race must fail without the fix: the save-race
  check passed at first because an earlier notice was still on screen.

## Open items

**Speed on the slowest PC, for reference** (the limits are judged on the
workstation since 2026-10-30; these are simple speed-ups, never blockers):
- **Less CPU work in the analysis.** The slowest PC took 169.7 s for the
  adapter (limit 180 s on the workstation, where it took 46.4 s); nearly
  all of it is reading the video (`grab` 113 s, `retrieve` 45 s).
  - **The draft search — done** (`ae4873c`): about 10× faster, the same
    best path. Exact ties (a saturated edge) now take the upper row.
  - **Cheaper medians — done** (`908f624`): the `uint8` partition, 2.46×
    less worker time on that PC with identical values; about 11 s less
    over SPL#1 by the two-minute pass (an estimate, to confirm in a run).
  - **Facts measured on macOS, 2026-10-29 evening:**
    - OpenCV cannot skip to a key frame: its seek decodes from the
      previous one (~59 ms, like ~90 frames in order).
    - With `CAP_PROP_CONVERT_RGB` off, OpenCV returns only the luma plane
      and warns on every frame. That cuts `retrieve` by 72 % and the
      medians by 68 %, but the context image turns grey: the user's call.
    - PyAV 19.0.2 (in a scratch venv only): skipping to key frames
      decoded 53–95 % of the frames but saved no time with frame
      threading (single-threaded decoding saved 17–29 % but is 2–3×
      slower). Its colours differ from OpenCV's by up to 2.6 levels. It
      ships a second FFmpeg (macOS warns about the duplicate libraries).
      Band-only conversion works. A new dependency is the user's decision.
- **What the app adds:** through the app's server the analysis took
  163.0 s on the slowest PC (2026-10-30), about what the adapter alone
  should take after the faster draft search. So the server adds little;
  the workstation's 60.6 s against 46.4 s was the other job. The window
  (pywebview) is timed in V2-5.
- **Exact frames** took 230 ms on the slowest PC (key frames every 250
  frames). A cheap gain if wanted: keep the frames decoded on the way to
  a seek, so stepping back a frame and clicking nearby are instant.

**The next Windows run** also covers the V2-2 follow-up above, as the
V2-2 run covered the V2-1 follow-up.

**Small facts:**
- `AnalysisSettings.sample_count` counts to `end_sec`, but the analysis
  stops at the last frame, so it can be one more than the analysis gives
  when the range ends at the video's end. The setup caption counts as the
  analysis does.
- Closing the window during an analysis took "about 10 s" on Windows; the
  app's own part takes under 1 s on macOS. A close with no analysis
  running has not been timed there.
- The slowest PC reported Python 3.15.2 instead of 3.14; the picture was
  identical.

## Notes for Windows runs

- **Agent requests:** copy the [V2-2 flow request](../40-operations/2026-10-29-v2-2-analysis-flow-windows-request.md):
  a commit ZIP, per-file SHA-256 values, a new venv, criteria fixed before
  the run, one result block. `scripts/inspection_summary.py` and
  `scripts/recipe_summary.py` print the exact values to judge.
- **A PC without an agent:** copy the
  [slowest-PC request](../40-operations/2026-10-29-v2-2-slowest-pc-timing-windows-request.md):
  the user runs a few commands; `scripts/time_analysis.py` writes a
  Markdown result.
- **Expected Windows test line:** run pytest on macOS without Playwright
  (`sys.modules['playwright'] = None` and
  `sys.modules['playwright.sync_api'] = None`, then `pytest.main`), then
  subtract one passed and add one skipped for the macOS-only Documents
  test. At `3cbe46e`: `199 passed, 3 skipped` on macOS, so
  `198 passed, 4 skipped` on Windows when its venv has no Playwright.
- `scripts/compare_draft_methods.py` is the diagnostic behind the draft
  decision; it is the only code that reads v1 files.
- Smoke-test screenshots: set `OLT_SMOKE_SHOTS` to a folder.
- The mock-up `design/mockup/recipe.html` predates the speed field and
  the help dialog; DESIGN.md governs where they differ.

## Known limits, accepted for now

- A zero line at the very top or bottom of its ellipse can be moved only
  by typing. At that height its chord is a point under the edge handle.
- There is no Recipe deletion in the first version (user, 2026-10-29).
- The PyInstaller build (V2-5) must ship `src/oil_tracker/web/` as data.
- **On the slowest PC (reference only),** the analysis takes 163.0 s
  through the app's server and an exact frame 230 ms. The user finds that
  usable (2026-10-30).

## Local environment (macOS)

- `.venv` is the old v1 venv.
  - It now also has `pywebview==6.2.1` and `playwright` 1.64.1.
  - The v2 package is not installed in it. Run the app with
    `PYTHONPATH=src .venv/bin/python -m oil_tracker`; pytest finds `src`
    through `pyproject.toml`.
- The smoke test drives the system Chrome (`channel="chrome"`).
- Mock-up screenshots come from headless Chrome. The in-app browser pane
  cannot open `file://`.

## Left to the user, with no deadline

- deleting `~/Developer/oil_level_tracker-v1-evidence/`;
- deleting branch `spike/webui` once the porting is done.

The three v1 remote branches that v1 docs cite stay.

## Next

- **Done:** V2-3 steps 1 to 7. The A5/A6 result passed A5, playback and
  the median comparison; the `uint8` medians are in the app. The user
  moved the time limits to the workstation and keeps the slowest PC for
  reference (Product SSOT §2). The point line closed step 7.
- **Waiting on the user:** the workstation run of
  [the V2-3 editor request](../40-operations/2026-10-30-v2-3-editor-windows-request.md)
  (step 8). Its result closes V2-3 or names what to fix.
