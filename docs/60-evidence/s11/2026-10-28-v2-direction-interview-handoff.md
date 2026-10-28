# v2 direction interview handoff — 2026-10-28

## Current disposition

S11 is ACTIVE; O2 is OPEN; the Windows field result remains FIELD FAIL. The
[Work Plan](../../00-project/work-plan.md) is the only owner of current state
and authorization.

- **v2 implementation has NOT started.** The user said so explicitly: "아직
  v2 구현 시작은 아니야".
- **None of the decisions below has been executed yet.**
  - S11 is not frozen.
  - No milestone is opened.
  - No tag or archive branch exists.
  - `main` is not reset.
  - No production default changed.
- **A web UI spike is on branch `spike/webui`.** Its Windows request is
  queued; see below.
- **Next session:**
  1. take in the spike's Windows result;
  2. continue the v2 interview with the user;
  3. only then start v2.
- **This handoff supersedes** the
  [graph-editing direction handoff](2026-10-27-graph-editing-direction-handoff.md).
  The user's proposal recorded there is now interviewed and decided as below.

## Decisions from the interview (user, 2026-10-28)

| Topic | Decision |
|---|---|
| Role of editing | **The default flow of every inspection.** An automatic draft is shown; the user checks it, edits it and submits the report. Acceptance moves from "the detector alone passes" to "draft plus edits yield a report that meets the criteria" |
| Draft source | **Extracted from the context image.** The read-only extraction check (CTX-1) is back in the v1 scope |
| Lines | **Oil and Foam lines, plus FULL / EMPTY / unknown segments.** Every line has a kind: Oil, Foam or reference. Oil and Foam feed the judgment; reference lines are only shown. An Oil or Foam line may have several pieces |
| Judgment | `judge_samples` runs on the edited lines automatically. **The user may override it.** An override needs a reason, which stays in the saved data. The report shows only the final judgment |
| Screen | **Extend the existing result review screen** (keep the graph ↔ frame link) |
| Precision aids | **All four:** zoom/pan; the lines over the source frame; snap-to-edge; the background-subtracted view. Plus the full-resolution context image |
| Curve | **A smooth curve through the points, with no overshoot.** Each point can switch to a corner |
| Memos | Attached to a graph position. The report shows a number on the graph and a list below it |
| Report | **The editor's layout:** the graph, the context image with the edited lines drawn over it, and the final judgment. The old detector graph goes. No edit history (decided 2026-10-27) |
| Save / submit | Save and resume. Submitting needs every Glass checked and locks the report. To resubmit, load the submitted report, edit it, and save it as a **new version** |
| Detector | **Off in the new flow.** The code is kept, as an option only |
| S11 | **Frozen as unmet**, records kept, and a **new milestone** opened. This takes effect when v2 starts |
| Acceptance of v2's first version | **The user completes analysis → edit → submit on target Windows with field videos**, and judges that the lines match the context images. Draft quality is not an acceptance condition |
| Repository | **Same repository.** Tag and keep the final v1 on an archive branch, then commit "remove everything + v2 skeleton" on `main` (no force push). Port needed code file by file from the tag after review |
| v1 compatibility | **None.** v2 makes new Recipes; v1 Recipes and result bundles are not read |
| UI technology | **Web UI candidate:** a Python back end plus a web front end in pywebview (WebView2 on Windows). It is decided by the spike below. If the spike fails, v2 falls back to Qt (QML / `QGraphicsView`) |

**Defaults the agent proposed** (the user has not objected; confirm in the
next interview):
- A FULL segment becomes `FULL_NO_INTERFACE`, an EMPTY segment
  `EMPTY_NO_INTERFACE`, and an unknown segment an invalid sample, which
  counts against coverage.
- Lines are sampled at the analysis sampling rate, without extra smoothing.
- Events are recomputed from the edited samples.
- Overrides are per Glass.
- Where extraction finds nothing, the draft marks the stretch unknown.

**Open risks:**
- **Draft quality is unknown.** No one has tried extraction on SPL#1's faint
  thin line or on SPL#4 Accum's Foam/Oil mix.
- **With the detector off,** the draft's FULL/EMPTY must also come from
  extraction.
- **The saved format needs a schema** for versions, point provenance
  (draft / edited / drawn) and override reasons.

**Non-goals for v2's first version:** detector improvement, edit history in
the report, draft-quality acceptance.

## Web UI spike (branch `spike/webui`)

The [spike README](https://github.com/teeeeooo/oil_level_tracker/blob/spike/webui/spikes/webui/README.md)
owns its pass criteria W1–W9. They were frozen before the Windows run.

- **Commits:** `fb3e076` (spike) and `fb627cb` (Windows request), on
  `spike/webui`. They are not merged and are throwaway by design.
- **What it is:**
  - a Python local server on `127.0.0.1` and a pywebview window;
  - plain JavaScript with no build step;
  - one drawing module (`render.js`) shared by the editor and the report.
- **It reads a v1 `.oilrecipe`** only for the Glass ellipse and zero line.
  That is a spike convenience, not v2 compatibility.
- **Mac result (local only):**
  - `check_ui.py` with Chrome: **23/23 PASS**;
  - frame seek: median about 60 ms;
  - 564 points: render median 3.9 ms, max 7.5 ms;
  - the native WKWebView window runs, from source and from the PyInstaller
    build;
  - the Mac build is 138 MB with 217 files.
- **Defects the Mac run fixed:**
  - a reverse-DNS stall over 30 s in `HTTPServer` bind;
  - the frame cursor swallowing presses;
  - the browser's double-click never firing on redrawn points;
  - the memo box losing focus.
- **Queued Windows request:**
  [WINDOWS_REQUEST.md](https://github.com/teeeeooo/oil_level_tracker/blob/spike/webui/spikes/webui/WINDOWS_REQUEST.md).
  - It uses the `spike/webui` ZIP, per-file SHA-256 and a new
    Python 3.14 venv.
  - It covers SPL#4 BASE and SPL#1 BASE from source, the user's hands-on
    checks W2–W9, and a packaged build (W1, size, file count).
  - It asks for one fixed result block.
- **Go:** W1–W4, W7 and W8 pass, and the user rates W5 and W9 usable.

### Windows result (user relay, 2026-10-28) — GO

**The spike verdict is GO for the web UI.** Qt is not needed.

**Run set:**
- Sources were the `spike/webui` ZIP with no SHA-256 mismatch and no CRLF.
- The runtime was:
  - Python 3.14.3;
  - pywebview 6.2.1 and pythonnet 3.2.1;
  - opencv-python-headless 4.14.0.94 and numpy 2.5.4;
  - PyInstaller 6.22.3;
  - WebView2 runtime 156.0.4314.50, under HKLM.
- The OS was Windows 11 (10.0.26200).

The values below come from the relayed `SPIKE` lines.

| ID | Result | Value |
|---|---|---|
| W1 | PASS | One-folder build: 152.3 MB, 105 files |
| W2 | PASS | `WebView2 Edg/156.0.0.0`, from source and from the exe |
| W3 | PASS | `127.0.0.1`; no firewall or security prompt |
| W4 | PASS | SPL#4 BASE: 520 × 544, built in 3.99 s. SPL#1 BASE: 8210 × 773, built in 165.93 s |
| W5 | user: usable | Comes with change requests; see below |
| W6 | △ | The user could not tell snap on from snap off. W6 is not a Go condition |
| W7 | PASS | Seek median: SPL#4 26 ms (n=300); SPL#1 68 ms (n=90) |
| W8 | PASS | The report opens offline, prints to PDF and prints in the app. SPL#4 is 538 KB; SPL#1 is 9.9 MB |
| W9 | user: usable | Render median / max: 130 points, 1.4 / 13.3 ms; 2053 points, 13.4 / 30.0 ms |

Save and resume both work: "저장본 v001 불러옴" appears on rerun.

**Notes:**
- The first SPL#1 run pointed at a bundle capture path that has no video.
  The rerun used the manifest's source video, `SPL#1_Heating_coldstart.mp4`.
- The first SPL#4 session was force-closed, so its log has no
  `window_closed` line. Later runs log `window_closed renderer=edgechromium`.

**Facts for v2 design:**
- SPL#1 is a 68-minute video:
  - the context build takes 2.8 min with sequential decode;
  - the report is 9.9 MB because it embeds the full-width PNG.

**The user's change requests** are design input for the next interview.
They are not spike fixes.
1. Points at the FULL position are clipped into half circles and read as a
   wavy line. Keep points inside the plot.
2. Moving 130 draft points one by one is close to impossible. The intended
   flow is to grab the line at a spot and drag to reshape it, not to move
   points.
3. A missed press pans the graph. Make panning an explicit mode, or
   Shift-drag.
4. Click a time-axis number and type a value to set the visible range.
5. The frame view is good. Video playback there would be better; how to do
   it is open.
6. Defect: a new Foam line is drawn blue like Oil, not orange.
7. Question: what is a FULL segment for? A line at the top already means
   FULL, so that stretch should become FULL automatically.

## Decisions from the post-spike interview (user, 2026-10-28)

These take precedence over the earlier tables where the two differ.

| Topic | Decision |
|---|---|
| UI technology | **Web UI** (pywebview + WebView2), from the GO above. The Qt fallback is dropped |
| Editing | **Grab-and-drag plus a pencil.** Grab the line anywhere and drag; nearby parts follow smoothly, within a width the user adjusts. The pencil redraws a time range and replaces that stretch. The draft is kept as dense samples. Points are not edited one by one |
| FULL / EMPTY | **Automatic from line position.** A line at the Glass top is FULL (`FULL_NO_INTERFACE`); at the bottom it is EMPTY (`EMPTY_NO_INTERFACE`). The only segment tool left is **"cannot judge"**. Those stretches are invalid samples and count against coverage. This replaces the FULL/EMPTY/unknown segments |
| Pan | Explicit: a pan tool and Shift-drag. A plain drag on empty space does not pan. Wheel zoom stays |
| Time axis | Click a time-axis number and type a value to set the visible range |
| Frame view | **Video playback from the first version:** the source file in the browser's player, cropped to the Glass, with the lines drawn over it. The graph cursor follows. Speed control and range repeat are included. A paused frame stays exact |
| Snap | **Not in the first version.** Precision comes from zoom, the background-subtracted view and the frame/video. Reason: the strongest edge can be a Foam top or glare, and the user felt no difference in the spike |
| Report contents | **Header:** the user enters compressor model and test type; the video file name, Recipe name, date-time and report version are filled in automatically. **Body:** the graph, the context image with lines, the final judgment, memos, the judgment-criteria table and the key-time table (compressor start, recovery, violations) |
| Saving | **One inspection folder.** It holds the versioned edit data, the context-image cache and the versioned report HTML. Opening the report or the folder resumes editing. The source video is found by path and SHA-256, not copied |
| Recipe | **A reusable Recipe stays:** Glass name, ellipse, zero line and judgment rule, made once per equipment/camera setup. A camera shift is corrected in that inspection only. The v1 detector settings are dropped |
| Draft | **The Oil line only, by a simple method:** the strongest edge per column, with temporal jumps suppressed, and weak-edge stretches marked "cannot judge". The user adds Foam lines. Draft improvement waits for field use |
| Context build time | 2.8 min on SPL#1 is acceptable. Show progress and the time left, and cache the result in the inspection folder |
| Compressor start / range | Set both before analysis while watching the video. The compressor-start marker can be dragged in the editor, which recomputes the judgment. Changing the range means re-analysis |
| Defect to fix | Foam lines must use their own colour |

**v2 first-version work order** (user-approved):
1. **Start.** Freeze S11 as unmet and open the new roadmap milestone. Create
   the v1 tag and archive branch, then reset `main` to the v2 skeleton. Do
   the deferred cleanup: re-review `sample/output` and delete the merged
   remote branches.
2. **Recipe screen:** Glass ellipse, zero line and judgment rule.
3. **Analysis:** the context image and the Oil draft, with progress and a
   cache.
4. **Editor:**
   - grab-and-drag and the pencil;
   - "cannot judge" stretches;
   - lines and memos;
   - zoom, pan and time-axis input;
   - the frame view and video playback.
5. **Judgment and report:**
   - the judgment, with override and reason;
   - the report;
   - submit and lock;
   - versions.
6. **Windows:** packaging and acceptance with field videos.

**Step 1 runs only when the user says to start v2.** Until then, nothing is
executed.

The routine details stay the agent's call and are reversible:
- the save schema;
- shortcuts;
- the undo depth;
- the report image downscaling for print.

## Interview topics left for after the spike

**Resolved by the post-spike interview above.** The list is kept as asked.

- The spike verdict: web UI or Qt.
- The order of v2 work for the first version.
- How the extraction draft is built, and what it must get right.
- Report details: header, events, other sections.
- Tool behaviour: snap, shortcuts, undo.
- Recipe creation in v2, now that there is no v1 compatibility.
- The schema of the saved edit document.
- When to execute:
  - the S11 freeze;
  - the new milestone in the roadmap;
  - the v1 tag and archive branch, and the `main` reset.
  - Cleanup that the user deferred to that step (2026-10-28):
    - re-review the 150 managed runs in `sample/output/` (311 MB); docs cite
      them by path and SHA-256;
    - delete the five remote branches already merged into `main`;
    - keep the unmerged `codex/ui-ux-refresh` and the two `work/s11-*-20261008`
      branches, which evidence docs cite.

    Local session scratch, caches and the local `work/*` branches were
    already removed on 2026-10-28.

## Detector Governance

- Logic-map nodes: `OIL-PHASE-FILL`, `OIL-AUTHORITY`, `OIL-SELECTOR`, `OIL-PROJECTION` — unchanged; this session touched none.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F10` — unchanged; this session touched none.
- First harmful stage: unchanged since the [graph-editing direction handoff](2026-10-27-graph-editing-direction-handoff.md#detector-governance).
- Existing feature coverage: unchanged; all S11 options stay default OFF.
- Execution scope: a direction interview and a UI spike on a side branch; no detector run, code change or Windows detector execution.
- Logic-map impact: NONE — a handoff.
- Failure-registry impact: NONE — no new mechanism.
