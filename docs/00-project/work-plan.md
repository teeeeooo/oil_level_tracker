# Current Work Plan

- **Document status:** `PLATEAU_DISCRIMINABILITY_REAUDIT_PENDING`
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
- **Typed-coherence start exact head:** `328a63a5472367aa3c5f2f3266a624f03e64c16d`
- **Typed-coherence start exact parent:** `15230707d45c4b719719feff09d40a516934093c`
- **Semantic-glare repair start exact head:** `1386331e628cdab6b6fce40ece3100141dd58982`
- **Support-generalization repair start exact head:** `eba6a7cf4fa75cb77fada712d919057dbe6de80a`
- **Plateau-discriminability repair start exact head:** `584030d402d6c802f9fc6887ff632ef28f9ff449`
- **Base:** `main @ 5f180d02a7aff36591e6f35adf44fca6347bdf9c`
- **Architecture audit:** `AUDIT: PASS`
- **Serialized source re-audit:** `AUDIT: PASS`
- **Calibration source audit:** `AUDIT: FAIL`
- **Semantic glare source audit:** `AUDIT: FAIL`
- **Semantic glare source re-audit:** `AUDIT: FAIL`
- **Controlled comparison:** `COMPARISON: FAIL`
- **Failure attribution:** `DIAGNOSIS: COMPLETE`
- **Glare helper disposition:** `INVALID_AND_REPLACE`, repaired by the honest perturbation contract
- **Primary repair owner:** `src/oil_tracker/adapters/vision/oil_shadow_observations.py`
- **Current gate:** Fresh independent exact-head source re-audit
- **Implementation status:** Localized high-contrast glare components and strong distributed fine variation are separated from weak full-phase texture without a width acceptance cliff
- **Glare coherence:** Typed construction remains coherent; the width-cliff and legitimate-texture recall findings are repaired on the Worker head
- **Controlled comparison and canonical validation:** Blocked pending source re-audit `PASS`

This plan records the bounded S5-B semantic glare plateau-discriminability repair after the latest independent source re-audit returned `AUDIT: FAIL`. It does not change preprocessing glare threshold, raw observation/proposal construction, boundary acceptance, Phase-A validation, temporal/fill-state ownership, fixtures, external schemas or detector version, and it does not approve controlled comparison, canonical validation, Windows/manual validation, packaging, merge or S5-B completion.

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

The subsequent typed-coherence repair now prevents contextual glare ambiguity from retaining a hypothesis-specific projected Y unless the complete likelihood tuple remains canonical to that hypothesis. Original saturated `glare-recovery` evidence is therefore reviewable ambiguous evidence with no numeric oil instead of a Phase-A pipeline failure. The final visible frame remains numeric, while semantic glare false-positive discrimination stays a separate bounded owner.

The strict-dominance robustness matrix covers clear and rapid representatives across boundary-position `-2` through `+2 px`, brightness `-8` through `+8`, contrast `0.90×` through `1.10×` and three fixed weak-noise seeds. All positive probes retain deterministic public numeric oil within the truth-near geometry tolerance. The same perturbations over thin line, paired pulse, rim line, reflection, glare, shimmer, learned static overlap, uniform full/empty and transient false-line controls produce no raw oil; uniform states remain no-interface and structural-plus-real remains distinguishable from structural-only evidence.

## Honest glare perturbation test contract

The independently completed glare attribution returned `DIAGNOSIS: COMPLETE` and classified the shared saturated-pixel preservation helper as `INVALID_AND_REPLACE`. That test-contract repair changed test infrastructure only; detector settings, controlled scene semantics, detector version and external schemas remain unchanged by the current typed-coherence repair.

The general neighborhood helper now uses non-wrapping `cv2.warpAffine` vertical translation with `BORDER_REPLICATE`, signed-integer full-frame brightness with clipping, fixed-center (`127.5`) full-frame contrast with clipping, and `np.random.default_rng(seed)` full-frame Gaussian noise with positive sigma and clipping. No source pixel is exempted because it was originally saturated. Deterministic diagnostics record shape, dtype, extrema, mean, standard deviation, changed-pixel count, absolute/difference statistics, populations at `>=230`, `>=235`, `>=240`, `>=245`, and frame SHA-256 without entering the detector input contract.

The mandatory `glare-recovery-1` `0.92×` contrast probe moves from source maximum `255` with a populated `>=245` mask to transformed maximum `244` with zero `>=245` pixels while retaining positive `>=240` population. The honest helper contract and deterministic diagnostics remain unchanged. At the typed-coherence gate, the two near-threshold glare-only and nineteen Foam clipped-glare findings remained red and were retained as the acceptance contract for the semantic repair below.

The current semantic repair makes all `21` assertions green without skipping, xfail, conditional weakening, false-oil acceptance, fixture changes or truth changes.

## Typed ambiguous-observation coherence repair

A contextual ambiguity value may summarize frame-level glare or the minimum ambiguity floor rather than one semantic hypothesis. The construction now retains `projected_source_y` only when that aggregate ambiguity remains equal to the selected hypothesis's canonical ambiguity within the existing Phase-A numeric tolerance. Otherwise it preserves the aggregate likelihoods and referenced hypothesis identities but emits no specific projected Y.

This keeps Phase-A unchanged and fail-closed: a malformed observation that claims a canonical hypothesis Y while supplying mismatched likelihoods is still rejected. Original saturated glare now produces coherent `AmbiguousOutcome`, no raw or smoothed numeric oil, `NO_UPDATE`, `PRESERVE`, glare/review flags and identical fresh-repeat/debug results. General thresholds, semantic scores, artifact penalties, preprocessing glare threshold, temporal reduction, fill-state, Foam, external schemas and detector version are unchanged.

## Semantic glare plateau-discriminability repair

The latest independent semantic source re-audit returned `AUDIT: FAIL` with two blockers. A centered uniform partial glare changed from no numeric oil at width `56 px` to accepted numeric oil at `58–60 px`, because the short side band became horizontally uniform once the glare component filled the local mask run. At the same time, normalized horizontal autocorrelation discarded texture amplitude and therefore classified weak stripes, smooth gradients and sinusoidal banding inside a legitimate oil phase as strong plateau artifacts.

The repair uses two continuous and complementary row evidences inside the same observation owner. Localized-component evidence evaluates only the strongest bounded set of lateral edges and raises support when one strong split or one opposite-edge pair explains a high-contrast component. Contrast and edge strength are squared before bounded weighting, so weak oil texture decays rapidly instead of crossing a hard threshold. Distributed-fine-texture evidence uses mean adjacent total variation with a steep continuous response and discounts the two strongest edges; it therefore retains the dense `240–244` glare pattern and clipped-glare Foam evidence without treating smooth or low-amplitude full-phase texture as glare.

Each hypothesis side now uses a window proportional to `45%` of valid ROI height and a proportional center gap. Only the longest contiguous mask run is evaluated when it covers at least `25%` of the ROI reference width. Row evidence is averaged across the complete side window and weighted by actual run width. A partial glare that fills the mask at the candidate row therefore remains visible in farther rows as the ellipse widens, and the score decreases continuously as width increases rather than collapsing at one mask-width boundary. Sparse, fragmented and single-column support remain fail-closed.

The evidence remains a private semantic term in `oil_shadow_observations.py`. Preprocessing, raw observations, proposals, acceptance thresholds, Phase-A, typed coherence, no-interface meaning, temporal/fill-state ownership, Foam, fixtures, schemas and detector version remain unchanged.

## Controlled evidence status

- Controlled comparison remains `COMPARISON: FAIL`; a new comparison is unauthorized until source re-audit `PASS`.
- Latest semantic glare source re-audit: `AUDIT: FAIL`; the width-cliff and legitimate-texture blockers are repaired on the Worker head and require fresh re-audit.
- Exact prior negatives: all two glare-only contrast and nineteen Foam clipped-glare probes produce no raw numeric oil.
- Uniform partial-glare width sweep `48–70 px`, including required `52`, `56`, `60` and `64 px`, produces no numeric oil. Artifact scores are non-increasing and every adjacent width delta is below `0.30`, so the prior `56 → 58 px` decision cliff is absent.
- Five horizontal locations and four scaled ellipse ROIs retain partial-glare suppression.
- Bright real-boundary matrix: all seven cases remain truth-near numeric oil, including both bright-side directions, threshold-minus-one, local bright line and both ROI limits.
- Legitimate phase-texture matrix: all nine weak stripe, smooth-gradient and sinusoidal cases remain truth-near numeric oil across brightness, amplitude, position and phase-side variation.
- ROI support matrix at `40×50`, `80×100` and `160×200`: broad localized glare scores above `0.80`; sparse, fragmented and single-column support score `0.0`.
- Final targeted set: `326 passed` across focused semantic evidence, the controlled oil benchmark file and focused S5-A Foam/shimmer acceptance.
- Clear/rapid neighborhoods, direct semantic recall, structural-only/structural-plus-real separation, saturated glare typed ambiguity, malformed Phase-A mismatch rejection, raster immutability and debug equality remain green.
- S5-A gate remains green with Foam precision `1.0`, Foam recall `>=0.80` and shimmer Foam false-positive rate `0.0`.
- Next gate: fresh independent exact-head source re-audit; that Auditor does not merge.

## Downstream sequence

1. Fresh independent exact-head source re-audit of the plateau-discriminability repair.
2. Controlled base/feature comparison only after source re-audit `PASS`.
3. Formal S5-B completion under separate merge authority.
4. `S5-C — Canonical/Qt validation stabilization` as a distinct post-S5-B gate.
5. S6 real-video, Windows/manual and packaging validation.

## Latest recorded closeout

- **Result:** Partial-glare evidence remains suppressive across the mask-width transition while weak legitimate phase texture retains numeric boundary recall.
- **Starting exact head:** `584030d402d6c802f9fc6887ff632ef28f9ff449`.
- **Changed owners:** semantic observation source, focused evidence tests, controlled public regressions and this work plan.
- **B1:** a longer ROI-scaled side window and row averaging retain localized-component evidence after glare fills the candidate-row mask; width changes no longer create an acceptance cliff.
- **B2:** normalized autocorrelation is replaced by strong localized-component and distributed-fine-variation evidence, both amplitude-sensitive; weak stripes, gradients and sinusoids remain recall-neutral.
- **Phase-A and typed coherence:** unchanged and fail-closed; saturated glare remains coherent ambiguity with no projected Y or numeric oil.
- **Temporal and Foam ownership:** unchanged; Foam detection remains independent from oil outcome selection.
- **Validation scope:** one final targeted set plus `git diff --check`; controlled comparison and broader gates are intentionally excluded.
- **Current gate:** fresh independent exact-head source re-audit after ordinary commit/push.
- **Resulting exact SHA:** reported by the Worker final report, not self-recorded in this commit.
