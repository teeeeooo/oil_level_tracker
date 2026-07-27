# Current Work Plan

- **Document status:** `VALIDATING`
- **Active milestone:** `S5-B — Oil-boundary hypothesis architecture`
- **Branch:** `feature/oil-boundary-temporal-tracking`
- **Task-start exact head:** `7d07844d0d376d755ee6ef4d0d9d8d31a2d0d7f4`
- **Task-start exact parent:** `eaa4abbe841e819ace040c866607f4ef16296b32`
- **Current gate:** Fresh independent S5-B1 exact-head re-audit
- **Last architecture/evidence audit result:** `AUDIT: FAIL`
- **Current state:** Shadow raster ownership isolation repair completed on feature head

This is the operational SSOT for the active milestone. Closeout results follow the [closeout policy](./closeout-policy.md); branch-local completion is not formal `DONE`.

## Problem statement

S5-B replaces brittle candidate/static suppression with immutable observations, bounded semantic proposals, continuous likelihoods and typed temporal reasoning without weakening Foam behavior or changing persisted contracts.

S5-B1 exists beside the unchanged production detector. The independent architecture/evidence audit found one blocking isolation defect: shadow NumPy views were read-only but shared memory with production preprocessing, mask and static-map arrays. A custom runner could mutate a writable base and then fail, causing the legacy detector to consume corrupted production evidence.

## Decision

Keep the accepted [S5-B architecture](../20-architecture/s5b-oil-boundary-hypothesis-architecture.md) and repair only the raster ownership boundary. Every raster passed to the shadow runner is now an independent shadow-owned copy marked read-only before invocation. The legacy oil path and S5-A Foam path remain the sole official authorities.

## Execution stages

1. **Documentation normalization — independently accepted**
   The documentation hierarchy and S5-B architecture contract passed their independent re-audit.
2. **S5-B1 shadow hypothesis pipeline — completed on feature head**
   Immutable observation/proposal/evidence types and bounded typed temporal state remain unchanged.
3. **Shadow raster ownership isolation repair — completed on feature head**
   Production preprocessing, mask and static-map memory is no longer reachable through shadow input base chains.
4. **Fresh independent exact-head re-audit — current stage**
   Re-audit the complete S5-B1 head, with emphasis on adversarial raster mutation and failure isolation.
5. **S5-B2 production cutover — blocked pending re-audit**
   Begin only after the fresh independent re-audit returns `PASS`.
6. **Later validation and merge gates — pending cutover**
   Exact-head audit, controlled comparison, sample probe, canonical validation, final audit and guarded merge remain later stages.

## Current gate

A fresh independent S5-B1 exact-head re-audit must verify:

- every `PreprocessResult` array, effective/ellipse/exclusion mask and static map passed to shadow execution has isolated memory ownership;
- direct assignment, writable-base traversal, `np.asarray`, `setflags(write=True)`, mutation followed by exception and invalid-return fallback cannot alter official output;
- shadow-enabled, shadow-disabled and failure paths preserve official oil/Foam/fill-state/tracker behavior and complete non-shadow debug artifacts;
- detector version, candidate trace, settings, benchmark, result, fixture and debug schemas remain unchanged;
- the repair delta is limited to the detector integration seam, focused regression evidence and required closeout documentation.

## Completed evidence

- The audit defect was reproduced before repair: base-chain mutation changed official fill state and removed the numeric oil boundary.
- Shadow input creation now allocates an independent owning NumPy copy for every current-frame raster and then marks that copy read-only.
- An adversarial runner traverses each base chain, makes the shadow owner writable, mutates all twelve raster inputs including the static map, and raises intentionally.
- After those real mutations, the complete official detection, candidates, non-shadow metrics, debug images, profiles, rows and state remain deeply equal to a fresh shadow-disabled baseline.
- Focused shadow tests passed `25` tests; the required shadow/oil/Foam/benchmark/result/fixture regression command passed `133` tests with no failures or skips on project Python 3.14.4.

## Blocking findings

- The prior shared-memory blocker is repaired on the feature head but is not independently accepted yet.
- S5-B2 remains blocked until the fresh exact-head re-audit returns `PASS`.

## Open risks

- Likelihood calibration, broad/narrow correlation and short-sample static-prior bias remain unresolved.
- Temporal stickiness and reacquisition behavior still require broader sequence evidence.
- Formal CPU cost, controlled comparison, real-video truth, Windows/manual and packaging validation remain deferred gates.
- Namespaced debug instrumentation can drift and remains part of independent audit coverage.

## Explicit non-goals

- No S5-B2 production cutover or algorithm redesign.
- No likelihood, threshold, proposal, deduplication or temporal-behavior change.
- No duplicate-identity or shadow-disabled diagnostic hardening.
- No legacy oil or Foam algorithm change.
- No dependency, detector version, port, settings, recipe, benchmark, result, fixture or debug schema change.
- No formal `DONE`, accuracy acceptance, canonical validation, Windows/package validation or merge claim.

## Next action

Perform a fresh independent S5-B1 exact-head re-audit at the resulting immutable remote head. Do not start S5-B2 unless that re-audit returns `PASS`.

## Latest recorded closeout

- **Repair result:** `SUCCESS`
- **Task-start exact head:** `7d07844d0d376d755ee6ef4d0d9d8d31a2d0d7f4`
- **Task-start exact parent:** `eaa4abbe841e819ace040c866607f4ef16296b32`
- **Audit handoff:** Independent S5-B1 architecture/evidence audit returned `AUDIT: FAIL` for shared raster memory ownership between shadow inputs and production detector evidence.
- **Completed source scope:** Replaced view-only protection with independent owning copies for all shadow preprocessing arrays, masks and optional static map; no shadow algorithm or production authority changed.
- **Completed regression scope:** Added adversarial base-chain traversal, writable mutation and post-mutation exception coverage for all shadow raster inputs, including static-map learning, followed by deep official comparison against a fresh shadow-disabled detector.
- **Validation evidence:** Project Python is 3.14.4; focused shadow suite passed `25` tests and the required adjacent suite passed `133` tests with no failures or skips. Documentation link/newline and Git whitespace checks are part of final closeout verification.
- **Compatibility:** Official oil/Foam/fill-state/tracker behavior, complete candidate/debug projection, detector version and persisted/external schemas remain unchanged; only additive `shadow_oil_*` failure evidence differs as intended.
- **Current gate:** Fresh independent S5-B1 exact-head re-audit. S5-B2 remains prohibited before re-audit `PASS`.
- **Deferred validation:** No controlled comparison, canonical validation, sample/real-video accuracy acceptance, Windows/manual GUI validation, packaging validation, merge or cleanup was performed.
