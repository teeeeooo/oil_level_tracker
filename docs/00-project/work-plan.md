# Current Work Plan

- **Document status:** `ROUTE_INVARIANT_IDENTIFIABILITY_MARGIN_REPAIR_AUDIT_PENDING`
- **Active milestone:** `S5-B — Oil-boundary hypothesis architecture`
- **Branch:** `feature/oil-boundary-temporal-tracking`
- **Route-invariant margin repair start exact head:** `38080906ed7380b27628251ae37f6c79726cf788`
- **Base:** `main @ 5f180d02a7aff36591e6f35adf44fca6347bdf9c`
- **Authoritative diagnosis:** `DIAGNOSIS: CONTRACT_UNIDENTIFIABLE`
- **Architecture audit:** `AUDIT: PASS`
- **Serialized source re-audit:** `AUDIT: PASS`
- **Observability Contract Exact-Head Audit:** `AUDIT: PASS`
- **Continuous-margin source re-audit:** `AUDIT: FAIL`
- **Discrete observability gate:** retired
- **Route-dependent normalization:** retired
- **Plateau-discriminability heuristic:** retained unchanged as a non-authoritative visible-artifact cue
- **Controlled comparison:** rerun blocked pending fresh independent source re-audit `PASS`
- **Current mutation owner:** bounded production source, focused regression, source-completing documentation and PR metadata
- **Production source mutation:** route-invariant current-frame identifiability margin complete
- **Current gate:** Fresh independent source exact-head re-audit; Auditor does not merge
- **Source repair:** complete and unapproved pending source re-audit
- **Canonical/Qt and controlled comparison:** blocked pending source re-audit `PASS`

This plan records the bounded production implementation of the audited S5-B single-frame observability contract. The existing detector input and typed evidence cannot always distinguish partial glare from a legitimate oil phase; therefore latent physical truth and detector-observable outcome remain separate contract dimensions. The implementation changes only typed current-observation acceptance in `oil_shadow_observations.py`; proposal construction, semantic scoring, Phase-A validation, temporal reducer/store, fill-state, smoothing, Foam ownership, detector version, dependencies and external schemas remain unchanged.

## Current observability decision

When oil boundary versus glare artifact is unidentifiable from the current frame and typed evidence, the only legal canonical family is `AmbiguousOutcome`. No raw or smoothed numeric oil is published, no oil candidate is selected, compatibility remains `NO_UPDATE` plus `PRESERVE`, and review-required projection is retained.

The controlled fixture owner records latent scene cause, physical numeric geometry presence, latent oil Y, detector identifiability and expected canonical family separately. Paired latent interpretations can therefore share an identical effective observation without deleting or weakening physical truth.

The executable collision matrix covers centered partial glare at `72/74 px`, legitimate `90 → 244` phase, alternating/block/sinusoidal stripe patterns, bright-side reversal, and ROI width/location variants where the component edge disappears. Repeated identical unresolved frames are not positive temporal evidence and cannot become numeric acceptance by repetition alone.

The prior source audit returned `AUDIT: FAIL` because the first current-frame observability override used four independent boolean cliffs: dtype ceiling minus `15`, broad strength `<0.40`, near-ceiling fraction `>=0.90`, and standard deviation `<=4.0`. The continuous-margin repair retired those switches and kept all four raw-metric cliff families closed. The plateau-discriminability heuristic remains unchanged and is not the acceptance owner.

The continuous-margin source re-audit then returned `AUDIT: FAIL` because otherwise identical observable evidence received a `0.40` normalization on the standard route and `0.35` on the corroborated-only route. Exact default-geometry `83 → 243` evidence therefore jumped by `+0.05` when only route ownership changed, allowing a route downgrade to increase acceptance margin.

Canonical route eligibility now remains exclusively in the caller. The identifiability helper receives no standard/corroborated route flags and combines only photometric ceiling pressure, lower-tail texture relief, broad-corroboration deficit, continuous coverage/availability/visibility/sample reliability, semantic boundary support, artifact/no-interface/competing-hypothesis dominance and ambiguity clearance. One route-invariant normalization varies continuously from `0.390` to `0.400` with existing evidence reliability. The exact route-limit states now produce the same margin `-0.0137589324`; no-route evidence cannot publish a boundary because canonical candidacy is checked separately. Observationally equivalent latent glare and latent oil inputs produce identical evidence and outcome. Controlled comparison remains blocked until the fresh independent source re-audit returns `PASS`, and the sequence `S5-B → S5-C → S6` is unchanged.

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

The exact historical set of two near-threshold glare-only probes and nineteen Foam clipped-glare probes remains an executable `21`-case no-numeric contract without skip, xfail, conditional weakening, false-oil acceptance or truth deletion.

## Retained typed and source history

The earlier typed-coherence repair remains retained: malformed Phase-A likelihood/projection mismatch is rejected, while original saturated glare produces coherent `AmbiguousOutcome`, no raw or smoothed numeric oil, `NO_UPDATE`, `PRESERVE` and review-required projection. S5-A Foam remains independently governed.

The later plateau-discriminability source changes remain historical implementation evidence only. The new diagnosis shows that local component and texture evidence cannot resolve every single-frame collision, so those changes are not approved as the final contract or as authority for controlled comparison.

## Contract evidence status

- Paired latent glare/oil interpretations retain different physical truth while sharing one ambiguous detector expectation and byte-identical effective current evidence.
- All eight collision pairs now produce `ShadowAmbiguousObservation` and `AmbiguousOutcome` with no raw/smoothed numeric oil, no selected oil candidate, `NO_UPDATE`, `PRESERVE` and review-required projection.
- The exact six prior red nodes are green: short-period block stripe, centered partial glare `72 px`, centered partial glare `74 px`, sinusoid with bright side above, sinusoid with bright side below and repeated identical ambiguity.
- Exact default-geometry `83 → 243` evidence produces margin `-0.0137589324` for standard plus corroborated, standard-only and corroborated-only route labels; route ownership discontinuity is exactly `0`.
- The structural-plus-real brightness `-12…+4` frame sweep crosses standard plus corroborated to corroborated-only without an upward margin jump, has no acceptance island, and proves positive no-route margin cannot bypass canonical candidacy.
- Intensity `235–245` has one explainable continuous margin progression; `239/240` are both ambiguity, and the `245` outcome remains ambiguity with materially changed semantic evidence after glare masking.
- Broad `82–89` including `85 → 244` and `86 → 244` has continuous corroboration deficit and margin progression; both audited neighbors remain ambiguity with no `0.40` switch or acceptance island.
- Sparse 10% alternating, block and sinusoidal lower-tail textures at low values `228–234`, with both bright-side polarities, remain numeric while the audited symmetric collision textures remain ambiguity.
- Near-ceiling support counts `4–14` are monotonic across centered, shifted and resized ROI geometries; audited counts `8/9` produce the same outcome and any later transition is a single continuous zero-margin crossing.
- The six-frame repeated unresolved sequence remains ambiguous on every frame and never promotes itself to numeric oil.
- Exact historical glare negatives remain `21/21` without numeric oil.
- Distinguishable clear/rapid, bright real-boundary and structural-plus-real cases remain truth-near numeric; structural-only remains without numeric oil.
- Saturated glare remains coherent ambiguity; malformed Phase-A likelihood/projection mismatch remains fail-closed; S5-A Foam/shimmer remains independently green.
- The immutable observability fixture and contract test SHA-256 values remain `818802756ebc206250f89540f06616988816b93c5e9b55b17bb42511decc8579` and `727455c5f6263a84e740fd307c9f28846af15e743c729945a4ac841a80ca3b18`.
- Full observability contract file: `40 passed`.
- Stabilized Worker-owned targeted set: `521 passed`, expected failures `0`, unexpected failures `0`, skip/xfail/conditional acceptance `0`.
- Python compile and `git diff --check`: `PASS`.
- Temporal owner, dependencies, detector version and external schemas are unchanged.

## Downstream sequence

1. Fresh independent source exact-head audit; the Auditor does not merge.
2. Controlled base/feature comparison only after the source audit returns `PASS` and authorizes it.
3. Formal S5-B completion under separate merge authority.
4. `S5-C — Canonical/Qt validation stabilization` as a distinct post-S5-B gate.
5. S6 real-video, Windows/manual and packaging validation.

## Latest recorded source state

- **Diagnosis:** `DIAGNOSIS: CONTRACT_UNIDENTIFIABLE`.
- **Starting exact head:** `38080906ed7380b27628251ae37f6c79726cf788`.
- **Changed owners:** typed current-observation source, focused route-invariance regression, source-completing architecture/work-plan documentation and PR metadata.
- **Production owner:** `src/oil_tracker/adapters/vision/oil_shadow_observations.py`.
- **Retired conditions:** dtype ceiling minus `15`, broad strength `<0.40`, near-ceiling fraction `>=0.90`, and standard deviation `<=4.0` as direct boolean observability switches; route-dependent `0.40/0.35/1.00` normalization.
- **Plateau-discriminability heuristic:** retained unchanged as a non-authoritative visible-artifact cue.
- **Temporal owner:** unchanged; existing ambiguity reduction already prevents repeated-frame numeric promotion.
- **Controlled comparison:** blocked pending independent source re-audit `PASS`.
- **Intentional non-runs:** full repository, canonical/Qt, E2E, controlled comparison, Windows/manual, packaging, merge, synchronization, Close and cleanup.
- **Current gate:** fresh independent source exact-head audit after ordinary commit/push.
- **Resulting exact SHA:** reported by the Worker final report, not self-recorded in this commit.
