# Current Work Plan

- **Document status:** `VALIDATING`
- **Active milestone:** `S5-B — Oil-boundary hypothesis architecture`
- **Branch:** `feature/oil-boundary-temporal-tracking`
- **Task-start exact head:** `eaa4abbe841e819ace040c866607f4ef16296b32`
- **Task-start exact parent:** `1256408be65223840ffee113a051ed35bf552257`
- **Current gate:** Independent S5-B1 architecture/evidence audit
- **Last independent documentation/planning gate result:** `AUDIT: PASS`
- **Current state:** S5-B1 completed on feature head; awaiting independent audit

This is the operational SSOT for the active milestone. Closeout results must be reflected according to the [closeout policy](./closeout-policy.md), without requiring a read-only actor to mutate a frozen exact head.

## Exact-head bookkeeping

The header records the task-start identity for the current mutation-capable task. It does not and cannot record the resulting commit SHA inside that same commit. The Worker final report records the resulting exact head and parent, and the next authorized mutation-capable owner updates the task-start identity before making another material change. During an exact-head freeze, do not add a documentation commit merely to copy audit or validation results into the branch.

## Bounded maintenance rules

- This document manages exactly one active milestone and is replaced when the next milestone becomes active.
- Replace Current gate, Next action, Blocking findings and Open risks with the current decision state; do not retain resolved or obsolete entries.
- Keep each execution stage to a short current result and at most one or two explanatory lines.
- Maintain exactly one `Latest recorded closeout` block and replace the whole block at the next mutation-capable closeout.
- Do not append audit logs, validation logs, commit histories or prior closeout blocks.
- Link detailed evidence to architecture, quality, external artifacts or Git history instead of copying it here.
- Create an archive snapshot only by explicit approval when exceptional historical preservation is necessary; do not archive every milestone by default.
- Compact obsolete content during each closeout so document growth is not itself an objective.

## Problem statement

S5-B must reduce oil-boundary position error, false boundaries and temporal contamination without weakening Foam behavior, adding a learned model/GPU dependency or changing persisted schemas.

Repeated narrow repairs to candidate consensus and static suppression did not establish a stable semantic boundary. They treated generator peaks and structural edge groups as if they were already boundary hypotheses, then attempted to recover meaning through increasingly local rejection exceptions. The accepted correction is to preserve immutable observations, construct bounded semantic proposals, retain competing continuous explanations and defer selection to typed current/temporal reasoning.

Historical failed repair heads and the current S5-B1 shadow implementation are evidence stages only. Neither establishes production cutover, accuracy acceptance or formal S5-B completion.

## Decision

Use the architecture defined by [S5-B oil-boundary hypothesis architecture](../20-architecture/s5b-oil-boundary-hypothesis-architecture.md): immutable raw observations, bounded deterministic Y proposals, separate broad/narrow evidence, continuous boundary/artifact/ambiguity likelihoods, soft static priors, deterministic semantic deduplication and typed no-interface/temporal decisions.

S5-B1 implements this architecture beside the unchanged production path. The legacy detector remains the only authority for official `PhaseDetection` values until an independently audited S5-B2 cutover.

## Execution stages

1. **Documentation normalization — independently accepted**
   The normalized hierarchy, exact-head bookkeeping and S5-B architecture contract passed the independent documentation/planning re-audit.
2. **S5-B1 shadow hypothesis pipeline — completed on feature head**
   Immutable observation/proposal/evidence types, typed no-interface output, bounded Glass-local shadow temporal state and runtime comparison evidence are implemented without changing official detector authority.
3. **Architecture/evidence audit — current stage**
   Independently verify type boundaries, evidence preservation, deterministic proposal/dedup behavior, finite bounds, failure isolation and production-output equivalence at the resulting immutable remote head.
4. **S5-B2 production cutover — blocked pending architecture/evidence audit**
   Switch production selection/temporal flow only after independent S5-B1 audit `PASS`; remove replaced legacy ownership in that later bounded task.
5. **Exact-head audit — pending cutover**
   Audit the production cutover at an immutable remote head.
6. **Controlled comparison — pending exact-head audit**
   Compare feature and base under the same environment, dataset and settings; include Foam non-regression and CPU evidence.
7. **Sample-video reference probe — pending controlled evidence**
   Use the repository sample only as supporting architecture evidence, never canonical truth.
8. **Python 3.14 canonical validation — pending prior gates**
   Run the complete required suite on the configured Python 3.14 environment.
9. **Final PR audit and merge — pending canonical validation**
   Perform independent final review and guarded merge only after all earlier gates pass.

## Current gate

The next owner is an independent S5-B1 architecture/evidence Auditor operating on the immutable remote exact head reported by this implementation Worker.

Gate requirements:

- verify that raw observations, proposals, evidence summaries, semantic hypotheses and typed temporal decisions are deeply immutable scalar records;
- verify deterministic stable identity, bounded-diameter proposal construction, deterministic truncation and semantic deduplication;
- verify broad region-step and narrow line/pulse evidence remain separate and unavailable evidence is not represented as zero negative evidence;
- verify continuous boundary/artifact/ambiguity likelihoods, positive typed no-interface evidence and capped soft static priors preserve competing explanations;
- verify Glass-local temporal beam/history/scalar bounds, reacquisition, stale-clear behavior and reset isolation;
- verify shadow execution and injected failure cannot alter official oil/Foam/fill-state/candidate/debug behavior outside the namespaced shadow evidence;
- verify detector version, settings fingerprint, benchmark metrics and persisted/result/fixture/debug schemas remain unchanged;
- verify the complete changed scope, tests, resource instrumentation and documentation at the exact remote head;
- return independent `PASS` before any S5-B2 cutover work begins.

## Acceptance criteria

### Architecture

- Raw edge observations are immutable and remain traceable to their source evidence.
- Proposal diameter, proposal count, scale count, deduplication tolerance and temporal state are explicitly bounded.
- Broad region-step and narrow line/pulse evidence remain separate continuous components.
- Boundary, artifact and ambiguity evidence are not collapsed into an early enum gate.
- Static evidence acts as a soft prior and cannot erase current contradictory evidence.
- No-interface is typed and competes with boundary hypotheses rather than being inferred from candidate absence.
- The external `PhaseDetection` contract and persisted schemas remain compatible.
- Legacy consensus/scorer/no-interface/OilTemporalPath ownership remains production authority during S5-B1 and is removed only after an audited S5-B2 cutover.

### Evidence and validation

- Deterministic tests cover immutable identity, bounded proposals, semantic deduplication, evidence separation, ambiguity preservation, typed no-interface transitions and bounded temporal state.
- Shadow-enabled, shadow-disabled and injected-failure runs preserve official output, Foam state, detector identity, benchmark metrics and settings fingerprints.
- Resource-count instrumentation proves finite per-frame observation/proposal/hypothesis/debug limits and bounded per-Glass temporal state.
- Controlled base/feature comparison, real-video truth acceptance, formal CPU acceptance, canonical validation and Windows/package validation remain later gates.

## Completed evidence

- S1 benchmark foundation and Phase 2C-3 user-truth/fixture export are available.
- S2, S3, S4 and S5-A are complete and form the compatibility baseline.
- The independent documentation/planning re-audit accepted the normalized hierarchy and S5-B architecture contract.
- S5-B1 now provides immutable raw edge observations, bounded proposals, separate broad/narrow evidence, continuous likelihoods, capped static priors, deterministic semantic deduplication, typed current observations and bounded Glass-local temporal decisions.
- `OpenCvPhaseDetector` executes the shadow path on read-only current-frame inputs while the existing legacy oil and S5-A Foam paths remain the sole official output authorities.
- Namespaced bounded runtime/debug evidence compares the shadow projection with the legacy official decision without changing persisted schemas or required output files.

## Blocking findings

- No material S5-B1 implementation blocker is currently recorded.
- S5-B2 production cutover is blocked until the independent S5-B1 architecture/evidence audit returns `PASS` at the resulting immutable remote exact head.
- Production oil authority intentionally remains the legacy consensus/scorer/no-interface/OilTemporalPath flow during this gate.

## Open risks

- Likelihood normalization and decision thresholds remain uncalibrated against broader truth data.
- Broad and narrow evidence can remain correlated under glare, blur and nearby multi-edge structures.
- Short-sample static maps can bias artifact likelihood despite the configured cap and neutral-undercoverage rule.
- Temporal decisions can become sticky or reacquisition can lag on unrepresented motion sequences.
- Shadow execution adds CPU/resource cost; formal CPU acceptance is deferred even though finite bounds are instrumented and adversarially tested.
- Real-video user-truth coverage remains limited until later validation stages.
- Namespaced debug instrumentation can drift from implementation semantics and requires independent audit coverage.

## Explicit non-goals

- No S5-B2 production selection or temporal cutover in this stage.
- No large learned model, checkpoint, CUDA or dedicated-GPU requirement.
- No fixture-ID, filename or single-video hard-coded exception.
- No S5-A redesign, Result Review feature expansion or annotated MP4 implementation.
- No persisted detector setting, recipe/truth/result/benchmark/debug schema or required bundle-file change.
- No claim that the repository sample is canonical truth.
- No `DONE` status before required validation and merge.

## Next action

Perform an independent S5-B1 architecture/evidence audit at the immutable remote exact head reported by this Worker. Do not begin S5-B2 production cutover unless that audit returns `PASS`.

## Latest recorded closeout

- **Implementation result:** `SUCCESS`
- **Task-start exact head:** `eaa4abbe841e819ace040c866607f4ef16296b32`
- **Task-start exact parent:** `1256408be65223840ffee113a051ed35bf552257`
- **Documentation/planning handoff:** The independent re-audit returned `AUDIT: PASS`, allowing bounded S5-B1 source implementation to begin.
- **Completed source scope:** Added four cohesive shadow owners for immutable scalar types/bounds, raw observation and semantic evidence construction, bounded typed temporal state and orchestration/debug projection; minimally integrated the shadow runner beside the unchanged production detector path.
- **Completed test scope:** Added focused immutable identity, proposal-bound, broad/narrow evidence, static-prior, semantic-dedup, typed no-interface, temporal-state and production-isolation tests. The focused and listed adjacent oil/Foam/benchmark/result/fixture regression command passed `132` tests with no failures or skips.
- **Production isolation:** Fresh enabled/disabled and injected-failure detector instances produced identical official fill state, raw/smoothed oil and Foam positions, confidence, zero-line projection, flags, candidate scalar snapshots, legacy debug metrics, artifacts and tracker/Foam behavior after excluding the additive `shadow_oil_*` namespace. Detector version, benchmark cases/aggregates/settings fingerprints and external persistence contracts remained unchanged.
- **Resource evidence:** Per-frame observations, scales, proposal diameter/members/count, semantic hypotheses and debug scalars are explicitly capped; Glass-local temporal beam/history/scalar state is bounded and retains no frame, mask, raster profile, array or mutable candidate.
- **Current gate:** Independent S5-B1 architecture/evidence audit at the resulting immutable remote exact head. S5-B2 remains prohibited before audit `PASS`.
- **Unresolved risks:** Likelihood calibration, broad/narrow correlation, static-prior bias, temporal stickiness/reacquisition, formal CPU cost, limited real-video truth and debug instrumentation drift remain open.
- **Validation not performed:** No S5-B2 cutover, controlled base/feature comparison, sample-video accuracy acceptance, real-video truth acceptance, full canonical validation, Windows GUI/manual validation, PyInstaller packaging validation, final exact-head/PR audit or merge was performed.
