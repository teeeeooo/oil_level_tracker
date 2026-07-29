# Current Work Plan

- **Document status:** `ACTIVE`
- **Active milestone:** `S5-C — Canonical/Qt validation stabilization`
- **Authoritative branch:** `main`
- **Close task-start main:** `df2c49c7fc0db5a44fca26a8da49f581288bff4e`
- **Previous milestone:** `S5-B — Oil-boundary hypothesis architecture` — `DONE`
- **Current gate:** Worker implementation complete on the bounded S5-C feature branch; fresh independent Lane C audit pending
- **Current blocker:** none
- **Next action:** independently audit the exact feature head, canonical/Qt focused validation, headless non-regression and mergeability
- **S6 Windows/manual, real-video and packaging validation:** not started

S5-C is a separate validation-stability milestone. It must preserve the merged S5-B typed oil-boundary architecture, observability contract, serialized temporal owner, S5-A Foam independence, detector schemas and headless validation behavior.

## S5-C scope

The bounded S5-C task owns only:

- stable `QApplication` / `QCoreApplication` lifecycle ownership;
- isolation of GUI-dependent fixtures and tests;
- removal of unnecessary duplicate GUI/canonical coverage;
- preservation of deterministic non-GUI and headless validation;
- explicit evidence for any intentionally retained canonical/Qt exclusions.

S5-C does not own detector threshold changes, oil/Foam semantic changes, S5-B architecture redesign, real-video qualification, Windows/manual acceptance or packaging.

## S5-C Worker evidence

- **Exact base:** `a6f0a95c862ebeaeabc25ad140172dfc7b37d3e1`
- **Feature branch:** `feature/s5c-canonical-qt-validation-stabilization`
- **Unmodified canonical baseline:** `1160 passed, 1 failed` on Python `3.14.4`, PySide6 `6.11.1` and pytest-qt `4.5.0`; no Qt crash or teardown failure occurred.
- **Baseline failure class:** the headless CLI child process could not import the source tree because it implicitly relied on editable installation; root `conftest.py` also leaked `QT_QPA_PLATFORM=offscreen` to all tests and child processes.
- **Application evidence:** the first `qtbot` group created one `QApplication`; `QCoreApplication.instance()` resolves to the same object. A QObject-only focused test created no application.
- **Lifecycle choice:** one session `qapp`, temporary offscreen platform injection, automatic `qt_app` ownership and non-mutating post-test state verification. No `QCoreApplication` subprocess owner, suite serialization or per-test GUI subprocess is used.
- **Coverage ownership:** no acceptance test was removed or moved. `python -m pytest -m qt_app` is a focused selection of canonical tests, not duplicate mandatory coverage.
- **Focused Qt result:** `161 passed, 1005 deselected`.
- **Canonical result:** `1166 passed in 131.68s`; no failure, crash, skip, xfail or conditional acceptance.
- **Order evidence:** GUI-before-headless and headless-before-GUI each reported `2 passed`.
- **Headless result:** `12 passed in 6.30s`; CLI import uses an explicit source-tree environment, excludes Qt platform state and imports neither PySide6 nor application bootstrap.
- **Intentional non-runs:** S6 real-video, Windows/manual, packaging and clean-PC acceptance remain not started.
- **Next gate:** fresh independent Lane C Auditor on the exact PR head.

## Latest recorded closeout

### S5-B — merged and closed

- **Result:** `DONE`
- **Accepted PR head:** `df5b4604b0eeb2b67eb7608beceb90298f0fb5f0`
- **Squash merge / authoritative main:** `df2c49c7fc0db5a44fca26a8da49f581288bff4e`
- **Pull request:** `#56 — feat: implement S5-B typed oil-boundary architecture`
- **Deterministic dataset infrastructure:** `AUDIT: PASS`
- **Performance-source exact-head audit:** `AUDIT: PASS`
- **Final deterministic comparison:** `COMPARISON: PASS`
- **Process ratio:** `1.4809208190318381×`
- **Wall ratio:** `1.4835741070817687×`
- **Performance limit:** `1.5×`
- **Final focused validation:** `427 passed`
- **Pipeline failures:** `0`

The completed S5-B scope establishes typed, evidence-preserving oil-boundary and no-interface hypotheses, canonical ambiguity for observationally unresolved oil/glare collisions, one serialized temporal-state owner, one immutable store replacement boundary and non-rejecting detector projection. The observability contract is complete, S5-A Foam independence is preserved, external schemas remain compatible and the accepted CPU limit is satisfied.

### Intentional non-runs at S5-B Close

- full repository suite;
- canonical/Qt validation;
- E2E validation;
- Windows/manual and real-video validation;
- packaging validation.

These remain successor-gate obligations and were not required to repeat the accepted exact-head source audit or deterministic comparison.

## Open risks and successor boundary

S5-B has no unresolved merge or Close blocker. Later evidence may still expose blur, fog, refractive-motion, exposure, Glass-calibration or long-duration runtime limitations; those findings must be handled by their owning successor milestone without weakening the merged observability or Foam contracts.

The active sequence remains:

`S5-C` → `S6` → `S7 / Phase 2C-4` → Phase 2D reassessment.
