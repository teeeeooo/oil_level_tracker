from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Protocol


class ReviewIoError(ValueError):
    """Base error exposed by application-facing review I/O ports."""


class BundleAssetError(ReviewIoError):
    """A bundle asset is missing, unsafe, or has the wrong filesystem type."""


class ResultBundleError(ReviewIoError):
    """A result bundle is unsupported, malformed, missing, or unsafe."""


class DebugTraceError(ReviewIoError):
    """A debug trace is unsupported, malformed, missing, or unsafe."""


class DebugCaseExportError(ReviewIoError):
    """A debug-case export could not be completed safely."""


class SourceVideoError(ReviewIoError):
    """A review source video is missing or unreadable."""


class SourceVideoMismatchError(SourceVideoError):
    """A selected source video is incompatible with its result bundle."""


class TruthRepositoryError(ReviewIoError):
    """A truth set is malformed, unsafe, incompatible, or cannot be stored."""


class TruthIdentityMismatchError(TruthRepositoryError):
    def __init__(self, mismatches: tuple[str, ...]) -> None:
        self.mismatches = mismatches
        super().__init__(
            "사용자 정답 파일이 현재 결과 bundle과 일치하지 않습니다.\n"
            + "\n".join(f"• {value}" for value in mismatches)
        )


class ExportCancelled(ReviewIoError):
    """An outer-layer export stopped through its cancellation contract."""


@dataclass(frozen=True)
class RecentResultEntry:
    path: str
    run_name: str = ""
    profile_name: str = ""
    source_video_name: str = ""

    def is_available(self) -> bool:
        return Path(self.path).expanduser().is_dir()

    def to_dict(self) -> dict[str, str]:
        return {
            "path": self.path,
            "run_name": self.run_name,
            "profile_name": self.profile_name,
            "source_video_name": self.source_video_name,
        }

    @classmethod
    def from_dict(cls, payload: Any) -> "RecentResultEntry":
        if not isinstance(payload, dict):
            raise ValueError("recent result entry must be an object")
        path = payload.get("path")
        if not isinstance(path, str) or not path.strip():
            raise ValueError("recent result path is missing")
        return cls(
            path=path,
            run_name=str(payload.get("run_name") or "").strip(),
            profile_name=str(payload.get("profile_name") or "").strip(),
            source_video_name=str(payload.get("source_video_name") or "").strip(),
        )


class ResultBundleReaderPort(Protocol):
    def read(self, source: str | Path) -> Any: ...


class BundleAssetResolverPort(Protocol):
    def resolve_file(
        self,
        root: str | Path,
        relative_path: str | Path,
        *,
        label: str = "결과 파일",
    ) -> Path: ...

    def resolve_directory(
        self,
        root: str | Path,
        relative_path: str | Path = ".",
        *,
        label: str = "결과 폴더",
    ) -> Path: ...


class RecentResultHistoryPort(Protocol):
    def entries(self) -> tuple[RecentResultEntry, ...]: ...

    def register_path(self, path: str | Path) -> Any: ...

    def record_bundle(self, bundle: Any) -> None: ...


class SourceVideoResolverPort(Protocol):
    def resolve(self, bundle: Any, override: str | Path | None = None) -> Any: ...

    def validate_candidate(self, bundle: Any, path: str | Path) -> Any: ...


class DebugTraceRepositoryPort(Protocol):
    index: Any

    def summaries(self, glass_id: str | None = None, reasons: set[str] | None = None) -> tuple[Any, ...]: ...

    def nearest(self, glass_id: str, timestamp_sec: float, tolerance_sec: float) -> Any: ...

    def load_record(self, record_id: str) -> Any: ...

    def load_image(self, record: Any, image_key: str) -> Any: ...

    def close(self) -> None: ...


class DebugTraceRepositoryFactory(Protocol):
    def __call__(self, bundle: Any) -> DebugTraceRepositoryPort: ...


class DebugCaseExporterPort(Protocol):
    def export(
        self,
        bundle: Any,
        repository: DebugTraceRepositoryPort,
        record_id: str,
        destination_parent: str | Path,
        *,
        source_video_path: str | Path | None = None,
    ) -> Path: ...


class TruthRepositoryPort(Protocol):
    def load(self, path: str | Path, *, expected_identity: Any = None, bundle: Any = None) -> Any: ...

    def save(
        self,
        path: str | Path,
        truth_set: Any,
        *,
        bundle_root: str | Path,
        bundle: Any = None,
        overwrite: bool = False,
        confirm_overwrite: Callable[[Path], bool] | None = None,
    ) -> Path: ...


class TruthFixtureExporterPort(Protocol):
    def export(self, **payload: Any) -> Any: ...


class ArtifactProposalPort(Protocol):
    def propose(self, frame: Any, glass: Any) -> list[Any]: ...


__all__ = [
    "ArtifactProposalPort",
    "BundleAssetError",
    "BundleAssetResolverPort",
    "DebugCaseExportError",
    "DebugCaseExporterPort",
    "DebugTraceError",
    "DebugTraceRepositoryFactory",
    "DebugTraceRepositoryPort",
    "ExportCancelled",
    "RecentResultEntry",
    "RecentResultHistoryPort",
    "ResultBundleError",
    "ResultBundleReaderPort",
    "ReviewIoError",
    "SourceVideoError",
    "SourceVideoMismatchError",
    "SourceVideoResolverPort",
    "TruthFixtureExporterPort",
    "TruthIdentityMismatchError",
    "TruthRepositoryError",
    "TruthRepositoryPort",
]
