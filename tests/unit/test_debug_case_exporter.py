from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import cv2
import numpy as np
import pytest

from oil_tracker.adapters.storage.debug_case_exporter import DebugCaseExportError, DebugCaseExporter
from oil_tracker.domain.debug_trace import DebugTraceRecord


def _record():
    return DebugTraceRecord(
        schema_version=1,
        record_id="record-1",
        run_id="run-1",
        glass_id="glass-1",
        glass_name="관찰창",
        frame_index=15,
        timestamp_sec=0.5,
        capture_reasons=("low_confidence",),
        fill_state="PARTIAL_VISIBLE",
        confidence={"overall": 0.4},
        flags=("LOW_CONFIDENCE",),
        positions={"raw_oil_y": 10.0},
        state={"previous_state": "EMPTY_NO_INTERFACE"},
        candidates=(),
        images={"overlay": "x", "original_roi": "y"},
    )


class _Repository:
    def __init__(self, *, missing_overlay=False):
        self.record = _record()
        self.missing_overlay = missing_overlay

    def load_record(self, record_id):
        assert record_id == self.record.record_id
        return self.record

    def load_image(self, record, key):
        if key == "overlay" and self.missing_overlay:
            return None
        if key in {"overlay", "original_roi", "normalized", "sobel", "canny", "effective_mask", "glare_mask", "foam_mask"}:
            image = np.full((24, 32), 100, dtype=np.uint8)
            return np.dstack([image, image, image]) if key in {"overlay", "original_roi"} else image
        return None


def _bundle(tmp_path: Path, root_name: str = "bundle"):
    root = tmp_path / root_name
    root.mkdir()
    recipe = root / "recipe_snapshot.oilrecipe"
    recipe.write_text('{"schema_version":1}', encoding="utf-8")
    return SimpleNamespace(
        run_id="run-1",
        root=root,
        files={"recipe_snapshot": recipe},
    )


def _video(path: Path):
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), 10.0, (64, 48))
    if not writer.isOpened():
        pytest.skip("mp4v VideoWriter is unavailable")
    for index in range(20):
        frame = np.full((48, 64, 3), index * 8, dtype=np.uint8)
        writer.write(frame)
    writer.release()


def _bundle_snapshot(root: Path):
    snapshot = {}
    for path in sorted(root.rglob("*"), key=lambda value: value.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix()
        if path.is_dir():
            snapshot[relative] = ("directory", b"")
        elif path.is_file():
            snapshot[relative] = ("file", path.read_bytes())
        else:
            snapshot[relative] = ("other", b"")
    return snapshot


def _symlink_or_skip(link: Path, target: Path):
    try:
        link.symlink_to(target, target_is_directory=True)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"directory symlink is unavailable: {exc}")


def test_package_without_source_keeps_required_trace_files_and_warning(tmp_path):
    bundle = _bundle(tmp_path)
    destination = tmp_path / "내보내기"
    output = DebugCaseExporter().export(bundle, _Repository(), "record-1", destination)
    assert output.parent == destination
    for filename in (
        "manifest.json",
        "candidate_overlay.png",
        "roi_crop.png",
        "detection_debug.json",
        "recipe_snapshot.oilrecipe",
    ):
        assert (output / filename).is_file()
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["record_id"] == "record-1"
    assert manifest["source_video"] is None
    assert any("원본 영상" in warning for warning in manifest["warnings"])
    assert not (output / "short_clip.mp4").exists()
    assert not list(destination.glob(".*.tmp-*"))


def test_package_with_source_writes_frame_context_and_raw_short_clip(tmp_path):
    bundle = _bundle(tmp_path)
    video = tmp_path / "source.mp4"
    _video(video)
    output = DebugCaseExporter().export(bundle, _Repository(), "record-1", tmp_path / "exports", source_video_path=video)
    for filename in ("frame.png", "context_before.png", "context_after.png", "short_clip.mp4"):
        assert (output / filename).is_file()
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["source_video"] == str(video)
    assert "frame.png" in manifest["decoded_timestamps"]


class _ClipFailExporter(DebugCaseExporter):
    def _write_short_clip(self, directory, source, timestamp, warnings):
        warnings.append("short clip codec/writer initialization failed")


def test_short_clip_failure_is_warning_and_keeps_required_package(tmp_path):
    bundle = _bundle(tmp_path)
    video = tmp_path / "source.mp4"
    _video(video)
    output = _ClipFailExporter().export(bundle, _Repository(), "record-1", tmp_path / "exports", source_video_path=video)
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert any("short clip" in warning for warning in manifest["warnings"])
    assert (output / "candidate_overlay.png").is_file()
    assert (output / "detection_debug.json").is_file()
    assert not (output / "short_clip.mp4").exists()


def test_existing_package_directory_is_not_overwritten(tmp_path, monkeypatch):
    import oil_tracker.adapters.storage.debug_case_exporter as module

    class _FixedDatetime:
        @classmethod
        def now(cls):
            class _Value:
                def strftime(self, _format):
                    return "debug_case_fixed"
            return _Value()

    monkeypatch.setattr(module, "datetime", _FixedDatetime)
    bundle = _bundle(tmp_path)
    destination = tmp_path / "exports"
    destination.mkdir()
    existing = destination / "debug_case_fixed"
    existing.mkdir()
    marker = existing / "keep.txt"
    marker.write_text("keep")
    with pytest.raises(DebugCaseExportError, match="덮어쓸 수 없습니다"):
        DebugCaseExporter().export(bundle, _Repository(), "record-1", destination)
    assert marker.read_text() == "keep"


def test_failure_cleans_temporary_output_and_keeps_bundle_unchanged(tmp_path, monkeypatch):
    import oil_tracker.adapters.storage.debug_case_exporter as module

    class _FixedDatetime:
        @classmethod
        def now(cls):
            class _Value:
                def strftime(self, _format):
                    return "debug_case_failure"
            return _Value()

    monkeypatch.setattr(module, "datetime", _FixedDatetime)
    bundle = _bundle(tmp_path)
    original_recipe = (bundle.root / "recipe_snapshot.oilrecipe").read_bytes()
    destination = tmp_path / "exports"
    with pytest.raises(DebugCaseExportError, match="overlay"):
        DebugCaseExporter().export(bundle, _Repository(missing_overlay=True), "record-1", destination)
    assert not (destination / "debug_case_failure").exists()
    assert not list(destination.glob(".*.tmp-*"))
    assert (bundle.root / "recipe_snapshot.oilrecipe").read_bytes() == original_recipe


def test_bundle_root_destination_is_rejected_without_mutation(tmp_path):
    bundle = _bundle(tmp_path)
    before = _bundle_snapshot(bundle.root)

    with pytest.raises(DebugCaseExportError, match="공식 결과 bundle 내부"):
        DebugCaseExporter().export(bundle, _Repository(), "record-1", bundle.root)

    assert _bundle_snapshot(bundle.root) == before
    assert not list(bundle.root.glob("debug_case_*"))
    assert not list(bundle.root.glob(".*.tmp-*"))


def test_missing_direct_bundle_child_is_rejected_before_directory_creation(tmp_path):
    bundle = _bundle(tmp_path)
    destination = bundle.root / "exports"
    before = _bundle_snapshot(bundle.root)

    with pytest.raises(DebugCaseExportError, match="공식 결과 bundle 내부"):
        DebugCaseExporter().export(bundle, _Repository(), "record-1", destination)

    assert not destination.exists()
    assert _bundle_snapshot(bundle.root) == before


def test_missing_deep_bundle_child_is_rejected_without_partial_output(tmp_path):
    bundle = _bundle(tmp_path)
    destination = bundle.root / "assets" / "debug_exports"
    before = _bundle_snapshot(bundle.root)

    with pytest.raises(DebugCaseExportError, match="공식 결과 bundle 내부"):
        DebugCaseExporter().export(bundle, _Repository(), "record-1", destination)

    assert not destination.exists()
    assert not (bundle.root / "assets").exists()
    assert _bundle_snapshot(bundle.root) == before


def test_external_symlink_to_bundle_root_is_rejected(tmp_path):
    bundle = _bundle(tmp_path)
    external = tmp_path / "external"
    external.mkdir()
    link = external / "link"
    _symlink_or_skip(link, bundle.root)
    before = _bundle_snapshot(bundle.root)

    with pytest.raises(DebugCaseExportError, match="공식 결과 bundle 내부"):
        DebugCaseExporter().export(bundle, _Repository(), "record-1", link)

    assert _bundle_snapshot(bundle.root) == before
    assert not list(bundle.root.glob("debug_case_*"))


def test_external_symlink_to_bundle_descendant_is_rejected(tmp_path):
    bundle = _bundle(tmp_path)
    assets = bundle.root / "assets"
    assets.mkdir()
    (assets / "keep.txt").write_text("keep", encoding="utf-8")
    external = tmp_path / "external"
    external.mkdir()
    link = external / "link"
    _symlink_or_skip(link, assets)
    before = _bundle_snapshot(bundle.root)

    with pytest.raises(DebugCaseExportError, match="공식 결과 bundle 내부"):
        DebugCaseExporter().export(bundle, _Repository(), "record-1", link)

    assert _bundle_snapshot(bundle.root) == before
    assert not list(assets.glob("debug_case_*"))


def test_bundle_parent_destination_creates_sibling_package_and_keeps_bundle_unchanged(tmp_path):
    bundle = _bundle(tmp_path)
    before = _bundle_snapshot(bundle.root)

    output = DebugCaseExporter().export(bundle, _Repository(), "record-1", bundle.root.parent)

    assert output.parent == bundle.root.parent.resolve()
    assert output.parent != bundle.root.resolve()
    assert output.is_dir()
    assert _bundle_snapshot(bundle.root) == before


def test_similar_prefix_external_destination_is_allowed(tmp_path):
    bundle = _bundle(tmp_path, "oil_level_analysis_1")
    destination = tmp_path / "oil_level_analysis_10"
    before = _bundle_snapshot(bundle.root)

    output = DebugCaseExporter().export(bundle, _Repository(), "record-1", destination)

    assert output.parent == destination.resolve()
    assert output.is_dir()
    assert _bundle_snapshot(bundle.root) == before


def test_relative_external_destination_is_resolved_and_allowed(tmp_path, monkeypatch):
    bundle = _bundle(tmp_path)
    working = tmp_path / "working"
    working.mkdir()
    monkeypatch.chdir(working)
    before = _bundle_snapshot(bundle.root)

    output = DebugCaseExporter().export(bundle, _Repository(), "record-1", Path("relative_exports"))

    assert output.parent == (working / "relative_exports").resolve()
    assert output.is_dir()
    assert _bundle_snapshot(bundle.root) == before


def test_rejected_bundle_destination_can_retry_to_external_directory(tmp_path):
    bundle = _bundle(tmp_path)
    before = _bundle_snapshot(bundle.root)
    exporter = DebugCaseExporter()

    with pytest.raises(DebugCaseExportError, match="공식 결과 bundle 내부"):
        exporter.export(bundle, _Repository(), "record-1", bundle.root / "exports")

    output = exporter.export(bundle, _Repository(), "record-1", tmp_path / "external-exports")
    assert output.is_dir()
    assert _bundle_snapshot(bundle.root) == before
    assert not list((tmp_path / "external-exports").glob(".*.tmp-*"))
