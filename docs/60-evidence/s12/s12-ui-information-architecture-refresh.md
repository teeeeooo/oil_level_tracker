# S12 UI Information Architecture Refresh Evidence

## Disposition

The bounded S12 Workbench and Result Review information-architecture refresh is locally complete. It passed source-tree automated regression, compilation, diff checks and same-viewport offscreen visual comparison. Target-Windows real-video and DPI behavior remains an external manual gate; this record does not claim that it passed.

The implementation commits are:

- `fbe8023` — Workbench action hierarchy, empty-state disclosure and shared three-role chrome; and
- `a19fd50` — Result Review progressive disclosure, review-first navigation and user-facing reason projection.

No separate Worker or Auditor was requested for this UI slice. The root implementation session performed the screenshot audit, design reconciliation, implementation and validation directly.

## Audit evidence and findings

Four current screens were captured before implementation and again at matching viewport/state after implementation:

- empty Workbench;
- loaded sample4 Workbench;
- new-Profile wizard; and
- loaded sample4 Result Review.

The local capture sets are `/tmp/oil-ui-audit-current-20260824`, `/tmp/oil-ui-audit-after-20260824` and `/tmp/oil-ui-audit-comparison-20260824`. They are temporary visual-QA artifacts rather than product/runtime resources.

The before-state audit found duplicated top-level Workbench actions, simultaneous ownership/status colors, a disabled full settings form in the empty state, repeated guidance text and a Result Review toolbar/right-detail surface that exposed primary, export, follow-up and developer work at once. The wizard was already comparatively focused and required only the shared visual foundation.

The accepted after-state comparison established:

- a Workbench top-level path of new Profile, Profile open, Result Review and one overflow menu;
- the existing left selection → center current task/video → right contextual settings → lower-right execution flow;
- a concise five-step progress row and compact current-scene summary;
- one empty-state instruction instead of disabled Glass settings;
- neutral, blue-interaction and red-blocking application-chrome roles without green/orange ownership or success fills;
- a Result Review toolbar limited to result open, view mode and one task menu;
- review-required navigation as the general-review default;
- hidden-by-default raw frame details with automatic disclosure for debug work; and
- Korean projection of detector review flags while exact stored codes remain in tooltips/debug surfaces.

Video pixels, detector overlays and graph evidence remain allowed to use additional data colors when labels, shape or line style preserve their meaning. This exception does not reintroduce competing application-chrome state colors.

## Authority preservation

The slice changes Qt presentation and action placement only. It preserves existing Recipe and `.oilrecipe` persistence, `AnalysisSession`, current-run confirmation, readiness, preflight, undo/redo, same-Profile transition, read-only Result Bundle, source-video resolution, export safety, re-detection, user truth, detector and S9 scene-coordinate/zoom/active-target authority.

Detector-oriented flags are projected through `review_reason_label()` only at presentation time. Official tracking samples, flags, review categories, CSV content and bundle provenance are not rewritten.

## Automated validation

Final exact-source checks:

- canonical repository suite: `1,639 passed in 152.21 s`;
- focused Workbench/ownership/interaction suite: `48 passed`;
- focused Result Review/information-architecture suite: `34 passed`;
- preflight/recent-Profile/settings-copy/close-guard selection: `46 passed`;
- Python `compileall` for `src` and `tests`: passed; and
- `git diff --check`: passed.

The new information-architecture tests assert direct-versus-menu action placement, empty-state disclosure, hidden/visible detail transitions, developer action placement, the three semantic chrome color roles and bounded user-facing review-reason vocabulary.

## Remaining external validation

The next proportional UI authority is the maintained Windows checklist at 100%, 125% and 150% display scale with real video. It must verify clipping, menu discoverability, keyboard shortcuts, at-most-three-level task paths, empty/detail disclosure, long Korean paths, Result Review graph stability and S8/S9 lifecycle/geometry non-regression. This UI result remains independent from the pending private-Windows R16 Base/Accum detector gate.
