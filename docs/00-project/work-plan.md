# Current Work Plan

- **Document status:** `VALIDATING`
- **Active milestone:** `S5-B — Oil-boundary hypothesis architecture`
- **Branch:** `feature/oil-boundary-temporal-tracking`
- **Repair-start exact head:** `7a05d1f40e175dfd2c0d7e86274559ab1899037b`
- **Repair-start exact parent:** `9dc6ff28da3524ef83ca7422218c98b9f4666763`
- **Source audit result:** `AUDIT: FAIL` — three transactional authority blockers repaired
- **Current gate:** Independent transactional authority-closure exact-head source re-audit
- **Repair status:** Source/test repair complete; pending independent re-audit
- **Controlled comparison:** Blocked until source exact-head re-audit `PASS`

This is the operational SSOT for the active milestone. The repair is not formal completion and makes no S5-B completion claim.

## Current repair state

The bounded repair closes the three source-audit blockers:

1. **Global reset atomicity**
   - a writer-priority lifecycle barrier admits normal transactions concurrently but blocks every new transaction once global reset is waiting;
   - all already-admitted transactions retain their Glass lock and lifecycle lease through validated commit and outcome handoff;
   - global reset runs only after all admitted transactions leave, increments the reset generation, invalidates pre-reset proposals and clears state atomically;
   - per-Glass locks remain independent when no global reset is pending;
   - lock ordering is lifecycle barrier -> Glass lock -> short state guard, while global reset takes lifecycle exclusivity -> state guard and never gathers/acquires Glass locks.

2. **External runner failure invariance**
   - stateful `oil_runner` injection was removed from `OpenCvPhaseDetector`;
   - the internal `OilHypothesisPipeline` is always the final validation and temporal-commit owner;
   - the remaining test seam is pre-commit input/failure probing over isolated read-only copies and cannot return a production result;
   - probe failure projects as `PipelineFailureOutcome`, compatibility `NO_UPDATE`, smoothing `PRESERVE` and no numeric oil while detector-owned temporal state remains unchanged.

3. **Commit authority closure**
   - the pipeline no longer exposes a temporal tracker/store object;
   - the former public tracker `snapshot/evaluate/commit` composition and public commit payload were removed;
   - temporal evaluation is a pure `OilShadowTemporalModel` without state authority;
   - live state is owned by a private authority that creates an opaque thread-bound transaction session;
   - commit requires that active session lease, is single-use, and is invalid after the pipeline transaction returns;
   - `temporal_snapshot()` now returns only an immutable read-only audit projection.

## Preserved behavior and scope

The repair does not change:

- observation/proposal/hypothesis algorithms, likelihood formulas or thresholds;
- accepted successful temporal transition policy;
- closed canonical outcome variants or external `PhaseDetection` shape;
- detector version `opencv-phase-detector-s5b-typed-production-v1`;
- Recipe/settings, persistence, benchmark, truth, result, CSV or debug schemas;
- S5-A Foam ownership and behavior;
- raster isolation, dependencies, lock files or workflows;
- the two deferred controlled-accuracy expectations.

No legacy oil fallback was reintroduced.

## Validation evidence

Executed with project `.venv` Python `3.14.4` after the final source changes:

- transactional/failure/concurrency focused suite:
  - command: `PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_oil_shadow_temporal.py tests/test_oil_transactional_boundary.py tests/test_oil_shadow_evidence.py tests/test_oil_shadow_observations.py`;
  - result: `51 passed in 4.50s`;
- production cutover and consumer suite:
  - command: `PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_oil_production_cutover.py tests/test_oil_detector_integration.py tests/test_oil_fill_state_classifier.py tests/test_oil_temporal_tracker.py tests/test_foam_fill_state_policy.py`;
  - result: `35 passed in 2.75s`;
- full repository suite, executed once:
  - command: `PYTHONPATH=src .venv/bin/python -m pytest -q`;
  - result: `768 passed, 2 failed in 54.92s`;
  - no native Qt crash occurred in this run;
  - the two failures are exactly the pre-recorded deferred controlled-accuracy findings below, with no new failure.

- syntax/import compilation: `PYTHONPATH=src .venv/bin/python -m compileall -q src tests` passed;
- whitespace/error check: `git diff --check` passed with no output.

## Deterministic concurrency and failure coverage

Event/barrier-based tests cover:

- a new Glass attempting entry after global reset becomes a waiting writer;
- global reset attempted after commit but before outcome handoff completes;
- reset crossing two active Glass transactions while a third transaction waits;
- same-Glass serialized prepare/commit/publish ordering;
- different-Glass concurrent admission and isolation;
- stale, replay and pre-reset session rejection;
- commit-hook, Phase A/B, temporal evaluation and outcome-preparation prior-state invariance;
- external state mutation followed by invalid pre-commit failure without detector-state mutation;
- removal of direct pipeline temporal-store and stateful runner capabilities;
- S5-A Foam and consumer failure projection non-regression.

## Deferred controlled accuracy findings

The two existing findings remain unchanged and were not relaxed:

- clear-oil raw detection coverage is `0.5714285714285714`, below expected `1.0`;
- `no-interface-to-visible` frame 3 still has no numeric raw oil recovery.

They remain controlled detector-accuracy findings for the later comparison gate. They are not classified as repair regressions.

## Remaining risks and downstream sequence

Independent source re-audit must verify the lifecycle barrier, transaction-session capability closure, external-runner removal and complete changed scope. Validation architecture redesign, test slimming, pytest marker classification and Qt-suite restructuring remain later S5-C planning input and are not part of this repair.

Controlled comparison, canonical real-video validation, Windows/manual validation, packaging, merge and cleanup remain unauthorized.

1. Independent transactional authority-closure exact-head source re-audit.
2. Controlled base/feature comparison only after re-audit `PASS`.
3. Later canonical, Windows/manual, packaging and merge gates under separate authority.

## Latest recorded closeout

- **Result:** Three transactional source-audit blockers repaired; pending independent exact-head re-audit.
- **Starting exact head:** `7a05d1f40e175dfd2c0d7e86274559ab1899037b`.
- **Starting parent:** `9dc6ff28da3524ef83ca7422218c98b9f4666763`.
- **Implemented boundary:** lifecycle-atomic global reset, internal-only validated commit sessions and internal production pipeline ownership.
- **Validation:** focused suites `51 passed` and `35 passed`; full suite `768 passed, 2 unchanged deferred controlled-accuracy failures`.
- **Current gate:** Independent transactional authority-closure exact-head source re-audit.
- **Resulting exact SHA:** Reported by the Worker final report, not self-recorded in this commit.
