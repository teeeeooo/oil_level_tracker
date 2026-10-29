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

## Result (run on 2026-10-29, macOS)

Command: `python scripts/compare_draft_methods.py`. The pictures are in
`sample/output/draft-comparison/` (ignored by Git).

| Method | Gold hits | Silver hits | Silver `no_interface`/`unclear` in "cannot judge" |
|---|---|---|---|
| A spike | 0 / 11 | 0 / 16 | — |
| B dynamic programming | 0 / 11 | 0 / 16 | 0 / 28 |
| C B on 0.7 raw + 0.3 background | 0 / 11 | 0 / 16 | 0 / 28 |

- **Every method missed every point.** On all three videos the strongest
  edge is not the Oil boundary:
  - **sample4:** a bright horizontal band near the bottom of the ellipse
    (about Y 884), present for the whole video. B and C follow it from
    start to end; A follows it for the last two thirds. The Oil boundary
    is the bottom of the bright Foam layer, about 30 px higher.
  - **base_sample_1:** the video itself carries red and green horizontal
    bars from about 4.5 s, drawn over the picture, and A and B settle on
    another horizontal band, about 100 px below the truth.
  - **sample2:** 9.6 s long, and the picture changes from column to
    column; all methods sit at Y 652–654 against a truth of 592.
- **"Cannot judge" never appeared** for B or C, not even at the 28
  points where the silver truth sees no interface. A strong but wrong edge
  is not weak, so the weak-edge rule cannot flag it.
- **Draft time** is 25–80 µs per column for B, so about 1 s for SPL#1's
  8,210 columns.

**Decision rule, as fixed:**
- B stays (A does not have 3 more hits).
- C does not replace B (it has no more hits).
- The "cannot judge" threshold stays (B has no hits to cover).

The rule keeps B, but its premise failed: B found no Oil boundary on
these samples. **The comparison says the edge source matters more than
spike against dynamic programming.**

### After the first run (post-hoc; does not count for the rule)

Three variants were added after seeing the result above. F answers the
user's question whether v1's fixed-structure templates (artifacts, marked
on the Recipe) would help: it weakens to 20 % the rows where the edge is
strong (`s > 0.5`) in at least 80 % of the columns, padded by 3 rows. Those
rows stand in for the bands a user would mark.

| Method | Gold hits | Silver hits | Silver `no_interface`/`unclear` in "cannot judge" |
|---|---|---|---|
| D dynamic programming on the background view only | 7 / 11 | 7 / 16 | 2 / 28 |
| E dynamic programming on 0.5 raw + 0.5 background | 0 / 11 | 0 / 16 | 0 / 28 |
| F B with the fixed bands weakened | 0 / 11 | 0 / 16 | 0 / 28 |

- **D** removes edges that stay at one height for the whole video, so the
  band at Y 884 drops out. On sample4 it follows the bottom of the Foam
  layer until about 35 s, then falls to the old band.
- **E** behaves like B: the raw static band still wins at a 0.5 share.
- **F** finds bands at source Y 477–492 on base_sample_1 and at 798–802,
  866–872 and 880–888 on sample4 (none on sample2). With them weakened, the
  path moves to the next static edge: just below the band on base_sample_1,
  and between the bands on sample4 (errors fall from 22–34 % to 13–26 % of
  H, still no hit). Marking the few obvious bands is not enough; many
  weaker fixed edges remain.
- **v1's own record agrees.** v1 rejected matching candidates outright, and
  its D2 comparison (`v1-final:docs/60-evidence/s11/2026-10-08-d2-recipe-artifact-comparison.md`)
  found a template that also removed true Oil boundaries at the same
  height. It was not adopted.
- **D's known weakness:** an Oil level that stays at one height for most
  of the video also drops out of the background view. SPL#4 Accum
  (`HOLD_BELOW_ZERO`) may be such a case.
- These are three short, unusual videos chosen after the fact. They do not
  settle the edge source for the field videos.

## Next

The edge source should be judged on the acceptance videos, SPL#1 and
SPL#4, which are only on the Windows PC.
`python scripts/compare_draft_methods.py --video <video> --recipe <v2 Recipe>`
draws A, B, D and F for every Glass of a v2 Recipe, for the user to judge
by eye. The request is
[2026-10-29-v2-2-draft-comparison-windows-request.md](../40-operations/2026-10-29-v2-2-draft-comparison-windows-request.md).

**Windows result:** [2026-10-29-v2-2-draft-comparison-windows-result.md](../60-evidence/2026-10-29-v2-2-draft-comparison-windows-result.md).
No method follows the Oil line on all three Glasses (best: A, F, none), so
the draft method goes back to the user.

**Decision (user, 2026-10-29):**
- the draft is method B (dynamic programming on raw edges); its weak
  stretches are left empty instead of "cannot judge";
- the editor (V2-3) makes a wrong stretch quick to fix: range delete, a
  point line that joins the user's points along the edges, and a snap
  that can be switched off;
- SPL#1's Oil boundary is faint but visible by eye in the full-size
  context image.
