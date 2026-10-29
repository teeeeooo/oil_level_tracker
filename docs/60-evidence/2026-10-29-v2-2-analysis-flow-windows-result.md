# V2-2 inspection and analysis flow — Windows result (2026-10-29)

**Verdict:** R1–R10 and R12–R15 pass; R11 is recorded only. V2-2 is
closed.
- **A4 in the app:** SPL#1 takes **60.6 s** on the workstation, from
  "분석 시작" to the cache written. That is well under 180 s, but over the
  60 s flag the request fixed. The adapter alone took 46.4 s on the same
  PC, so the cause of the gap must be found before V2-5.

- **Request:** [2026-10-29-v2-2-analysis-flow-windows-request.md](../40-operations/2026-10-29-v2-2-analysis-flow-windows-request.md).
  Its criteria were fixed before the run.
- **Source run:** commit `0df5ce6`, confirmed by R1 (72 per-file SHA-256
  values).
- **Who ran it:** the user in the app window, and the Windows agent for the
  commands, on the workstation.
- **Relay:** the user relayed the result block as text, with the agent's
  own verdict on top.
  - Every criterion below was rechecked against the relayed rows.
  - In the §6 output, the agent wrapped the first `inspection` line after
    `compressor=11.0`; the values are complete.

## Environment

| Item | Value |
|---|---|
| CPU | AMD Ryzen Threadripper PRO 7945WX (the workstation of the earlier runs) |
| Python | 3.14.3 |
| pywebview | 6.2.1 |
| pythonnet / clr_loader | 3.2.1 / 0.3.1 |
| OpenCV / NumPy | 4.14.0.94 (headless) / 2.5.4 |
| pytest | 9.2.0 |
| WebView2 runtime | 156.0.4314.50 |
| Firewall or security prompt | none |
| Other heavy work | none left running, as relayed |
| Documents | `C:\Users\teeoo.kim\Documents` |

## Judgment

| ID | Relayed evidence | Verdict |
|---|---|---|
| R1 | `checked=72 mismatched=0`, no `MISMATCH` line | PASS |
| R2 | `140 passed, 3 skipped in 22.66s` | PASS |
| R3 | O: the inspection list was the first screen; F1 opened its help | PASS |
| R4 | O: the file dialog, the picker with the video facts, no greyed row, then the setup | PASS |
| R5 | O: the first problem and its wording, `04:20.0`, 520 samples, `[` `]` in Korean input mode, "지금", the `abc` error | PASS |
| R6 | O for each: the speed field, the help button, **F1**, the `?` key, and all three ways to close | PASS |
| R7 | O: one frame per key press, and the picture holds still | PASS |
| R8 | O for the confirm dialog and for no new row; `inspections=0` before and `inspections=3` after | PASS |
| R9 | O. SPL#4 `state=ANALYSED`, `times=520`, BASE `recipe_diff="none"`, ACCUM `recipe_diff="cx +1"`, both `pieces=1 files=2/2`, BASE `rows=484`, ACCUM `rows=298` | PASS |
| R10 | O. SPL#1 first inspection `state=ANALYSED`, `times=8210`, `recipe_diff="none"`, `rows=728 pieces=3 files=6/6`, `empty=87.7%`. **A4:** `cache_written=60.6` ≤ 180 | PASS; over the 60 s flag (below) |
| R11 | "이상 없음": no slow or halting switches | recorded |
| R12 | O: cancelled between 10 and 40 %; the setup, the notice and the single "분석 안 됨" row as described; the settings stayed | PASS |
| R13 | O: closed between 10 and 40 %; the prompt came back in "about 10 s"; "분석 안 됨" after reopening; then `state=ANALYSED`, `times=8210`, `files=6/6` | PASS, at the limit (below) |
| R14 | O: Explorer opened the Inspections folder | PASS |
| R15 | `unreadable=0`; all three `partial=no` and `sha256_check=same`; `recipe_updated_at` 04:38:15 and 04:43:17 UTC, before `created_at` 10:07:45, 10:10:52 and 10:13:34 | PASS |
| — | No console lines at either close, so no `Traceback` | PASS |

**First confirmed on Windows:**
- F1, the `?` key and the speed field in WebView2 (the V2-1 follow-up);
- a JavaScript `confirm` dialog in WebView2 (R8);
- `[` and `]` in Korean input mode, through the physical key code (R5);
- closing the window during an analysis cancels it and leaves
  "분석 안 됨", and the list resumes it (R13);
- the cache swap and the source SHA-256 on a second thread (R15).

## The inspections left on the workstation

They stay in `Documents\OilLevelTracker\Inspections` for V2-3.

| Folder | Video | Range | Compressor start | Glass copy | `cache_written` | Empty |
|---|---|---|---|---|---|---|
| `20261029-1907_SPL#4_Cooling_onoff_#2` | SPL#4, SHA-256 `9f494a6fd0a0…` | 0.0–260.0 s | 11.0 s | ACCUM `cx +1` | 3.9 s | BASE 5.0 %, ACCUM 50.8 % |
| `20261029-1910_SPL#1_Heating_coldstart` | SPL#1, SHA-256 `fb03d7428c17…` | 0.0–4104.6 s | 485.0 s | none | 60.6 s | BASE 87.7 % |
| `20261029-1913_SPL#1_Heating_coldstart` | SPL#1 | 0.0–4104.6 s | 485.0 s | none | 299.5 s, including the cancel, the close and the reopening | BASE 87.7 % |

- **The drafts equal the timing runs:** SPL#1 87.7 % against the
  script's 88 %, and SPL#4 BASE 5.0 % against 5 %. ACCUM's 50.8 % is with
  the 1 px correction (the script's 51 % was without it).
- The SPL#4 Recipe names the second Glass `ACCUM`.

## A4 in the app: 60.6 s against 46.4 s

- **What 60.6 s covers:** from "분석 시작" (`created_at`, cut to the
  second, so up to 1 s too long) to `cache\analysis.json` written. That
  span holds the pass, the drafts, the PNG pieces, the wait for the
  SHA-256 and the cache write (0.6 s, the gap to `seconds=60`).
- **The gap is 14.2 s (31 %).** This run cannot separate its causes,
  because the app reports no stage times:
  - **Run-to-run spread on the workstation.** The 46.4 s comes from one
    script run, hours earlier, possibly beside the e-mail embedding job.
  - **Work the app adds during the analysis.** The WebView2 window, the
    local server and the progress polling share the process and the CPU.
- **Why it matters:** V2-5 judges A4 in the app on the slowest PC, where
  the script took 169.7 s of 180 s. A 31 % app overhead there would fail
  A4.
- **Next:** run `scripts/time_analysis.py` and the app one after the other
  on the same PC. If the gap stays, time the stages inside the app. This
  belongs with the slowest-PC speed-up, before V2-5.

## Limits of this evidence

- **The close time is rough.** "About 10 s" sits at R13's limit. On macOS
  the app's own close during an analysis took at most 0.6 s, and the
  process ended within 1.5 s, leaving "분석 안 됨". The rest on Windows is
  the window shutdown or the estimate. A close with no analysis running
  was not timed for comparison.
- **The cancel and close points were not recorded** beyond "10–40 %".
- **Not shown on Windows:**
  - a greyed Recipe of another frame size (every Recipe there is
    1920 × 1080);
  - "이 영상으로 새 Recipe 만들기" from the picker;
  - an inspection that ends "분석 실패".
- **One PC.** The app was not run on the slowest PC.

## User comments

| Comment | Routing |
|---|---|
| R5: the range band (`--brand-tint`) is too faint and close to the blue of the scrub bar; it should be a yellow tone | A DESIGN.md colour change. Waits for the user: now as a small follow-up, or with the V2-3 transport, which reuses the bar |
| Opinion 1: the compressor start field is unclear between seconds and minutes:seconds; a number typed as seconds should turn into `mm:ss.s` once entered | Fits the time field of DESIGN.md §4. Waits for the user, as above |
| Opinion 2: the result screen has no line drawing or zoom yet; the layout and legibility are good | As designed: the result is read-only in V2-2. V2-3 adds the editing, zoom and video to this screen (Product SSOT §6) |
| Opinion 3: the user would like to type a name for each inspection | A product decision: Product SSOT §8 names the folder from the time and the video, and §7 lets the user enter the compressor model and test type for the report. Waits for the user |
