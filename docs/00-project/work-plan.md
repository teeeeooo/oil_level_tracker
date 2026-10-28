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

## Session handoff — 2026-10-28

**The session closed at `ea570e0`.** The working tree is clean, and `main`
and the remote are in sync.

**What this session settled:**
1. The web UI spike was GO on Windows.
2. The v2 product decisions were interviewed and recorded.
3. V2 started:
   - S11 frozen as unmet;
   - `v1-final` and `archive/v1` created;
   - the merged remote branches deleted;
   - the v1 local evidence moved out of the repository;
   - `main` reset to the v2 skeleton.
4. `DESIGN.md` and the confirmed editor mock-up.
5. The Product SSOT with A1–A9, the architecture, and the documentation
   structure.

**Resume:** read this file, then
[product.md](../10-product/product.md),
[architecture.md](../20-architecture/architecture.md) and
[DESIGN.md](../../DESIGN.md). Do not start V2-1 until the user says so.

**Questions to settle with the user at the V2-1 start:**
- Which v1 `JudgmentRule` fields v2 keeps. v1 had:
  - `recovery_limit_sec`, `stable_hold_sec`;
  - `minimum_valid_coverage_ratio`;
  - `allowed_excursion_*`, `allowed_violation_*`;
  - `unknown_policy`.
- **The Recipe file:** its format, where it lives, and how it is picked when
  an inspection starts.
- **The reference frame:** which video frame the Glass ellipse and zero line
  are drawn on in the Recipe screen.

**Left to the user, with no deadline:**
- deleting `~/Developer/oil_level_tracker-v1-evidence/`;
- deleting branch `spike/webui` once the porting is done.

The three v1 remote branches that v1 docs cite stay.

## Next

- **Next action:** V2-1, the Recipe screen and Recipe file. It starts when
  the user says so.
- **Expected first ports:** `JudgmentRule` and `JudgmentMode` from
  `v1-final:src/oil_tracker/domain/`. The `server.py` bind fix from
  `spike/webui`.
