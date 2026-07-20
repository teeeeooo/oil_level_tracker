from __future__ import annotations

import csv
from pathlib import Path

from oil_tracker.domain.results import AnalysisResult


TRACKING_COLUMNS = [
    "run_id", "glass_id", "frame_index", "timestamp_sec", "fill_state",
    "raw_oil_air_level_y", "raw_oil_air_level_px_from_zero", "raw_oil_air_level_mm_from_zero",
    "smoothed_oil_air_level_px_from_zero", "smoothed_oil_air_level_mm_from_zero", "oil_air_confidence",
    "raw_foam_front_y", "raw_foam_front_px_from_zero", "raw_foam_front_mm_from_zero",
    "smoothed_foam_front_px_from_zero", "smoothed_foam_front_mm_from_zero", "foam_confidence",
    "visibility_confidence", "overall_confidence", "is_valid", "flags",
]

EVENT_COLUMNS = [
    "run_id", "glass_id", "event_type", "start_time_sec", "end_time_sec",
    "representative_frame_index", "oil_level_px", "oil_level_mm", "foam_front_px", "foam_front_mm",
    "confidence", "capture_path", "note",
]


class CsvExporter:
    def export(self, result: AnalysisResult, tracking_path: Path, events_path: Path) -> None:
        tracking_path.parent.mkdir(parents=True, exist_ok=True)
        with tracking_path.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=TRACKING_COLUMNS)
            writer.writeheader()
            for glass in result.glass_results:
                for sample in glass.samples:
                    row = {column: getattr(sample, column) for column in TRACKING_COLUMNS}
                    row["fill_state"] = sample.fill_state.value
                    row["flags"] = ";".join(sample.flags)
                    writer.writerow(row)
        with events_path.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=EVENT_COLUMNS)
            writer.writeheader()
            for glass in result.glass_results:
                for event in glass.events:
                    row = {column: getattr(event, column) for column in EVENT_COLUMNS}
                    row["event_type"] = event.event_type.value
                    writer.writerow(row)
