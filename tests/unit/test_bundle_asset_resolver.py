from __future__ import annotations

from pathlib import Path

import pytest

from oil_tracker.adapters.storage.bundle_asset_resolver import BundleAssetError, BundleAssetResolver


def test_resolves_report_capture_unicode_and_root_folder(tmp_path):
    root = tmp_path / "결과 번들"
    root.mkdir()
    report = root / "report.html"
    report.write_text("ok", encoding="utf-8")
    captures = root / "captures"
    captures.mkdir()
    capture = captures / "유면 장면.png"
    capture.write_bytes(b"png")
    resolver = BundleAssetResolver()
    assert resolver.resolve_file(root, "report.html") == report.resolve()
    assert resolver.resolve_file(root, "captures/유면 장면.png") == capture.resolve()
    assert resolver.resolve_directory(root) == root.resolve()


@pytest.mark.parametrize("unsafe", ["/tmp/report.html", "../report.html", "captures/../../report.html"])
def test_rejects_absolute_and_parent_escape(tmp_path, unsafe):
    root = tmp_path / "bundle"
    root.mkdir()
    with pytest.raises(BundleAssetError):
        BundleAssetResolver().resolve_file(root, unsafe)


def test_rejects_missing_and_type_mismatch(tmp_path):
    root = tmp_path / "bundle"
    root.mkdir()
    directory = root / "report.html"
    directory.mkdir()
    resolver = BundleAssetResolver()
    with pytest.raises(BundleAssetError, match="파일"):
        resolver.resolve_file(root, "report.html")
    with pytest.raises(BundleAssetError, match="존재하지"):
        resolver.resolve_file(root, "missing.png")
    file_path = root / "not-a-folder"
    file_path.write_text("x", encoding="utf-8")
    with pytest.raises(BundleAssetError, match="폴더"):
        resolver.resolve_directory(root, "not-a-folder")


def test_rejects_symlink_that_escapes_bundle_root(tmp_path):
    root = tmp_path / "bundle"
    root.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("secret", encoding="utf-8")
    link = root / "capture.png"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("symlink creation is not available")
    with pytest.raises(BundleAssetError, match="밖"):
        BundleAssetResolver().resolve_file(root, "capture.png")
