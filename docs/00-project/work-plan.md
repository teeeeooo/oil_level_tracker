# Current Work Plan

- **Document status:** `DESIGNING`
- **Active milestone:** `S5-B — Oil-boundary hypothesis architecture`
- **Branch:** `feature/oil-boundary-temporal-tracking`
- **Redesign-start exact head:** `fc923dbdfbf827da7ba1f8193a2ba5314ed9b606`
- **Redesign-start exact parent:** `a8e308c514762e0bca0af0273b2bfcb01ab4bc29`
- **Base:** `main @ 5f180d02a7aff36591e6f35adf44fca6347bdf9c`
- **Independent source-audit history:** Three successive failures of the multi-lock transactional temporal architecture
- **Current gate:** Independent serialized temporal-state architecture exact-head re-audit
- **Implementation status:** Blocked pending architecture re-audit `PASS`
- **Controlled comparison:** Blocked pending later independent source exact-head audit `PASS`

This plan records a documentation-only S5-B architecture redesign. It makes no source repair, test, controlled-comparison, canonical-validation, Windows, packaging, merge or S5-B completion claim.

## Why the previous source direction is retired

The current source attempted to preserve different-Glass temporal mutation parallelism through:

- a writer-priority lifecycle barrier;
- per-Glass locks plus shared guards;
- state and version side mappings;
- reset generation;
- immutable snapshots with stale/replay validation;
- commit tokens;
- commit-to-return exclusion;
- post-hoc decision/state/outcome coherence checks.

Three independent source audits found recurring partial-commit, reset re-entry, post-commit rejection and semantic-coherence problems despite two bounded repairs. The failures indicate architectural over-complexity rather than another local validation gap.

Different-Glass temporal mutation parallelism is therefore abandoned. The product has one to three Glasses and prioritizes temporal correctness and auditability over unmeasured mutation throughput.

## Governing redesign

The authoritative contract is [S5-B Oil-Boundary Hypothesis Architecture](../20-architecture/s5b-oil-boundary-hypothesis-architecture.md).

The redesign requires:

1. **One serialized owner**
   - oil-frame temporal processing, Glass reset, global reset, snapshot and count use one owner command order;
   - concurrent callers are sequenced at one ingress and execute in assigned order;
   - stateless image preprocessing may remain outside the owner command loop;
   - the public owner facade performs immutable input isolation before sequencing;
   - temporal evidence application, reduction, outcome creation and state mutation are serialized.

2. **One immutable store reference**
   - `TemporalStoreState` owns all Glass records;
   - each `GlassTemporalRecord` owns version and temporal state together;
   - missing records denote initial state without insertion;
   - successful mutation prepares a complete new store and replaces the owner reference once;
   - any run failure leaves the exact prior store unchanged.

3. **One fixed canonical reducer**
   - the same reducer branch creates canonical decision, next record, canonical outcome, tracker action and smoothing action;
   - the reducer is a private fixed source component, not a constructor/public seam;
   - production callback, evaluator, runner and external commit injection remain prohibited.

4. **One load-bearing validation owner**
   - canonical evidence, reducer result and prepared replacement store are validated inside the owner before replacement;
   - detector projection does not revalidate or reject a returned successful outcome;
   - there is no commit-after-handoff or failure conversion after state assignment.

5. **Ordered reset and explicit re-entry rejection**
   - reset commands share the same owner order as run and read commands;
   - run-before-reset and reset-before-run semantics follow assigned sequence exactly;
   - active-owner public re-entry is rejected before enqueue and mutation;
   - owner commands execute no user callback or hook.

## Retired concurrency requirements

The following are no longer acceptance requirements and must be removed rather than retained dormant:

- different-Glass temporal mutation parallelism;
- lifecycle barrier and reset waiters;
- per-Glass lock ordering;
- separate state/version stores;
- reset generation;
- commit token and stale/replay handling;
- public proposal/commit composition;
- callback-based transaction instrumentation;
- post-commit detector rejection.

Future performance work requires measurement and a separately audited architecture decision. It may not restore parallel temporal mutation by default.

## Failure contract

Every oil pipeline failure must produce:

- unchanged complete prior owner state;
- `PipelineFailureOutcome`;
- no numeric oil and no selected candidate;
- tracker `NO_UPDATE`;
- smoothing `PRESERVE`;
- no positive no-interface projection;
- no legacy oil fallback;
- independent S5-A Foam processing;
- unchanged input raster ownership.

There is no post-replacement failure projection.

## Future source migration scope

After architecture re-audit `PASS`, a bounded implementation Worker must:

- replace the current barrier/guard/per-Glass-lock architecture with a single serialized owner;
- introduce the immutable store and Glass-record model;
- fold evaluator, next-state, outcome and action construction into one fixed reducer;
- validate all canonical invariants before one store-reference replacement;
- remove reset generation, commit token, stale/replay/session semantics and related tests;
- remove detector-side post-run result rejection;
- keep projection exhaustive and non-rejecting;
- replace different-Glass parallelism tests with total-order, re-entry and failure-invariance tests;
- preserve successful temporal mathematics, S5-A Foam, external schemas and detector behavior.

No source or test implementation is authorized by this documentation commit.

## Architecture acceptance matrix

Independent architecture re-audit must verify:

- one owner defines a total order for run, reset, snapshot and count;
- one immutable store value owns all Glass records;
- record version and temporal state are co-owned;
- successful mutation has exactly one state-reference replacement;
- every pre-replacement failure preserves the complete prior store;
- one fixed reducer creates decision, record, outcome and actions together;
- exactly one load-bearing production validation owner exists;
- detector cannot reject or convert an outcome after commit;
- reset ordering and re-entry semantics are explicit and deadlock-free;
- lock/barrier/generation/token/session complexity is an explicit removal target;
- source acceptance and deterministic test matrices cover all temporal variants and failure points;
- S5-A Foam, raster isolation and external contracts remain protected.

## Deferred controlled accuracy findings

Unchanged and not relaxed:

- clear-oil raw detection coverage remains `0.5714285714285714`, below expected `1.0`;
- `no-interface-to-visible` frame 3 still has no numeric raw oil recovery.

These remain future controlled-comparison findings and are not part of this documentation redesign.

## Downstream sequence

1. Independent serialized temporal-state architecture exact-head re-audit.
2. Bounded source/test implementation only after architecture `AUDIT: PASS`.
3. Independent implementation exact-head source audit.
4. Controlled base/feature comparison only after source audit `PASS`.
5. Later canonical, Windows/manual, packaging and merge gates under separate authority.

## Latest recorded closeout

- **Result:** Multi-lock transactional temporal architecture retired in favor of one serialized owner.
- **Starting exact head:** `fc923dbdfbf827da7ba1f8193a2ba5314ed9b606`.
- **Starting parent:** `a8e308c514762e0bca0af0273b2bfcb01ab4bc29`.
- **Changed scope:** Architecture and current work-plan documentation only.
- **Validation:** Documentation inspection and repository diff checks only; no source tests or controlled validation authorized.
- **Current gate:** Independent serialized temporal-state architecture exact-head re-audit.
- **Resulting exact SHA:** Reported by the Worker final report, not self-recorded in this commit.
