# Current Work Plan

**Current milestone:** `V2-2 — Analysis` / `ACTIVE` (started 2026-10-29).
**Last completed:** `V2-1 — Recipe` / `DONE` (2026-10-29).

This is the sole owner of the current state, authorization and next action.
Rewrite it; do not append to it.

## Accepted baseline

- **Product SSOT:** [product.md](../10-product/product.md).
  - Goal and the acceptance criteria A1–A9.
  - Acceptance videos: SPL#1 and SPL#4.
  - All product decisions. On 2026-10-29 the user settled the Recipe (§3),
    the judgment rule (§5) and the data folder (§8) at the V2-1 start, and
    the inspection flow, the analysis setup (§3) and the draft method (§4)
    at the V2-2 start.
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
    is **confirmed by the user** (2026-10-28).
  - The inspection list and analysis setup in
    [design/mockup/inspection.html](../../design/mockup/inspection.html)
    are **confirmed by the user** (2026-10-29).
  - The Recipe layout in [design/mockup/recipe.html](../../design/mockup/recipe.html)
    is **confirmed by the user** (2026-10-29). The Glass editing follows v1.
- **V2-1 result:** the Recipe screen and the `.recipe.json` file
  ([recipe-file.md](../20-architecture/recipe-file.md)) passed the Windows
  run; see
  [2026-10-29-v2-1-recipe-windows-result.md](../60-evidence/2026-10-29-v2-1-recipe-windows-result.md).
  - The user's SPL#4 and SPL#1 Recipes stay on that Windows PC for V2-2.
    Their names are `SPL#4_test1_607bccb` and `SPL#1_test1_607bccb`, not
    the names the request suggested.
  - **Not yet shown on Windows:** a save at a frame other than the first,
    a redirected Documents folder, and the wording of the resolution
    refusal.
- **Documentation:** the v1 conventions, per [docs/README.md](../README.md).
  - numbered folders;
  - the date catalog and its pre-push check;
  - the roadmap and the execution policy;
  - the recall index.
- **The repository holds only v2.**
  - v1 is at tag `v1-final` and branch `archive/v1`.
  - v1 local evidence is at `~/Developer/oil_level_tracker-v1-evidence/`.
  - Branch `spike/webui` is kept for porting.

## V2-2 — Analysis

**The start decisions are settled** (user, 2026-10-29) and recorded in the
Product SSOT §3, §4 and §6:
- the app opens on the inspection list; a new inspection takes the video,
  then a Recipe;
- the setup screen sets the range, the compressor start (required only
  with a `RECOVERY` Glass, inside the range) and, if the camera shifted,
  the Glass positions in the inspection's Recipe copy;
- the analysis rate is 2 samples per second, fixed;
- the Oil draft follows the strongest edges as one path (dynamic
  programming, method B of the comparison); its weak stretches are left
  empty, and empty stretches count as invalid until drawn;
- V2-3 adds range delete, the point line (dynamic programming between the
  user's points) and a snap that can be switched off;
- after analysis, the result opens read-only in the editor layout. V2-3
  adds editing to that same screen.

**Left to the agent** (user, 2026-10-29):
- the inspection folder `Inspections\YYYYMMDD-HHMM_<video name>\` holds
  `inspection.json`, the Recipe copy `recipe.json` and `cache\`;
- the cache stores each Glass's context image and background view as PNG
  pieces of 4,096 columns, with the times and draft samples in JSON;
- the source SHA-256 is computed on a second thread during the analysis.

**Steps:**
1. **Draft-method comparison — done.**
   [Diagnostic](../50-diagnostics/2026-10-29-draft-method-comparison.md),
   [Windows result](../60-evidence/2026-10-29-v2-2-draft-comparison-windows-result.md).
   - No edge-based method followed the Oil line on SPL#4 and SPL#1; they
     follow the Foam boundary or fixed bands. The user chose method B plus
     quick deletion and the point line (above).
   - The user found SPL#1's Oil boundary faint but visible by eye in the
     full-size context image, so the context image method stays.
2. **A4 timing — done.**
   [Windows result](../60-evidence/2026-10-29-v2-2-analysis-timing-windows-result.md)
   (source `f330e62`).
   - SPL#1's whole analysis core takes **87.4 s** (limit 180 s; the draft
     comparison took 202.1 s for the context image alone). Sorting each
     row instead of `numpy.nanmedian` made the difference. The screens go
     on with this design.
   - Hardware decoding was 38 % slower, so the analysis uses software
     decoding.
   - The drafts equal the comparison's method B on Windows (empty 88 %,
     5 %, 51 %).
   - Measured on one 12-core workstation; step 9 times the app itself.
   - **The slowest target PC** (Product SSOT §2: Xeon E5-1620 v3, 4
     cores) has about half the speed per core and a third of the cores.
     Scaled from T1, the single loop would have taken about 190–210 s
     there, so step 6 made the pass faster; that PC then took 169.7 s
     (step 6).
3. **Mock-ups** of the inspection list and the setup screen, for the
   user's confirmation:
   [design/mockup/inspection.html](../../design/mockup/inspection.html)
   (the list, the Recipe picker, the setup and the progress dialog).
   **Confirmed by the user** (2026-10-29) and written into DESIGN.md §4–§5.
   The read-only result follows the confirmed editor mock-up.
4. **`domain` — done** (`3a0516f`): the inspection, the analysis
   settings with the setup checks, and lines as samples (empty where
   `None`). The "cannot judge" stretches come with the editor (V2-3).
5. **`adapters/storage` — done:** the inspection folder, the Recipe copy
   and the cache, in
   [inspection-folder.md](../20-architecture/inspection-folder.md). Images
   cross `application` as encoded PNG pieces (bytes).
6. **`adapters/video` — done** (`4750b24`): the `VideoAnalyser` port and
   `OpenCvAnalyser` (`adapters/video/analysis.py`). One pass for every
   Glass, in software decoding, gives the context images, the background
   views, the Oil drafts as domain samples and the PNG pieces, with
   progress and cancellation.
   - **The pass is faster for the slowest PC** (step 2): worker threads
     compute the row medians while the decoder reads on. NumPy's sort and
     OpenCV release the GIL. The images equal the inline pass on the tests
     and three local videos.
   - **Slowest-PC timing — done:**
     [Windows result](../60-evidence/2026-10-29-v2-2-slowest-pc-timing-windows-result.md)
     (source `2d43f4c`; the user ran `scripts/time_analysis.py` in a
     terminal there).
     - **169.7 s** on the Xeon E5-1620 v3, 46.4 s on the workstation (was
       87.4 s), with an identical picture on both.
     - In the 150–180 s band: the screens go on, and the analysis must use
       less CPU before V2-5. Decoding limits the pass with every core
       busy, so more threads do not help; the result lists three
       candidates.
     - Hardware decoding is slower on both PCs and is out.
7. **`application` and `adapters/http` — done** (`8c20d57`, `e9441be`).
   - **`application/inspections.py`:** the list, the Recipe choices for a
     video (another frame size is greyed with its reason), the setup check,
     and `prepare`, which writes the folder with the Recipe copy only when
     the analysis starts. `analyse` ends `ANALYSED`, `FAILED` with a
     reason, or `NOT_ANALYSED` when cancelled; the source SHA-256 runs on
     a second thread (`SourceHasher`, storage).
   - **`adapters/http/jobs.py`:** one analysis at a time on its own
     thread, with progress, elapsed time, time left and cancel.
   - **Routes** for step 8: `GET /api/inspections`,
     `POST /api/inspections/open-folder`,
     `GET /api/inspections/recipe-choices?video_id=`,
     `POST /api/inspections/check`, `POST /api/inspections/start`,
     `GET /api/inspections/{id}`, `GET /api/inspections/{id}/analysis`,
     `POST /api/inspections/{id}/video`,
     `GET /api/inspections/{id}/images/{glass}/{context|background}-{n}.png`,
     `GET /api/jobs/{id}`, `POST /api/jobs/{id}/cancel`. A new
     inspection's video comes from the existing `/api/videos/pick` and
     `/api/videos`.
   - Checked on a real 250 s video through the server: cancel at 38 %
     leaves `NOT_ANALYSED` and no cache; starting again gives `ANALYSED`
     with the cache.
   - **Left for V2-3:** re-analysing an analysed inspection (409 until
     then), and the warning when a reopened video's SHA-256 differs (A9).
8. **`web` — done:** the screens of DESIGN.md §5 over the step 7 routes.
   - **The inspection list** is the first screen; the Recipe list gets
     "← 검사 목록".
   - **New inspection:** the file dialog, the Recipe picker (another
     frame size greyed with its reason; "이 영상으로 새 Recipe 만들기"),
     then the setup.
   - **Setup:** the Recipe screen's frame view and Glass editing, now
     shared in `web/frame.js`; the range and the compressor start as
     `mm:ss.s` fields with "지금" and the `[` `]` keys; marks on the scrub
     bar; "Recipe와 다름" and "Recipe 위치로 되돌리기".
   - **Progress dialog,** polling the job, with cancel.
   - **The read-only result** in the editor layout: the graph, the context
     image with a "배경 제거 보기" switch, the shared time axis and the
     Glass picker; the right column shows the analysis and Glass facts.
     The video, zoom, tools and judgment come with V2-3 and V2-4.
   - `web/render.js` is ported in part from the spike's `render.js`.
   - **Fixed on the way:** the frame view asked for the middle of a frame
     and the server rounds a half to even, so an odd frame index showed
     the next frame and the view kept reloading it (also on the V2-1
     Recipe screen). It now asks for the frame's start.
   - Checked with three browser smoke tests on macOS Chrome, and by hand
     on a 250 s local video: cancel from the dialog, start again, the
     result with two Glasses.
9. **Checks — the Windows request is written; waiting on Windows:**
   [2026-10-29-v2-2-analysis-flow-windows-request.md](../40-operations/2026-10-29-v2-2-analysis-flow-windows-request.md)
   (source `0df5ce6`, 72 per-file SHA-256 values; tests
   `140 passed, 3 skipped`).
   - The user, with the Windows agent on the workstation: three new
     inspections on the V2-1 Recipes. SPL#4 with a kept 1 px Accum
     correction; SPL#1 once with no cancel and no correction, for A4;
     SPL#1 again with a cancel, an app close during the analysis and a
     resumed analysis. Also a setup left before "분석 시작", the V2-1
     follow-up (speed field, help, F1) and the frame step in WebView2.
   - `scripts/inspection_summary.py` (new, read-only) prints each
     inspection: its Glass copy against the stored Recipe, the time from
     `created_at` to the cache written (`cache_written`), the cache
     pieces and the source SHA-256 computed again.
   - **A4 in the app:** SPL#1's `cache_written` ≤ 180 s. Over 60 s means
     the app adds work beyond the adapter's 46.4 s; V2-2 still closes, and
     the cause is found before V2-5.
   - The slowest PC is not timed again: the analysis has not changed since
     its run.

**V2-1 follow-up** (built in `30b972c`, `298ab15`): the speed field and the
help dialog (DESIGN.md §4–§5). The user dropped moving the zero line alone
with the keyboard. The mock-ups `design/mockup/editor.html` and
`recipe.html` predate these; DESIGN.md governs where they differ.

## Session handoff — 2026-10-29 (third)

**The session resumed from this handoff** and wrote the step 9 request
(step 9 above). V2-2 steps 1 to 8 are done; step 9 waits on Windows.

**Resume:** read this file, then
[product.md](../10-product/product.md) (§2 now names the slowest target
PC; §3, §4 and §6 changed today),
[architecture.md](../20-architecture/architecture.md) (the web modules),
[inspection-folder.md](../20-architecture/inspection-folder.md),
[DESIGN.md](../../DESIGN.md) §4–§5, the two timing results
([workstation](../60-evidence/2026-10-29-v2-2-analysis-timing-windows-result.md),
[slowest PC](../60-evidence/2026-10-29-v2-2-slowest-pc-timing-windows-result.md))
and the two request styles: the
[V2-1 request](../40-operations/2026-10-29-v2-1-recipe-windows-request.md)
for the Windows agent, and the
[slowest-PC request](../40-operations/2026-10-29-v2-2-slowest-pc-timing-windows-request.md)
for a person in a terminal on a PC without an agent.

**When the step 9 result comes back:** judge it against R1–R15 of the
request, record it in `docs/60-evidence/`, and close V2-2 in the roadmap
if it passes. R11 (how the SPL#1 result screen feels) is recorded only.

**Carried forward:**
- **Speed before V2-5:** the slowest PC takes 169.7 s of 180 s. The
  slowest-PC result lists the candidates: the draft's dynamic
  programming, cheaper medians on that CPU (benchmark there first), and
  converting only the Glass band (PyAV, the user's decision).
- **V2-3:** A5 and A6 on the slowest PC; re-analysing an analysed
  inspection (the API refuses it with 409 until then); the warning when a
  reopened video's SHA-256 differs (A9); the video, zoom and tools on the
  result screen.
- `AnalysisSettings.sample_count` counts to `end_sec`, but the analysis
  stops at the last frame, so it can be one more than the analysis gives
  when the range ends at the video's end. The setup caption counts as the
  analysis does.
- The slowest PC reported Python 3.15.2 instead of 3.14; the picture was
  identical.

**Other notes:**
- `scripts/compare_draft_methods.py` is the diagnostic behind the draft
  decision; it is the only code that reads v1 files.
- `scripts/time_analysis.py` runs the app's analysis adapter stage by
  stage and writes a Markdown result; it is meant for a person in a
  terminal.
- Expected Windows test line: run pytest on macOS without Playwright
  (`sys.modules['playwright'] = None` and
  `sys.modules['playwright.sync_api'] = None`, then `pytest.main`), then
  subtract one passed and add one skipped for the macOS-only Documents
  test. At `0df5ce6`: `141 passed, 2 skipped` on macOS, so
  `140 passed, 3 skipped` on Windows.
- Smoke-test screenshots: set `OLT_SMOKE_SHOTS` to a folder.
- The mock-ups `design/mockup/editor.html` and `recipe.html` predate the
  speed field and the help dialog; DESIGN.md governs where they differ.

## Known limits, accepted for now

- A zero line at the very top or bottom of its ellipse can be moved only
  by typing. At that height its chord is a point under the edge handle.
- There is no Recipe deletion in the first version (user, 2026-10-29).
- The PyInstaller build (V2-5) must ship `src/oil_tracker/web/` as data.
- **A4 has about 10 s to spare on the slowest PC** (169.7 s). Less CPU
  work is due before V2-5; see the step 6 result.
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

- **Done today:** V2-1 closed; V2-2 steps 1 to 8, with the slowest-PC
  timing judged; the step 9 Windows request.
- **Next action:** the user runs the step 9 request on the workstation and
  relays its result block; then judge it (see the handoff above).
