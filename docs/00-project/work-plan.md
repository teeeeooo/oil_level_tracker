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
4. **`application` and `adapters/http`:** loading and saving the edits,
   the derived bands, the source video over HTTP Range, re-analysis, the
   point line (dynamic programming between the user's points) and the
   edge data for the snap.
5. **`web`, the core:** the editor state with undo; grab-and-drag, the
   pencil and range delete; zoom, pan and time-axis input; the playhead;
   the video.
6. **A5 and A6 on the slowest PC:** a terminal request for the user
   (no agent there), with the app timing itself and writing a Markdown
   result.
7. **`web`, the rest:** the point line, the snap, "cannot judge", Foam and
   reference lines, memos, the compressor marker, re-analysis, the save
   question and the SHA-256 warning.
8. **Checks:** unit and API tests, macOS smoke checks, and a Windows run.
   It also covers the V2-2 follow-up.

## Open items

**Before V2-5** (A4 is judged in the app on the slowest PC):
- **Less CPU work in the analysis.** The slowest PC takes 169.7 s of 180 s
  for the adapter. Candidates, from its result: a faster draft (dynamic
  programming), cheaper medians on that CPU (benchmark there first), and
  converting only the Glass band (PyAV, a new dependency: the user's
  decision).
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
  test. At `4f7d493`: `146 passed, 2 skipped` on macOS, so
  `145 passed, 3 skipped` on Windows.
- `scripts/compare_draft_methods.py` is the diagnostic behind the draft
  decision; it is the only code that reads v1 files.
- Smoke-test screenshots: set `OLT_SMOKE_SHOTS` to a folder.
- The mock-ups `design/mockup/editor.html` and `recipe.html` predate the
  speed field and the help dialog; DESIGN.md governs where they differ.

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
- **Next action:** V2-3 step 4, the `application` use cases and the
  `adapters/http` routes for the editor.
