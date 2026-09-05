# Project Roadmap

**Status:** `ACTIVE`

This document is the milestone-order/state SSOT. It is a bounded current-state map, not an execution journal. Exact current S11 authorization, blockers, and next transition live in [`work-plan.md`](work-plan.md).

## Status rules

Allowed formal values are `PLANNED`, `ACTIVE`, `BLOCKED`, `VALIDATING`, `DONE`, `DEFERRED`, and `SUPERSEDED`. `DONE` means implementation, required acceptance, and required merge/publication are complete.

Do not append branch chronology, review logs, test counts, or resolved findings here. Historical detail remains in linked owners, evidence, and Git history.

## Milestone map

| Milestone | Status | Durable result / current boundary |
|---|---|---|
| Phase 1 — Guided Workbench UX | `DONE` | guided setup, recoverable geometry/config editing, validation feedback |
| Phase 2A — Pre-analysis readiness | `DONE` | reusable settings and representative-timestamp readiness/preflight |
| Phase 2B — Result Review Viewer | `DONE` | immutable stored-result review against source video |
| Phase 2C-1..3 — Debug, re-detection and truth | `DONE` | inspectable/replayable detector evidence and exportable regression truth |
| S1 — Detector benchmark foundation | `DONE` | repeatable benchmark/metric/fingerprint foundation |
| S2 — UI raster boundary architecture | `DONE` | Qt presentation no longer owns raster-library behavior |
| S3 — Workbench usability stabilization | `DONE` | accepted real-use layout/terminology/input behavior |
| S4 — Analysis lifecycle/result visualization | `DONE` | stage progress, graph bounds, fonts, lifecycle cleanup |
| S5-A — Foam/shimmer discrimination | `DONE` | bounded multi-evidence Foam discrimination |
| S5-B — Oil-boundary hypothesis architecture | `DONE` | typed observability, bounded temporal owner, fail-closed ambiguity |
| S5-C — Canonical/Qt validation stabilization | `DONE` | deterministic QApplication/headless validation boundaries |
| S6 — Real-video/runtime validation | `DONE` | available-corpus qualification plus bounded/one-hour runtime evidence |
| S7 / Phase 2C-4 — Annotated MP4 Export | `DONE` | stored-result overlay export with bounded publication/cancellation semantics |
| S8 — Repeated-Test Workflow & Result Management | `DONE` | reusable Profile/result workflow and completion/recent-access UX |
| S9 — Operational Recovery & UX Polish | `DONE` | unsaved-change guard, viewport controls, active-target feedback; autosave remains deferred |
| S10 — Windows and Packaging Final Release Gate | `DONE` | target-Windows canonical/package/clean-PC acceptance baseline |
| S11 — Real-Field Detector Effectiveness Recovery | `ACTIVE` | locally accepted behavioral lifecycle/Foam-witness baseline; latest Windows disposition remains `FIELD FAIL`; field qualification outstanding |
| S11-M — Post-S11 Structural Maintainability | `PLANNED` | evidence-backed responsibility cleanup after the active S11 field gate |
| S12 — Post-S10 UI/UX Refinement | `PLANNED` | evidence-led post-detector UX refinement; scope not yet authorized |

## Current sequence

`S1–S10 DONE` → `S11 ACTIVE` → `S11-M / S12 PLANNED`.

S11 does not currently authorize another detector revision automatically. Its exact accepted baseline, non-authorized work, field-risk boundary, and next transition are owned by the [Current Work Plan](work-plan.md).

Affirmatively retained but non-current work is owned by [`retained-commitments.md`](retained-commitments.md). This includes autosave/abnormal-exit recovery, unresolved evidence-gated S11 behavior surfaces, and optional R20 decision-witness observability.

## Detail routers

- current project/gate — [Current Work Plan](work-plan.md)
- product/UX history and durable behavior — [`../10-product/`](../10-product/)
- architecture owners — [`../20-architecture/`](../20-architecture/)
- validation contracts — [`../30-validation/`](../30-validation/)
- completed evidence — [`../60-evidence/`](../60-evidence/)
- superseded historical context — [`../90-archive/`](../90-archive/)