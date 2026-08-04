# Test Authoring Portability Contract

This is the repository quality contract for tests that must run on supported macOS and Windows Python environments. Apply the narrowest rule that matches the contract under test; do not normalize away a real serialized or public format requirement.

## Filesystem and text

- Compare platform-native filesystem paths as `Path` values or equivalent normalized filesystem identity, not raw `/` versus `\\` spelling.
- Assert an exact separator only when a serialized/public format explicitly owns that separator, such as a POSIX-style bundle-relative field.
- Repository UTF-8 text artifact tests must pass an explicit `encoding` to `Path.read_text()` and `Path.write_text()`.
- Non-interactive `subprocess.run()` tests must not inherit stdin accidentally. Close stdin explicitly and, for text I/O, declare UTF-8 encoding instead of depending on the host locale.

## Identity and errors

- Do not use raw ZIP/NPZ container bytes as a cross-platform logical-content identity when archive metadata can differ by platform.
- When logical identity is the contract, fingerprint deterministic logical content such as ordered keys, dtype/shape metadata and canonical bytes.
- Raw artifact hashes remain valid only when exact artifact bytes themselves are the declared contract.
- Prefer semantic error assertions when discovery order or the full rendered message is not part of the contract.

## Qt lifecycle and teardown

- Tests that depend on `QTimer`, queued signals, event delivery or another Qt event-loop behavior must own the repository `qapp` or `qtbot` lifecycle.
- `ResultReviewController` creates a `QTimer`; tests that construct it directly therefore require `qapp` or `qtbot` even when they manually call controller methods.
- Ordinary dirty registered `MainWindow` cleanup belongs to the shared pytest/pytest-qt teardown owner and must finish non-interactively.
- Tests whose subject is S9-A unsaved-close semantics remain separate: they directly prove Save, Discard, Cancel and rejected-close lifecycle behavior.
- The test process keeps one session-owned `QApplication`; headless subprocess tests must not inherit that GUI platform contract.

## Automated guard boundary

`tests/test_test_authoring_policy.py` enforces only low-false-positive repository patterns: explicit text encoding, explicit non-interactive subprocess stdin/text encoding, and Qt lifecycle ownership for direct `QTimer`/`ResultReviewController` tests. Separator literals, arbitrary error messages and ZIP/NPZ hashes are not globally linted because legitimate serialized/exact-artifact contracts exist; their owner tests and this contract remain authoritative.
