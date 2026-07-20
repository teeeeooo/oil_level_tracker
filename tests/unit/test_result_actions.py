from __future__ import annotations

from pathlib import Path

import pytest

from oil_tracker.adapters.storage.bundle_asset_resolver import BundleAssetError
from oil_tracker.ui.result_actions import ResultActionError, ResultActionService


def _bundle(tmp_path):
    root = tmp_path / "bundle"
    root.mkdir()
    (root / "report.html").write_text("report", encoding="utf-8")
    (root / "captures").mkdir()
    (root / "captures" / "event.png").write_bytes(b"png")
    return root


def test_report_folder_and_capture_use_local_file_urls(tmp_path):
    root = _bundle(tmp_path)
    opened = []
    service = ResultActionService(opener=lambda url: opened.append(url.toLocalFile()) or True)
    assert service.open_report(root).name == "report.html"
    assert service.open_folder(root) == root.resolve()
    assert service.open_capture(root, "captures/event.png").name == "event.png"
    assert opened == [
        str((root / "report.html").resolve()),
        str(root.resolve()),
        str((root / "captures" / "event.png").resolve()),
    ]


def test_missing_report_and_capture_are_clear_errors(tmp_path):
    root = tmp_path / "bundle"
    root.mkdir()
    service = ResultActionService(opener=lambda _url: True)
    with pytest.raises(BundleAssetError, match="보고서"):
        service.open_report(root)
    with pytest.raises(ResultActionError, match="기록된 캡처"):
        service.open_capture(root, "")
    with pytest.raises(BundleAssetError, match="존재하지"):
        service.open_capture(root, "captures/missing.png")


def test_invalid_capture_path_and_os_open_failure_are_rejected(tmp_path):
    root = _bundle(tmp_path)
    service = ResultActionService(opener=lambda _url: False)
    with pytest.raises(BundleAssetError):
        service.open_capture(root, "../outside.png")
    with pytest.raises(ResultActionError, match="운영체제"):
        service.open_report(root)
