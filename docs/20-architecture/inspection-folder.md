# Inspection Folder

**Status:** `ACTIVE`. Schema version 1, 2026-10-29.

This document owns the inspection folder and its files. The contents and
the rules come from the [Product SSOT](../10-product/product.md) §3, §4
and §8. The code is `src/oil_tracker/adapters/storage/inspection_files.py`.

## Location and name

- **Folder:** `<data folder>\Inspections\<name>\`. The data folder is
  `Documents\OilLevelTracker\`.
- **Name:** `YYYYMMDD-HHMM_<video file name without its extension>`, from
  the creation time in local time. The video name is made safe for
  Windows by the [Recipe file](recipe-file.md) rule.
- **Two inspections in the same minute** of the same video get `_2`, `_3`,
  … after the name.
- **The folder is made when the analysis starts,** with the Recipe copy
  (Product SSOT §3). A setup left before that writes nothing.
- **Reading:** every sub-folder is read. A folder whose files cannot be
  read is listed with its reason; a folder whose name starts with a dot is
  skipped. Two folders with the same inspection ID: the second is listed
  as unreadable.

## Files

| Path | Contents | Written |
|---|---|---|
| `inspection.json` | the inspection (below) | atomically, on every change |
| `recipe.json` | the inspection's Recipe copy, in the [Recipe file](recipe-file.md) format; Glass corrections are made here | atomically, with `inspection.json` |
| `cache\analysis.json` | the analysis: times and Oil drafts (below) | inside the cache swap |
| `cache\<Glass ID>\context-NNN.png` | the context image, in pieces of at most 4,096 columns, `NNN` from `000` | inside the cache swap |
| `cache\<Glass ID>\background-NNN.png` | the background view, in the same pieces (8-bit grey) | inside the cache swap |

Reserved for later milestones: the versioned edit data (V2-3) and the
versioned report HTML (V2-4).

**The cache swap.** An analysis writes everything into `cache.partial\`,
then removes `cache\` and renames `cache.partial\` to `cache\`. A reader
never sees half of an analysis; a cancelled one leaves no cache.

## `inspection.json`

UTF-8 JSON:

```json
{
  "format": "oil-level-tracker-inspection",
  "schema_version": 1,
  "id": "<uuid>",
  "created_at": "2026-10-29T05:06:07+00:00",
  "video": {
    "path": "C:\\videos\\SPL#1_Heating_coldstart.mp4",
    "name": "SPL#1_Heating_coldstart.mp4",
    "size_bytes": 683165477,
    "width": 1920,
    "height": 1080,
    "fps": 23.976,
    "frame_count": 98413,
    "sha256": null
  },
  "settings": {"start_sec": 0.0, "end_sec": 4104.6, "compressor_start_sec": 532.0},
  "state": "NOT_ANALYSED",
  "failure": null
}
```

- `video.sha256` is filled in by the analysis. Reopening warns when the
  video's SHA-256 differs (Product SSOT A9).
- `state` is `NOT_ANALYSED`, `ANALYSED` or `FAILED`; `failure` gives the
  reason of a `FAILED` one.

## `cache\analysis.json`

```json
{
  "format": "oil-level-tracker-analysis",
  "schema_version": 1,
  "finished_at": "2026-10-29T05:09:00+00:00",
  "times": [0.0, 0.5, 1.0],
  "glasses": [
    {
      "glass_id": "<uuid>",
      "y0": 312,
      "rows": 728,
      "pieces": 3,
      "oil": {"ys": [460.0, null, 461.0], "origins": ["DRAFT", "DRAFT", "DRAFT"]}
    }
  ]
}
```

- `times` are the source-video seconds of the sampled frames, at 2 per
  second (Product SSOT §3). Every line has one value per time.
- `y0` is the source-frame y of the images' first row; `rows` is their
  height. Column `t` of the joined pieces is `times[t]`.
- `oil.ys` are source-frame y values, `null` where the draft is empty
  (Product SSOT §4). `origins` say where each sample came from: `DRAFT`,
  `EDITED` or `DRAWN`.

## Reading rules

- A file with another `format`, or a `schema_version` other than 1, is
  refused with the reason.
- Values are type-checked strictly; a wrong type refuses the file.
- There is no reader for v1 result bundles.
