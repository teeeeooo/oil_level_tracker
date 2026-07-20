from __future__ import annotations

from pathlib import Path

import pytest

from oil_tracker.adapters.vision.source_video_resolver import SourceVideoMismatchError, SourceVideoResolver
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.review import ReviewBundle, ReviewGlass
from oil_tracker.domain.session import AnalysisSession, VideoMetadata


class _Reader:
    instances = []

    def __init__(self, path, metadata=None):
        self.path = Path(path)
        self.metadata = metadata or VideoMetadata(str(path), 320, 240, 30.0, 5.0, 150, "mp4v")
        self.closed = False
        self.__class__.instances.append(self)

    def close(self):
        self.closed = True


def _bundle(tmp_path: Path, candidates=()):
    recipe = InspectionRecipe.empty(320, 240, "review")
    glass = InspectionRecipe.default_glass(320, 240, 1)
    recipe.glasses.append(glass)
    metadata = VideoMetadata("original.mp4", 320, 240, 30.0, 5.0, 150, "mp4v")
    return ReviewBundle(
        root=tmp_path / "bundle",
        run_id="run",
        recipe=recipe,
        session=AnalysisSession(input_video_path="original.mp4", video_metadata=metadata),
        manifest={},
        source_video_path=str(candidates[0]) if candidates else "original.mp4",
        source_video_candidates=tuple(str(value) for value in candidates),
        source_metadata=metadata,
        analysis_start_sec=0.0,
        analysis_end_sec=5.0,
        compressor_start_sec=None,
        glasses=(ReviewGlass(glass.id, glass.name),),
        samples=(),
        events=(),
    )


def test_resolver_prefers_user_override(tmp_path):
    bundle = _bundle(tmp_path, [tmp_path / "missing.mp4"])
    bundle.root.mkdir()
    override = tmp_path / "override.mp4"
    override.write_bytes(b"video")
    resolved = SourceVideoResolver().resolve(bundle, override)
    assert resolved.path == override.resolve()
    assert resolved.used_override is True


def test_resolver_uses_recorded_existing_path(tmp_path):
    original = tmp_path / "original.mp4"
    original.write_bytes(b"video")
    bundle = _bundle(tmp_path, [original])
    bundle.root.mkdir()
    assert SourceVideoResolver().resolve(bundle).path == original.resolve()


def test_resolver_uses_bundle_or_parent_basename_fallback(tmp_path):
    bundle = _bundle(tmp_path, [Path("moved") / "original.mp4"])
    bundle.root.mkdir()
    adjacent = bundle.root.parent / "original.mp4"
    adjacent.write_bytes(b"video")
    assert SourceVideoResolver().resolve(bundle).path == adjacent.resolve()


def test_resolver_returns_missing_without_broad_search(tmp_path):
    bundle = _bundle(tmp_path, [tmp_path / "missing.mp4"])
    bundle.root.mkdir()
    result = SourceVideoResolver().resolve(bundle)
    assert result.path is None
    assert result.attempted_paths


def test_candidate_validation_accepts_resolution_and_closes_reader(tmp_path):
    path = tmp_path / "candidate.mp4"
    path.write_bytes(b"video")
    bundle = _bundle(tmp_path)
    resolver = SourceVideoResolver(lambda candidate: _Reader(candidate))
    validation = resolver.validate_candidate(bundle, path)
    assert validation.metadata.width == 320
    assert _Reader.instances[-1].closed is True


def test_candidate_validation_rejects_resolution_mismatch_and_closes_reader(tmp_path):
    path = tmp_path / "candidate.mp4"
    path.write_bytes(b"video")
    bundle = _bundle(tmp_path)
    bad = VideoMetadata(str(path), 640, 480, 30.0, 5.0, 150, "mp4v")
    resolver = SourceVideoResolver(lambda candidate: _Reader(candidate, bad))
    with pytest.raises(SourceVideoMismatchError, match="320×240"):
        resolver.validate_candidate(bundle, path)
    assert _Reader.instances[-1].closed is True


def test_candidate_validation_reports_fps_duration_codec_warnings(tmp_path):
    path = tmp_path / "candidate.mp4"
    path.write_bytes(b"video")
    bundle = _bundle(tmp_path)
    changed = VideoMetadata(str(path), 320, 240, 25.0, 7.0, 175, "h264")
    validation = SourceVideoResolver(lambda candidate: _Reader(candidate, changed)).validate_candidate(bundle, path)
    assert len(validation.warnings) == 3
