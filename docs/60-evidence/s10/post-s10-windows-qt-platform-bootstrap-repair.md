# Post-S10 Windows Qt Platform Bootstrap Repair

## Scope and authority

This document records a bounded packaging maintenance repair discovered after S10 was already accepted and closed. It is not S10 reopening, S11 detector work or S12 UI work.

Starting authority:

- repository: `teeeeooo/oil_level_tracker`;
- base `main == origin/main`: `f52e477e71f562744ccb27846c9248a8b46fb310`;
- focused branch: `repair/windows-qt-platform-bootstrap`.

The reported Windows packaged-startup failure is reproduction input. Mac source inspection independently confirmed that `packaging/pyinstaller/oil_tracker.spec` had no custom runtime hook while its entry script is `src/oil_tracker/__main__.py`, which imports PySide6 GUI modules at module import time.

## Ownership decision

The repair belongs to the PyInstaller GUI artifact, not to source-tree GUI or CLI startup. `packaging/pyinstaller/runtime_hooks/windows_qt_platform.py` is registered as a custom runtime hook in the GUI spec.

Local PyInstaller 6.21 source inspection confirmed that custom runtime hooks are placed ahead of PyInstaller-defined runtime hooks and therefore execute before the packaged entry script. The hook contains no Qt import and establishes the platform contract before PySide6 GUI import/initialization.

On `sys.platform == "win32"`, the hook assigns:

`QT_QPA_PLATFORM=windows`


This is intentionally an assignment rather than `setdefault()`. The one-folder artifact is a Windows GUI product and must not let an inherited `offscreen`, `minimal` or otherwise conflicting QPA value override its supported native platform. A user/system environment setting is external input, not package authority.

The assignment is still bounded: it runs only inside the PyInstaller runtime-hook surface and only when `sys.platform == "win32"`. Source-tree GUI, macOS execution and `oil-tracker-cli` do not import this hook.

## Regression prevention

`tests/test_windows_packaging_bootstrap.py` verifies that:

- the PyInstaller `Analysis` registers exactly the repository Windows Qt runtime hook;
- the packaged GUI entry remains `oil_tracker/__main__.py`;
- the hook file is owned beside the spec and imports no PySide6 module;
- absent or conflicting inherited QPA values become `windows` on simulated Windows runtime;
- non-Windows runtime does not force `windows`;
- source-tree GUI and CLI entry modules do not import the packaging hook.

The existing `tests/test_benchmark_cli.py::test_cli_import_is_headless_and_does_not_initialize_qt` remains the dynamic CLI/headless non-regression owner.


## Validation boundary

Mac/source-tree validation can prove repository wiring, hook behavior under a simulated platform value, CLI isolation and that PyInstaller accepts the spec. It cannot prove the Windows bootloader, Windows Qt plugin loading, a visible native window or clean-PC startup.

The exact feature head therefore requires read-only Windows packaged validation:

1. start from the exact feature head with no source edits;
2. ensure no user/system `QT_QPA_PLATFORM` prerequisite is present and clear the validation-shell value;
3. perform a clean PyInstaller one-folder build;
4. launch `dist\\RotaryOilLevelTracker\\RotaryOilLevelTracker.exe` and confirm normal native GUI startup/close;
5. confirm the package behaves as the Windows QPA owner, not an external environment dependency;
6. perform one bounded child-process conflict probe with `QT_QPA_PLATFORM=offscreen` and confirm the native GUI still appears, then remove the probe variable;
7. record OS/build, Python, PyInstaller/PySide6/Qt versions, build result, launch result and source cleanliness.

Windows packaged PASS is not inferred from Mac evidence. After that validation passes, the next gate is `Fresh Lane C Exact-Head Auditor`; only the merge/close owner returns the project to `S11-A — Real-field failure attribution and truth/corpus planning`.


## Mac implementation evidence

The stabilized targeted suite covered the new package-bootstrap contract, repository test-authoring policy, shared Qt lifecycle, the existing dynamic CLI/headless import contract and GUI smoke. Result: `29 passed`.

An earlier aggregation run exposed a Worker-authored test-isolation defect: executing the runtime hook in the shared pytest process leaked its direct environment mutation into later macOS `qapp` creation. The hook behavior tests were moved to isolated child processes; production bootstrap code did not change to accommodate the test.

A real Mac PyInstaller configuration build used Python 3.14.4 and PyInstaller 6.21.0 with isolated `/tmp` work/dist output. It completed successfully and the build log recorded the custom `windows_qt_platform.py` runtime hook before PyInstaller's `pyi_rth_pyside6.py` hook. This proves repository packaging wiring/order on the Mac build host, not Windows GUI startup.

Mac packaged output, Windows bootloader/plugin behavior, Windows native GUI startup and clean-PC execution are distinct evidence classes. The required Windows packaged validation remains `NOT RUN` by this Worker.
