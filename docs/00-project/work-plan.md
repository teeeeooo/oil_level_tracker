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
    (`video`, `storage`, `report`, `http`);
  - `bootstrap.py` is the only wiring point;
  - there is no NumPy in `domain` or `application`;
  - during a drag, the bands and the judgment update from the API after
    release.
- **Visual rules:** [DESIGN.md](../../DESIGN.md), Fluent 2 light.
  - The editor layout in [design/mockup/editor.html](../../design/mockup/editor.html)
    is **confirmed by the user** (2026-10-28).
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
   - the user makes a Recipe from a local sample video.

**Closing V2-1 (to confirm with the user):** a macOS run is enough for V2-1.
Windows confirmation is part of V2-5.

## Left to the user, with no deadline

- deleting `~/Developer/oil_level_tracker-v1-evidence/`;
- deleting branch `spike/webui` once the porting is done.

The three v1 remote branches that v1 docs cite stay.

## Next

- **Done:** steps 1–5.
- **Next action:** step 6, the Recipe screen in `web`.
