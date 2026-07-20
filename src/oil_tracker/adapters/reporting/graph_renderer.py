from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from oil_tracker.domain.enums import FillState
from oil_tracker.domain.results import AnalysisResult, GlassAnalysisResult


class GraphRenderer:
    def render(self, result: AnalysisResult, directory: Path) -> dict[str, str]:
        directory.mkdir(parents=True, exist_ok=True)
        paths: dict[str, str] = {}
        combined = directory / "combined_levels.png"
        self._render_combined(result, combined)
        paths["combined"] = f"graphs/{combined.name}"
        for glass in result.glass_results:
            filename = f"{_safe_name(glass.glass_name)}_detail.png"
            path = directory / filename
            self._render_glass(glass, path)
            paths[glass.glass_id] = f"graphs/{filename}"
        return paths

    def _render_combined(self, result: AnalysisResult, path: Path) -> None:
        fig, ax = plt.subplots(figsize=(12, 5.5))
        for glass in result.glass_results:
            times = [s.timestamp_sec for s in glass.samples]
            oil = [np.nan if s.smoothed_oil_air_level_px_from_zero is None else s.smoothed_oil_air_level_px_from_zero for s in glass.samples]
            foam = [np.nan if s.smoothed_foam_front_px_from_zero is None else s.smoothed_foam_front_px_from_zero for s in glass.samples]
            ax.plot(times, oil, label=f"{glass.glass_name} oil-air")
            if not all(np.isnan(v) for v in foam):
                ax.plot(times, foam, linestyle="--", label=f"{glass.glass_name} foam")
        ax.axhline(0.0, linestyle=":", linewidth=1.5, label="Zero line")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Height from zero (px)")
        ax.set_title(f"Rotary Oil Level Tracking — {result.overall_state.value}")
        ax.grid(True, alpha=0.25)
        ax.legend(loc="best")
        fig.tight_layout()
        fig.savefig(path, dpi=140)
        plt.close(fig)

    def _render_glass(self, glass: GlassAnalysisResult, path: Path) -> None:
        fig, ax = plt.subplots(figsize=(12, 5.5))
        times = [s.timestamp_sec for s in glass.samples]
        oil = [np.nan if s.smoothed_oil_air_level_px_from_zero is None else s.smoothed_oil_air_level_px_from_zero for s in glass.samples]
        foam = [np.nan if s.smoothed_foam_front_px_from_zero is None else s.smoothed_foam_front_px_from_zero for s in glass.samples]
        ax.plot(times, oil, label="Oil-air level", linewidth=2)
        if not all(np.isnan(v) for v in foam):
            ax.plot(times, foam, linestyle="--", label="Foam front", linewidth=2)
        ax.axhline(0.0, linestyle=":", linewidth=1.5, label="Zero line")
        self._state_bands(ax, glass)
        for event in glass.events:
            ax.axvline(event.start_time_sec, alpha=0.12, linewidth=0.8)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Height from zero (px)")
        ax.set_title(f"{glass.glass_name} — {glass.result_state.value} — valid {glass.valid_coverage_ratio:.1%}")
        ax.grid(True, alpha=0.25)
        ax.legend(loc="best")
        fig.tight_layout()
        fig.savefig(path, dpi=140)
        plt.close(fig)

    def _state_bands(self, ax, glass: GlassAnalysisResult) -> None:
        if not glass.samples:
            return
        groups = []
        start = glass.samples[0]
        previous = start
        for current in glass.samples[1:]:
            if current.fill_state != start.fill_state:
                groups.append((start, previous))
                start = current
            previous = current
        groups.append((start, previous))
        for begin, end in groups:
            if begin.fill_state in {FillState.FULL_NO_INTERFACE, FillState.FULL_WITH_FOAM}:
                ax.axvspan(begin.timestamp_sec, end.timestamp_sec, alpha=0.07)
            elif begin.fill_state == FillState.EMPTY_NO_INTERFACE:
                ax.axvspan(begin.timestamp_sec, end.timestamp_sec, alpha=0.05)
            elif begin.fill_state == FillState.UNKNOWN_REVIEW:
                ax.axvspan(begin.timestamp_sec, end.timestamp_sec, alpha=0.12, hatch="//")
        for sample in glass.samples:
            if sample.overall_confidence < 0.35:
                ax.axvline(sample.timestamp_sec, alpha=0.04)


def _safe_name(value: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in value)
