# Current Work Plan

- **Document status:** `VALIDATING`
- **Active milestone:** `S5-B — Oil-boundary hypothesis architecture`
- **Branch:** `feature/oil-boundary-temporal-tracking`
- **Repair-start exact head:** `a8e308c514762e0bca0af0273b2bfcb01ab4bc29`
- **Repair-start exact parent:** `7a05d1f40e175dfd2c0d7e86274559ab1899037b`
- **Second source re-audit:** `AUDIT: FAIL` — production transaction seams required elimination
- **Current gate:** Independent production transaction seam-elimination exact-head source re-audit
- **Repair status:** Source/test repair complete; pending independent re-audit
- **Controlled comparison:** Blocked until source exact-head re-audit `PASS`

This operational plan records the bounded S5-B2 repair. It makes no S5-B completion, controlled-comparison, canonical-validation, Windows, packaging or merge claim.

## Repair result

The repair removes replaceable production transaction authority:

1. **Production hooks eliminated**
   - `OilHypothesisPipeline` no longer accepts `temporal_evaluator`, `outcome_preparer`, `commit_hook`, `handoff_hook`, `transaction_admitted_hook` or `global_reset_waiting_hook`;
   - `OpenCvPhaseDetector` no longer accepts `oil_runner` or `oil_precommit_probe`;
   - lifecycle condition locks, Glass locks and commit-to-return flow invoke no user-supplied callback;
   - test synchronization and failure injection now use monkeypatching, private owner instrumentation and deterministic event/barrier wrappers only.

2. **Fixed transaction ownership**
   - the former generic `_OilTemporalAuthority.execute(glass_id, callback)` and `_TemporalTransactionSession` object graph were removed;
   - live Glass state, versions, locks, reset generation and writer-priority lifecycle barrier are owned directly by `OilHypothesisPipeline`;
   - evidence construction, Phase A, fixed internal temporal evaluation, Phase B, outcome preparation/validation, commit and return execute in one lexical `run()` transaction;
   - no public or production-object callback/session/commit operation can receive an arbitrary `next_state`;
   - the public operation surface is `run`, `reset`, `temporal_state_count` and immutable `temporal_snapshot` only.

3. **Fixed temporal evaluator and transition coherence**
   - production always constructs and uses its own private `OilShadowTemporalModel`;
   - Phase B validates decision/current identity, state/resource bounds and load-bearing decision-to-next-state coherence without re-evaluating the transition;
   - accepted outcome Y must equal committed `accepted_y`;
   - reacquisition pending Y/count, accepted/reacquired velocity, no-interface and unavailable counters/stability/clearing, and ambiguous-state preservation are validated;
   - prepared outcome variant, confidence, margin, reason, mode, selected/pending hypothesis and state Y must agree with the same validated transition.

4. **Lifecycle safety retained**
   - writer-priority global reset blocks new transactions after a reset waiter appears;
   - admitted transactions retain lifecycle and Glass ownership through state replacement and outcome return preparation;
   - global reset never gathers Glass locks and runs only after admitted transactions leave;
   - global reset re-entry from an active transaction fails closed rather than self-deadlocking;
   - same-Glass ordering and different-Glass parallelism remain intact;
   - all condition counters and locks release through context-manager `finally` paths.

## Preserved scope

Unchanged:

- observation/proposal/hypothesis algorithms, likelihoods, thresholds and accepted temporal mathematics;
- closed canonical outcomes and external `PhaseDetection` shape;
- detector version `opencv-phase-detector-s5b-typed-production-v1`;
- Recipe/settings, persistence, benchmark, truth, result, CSV and debug schemas;
- S5-A Foam ownership and behavior;
- raster isolation, dependencies, lock files and workflows;
- the two deferred controlled-accuracy expectations.

No legacy oil fallback was introduced.

## Final validation evidence

Executed with project `.venv` Python `3.14.4` after the final source changes:

- transactional/concurrency/failure focused suite:
  - command: `PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_oil_shadow_temporal.py tests/test_oil_transactional_boundary.py tests/test_oil_shadow_evidence.py tests/test_oil_shadow_observations.py`;
  - result: `58 passed in 4.52s`;
- production consumer suite:
  - command: `PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_oil_production_cutover.py tests/test_oil_detector_integration.py tests/test_oil_fill_state_classifier.py tests/test_oil_temporal_tracker.py tests/test_foam_fill_state_policy.py`;
  - result: `35 passed in 2.53s`;
- full repository suite, executed once:
  - command: `PYTHONPATH=src .venv/bin/python -m pytest -q`;
  - result: `775 passed, 2 failed in 56.39s`;
  - no native Qt crash occurred;
  - both failures are the unchanged controlled-accuracy findings below and no new failure occurred;
- syntax/import compilation: `PYTHONPATH=src .venv/bin/python -m compileall -q src tests` — passed;
- whitespace/error check: `git diff --check` — passed with no output.

## Deterministic coverage

Tests cover:

- reset waiter re-entry rejection without deadlock;
- global reset versus newly arriving transactions;
- commit-to-outcome reset exclusion;
- reset crossing multiple active Glass transactions;
- same-Glass ordering and different-Glass parallelism;
- stale, replay, cross-thread, cross-Glass and pre-reset rejection;
- evidence, Phase A, temporal evaluation, Phase B, outcome preparation/validation and commit failure prior-state invariance;
- all temporal decision variants and outcome-to-state semantic coherence;
- absence of constructor evaluator/outcome/commit/handoff/session seams;
- consumer failure projection, S5-A Foam and raster isolation non-regression.

## Deferred controlled accuracy findings

Unchanged and not relaxed:

- clear-oil raw detection coverage remains `0.5714285714285714`, below expected `1.0`;
- `no-interface-to-visible` frame 3 still has no numeric raw oil recovery.

These remain later controlled-comparison findings, not repair regressions.

## Remaining risks and downstream sequence

Independent re-audit must verify the complete diff, lexical transaction ownership, absence of callback/session/commit seams, transition coherence and lifecycle lock ordering. Validation redesign and suite slimming remain later S5-C planning input.

1. Independent production transaction seam-elimination exact-head source re-audit.
2. Controlled base/feature comparison only after re-audit `PASS`.
3. Later canonical, Windows/manual, packaging and merge gates under separate authority.

## Latest recorded closeout

- **Result:** Production transaction seams eliminated; pending independent exact-head source re-audit.
- **Starting exact head:** `a8e308c514762e0bca0af0273b2bfcb01ab4bc29`.
- **Starting parent:** `7a05d1f40e175dfd2c0d7e86274559ab1899037b`.
- **Implemented boundary:** Fixed lexical pipeline transaction, private fixed evaluator, inline validated commit and callback-free lifecycle barrier.
- **Validation:** Focused suites `58 passed` and `35 passed`; full suite `775 passed, 2 unchanged deferred controlled-accuracy failures`.
- **Current gate:** Independent production transaction seam-elimination exact-head source re-audit.
- **Resulting exact SHA:** Reported by the Worker final report, not self-recorded in this commit.
