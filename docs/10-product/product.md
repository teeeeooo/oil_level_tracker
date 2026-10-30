# Oil Level Tracker v2 — Product SSOT

**Status:** `ACTIVE`.

This is the single source of truth for what v2 is for, how it is accepted,
and what it does. The user made these decisions:
- on 2026-10-28, in the direction interview, the post-spike interview and
  the acceptance-criteria decision;
- on 2026-10-29, at the V2-1 start: the Recipe, the judgment rule (§5) and
  the data folder (§8);
- on 2026-10-29, at the V2-2 start: the inspection flow and analysis setup
  (§3), and, after the draft comparison, the draft (§4) and the editing
  tools and snap (§6);
- on 2026-10-29, after the V2-2 Windows run: the inspection name (§3, §8);
- on 2026-10-29, at the V2-3 start: re-analysis after editing, and saving
  (§6).

- **Interview record:** `docs/60-evidence/s11/2026-10-28-v2-direction-interview-handoff.md`
  at tag `v1-final`.
- **Changing a goal, an acceptance criterion or a decision needs the user.**
  Implementation details not listed here are the agent's call, as long as
  they stay reversible.

## 1. Goal

An inspector can turn one compressor sight-glass video into a trustworthy,
submitted oil-level report on a Windows PC.

- The app does the tedious part: it builds the context image, a draft Oil
  line and the judgment.
- The inspector stays the authority on where the lines are and on the final
  judgment.

**Why the direction changed:**
- v1 tried to make the automatic detector alone pass field videos. S11 ended
  unmet, with FIELD FAIL.
- v2 makes draft plus human editing the default flow. Acceptance therefore
  depends on the tool, not on detector accuracy.

## 2. First-version acceptance criteria

The first version is accepted only when **all** of these hold. They are
judged on target Windows with the PyInstaller one-folder build.

| ID | Criterion | Pass |
|---|---|---|
| A1 | Complete workflow | The user completes Recipe → analysis → edit → submit for **SPL#1** (`SPL#1_Heating_coldstart.mp4`, 68 min, Glass BASE) and **SPL#4** (`SPL#4_Cooling_onoff_#2.mp4`, Glasses BASE and Accum) |
| A2 | Lines match | The user judges that the submitted lines match the context images for every Glass in A1 |
| A3 | Judgment | Each computed judgment follows the `JudgmentRule` semantics, proven by unit tests with fixed cases. The user agrees with each final judgment in A1, or records an override with a reason |
| A4 | Context-image time | The 68-min SPL#1 video takes **≤ 3 min** (spike: 2.8 min) |
| A5 | Editing response | Redraw while editing: median **≤ 16 ms**, max **≤ 50 ms**, on SPL#1 (spike: 2,053 samples, 13.4 / 30 ms) |
| A6 | Frame and video | Frame seek median **≤ 100 ms** (spike: 26–68 ms). 1× playback without stalls |
| A7 | Report | Opens offline in Edge. Prints to a readable A4-landscape PDF. **≤ 5 MB** per report (spike: 9.9 MB, before print downscaling) |
| A8 | Package | One-folder build **≤ 200 MB** (spike: 152 MB). It runs on a PC that has only the WebView2 runtime |
| A9 | Data safety | Save and resume lose nothing. A submitted version is locked. A resubmission creates a new version. Reopening warns when the source video's SHA-256 differs |

Draft quality is **not** an acceptance criterion.

**Target Windows** (user, 2026-10-29; changed 2026-10-30): the inspectors'
PCs vary.
- **The time limits (A4–A6) are judged on the workstation** (AMD Ryzen
  Threadripper PRO 7945WX, 12 cores, 128 GB RAM).
- **The slowest PC is for reference only:** about an Intel Xeon E5-1620 v3
  (4 cores, 8 threads, 3.5 GHz) with 16 GB RAM and an NVIDIA Quadro K620,
  the worst case. Its timings show where a simple change could make the
  app faster; missing a limit there does not fail acceptance or hold work
  up. What matters there is that the app is usable.

## 3. Flow

**The app opens on the inspection list.** The Recipe list is reached from
its toolbar.

1. **Recipe.** It is made once per equipment and camera setup, and reused
   for every inspection.
   - It holds the Glass name, the ellipse, the zero line and the judgment
     rule (§5).
   - The ellipse is axis-aligned. The zero line is horizontal.
   - **Reference frame:** the user scrubs a sample video and draws on it.
     The frame on screen when the Recipe is saved becomes the reference
     frame; there is no separate "set reference" step.
     - Saving without a video open keeps the stored reference frame.
     - The Recipe keeps that frame as a downscaled JPEG, the frame size,
       and the source video name and time, for reference.
   - **Picking:** a new inspection starts with the video, then a Recipe
     from the Recipe folder (§8). The list shows the name, the Glass names,
     the frame size and the modified date.
   - **Resolution:** a video whose resolution differs from the Recipe's is
     refused, with the reason shown.
   - **Copy:** when analysis starts, a copy of the Recipe is saved in the
     inspection folder. Later Recipe edits do not change past inspections.
   - If the camera shifted, the Glass position is corrected in that copy
     only, during the analysis setup, with the Recipe screen's Glass
     editing.
   - There are no detector settings.
2. **Analysis setup.** While watching the video, the user sets:
   - the analysis range;
   - the compressor start time. It is required only when a Glass uses
     `RECOVERY`, and it must lie inside the analysis range;
   - the Glass positions, if the camera shifted (above);
   - an inspection name, if wanted. It is shown in the inspection list and
     names the inspection folder (§8). It is set when the analysis first
     starts.
3. **Analysis.**
   - The video is read once for all Glasses.
   - Each Glass gets a full-resolution context image. Each column is one
     time; each row is the RGB median of one source row inside the central
     band of the ellipse.
   - Each Glass gets a background-subtracted view and an Oil draft line.
   - Progress and the time left are shown.
   - The analysis rate is **2 samples per second**, fixed in the first
     version.
   - The result is cached in the inspection folder.
   - For reference, 2.8 min for a 68-min video is acceptable.
4. **Editing.** Every inspection does it; see below.
5. **Judgment.** It is computed automatically from the edited Oil line
   (§5). The user may override it per Glass, with a required reason that is
   saved.
6. **Submit.**
   - Every Glass must be checked first.
   - Submitting locks that version.
   - To resubmit, open the submitted inspection, edit, and save a new
     version.

The detector is not part of the v2 flow.

## 4. Lines and states

- **Line kinds:** Oil, Foam and reference.
  - Only Oil feeds the judgment. Foam and reference lines are only shown.
  - A line may have several pieces.
- **The draft is the Oil line only,** found by a simple method:
  - the path across time that follows the strongest vertical edges with
    the fewest jumps (dynamic programming), so jumps are suppressed along
    the whole path;
  - stretches where that path's edge is weak are left empty, for the user
    to draw.
  - On the acceptance videos this path often follows the Foam boundary or
    a fixed band (comparison of 2026-10-29). The editor therefore makes a
    wrong stretch quick to delete and redraw (§6).
  - The user adds Foam lines.
  - Draft quality is not an acceptance condition.
- **FULL and EMPTY are automatic.**
  - A line at the Glass top is FULL (`FULL_NO_INTERFACE`).
  - A line at the Glass bottom is EMPTY (`EMPTY_NO_INTERFACE`).
- **Stretch states:** a stretch of the Oil line can be empty or "cannot
  judge". Both are invalid samples and count against coverage.
  - **Empty:** no line yet. It comes from a range delete (§6) or from the
    draft's weak stretches, and stays invalid until the user draws it, so a
    forgotten gap never passes.
  - **"Cannot judge":** set only by the user, on purpose.
- **Sampling and events:** lines are sampled at the analysis rate with no
  extra smoothing. Events are recomputed from the edited samples.

## 5. Judgment rule

Each Glass in a Recipe has one rule.
- It is computed from the Oil line only.
- Heights are source-frame pixels from the zero line, positive upward.

| Field | Default | Used by |
|---|---|---|
| `mode` | `RECOVERY` | all |
| `recovery_limit_sec` | 120 | `RECOVERY` |
| `stable_hold_sec` | 5 | `RECOVERY` |
| `minimum_valid_coverage_ratio` | 0.70 | all |
| `allowed_sec` | 5 | both HOLD modes |
| `allowed_px` | 0 | both HOLD modes |

- **Modes:**
  - `RECOVERY` (기준점 회복): after the compressor start, the Oil line
    reaches the zero line or above and stays there for `stable_hold_sec`.
    That stretch must begin within `recovery_limit_sec` of the compressor
    start.
  - `HOLD_BELOW_ZERO` (기준점 아래 유지): a violation is the Oil line more
    than `allowed_px` above zero.
  - `HOLD_ABOVE_ZERO` (기준점 위 유지): a violation is the Oil line more
    than `allowed_px` below zero.
- **Allowed time:** in a HOLD mode, the Glass fails only when its
  **longest continuous** violation lasts longer than `allowed_sec`.
  - v1 measured from the first to the last violating sample instead. v2
    does not keep that.
- **Coverage:** empty and "cannot judge" samples are invalid (§4). A valid
  share below `minimum_valid_coverage_ratio` gives "needs review".
- **Foam never affects the judgment.** It may rise above the zero line.
- **Recipe screen:** it shows only the fields the selected mode uses, and
  all of them are editable.
- **Dropped from v1:**
  - `unknown_policy` (v1 never used it);
  - `initial_state`;
  - `mm_per_pixel`;
  - the detector settings, margin, exclusions and artifacts.

## 6. Editor

- **Layout:** the graph above the context image. The two share one time axis
  and one playhead, and the edited lines are drawn over both.
- **Editing:**
  - **Grab-and-drag:** grab a line anywhere; nearby parts follow smoothly,
    within a width the user adjusts.
  - **Pencil:** redraw a time range, replacing that stretch.
  - **Range:** the range tool selects a time range by dragging across the
    graph or the context image. Delete then empties the Oil line there
    (§4), and U marks it "cannot judge". One tool serves both (user,
    2026-10-29).
  - **Point line:** click points on the context image. Each pair of
    neighbouring points is joined by a path that follows the edges between
    them: the draft's dynamic programming, pinned to the user's points.
  - The draft is kept as dense samples. Points are not edited one by one.
- **Curve shape:** grab-and-drag bends the line smoothly, with no
  overshoot. Holding Alt, or choosing the pointed shape, bends it to a
  corner at the grabbed spot (user, 2026-10-29).
- **Precision aids:**
  - zoom;
  - the background-subtracted view;
  - the lines drawn over the source frame;
  - video playback;
  - **snap** (user, 2026-10-29): while dragging, the line settles on a
    nearby edge. It can be switched off, because the strongest edge can be
    a Foam top or glare. It is on by default and reaches 8 px of the
    source frame (user, 2026-10-29).
- **Navigation:**
  - wheel zoom;
  - panning only with the pan tool or Shift-drag; a plain drag on empty
    space does nothing;
  - click a time-axis number and type a value to set the visible range.
- **Video:**
  - the source file plays in the built-in player, cropped to the Glass, with
    the lines drawn over it;
  - the graph playhead follows;
  - speed control and range repeat;
  - a paused frame is exact.
- **Compressor start:** a marker the user can drag. Dragging it recomputes
  the judgment. Changing the analysis range means re-analysis.
- **Re-analysis after editing** (user, 2026-10-29): the edited lines are
  kept where the new range overlaps the old one; only the new stretches
  get a draft. Before it starts, the app says which edits fall outside the
  new range and will be dropped.
- **Memos:** attached to a graph position.
- **Saving** (user, 2026-10-29): "저장" saves the edits. Leaving the editor
  or closing the window with unsaved changes asks first.

## 7. Report

- **Header:**
  - entered by the user: compressor model and test type;
  - filled in automatically: video file name, Recipe name, date-time and
    report version.
- **Body:**
  - the graph and the context image with the edited lines;
  - the final judgment;
  - the judgment-criteria table;
  - the key-time table: compressor start, recovery and violations;
  - memos, as numbered pins with a list below.
- **Left out:** the v1 detector graph and the edit history.
- **Format:** self-contained HTML that works offline and prints to PDF. It
  uses the editor's drawing module and the [DESIGN.md](../../DESIGN.md) colour
  roles.

## 8. Storage

- **Data folder:** `Documents\OilLevelTracker\` on each PC.
  - It is found with the Windows known-folder API, so a redirected
    Documents folder (for example, to OneDrive) is followed.
  - `Recipes\` holds the Recipes, one `<name>.recipe.json` file each.
  - `Inspections\` holds the inspection folders. A folder takes the
    inspection name, made safe for Windows; without a name it is
    `YYYYMMDD-HHMM_<video name>`.
- **Settings and logs** go to `%LOCALAPPDATA%\OilLevelTracker\`.
- **Nothing is written inside the package folder.**
- **Sharing:** the app is installed on several PCs, and each inspector uses
  their own. Nothing is shared between PCs; a Recipe moves to another PC
  by copying its file.
- **One folder per inspection.** It holds:
  - the Recipe copy (§3);
  - the edit data, versioned;
  - the context-image cache;
  - the report HTML, versioned.
- **Resuming:** opening the folder or a report resumes editing.
- **The source video** is referenced by path and SHA-256, not copied.

## 9. Platform and acceptance

- **Platform:**
  - a web UI, decided by the spike (`spike/webui`, Windows GO on
    2026-10-28);
  - Fluent 2 visual language, light theme ([DESIGN.md](../../DESIGN.md));
  - a PyInstaller one-folder build for Windows.
- **Acceptance:** see §2.

## 10. Non-goals of the first version

- detector work;
- edit history in the report;
- draft-quality acceptance;
- Foam draft extraction;
- reading v1 files.
