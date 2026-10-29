# V2-1 Recipe screen — Windows result (2026-10-29)

**Verdict:** R1–R12 pass. V2-1 is closed.

- **Request:** [2026-10-29-v2-1-recipe-windows-request.md](../40-operations/2026-10-29-v2-1-recipe-windows-request.md).
  Its criteria were fixed before the run.
- **Source run:** commit `4ea7ade`, confirmed by R1 (41 per-file SHA-256
  values). The ZIP was taken from `main` at `607bccb`, which differs from
  `4ea7ade` only in documents.
- **Result file:** on the Windows PC only, at
  `C:\0.Coding\oil_level_tracker-main\v2-1_run_20261029\result.md`.
- **Relay:** the user relayed the result block as text.
  - The Windows agent shortened the `recipe` and `glass` lines of §5 instead
    of copying them verbatim.
  - The fields the criteria use (`glasses`, `problems`, `source`, `t`,
    `frame`) are present for the two Recipes judged.
  - `recipes=3` matches the three `recipe` lines listed.

## Environment

| Item | Value |
|---|---|
| Python | 3.14.3 |
| pywebview | 6.2.1 |
| pythonnet / clr_loader | 3.2.1 / 0.3.1 |
| OpenCV / NumPy | 4.14.0.94 / 2.5.4 |
| pytest | 9.2.0 |
| WebView2 runtime | 156.0.4314.50 |
| Firewall or security prompt | none |

## Judgment

| ID | Relayed evidence | Verdict |
|---|---|---|
| R1 | `checked=41 mismatched=0`, no `MISMATCH` line | PASS |
| R2 | `77 passed, 2 skipped in 9.24s` | PASS |
| R3 | `documents=C:\Users\teeoo.kim\Documents` equals `GetFolderPath('MyDocuments')`; the app folder and `folder=` are `…\Documents\OilLevelTracker\Recipes` | PASS |
| R4 | O: the file dialog opened; scrubbing, playback and frame steps worked | PASS |
| R5 | O: the user judged the Glass editing usable | PASS |
| R6 | O for "숫자를 입력하세요." and for the save refused at `-1` | PASS |
| R7 | The SPL#4 Recipe (`SPL#4_test1_607bccb`): `glasses=2 problems=0`, source `SPL#4_Cooling_onoff_#2.mp4`, `frame=1920x1080` equal to the SPL#4 `video` size | PASS |
| R8 | `t=0.000` against the noted 0.00 s | PASS |
| R9 | O: the reopened Recipe showed its reference frame and Glasses in place | PASS |
| R10 | Both `video` lines are `size=1920x1080`, and SPL#1 opened | PASS |
| R11 | O: Explorer opened the Recipes folder | PASS |
| R12 | The SPL#1 Recipe (`SPL#1_test1_607bccb`): `glasses=1 problems=0`, source `SPL#1_Heating_coldstart.mp4` | PASS |
| — | Console after closing: no lines, no `Traceback` | PASS |

**First confirmed on Windows:**
- the Documents known-folder API (R3);
- the WebView2 file dialog called from the HTTP thread (R4);
- `os.startfile` for "폴더 열기" (R11).

## Limits of this evidence

- **R8 does not separate the shown frame from the first frame.** Both
  Recipes were saved at 0.0 s. The rule that the frame on screen at save
  becomes the reference is shown only by the macOS smoke check, which saves
  at 0.2 s.
- **Documents is not redirected on this PC.** Following a redirected
  Documents folder, for example to OneDrive, is still untested.
- **The refusal path of R10 was not required,** because the two videos share
  a resolution. The agent reports that another video, relayed as
  1270x780, was refused. Its message was not relayed.
- **The Recipe names differ from the request** (`SPL#4 냉각`,
  `SPL#1 가열`). The lines were identified by their Glass count and source.
  A third Recipe, `SPL#4_test2_607bccb` with one Glass, is also in the
  folder.
- **The SPL#1 Glass line was not relayed;** its mode comes from the user's
  R5 entry.

## Recipes left on the Windows PC for V2-2

| Recipe | Glass: mode (user's choice) |
|---|---|
| `SPL#4_test1_607bccb` | BASE: `RECOVERY`; Accum: `HOLD_BELOW_ZERO` |
| `SPL#1_test1_607bccb` | BASE: `RECOVERY` |
| `SPL#4_test2_607bccb` | one Glass, not described |

## Video facts

| Video | Bytes | Size | fps | Frames | Duration |
|---|---|---|---|---|---|
| `SPL#4_Cooling_onoff_#2.mp4` | 53,165,455 | 1920 × 1080 | 30.000 | 7,800 | 260.0 s |
| `SPL#1_Heating_coldstart.mp4` | 683,165,477 | 1920 × 1080 | 23.976 | 98,413 | 4,104.6 s |

## User comments

- R4 and overall: "배속 재생 추가 필요 (*2/*3/*4/*0.5/유저 선택)".
- Overall: whether to add help for the `,` and `.` frame-step keys needs
  discussion.
- R5: the zero line does not move alone with the arrow keys. The Windows
  agent confirmed this is the designed behaviour (DESIGN.md §4: the arrow
  keys move the whole Glass).
