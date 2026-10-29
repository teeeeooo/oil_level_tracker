# Current Work Plan

**Current milestone:** `V2-3 — Editor` / `ACTIVE` (started 2026-10-29).
**Last completed:** `V2-2 — Analysis` / `DONE` (2026-10-29).

This is the sole owner of the current state, authorization and next action.
Rewrite it; do not append to it.

## Accepted baseline

- **Product SSOT:** [product.md](../10-product/product.md).
  - Goal and the acceptance criteria A1–A9.
  - Acceptance videos: SPL#1 and SPL#4.
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
   - **Not yet in the editor** (step 7): the point line, "cannot judge",
     memos, the compressor marker, re-analysis, the window-close question
     and the SHA-256 warning. Their toolbar buttons are there, disabled.
6. **A5 and A6 on the slowest PC — request sent, waiting on the user:**
   [the request](../40-operations/2026-10-29-v2-3-editor-slowest-pc-windows-request.md),
   commit `8a96b22`, `source=1da92bcf0279 files=54`, criteria fixed in it.
   (Re-pinned before the run: from `4086e54`, whose seek clicks could land
   on the time axis's range numbers; then for the faster draft search and
   the key-frame spacing line; then for the median comparison, stage 5.)
   - The result also gives SPL#1's key-frame spacing (for the PyAV
     decision) and the analysis time through the app's server, now with
     the faster draft search.
   - `scripts/measure_editor.py` analyses SPL#1 through the app's server,
     then drives the editor in **Microsoft Edge** (WebView2's engine) with
     Playwright, so that PC needs no pywebview or pythonnet (it runs
     Python 3.15). The packaged app is judged in V2-5.
   - It times each lines redraw during pencil strokes and grab-and-drags
     (the spike's measure), the frame intervals beside them, exact frames
     at 40 random times, the `<video>`'s own seeks, and 60 s of 1×
     playback; it also reports SPL#1's codec and whether Edge plays it.
   - **Exact frames are cropped** to the region the video panel shows (the
     frame API took a crop). On macOS with an H.264 sample, an exact frame
     took about 60–80 ms, nearly all of it OpenCV seeking and decoding;
     the `<video>`'s own seek took about 33 ms. If exact frames miss
     100 ms there, the request's criteria route the choice to the user.
   - On macOS (sample7, 1,600 × 900) the lines redraw took 0.9 ms at the
     median and 2.3 ms at most.
7. **`web`, the rest:** the point line, the snap, "cannot judge", Foam and
   reference lines, memos, the compressor marker, re-analysis, the save
   question and the SHA-256 warning.
8. **Checks:** unit and API tests, macOS smoke checks, and a Windows run.
   It also covers the V2-2 follow-up.

## Session handoff — 2026-10-29 (fifth)

**The session closed after `11c9617`,** with this handoff commit on top.
The working tree is clean, and `main` and the remote are in sync.
- V2-3 steps 1 to 5 are done.
- **Step 6 waits on the user:** they run the
  [A5/A6 request](../40-operations/2026-10-29-v2-3-editor-slowest-pc-windows-request.md)
  on the slowest PC (no agent there), pinned to `8a96b22`,
  `source=1da92bcf0279 files=54`. The user could not reach Windows in the
  evening of 2026-10-29.

**Resume:** read this file, then
- the A5/A6 request: its fixed criteria (M1–M3, A5, A5-f, A6-s, A6-p,
  A6-c) decide what comes next;
- [product.md](../10-product/product.md) §4 and §6,
  [DESIGN.md](../../DESIGN.md) §5 ("Editor window") and
  [architecture.md](../20-architecture/architecture.md) ("During a drag",
  the editor's video, the point line, `/media/`);
- the code: `web/editor.js` (screen, pointer, keys), `web/lines.js`
  (operations, snap, undo history), `web/player.js` (video),
  `web/render.js` (layers), `application/editing.py`,
  `scripts/measure_editor.py`.

**When the A5/A6 result comes:** judge it row by row against the request,
write `60-evidence/2026-10-29-v2-3-editor-slowest-pc-windows-result.md`
(or dated the day it arrives) and add it to the catalog.
- A5 fails: make the drawing lighter before step 7.
- A6-s or A6-c fails: put the choice to the user, as the criteria say.
- A4-m2 passes: put that way into `_Band.median`
  (`adapters/video/context.py`). The values are identical, so the tests
  and the pictures stay as they are.
- Also read: the key-frame spacing line (how much PyAV's skipping could
  save) and the analysis time (the app's share; the draft search is now
  about 7 s faster there).

**Work the user allowed before the result** (2026-10-29 evening, "1번,
2번하고 시간 되면 3번도"):
1. **Review and fixes — done** (`890b5ea`).
2. **A4 groundwork — done.**
   - The draft search (`ae4873c`) and the facts in the open items below.
   - **The median comparison** (`8a96b22`, user: "그 요청서에 넣고 고정한
     커밋을 다시 바꿔도 돼"): `scripts/compare_medians.py`, stage 5 of the
     A5/A6 request. It compares 11 ways that must give the app's values
     exactly: the `int16` sort, other types and layouts, a partition (half
     of each row's outside pixels sort below every value, half above, so
     every row's middle ranks fall on the same positions) and an 8-bit
     counting median. Then it runs the app's context pass over two
     minutes of SPL#1 with the two fastest. Criteria A4-m1 and A4-m2.
   - On macOS (ARM) the `int16` sort stays the fastest (0.73 ms a frame
     for a 728 × 120 band); the partition takes 1.2–1.3 ms and the
     counting median 2.9 ms, and it scales worst over threads.
3. **The step 7 parts that do not depend on the drawing or the video —
   not started:**
   - the window-close question (the pywebview closing event, when the
     edits are unsaved);
   - the SHA-256 warning (the `source-check` API exists; show
     DIFFERENT, MISSING and UNREADABLE);
   - re-analysis from the editor: "범위 바꿔 다시 분석…" opens the setup
     for the analysed inspection, saves the edits first, shows `dropped`
     from the check before starting, and comes back to the editor;
   - "cannot judge": U and "판단 불가 풀기" on the selected range. The undo
     history holds only line samples now, so it needs an entry for
     stretches.
   - The rest of step 7 (the point line with its preview, memos, the
     compressor marker) waits for the A5/A6 result.

**Learned this session:**
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

## Open items

**Before V2-5** (A4 is judged in the app on the slowest PC):
- **Less CPU work in the analysis.** The slowest PC takes 169.7 s of 180 s
  for the adapter; nearly all of it is reading the video (`grab` 113 s,
  `retrieve` 45 s).
  - **The draft search — done** (`ae4873c`): about 10× faster, the same
    best path. Exact ties (a saturated edge) now take the upper row.
  - **Cheaper medians:** the A5/A6 request's stage 5 decides (A4-m2).
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
- **What the app adds:** 60.6 s in the app against 46.4 s for the adapter
  on the workstation. The user traced the gap to a RAG chunking job at
  about 50 % CPU during the run. Confirm the app's own share on a quiet
  PC when the app is timed on the slowest PC.

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
  test. At `8a96b22`: `185 passed, 3 skipped` on macOS, so
  `184 passed, 4 skipped` on Windows when its venv has no Playwright.
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
- **A4 has about 10 s to spare on the slowest PC** (169.7 s for the
  adapter), before what the app adds. See the open items.
- **A5 and A6 are not yet measured on the slowest PC.** They must hold
  there too (Product SSOT §2). The spike's redraw median was 13.4 ms on
  the workstation against 16 ms, so V2-3 measures the editor on that PC.

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

- **Done today:** V2-1 and V2-2 closed, each with its Windows run; the
  V2-2 follow-up; V2-3 started.
- **Done today also:** V2-3 steps 1 to 5 (the confirmed mock-up, the edit
  document, `edits.json`, the editor's use cases and routes, the editor's
  web core).
- **Waiting on the user:** the slowest-PC run of
  [the A5/A6 request](../40-operations/2026-10-29-v2-3-editor-slowest-pc-windows-request.md).
  Judge its result against the request's fixed criteria and write it to
  `60-evidence/`.
- **Meanwhile (allowed by the user):** the step 7 parts that do not
  depend on the drawing or the video, as the handoff above lists. (The
  median comparison went into the A5/A6 request.)
- **Then:** the rest of step 7 after that result: the user decided that A5
  and A6 are measured before the other tools are built. If A5 fails, the
  drawing gets lighter first; A6-s and A6-c route their choices to the
  user, as the request's criteria say.
