from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from oil_tracker.adapters.storage.image_capture_store import ImageCaptureStore
from oil_tracker.application.services.report_presentation import (
    ReportGlassPresentation,
    ReportLandmark,
    ReportPresentation,
)
from oil_tracker.domain.enums import EventType, FillState, ResultState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.results import AnalysisResult, EventMarker, GlassAnalysisResult, TrackingSample


def _video(path: Path) -> None:
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), 5.0, (320, 240))
    assert writer.isOpened()
    for _ in range(3):
        frame = np.full((240, 320, 3), 70, dtype=np.uint8)
        cv2.circle(frame, (160, 120), 70, (120, 140, 170), -1)
        writer.write(frame)
    writer.release()


def test_capture_store_writes_only_selected_glass_focused_landmarks(tmp_path):
    video = tmp_path / "source.avi"
    _video(video)
    recipe = InspectionRecipe.empty(320, 240, "capture")
    config = InspectionRecipe.default_glass(320, 240, 1)
    recipe.glasses.append(config)
    sample = TrackingSample(
        "run",
        config.id,
        0,
        0.0,
        FillState.PARTIAL_VISIBLE,
        raw_oil_air_level_y=config.geometry.zero_line_y - 10,
        smoothed_oil_air_level_px_from_zero=10.0,
        smoothed_foam_front_px_from_zero=20.0,
    )
    source_event = EventMarker("run", config.id, EventType.MAXIMUM_OIL_LEVEL, 0.0)
    landmark = ReportLandmark(
        EventType.MAXIMUM_OIL_LEVEL,
        0.0,
        "관측 최고 유면",
        "fixture",
        sample,
        "maximum",
        source_event=source_event,
    )
    report_glass = ReportGlassPresentation(
        config.id,
        config.name,
        ResultState.PASS,
        "합격",
        "summary",
        "note",
        "judgment",
        (landmark,),
        (),
        1,
        0,
    )
    presentation = ReportPresentation(ResultState.PASS, "합격", (report_glass,))
    result = AnalysisResult(
        "run",
        ResultState.PASS,
        [GlassAnalysisResult(config.id, config.name, ResultState.PASS, [sample], [source_event])],
        "start",
        "end",
    )

    output = tmp_path / "captures"
    ImageCaptureStore().create_event_captures(
        result,
        str(video),
        output,
        recipe=recipe,
        presentation=presentation,
    )

    files = list(output.glob("*.png"))
    assert len(files) == 1
    image = cv2.imread(str(files[0]))
    assert image is not None
    assert image.shape[:2] != (240, 320)
    assert max(image.shape[:2]) >= 320
    assert landmark.capture_path.startswith("captures/")
    assert source_event.capture_path == landmark.capture_path
