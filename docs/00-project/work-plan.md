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
8. **`web`:** the inspection list, the new-inspection flow, the setup
   screen, progress, and the read-only result (porting the spike's
   `render.js`).
9. **Checks:** unit and API tests, a macOS smoke check, and a Windows run.
   The Windows run also covers:
   - **A4 timing on SPL#1** with the whole analysis;
   - if the analysis got less CPU work by then (the slowest-PC result's
     candidates 1 and 2), the user times the slowest PC again with
     `scripts/time_analysis.py`;
   - the V2-1 follow-up: the speed field, the help dialog and F1 in
     WebView2.
   - The expected Windows test line is the macOS run without Playwright
     (see the handoff) minus the macOS-only Documents test.

**V2-1 follow-up** (built in `30b972c`, `298ab15`): the speed field and the
help dialog (DESIGN.md §4–§5). The user dropped moving the zero line alone
with the keyboard. The mock-ups `design/mockup/editor.html` and
`recipe.html` predate these; DESIGN.md governs where they differ.

## Session handoff — 2026-10-29 (second)

**The session closed after `5aadd35`,** with this handoff commit on top.
The working tree is clean, and `main` and the remote are in sync.

**Resume:** read this file, then
[product.md](../10-product/product.md) (§3, §4, §6 changed today),
[architecture.md](../20-architecture/architecture.md),
[inspection-folder.md](../20-architecture/inspection-folder.md),
[DESIGN.md](../../DESIGN.md) §4–§5 (the inspection screens) and the
[A4 timing request](../40-operations/2026-10-29-v2-2-analysis-timing-windows-request.md).

**Since then:** the A4 result came in after the compaction and is judged
(step 2). The user named the slowest target PC (Product SSOT §2); step 6
is done, and its timing on that class is judged (step 6). Nothing waits
on Windows.

**Step 8, next:** the screens in DESIGN.md §5 over the step 7 routes:
- the inspection list as the first screen (the Recipe list gets
  "← 검사 목록");
- the new-inspection flow: the file dialog, the Recipe picker, then the
  setup screen with the Recipe screen's frame view and Glass editing;
- the progress dialog, polling the job;
- the read-only result in the editor layout, porting the spike's
  `render.js` (`spike/webui:spikes/webui/static/render.js`).

**Other notes:**
- `scripts/compare_draft_methods.py` is the diagnostic behind the draft
  decision; it is the only code that reads v1 files.
- Expected Windows test line: run pytest on macOS without Playwright
  (`sys.modules['playwright'] = None` and
  `sys.modules['playwright.sync_api'] = None`, then `pytest.main`), then
  subtract one passed and add one skipped for the macOS-only Documents
  test. At `e9441be`: `140 passed, 1 skipped` on macOS, so
  `139 passed, 2 skipped` on Windows.
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

- **Done today:** V2-1 closed; V2-2 steps 1 to 7, with the slowest-PC
  timing judged.
- **Next action:** step 8 as above.
