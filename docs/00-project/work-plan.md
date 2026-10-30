# Current Work Plan

**Current milestone:** `V2-4 — Judgment and report` / `ACTIVE` (started
2026-10-30; its start decisions wait on the user).
**Last completed:** `V2-3 — Editor` / `DONE` (2026-10-30).

This is the sole owner of the current state, authorization and next action.
Rewrite it; do not append to it.

## Accepted baseline

- **Product SSOT:** [product.md](../10-product/product.md).
  - Goal and the acceptance criteria A1–A9.
  - Acceptance videos: SPL#1 and SPL#4.
  - **Where the time limits are judged** (user, 2026-10-30, §2): A4–A6
    pass or fail on the workstation. The slowest PC is the worst case,
    for reference only: its timings point to simple speed-ups, and a miss
    there holds nothing up.
  - All product decisions. On 2026-10-29 the user settled the Recipe (§3),
    the judgment rule (§5) and the data folder (§8) at the V2-1 start, and
    the inspection flow, the analysis setup (§3), the draft method (§4)
    and the editing aids and snap (§6) at the V2-2 start.
- **Architecture:** [architecture.md](../20-architecture/architecture.md).
  The judgment lives only in Python. Since 2026-10-29 it uses v1-style
  layers:
  - `domain` ← `application` (use cases and ports) ← `adapters`
    (`video`, `storage`, `report`, `http`, `desktop`);
  - `bootstrap.py` is the only wiring point;
  - there is no NumPy in `domain` or `application`;
  - during a drag, the bands and the judgment update from the API after
    release.
  - A test enforces the dependency rule (`tests/test_architecture.py`).
- **Visual rules:** [DESIGN.md](../../DESIGN.md), Fluent 2 light.
  - The editor layout in [design/mockup/editor.html](../../design/mockup/editor.html)
    is **confirmed by the user** (2026-10-28), and its V2-3 update too
    (2026-10-29).
  - The inspection list and analysis setup in
    [design/mockup/inspection.html](../../design/mockup/inspection.html)
    are **confirmed by the user** (2026-10-29).
  - The Recipe layout in [design/mockup/recipe.html](../../design/mockup/recipe.html)
    is **confirmed by the user** (2026-10-29). The Glass editing follows v1.
- **V2-1 result:** the Recipe screen and the `.recipe.json` file
  ([recipe-file.md](../20-architecture/recipe-file.md)) passed the Windows
  run; see
  [2026-10-29-v2-1-recipe-windows-result.md](../60-evidence/2026-10-29-v2-1-recipe-windows-result.md).
  - The user's Recipes `SPL#4_test1_607bccb` (BASE, ACCUM) and
    `SPL#1_test1_607bccb` (BASE) stay on the Windows workstation.
  - **Not yet shown on Windows:** a save at a frame other than the first,
    a redirected Documents folder, and the wording of the resolution
    refusal.
- **V2-2 result:** the inspection list, the new-inspection flow, the
  analysis setup, the progress dialog and the read-only result passed the
  Windows run on source `0df5ce6`; see
  [2026-10-29-v2-2-analysis-flow-windows-result.md](../60-evidence/2026-10-29-v2-2-analysis-flow-windows-result.md).
  - **The analysis:** one software-decoded pass for every Glass, with the
    row medians on worker threads; the drafts by dynamic programming
    (method B); the cache as PNG pieces in
    [inspection-folder.md](../20-architecture/inspection-folder.md).
    Why: the [draft comparison](../60-evidence/2026-10-29-v2-2-draft-comparison-windows-result.md)
    and the [slowest-PC timing](../60-evidence/2026-10-29-v2-2-slowest-pc-timing-windows-result.md).
  - **A4 so far:** SPL#1 takes 60.6 s in the app on the workstation (with
    another job at about 50 % CPU), 46.4 s for the adapter alone, and
    169.7 s for the adapter on the slowest PC (limit 180 s).
  - **Three inspections stay on the workstation** for V2-3: SPL#4 (an
    ACCUM correction of `cx +1`), and SPL#1 twice. Their folders and
    SHA-256 values are in the result.
  - The web screens share `web/frame.js` (frame view and Glass editing)
    and `web/render.js` (drawing, also for the report).
- **V2-2 follow-up** (user, 2026-10-29, after the Windows run; seen on
  Windows in the V2-3 run):
  - the analysis range band on the scrub bar is yellow (`--range-fill`,
    `--range-edge`);
  - a time field shows a typed value as `mm:ss.s` once entered;
  - **the inspection name** (Product SSOT §3, §8): optional in the setup,
    shown in the list and the result, and naming the folder; without one,
    the folder is named as before. It is fixed once the folder exists;
  - **fixed:** the local server's listen queue was 5, so a page load
    sometimes lost a JavaScript module to a reset connection and stayed
    blank (seen as a flaky browser smoke test). It is now 64.
- **V2-3 result:** the editor passed on the workstation in
  [the run](../60-evidence/2026-10-30-v2-3-editor-windows-result.md) and
  [its re-check](../60-evidence/2026-10-30-v2-3-editor-recheck-windows-result.md).
  - **The time limits pass there:** A4 39.3 s for SPL#1, A5 2.8 / 8.9 ms,
    the exact frame 56 ms, 1× playback in the `<video>` (SPL#1 is H.264).
    The slowest PC is reference only (Product SSOT §2).
  - **The editor:** `web/editor.js`, `lines.js`, `player.js`, with
    `render.js` drawing in layers (back, lines, marks) so a drag redraws
    only the lines. Edits are `edits.json` beside `inspection.json`
    ([inspection-folder.md](../20-architecture/inspection-folder.md)),
    saved on "저장"; leaving or closing the window with unsaved edits asks
    (WinForms on Windows). Re-analysis keeps the edits inside the new
    range. The SHA-256 warning (A9) checks the source on each open.
  - **The user's decisions of 2026-10-30** (Product SSOT §6): Delete
    empties the line chosen in "그릴 선"; the point line follows the snap
    (along the edges, or straight); the pencil's "수평·수직" switch; the
    view stays inside the analysed range, with "전체 보기".
  - **After the re-check** (user, 2026-10-30): with the snap on, the point
    line keeps within 8 px of the straight line between two points
    (`video/trace.py`); free to follow the strongest edges, it ran to the
    image's top or bottom in practice (for spans of 10 s and more).
  - **Not yet seen on Windows:** the upright stroke as a vertical step
    (`ca7d3ee`, from the re-check's C4 note) and the point line's 8 px
    band.
- **Documentation:** the v1 conventions, per [docs/README.md](../README.md).
  - numbered folders;
  - the date catalog and its pre-push check;
  - the roadmap and the execution policy;
  - the recall index.
- **The repository holds only v2.**
  - v1 is at tag `v1-final` and branch `archive/v1`.
  - v1 local evidence is at `~/Developer/oil_level_tracker-v1-evidence/`.
  - Branch `spike/webui` is kept for porting.

## V2-4 — Judgment and report

**Scope** (roadmap; Product SSOT §3 steps 5–6, §5 and §7):
- the judgment per Glass, computed from the edited Oil line by the Recipe's
  rule (§5), recomputed when the lines or the compressor start change;
  A3 asks for unit tests with fixed cases;
- the override per Glass, with a required reason that is saved;
- submitting: every Glass checked first; submitting locks that version; to
  resubmit, open it, edit and save a new version;
- the report: self-contained HTML that works offline and prints to PDF,
  drawn by the editor's drawing module (`render.js`), with the contents
  §7 lists.

**Already decided:** the rule and its modes (§5, user, 2026-10-29), the
coverage threshold, Foam never counting, and the report's contents (§7).
DESIGN.md §5 keeps a place in the editor's right column for the judgment
panel (computed result, override, reason).

**Steps:**
1. **Start decisions and mock-ups — done** (2026-10-30).
   - **The user's decisions** (2026-10-30, Product SSOT §3 and §7):
     - each Glass is checked with its own "확인" on the judgment; changing
       that Glass's lines afterwards takes the check off;
     - a resubmission's version stays in the same inspection folder (one
       subfolder each); the list keeps one row per inspection;
     - the report header (compressor model, test type) is entered with the
       inspection name in the analysis setup, per inspection;
     - the mock-ups come first;
     - **the report shows the final judgment,** and for a Glass the user
       judged, one line "판정 사유: <reason>", never "덮어씀"; the computed
       result and how much of the draft was changed are the user's record
       in the app (Product SSOT §7, DESIGN.md §2.4).
   - **No report is written yet:** there is no `adapters/report`, and the
     editor's "제출" is disabled. The folder layout reserves the versions
     and their report ([inspection-folder.md](../20-architecture/inspection-folder.md)).
   - **The mock-ups, confirmed by the user** and written into DESIGN.md
     §2.3, §2.4 and §5:
     - [editor.html](../../design/mockup/editor.html) `#judge`,
       `#override`, `#checked`, `#submit`, `#locked`: the judgment panel
       (the computed result and its grounds, the override with a required
       reason, "이 Glass 확인"), the Glass picker's badges, the submit
       dialog, and a submitted version (read-only, an info bar with "보고서
       열기", "고쳐서 다시 제출 (v2)…" and the version picker);
     - [report.html](../../design/mockup/report.html): A4 landscape, the
       header and the judgment summary on page 1, then a page per Glass;
     - [inspection.html](../../design/mockup/inspection.html): "검사 정보"
       in the setup (name, compressor model, test type) and the submitted
       state in the list ("v1 제출함", "v2 고치는 중").
   - **The agent's choices inside them,** confirmed with the mock-ups: the
     check also comes off when that Glass's "cannot judge" stretches or the
     compressor start change; the header stays editable in the editor
     until submitting; the override is a 자동/합격/불합격 choice; the
     versions live in `versions\NNN\` with the edits, the judgment and
     `report.html`; a HOLD mode's longest violation is `--violation-band`;
     the first Glass shares page 1 with the header.
2. **`domain`, the judgment** (§5) — done: `domain/judgment.py`,
   `judge(times, glass edits, Glass, compressor start)` gives 합격, 불합격
   or 검토 필요 with a Korean reason, the coverage, the recovery (RECOVERY)
   or the longest violation (the HOLD modes); 22 fixed cases in
   `tests/test_domain_judgment.py` (A3). Written anew: v1's
   `domain/judgment.py` measured a violation from the first violating
   sample to the last, which §5 drops.
   - **Agent's choices where §5 is silent,** to show the user: invalid
     samples inside a recovery's hold are passed over (as in v1); an
     invalid sample ends a violation run; a run lasts its sample count ×
     0.5 s; the HOLD modes ignore the compressor start; the measures are
     still found when the valid share is too low.
3. **The judgment in the editor — done** (2026-10-30):
   - **API:** each Glass's states carry its judgment (`computed`,
     `verdict`, `reason`, `recovery` or `violation`); the edits carry each
     Glass's `decision` (`override`, `reason`, `checked_at`).
   - **`edits.json` schema 2** adds the decision; schema 1 files from
     V2-3, which the workstation keeps, read as undecided
     ([inspection-folder.md](../20-architecture/inspection-folder.md)).
     Re-analysis keeps the override and reason and clears the check.
   - **The panel** (DESIGN.md §5): the final badge, "직접 판정 · 자동 판정은
     …", the computed reason, the grounds, 자동/합격/불합격 with the
     required reason, "이 Glass 확인" and "확인 풀기"; the Glass picker
     shows "확인 전" or the final judgment; the Glass panel's 편집 기록.
     The check comes off when the history records, undoes or redoes a
     change to that Glass's Oil line or "cannot judge" stretches, or to
     the compressor start (`History.listener`). 제출 stays disabled.
4. **The report header — done** (2026-10-30):
   - `inspection.json` schema 2 adds `report_header` (`compressor_model`,
     `test_type`; trimmed, `null` when blank, at most 60 characters);
     schema 1 files read with an empty header
     ([inspection-folder.md](../20-architecture/inspection-folder.md)).
   - The setup's 검사 정보 has 검사 이름, 압축기 모델 and 시험 종류; the
     editor's has the two header fields (`web/header.js`, shared). A new
     inspection's header goes with "분석 시작"; once the folder exists, a
     change is saved at once through `POST /api/inspections/<id>/header`,
     apart from the edits' "저장", and is sent before leaving the editor
     or the setup. A re-analysis keeps it.
   - **Agent's choices, to show the user:** saving at once (the open
     question of the handoff); the 60-character limit; the editor's fields
     side by side, as in the setup. Nothing locks the header yet: step 5
     does, on submitting.
5. **Submitting and versions — done** (2026-10-30), without the report:
   - **Format** ([inspection-folder.md](../20-architecture/inspection-folder.md)
     "Versions"): `versions\NNN\` holds `version.json` (each Glass's
     final and computed judgment, the user's decision and check),
     `edits.json`, and copies of `inspection.json` and `recipe.json`,
     written through `NNN.partial\`; then the working `edits.json` is
     removed. The state follows from the folder: versions without
     `edits.json` are locked; with it, the next version is being edited.
   - **Code:** `domain/version.py`; `Editing.submit`, `.revise` and
     `.open(version)`; `is_locked` refuses saving, submitting, the report
     header and re-analysis (`Locked`, 409); API `POST …/submit`,
     `POST …/revise`, `GET …/edits?version=N` and the list's `submitted`
     and `revising`.
   - **Screens:** the submit dialog; a submitted version read-only under
     a `--brand-tint` bar with the version picker and "고쳐서 다시 제출
     (v<N+1>)…"; the list's "v<N> 제출함" with each Glass's judgment, or
     "v<N+1> 고치는 중".
   - **Agent's choices, to show the user:** revising keeps each Glass's
     decision and check (a change takes a check off as before); the bar
     stays while the next version is edited; on a submitted version the
     editing panels are hidden; an older version that a later
     re-analysis no longer fits opens only as its report; the app sets no
     read-only file attributes (the lock is the app's).
6. **The report — done** (2026-10-30):
   - `adapters/report` (`HtmlReports`) writes `versions\NNN\report.html`
     on submitting: Python writes the text and the tables (header,
     judgment summary, then per Glass the final badge, "판정 사유" for a
     Glass the user judged, the criteria and key-time tables and the
     memos); `web/render.js` with `web/report.js`, inlined, draws the
     graph, the context image and the axis on opening. The context image
     is joined from the cache, scaled to at most 2,000 × 360 px and
     embedded as JPEG; a 68-minute video with three Glasses and noise
     images stays under 5 MB (A7, `tests/test_report.py`).
   - "보고서 열기" (`POST …/versions/<n>/report/open`) opens it in the
     default browser; printing makes an A4 landscape PDF, in colour.
   - The editor's graph also shows a HOLD mode's longest violation.
   - Agent's choices: DESIGN.md §5 "Report".
7. A Windows run of V2-4, with the V2-3 follow-ups (the upright stroke,
   the point line's 8 px band).

## Session handoff — 2026-10-30 (fifth)

**The session closed after `29cfbf2`** (and this handoff). The working
tree is clean, and `main` and the remote are in sync. 241 tests pass on
macOS.

**Where it stands:** V2-3 is `DONE`. V2-4 is `ACTIVE`: steps 1–3 are done
(start decisions and confirmed mock-ups, the judgment in `domain`, the
judgment panel with the user's verdict and the check in the editor).
**Next is step 4, the report header,** then 5 (submitting and versions),
6 (the report) and 7 (the Windows run). Nothing waits on the user.

**Resume:** read this file (the V2-4 steps above), the Product SSOT §3,
§5 and §7, DESIGN.md §2.4 and §5, and the mock-ups
[editor.html](../../design/mockup/editor.html) (`#judge` … `#locked`),
[report.html](../../design/mockup/report.html) and
[inspection.html](../../design/mockup/inspection.html). Then as needed:
- `domain/judgment.py` (`judge`, `final_verdict`) and `domain/edits.py`
  (`Decision` on `GlassEdits`);
- `application/editing.py` (`GlassState.judgment`, `.verdict`);
- `adapters/http/api.py` (`judgment_json`, `_decision`) and
  `adapters/storage/inspection_files.py` (`edits.json` schema 2);
- `web/editor.js` ("the judgment" section: `takeCheckOff`, `decide`,
  `renderJudgment`, `renderGlassPicker`) and `web/lines.js`
  (`History.listener`).

**Step 4 plan:** the header (`compressor_model`, `test_type`, both
optional) is part of the inspection, so `inspection.json` gains it (a
schema change: read the files without it, as `edits.json` did). The setup
shows it under 검사 정보 with the name (DESIGN.md §5); the editor's 검사
정보 section edits it until submitting. Decide whether an edit there saves
at once or with "저장" (it is not part of the edits).

**Step 5 notes:** submitting saves first, needs every Glass checked, and
writes `versions\NNN\` (edits, judgment, report); a submitted version is
read-only; "고쳐서 다시 제출 (vN+1)" starts a working copy from it; the list
shows one row per inspection with the latest state. `inspection-folder.md`
reserves the layout; write its format there before the code.

**The user's rules that shape V2-4** (2026-10-30):
- the report shows the final judgment only; a Glass the user judged gets
  one line "판정 사유: <reason>", never "덮어씀"; the computed result and the
  edit record stay in the app;
- versions stay in the same inspection folder;
- reply to the user in Korean (saved in memory).

**Agent's choices in V2-3 to show the user if asked:**
- **Views:** "전체 보기" in the graph header; the selected range kept
  while the range tool stays (the video's range repeat uses it).
- **Pencil:** its switch in the 편집 panel, with no key; an upright stroke
  joins two neighbouring samples.
- **Point line:** inside its 8 px band a luma step below 6 counts as no
  edge, as for the snap; straight joins interpolated in time; points kept in time
  order; a click at a sample that has a point replaces it; the snap
  settles a point as it does a drag; straight dotted guides until a path
  arrives.
- **Elsewhere:** the source-warning bar (DESIGN.md §2.7 tokens); the
  source check on every editor open (about 5 s of background hashing on
  the slowest PC); the compressor in 0.1 s steps; memo pins on the graph
  only; the memo dialog.
- DESIGN.md §5 lists them all.

**Learned these sessions:**
- A request whose agent's quick O/X was wrong once (the console row) is
  read from its raw lines; likewise a mock-up label can carry meaning the
  user did not intend ("덮어씀" read as tampering). Show wording that a
  reader outside the team will see before building it.
- A Windows agent's account of the code can be wrong: it told the user the
  draft does not follow the point line's edges, when both use the same
  edge strength. Check the code before relaying such an answer.
- A request's steps must not undo what its criteria count: E7 told the
  user to Delete "몇 초" anywhere, and R2 then counted drawn Oil. Say where
  each step acts when a later criterion reads its result.
- A Windows agent's own O/X can differ from the fixed criterion (it passed
  the console row because the traceback did not come at a close). Judge
  from the relayed lines, not the agent's table.
- Tests that pass on macOS can fail on Windows: an open file cannot be
  deleted or renamed there (close every video session first), and
  `str(Path)` uses backslashes (compare paths as `Path`).
- zsh does not split an unquoted variable: a re-pin wrote
  `source=766d5e5886c9 52 files=` until it was caught. Grep pinned values
  after writing them.
- Playwright's `get_by_title` and `get_by_label` match hidden elements:
  scope locators to the screen (the editor repeats the transport labels).
- `typing()` counts only text fields; a clicked switch or picker must not
  turn the shortcut keys off.
- Exact frames on macOS take 60–80 ms, nearly all of it OpenCV seeking and
  decoding; the page adds little.
- The user wants parallel progress when Windows is out of reach, inside
  the decisions already made; ask before crossing one.
- `pytest | tail -1 && git commit` commits whatever the tests say:
  `8ec20d4` went out with a failing smoke test (fixed in `942dc55`).
  Check pytest's exit code before committing.
- The editor's panels update at once, but the plots and the time axis
  redraw on the next animation frame: smoke checks wait for the drawn
  marks instead of counting them at once.
- Async ordering in the page: a `<dialog>`'s "close" event comes a task
  later than `close()`, parallel fetches can arrive swapped, and a save's
  response can come after newer edits. Keep such state where it is
  changed, send in order, and count changes across an await.
- A check written for a race must fail without the fix: the save-race
  check passed at first because an earlier notice was still on screen.

## Open items

**Speed on the slowest PC, for reference** (the limits are judged on the
workstation since 2026-10-30; these are simple speed-ups, never blockers):
- **Less CPU work in the analysis.** The slowest PC took 169.7 s for the
  adapter (limit 180 s on the workstation, where it took 46.4 s); nearly
  all of it is reading the video (`grab` 113 s, `retrieve` 45 s).
  - **The draft search — done** (`ae4873c`): about 10× faster, the same
    best path. Exact ties (a saturated edge) now take the upper row.
  - **Cheaper medians — done** (`908f624`): the `uint8` partition, 2.46×
    less worker time on that PC with identical values; about 11 s less
    over SPL#1 by the two-minute pass (an estimate, to confirm in a run).
  - **Facts measured on macOS, 2026-10-29 evening:**
    - OpenCV cannot skip to a key frame: its seek decodes from the
      previous one (~59 ms, like ~90 frames in order).
    - With `CAP_PROP_CONVERT_RGB` off, OpenCV returns only the luma plane
      and warns on every frame. That cuts `retrieve` by 72 % and the
      medians by 68 %, but the context image turns grey: the user's call.
    - PyAV 19.0.2 (in a scratch venv only): skipping to key frames
      decoded 53–95 % of the frames but saved no time with frame
      threading (single-threaded decoding saved 17–29 % but is 2–3×
      slower). Its colours differ from OpenCV's by up to 2.6 levels. It
      ships a second FFmpeg (macOS warns about the duplicate libraries).
      Band-only conversion works. A new dependency is the user's decision.
- **What the app adds:** through the app's server the analysis took
  163.0 s on the slowest PC (2026-10-30), about what the adapter alone
  should take after the faster draft search. So the server adds little;
  the workstation's 60.6 s against 46.4 s was the other job. The window
  (pywebview) is timed in V2-5.
- **Exact frames** took 230 ms on the slowest PC (key frames every 250
  frames). A cheap gain if wanted: keep the frames decoded on the way to
  a seek, so stepping back a frame and clicking nearby are instant.

**The next Windows run** also covers the upright stroke (`ca7d3ee`) and
the point line's 8 px band, as each run covered the previous follow-up.

**Small facts:**
- `AnalysisSettings.sample_count` counts to `end_sec`, but the analysis
  stops at the last frame, so it can be one more than the analysis gives
  when the range ends at the video's end. The setup caption counts as the
  analysis does.
- Closing the window during an analysis took "about 10 s" on Windows; the
  app's own part takes under 1 s on macOS. A close with no analysis
  running has not been timed there.
- The slowest PC reported Python 3.15.2 instead of 3.14; the picture was
  identical.

## Notes for Windows runs

- **Agent requests:** copy the [V2-2 flow request](../40-operations/2026-10-29-v2-2-analysis-flow-windows-request.md):
  a commit ZIP, per-file SHA-256 values, a new venv, criteria fixed before
  the run, one result block. `scripts/inspection_summary.py` and
  `scripts/recipe_summary.py` print the exact values to judge.
- **A PC without an agent:** copy the
  [slowest-PC request](../40-operations/2026-10-29-v2-2-slowest-pc-timing-windows-request.md):
  the user runs a few commands; `scripts/time_analysis.py` writes a
  Markdown result.
- **Expected Windows test line:** run pytest on macOS without Playwright
  (`sys.modules['playwright'] = None` and
  `sys.modules['playwright.sync_api'] = None`, then `pytest.main`), then
  subtract one passed and add one skipped for the macOS-only Documents
  test. At `8c9ea35`: `202 passed, 3 skipped` on macOS, so
  `201 passed, 4 skipped` on Windows when its venv has no Playwright.
- `scripts/compare_draft_methods.py` is the diagnostic behind the draft
  decision; it is the only code that reads v1 files.
- Smoke-test screenshots: set `OLT_SMOKE_SHOTS` to a folder.
- The mock-up `design/mockup/recipe.html` predates the speed field and
  the help dialog; DESIGN.md governs where they differ.

## Known limits, accepted for now

- A zero line at the very top or bottom of its ellipse can be moved only
  by typing. At that height its chord is a point under the edge handle.
- There is no Recipe deletion in the first version (user, 2026-10-29).
- The PyInstaller build (V2-5) must ship `src/oil_tracker/web/` as data.
- **On the slowest PC (reference only),** the analysis takes 163.0 s
  through the app's server and an exact frame 230 ms. The user finds that
  usable (2026-10-30).

## Local environment (macOS)

- `.venv` is the old v1 venv.
  - It now also has `pywebview==6.2.1` and `playwright` 1.64.1.
  - The v2 package is not installed in it. Run the app with
    `PYTHONPATH=src .venv/bin/python -m oil_tracker`; pytest finds `src`
    through `pyproject.toml`.
- The smoke test drives the system Chrome (`channel="chrome"`).
- Mock-up screenshots come from headless Chrome. The in-app browser pane
  cannot open `file://`.

## Left to the user, with no deadline

- deleting `~/Developer/oil_level_tracker-v1-evidence/`;
- deleting branch `spike/webui` once the porting is done.

The three v1 remote branches that v1 docs cite stay.

## Next

- **Done:** V2-3 (2026-10-30): the workstation run and its re-check pass;
  the upright stroke and the point line's 8 px band followed.
- **Next:** V2-4 step 4, the report header; then submitting and versions,
  and the report.
