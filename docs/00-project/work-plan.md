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
Product SSOT §3 and §4:
- the app opens on the inspection list; a new inspection takes the video,
  then a Recipe;
- the setup screen sets the range, the compressor start (required only
  with a `RECOVERY` Glass, inside the range) and, if the camera shifted,
  the Glass positions in the inspection's Recipe copy;
- the analysis rate is 2 samples per second, fixed;
- the Oil draft follows the strongest edges as one path (dynamic
  programming), with weak stretches marked "cannot judge";
- after analysis, the result opens read-only in the editor layout. V2-3
  adds editing to that same screen.

**Left to the agent** (user, 2026-10-29):
- the inspection folder `Inspections\YYYYMMDD-HHMM_<video name>\` holds
  `inspection.json`, the Recipe copy `recipe.json` and `cache\`;
- the cache stores each Glass's context image and background view as PNG
  pieces of 4,096 columns, with the times and draft samples in JSON;
- the source SHA-256 is computed on a second thread during the analysis.

**Steps:**
1. **Draft-method comparison** (the user asked for it):
   [2026-10-29-draft-method-comparison.md](../50-diagnostics/2026-10-29-draft-method-comparison.md).
   - **macOS, done:** on the local samples every method with raw edges,
     the spike's and dynamic programming alike, followed static bands and
     hit none of the 27 truth points. Dynamic programming on the
     background view (post-hoc) hit 14. Weakening the obvious fixed bands,
     standing in for v1's fixed-structure templates, hit none.
   - **Windows, waiting:** the user judges A, B, D and F by eye on SPL#4
     and SPL#1:
     [2026-10-29-v2-2-draft-comparison-windows-request.md](../40-operations/2026-10-29-v2-2-draft-comparison-windows-request.md)
     (source `4f58ead`). Its decision table, fixed before the run, sets the
     draft's edge source for step 5.
2. **Mock-ups** of the inspection list and the setup screen, for the
   user's confirmation. The read-only result follows the confirmed editor
   mock-up.
3. **`domain`:** the inspection, the analysis settings, the line samples
   and the "cannot judge" stretches, with validation.
4. **`adapters/storage`:** the inspection folder, the Recipe copy and the
   cache, with a format document in `docs/20-architecture/`.
5. **`adapters/video`:** one pass over the video for every Glass: context
   image, background view and Oil draft, with progress and cancellation.
   Ported from `spike/webui:spikes/webui/context.py`.
6. **`application` and `adapters/http`:** creating an inspection, the
   analysis job (progress, time left, cancel) and the result data.
7. **`web`:** the inspection list, the new-inspection flow, the setup
   screen, progress, and the read-only result (porting the spike's
   `render.js`).
8. **Checks:** unit and API tests, a macOS smoke check, and a Windows run.
   The Windows run also covers:
   - **A4 timing on SPL#1.** The spike took 166 s of the 180 s for one
     Glass; this is the main risk of V2-2;
   - the V2-1 follow-up: the speed field, the help dialog and F1 in
     WebView2. Without Playwright the expected test line stays
     `77 passed, 2 skipped` plus the new tests.

**V2-1 follow-up** (built in `30b972c`, `298ab15`): the speed field and the
help dialog (DESIGN.md §4–§5). The user dropped moving the zero line alone
with the keyboard. The mock-ups `design/mockup/editor.html` and
`recipe.html` predate these; DESIGN.md governs where they differ.

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

- **Next action:**
  - the user runs the draft-comparison Windows request and relays its
    result block;
  - meanwhile, step 2: the mock-ups of the inspection list and the setup
    screen.
