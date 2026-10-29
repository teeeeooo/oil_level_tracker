# Current Work Plan

**Current milestone:** `V2-1 — Recipe` / `ACTIVE` (started 2026-10-29).
**Last completed:** `V2-0 — Start and foundations` / `DONE` (2026-10-28).

This is the sole owner of the current state, authorization and next action.
Rewrite it; do not append to it.

## Accepted baseline

- **Product SSOT:** [product.md](../10-product/product.md).
  - Goal and the acceptance criteria A1–A9.
  - Acceptance videos: SPL#1 and SPL#4.
  - All product decisions.
- **Architecture:** [architecture.md](../20-architecture/architecture.md).
  The judgment lives only in Python. On 2026-10-29 the user switched to
  v1-style layers:
  - `domain` ← `application` (use cases and ports) ← `adapters`
    (`video`, `storage`, `report`, `http`, `desktop`);
  - `bootstrap.py` is the only wiring point;
  - there is no NumPy in `domain` or `application`;
  - during a drag, the bands and the judgment update from the API after
    release.
- **Visual rules:** [DESIGN.md](../../DESIGN.md), Fluent 2 light.
  - The editor layout in [design/mockup/editor.html](../../design/mockup/editor.html)
    is **confirmed by the user** (2026-10-28).
  - The Recipe layout in [design/mockup/recipe.html](../../design/mockup/recipe.html)
    is **confirmed by the user** (2026-10-29).
- **Documentation:** the v1 conventions, per [docs/README.md](../README.md).
  - numbered folders;
  - the date catalog and its pre-push check;
  - the roadmap and the execution policy;
  - the recall index.
- **The repository holds only v2.**
  - v1 is at tag `v1-final` and branch `archive/v1`.
  - v1 local evidence is at `~/Developer/oil_level_tracker-v1-evidence/`.
  - Branch `spike/webui` is kept for porting.

## V2-1 — Recipe

**The start decisions are settled** (2026-10-29) and recorded in the Product
SSOT:
- the Recipe contents and reference frame, §3;
- the judgment rule, §5;
- the data folder and the Recipe copy, §8.

**Steps:**
1. **`domain`.**
   - `JudgmentMode`, `JudgmentRule`, Glass geometry, the reference frame and
     `Recipe`, with validation.
   - Adapted ports from `v1-final:src/oil_tracker/domain/` (`enums.py`,
     `recipe.py`, `geometry.py`).
   - The judgment computation itself (`judge_samples`) waits for V2-4.
2. **`adapters/storage`:** the data folder and the Recipe files.
   - `.recipe.json` with a schema version;
   - atomic writes;
   - the Recipe list.
3. **Recipe screen layout.** Added to [DESIGN.md](../../DESIGN.md) §4–§5,
   with the static mock-up
   [design/mockup/recipe.html](../../design/mockup/recipe.html).
   **Confirmed by the user** (2026-10-29), with two changes: the frame on
   screen at save becomes the reference, and the Glass editing follows v1.
4. **`adapters/video`:** video metadata, a frame at a given time, and a
   downscaled JPEG.
5. **The app shell:**
   - the `application` use cases;
   - `adapters/http`, with the `server.py` bind fix from `spike/webui`;
   - `bootstrap.py` and `app.py`.
6. **`web`:** the Recipe screen.
7. **Checks:**
   - unit and API tests;
   - a Playwright smoke check on macOS;
   - **a Windows run** (the user has no macOS access now):
     [2026-10-29-v2-1-recipe-windows-request.md](../40-operations/2026-10-29-v2-1-recipe-windows-request.md).
     The user makes the SPL#4 and SPL#1 Recipes there; they stay for V2-2.

**Closing V2-1:** the Windows run passes R1–R12, judged in
`docs/60-evidence/`.

## Session handoff — 2026-10-29

**The session closed after `607bccb`,** with this handoff commit on top. The
working tree is clean, and `main` and the remote are in sync.

**Resume:** read this file, then
[product.md](../10-product/product.md),
[architecture.md](../20-architecture/architecture.md),
[DESIGN.md](../../DESIGN.md) and the
[Windows request](../40-operations/2026-10-29-v2-1-recipe-windows-request.md).

**What this session settled.** The owners hold the details; Git has the
commits.
1. **Architecture:** v1-style layers (`829fa68`). It adds the `desktop`
   adapter. A test enforces the dependency rule
   (`tests/test_architecture.py`).
2. **Product decisions:** the Recipe, the judgment rule and the data folder
   (`66d8f2b`, `4120efa`); see Product SSOT §3, §5 and §8.
   - `allowed_sec` defaults to 5 s, against the longest continuous
     violation.
   - Only Oil feeds the judgment.
   - The frame on screen at save becomes the reference frame.
3. **Design:** the Recipe screen layout is confirmed. The Glass editing
   follows v1. DESIGN.md gained:
   - frame-chrome, validation and `--glass-shadow` tokens;
   - the field-error rule.
4. **Code, steps 1–6:**
   - `domain`;
   - `adapters/storage` (format in
     [recipe-file.md](../20-architecture/recipe-file.md));
   - `adapters/video`;
   - the use cases, the HTTP API, `bootstrap.py` and `app.py`;
   - the web Recipe list and screen.

   **79 tests:** unit, API, and a Playwright smoke check in macOS Chrome.

**Waiting:** the user's Windows result for the request (source `4ea7ade`).

**When the result arrives:**
1. **Identify the run** by R1 (`checked=41 mismatched=0`) and the
   environment lines.
   - The text is relayed by OCR, so labels and digits can slip.
   - Recheck any derived value against the listed rows.
2. **Judge R1–R12** only against the request's fixed criteria.
   - R8: `t` in the `SPL#4 냉각` line against the time the user noted.
   - R10: compare the two `video` lines' `size`.
3. **Record the judgment** in
   `docs/60-evidence/YYYY-MM-DD-v2-1-recipe-windows-result.md`, with a
   catalog row. Include:
   - the judgment modes the user chose for SPL#4 BASE/Accum and SPL#1
     BASE;
   - the user's comments.
4. **If everything passes:**
   - mark V2-1 `DONE` in the [roadmap](roadmap.md) and here;
   - V2-2 then starts when the user says so.
5. **If anything fails:**
   - fix it;
   - send a short follow-up request that names the new head;
   - recheck only the affected items.

**First seen on Windows in this run:**
- the Documents known-folder API (`adapters/storage/locations.py`);
- the WebView2 file dialog, called from the HTTP thread (`app.py`);
- `os.startfile` for "폴더 열기".

**Known limits, accepted for now:**
- A zero line at the very top or bottom of its ellipse can be moved only
  by typing. At that height its chord is a point under the edge handle.
- Frame stepping uses `,` and `.`, because the arrow keys move the Glass.
- There is no Recipe deletion in the first version (user, 2026-10-29).
- The PyInstaller build (V2-5) must ship `src/oil_tracker/web/` as data.

**Local environment (macOS):**
- `.venv` is the old v1 venv.
  - It now also has `pywebview==6.2.1` and `playwright` 1.64.1.
  - The v2 package is not installed in it. Run the app with
    `PYTHONPATH=src .venv/bin/python -m oil_tracker`; pytest finds `src`
    through `pyproject.toml`.
- The smoke test drives the system Chrome (`channel="chrome"`).
- Mock-up screenshots come from headless Chrome. The in-app browser pane
  cannot open `file://`.

**To settle with the user at the V2-2 start:**
- the inspection-folder layout, including where the Recipe copy goes;
- the analysis setup screen (range, compressor start), and whether it needs
  a mock-up;
- the analysis rate (the spike used 2 fps) and the context-image cache
  format;
- the porting of the spike's `context.py` (context image, background view,
  draft).

## Left to the user, with no deadline

- deleting `~/Developer/oil_level_tracker-v1-evidence/`;
- deleting branch `spike/webui` once the porting is done.

The three v1 remote branches that v1 docs cite stay.

## Next

- **Done:** V2-1 steps 1–6, and the automated part of step 7.
- **Next action:** the user runs the Windows request and relays its result
  block. Judge it as above.
