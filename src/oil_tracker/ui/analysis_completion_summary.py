from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PureWindowsPath

from oil_tracker.domain.enums import ResultState


@dataclass(frozen=True)
class FinalRunGlassSummary:
    name: str
    result_state: ResultState


@dataclass(frozen=True)
class FinalRunSummary:
    output_path: Path
    overall_state: ResultState
    glasses: tuple[FinalRunGlassSummary, ...]
    warning_count: int
    error_count: int
    run_name: str = ""
    profile_name: str = ""
    source_video_path: str = ""
    finalized_metadata_available: bool = False

    @property
    def source_video_name(self) -> str:
        return _basename(self.source_video_path)


def build_final_run_summary(result, output_path: str | Path, bundle=None) -> FinalRunSummary:
    run_name = ""
    profile_name = ""
    source_video_path = ""
    metadata_available = bundle is not None
    if bundle is not None:
        run_name = _text(getattr(bundle, "run_name", ""))
        recipe = getattr(bundle, "recipe", None)
        profile_name = _text(getattr(recipe, "name", ""))
        source_video_path = _text(getattr(bundle, "source_video_path", ""))

    glasses = tuple(
        FinalRunGlassSummary(
            name=_text(getattr(glass, "glass_name", "")) or "이름 없는 Glass",
            result_state=glass.result_state,
        )
        for glass in result.glass_results
    )
    return FinalRunSummary(
        output_path=Path(output_path),
        overall_state=result.overall_state,
        glasses=glasses,
        warning_count=len(result.warnings),
        error_count=len(result.errors),
        run_name=run_name,
        profile_name=profile_name,
        source_video_path=source_video_path,
        finalized_metadata_available=metadata_available,
    )


def _text(value) -> str:
    return str(value or "").strip()


def _basename(value: str) -> str:
    text = _text(value)
    if not text:
        return ""
    if "\\" in text:
        return PureWindowsPath(text).name
    return Path(text).name
