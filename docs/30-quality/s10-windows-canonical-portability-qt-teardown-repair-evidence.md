# S10 Windows Canonical Portability & Qt Teardown Repair Evidence

## Scope and claim boundary

This document records the Mac source-repair evidence produced after Windows S10 canonical validation exposed portability and Qt teardown failures. The repair starts from authoritative `main` `cf7936fde8a24a3414d27fe3ade66bfa9af7842c` on branch `repair/s10-windows-canonical-portability-qt-teardown`.

The Mac repair does **not** establish Windows acceptance. Windows canonical `python -m pytest`, Windows DPI/manual GUI, PyInstaller, relocation and clean-PC evidence remain `NOT RUN` here and require exact-head Windows validation.

Mac repair environment:

- macOS authoritative checkout;
- Python `3.14.4`;
- pytest `9.1.1`;
- pytest-qt `4.5.0`;
- PySide6 / Qt `6.11.1`.

## Dirty MainWindow teardown diagnosis

pytest-qt 4.5.0 closes every widget registered through `qtbot.addWidget()` in its `pytest_runtest_teardown` wrapper before pytest fixture finalizers run. Its registered-widget cleanup calls `widget.close()` directly.

The repository `_qt_test_lifecycle` fixture therefore ran too late to prevent an ordinary dirty `MainWindow` from entering the production S9-A `closeEvent()` confirmation dialog. A focused Mac reproducer reached test-body `PASSED` and then blocked in teardown at the modal, confirming that the apparent next-test attribution was misleading.

## Shared lifecycle repair

Repository test lifecycle now owns a teardown-only preparation hook that runs before pytest-qt registered-widget cleanup. For an ordinary registered `MainWindow` whose Profile is dirty, that hook supplies a test-owned `Discard` response only for the impending pytest teardown close.

The production `MainWindow.closeEvent()`, `_confirm_unsaved_profile_close()`, dirty tracking and Save / Discard / Cancel behavior are unchanged. Tests whose subject is S9-A close semantics continue to invoke and assert those choices explicitly. Ordinary GUI tests no longer need local Discard monkeypatches or private Profile-baseline mutation merely to survive pytest teardown.

The existing post-close repository verifier still checks that no visible top-level widgets or global `QThreadPool` work leak. The session-owned `QApplication`, pytest-qt widget registration, and headless-subprocess separation remain intact.

Mac regression evidence after the repair:

- prior hanging readiness reproducer + Qt lifecycle + S9-A close guard: `17 passed`;
- requested ordinary GUI family: `47 passed`;
- `python -m pytest -q -m qt_app --maxfail=1`: `220 passed, 1074 deselected`;
- no `thread event dispatcher destroyed` warning/failure was observed in those runs.

No production-owned Qt thread/lifecycle defect was demonstrated on Mac after modal teardown was repaired. Windows must repeat this judgment on the exact feature head.

## Windows portability repair judgments

### UTF-8 versus cp949

Repository/process text artifacts are UTF-8 contracts. Test reads/writes that relied on the host default encoding now state UTF-8 explicitly. Non-interactive Python subprocess checks set UTF-8 child I/O and decode captured output as UTF-8. No global locale is changed.

### Native filesystem paths

The benchmark CLI prints a `Path` supplied by its service, so test expectations now use native `Path` rendering instead of requiring `/`. Serialized bundle/debug relative paths that intentionally use POSIX separators are unchanged. The unsafe-path regression now constructs a genuinely native absolute path instead of assuming `/absolute/...` is absolute on every platform.

### NPZ identity

`numpy.savez()` produces a ZIP container. Python's `ZipInfo` records different creator-system metadata on Windows and Unix, so a raw `.npz` archive SHA-256 is not a cross-platform logical-array identity. The direct 50-frame acceptance now fingerprints sorted array keys plus dtype, shape and contiguous C-order bytes, then repeats that fingerprint after loading the `.npz`.

The manifest remains an exact byte contract: its writer fixes LF newlines and its existing SHA-256 stays asserted. Production regression-dataset integrity hashes and benchmark identity authorities are not weakened by this test-only separation.

### Error semantics and non-interactive subprocesses

Path and fixture-identity regressions now assert the semantic error for the mutation under test rather than accepting unrelated alternatives caused by discovery order. The three repository test subprocess calls are non-interactive; they now use `stdin=DEVNULL`, preventing inheritance of an invalid pytest capture handle on Windows while leaving application subprocess semantics untouched.

Portability-focused Mac regression: `119 passed`. Windows behavior remains unverified until the next exact-head gate.

## Exact-head Windows continuation

The next owner must validate the same feature HEAD on supported Windows 10/11 with Python 3.14. It must rerun the focused portability/Qt regressions and fresh canonical `python -m pytest`, record terminal exit code and warnings, and specifically check whether any dispatcher-destruction or invalid-handle failure remains.

A Windows-only failure in the repaired owners returns to this repair lineage. A materially distinct runtime or packaging failure is classified separately rather than silently absorbed. Only after exact-head Windows validation should the Lane C Fresh Auditor proceed.

## PR #77 exact-head continuation: final two Windows regressions

Windows validation of PR #77 head `8cc6d0fe5640a65f5a9c91b42f62d831fd99832b` reported that the earlier portability and dirty-window teardown blockers were cleared, leaving two test-contract failures.

Result Action production behavior remains unchanged. Its local-file URL regression now converts `QUrl.toLocalFile()` back to resolved `Path` values before comparison, so filesystem identity rather than `/` versus `\\` spelling is asserted.

All four `tests/unit/test_result_review_playback.py` tests now request the repository-owned Qt lifecycle: the existing first case through `qtbot`, and the remaining timer/controller cases through `qapp`. No `ResultReviewController` timer, playback, or production event-loop behavior is changed.

Mac continuation evidence:

- both reported focused regressions: `2 passed`;
- complete Result Actions + Result Review playback unit files: `7 passed`;
- Result Review playback consumers plus shared Qt lifecycle: `30 passed`;
- collection confirms all four Result Review playback tests are selected by `-m qt_app`;
- full Mac `python -m pytest -q -m qt_app --maxfail=1`: `223 passed, 1071 deselected`, exit `0`.

Windows behavior is still unverified for the new feature head. The next gate must first rerun the two focused regressions on Windows, then `python -m pytest -m qt_app`, then canonical `python -m pytest`.
