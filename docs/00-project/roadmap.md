# Project Roadmap

**Status:** `ACTIVE`

This document is the milestone-order and milestone-state SSOT.
- The exact current step, its blockers and the next transition live in
  [work-plan.md](work-plan.md).
- What each milestone must achieve lives in the
  [Product SSOT](../10-product/product.md).

## Status rules

- **Allowed values:** `PLANNED`, `ACTIVE`, `BLOCKED`, `VALIDATING`, `DONE`,
  `DEFERRED` and `SUPERSEDED`.
- **`DONE`** means implementation, the required acceptance and the required
  publication are all complete.
- **Keep it a map.** Do not append branch chronology, test counts or review
  logs here.

## Milestone map

| Milestone | Status | Result / boundary |
|---|---|---|
| v1 (Phases 1–2, S1–S11) | `SUPERSEDED` | Automatic-detector application. S11 was frozen as unmet on 2026-10-28. Preserved at tag `v1-final` and branch `archive/v1` |
| V2-0 — Start and foundations | `DONE` | S11 freeze, v1 tag and archive, `main` reset, `DESIGN.md`, a confirmed editor mock-up, Product SSOT, architecture, documentation structure |
| V2-1 — Recipe | `DONE` | Recipe screen and file: Glass ellipse, zero line, judgment rule |
| V2-2 — Analysis | `DONE` | One video pass, context image, background view, Oil draft, progress, cache |
| V2-3 — Editor | `DONE` | Grab/pencil, "cannot judge", lines, memos, zoom/pan/axis input, frame and video |
| V2-4 — Judgment and report | `DONE` | Judgment, override with reason, report, submit/lock, versions |
| V2-4b — Video window and pattern copy | `DONE` | The user's additions for the first version (2026-11-02): the source video at full size in its own window; copying and pasting a stretch of the Oil and Foam lines |
| V2-5 — Windows acceptance | `DONE` | One-folder package and the Product SSOT §2 criteria A1–A9 on target Windows |
| P-1 — Introduction video | `ACTIVE` | A short video that introduces the app (user, 2026-11-02); [storyboard](../40-operations/intro-video.md) |
| P-2 — User manual | `PLANNED` | How to use the app, as HTML or another fitting form (user, 2026-11-02) |
| P-3 — Field-use fixes | `PLANNED` | Problems found once inspectors use the first version (user, 2026-11-02) |

## Current sequence

`v1 SUPERSEDED` → `V2-0 DONE` → `V2-1 DONE` → `V2-2 DONE` → `V2-3 DONE` → `V2-4 DONE` → `V2-4b DONE` → `V2-5 DONE` → `P-1 ACTIVE` → `P-2 PLANNED` → `P-3 PLANNED`.

The first version is accepted only at V2-5, against the Product SSOT §2. **It was accepted on 2026-11-02** ([re-check](../60-evidence/2026-11-02-v2-5-recheck-windows-result.md), on the build of `8448e79`).

## Detail routers

- current step — [work-plan.md](work-plan.md)
- product goal, acceptance and decisions — [../10-product/product.md](../10-product/product.md)
- architecture — [../20-architecture/architecture.md](../20-architecture/architecture.md)
- documentation map — [../README.md](../README.md)
