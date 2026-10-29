"""Print the inspections and their analyses as short text lines, for Windows result requests.

Usage: python scripts/inspection_summary.py [--data DATA_FOLDER]
Read-only. The default data folder is Documents\\OilLevelTracker. The source SHA-256 of every
analysed inspection is computed again from its video, when the video is still there.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

from oil_tracker.adapters.storage import locations
from oil_tracker.adapters.storage.files import sha256_of
from oil_tracker.adapters.storage.inspection_files import ANALYSIS_FILE, CACHE, IMAGE_KINDS, InspectionFolders
from oil_tracker.adapters.storage.recipe_files import RecipeFolder
from oil_tracker.application.ports import InspectionNotFound, RecipeNotFound
from oil_tracker.domain.enums import InspectionState
from oil_tracker.domain.recipe import Glass, Recipe

POSITION = (("cx", "center_x"), ("cy", "center_y"), ("rx", "radius_x"), ("ry", "radius_y"))


def recipe_diff(glass: Glass, stored: Recipe | None) -> str:
    """How the inspection's copy of a Glass differs from the stored Recipe: "none", or each change."""
    if stored is None:
        return "recipe_missing"
    original = next((g for g in stored.glasses if g.id == glass.id), None)
    if original is None:
        return "glass_missing"
    changes = [
        f"{label} {getattr(glass.ellipse, field) - getattr(original.ellipse, field):+g}"
        for label, field in POSITION
        if getattr(glass.ellipse, field) != getattr(original.ellipse, field)
    ]
    if glass.zero_line_y != original.zero_line_y:
        changes.append(f"zero {glass.zero_line_y - original.zero_line_y:+g}")
    return " ".join(changes) or "none"


def has_piece(folders: InspectionFolders, inspection_id: str, glass_id: str, kind: str, index: int) -> bool:
    try:
        folders.image_piece(inspection_id, glass_id, kind, index)
    except InspectionNotFound:
        return False
    return True


def seconds_between(start: str, end: str) -> float:
    return (datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--data", type=Path, default=None)
    args = parser.parse_args(argv)

    data = args.data or locations.default_data_folder()
    if args.data is None:
        print(f"documents={locations.documents_folder()}")
    folders = InspectionFolders(data / locations.INSPECTIONS)
    recipes = RecipeFolder(data / locations.RECIPES)
    print(f"folder={folders.location}")
    listing = folders.list_inspections()
    print(f"inspections={len(listing.inspections)} unreadable={len(listing.unreadable)}")
    for name, reason in listing.unreadable:
        print(f'unreadable folder="{name}" reason="{reason}"')

    hashes: dict[str, str] = {}
    for entry in reversed(listing.inspections):  # oldest first, as they were made
        inspection, folder = entry.inspection, folders.location / entry.folder_name
        video, settings = inspection.video, inspection.settings
        try:
            stored = recipes.load(inspection.recipe.id)
        except RecipeNotFound:
            stored = None
        compressor = "-" if settings.compressor_start_sec is None else f"{settings.compressor_start_sec:.1f}"
        print(
            f'inspection folder="{entry.folder_name}" name="{inspection.name or ""}" state={inspection.state.value} '
            f'failure="{inspection.failure or ""}" video="{video.name}" bytes={video.size_bytes} '
            f"frames={video.frame_count} fps={video.fps:.3f} range={settings.start_sec:.1f}-{settings.end_sec:.1f} "
            f'compressor={compressor} recipe="{inspection.recipe.name}" created_at={inspection.created_at} '
            f"recipe_updated_at={stored.updated_at if stored else '-'}"
        )
        for glass in inspection.recipe.glasses:
            e = glass.ellipse
            print(
                f'  glass name="{glass.name}" cx={e.center_x:g} cy={e.center_y:g} rx={e.radius_x:g} '
                f"ry={e.radius_y:g} zero={glass.zero_line_y:g} mode={glass.judgment_rule.mode.value} "
                f'recipe_diff="{recipe_diff(glass, stored)}"'
            )

        partial = "yes" if (folder / f"{CACHE}.partial").exists() else "no"
        stored_analysis = folders.load_analysis(inspection.id)
        if stored_analysis is None:
            print(f"  analysis none partial={partial}")
            continue
        analysis = stored_analysis.analysis
        written = (folder / CACHE / ANALYSIS_FILE).stat().st_mtime - datetime.fromisoformat(inspection.created_at).timestamp()
        check = "-"
        if inspection.state is InspectionState.ANALYSED:
            path = Path(video.path)
            if not path.is_file():
                check = "video_missing"
            else:
                if video.path not in hashes:
                    hashes[video.path] = sha256_of(path)
                check = "same" if hashes[video.path] == video.sha256 else "different"
        print(
            f"  analysis finished_at={analysis.finished_at} "
            f"seconds={seconds_between(inspection.created_at, analysis.finished_at):.0f} "
            f"cache_written={written:.1f} times={len(analysis.times)} partial={partial} "
            f"sha256={(video.sha256 or '-')[:12]} sha256_check={check}"
        )
        names = {glass.id: glass.name for glass in inspection.recipe.glasses}
        drafts = {draft.glass_id: draft.oil for draft in analysis.drafts}
        for layout in stored_analysis.images:
            ys = drafts[layout.glass_id].ys
            files = sum(has_piece(folders, inspection.id, layout.glass_id, kind, index)
                        for kind in IMAGE_KINDS for index in range(layout.pieces))
            empty = 100 * sum(y is None for y in ys) / max(1, len(ys))
            print(
                f'  cache glass name="{names.get(layout.glass_id, layout.glass_id)}" y0={layout.y0} '
                f"rows={layout.rows} pieces={layout.pieces} files={files}/{2 * layout.pieces} empty={empty:.1f}%"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
