# Current Work Plan

- **Document status:** `VALIDATING`
- **Active milestone:** `S5-B — Oil-boundary hypothesis architecture`
- **Branch:** `feature/oil-boundary-temporal-tracking`
- **Task-start exact head:** `f8ad80f69ecbab4033725f61ab6a8afbed7f15e5`
- **Task-start exact parent:** `7d07844d0d376d755ee6ef4d0d9d8d31a2d0d7f4`
- **Last S5-B1 re-audit result:** `AUDIT: PASS`
- **Current gate:** Independent S5-B2 exact-head production-cutover audit
- **Current state:** S5-B2 typed oil-hypothesis production cutover completed on feature head

This is the operational SSOT for the active milestone. Closeout results follow the [closeout policy](./closeout-policy.md); branch-local completion is not formal `DONE`.

## Problem statement

S5-B replaces the legacy scalar candidate/consensus/scorer/no-interface/path chain with immutable edge observations, bounded semantic hypotheses, typed current observations and bounded temporal decisions while preserving the external detector contract and the independently owned S5-A Foam path.

S5-B1 established and independently accepted the typed pipeline. S5-B2 must make that pipeline the single production authority without retaining a legacy fallback or allowing compatibility projections to become selection inputs.

## Current decision

`OpenCvPhaseDetector.detect()` now obtains every official oil boundary, no-interface decision, confidence, temporal acceptance and smoothing-clear instruction from the typed hypothesis pipeline. The legacy oil generator, consensus, scorer, no-interface evaluator and `OilTemporalPath` remain historical standalone code only and are not imported, constructed or called by production detection.

The existing `PhaseDetection`, Recipe/settings persistence, user-truth, regression fixture, result bundle, tracking/events CSV and debug trace schemas remain unchanged. Official oil candidate rows are deterministic compatibility projections from immutable semantic hypotheses and provenance. S5-A Foam detection and Foam temporal gating remain separate production owners.

## Current gate

A fresh independent S5-B2 exact-head cutover audit must verify:

- typed observation → proposal → semantic evidence → typed current observation → typed temporal decision is the sole official oil flow;
- no prohibited legacy oil owner, legacy state or fallback influences production selection;
- accepted boundary, no-interface, ambiguity, unavailable and reacquisition-pending decisions project correctly to `PhaseDetection` and `TemporalTracker`;
- official candidate/debug rows are deterministic, finite, JSON-safe and provenance-based, with no `oil_consensus`, raw-generator or legacy-comparison truth;
- S5-A Foam behavior, external/persisted schemas, detector identity and bounded resource contracts remain compatible;
- the complete cutover delta and focused evidence are sufficient before controlled comparison begins.

Controlled base/feature comparison remains blocked until this independent audit returns `PASS` on the immutable resulting head.

## Completed scope on feature head

- Replaced the legacy production oil decision chain with the typed S5-B pipeline.
- Added a one-way typed-to-`PhaseDetection` candidate/debug/result projection.
- Mapped typed no-interface evidence and compatible prior state to full, empty or review output without a numeric boundary.
- Preserved accepted Foam authority when the oil path is absent, ambiguous, unavailable or pending.
- Removed shadow-versus-legacy comparison metrics from production truth and changed runtime metrics to production hypothesis evidence.
- Updated detector/reporting identity to distinguish the typed production algorithm.
- Replaced legacy implementation-detail integration expectations with equivalent typed-production behavior tests while retaining standalone legacy module tests.

## Validation evidence

Project `.venv` uses Python 3.14.4 with pytest 9.1.1. Focused typed production tests cover single authority, boundary projection, no-interface mapping, smoothing clear, ambiguity, failure, invalid return, reacquisition pending, raster isolation, deterministic provenance, Glass-local reset and benchmark identity. The final required oil, Foam, benchmark, settings, result-bundle, regression-fixture, debug trace/CSV and automated debug-viewer compatibility scope passed `226` tests on the feature worktree.

This evidence is implementation validation only. It is not controlled comparison, canonical validation, real-video accuracy acceptance, Windows/manual GUI validation or packaging validation.

## Blocking findings

- No implementation blocker is currently recorded on the Worker head.
- The cutover is not independently accepted until the exact-head audit returns `PASS`.
- Controlled comparison remains blocked until that audit passes.

## Open risks

- Broad transition and narrow artifact likelihood calibration still requires controlled dataset evidence.
- Full/empty projection remains sensitive to camera exposure and compatible prior state.
- Rapid movement, dropout and reacquisition behavior requires sequence-level controlled comparison.
- CPU and long-duration memory acceptance, real-video truth, Windows/manual workflow and packaging remain later gates.

## Explicit non-goals

- No persisted schema, domain port, `PhaseDetection`, result bundle, CSV, truth, fixture or debug trace schema change.
- No dependency or environment mutation.
- No S5-A Foam algorithm or Foam temporal ownership change.
- No broad historical legacy-code cleanup.
- No controlled comparison, canonical validation, sample/real-video accuracy acceptance, Windows/manual GUI validation, packaging validation, merge or branch cleanup.
- No formal `DONE` claim.

## Next action

Perform an independent S5-B2 exact-head production-cutover audit. If and only if that audit returns `PASS`, proceed to controlled base/feature comparison on the same immutable head.

## Latest recorded closeout

- **Worker result:** S5-B2 typed oil-hypothesis production cutover completed on feature head.
- **Task-start exact head:** `f8ad80f69ecbab4033725f61ab6a8afbed7f15e5`
- **Task-start exact parent:** `7d07844d0d376d755ee6ef4d0d9d8d31a2d0d7f4`
- **Prior gate:** Independent S5-B1 exact-head re-audit returned `AUDIT: PASS`.
- **Completed source scope:** Single typed oil production authority, compatibility projection, fill-state/status mapping, detector/debug integration and detector identity update.
- **Compatibility:** External detector and persisted/result/fixture/debug schemas remain unchanged; S5-A Foam owners remain unchanged.
- **Current gate:** Independent S5-B2 exact-head production-cutover audit.
- **Deferred gates:** Controlled comparison, canonical validation, sample/real-video accuracy acceptance, Windows/manual GUI validation, packaging validation, merge and cleanup were not performed.
