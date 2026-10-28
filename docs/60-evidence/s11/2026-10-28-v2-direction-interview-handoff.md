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

## Interview topics left for after the spike

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

## Detector Governance

- Logic-map nodes: none touched.
- Failure-registry entries: none touched.
- First harmful stage: unchanged since the [graph-editing direction handoff](2026-10-27-graph-editing-direction-handoff.md#detector-governance).
- Existing feature coverage: unchanged; all S11 options stay default OFF.
- Execution scope: a direction interview and a UI spike on a side branch; no detector run, code change or Windows detector execution.
- Logic-map impact: NONE — a handoff.
- Failure-registry impact: NONE — no new mechanism.
