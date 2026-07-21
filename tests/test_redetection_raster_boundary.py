from __future__ import annotations

from types import SimpleNamespace

import numpy as np
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QImage

from oil_tracker.ui.redetection_comparison_coordinator import RedetectionComparisonCoordinator
from review_raster_fixtures import debug_artifact_presenter


class _Viewer(QObject):
    redetectionRequested = Signal()
    bundleAboutToChange = Signal()
    bundleChanged = Signal(object)
    sourceVideoChanged = Signal(object)
    selectedGlassChanged = Signal(str)
    viewerClosing = Signal()

    def __init__(self, repository):
        super().__init__()
        self.debug_repository = repository
        self.debug_artifact_presenter = debug_artifact_presenter()
        self.bundle = None
        self.current_time = 0.0


class _Controller(QObject):
    started = Signal(int, str)
    progress = Signal(object)
    completed = Signal(object)
    failed = Signal(int, str)
    cancelled = Signal(int)

    def __init__(self, repository):
        super().__init__()
        self.current_workspace = SimpleNamespace(repository=repository)

    def invalidate(self, _generation):
        pass

    def close(self):
        pass


class _Repository:
    def __init__(self, value):
        self.value = value
        self.calls = []

    def load_image(self, record, key):
        self.calls.append((record, key))
        return self.value.copy()


class _Panel:
    def __init__(self):
        self.official = []
        self.rerun = []

    def set_official_artifact(self, key, image, error):
        snapshot = None if image is None else QImage(image).copy()
        self.official.append((key, snapshot, error))

    def set_rerun_artifact(self, key, image, error):
        snapshot = None if image is None else QImage(image).copy()
        self.rerun.append((key, snapshot, error))


def test_redetection_official_and_rerun_artifacts_cross_ui_as_detached_qimages():
    official_repository = _Repository(np.full((12, 20, 3), 40, dtype=np.uint8))
    rerun_repository = _Repository(np.full((8, 16), 90, dtype=np.uint8))
    viewer = _Viewer(official_repository)
    controller = _Controller(rerun_repository)
    coordinator = RedetectionComparisonCoordinator(object(), viewer, controller)
    first = _Panel()
    second = _Panel()
    coordinator.window = SimpleNamespace(candidate_compare=first, artifact_compare=second)
    coordinator.current_official_record = object()
    coordinator.current_rerun_record = object()

    coordinator._load_official_artifact("overlay")
    coordinator._load_rerun_artifact("normalized")

    for panel in (first, second):
        official_key, official_image, official_error = panel.official[-1]
        rerun_key, rerun_image, rerun_error = panel.rerun[-1]
        assert official_key == "overlay"
        assert rerun_key == "normalized"
        assert official_error == rerun_error == ""
        assert isinstance(official_image, QImage) and not official_image.isNull()
        assert isinstance(rerun_image, QImage) and not rerun_image.isNull()
        assert (official_image.width(), official_image.height()) == (20, 12)
        assert (rerun_image.width(), rerun_image.height()) == (16, 8)

    first.official[-1][1].fill(0)
    assert second.official[-1][1].pixelColor(0, 0).red() == 40
    assert official_repository.calls
    assert rerun_repository.calls
