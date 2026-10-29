# Current Work Plan

**Current milestone:** none active. `V2-2 — Analysis` / `PLANNED` starts when
the user says so.
**Last completed:** `V2-1 — Recipe` / `DONE` (2026-10-29).

This is the sole owner of the current state, authorization and next action.
Rewrite it; do not append to it.

## Accepted baseline

- **Product SSOT:** [product.md](../10-product/product.md).
  - Goal and the acceptance criteria A1–A9.
  - Acceptance videos: SPL#1 and SPL#4.
  - All product decisions, including the Recipe (§3), the judgment rule
    (§5) and the data folder (§8), settled on 2026-10-29.
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

## V2-1 follow-up (user, 2026-10-29)

The user's requests from the Windows run are settled and built (`30b972c`,
`298ab15`); DESIGN.md §4–§5 holds the rules.
- **Speed field:** type any speed from 0.1× to 16×, or pick 0.5×–4× from
  its menu. The same control replaces the editor's 1× 4× 16× segmented
  control.
- **Help:** a "?" button on every toolbar; F1 or `?` opens an overlay
  dialog. Inline hints stay only where they must be read every time; the
  frame header's mouse and key hint moved into the help.
- **Dropped by the user:** moving the zero line alone with the keyboard.
- **Not yet on Windows:** F1 in WebView2, the speed field and the help
  dialog. Add them to the next Windows request (V2-2). Without Playwright
  the expected test line stays `77 passed, 2 skipped`.
- The mock-ups `design/mockup/editor.html` and `recipe.html` predate this.
  DESIGN.md governs where they differ.

## Known limits, accepted for now

- A zero line at the very top or bottom of its ellipse can be moved only
  by typing. At that height its chord is a point under the edge handle.
- There is no Recipe deletion in the first version (user, 2026-10-29).
- The PyInstaller build (V2-5) must ship `src/oil_tracker/web/` as data.

## To settle with the user at the V2-2 start

- the inspection-folder layout, including where the Recipe copy goes;
- the analysis setup screen (range, compressor start), and whether it needs
  a mock-up;
- the analysis rate (the spike used 2 fps) and the context-image cache
  format;
- the porting of the spike's `context.py` (context image, background view,
  draft).

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

- **Next action:** V2-2 starts when the user says so; settle the questions
  above first.
