# v2 Product Decisions

**Owner of what v2 does.** The user made these decisions on 2026-10-28, in
the direction interview and the post-spike interview.

- **Interview record:** `docs/60-evidence/s11/2026-10-28-v2-direction-interview-handoff.md`
  at tag `v1-final`.
- **Changing a decision needs the user.** Implementation details not listed
  here are the agent's call, as long as they stay reversible.

## Flow

1. **Recipe.** It is made once per equipment and camera setup, and reused
   for every inspection.
   - It holds the Glass name, the ellipse, the zero line and the judgment
     rule.
   - If the camera shifted, the Glass position is corrected in that
     inspection only.
   - There are no detector settings.
2. **Analysis setup.** While watching the video, the user sets:
   - the analysis range;
   - the compressor start time.
3. **Analysis.**
   - The video is read once for all Glasses.
   - Each Glass gets a full-resolution context image. Each column is one
     time; each row is the RGB median of one source row inside the central
     band of the ellipse.
   - Each Glass gets a background-subtracted view and an Oil draft line.
   - Progress and the time left are shown.
   - The result is cached in the inspection folder.
   - For reference, 2.8 min for a 68-min video is acceptable.
4. **Editing.** Every inspection does it; see below.
5. **Judgment.** It is computed automatically from the edited lines. The
   user may override it per Glass, with a required reason that is saved.
6. **Submit.**
   - Every Glass must be checked first.
   - Submitting locks that version.
   - To resubmit, open the submitted inspection, edit, and save a new
     version.

The detector is not part of the v2 flow.

## Lines and states

- **Line kinds:** Oil, Foam and reference.
  - Oil and Foam feed the judgment; reference lines are only shown.
  - A line may have several pieces.
- **The draft is the Oil line only,** found by a simple method:
  - the strongest vertical edge per column;
  - temporal jumps suppressed;
  - weak-edge stretches marked "cannot judge".
  - The user adds Foam lines.
  - Draft quality is not an acceptance condition.
- **FULL and EMPTY are automatic.**
  - A line at the Glass top is FULL (`FULL_NO_INTERFACE`).
  - A line at the Glass bottom is EMPTY (`EMPTY_NO_INTERFACE`).
- **"Cannot judge" is the only stretch tool.** Those samples are invalid and
  count against coverage.
- **Sampling and events:** lines are sampled at the analysis rate with no
  extra smoothing. Events are recomputed from the edited samples.

## Editor

- **Layout:** the graph above the context image. The two share one time axis
  and one playhead, and the edited lines are drawn over both.
- **Editing:**
  - **Grab-and-drag:** grab a line anywhere; nearby parts follow smoothly,
    within a width the user adjusts.
  - **Pencil:** redraw a time range, replacing that stretch.
  - The draft is kept as dense samples. Points are not edited one by one.
- **Curve shape:** smooth with no overshoot. A spot can be switched to a
  corner.
- **Precision aids:**
  - zoom;
  - the background-subtracted view;
  - the lines drawn over the source frame;
  - video playback.
  - **Snap is not in the first version.**
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
- **Memos:** attached to a graph position.

## Report

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
  uses the editor's drawing module and the [DESIGN.md](../DESIGN.md) colour
  roles.

## Storage

- **One folder per inspection.** It holds:
  - the edit data, versioned;
  - the context-image cache;
  - the report HTML, versioned.
- **Resuming:** opening the folder or a report resumes editing.
- **The source video** is referenced by path and SHA-256, not copied.

## Platform and acceptance

- **Platform:**
  - a web UI, decided by the spike (`spike/webui`, Windows GO on
    2026-10-28);
  - Fluent 2 visual language, light theme ([DESIGN.md](../DESIGN.md));
  - a PyInstaller one-folder build for Windows.
- **First-version acceptance:**
  - The user completes analysis → edit → submit on target Windows with
    field videos.
  - The user judges that the lines match the context images.

## Non-goals of the first version

- detector work;
- edit history in the report;
- draft-quality acceptance;
- snap;
- Foam draft extraction;
- reading v1 files.
