# Current Work Plan

- **Document status:** `VALIDATING`
- **Active milestone:** `S5-B — Oil-boundary hypothesis architecture`
- **Branch:** `feature/oil-boundary-temporal-tracking`
- **Current exact head:** `7ac6c5da7289ad53662caf43447b5cf3a8c10476`
- **Current exact parent:** `73e9cd3d6562ba65126f4cd74574f3289f1dd9ad`
- **Current gate:** Independent documentation and planning audit
- **Last closeout result:** `SUCCESS`
- **Current state:** Documentation and planning audit

This is the operational SSOT for the active milestone. Closeout results must be reflected according to the [closeout policy](./closeout-policy.md), without requiring a read-only actor to mutate a frozen exact head.

## Exact-head bookkeeping

The header records the authoritative branch head at the start of the current mutation-capable task. After that task creates a commit, the Worker final report records the resulting exact head and parent. The next authorized mutation-capable closeout owner updates this header before making another material change. During an exact-head freeze, documentation is not changed merely to copy audit or validation results into the branch.

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

Repeated narrow repairs to candidate consensus and static suppression did not establish a stable semantic boundary. They treated generator peaks and structural edge groups as if they were already boundary hypotheses, then attempted to recover meaning through increasingly local rejection exceptions. The sequence produced alternating failures: real boundaries were suppressed, undercovered static survivors remained, multi-edge structures collapsed incorrectly, and candidate-local exceptions still depended on brittle intermediate grouping.

The failed repair heads are historical evidence only. They are not completion results and do not make S5-B `DONE`.

## Decision

Stop narrow candidate/static suppression repair. Replace it with the architecture defined by [S5-B oil-boundary hypothesis architecture](../20-architecture/s5b-oil-boundary-hypothesis-architecture.md): immutable raw observations, bounded deterministic Y proposals, continuous evidence likelihoods, soft static priors, typed no-interface/temporal hypotheses and deterministic semantic deduplication.

## Execution stages

1. **Documentation normalization — completed on feature head**
   The document hierarchy, roadmap, work plan, closeout policy and S5-B architecture contract are present on the feature branch and await independent audit.
2. **S5-B1 shadow hypothesis pipeline — awaiting documentation audit**
   Implement the new typed pipeline beside production behavior only after the current gate passes. Record comparable evidence without changing external `PhaseDetection` results.
3. **Architecture/evidence audit — pending shadow implementation**
   Independently verify type boundaries, deterministic proposals/deduplication, evidence preservation and resource bounds.
4. **S5-B2 production cutover — pending architecture audit**
   Switch production selection/temporal flow to the audited hypothesis pipeline and remove replaced legacy ownership.
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

An independent documentation and planning audit must pass before S5-B1 implementation begins.

Gate requirements:

- review the normalized hierarchy and authoritative ownership independently;
- verify roadmap status against merged project history;
- verify the work-plan gate, findings, risks and next action;
- verify the S5-B architecture contract against the read-only investigation evidence;
- confirm links, archive replacements and Markdown-only scope at the exact remote head;
- return `PASS` before S5-B1 begins; on failure, report the blocking findings without mutating the audited head, and require the next authorized Worker to reflect them before repair.

## Acceptance criteria

### Architecture

- Raw edge observations are immutable and remain traceable to their source evidence.
- Proposal diameter, proposal count, scale count, deduplication tolerance and temporal state are explicitly bounded.
- Broad region-step and narrow line/pulse evidence remain separate continuous likelihoods.
- Boundary, artifact and ambiguity evidence are not collapsed into an early enum gate.
- Static evidence acts as a soft prior and cannot erase current contradictory evidence.
- No-interface is typed and competes with boundary hypotheses rather than being inferred from candidate absence.
- The external `PhaseDetection` contract and persisted schemas remain compatible.
- Legacy consensus/scorer/pair-suppression ownership is removed after production cutover.

### Evidence and validation

- Deterministic tests cover proposal construction, semantic deduplication, ambiguity preservation, no-interface transitions and bounded temporal state.
- Controlled comparison uses the same environment, dataset and settings for base and feature.
- Oil metrics do not regress outside the accepted gate; no-interface false-boundary behavior improves or remains acceptable.
- S5-A Foam/shimmer behavior is non-regressing.
- CPU, memory and packaging obligations remain within the documented quality gate.
- Real sample/video observations are supporting probes, not a substitute for user truth and benchmark fixtures.

## Completed evidence

- S1 benchmark foundation and Phase 2C-3 user-truth/fixture export are available.
- S2, S3, S4 and S5-A are complete and form the compatibility baseline.
- The existing S5-B branch contains broad oil consensus, explicit no-interface and bounded temporal-path experiments, but the latest candidate/static suppression sequence failed to establish an acceptable architecture.
- Read-only architecture investigation concluded that semantic hypotheses must precede suppression and temporal selection.

## Blocking findings

- The production path still assigns semantic meaning after raw generator clustering and hard suppression decisions.
- Repeated repairs have not separated broad region transitions from narrow structural pulses.
- Current static suppression can still become an early information-destroying gate.
- A shadow pipeline and independent evidence audit do not yet exist.

## Open risks

- Broad and narrow evidence may correlate under glare, blur or multiple structural edges and still require calibrated ambiguity handling.
- Shadow/production comparison can drift if instrumentation changes external results or settings fingerprints.
- Temporal likelihoods can become sticky if missing/no-interface transitions are not explicitly bounded.
- Static priors derived from short samples may misrepresent moving reflections or real boundaries.
- CPU cost can increase if scale, diameter or proposal bounds are not enforced at every stage.
- Real-video truth coverage remains limited until S6.

## Explicit non-goals

- No Python source, test, dependency, workflow or persisted-schema change in the documentation-normalization stage.
- No large learned model, checkpoint, CUDA or dedicated-GPU requirement.
- No fixture-ID, filename or single-video hard-coded exception.
- No S5-A redesign, Result Review feature expansion or annotated MP4 implementation.
- No claim that the repository sample is canonical truth.
- No `DONE` status before required validation and merge.

## Next action

Obtain an independent documentation and planning audit at the immutable exact head reported by this repair Worker. After an audit `PASS`, the next authorized mutation-capable Worker updates the Work Plan header and begins S5-B1 as a bounded shadow implementation that leaves production `PhaseDetection` behavior unchanged.

## Latest recorded closeout

- **Result:** `SUCCESS`
- **Task-start exact head:** `7ac6c5da7289ad53662caf43447b5cf3a8c10476`
- **Task-start exact parent:** `73e9cd3d6562ba65126f4cd74574f3289f1dd9ad`
- **Completed scope:** Added bounded replacement and compaction rules for the Roadmap, Work Plan, closeout policy and documentation guide.
- **Validation evidence:** Relative links, single latest-closeout ownership, current gate/next-action consistency, Markdown-only scope, trailing newlines and `git diff --check` verified before commit.
- **Findings:** Planning documents must replace obsolete current-state content rather than accumulate closeout, audit, validation or commit journals.
- **Current gate and next action:** Unchanged; obtain independent documentation and planning audit `PASS` before S5-B1 begins.
- **Unresolved risks:** Existing S5-B architecture and evidence risks remain current; no detector implementation or runtime validation is claimed.
