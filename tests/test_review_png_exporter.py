from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtGui import QColor, QImage

from oil_tracker.adapters.storage.review_png_exporter import (
    ReviewPngDestinationError,
    ReviewPngEncodingError,
    ReviewPngExporter,
    ReviewPngWriteError,
)


def _image(width=320, height=240, rgb=(10, 20, 30)):
    image = QImage(width, height, QImage.Format.Format_RGB32)
    image.fill(QColor(*rgb))
    return image


def test_unicode_destination_suffix_parent_and_original_resolution(tmp_path):
    destination = tmp_path / "긴 경로" / "검토 장면.jpeg"
    output = ReviewPngExporter().export(_image(), destination)
    assert output == (tmp_path / "긴 경로" / "검토 장면.png").resolve()
    assert output.is_file()
    decoded = QImage(str(output))
    assert not decoded.isNull()
    assert (decoded.width(), decoded.height()) == (320, 240)
    color = decoded.pixelColor(0, 0)
    assert (color.red(), color.green(), color.blue()) == (10, 20, 30)
    assert not destination.exists()


def test_successful_export_atomically_finalizes_without_partial_file(tmp_path):
    output = ReviewPngExporter().export(_image(17, 11), tmp_path / "scene.png")
    assert output.is_file()
    assert list(tmp_path.glob(".*.tmp-*")) == []
    assert (QImage(str(output)).width(), QImage(str(output)).height()) == (17, 11)


def test_encoding_failure_is_distinct_and_leaves_no_partial_file(tmp_path):
    exporter = ReviewPngExporter(encoder=lambda _image: b"")
    with pytest.raises(ReviewPngEncodingError, match="빈 결과"):
        exporter.export(_image(), tmp_path / "failed.png")
    assert not (tmp_path / "failed.png").exists()
    assert list(tmp_path.glob(".*.tmp-*")) == []


def test_write_failure_is_distinct_and_cleans_temporary_file(tmp_path):
    def fail_replace(_source, _destination):
        raise OSError("replace blocked")

    exporter = ReviewPngExporter(replacer=fail_replace)
    with pytest.raises(ReviewPngWriteError, match="저장할 수 없습니다"):
        exporter.export(_image(), tmp_path / "failed.png")
    assert not (tmp_path / "failed.png").exists()
    assert list(tmp_path.glob(".*.tmp-*")) == []


def test_protected_bundle_destination_is_rejected_without_mutation(tmp_path):
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    sentinel = bundle / "analysis_manifest.json"
    sentinel.write_text("official", encoding="utf-8")
    with pytest.raises(ReviewPngDestinationError, match="공식 결과 bundle 내부"):
        ReviewPngExporter().export(
            _image(),
            bundle / "review.png",
            protected_roots=(bundle,),
        )
    assert sentinel.read_text(encoding="utf-8") == "official"
    assert not (bundle / "review.png").exists()
    assert list(bundle.glob(".*.tmp-*")) == []


def test_repeated_export_obeys_explicit_overwrite_policy(tmp_path):
    destination = tmp_path / "repeat.png"
    exporter = ReviewPngExporter()
    exporter.export(_image(rgb=(1, 2, 3)), destination)
    with pytest.raises(ReviewPngDestinationError, match="덮어쓸 수 없습니다"):
        exporter.export(_image(rgb=(4, 5, 6)), destination, overwrite=False)
    original = QImage(str(destination)).pixelColor(0, 0)
    assert (original.red(), original.green(), original.blue()) == (1, 2, 3)
    exporter.export(_image(rgb=(4, 5, 6)), destination, overwrite=True)
    replaced = QImage(str(destination)).pixelColor(0, 0)
    assert (replaced.red(), replaced.green(), replaced.blue()) == (4, 5, 6)


def test_general_and_debug_highlight_snapshots_remain_distinct(tmp_path):
    exporter = ReviewPngExporter()
    general = exporter.export(_image(rgb=(20, 30, 40)), tmp_path / "general.png")
    debug = exporter.export(_image(rgb=(80, 90, 100)), tmp_path / "debug.png")
    general_color = QImage(str(general)).pixelColor(0, 0)
    debug_color = QImage(str(debug)).pixelColor(0, 0)
    assert general_color != debug_color
