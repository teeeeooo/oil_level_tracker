from __future__ import annotations

from pathlib import Path
import re

import cv2

from oil_tracker.application.ports.progress import AnalysisCancelled
from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
from oil_tracker.domain.results import AnalysisResult


class ImageCaptureStore:
    def create_event_captures(
        self,
        result: AnalysisResult,
        video_path: str,
        directory: Path,
        *,
        cancellation=None,
        progress=None,
    ) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        events = tuple(
            (glass, event)
            for glass in result.glass_results
            for event in glass.events
            if event.representative_frame_index is not None
        )
        reader = OpenCvVideoReader(video_path)
        completed = 0
        try:
            for glass, event in events:
                _check_cancelled(cancellation)
                try:
                    frame, _, _ = reader.read_at(event.start_time_sec)
                except Exception:
                    completed += 1
                    if progress is not None:
                        progress(completed, len(events))
                    continue
                label = f"{glass.glass_name} | {event.event_type.value} | {event.start_time_sec:.2f}s"
                cv2.rectangle(frame, (8, 8), (min(frame.shape[1] - 8, 760), 44), (0, 0, 0), -1)
                cv2.putText(frame, label, (16, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)
                safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", f"{glass.glass_name}_{event.event_type.value}_{event.start_time_sec:.2f}")
                filename = f"{safe}.png"
                path = directory / filename
                if cv2.imwrite(str(path), frame):
                    event.capture_path = f"captures/{filename}"
                completed += 1
                if progress is not None:
                    progress(completed, len(events))
        finally:
            reader.close()


def _check_cancelled(cancellation) -> None:
    if cancellation is not None and cancellation.cancelled:
        raise AnalysisCancelled("Analysis was cancelled while creating result images.")
