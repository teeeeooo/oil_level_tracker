# Current Work Plan

- **Document status:** `VALIDATING`
- **Active milestone:** `S5-B — Oil-boundary hypothesis architecture`
- **Branch:** `feature/oil-boundary-temporal-tracking`
- **Task-start exact head:** `e937a4b77319377598c6927a9967559bf249e631`
- **Task-start exact parent:** `64093e359cee24831f6c88184791fc05ef166331`
- **Last S5-B2 re-audit:** `AUDIT: FAIL`
- **Blocking finding:** Current-observation internal kind coherence gap
- **Current gate:** Fresh independent S5-B2 exact-head re-audit
- **Current state:** Current-observation kind validation repair completed on the feature worktree

This is the operational SSOT for the active milestone. Closeout results follow the [closeout policy](./closeout-policy.md); branch-local completion is not a formal completion declaration.

## Blocker and repair

The previous validator checked temporal status, temporal decision `observation_kind` and current-observation Python class, but did not independently revalidate the frozen current observation's internal `kind` field after construction.

`validate_production_result()` now requires all three axes to agree:

1. temporal status;
2. temporal decision `observation_kind`;
3. current-observation class and its internal `kind`.

Boundary and reacquisition validation also enforce `ShadowBoundaryObservation.kind is BOUNDARY` inside the shared canonical-hypothesis helper.

The existing canonical identity/content/Y checks, reacquisition no-numeric rule, no-interface and unavailable no-selection rules, ambiguous optional-Y coherence and unsupported-status rejection remain unchanged.

## Adversarial evidence

Five normally constructed frozen current observations were copied and then had only `kind` forged with `object.__setattr__()`:

- boundary accepted: boundary current forged to `NO_INTERFACE`;
- reacquisition pending: boundary current forged to `AMBIGUOUS`;
- no-interface accepted: no-interface current forged to `BOUNDARY`;
- ambiguous: ambiguous current forged to `UNAVAILABLE`;
- unavailable: unavailable current forged to `NO_INTERFACE`.

Each malformed exact-type result fails closed through the existing detector exception boundary:

- `oil_pipeline_available` is false;
- `OIL_PIPELINE_FAILURE` is present;
- raw and smoothed oil Y are absent;
- no oil candidate is selected;
- no legacy candidate or fallback is used;
- the input frame remains unchanged;
- Foam candidates, confidence, metrics and debug images match the invalid-return baseline.

Normal coherent boundary, reacquisition, no-interface, ambiguous and unavailable combinations continue to validate.

## Validation evidence

Project `.venv` uses Python 3.14.4 with pytest 9.1.1.

- Focused production-cutover and fill-state scope: `47 passed`.
- Non-controlled oil/Foam/benchmark/result/fixture/debug compatibility scope: `250 passed`.
- Controlled oil benchmark, executed separately: `1 passed, 2 failed`.

The controlled failures remain deferred accuracy findings:

- clear-oil raw detection coverage is `0.5714285714285714`, below the expected `1.0`;
- `no-interface-to-visible` frame 3 still has no numeric raw oil recovery.

No controlled expectation was removed, relaxed or hidden. Controlled comparison remains blocked until the fresh independent exact-head re-audit returns `PASS`.

## Compatibility and non-goals

- Observation, proposal, evidence, likelihood, thresholds and temporal transitions are unchanged.
- Detector version, candidate projection semantics and external/persisted/debug schemas are unchanged.
- S5-A Foam algorithm and temporal ownership are unchanged.
- No dependency or environment mutation was performed.
- Roadmap and architecture documents are unchanged.
- Controlled comparison, canonical validation, Windows/manual GUI validation, packaging validation, merge and cleanup were not performed.

## Next action

Perform a fresh independent S5-B2 exact-head re-audit of the immutable repair head. Controlled comparison remains prohibited until that audit returns `PASS`.

## Latest recorded closeout

- **Repair result:** Current-observation internal kind validation and forged-kind adversarial evidence completed on the feature worktree.
- **Task-start exact head:** `e937a4b77319377598c6927a9967559bf249e631`
- **Task-start exact parent:** `64093e359cee24831f6c88184791fc05ef166331`
- **Prior audit:** Independent S5-B2 exact-head re-audit returned `AUDIT: FAIL` for current-observation internal kind coherence.
- **Completed source scope:** Current class/kind/status coherence validation only.
- **Completed test scope:** Five forged-kind exact-type results fail closed while all coherent typed status combinations remain valid.
- **Current gate:** Fresh independent S5-B2 exact-head re-audit.
- **Deferred findings:** The two controlled oil accuracy failures remain unchanged and outside this repair.
