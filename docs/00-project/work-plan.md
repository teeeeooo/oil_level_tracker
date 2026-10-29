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
2. **A4 timing, before the screens.** SPL#1 BASE's context build took
   202.1 s on Windows, over the 180 s for the whole analysis.
   - **Done on macOS:** the row median was most of that time
     (`numpy.nanmedian`); sorting each row gives the same values about ten
     times faster. The analysis core of step 6 is built ahead for the
     timing (`adapters/video/context.py`, `draft.py`, `fc3feec`); it
     matches the comparison script on the local samples.
   - **Windows, waiting:**
     [2026-10-29-v2-2-analysis-timing-windows-request.md](../40-operations/2026-10-29-v2-2-analysis-timing-windows-request.md)
     (source `f330e62`, a commit ZIP). Its table, fixed before the run,
     decides whether the screens wait for more speed and whether hardware
     decoding becomes the default.
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
6. **`adapters/video`:** one pass over the video for every Glass: context
   image, background view and Oil draft, with progress and cancellation.
   Ported from `spike/webui:spikes/webui/context.py`. The core is built
   (step 2); the ports, cancellation and the domain samples remain.
7. **`application` and `adapters/http`:** creating an inspection, the
   analysis job (progress, time left, cancel) and the result data.
8. **`web`:** the inspection list, the new-inspection flow, the setup
   screen, progress, and the read-only result (porting the spike's
   `render.js`).
9. **Checks:** unit and API tests, a macOS smoke check, and a Windows run.
   The Windows run also covers:
   - **A4 timing on SPL#1** with the whole analysis;
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

**Waiting:** the user's A4 timing result (source `f330e62`).

**When it arrives:**
1. **Identify the run** by R1 (`checked=46 mismatched=0`), R2
   (`87 passed, 2 skipped`) and the environment lines. The text is
   relayed, so labels and digits can slip; recheck derived values.
2. **Judge T1–T3** only against the request's fixed table.
   - T1, SPL#1 software decoding, `analysis total`: ≤ 150 s, go on; 150–180
     s, go on and look for more speed in step 6; > 180 s, speed up before
     the screens.
   - T2 makes hardware decoding the default only if `hardware_used=True`,
     it is at least 10 % faster than T1, and each Glass `mean` is within
     1.0 of T1's. Then pass `hardware=True` from the analysis adapter.
   - Compare `pass` (`grab`, `retrieve`, `reduce`) with the 202.1 s of the
     draft comparison to see where the time went.
3. **Record it** in
   `docs/60-evidence/YYYY-MM-DD-v2-2-analysis-timing-windows-result.md`,
   with a catalog row, and update step 2 here.

**Step 6, as planned:**
- **The analysis port** (in `application/ports.py`): given the video path,
  the Recipe copy's ellipses and the settings, return the times, each
  Glass's draft as a domain `Line` (`adapters/video/draft.py:draft_line`)
  and its images as `GlassImages` (PNG pieces as bytes). It reports
  progress (done and total frames) and checks a cancel flag between
  frames.
- **The PNG pieces** move from `scripts/time_analysis.py:png_pieces` into
  `adapters/video`; the script then imports them.
- **The SHA-256** is computed on a second thread during the pass, as the
  timing script does.

**Step 7, as planned:**
- **Use cases:** list inspections; pick a video and list the Recipes that
  fit it; check a setup (`domain/inspection.py:setup_problems`); start an
  analysis, which creates the folder with the Recipe copy, then sets
  `ANALYSED` or `FAILED` (cancel clears the cache and keeps
  `NOT_ANALYSED`); load the stored analysis.
- **HTTP:** the job runs on a thread in `adapters/http`; the UI polls the
  progress and the time left, and can cancel. Image pieces are served by
  inspection, Glass, kind and index.

**Other notes:**
- `scripts/compare_draft_methods.py` is the diagnostic behind the draft
  decision; it is the only code that reads v1 files.
- Expected Windows test line: run pytest on macOS without Playwright
  (`sys.modules['playwright'] = None` and
  `sys.modules['playwright.sync_api'] = None`, then `pytest.main`), then
  subtract one passed and add one skipped for the macOS-only Documents
  test. At `5aadd35`: `113 passed, 1 skipped` on macOS, so
  `112 passed, 2 skipped` on Windows.
- The mock-ups `design/mockup/editor.html` and `recipe.html` predate the
  speed field and the help dialog; DESIGN.md governs where they differ.

## Known limits, accepted for now

- A zero line at the very top or bottom of its ellipse can be moved only
  by typing. At that height its chord is a point under the edge handle.
- There is no Recipe deletion in the first version (user, 2026-10-29).
- The PyInstaller build (V2-5) must ship `src/oil_tracker/web/` as data.

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

- **Done today:** V2-1 closed; V2-2 steps 1, 3, 4 and 5, and the analysis
  core of step 6.
- **Next action:** judge the A4 timing result when the user relays it;
  then step 6 and step 7 as planned above.
