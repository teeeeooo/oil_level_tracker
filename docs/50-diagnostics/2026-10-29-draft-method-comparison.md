# Draft-method comparison (2026-10-29)

**Status:** plan fixed before the run. The result is added below it.

**Question.** For the V2-2 Oil draft, how does dynamic programming (the
method the user chose for Product SSOT §4) compare with the spike's
per-column method on the local samples that have truth? The user asked for
this comparison on 2026-10-29. It is a diagnostic: draft quality is not an
acceptance criterion, and the result changes the plan only through the
decision rule below.

## Inputs

| Video | Glass (from its v1 Recipe) | Gold truth | Silver truth |
|---|---|---|---|
| `sample/base_sample_1.mp4` (1280 × 720, 14.4 s) | `Bitzer sight glass`, ry 148 | 3 user-corrected points | 19 agent points |
| `sample/sample2.mp4` (720 × 1280, 9.6 s) | `sample2 sight glass`, ry 170 | 3 | 9 |
| `sample/sample4.mp4` (1080 × 1234, 56.1 s) | `sample4 sight glass`, ry 52 | 5 | 16 |

- **Gold:** the user's v1 `.oiltruth` Oil boundary `source_frame_y`.
- **Silver:** the agent-assisted `.provisional-truth.json`, not confirmed by
  the user. A visible point gives a Y or a Y range; a `no_interface` or
  `unclear` point gives none.
- **Left out:** `sample3` (quarantined in v1), the two public videos (no
  Recipe or truth), and SPL#1 and SPL#4 (only on the Windows PC).
- **Only the comparison script** (`scripts/compare_draft_methods.py`) reads
  the v1 files. The product never does.

## Common steps

- **Context image** as in the spike and v1 (`ellipse-central-40pct-row-rgb-median`):
  each column is one time at 2 per second over the whole video; each row is
  the RGB median of one source row inside the central 40 % band of the
  ellipse.
- **Edge strength** `g`: the luma (0.299 R + 0.587 G + 0.114 B) difference
  between the rows above and below, `|L[y+1] − L[y−1]|`, blurred over 5
  columns (as the spike).
- **Error:** the distance in source pixels from the draft row to the truth
  Y, or to the truth range (0 inside it), as a percentage of the Glass
  height `H = 2 ry`. **A hit is an error ≤ 5 % of H.**
- Each truth time maps to the nearest column (at most 0.25 s away).

## Methods (parameters fixed now)

| ID | Method |
|---|---|
| A | **Spike:** the row of the largest `g` in each column, then a 5-column median |
| B | **Dynamic programming:** the path that maximises `Σ s − 5 · Σ |Δy| / H`, with `s = min(g / 24, 1)` and at most `H / 4` rows per column. **Cannot judge** where the path's `s`, averaged over 10 columns (5 s), is below 0.25; runs shorter than 4 columns (2 s) are dropped |
| C | **B on a mixed strength:** `0.7 g + 0.3 g_bg`, where `g_bg` is the same edge strength on the background view (each row minus its median over time) |

## What is reported

- Per method: hits and misses on the gold points, then on the silver points
  with a Y.
- For B and C: which of those points fall in a "cannot judge" stretch; how
  many silver `no_interface` / `unclear` points fall in one; the share of
  each video marked "cannot judge".
- Run time of each draft per column, to scale to SPL#1 (8,210 columns).
- One image per video: the context image with A, B and C drawn over it,
  B's "cannot judge" stretches shaded, and the truth points.

## Decision rule (fixed now)

- **B stays,** as the user decided, unless A has 3 or more hits than B over
  gold and silver together. Then the result goes back to the user before
  any code.
- **C replaces B** only if C has 2 or more hits than B and misses no gold
  point that B hits.
- **The "cannot judge" threshold stays** unless it covers more than half of
  B's hits. A point in a "cannot judge" stretch counts as not a hit.
- Any parameter changed after seeing the result is labelled as such and
  does not count for this rule.
