# Current Work Plan

- **Document status:** `VALIDATING`
- **Active milestone:** `S5-B — Oil-boundary hypothesis architecture`
- **Branch:** `feature/oil-boundary-temporal-tracking`
- **Task-start exact head:** `64093e359cee24831f6c88184791fc05ef166331`
- **Task-start exact parent:** `f8ad80f69ecbab4033725f61ab6a8afbed7f15e5`
- **Last S5-B2 cutover audit:** `AUDIT: FAIL`
- **Blocking finding:** Malformed typed-result coherence validation gap
- **Current gate:** Fresh independent S5-B2 exact-head re-audit
- **Current state:** Typed result coherence validation repair completed on the feature worktree

This is the operational SSOT for the active milestone. Closeout results follow the [closeout policy](./closeout-policy.md); branch-local completion is not formal completion.

## Blocker and repair

The production cutover validator previously accepted some exact `OilShadowFrameResult` values whose current observation, temporal status, selected hypothesis identity or projected Y contradicted one another. Such a result could reach the compatibility projection and create official numeric oil output despite being internally malformed.

`validate_production_result()` now validates each supported temporal status against its required current-observation type and observation kind. Boundary and reacquisition decisions must reference the same canonical hypothesis content and identity, accepted boundary Y must agree across decision/current/canonical evidence, ambiguous projected Y must agree with the current ambiguous observation, and unsupported statuses fail closed.

## Failure projection

A coherence-validation failure is handled by the existing detector exception boundary and becomes a typed unavailable result:

- no raw or smoothed numeric oil Y;
- no selected oil candidate;
- `OIL_PIPELINE_FAILURE` is present;
- no legacy fallback or candidate source is used;
- Foam detection, Foam temporal processing and Foam debug evidence continue from the original frame;
- the input frame remains unchanged.

## Validation evidence

Project `.venv` uses Python 3.14.4 with pytest 9.1.1.

- Focused production-cutover and fill-state scope: `42 passed`.
- Non-controlled oil/Foam/benchmark/result/fixture/debug compatibility scope: `245 passed`.
- Controlled oil benchmark, executed separately: `1 passed, 2 failed`.

The controlled failures are unchanged deferred findings:

- clear-oil raw detection coverage is `0.5714285714285714`, below the expected `1.0`;
- `no-interface-to-visible` frame 3 still has no numeric raw oil recovery.

No controlled expectation was removed, relaxed or hidden. Controlled comparison remains blocked until the fresh independent exact-head re-audit returns `PASS`.

## Compatibility and non-goals

- Observation, proposal, evidence, likelihood and temporal-transition algorithms are unchanged.
- Detector version, candidate projection semantics and external/persisted/debug schemas are unchanged.
- S5-A Foam algorithm and temporal ownership are unchanged.
- No dependency or environment mutation was performed.
- No controlled comparison, canonical validation, Windows/manual GUI validation, packaging validation, merge or cleanup is part of this repair.

## Next action

Perform a fresh independent S5-B2 exact-head re-audit of the immutable repair head. Controlled comparison remains prohibited until that audit returns `PASS`.

## Latest recorded closeout

- **Repair result:** Typed result coherence validator and adversarial evidence completed on the feature worktree.
- **Task-start exact head:** `64093e359cee24831f6c88184791fc05ef166331`
- **Task-start exact parent:** `f8ad80f69ecbab4033725f61ab6a8afbed7f15e5`
- **Prior audit:** Independent S5-B2 production-cutover audit returned `AUDIT: FAIL` for malformed typed-result coherence validation.
- **Completed source scope:** Status/current-observation, canonical hypothesis identity/content and projected-Y coherence validation only.
- **Completed test scope:** Exact-type adversarial combinations fail closed while normal boundary, no-interface, ambiguous, unavailable and reacquisition combinations remain valid.
- **Current gate:** Fresh independent S5-B2 exact-head re-audit.
- **Deferred findings:** The two controlled oil accuracy failures remain unchanged and are not repaired by this task.
