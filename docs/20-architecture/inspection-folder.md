# Inspection Folder

**Status:** `ACTIVE`. Schema version 1, 2026-10-29; `edits.json` and
`inspection.json` schema 2, 2026-10-30 (V2-4).

This document owns the inspection folder and its files. The contents and
the rules come from the [Product SSOT](../10-product/product.md) §3, §4
and §8. The code is `src/oil_tracker/adapters/storage/inspection_files.py`.

## Location and name

- **Folder:** `<data folder>\Inspections\<name>\`. The data folder is
  `Documents\OilLevelTracker\`.
- **Name:** the inspection name the user gave, made safe for Windows by the
  [Recipe file](recipe-file.md) rule; a name that would start with a dot
  gets a leading `_`, so the folder is still read.
  - **Without a name:** `YYYYMMDD-HHMM_<video file name without its
    extension>`, from the creation time in local time, with the video name
    made safe the same way.
  - The name has at most 60 characters, so the deepest cache file stays
    inside Windows' 260-character path limit (about 190 characters with
    `C:\Users\<user>\Documents`).
- **A folder name already taken,** by the same name or by two inspections
  of one video in the same minute, gets `_2`, `_3`, … after it.
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
| `edits.json` | the user's edits (below) | atomically, on "저장" |
| `cache\analysis.json` | the analysis: times and Oil drafts (below) | inside the cache swap |
| `cache\<Glass ID>\context-NNN.png` | the context image, in pieces of at most 4,096 columns, `NNN` from `000` | inside the cache swap |
| `cache\<Glass ID>\background-NNN.png` | the background view, in the same pieces (8-bit grey) | inside the cache swap |
| `versions\NNN\` | a submitted version, `NNN` from `001` (below) | once, on "제출"; never changed |

## Versions

Submitting (Product SSOT §3, A9; V2-4) locks the edits as a version. The
versions stay in the inspection folder, one subfolder each:

| Path | Contents |
|---|---|
| `versions\NNN\version.json` | the version: its number, when it was submitted and each Glass's judgment (below) |
| `versions\NNN\edits.json` | the submitted edits, in the `edits.json` format; `saved_at` is the submission time |
| `versions\NNN\inspection.json`, `recipe.json` | copies of the inspection (with the report header) and its Recipe copy as submitted |
| `versions\NNN\report.html` | the report (V2-4 step 6) |

- **Writing:** everything goes into `versions\NNN.partial\`, which is
  then renamed to `versions\NNN\`; then the working `edits.json` is
  removed. A stale `.partial` folder is removed before the next
  submission and never read.
- **The inspection's state follows from the folder:**
  - no version: being edited (`edits.json`, once saved);
  - versions and no `edits.json`: the latest version is submitted and
    locked. The editor shows it read-only; saving, the report header and
    re-analysis are refused;
  - versions and an `edits.json`: the next version is being edited ("고쳐서
    다시 제출" copied the latest version's edits there, with each Glass's
    decision and check).
- **A version is never changed or removed by the app.** An older version
  opens read-only in the editor while the cache still fits its times;
  after a later re-analysis only its report shows it.

### `version.json`

```json
{
  "format": "oil-level-tracker-version",
  "schema_version": 1,
  "version": 1,
  "submitted_at": "2026-10-30T05:22:00+00:00",
  "glasses": [
    {
      "glass_id": "<uuid>",
      "verdict": "FAIL",
      "computed": "PASS",
      "computed_reason": "기동 후 20초에 0선을 회복해 5초 이상 유지했습니다.",
      "override": "FAIL",
      "reason": "거품이 유면을 가림",
      "checked_at": "2026-10-30T05:21:00+00:00"
    }
  ]
}
```

- `version` equals the folder's `NNN`.
- `verdict` is the final judgment the report shows; `computed` and
  `computed_reason` are the app's own result, kept as the user's record
  (DESIGN.md §2.4). `override` and `reason` are the user's decision
  (`null` and `""` without one); `checked_at` is when the Glass was
  checked.
- One entry per Glass of the Recipe copy, in its order.

**The cache swap.** An analysis writes everything into `cache.partial\`,
then removes `cache\` and renames `cache.partial\` to `cache\`. A reader
never sees half of an analysis; a cancelled one leaves no cache.

**Re-analysis** (V2-3): while it runs, `inspection.json`, `recipe.json`,
`cache\` and `edits.json` keep the previous analysis, so the editor stays
usable and a cancel, a failure or closing the app leaves the inspection as
it was. When it ends, the cache swap comes first, then `edits.json` (the
merged edits), then `inspection.json` with the new setup.

## `inspection.json`

UTF-8 JSON:

```json
{
  "format": "oil-level-tracker-inspection",
  "schema_version": 2,
  "id": "<uuid>",
  "name": "1차 냉각",
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
  "failure": null,
  "report_header": {"compressor_model": "GB-2 R410A", "test_type": null}
}
```

- `name` is the inspection name, or `null`. It is set when the folder is
  made and does not change. Files written before names (2026-10-29) have no
  `name` key and read as `null`.
- `video.sha256` is filled in by the analysis. Reopening warns when the
  video's SHA-256 differs (Product SSOT A9).
- `state` is `NOT_ANALYSED`, `ANALYSED` or `FAILED`; `failure` gives the
  reason of a `FAILED` one.
- `report_header` is what the user enters for the report header (Product
  SSOT §7): each field trimmed, `null` when blank, at most 60 characters.
  A new inspection's comes from the setup with "분석 시작"; afterwards the
  setup's and the editor's 검사 정보 rewrite this file at once, apart from
  `edits.json` (V2-4).
- **Schema 2** (V2-4) added `report_header`. Schema 1 files still read,
  with an empty header; the next write makes them schema 2.

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

## `edits.json`

The user's edits on the analysis (Product SSOT §4 and §6). It sits beside
`cache\`, so re-analysis, which swaps the cache, leaves it alone; the
re-analysis then rewrites it with the edits merged onto the new times.
- If the app stops between the cache swap and that rewrite, the times no
  longer match the cache. The editor then merges on opening and shows the
  edits as unsaved.

```json
{
  "format": "oil-level-tracker-edits",
  "schema_version": 2,
  "saved_at": "2026-10-29T06:00:00+00:00",
  "times": [0.0, 0.5, 1.0],
  "compressor_start_sec": 532.0,
  "glasses": [
    {
      "glass_id": "<uuid>",
      "oil": {"ys": [460.0, null, 461.0], "origins": ["DRAFT", "EDITED", "DRAWN"]},
      "foam": {"ys": [null, 420.0, null], "origins": ["DRAFT", "DRAWN", "DRAFT"]},
      "reference": {"ys": [null, null, null], "origins": ["DRAFT", "DRAFT", "DRAFT"]},
      "cannot_judge": [{"start_sec": 0.5, "end_sec": 1.0}],
      "memos": [{"id": "<uuid>", "time_sec": 0.5, "y": 420.0, "text": "거품"}],
      "decision": {"override": "FAIL", "reason": "거품이 유면을 가림", "checked_at": "2026-10-30T05:00:00+00:00"}
    }
  ]
}
```

- `times` equal the analysis's. Every line has one value per time.
- **Lines** are source-frame y values, `null` where empty. A line's pieces
  are the stretches between its empty samples. An Oil sample emptied by the
  user is `null` with origin `EDITED`, so re-analysis cannot refill it.
- `cannot_judge` stretches hold the samples whose times lie in
  `[start_sec, end_sec)`.
- `memos` belong to a Glass; `y` is `null` for a memo pinned to a time
  alone. A memo's text has at most 500 characters.
- `compressor_start_sec` starts as the setup's value and follows the marker
  the user drags.
- FULL and EMPTY are not stored; they follow from the Oil line, as does
  the computed judgment.
- `decision` is the user's part of the judgment (V2-4, Product SSOT §3):
  `override` is `"PASS"`, `"FAIL"` or `null` (the computed verdict
  stands); `reason` is required (non-blank) once a Glass with an override
  is checked, and at most 500 characters; `checked_at` is when the user
  checked the Glass, or `null`. Re-analysis keeps the override and the
  reason and clears the check.
- **Schema 2** (V2-4) added `decision`. Schema 1 files (V2-3) still read,
  with every Glass undecided; a save writes schema 2.

## Reading rules

- A file with another `format`, or a `schema_version` other than 1 (2 or
  1 for `edits.json` and `inspection.json`), is refused with the reason.
- Values are type-checked strictly; a wrong type refuses the file.
- There is no reader for v1 result bundles.
