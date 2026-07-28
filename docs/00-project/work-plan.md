# Current Work Plan

- **Document status:** `SOURCE_REAUDIT_PENDING`
- **Active milestone:** `S5-B — Oil-boundary hypothesis architecture`
- **Branch:** `feature/oil-boundary-temporal-tracking`
- **Implementation-start exact head:** `79428752f5b026e92dcd36f7ddc595da3bea8fd6`
- **Implementation-start exact parent:** `fc923dbdfbf827da7ba1f8193a2ba5314ed9b606`
- **Repair-start exact head:** `687105264d6b4982216bdd06d076b2bd48f6cc3b`
- **Repair-start exact parent:** `79428752f5b026e92dcd36f7ddc595da3bea8fd6`
- **Base:** `main @ 5f180d02a7aff36591e6f35adf44fca6347bdf9c`
- **Architecture audit:** `AUDIT: PASS`
- **Source audit:** `AUDIT: FAIL` — core serialized architecture passed; detector pre-owner immutable-input preparation failure escaped `detect()`
- **Independent source-audit history:** Three failures of the retired transactional design plus one bounded detector-normalization defect on the serialized implementation
- **Current gate:** Independent detector pre-owner failure-normalization repair exact-head source re-audit
- **Implementation status:** Blocking detector normalization defect repaired; independent exact-head source re-audit required
- **Controlled comparison:** Blocked pending independent source re-audit `PASS`

This plan records the bounded S5-B serialized temporal-state source/test implementation. It makes no controlled-comparison, canonical-validation, Windows/manual-validation, packaging, merge or S5-B completion claim.

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

## Detector pre-owner failure-normalization repair

The serialized core passed independent source audit. The blocking defect was limited to the detector facade: `_isolated_pipeline_inputs(...)` executed before the detector's exception-normalization boundary, so an immutable-copy failure could escape `detect()` before the owner was invoked.

The bounded repair places detector-side immutable oil-input preparation and serialized-owner invocation inside the same normalization boundary. Any preparation or invocation exception now returns `PipelineFailureOutcome` with tracker `NO_UPDATE`, smoothing `PRESERVE`, no numeric oil, no selected candidate and no positive no-interface evidence.

The repair does not change owner sequencing, immutable store/record models, reducer logic, temporal mathematics, replacement behavior, reset/re-entry semantics, projection mapping, detector version or external schemas. Production-path tests inject failures into both `_isolated_pipeline_inputs` and the internal readonly-copy operation through `OpenCvPhaseDetector.detect()`. They verify exact oil-store identity/replacement invariance, retained existing Glass record, continued S5-A Foam processing and a successful following oil command for debug-off and debug-on paths.

## Implemented source migration scope

The audited architecture has been implemented as a bounded owner-aligned source change:

- one ticket-based ingress serializes oil-frame run, Glass reset, global reset, snapshot and count;
- immutable preparation owns independent read-only raster copies before sequencing;
- one immutable `TemporalStoreState` reference owns all versioned `GlassTemporalRecord` values;
- one fixed private reducer creates decision, next record, outcome, tracker/smoothing actions and resources;
- owner validation completes before exactly one successful store-reference replacement;
- reset generation, commit token, stale/replay/session semantics, lifecycle barriers and per-Glass locks are removed;
- detector-side post-owner rejection and projection-side load-bearing validation are removed;
- projection is exhaustive and non-rejecting for the closed outcome family;
- deterministic tests enforce total order, re-entry rejection, failure invariance and single replacement;
- successful temporal mathematics, S5-A Foam, external schemas and detector behavior remain protected.

This implementation remains unapproved until an independent exact-head source Auditor returns `AUDIT: PASS`.

## Source implementation acceptance matrix

Independent exact-head source audit must verify:

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

These remain future controlled-comparison findings and are not part of this bounded serialized-owner correctness change.

## Downstream sequence

1. Independent detector pre-owner failure-normalization repair exact-head source re-audit.
2. Controlled base/feature comparison only after source re-audit `PASS`.
3. Later canonical, Windows/manual, packaging and merge gates under separate authority.

## Latest recorded closeout

- **Result:** Detector pre-owner immutable-input preparation failures are normalized without changing the serialized core; independent exact-head source re-audit required.
- **Starting exact head:** `687105264d6b4982216bdd06d076b2bd48f6cc3b`.
- **Starting parent:** `79428752f5b026e92dcd36f7ddc595da3bea8fd6`.
- **Changed scope:** Detector oil evaluation boundary, production-path normalization tests and this current work plan only.
- **Repair-focused validation:** `5 passed` for helper/copy failures across debug-off and debug-on production paths.
- **Serialized validation:** `36 passed` for owner ordering, reducer coherence, failure invariance, reset and re-entry.
- **Production validation:** `44 passed` for detector/consumer, S5-A Foam, raster isolation and closed projection coverage.
- **Full repository validation:** `771 passed`, with only the two unchanged controlled-accuracy failures recorded above.
- **Compile validation:** `PYTHONPATH=src .venv/bin/python -m compileall -q src tests` passed.
- **Current gate:** Independent detector pre-owner failure-normalization repair exact-head source re-audit.
- **Resulting exact SHA:** Reported by the Worker final report, not self-recorded in this commit.
