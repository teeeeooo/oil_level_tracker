from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices

from oil_tracker.adapters.storage.bundle_asset_resolver import BundleAssetError, BundleAssetResolver


class ResultActionError(ValueError):
    pass


class ResultActionService:
    def __init__(self, resolver: BundleAssetResolver | None = None, opener=None) -> None:
        self.resolver = resolver or BundleAssetResolver()
        self.opener = opener or QDesktopServices.openUrl

    def open_report(self, bundle_or_root) -> Path:
        root = _root(bundle_or_root)
        path = self.resolver.resolve_file(root, "report.html", label="결과 보고서")
        self._open(path, "결과 보고서")
        return path

    def open_folder(self, bundle_or_root) -> Path:
        root = _root(bundle_or_root)
        path = self.resolver.resolve_directory(root, ".", label="결과 폴더")
        self._open(path, "결과 폴더")
        return path

    def open_capture(self, bundle_or_root, capture_path: str) -> Path:
        if not str(capture_path or "").strip():
            raise ResultActionError("선택한 이벤트에 기록된 캡처가 없습니다.")
        root = _root(bundle_or_root)
        path = self.resolver.resolve_file(root, capture_path, label="이벤트 캡처")
        self._open(path, "이벤트 캡처")
        return path

    def _open(self, path: Path, label: str) -> None:
        try:
            opened = bool(self.opener(QUrl.fromLocalFile(str(path))))
        except Exception as exc:
            raise ResultActionError(f"{label}을 열 수 없습니다: {exc}") from exc
        if not opened:
            raise ResultActionError(f"운영체제에서 {label}을 열지 못했습니다: {path}")


def _root(bundle_or_root) -> Path:
    if isinstance(bundle_or_root, (str, Path)):
        root = bundle_or_root
    else:
        root = getattr(bundle_or_root, "root", None)
    if root in (None, ""):
        raise ResultActionError("결과 bundle 경로가 없습니다.")
    return Path(root)


__all__ = ["BundleAssetError", "ResultActionError", "ResultActionService"]
