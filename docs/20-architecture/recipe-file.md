# Recipe File

**Status:** `ACTIVE`. Schema version 1, 2026-10-29.

This document owns the Recipe file format. The contents and the rules come
from the [Product SSOT](../10-product/product.md) §3, §5 and §8. The code
is `src/oil_tracker/adapters/storage/recipe_files.py`.

## Location and name

- **Folder:** `<data folder>\Recipes\`. The data folder is
  `Documents\OilLevelTracker\`.
- **File name:** the Recipe name plus `.recipe.json`, made safe for Windows:
  - `< > : " / \ | ? *` and control characters become `_`;
  - trailing dots and spaces are removed;
  - reserved device names (`CON`, `NUL`, `COM1`, `LPT1`, …) get a leading
    `_`.
- **Uniqueness:** two Recipes cannot share a file name. File names compare
  without case, as on Windows.
- **Renaming** a Recipe writes the new file, then removes the old one.
- **Writes are atomic:** a temporary file in the same folder, then a
  replace.

## Content

UTF-8 JSON:

```json
{
  "format": "oil-level-tracker-recipe",
  "schema_version": 1,
  "id": "<uuid>",
  "name": "2호기 냉각",
  "created_at": "2026-10-29T01:02:03+00:00",
  "updated_at": "2026-10-29T04:05:06+00:00",
  "reference_frame": {
    "width": 1280,
    "height": 720,
    "source_name": "SPL#4_Cooling_onoff_#2.mp4",
    "time_sec": 12.5,
    "jpeg_base64": "<downscaled JPEG>"
  },
  "glasses": [
    {
      "id": "<uuid>",
      "name": "BASE",
      "ellipse": {"center_x": 640.0, "center_y": 360.0, "radius_x": 80.0, "radius_y": 200.0},
      "zero_line_y": 380.0,
      "judgment_rule": {
        "mode": "RECOVERY",
        "recovery_limit_sec": 120.0,
        "stable_hold_sec": 5.0,
        "minimum_valid_coverage_ratio": 0.7,
        "allowed_sec": 5.0,
        "allowed_px": 0.0
      }
    }
  ]
}
```

- **Coordinates** are source-frame pixels of the reference frame. y grows
  downward.
- **`mode`** is one of:
  - `RECOVERY`;
  - `HOLD_BELOW_ZERO`;
  - `HOLD_ABOVE_ZERO`.
- **All rule fields are stored for every mode.** The Recipe screen shows
  only the ones the mode uses.

## Reading

- **A file is refused when:**
  - `format` is not `oil-level-tracker-recipe`;
  - `schema_version` is not 1, including any future version;
  - a field is missing or has the wrong type.
- **A refused file stays on disk.** The Recipe list names it with the
  reason.
- **Duplicate IDs:** if a second file has the same `id`, the list reports
  that file instead of showing the Recipe twice.
- **v1 `.oilrecipe` files** are not listed and not read.
- **Domain rules are checked by the use case, not the reader.** These are
  the ellipse inside the frame, the zero line within the ellipse and the
  rule values.

The inspection folder's Recipe copy (§3 of the Product SSOT) uses the same
content. Its location is settled in V2-2.
