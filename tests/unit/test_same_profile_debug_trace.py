from __future__ import annotations

import numpy as np

from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.session import DebugTraceLevel, VideoMetadata
from oil_tracker.ui.controllers.workbench_controller import WorkbenchController


class _Reader:
    def __init__(self, path):
        self.metadata = VideoMetadata(str(path), 320, 240, 10.0, 4.0, 40, "fake")

    def read_at(self, _timestamp):
        return np.zeros((240, 320, 3), dtype=np.uint8), 0, 0.0

    def close(self):
        pass


def test_same_profile_new_video_does_not_inherit_full_trace_level():
    controller = WorkbenchController(None, None, None, reader_factory=_Reader)
    snapshot = InspectionRecipe.empty(320, 240, "snapshot")
    snapshot.glasses.append(InspectionRecipe.default_glass(320, 240, 1))
    prepared = controller.prepare_same_profile_video(snapshot, 2.0, "new.mp4")
    try:
        assert prepared.session.debug_trace_level is DebugTraceLevel.BASIC
    finally:
        prepared.close()
