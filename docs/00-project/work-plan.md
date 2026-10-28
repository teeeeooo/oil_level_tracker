# Current Work Plan

**Current milestone:** `V2-1 — Recipe` / `PLANNED`. It has not started.
**Last completed:** `V2-0 — Start and foundations` / `DONE` (2026-10-28).

This is the sole owner of the current state, authorization and next action.
Rewrite it; do not append to it.

## Accepted baseline

- **Product SSOT:** [product.md](../10-product/product.md).
  - Goal and the acceptance criteria A1–A9.
  - Acceptance videos: SPL#1 and SPL#4.
  - All product decisions.
- **Architecture:** [architecture.md](../20-architecture/architecture.md).
  Feature modules with one-way dependencies; the judgment lives only in
  Python.
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

## Next

- **Next action:** V2-1, the Recipe screen and Recipe file. It starts when
  the user says so.
- **Expected first ports:** `JudgmentRule` and `JudgmentMode` from
  `v1-final:src/oil_tracker/domain/`. The `server.py` bind fix from
  `spike/webui`.
