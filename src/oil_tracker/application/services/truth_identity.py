from __future__ import annotations

import hashlib
import json
from pathlib import Path

from oil_tracker.domain.user_truth import TruthBundleIdentity


def build_truth_bundle_identity(bundle) -> TruthBundleIdentity:
    """Build the immutable identity used by truth-set application workflows."""

    metadata = bundle.source_metadata or bundle.session.video_metadata
    width = int(metadata.width) if metadata is not None and metadata.width > 0 else int(bundle.recipe.reference_frame_width)
    height = int(metadata.height) if metadata is not None and metadata.height > 0 else int(bundle.recipe.reference_frame_height)
    fps = float(metadata.fps) if metadata is not None else 0.0
    duration = float(metadata.duration_sec) if metadata is not None else 0.0
    snapshot = bundle.files.get("recipe_snapshot") if getattr(bundle, "files", None) else None
    snapshot_path = Path(snapshot) if snapshot else Path(bundle.root) / "recipe_snapshot.oilrecipe"
    if snapshot_path.is_file():
        digest = sha256_file(snapshot_path)
    else:
        canonical = json.dumps(
            bundle.recipe.to_dict(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        digest = hashlib.sha256(canonical).hexdigest()
    basename = ""
    for raw in (*getattr(bundle, "source_video_candidates", ()), getattr(bundle, "source_video_path", "")):
        if raw:
            basename = Path(raw).name
            if basename:
                break
    return TruthBundleIdentity(
        run_id=str(bundle.run_id),
        recipe_id=str(bundle.recipe.recipe_id),
        recipe_snapshot_hash=digest,
        source_video_basename=basename,
        source_width=width,
        source_height=height,
        source_fps=fps,
        source_duration_sec=duration,
    )


def sha256_file(path: str | Path, *, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


__all__ = ["build_truth_bundle_identity", "sha256_file"]
