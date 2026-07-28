# Current Work Plan

- **Document status:** `SOURCE_AUDIT_PENDING`
- **Active milestone:** `S5-B — Oil-boundary hypothesis architecture`
- **Branch:** `feature/oil-boundary-temporal-tracking`
- **Implementation-start exact head:** `79428752f5b026e92dcd36f7ddc595da3bea8fd6`
- **Implementation-start exact parent:** `fc923dbdfbf827da7ba1f8193a2ba5314ed9b606`
- **Serialized repair exact head:** `e0d5c9fddb53c549bac0e56a4b7b6084862e5ca7`
- **Serialized repair exact parent:** `687105264d6b4982216bdd06d076b2bd48f6cc3b`
- **Calibration-start exact head:** `e0d5c9fddb53c549bac0e56a4b7b6084862e5ca7`
- **Calibration-start exact parent:** `687105264d6b4982216bdd06d076b2bd48f6cc3b`
- **Dominance-robustness start exact head:** `912a94b1cd62b0164e896a7e02dbb1df1c0c85dc`
- **Dominance-robustness start exact parent:** `e0d5c9fddb53c549bac0e56a4b7b6084862e5ca7`
- **Base:** `main @ 5f180d02a7aff36591e6f35adf44fca6347bdf9c`
- **Architecture audit:** `AUDIT: PASS`
- **Serialized source re-audit:** `AUDIT: PASS`
- **Calibration source audit:** `AUDIT: FAIL`
- **Controlled comparison:** `COMPARISON: FAIL`
- **Failure attribution:** `DIAGNOSIS: COMPLETE`
- **Primary repair owner:** narrow-path boundary-to-no-interface semantic dominance
- **Current gate:** Independent exact-head source re-audit of the dominance-robustness repair
- **Implementation status:** Fixed positive-margin cliff replaced by strict semantic dominance; audit required
- **Glare coherence:** Separate bounded follow-up owner; not repaired here
- **Controlled comparison and canonical validation:** Blocked

This plan records the bounded S5-B corroborated-boundary no-interface-dominance robustness repair. It does not approve the separate glare-coherence repair, a new controlled comparison, canonical validation, Windows/manual validation, packaging, merge or S5-B completion.

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

## Single-candidate semantic boundary calibration repair

The independently completed controlled comparison returned `COMPARISON: FAIL`, and the bounded failure attribution returned `DIAGNOSIS: COMPLETE`. Persisted truth-visible failures retained truth-near raw observations, bounded proposals and semantic hypotheses, but one dominant hypothesis with no material alternative was withheld before the temporal reducer because its boundary likelihood was approximately `0.4329–0.4541`, below the unchanged general `0.48` floor.

The repair uses a separate narrow current-observation acceptance path. It requires exactly one semantic hypothesis and one proposal, at least six observation provenance members, boundary likelihood `>= 0.43`, boundary-to-artifact margin `>= 0.26`, strict boundary dominance over no-interface evidence by more than the numerical equality epsilon `1e-12`, ambiguity `< 0.60`, broad strength `>= 0.40`, at least two broad scales, broad scale consistency `>= 0.85`, available narrow evidence with peak and scale persistence `>= 0.90`, pulse-artifact support `<= 0.50`, paired-edge strength `<= 0.80`, visibility `>= 0.85`, evidence availability `>= 0.90`, coherent available polarity, bounded glare/exclusion/border conflict `<= 0.15`, static-prior contribution `<= 0.08` and static overlap `<= 0.20`.

The independent calibration source audit returned `AUDIT: FAIL` after persisted targets and negative controls passed. Its single blocker was the fixed `0.06` boundary-to-no-interface difference: small truth-preserving position, brightness and contrast perturbations kept boundary evidence semantically dominant and passed every other narrow guard, but crossed that arbitrary positive-margin cliff and lost numeric oil. This repair removes only that calibrated distance and replaces it with strict semantic winner identity. Exact equality and differences at or below `1e-12` remain fail-closed, and no replacement margin such as `0.04`, `0.05` or `0.055` is introduced.

The general boundary floor `0.48`, general boundary margin `0.08`, ambiguity ceiling `0.72`, visibility floor `0.30`, no-interface likelihood `0.58` and no-interface margin `0.10` remain unchanged. All other corroboration guards remain unchanged. Semantic scoring weights, artifact penalties, no-interface evidence calculation, static-prior meaning, proposal clustering, semantic deduplication, temporal reduction, reacquisition, fill-state hold, external schemas and detector version are unchanged.

Feature-only persisted-dataset validation restored clear raw/smoothed coverage to `1.0`, rapid raw/smoothed coverage to `0.9565217391`, and kept no-interface raw/smoothed false-boundary rates at `0.0`. Reflection-only, structural rim-line, shimmer-only and transient false-line controls produced no raw oil. Foam precision and recall remained `1.0`.

`glare-recovery` frames 1–2 still report the known Phase-A `Ambiguous likelihoods disagree with canonical evidence` pipeline failure. The final visible frame now has numeric raw oil, so the intermediate cross-field coherence defect remains a separate bounded owner rather than expanding this calibration repair.

The strict-dominance robustness matrix covers clear and rapid representatives across boundary-position `-2` through `+2 px`, brightness `-8` through `+8`, contrast `0.90×` through `1.10×` and three fixed weak-noise seeds. All positive probes retain deterministic public numeric oil within the truth-near geometry tolerance. The same perturbations over thin line, paired pulse, rim line, reflection, glare, shimmer, learned static overlap, uniform full/empty and transient false-line controls produce no raw oil; uniform states remain no-interface and structural-plus-real remains distinguishable from structural-only evidence.

## Controlled evidence status

- Controlled comparison: `COMPARISON: FAIL`.
- Failure attribution: `DIAGNOSIS: COMPLETE`.
- Calibration source audit: `AUDIT: FAIL`; persisted and negative-control behavior passed, with one fixed-margin neighborhood blocker.
- Primary owner repaired here: strict boundary-over-no-interface semantic dominance in the narrow corroborated path.
- General boundary and no-interface acceptance gates remain unchanged.
- Separate follow-up owner: glare ambiguous-observation cross-field coherence.
- Next gate: independent exact-head source re-audit.
- New controlled comparison and canonical validation remain blocked.

## Downstream sequence

1. Independent exact-head source re-audit of this strict-dominance robustness repair.
2. Separate bounded glare cross-field coherence repair and independent audit.
3. New controlled base/feature comparison only after the owner-aligned source gates pass.
4. Later canonical, Windows/manual, packaging and merge gates under separate authority.

## Latest recorded closeout

- **Result:** The narrow corroborated path now requires strict semantic dominance over no-interface evidence instead of a calibrated positive distance; all other guards and global gates remain unchanged.
- **Starting exact head:** `912a94b1cd62b0164e896a7e02dbb1df1c0c85dc`.
- **Starting parent:** `e0d5c9fddb53c549bac0e56a4b7b6084862e5ca7`.
- **Changed scope:** `oil_shadow_observations.py`, directly related observation/controlled tests and this current work plan only.
- **Dominance and guard validation:** `22 passed`.
- **Positive neighborhood validation:** clear and rapid representatives, `36` probes, deterministic numeric oil and truth-near geometry.
- **Negative neighborhood validation:** ten control families, `180` probes, zero raw-oil false positives and deterministic debug on/off behavior.
- **Observation/evidence validation:** `40 passed`.
- **Required controlled targets/sequences:** `2 passed`.
- **Controlled benchmark validation:** `6 passed`.
- **Production detector/consumer/Foam validation:** `69 passed`.
- **Serialized owner/reducer validation:** `55 passed`.
- **Persisted parent-to-candidate diagnostic:** `74` cases; oil and Foam semantic payloads and public records exactly unchanged, zero head-only numeric oil and zero unhandled detector exceptions.
- **Persisted metrics:** clear raw/smoothed coverage `1.0`; rapid raw/smoothed coverage `0.9565217391`; no-interface raw/smoothed false-boundary `0.0`; Foam precision/recall `1.0`.
- **Known residual:** glare-recovery frames 1–2 retain `ValueError:Ambiguous likelihoods disagree with canonical evidence` at `phase_a`; final visible frame retains numeric raw oil.
- **Full repository validation:** `798 passed`.
- **Compile validation:** `PYTHONPATH=src .venv/bin/python -m compileall -q src tests` passed.
- **Diff validation:** `git diff --check` passed.
- **Current gate:** Independent exact-head source re-audit after ordinary commit/push.
- **Resulting exact SHA:** Reported by the Worker final report, not self-recorded in this commit.
