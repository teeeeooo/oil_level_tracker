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
| V2-2 — Analysis | `ACTIVE` | One video pass, context image, background view, Oil draft, progress, cache |
| V2-3 — Editor | `PLANNED` | Grab/pencil, "cannot judge", lines, memos, zoom/pan/axis input, frame and video |
| V2-4 — Judgment and report | `PLANNED` | Judgment, override with reason, report, submit/lock, versions |
| V2-5 — Windows acceptance | `PLANNED` | One-folder package and the Product SSOT §2 criteria A1–A9 on target Windows |

## Current sequence

`v1 SUPERSEDED` → `V2-0 DONE` → `V2-1 DONE` → `V2-2 ACTIVE` → `V2-3 … V2-5 PLANNED`.

The first version is accepted only at V2-5, against the Product SSOT §2.

## Detail routers

- current step — [work-plan.md](work-plan.md)
- product goal, acceptance and decisions — [../10-product/product.md](../10-product/product.md)
- architecture — [../20-architecture/architecture.md](../20-architecture/architecture.md)
- documentation map — [../README.md](../README.md)
