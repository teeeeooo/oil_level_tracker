# Current Work Plan

**Current milestone:** `P-2b — Windows package and distribution` /
`PLANNED`, next: a short interview on its scope (user, 2026-11-03).
**Last completed:** `P-2 — User manual` / `DONE` (2026-11-03): the user
fixed the first draft, an offline page opened from the help
([decisions and making](../40-operations/user-manual.md)). Before it, P-1
(the introduction video) closed the same day. **The first version is
accepted** (2026-11-02). **After P-2b:** P-3 field-use fixes.

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
- **V2-2 follow-up** (user, 2026-10-29, after the Windows run; seen on
  Windows in the V2-3 run):
  - the analysis range band on the scrub bar is yellow (`--range-fill`,
    `--range-edge`);
  - a time field shows a typed value as `mm:ss.s` once entered;
  - **the inspection name** (Product SSOT §3, §8): optional in the setup,
    shown in the list and the result, and naming the folder; without one,
    the folder is named as before. It is fixed once the folder exists;
  - **fixed:** the local server's listen queue was 5, so a page load
    sometimes lost a JavaScript module to a reset connection and stayed
    blank (seen as a flaky browser smoke test). It is now 64.
- **V2-3 result:** the editor passed on the workstation in
  [the run](../60-evidence/2026-10-30-v2-3-editor-windows-result.md) and
  [its re-check](../60-evidence/2026-10-30-v2-3-editor-recheck-windows-result.md).
  - **The time limits pass there:** A4 39.3 s for SPL#1, A5 2.8 / 8.9 ms,
    the exact frame 56 ms, 1× playback in the `<video>` (SPL#1 is H.264).
    The slowest PC is reference only (Product SSOT §2).
  - **The editor:** `web/editor.js`, `lines.js`, `player.js`, with
    `render.js` drawing in layers (back, lines, marks) so a drag redraws
    only the lines. Edits are `edits.json` beside `inspection.json`
    ([inspection-folder.md](../20-architecture/inspection-folder.md)),
    saved on "저장"; leaving or closing the window with unsaved edits asks
    (WinForms on Windows). Re-analysis keeps the edits inside the new
    range. The SHA-256 warning (A9) checks the source on each open.
  - **The user's decisions of 2026-10-30** (Product SSOT §6): Delete
    empties the line chosen in "그릴 선"; the point line follows the snap
    (along the edges, or straight); the pencil's "수평·수직" switch; the
    view stays inside the analysed range, with "전체 보기".
  - **After the re-check** (user, 2026-10-30): with the snap on, the point
    line keeps within 8 px of the straight line between two points
    (`video/trace.py`); free to follow the strongest edges, it ran to the
    image's top or bottom in practice (for spans of 10 s and more).
  - **Not yet seen on Windows:** the upright stroke as a vertical step
    (`ca7d3ee`, from the re-check's C4 note) and the point line's 8 px
    band.
- **V2-4 result:** the judgment, the override, submitting and versions,
  and the report passed on the workstation in
  [the run](../60-evidence/2026-10-30-v2-4-judgment-report-windows-result.md)
  and [its re-check](../60-evidence/2026-11-02-v2-4-recheck-windows-result.md)
  (2026-11-02, on `b66f387`).
  - **The judgment:** `domain/judgment.py`, with 22 fixed cases in
    `tests/test_domain_judgment.py` (A3). Where §5 is silent (agent's
    choices): invalid samples inside a recovery's hold are passed over;
    an invalid sample ends a violation run; a run lasts its sample count ×
    0.5 s; the HOLD modes ignore the compressor start.
  - **Saved data** ([inspection-folder.md](../20-architecture/inspection-folder.md)):
    `edits.json` schema 2 holds each Glass's decision (`override`,
    `reason`, `checked_at`); `inspection.json` schema 2 holds
    `report_header`; `versions\NNN\` holds a submitted version, locked by
    the app (`Editing.is_locked`, 409).
  - **The report:** `adapters/report` (`HtmlReports`) writes
    `versions\NNN\report.html` on submitting, drawn by `web/render.js`
    with `web/report.js`; 379,159 bytes for 68 minutes (A7).
  - **The user's rules** (2026-10-30): the report shows the final
    judgment only, and a Glass the user judged gets one line "판정 사유:
    <reason>", never "덮어씀"; versions stay in the inspection folder; the
    header is entered in the setup and checked in the submit dialog; the
    right column reads 원본 영상, 편집, 판정, Glass, 분석; memos live in
    the toolbar's list; the report's page 1 holds the facts, the
    judgments and every Glass's graph, then a page per Glass; the
    pencil's lock is "수평" only.
  - **Agent's choices, in DESIGN.md §5:** the header saves at once and
    holds 60 characters; revising keeps each Glass's decision and check; a
    submitted version hides the editing panels; an older version a later
    re-analysis no longer fits offers its report; the report embeds the
    context image at most 2,000 × 360 px as JPEG and prints in colour;
    "보고서 열기" uses the default browser; a HOLD mode's longest
    violation is banded.
  - **Left on the workstation:** 1907 (SPL#4) with v1–v3 submitted; 1913
    (SPL#1) with v1–v2 submitted; 1910 (SPL#1) and `V2-3 확인` untouched
    by V2-4. Backups `C:\olt-v24-backup` and `C:\olt-v24b-backup`.
- **Documentation:** the v1 conventions, per [docs/README.md](../README.md).
  - numbered folders;
  - the date catalog and its pre-push check;
  - the roadmap and the execution policy;
  - the recall index.
- **The repository holds only v2.**
  - v1 is at tag `v1-final` and branch `archive/v1`.
  - v1 local evidence is at `~/Developer/oil_level_tracker-v1-evidence/`.
  - Branch `spike/webui` is kept for porting.

## V2-4b — Video window and pattern copy

**Why:** after the V2-4 re-check the user asked for two features, both for
the first version, before V2-5 (user, 2026-11-02), so that A1–A9 are
judged once on the final build.

**Scope** (Product SSOT §6, 2026-11-02):
- **the full-size view:** a button on the editor's video opens the source
  at full size in a window of its own (a second OS window, not inside the
  app's, for a second monitor); its play position and the editor's time
  follow each other;
- **copy and paste:** the range tool's selection copies the Oil and Foam
  lines (not the reference line, nor "cannot judge"); the user pastes by
  repeating over a stretch or at places picked one by one, chosen each
  time; the user picks where, with no tie to the compressor start; the
  pasted stretch keeps its heights, with no snap; for the judgment and
  the check a paste counts as drawing a new line.

**Steps:**
1. **Start decisions and mock-ups — done** (2026-11-02). The user
   confirmed [editor.html](../../design/mockup/editor.html) `#bigview`,
   `#copy`, `#paste`, `#repeat` and
   [video-window.html](../../design/mockup/video-window.html) with the
   agent's choices in them; they are in DESIGN.md §5 ("copy and paste",
   "Video window"). New tokens: `--frame-button-bg`, `--frame-button-hover`.
2. **The full-size view — done** (2026-11-02):
   - `app.py` `VideoWindow`: a second pywebview window, one at a time,
     brought forward when shown again, closed with the editor or the
     app's window; its place is kept in
     `%LOCALAPPDATA%\OilLevelTracker\video-window.json` and dropped when
     no screen shows it. `Desktop.show_video_window` /
     `close_video_window`; `POST /api/inspections/<id>/video-window`
     answers the page's path and whether a window opened (in a browser the
     page opens a popup instead).
   - **Sync:** the two WebView windows share no browser channel, so
     `adapters/http/relay.py` passes long-polled messages
     (`/api/relay/<channel>`). The editor is the master
     (`web/videolink.js`): it sends its state (time, playing, speed, the
     Glass, the range) on each change and twice a second while playing,
     and the chosen Glass's lines; the window (`web/video.html`,
     `video-window.js`) plays its own `<video>`, jumps past 0.25 s of
     drift, shows the exact frame when paused, and sends its transport as
     commands. `render.videoOverlay` draws the Glass for both videos.
   - Checked on macOS: unit and API tests, a browser smoke test (the
     popup follows and moves the editor, closes on leaving), and a probe
     of the pywebview window (open, re-point, close, place saved).
     **Not yet seen on Windows:** WebView2's second window, bringing it
     forward, the saved place with display scaling, and two decoders at
     once on the slowest PC.
3. **Copy and paste — done** (2026-11-02): `web/lines.js`
   (`copyStretch`, `pasteAt`, `repeatStarts`, `History.recordLines`: one
   undo step over Oil and Foam, an entry of kind `lines`) and
   `web/editor.js` ("copy and paste": Ctrl+C, Ctrl+V with the ghost under
   the pointer, "반복 붙여넣기…" with its three time fields, Enter, Esc, and
   dragging the first ghost); `render.js` draws the ghosts in the marks
   layer. A paste writes heights as `DRAWN` and empty samples as
   `EDITED` (as a delete does), so it takes the check off when it touches
   Oil. At most 1,000 copies in one repeat (agent's choice). Checked by
   an in-page unit check and a browser smoke test on macOS.
4. **A Windows run of V2-4b — done, every row passes** (2026-11-02,
   [result](../60-evidence/2026-11-02-v2-4b-windows-result.md); request
   pinned to `f2d6850`). The user: built as asked; copy and paste is
   useful for the on-off tests; **the big window stutters when playing
   at a higher speed** (see Open items). The V2-1 items never seen on
   Windows (a Recipe saved at another frame, a redirected Documents
   folder, the resolution refusal's wording) move to the V2-5 acceptance
   run.

## V2-5 — the steps

Held until V2-4b closed (user, 2026-11-02); V2-4b closed the same day:
- **Frozen paths — done, no code change:** PyInstaller sets a frozen
  module's `__file__` inside the build, so `bootstrap.WEB_FOLDER` finds
  `web/` where the spec ships it (`oil_tracker/web`). Checked by a macOS
  one-folder build (below).
- **Logs — done:** `app.start_log` writes `app.log` in
  `%LOCALAPPDATA%\OilLevelTracker\` (Product SSOT §8): the error stream
  (tracebacks, pywebview's log) goes to the console when there is one and
  to the log always; `faulthandler` adds a crash's stack. Over 1 MB it
  becomes `app.1.log` at the next start. A folder that cannot be written
  leaves the app running without a log.
- **The spec and the build script — done:**
  [OilLevelTracker.spec](../../packaging/OilLevelTracker.spec) (one
  folder, no console, `OilLevelTracker.exe`, the icon on Windows; other
  window toolkits and test tools left out) and
  `scripts/build_package.py` (PyInstaller 6.21.0, the `package` extra):
  builds into `build/dist/OilLevelTracker`, reports the size against A8,
  starts the built app without a window, asks for four pages, and checks
  that nothing in the package folder changed; ends in `package=PASS`.
  - **macOS build** (2026-11-02, PyInstaller 6.21.0): 239 files, 141.9 MB,
    pages served from the frozen `web/`, the package folder unchanged,
    `app.log` written with "(build)"; the windowed build ran with nothing
    in the log. The Windows size is unknown until the workstation builds
    it: trimming waits for that number (the spike's build was 152 MB).
- **An icon — done** (2026-11-02): the user chose candidate A of three
  ([design/icon/](../../design/icon/candidates.html)), the sight glass;
  DESIGN.md §4 "App icon". `packaging/OilLevelTracker.ico` is made by
  `scripts/make_icon.py` (Playwright and Chrome, on the Mac) and checked
  by `tests/test_app_icon.py`; the spec points at it.
- **The big window's stutter at a higher speed — done** (user, 2026-11-02:
  in V2-5); see Open items.
- **Measuring the build — done:** `measure_editor.py --app` starts the
  built exe with WebView2's debugging port (the app's
  `OLT_WEBVIEW_DEBUG_PORT`, handed to pywebview's `REMOTE_DEBUGGING_PORT`;
  WebView2's own `WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS` is not read under
  pywebview, which sets the arguments itself: the first Windows attempt
  on `7dc38e7` never reached the window), analyses through its API
  (the token from its page's address) and measures A5/A6 in its window,
  with the time until the window shows the list. Checked on macOS with a
  stand-in app (Chrome with the same port). It found a page bug, fixed:
  a resize while an inspection opened drew before the view was set. The
  app also logs `window: page loaded … s after start`. **Unproven on
  Windows:** the port through pywebview; the request falls back to Edge
  with the source if it fails.
- **The V2-5 request — waits on the user:**
  [2026-11-02-v2-5-acceptance-windows-request.md](../40-operations/2026-11-02-v2-5-acceptance-windows-request.md),
  revised twice and pinned to `daf381a` (`checked=108`), run again from
  §0 in a new folder (backup `C:\olt-v25c-backup`). Second attempt
  (`5bb9025`): the port answered but Playwright showed no page, taken as
  a connection made before WebView2 created it; the script now waits for
  `/json/list` to show the page, reconnects, and failing that measures
  the build's server in Edge (marked in the result). On the workstation: tests
  (`261 passed, 4 skipped`), the build (`package=PASS`, ≤ 200 MB), the
  ZIP for the slowest PC, A4–A6 measured in the build, the pre-run
  lists, then the user in the build: Recipes `V25 SPL#4` (at ~01:00) and
  `V25 SPL#1` (at ~10:00), the resolution refusal (a 1280×720 file the
  agent makes), new inspections `V25 SPL#4 인수` (save, restart, resume,
  judge, submit v1, report PDF, resubmit v2) and `V25 SPL#1 인수` (1×
  play, the big window at 4×, submit, 68-min PDF), and the source warning
  on `V2-3 확인` (one byte appended, then the length restored). The
  slowest PC (user, 2026-11-02): the built ZIP moved and run only, no
  build there; A8's "runs with only WebView2" is judged there, its times
  are reference. The four existing inspections are not submitted.

## Session state — 2026-11-02

The first version is accepted on the one-folder build of `8448e79`
(`OilLevelTracker.exe`, 159.6 MB). On the workstation the data folder now
holds seven inspections: the four earlier ones unchanged, `V25 SPL#4 인수`
(v1, v2 submitted), `20261102-1521_SPL#1_Heating_coldstart` (Recipe
`V25 SPL#1`, v1 submitted) and `V25b 선택 확인` (saved, both Glasses
checked, not submitted); Recipes `V25 SPL#4` and `V25 SPL#1` beside the
two earlier ones. Backups: `C:\olt-v25c-backup`, `C:\olt-v25d-backup`.
The slowest PC holds the moved build in `C:\olt-v25\OilLevelTracker` and
one submitted SPL#1 inspection.

## Session notes

**Learned these sessions:**
- A request whose agent's quick O/X was wrong once (the console row) is
  read from its raw lines; likewise a mock-up label can carry meaning the
  user did not intend ("덮어씀" read as tampering). Show wording that a
  reader outside the team will see before building it.
- A Windows agent's account of the code can be wrong: it told the user the
  draft does not follow the point line's edges, when both use the same
  edge strength. Check the code before relaying such an answer.
- A request's steps must not undo what its criteria count: E7 told the
  user to Delete "몇 초" anywhere, and R2 then counted drawn Oil. Say where
  each step acts when a later criterion reads its result.
- A Windows agent's own O/X can differ from the fixed criterion (it passed
  the console row because the traceback did not come at a close). Judge
  from the relayed lines, not the agent's table.
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
- A Windows request that submits must say which steps not to take: the
  user pressed "고쳐서 다시 제출 (v3)…" after v2, and R2 then expected no
  working copy. Name the irreversible buttons a step must leave alone.
- A sampled line cannot draw a vertical: one height per 0.5 s makes any
  "upright" a slope and a spike back. Explain what the data can hold
  before building the second fix of a visual complaint.
- A modal `<dialog>` closed by Esc keeps the focus on its text field, so
  `typing()` stays true; let go of it on "cancel" (at once) and "close".
- A report's page that shares a fixed height should let its plots flex
  (`flex: 1`): fixed heights left a squeezed page 1 and an empty page 2.
- A value in a result that differs from the step's text, where the same
  path worked in another row, is most likely what the user typed: ask
  before calling it a defect (R3 of the V2-4 re-check, 2026-11-02).
- The server serves the web files only under `/web/`: a page path of
  `/video.html` was a 404 (caught by the smoke test).
- Two pywebview windows share no browser channel (WKWebView and WebView2
  windows each get their own store in private mode), so pages talk
  through the server; a page must join the relay before the other side
  can answer, or its first message is lost.
- macOS reports a window's position as floats; round before saving.
- Playwright calls a zero-width SVG line "hidden": wait for
  `state="attached"`, and wait for marks drawn on the next frame.
- WebView2 under pywebview ignores `WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS`
  (pywebview sets the browser arguments itself); its debugging port comes
  from pywebview's `REMOTE_DEBUGGING_PORT` (the app's
  `OLT_WEBVIEW_DEBUG_PORT`). A CDP connection made before WebView2 has
  navigated to the app sees only `about:blank` and never the app page:
  connect once `/json/list` lists it (the user's diagnosis agreed,
  2026-11-02). Playwright's `close()` on such a connection only
  disconnects.
- macOS's first start of a fresh build takes about 30 s (the system
  checks the new binaries); later starts take under a second.
- Over Remote Desktop, frame intervals are about 31 ms (the remote
  display's rate); redraw times do not change. Note RDP in a result.
- A request copied from an older one can point at UI that has moved: the
  V2-5 request said "검사 정보에" after V2-4b had removed that section.
  Check each step against the current screen.
- A result block's "before" list can be taken after the run: compare it
  with the previous run's final list and the backup's file count.

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

**The big window stuttered at a higher speed** (V2-4b run, W6): it sought
whenever it drifted more than 0.25 s of video time from the editor, about
60 ms of wall time at 4×, and each seek decodes from a key frame. **Fixed
in V2-5:** `videolink.catchUp` makes up a small drift with the playback
rate (±10 %) and jumps only past 1 s of wall time. A probe on macOS (two
`<video>`s of a 250 s 720p file, the window following by the editor's
messages every 500 ms): the old rule sought 23–24 times in 12 s and fell
behind; the new one sought once (the start) and stayed within 0.06 s, at
1× and 4×. To see on Windows in the V2-5 run.

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
  test. At `8c9ea35`: `202 passed, 3 skipped` on macOS, so
  `201 passed, 4 skipped` on Windows when its venv has no Playwright.
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
  - It now also has `pywebview==6.2.1`, `playwright` 1.64.1 and
    `imageio-ffmpeg` 0.8.0 (the intro video's ffmpeg).
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

- **Done:** V2-5 (2026-11-02), and with it the first version:
  - [workstation run](../60-evidence/2026-11-02-v2-5-acceptance-workstation-windows-result.md)
    on `daf381a`: A1–A9, A4–A6 in the build's window;
  - [slowest PC](../60-evidence/2026-11-02-v2-5-acceptance-slowest-pc-windows-result.md):
    the moved build ran the whole flow with only the WebView2 runtime;
  - after the user's notes (select tool, deleting a picked line,
    FULL/EMPTY made easy, the refusal wording; Product SSOT §6),
    [re-check](../60-evidence/2026-11-02-v2-5-recheck-windows-result.md)
    on `8448e79`: every row, A5 2.2 / 9.3 ms.
- **Done:** P-1, the introduction video (2026-11-03,
  [scenes and making](../40-operations/intro-video.md)). The video is
  outside Git: `~/Movies/OilLevelTracker/intro-draft3.mp4`.
- **Done:** P-2, the user manual (2026-11-03,
  [decisions and making](../40-operations/user-manual.md)):
  - the page is `src/oil_tracker/web/manual/`, made by
    `scripts/render_manual.py`;
  - it opens from the help's "사용 설명서" button;
  - the user's review changed only two captions ("우유" → "유체");
  - the doubled "영상을 열 수 없습니다:" notice found while making it is
    fixed in three places, with a smoke-test step.
- **Next: P-2b — Windows package and distribution** (user, 2026-11-03).
  It starts with a short interview. What it can build on:
  - `scripts/build_package.py` and `packaging/OilLevelTracker.spec` (the
    one-folder build, `package=PASS`, ≤ 200 MB; "Notes for Windows runs"
    above);
  - the ZIP the V2-5 run made for the slowest PC.

  To settle in the interview: the version number (`pyproject.toml` says
  `2.0.0.dev0`), the form (the folder as a ZIP, or an installer), how it
  reaches the PCs and who installs it, whether the introduction video and
  the user manual go with it, and release notes. The build's first
  Windows run also checks that the help opens the manual in Edge (P-2
  left that to this run).
- **After P-2b** (user, 2026-11-02): **P-3 — fixes for problems found in
  field use.** The open items above (speed-ups on the slowest PC, small
  facts) stay for reference until P-3 picks any up.

## Session handoff — 2026-11-03 (P-2 done; P-2b next)

**Where it stands:** the first version is accepted (`8448e79`). Since
then the app has gained the user manual, its help button and the fix of
the doubled video notice; no Windows build has these yet.

**Next session: start P-2b** with the interview above. **Read first:**
- this file, including "Notes for Windows runs";
- the [roadmap](roadmap.md);
- the [execution policy](execution-policy.md) for Windows runs;
- `scripts/build_package.py`;
- the V2-5 requests in `docs/40-operations/` as the latest models of a
  Windows request.
