# S5-B Oil-Boundary Hypothesis Architecture

**Status:** `ACTIVE` route-invariant identifiability-margin repair implemented; fresh independent source exact-head re-audit pending
**Milestone:** [S5-B](../00-project/work-plan.md)
**Authoritative diagnosis:** `DIAGNOSIS: CONTRACT_UNIDENTIFIABLE`

This document governs the S5-B internal evidence, temporal-state, canonical-decision, canonical-outcome and detector-projection boundaries. It retains the audited serialized temporal owner while superseding the assumption that every robust oil/glare distinction can be recovered from one current frame and its existing typed evidence.

`ACTIVE` identifies the governing architecture only. The audited observability contract remains immutable. The continuous-margin source re-audit returned `AUDIT: FAIL`, and the bounded route-invariant repair is complete but unapproved. It does not authorize controlled comparison, canonical validation, Windows/manual validation, packaging, merge, synchronization, cleanup or S5-B completion. The next gate is a fresh independent **source exact-head re-audit** of the immutable contract, production owner, route-limit regression, retained cliff regressions and behavior.

## Single-frame observability contract

### Diagnosis

`DIAGNOSIS: CONTRACT_UNIDENTIFIABLE`

A centered partial-glare component and a legitimate `90 → 244` oil phase can produce the same effective masked raster and the same current typed evidence. The collision remains possible at partial-glare widths `72/74 px`, with high-frequency low-amplitude alternating stripes, short-period block stripes, sinusoidal texture, reversed bright-side direction, and ROI width/location changes that remove the component edge from the effective observation.

No additional local geometry or texture heuristic can identify the latent cause in every such collision. It can only move the acceptance cliff to another width, texture, polarity or ROI geometry. The present temporal store also preserves no photometric component history capable of correcting a wrongly accepted single-frame boundary.

### Latent truth and observable outcome

Controlled truth must keep these dimensions separate:

- latent scene cause, such as legitimate oil geometry or glare artifact;
- whether a numeric physical oil boundary exists in the scene;
- the latent numeric oil Y when it exists;
- whether that geometry is identifiable from the current detector input and typed evidence;
- the expected canonical outcome family.

A physically present oil boundary is not automatically detector-observable. Conversely, an ambiguous detector outcome is not a physical declaration that oil is absent. Re-labelling an oil-bearing collision as “no oil” is prohibited.

### Canonical fail-closed rule

When the current input and typed evidence do not identify oil boundary versus glare artifact:

- typed current observation is `ShadowAmbiguousObservation`;
- canonical result is `AmbiguousOutcome`, never `AcceptedBoundaryOutcome`;
- no raw, smoothed or compatibility numeric oil value is published;
- no oil candidate is selected;
- tracker action is `NO_UPDATE`;
- smoothing action is `PRESERVE`;
- review-required projection is retained.

Repeated presentation of the same unresolved frame is not positive temporal evidence. Repetition alone cannot promote ambiguity into numeric boundary acceptance. A future implementation may use new positive evidence, but it may not reinterpret repeated identical ambiguity as corroboration.

### Executable collision contract

The controlled owner in `tests/oil_observability_fixtures.py` records paired latent interpretations while preserving one observable expectation. `tests/test_oil_single_frame_observability_contract.py` proves effective raster/preprocess equivalence and requires the same ambiguous/no-numeric canonical result for both interpretations.

The contract covers:

- centered partial glare at `72 px` and `74 px` against legitimate `90 → 244` oil phase;
- high-frequency low-amplitude alternating stripe;
- short-period block stripe;
- sinusoidal stripe;
- bright-side direction reversal;
- centered and shifted ROI variants where the component edge disappears;
- repeated identical unresolved observations.

Retained distinguishable clear/rapid, bright real-boundary and structural-plus-real cases remain numeric and truth-near. Structural-only, the exact historical glare-negative set of `21`, saturated glare, malformed Phase-A mismatch and independently governed S5-A Foam remain fail-closed or otherwise unchanged according to their existing contracts.

### Implemented observability boundary and next gate

The independent Observability Contract Exact-Head Audit returned `PASS`. The later source audit returned `AUDIT: FAIL` because the first implementation placed canonical acceptance behind four direct boolean conditions: dtype ceiling minus `15`, broad strength `<0.40`, near-ceiling fraction `>=0.90`, and standard deviation `<=4.0`. Adjacent observable inputs therefore produced isolated numeric/ambiguity reversals. Those conditions are retired rather than moved to new threshold values.

The continuous-margin repair keeps the plateau-discriminability heuristic unchanged as a visible-artifact cue and adds no physical glare classification. It builds continuous photometric ceiling pressure and lower-tail texture relief from current side-band samples, combines them with continuous broad-corroboration deficit and coverage/availability/visibility/sample reliability, and subtracts the resulting collision pressure from semantic boundary, artifact/no-interface/alternative dominance and ambiguity-clearance support. The retained focused regressions cover intensity `235–245`, broad `82–89`, sparse texture `228–234`, and near-ceiling support `4–14`; all four prior raw-metric cliff families remain closed.

The continuous-margin source re-audit returned `AUDIT: FAIL` because the helper added route-dependent normalizations: `0.40` for standard candidates, `0.35` for corroborated-only candidates and `1.00` otherwise. Identical default-geometry `83 → 243` evidence therefore changed from `-0.0139242330` to `+0.0360757670` when only route ownership changed.

Canonical candidacy and identifiability are now separate owners. The caller retains the unchanged standard and corroborated eligibility rules and decides whether a boundary may be published. The private identifiability helper accepts no route flags and uses only observable continuous evidence. Its shared normalization is `0.39 + 0.01 × evidence_reliability`, so it varies continuously from `0.390` to `0.400` without route labels. Standard plus corroborated, standard-only and corroborated-only labels over fixed `83 → 243` evidence all produce margin `-0.0137589324`. A no-route candidate may have a positive diagnostic margin but remains ambiguity because the caller's canonical-candidate guard is false.

The route-transition regression uses structural-plus-real brightness `-12…+4`. The standard-to-corroborated-only transition has a decreasing margin, no ambiguity-to-numeric improvement and no acceptance island. Existing intensity, broad, texture and support neighborhoods remain continuous; audited `239/240`, `85/86` and `8/9` neighbors do not reverse, legitimate texture remains numeric, and unresolved collisions remain ambiguity.

The implementation does not change preprocessing, proposal construction, semantic likelihood formulas, the general boundary floor, Phase-A, temporal mathematics, fill-state, Foam, external schemas, detector version or dependencies. Existing ambiguity reduction already preserves accepted temporal state and cannot promote repeated identical unresolved frames, so no temporal owner change is required.

The bounded source remains unapproved until a fresh independent source exact-head re-audit returns `PASS`. Controlled base/feature comparison is blocked until that audit authorizes it.

Future architecture options are limited to separately designed and audited positive evidence such as temporal photometric/component history or capture metadata. Optical flow, retained raster history and capture-metadata schemas are not implemented by this source change.

The milestone order remains `S5-B → S5-C → S6`; this diagnosis does not reorder or combine S5-C or S6.

## Decision summary

S5-B adopts one serialized temporal-state owner for all Glasses. Every oil-frame temporal command, Glass-local reset, global reset, temporal snapshot and state-count query executes in one owner-defined total order. Different-Glass temporal mutation parallelism is no longer a product requirement.

The owner holds one immutable `TemporalStoreState` value. Each `GlassTemporalRecord` contains its own version and temporal state. A fixed internal reducer creates the canonical decision, next record, canonical outcome, compatibility tracker action and smoothing action as one coherent reduction. The owner validates the complete reduction and prepared replacement store before replacing the owner-state reference once.

There is no temporal commit after that replacement and no production rejection of the returned outcome. Any run failure leaves the complete prior owner state unchanged and returns `PipelineFailureOutcome` with no numeric oil or selection, tracker `NO_UPDATE` and smoothing `PRESERVE`.

## Why the prior transactional concurrency direction is retired

Three independent source audits rejected successive versions of the multi-lock transaction design. The repeated defects were not isolated missing checks. They arose from the architecture's need to coordinate independently created decisions, states, outcomes and lifecycle metadata across multiple synchronization mechanisms.

The retired design accumulated:

- a lifecycle barrier and reset waiters;
- per-Glass locks plus a shared guard;
- state and version in separate mappings;
- global reset generation;
- snapshot admission and stale-proposal checks;
- commit tokens and replay checks;
- commit-to-handoff atomicity requirements;
- decision/state/outcome post-hoc coherence validation;
- reset re-entry and lock-ordering rules;
- post-commit rejection paths in downstream detector code.

After redesign and two bounded repairs, audits still found partial-commit risk, reset re-entry ambiguity, possible post-commit rejection and semantic mismatch between independently prepared artifacts. Preserving different-Glass mutation parallelism would continue to require CAS-like validation, lifecycle coordination and rollback-sensitive reasoning that is disproportionate for a Windows desktop product processing one to three Glasses.

The product therefore chooses temporal correctness and auditability over parallel temporal mutation. An unmeasured throughput concern is not authority to restore the retired transaction graph.

## Retained detection and external contracts

The following remain unchanged unless a later separately authorized task changes them:

- masked-raster preprocessing and isolation;
- raw observation extraction;
- bounded deterministic Y proposal construction;
- broad region-step and narrow line/pulse evidence;
- boundary, artifact and ambiguity likelihood formulas;
- soft static prior behavior;
- semantic hypothesis deduplication;
- successful temporal transition mathematics and configured bounds;
- closed current-observation, decision and canonical-outcome variants;
- external `PhaseDetection` and application-port schemas;
- Recipe/settings persistence;
- benchmark, truth, fixture, result, CSV and debug schema versions;
- detector version and dependencies;
- independently governed S5-A Foam behavior.

Legacy oil fallback remains prohibited.

## Explicitly abandoned requirements

The source implementation must not preserve or recreate these requirements:

- simultaneous temporal mutation for different Glasses;
- external temporal proposal creation or commit;
- public snapshot/evaluate/commit composition;
- arbitrary custom temporal runner or evaluator injection;
- callback-based transaction instrumentation;
- per-Glass lock ownership;
- lifecycle read/write barriers or reset waiters;
- generation-based stale proposal rejection;
- commit token, replay or session ownership protocols;
- post-commit handoff validation.

Stateless preprocessing may be parallelized independently. S5-B evidence application, temporal reduction, outcome creation and owner-state mutation remain serialized. Future performance work must begin with measurement and cannot reintroduce parallel state mutation without a new audited architecture decision.

## Single temporal-state owner

### Owner responsibility

One production owner has exclusive authority over:

- S5-B oil-frame evidence construction and temporal application;
- all Glass-local temporal records;
- Glass-local reset;
- global reset;
- immutable temporal snapshot projection;
- temporal state count;
- canonical run failure conversion;
- canonical outcome publication.

The implementation may use a dedicated executor/queue or an equivalent single-owner command loop. The implementation detail is flexible only if it proves that no two temporal commands can read or modify owner state concurrently.

The owner is not a general task executor. It accepts only the closed S5-B command family defined below and invokes no user callback, public hook or replaceable production component while a command is active.

### Closed command family

Conceptually, the owner accepts:

```text
RunOilFrame(glass_id, immutable isolated frame inputs)
ResetGlass(glass_id)
ResetAll()
ReadSnapshot(glass_id)
ReadStateCount()
```

Public `run`, `reset`, `temporal_snapshot` and `temporal_state_count` operations are synchronous facades over these commands. A caller receives a result only after its command has completed in owner order.

No public command exposes a prior-state object, reducer, next record, commit operation or mutable owner reference.

### Deterministic ordering rule

A single ingress assigns each accepted command a strictly increasing command sequence number. Commands execute in ascending sequence order. This assigned sequence, rather than thread scheduling time or Glass identity, defines the authoritative order for concurrent callers.

Tests may capture assigned command sequence numbers through private, non-production instrumentation. The sequence is diagnostic ordering evidence and not a commit token or authorization capability.

Input validation that does not inspect temporal state may occur before sequence assignment. Once accepted and sequenced, a command cannot be overtaken by another temporal command. Cancellation after sequencing is not a production operation.

### Stateless work outside the owner

Image preprocessing that does not read or change S5-B temporal state may execute before the owner facade is called. The public owner facade performs read-only copying and input isolation before command sequencing; that preparation remains part of the sole owner boundary and converts its own failure to `PipelineFailureOutcome`. An accepted command payload is immutable and exposes no mutable arrays or callbacks to the command loop.

The authoritative S5-B sequence inside the owner is:

```text
Evidence construction
→ canonical evidence validation
→ fixed canonical reducer
→ outcome/record invariant validation
→ new immutable owner-state preparation
→ single owner-state reference replacement
→ return the same canonical outcome
```

Moving evidence construction outside the owner is not part of this redesign. A later optimization requires measurement plus proof that the resulting immutable evidence payload cannot create a second validation or temporal authority.

## Immutable owner state

### Store model

The owner holds exactly one live immutable store value:

```text
TemporalStoreState
  records: Glass ID → GlassTemporalRecord
  epoch: non-negative successful-mutation ordering metadata
```

Each record owns related data together:

```text
GlassTemporalRecord
  glass_id: Glass ID
  version: non-negative per-Glass successful-transition version
  temporal_state:
    bounded beam and history
    accepted Y and accepted velocity
    pending reacquisition Y, velocity and count
    no-interface stability count
    successful-unavailable stability count
    smoothing invalidation state
    bounded static temporal diagnostics
```

`records` is an immutable mapping value. A record, its version and its temporal state cannot be mutated in place. Version is not stored in a second mapping. There is no reset generation, commit token, transaction session or stale snapshot authority.

The owner may keep queue sequence bookkeeping outside `TemporalStoreState`; it must not use that bookkeeping as a second state store. `epoch` changes only through a successful mutating command and is diagnostic ordering metadata, not a CAS guard.

### Missing records

A missing Glass record denotes the canonical initial temporal state for that Glass with record version `0`. Reading an initial state must not insert a live record. A successful frame transition creates the first record at version `1` only through the single prepared store replacement. After either Glass-local or global reset, the next successful transition for the affected Glass again starts at version `1`; store `epoch` provides only cross-reset diagnostic ordering.

A Glass-local reset removes that Glass record and advances store `epoch`, even when the record was already absent. A global reset replaces the store with an empty record mapping and advances `epoch`. Reset does not preserve tombstones, per-Glass locks, version side tables or reset generations.

### One replacement rule

For a successful mutating command, the owner performs exactly:

1. read the prior `TemporalStoreState` reference;
2. derive the prior Glass record or canonical initial record;
3. complete the canonical reduction;
4. validate the complete decision, next record, outcome and actions;
5. build and validate the complete new `TemporalStoreState` value;
6. replace the live owner-state reference once;
7. return the already completed canonical outcome or reset acknowledgment.

No field-by-field live mutation is permitted. No second assignment may complete the same command. No validation, normalization, projection or failure conversion is permitted after assignment.

If construction or validation fails, the owner does not assign a new store reference. The exact prior store object and all contained records remain unchanged.

## Exact linearization points

The architecture has explicit linearization points:

| Command | Linearization point |
|---|---|
| `RunOilFrame` rejected before sequencing | owner-facade failure finalization, with no temporal-state read or replacement |
| successful sequenced `RunOilFrame` | the single owner-state reference replacement |
| failed sequenced `RunOilFrame` | failure outcome finalization in its owner sequence slot, with no state replacement |
| `ResetGlass` | the single replacement with the target record removed and epoch advanced |
| `ResetAll` | the single replacement with an empty record mapping and epoch advanced |
| `ReadSnapshot` | the owner-state reference read used to construct the immutable snapshot |
| `ReadStateCount` | the owner-state reference read used to compute the count |

The command queue order defines relative ordering. The state replacement is the only mutating linearization point. Returning to the caller is not an additional commit or handoff phase.

## Fixed canonical reducer ownership

### Reduction result

One fixed internal reducer consumes canonical evidence plus one prior `GlassTemporalRecord` and produces one immutable coherent reduction:

```text
CanonicalTemporalReduction
  decision
  next_record
  outcome
  tracker_action
  smoothing_action
  resource_metrics
```

The reducer creates these values together from the same branch of the successful temporal policy. It does not independently create an outcome and next record and then reconcile them later.

Concrete decision and outcome variants derive status, observation kind and legal actions. Generic booleans or optional fields cannot recreate a second discriminator.

### Reducer trust boundary

The reducer is a trusted source component:

- production constructs and calls the fixed reducer directly;
- it is not accepted through a constructor argument;
- it is not replaceable through a public protocol, runner, evaluator or callback;
- it exposes no public commit capability;
- it cannot retain or mutate the owner-state reference;
- it returns immutable values only.

Private reflection or test monkeypatching is not a production trust boundary. Tests may use private patching for deterministic failure injection, and an Auditor may inspect the reducer source and variant coverage. Such test mechanisms do not justify production injection seams.

### Reducer variant requirements

The fixed reducer must cover the complete successful temporal family:

- initial boundary acceptance;
- continuous boundary acceptance;
- bounded boundary reacquisition acceptance;
- reacquisition pending;
- no-interface pending and stable absence;
- successful evidence-unavailable pending and stable absence;
- ambiguous evidence.

Pipeline execution or validation failure never enters the successful reducer and never advances successful-unavailable or no-interface counters.

## Sole validation ownership

The temporal owner is the only load-bearing production validation owner. Constructor checks may reject impossible local values during construction, but no downstream component may independently reclassify or reject a committed successful outcome.

The owner validates:

### Canonical evidence

- supported concrete evidence variants;
- deterministic identity, content, provenance and Y coherence;
- canonical ordering and membership;
- finiteness, ranges and JSON safety;
- positive no-interface evidence availability and meaning;
- tuple and resource limits;
- immutable isolated raster/evidence ownership;
- absence of unsupported subclasses or duplicate discriminator attributes.

### Canonical reduction

- supported concrete decision and outcome variants;
- decision/current-observation compatibility;
- selected hypothesis identity, content, provenance and Y;
- acceptance or stability mode;
- exact decision-to-record temporal semantics;
- version increment and Glass identity;
- beam, history, counter and retained-resource bounds;
- exact tracker and smoothing actions derived by the variant;
- outcome/record/resource/action coherence;
- bounded diagnostics and projection data.

### Prepared owner state

- only the targeted Glass record changes for a successful run;
- all untargeted records are value-identical to the prior store;
- a reset changes only its defined scope;
- records and mapping are immutable;
- epoch and record version changes are canonical;
- the complete replacement value is valid before assignment.

Validation must finish before the owner-state reference replacement. There is no commit failure category after assignment: the replacement is a local reference assignment of an already completed immutable value, is treated as non-failing, and is immediately followed only by returning the already prepared outcome.

## Canonical outcomes and action mapping

The owner returns exactly one closed outcome variant:

- `AcceptedBoundaryOutcome`;
- `NoInterfaceOutcome`;
- `AmbiguousOutcome`;
- `EvidenceUnavailableOutcome`;
- `ReacquisitionPendingOutcome`;
- `PipelineFailureOutcome`.

Only `AcceptedBoundaryOutcome` owns numeric oil and selected boundary identity. `EvidenceUnavailableOutcome` represents successful execution with insufficient evidence and may participate in its bounded successful-absence policy. `PipelineFailureOutcome` represents execution, evidence construction, reducer or validation failure and cannot participate in successful absence counters.

The legal compatibility actions remain:

| Canonical situation | Tracker action | Smoothing action |
|---|---|---|
| accepted boundary, initial or continuous | `ACCEPT_BOUNDARY` | `PRESERVE` |
| accepted boundary, reacquired | `ACCEPT_BOUNDARY` | `CLEAR_BEFORE_ACCEPT` |
| accepted no-interface, pending | `NO_UPDATE` | `PRESERVE` |
| accepted no-interface, stable | `NO_UPDATE` | `CLEAR_STALE_AFTER_STABLE_ABSENCE` |
| successful evidence unavailable, pending | `NO_UPDATE` | `PRESERVE` |
| successful evidence unavailable, stable | `NO_UPDATE` | `CLEAR_STALE_AFTER_STABLE_ABSENCE` |
| ambiguous or reacquisition pending | `NO_UPDATE` | `PRESERVE` |
| any pipeline failure | `NO_UPDATE` | `PRESERVE` |

A generic `clear_smoothing` boolean is not a production discriminator.

## Detector projection boundary

`OpenCvPhaseDetector` supplies preprocessed raster inputs to the public temporal-owner facade. That facade performs immutable isolation, accepts the command and returns one canonical outcome. The detector then performs one-way projection to existing consumers.

The detector must not:

- call a second load-bearing `validate_production_result` after the owner returns;
- convert a returned successful canonical outcome into `PipelineFailureOutcome`;
- inspect a provisional decision or next record;
- reread temporal state to verify the outcome;
- select from raw evidence after canonical outcome publication;
- use legacy oil fallback;
- mutate S5-B temporal owner state through projection.

All expected operational failures inside `RunOilFrame` are caught and normalized by the owner before any replacement. A failure before command acceptance cannot have changed temporal state. Once a canonical outcome is returned, projection is exhaustive and non-rejecting.

Compatibility smoothing and fill-state remain separate downstream state owners. They consume only the canonical outcome variant and its canonical tracker/smoothing actions. S5-A Foam processing remains independent and must continue even when oil returns `PipelineFailureOutcome`.

## Reset ordering and re-entry

### Queue ordering

Reset commands use the same owner queue and ordering rule as run and read commands.

- `run → reset`: the run completes, including its outcome and any single replacement, before reset linearizes;
- `reset → run`: reset linearizes first and the run reduces from the reset initial record;
- `run A → reset Glass A → run A`: the second run observes no record from the first run;
- `run A → reset all → run B`: the final run observes an empty store;
- snapshots and counts observe the store at their own sequence position.

Global reset does not wait on per-Glass locks because none exist. It simply executes when its sequence position reaches the owner.

### Re-entry rejection

A public `run`, `reset`, `temporal_snapshot` or `temporal_state_count` call made from the active owner command context is rejected before enqueue and before any owner-state mutation. The implementation uses an explicit owner-context re-entry guard and a dedicated error category; it must not block waiting for its own queue.

A re-entered `run` is rejected by the public owner facade before sequencing and returns `PipelineFailureOutcome` with a bounded `temporal_reentry_rejected` reason, `NO_UPDATE` and `PRESERVE`. Re-entered reset and read operations raise the dedicated `TemporalReentryError` before sequencing because their return contracts are not oil outcomes. In every case, prior owner state is unchanged and no new external schema discriminator is introduced.

The owner invokes no user callback, hook or externally supplied callable during a command, so production re-entry has no supported use case.

## Failure contract

Every `RunOilFrame` failure point has the same result:

- exact prior `TemporalStoreState` reference unchanged;
- all Glass records unchanged;
- fresh `PipelineFailureOutcome`;
- no numeric oil;
- no selected candidate;
- no positive no-interface projection;
- tracker `NO_UPDATE`;
- smoothing `PRESERVE`;
- no legacy oil fallback;
- independently valid S5-A Foam processing preserved;
- input raster and frame-owned images unchanged.

Failure points include:

- S5-B evidence construction;
- canonical evidence validation;
- canonical reducer execution;
- reducer-result construction;
- decision/record/outcome/action/resource invariant validation;
- new owner-state preparation or validation;
- pre-enqueue immutable input preparation.

There is no post-replacement failure projection. The owner must prepare the successful outcome and replacement store completely before assignment. A Python-level local reference assignment is the final mutating action; code after it may only return the already prepared outcome without invoking fallible validation, hooks or callbacks.

## Source migration scope

A later bounded source implementation, after architecture re-audit `PASS`, must at minimum:

1. Replace the lifecycle barrier, shared guard, per-Glass locks, separate state/version mappings and reset generation in `oil_shadow_pipeline.py` with the single serialized owner and one immutable store reference.
2. Replace `GlassTemporalSnapshot`, commit token, replay/stale checks and `TemporalCommitError` transaction semantics with `TemporalStoreState`, `GlassTemporalRecord`, closed commands and immutable reduction values.
3. Refactor the current pure evaluator plus post-hoc coherence checks into one fixed reducer that creates decision, next record, outcome and actions together.
4. Retain canonical evidence validation but consolidate all load-bearing outcome/record validation inside the owner before replacement.
5. Remove detector-side post-run canonical result rejection from `opencv_phase_detector.py`; detector projection must be exhaustive and non-rejecting.
6. Adjust `oil_hypothesis_projection.py` so projection consumes closed outcomes without acting as a second production trust boundary.
7. Replace transaction/CAS/lifecycle tests with serialized owner, ordering, re-entry, single-replacement and prior-store invariance tests.
8. Remove obsolete lock, barrier, session, generation, commit-token, stale/replay and different-Glass parallelism code and tests.
9. Preserve external schemas, successful temporal mathematics, Foam behavior and detector compatibility.

Exact private class and module names remain implementation choices. The ownership, ordering, replacement and validation contracts do not.

## Architecture acceptance matrix

### Owner and ordering

- concurrent callers are fully serialized by one owner;
- accepted command sequence numbers form one total order;
- execution order equals assigned sequence order;
- no two commands read or mutate owner state concurrently;
- same-Glass and different-Glass calls follow the same contract;
- snapshots and counts are ordered commands, not unsynchronized reads;
- no lifecycle barrier, reset waiter or per-Glass lock remains.

### Immutable state and replacement

- one live `TemporalStoreState` reference owns all Glass records;
- each record owns version and temporal state together;
- missing-record reads do not create state;
- a successful run replaces the owner-state reference exactly once;
- reset replaces the owner-state reference exactly once;
- untargeted Glass records remain value-identical;
- no failure point replaces the owner-state reference;
- no field-by-field live mutation or rollback exists.

### Reducer coherence

- every successful temporal variant yields decision, next record, outcome and actions from the same reducer branch;
- accepted outcome Y equals the next record's accepted Y;
- reacquisition pending identity/Y/count agree across reduction values;
- no-interface and successful-unavailable stability mode, counters and clear action agree;
- ambiguous reduction preserves accepted state according to the accepted policy;
- pipeline failure never invokes successful absence transition logic;
- reducer source is fixed and not production-replaceable.

### Validation and projection

- exactly one load-bearing production validation owner exists;
- all canonical evidence and reduction invariants are validated before replacement;
- detector performs no post-commit rejection or failure conversion;
- downstream tracker, smoothing, fill-state, flags and debug consumers use only canonical outcomes/actions;
- only accepted boundary owns numeric oil and selection;
- pipeline failure owns no positive no-interface evidence;
- S5-A Foam and raster isolation remain unaffected.

### Reset and re-entry

- run-before-reset and reset-before-run produce state and outcome consistent with owner order;
- Glass reset affects only the target record;
- global reset yields an empty store;
- snapshots/counts around reset observe their sequence position;
- active-owner re-entry is rejected before enqueue and mutation;
- re-entry never deadlocks;
- owner commands invoke no user callback or hook.

### Failure injection

Deterministic tests inject failure at each pre-replacement stage:

- evidence construction;
- evidence canonicalization/validation;
- each reducer variant;
- reduction value construction;
- decision/record/outcome/resource validation;
- new store creation and validation;
- immutable input preparation.

Every row asserts exact prior-store identity or value equality, `PipelineFailureOutcome`, no numeric oil/selection, `NO_UPDATE`, `PRESERVE`, no legacy fallback and independent Foam behavior.

### Compatibility and regression

- successful temporal sequence behavior remains unchanged;
- external `PhaseDetection`, Recipe, persistence, benchmark, truth, result, CSV and debug schemas remain unchanged;
- detector version and dependency set remain unchanged unless separately authorized;
- controlled accuracy expectations are not relaxed;
- obsolete concurrency code is absent rather than dormant.

## Required source-audit evidence

The fresh independent source Auditor must verify:

- immutable observability fixtures and contract tests are byte-for-byte unchanged;
- all eight observationally equivalent collision pairs produce the same typed and canonical ambiguity family;
- no collision publishes raw or smoothed numeric oil or selects an oil candidate;
- repeated identical unresolved frames remain `NO_UPDATE` plus `PRESERVE` without numeric promotion;
- the prior dtype-ceiling, `0.40` broad-strength, `0.90` near-ceiling-fraction and `4.0` standard-deviation boolean observability switches are absent;
- the route-dependent `0.40/0.35/1.00` normalization and both route parameters are absent from the identifiability helper;
- exact `83 → 243` fixed evidence produces equal component fields and margin `-0.0137589324` for standard plus corroborated, standard-only and corroborated-only labels, with discontinuity `0`;
- the structural-plus-real brightness `-12…+4` route transition has no upward margin jump, ambiguity-to-numeric route improvement or acceptance island, while no-route positive diagnostic margin cannot publish a boundary;
- the implemented boundary uses only current observable evidence and contains no latent label, fixture ID or case-specific branch;
- intensity `235–245`, broad `82–89`, sparse texture `228–234` in both polarities, and near-ceiling support `4–14` show no isolated acceptance island and expose a continuous identifiability margin;
- the audited `239/240`, `85/86`, texture-statistics and `8/9` neighbor pairs no longer reverse independently;
- the general boundary floor, semantic likelihood formulas, preprocessing and plateau score are unchanged;
- retained clear/rapid, bright-boundary, structural, historical glare, saturated-glare, malformed Phase-A and S5-A Foam contracts remain satisfied;
- immutable contract hashes remain `818802756ebc206250f89540f06616988816b93c5e9b55b17bb42511decc8579` and `727455c5f6263a84e740fd307c9f28846af15e743c729945a4ac841a80ca3b18`;
- the Worker-owned targeted validation reports `521 passed` with no expected failure, unexpected failure, skip, xfail or conditional acceptance;
- temporal source is unchanged because existing ambiguity reduction already owns the repeated-sequence behavior;
- detector version, dependencies and external schemas remain unchanged.

Controlled comparison remains blocked until this fresh source re-audit returns `PASS`.

## Non-goals

This bounded source implementation does not:

- change preprocessing, proposal construction, semantic likelihood formulas, the general boundary floor, dependencies, detector version or external schemas;
- infer a physical glare cause or relabel latent oil truth;
- redesign temporal or Foam ownership;
- implement temporal raster history, optical flow or capture metadata;
- authorize controlled comparison or broader validation before the source audit;
- make the retained plateau-discriminability cue the acceptance owner;
- approve packaging, merge, synchronization, cleanup or S5-B completion.

## Remaining risks

The executable contract remains the immutable acceptance target for the bounded source. Any future contract-red result is not permission to weaken latent truth, relabel oil-bearing scenes as no oil, add case-ID behavior or move another local threshold cliff.

Serialization may increase per-frame latency if evidence construction is expensive. The product has only one to three Glasses, so this remains an accepted architectural trade until measured. Later profiling may identify safe stateless preprocessing work outside the owner, but must not split temporal authority or create a second validation boundary.

Broad/narrow evidence correlation under blur, fog and refractive motion, exposure-dependent full/empty classification, Glass calibration variance and debug CPU cost remain detector-evidence risks for later controlled comparison. They are not reasons to weaken serialized ownership or the observability contract.

The current gate is the fresh independent source exact-head re-audit. Controlled comparison remains blocked until that re-audit returns `PASS`.
