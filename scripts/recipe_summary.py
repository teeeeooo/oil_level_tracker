"""Print saved Recipes and video facts as short text lines, for Windows result requests.

Usage: python scripts/recipe_summary.py [--folder RECIPES_FOLDER] [--video PATH ...]
Read-only. The default folder is Documents\\OilLevelTracker\\Recipes.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from oil_tracker.adapters.storage import locations
from oil_tracker.adapters.storage.recipe_files import RecipeFolder, file_name_for
from oil_tracker.adapters.video.frames import open_video
from oil_tracker.application.ports import VideoUnreadable
from oil_tracker.domain.recipe import recipe_problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--folder", type=Path, default=None)
    parser.add_argument("--video", type=Path, action="append", default=[])
    args = parser.parse_args(argv)

    folder = args.folder or locations.default_data_folder() / locations.RECIPES
    if args.folder is None:
        print(f"documents={locations.documents_folder()}")
    print(f"folder={folder}")
    listing = RecipeFolder(folder).list_recipes()
    print(f"recipes={len(listing.recipes)} unreadable={len(listing.unreadable)}")
    for name, reason in listing.unreadable:
        print(f'unreadable file="{name}" reason="{reason}"')
    for recipe in listing.recipes:
        path = folder / file_name_for(recipe.name)
        frame = recipe.reference_frame
        print(
            f'recipe name="{recipe.name}" file="{path.name}" bytes={path.stat().st_size} '
            f"frame={frame.width}x{frame.height} source=\"{frame.source_name}\" t={frame.time_sec:.3f} "
            f"jpeg={len(frame.jpeg)} glasses={len(recipe.glasses)} problems={len(recipe_problems(recipe))}"
        )
        for glass in recipe.glasses:
            e, rule = glass.ellipse, glass.judgment_rule
            print(
                f'  glass name="{glass.name}" cx={e.center_x:g} cy={e.center_y:g} rx={e.radius_x:g} '
                f"ry={e.radius_y:g} zero={glass.zero_line_y:g} mode={rule.mode.value} "
                f"limit={rule.recovery_limit_sec:g} hold={rule.stable_hold_sec:g} "
                f"cov={rule.minimum_valid_coverage_ratio:g} allowed_sec={rule.allowed_sec:g} "
                f"allowed_px={rule.allowed_px:g}"
            )
    for video in args.video:
        try:
            opened = open_video(video)
        except VideoUnreadable as error:
            print(f'video name="{video.name}" error="{error}"')
            continue
        info = opened.info
        opened.close()
        print(
            f'video name="{info.name}" bytes={video.stat().st_size} size={info.width}x{info.height} '
            f"fps={info.fps:.3f} frames={info.frame_count} duration={info.duration_sec:.1f}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
