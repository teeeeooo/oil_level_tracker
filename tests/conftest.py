from __future__ import annotations

from contextlib import contextmanager
import os
import sys
import warnings
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TESTS_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(TESTS_ROOT))

_QT_APP_MARKER = "qt_app"
_QT_PLATFORM_ENV = "QT_QPA_PLATFORM"


@contextmanager
def _temporary_qt_platform():
    previous = os.environ.get(_QT_PLATFORM_ENV)
    injected = previous is None
    if injected:
        os.environ[_QT_PLATFORM_ENV] = "offscreen"
    try:
        yield injected
    finally:
        if injected:
            os.environ.pop(_QT_PLATFORM_ENV, None)
        elif previous is not None:
            os.environ[_QT_PLATFORM_ENV] = previous


@pytest.fixture(scope="session")
def qapp(qapp_args, qapp_cls, pytestconfig):
    """Own exactly one Qt application for every QApplication-dependent test."""
    from pytestqt.qt_compat import qt_api

    app = qt_api.QtWidgets.QApplication.instance()
    if app is None:
        with _temporary_qt_platform() as injected:
            app = qapp_cls(qapp_args)
        app.setApplicationName(pytestconfig.getini("qt_qapp_name"))
        app.setProperty("oil_tracker_test_qpa_injected", injected)
    elif not isinstance(app, qapp_cls):
        warnings.warn(
            f"Existing QApplication {app} is not an instance of qapp_cls: {qapp_cls}",
            stacklevel=2,
        )
    return app


def pytest_collection_modifyitems(items):
    """Give QApplication-dependent tests one selectable lifecycle owner."""
    for item in items:
        fixture_names = set(getattr(item, "fixturenames", ()))
        if fixture_names.intersection({"qapp", "qtbot"}):
            item.add_marker(_QT_APP_MARKER)


@pytest.fixture
def headless_subprocess_env():
    """Return an importable source-tree environment with no GUI platform contract."""
    env = os.environ.copy()
    env.pop(_QT_PLATFORM_ENV, None)
    existing = env.get("PYTHONPATH")
    paths = [str(ROOT / "src")]
    if existing:
        paths.append(existing)
    env["PYTHONPATH"] = os.pathsep.join(paths)
    return env


def _verify_qt_state(app) -> None:
    from PySide6.QtCore import QThreadPool

    visible = tuple(
        type(widget).__name__ for widget in app.topLevelWidgets() if widget.isVisible()
    )
    pool_active = QThreadPool.globalInstance().activeThreadCount()
    assert not visible, f"visible top-level widgets leaked: {visible}"
    assert pool_active == 0, f"global QThreadPool leaked {pool_active} active task(s)"


@pytest.fixture(autouse=True)
def _qt_test_lifecycle(request):
    """Verify Qt state after each QApplication-owned test without mutating it."""
    if request.node.get_closest_marker(_QT_APP_MARKER) is None:
        yield
        return
    app = request.getfixturevalue("qapp")
    yield
    _verify_qt_state(app)


@pytest.fixture
def qt_state_verifier():
    """Expose the teardown verifier for focused lifecycle regressions."""
    return _verify_qt_state
