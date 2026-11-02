# V2-5 acceptance on the workstation — Windows result (2026-11-02)

**Verdict:** every workstation row of the
[request](../40-operations/2026-11-02-v2-5-acceptance-windows-request.md)'s
fixed criteria passes on the one-folder build of `daf381a`. A4–A6 were
measured in the build's own window (WebView2). Two rows pass on the
identifying values rather than the literal wording (A1's inspection name,
R's pre-run list; below). V2-5 stays open for the slowest-PC part (§10)
and the user's notes.

- **Source run:** commit `daf381a` (`checked=108 mismatched=0`), a new
  folder from the commit ZIP, after two attempts whose §5 could not reach
  the window (`7dc38e7`, `5bb9025`; backups `C:\olt-v25-backup`,
  `C:\olt-v25b-backup`; no change to the data folder).
- **Who ran it:** the Windows agent ran §0–§7 and §9; the user worked the
  build (§8). **§5 ran over Remote Desktop** (GPU line: Microsoft Remote
  Display Adapter). Python 3.14.3, PyInstaller 6.21.0, WebView2
  156.0.4314.58.
- **Text recognition:** the O/X column came through as `0` (O, as in the
  last two runs); `[B]` came through as `[0]`.

## Against the fixed criteria

| ID | Condition | Result |
|---|---|---|
| S1 | `checked=108 mismatched=0` | **pass** |
| B | `files_src` = `files_backup` | **pass**: 60 and 60 (`C:\olt-v25c-backup`) |
| S2 | `261 passed, 4 skipped` | **pass** (25.57 s) |
| A8-b | `package=PASS`, ≤ 200 MB, nothing changed, four pages 200 | **pass**: 121 files, **159.6 MB**, `package_files_changed=0`, the built app started in 1.1 s |
| A4 | analysis in the build ≤ 180.0 s, 8,210 samples | **pass: 36.0 s** |
| A5 | whole median ≤ 16 ms, max ≤ 50 ms | **pass: 2.8 / 7.4 ms** (660 redraws) |
| A6 | exact frame median ≤ 100 ms; 1× `<video>` ≥ 59.0 s of 60, 0 waiting, ≤ 1 % dropped; U14 | **pass**: 50 ms (max 92); 59.6 s, 0, 0 of 1,550; U14 O |
| M | the built `OilLevelTracker.exe`, `오류: 없음` | **pass**, in **`WebView2 (앱 창)`**; window to the list 3.2 s |
| A1 | U1–U17 O; `V25 SPL#4 인수` (2 Glasses) and `V25 SPL#1 인수` (1 Glass), each with `version v=1` | **pass, on the identifying values**: `V25 SPL#4 인수` as asked. The SPL#1 inspection carries no name (`20261102-1521_SPL#1_Heating_coldstart`, `name=""`); it is this run's — Recipe `V25 SPL#1`, created `2026-11-02T06:21:28`, header `V25-모델` / `V25-시험`, `version v=1` |
| A2 | U8, U16 | **pass** |
| A3 | S2; each `version glass` `verdict` = `computed`, or an override with a reason; U9 | **pass**: all five lines `PASS` = `PASS`, no override |
| A7 | three new reports ≤ 5,000,000 bytes; U11, U17; two PDFs | **pass**: 109,365, 109,368 and 398,309 (68 min); PDFs 214,196 and 169,956 bytes |
| A9 | U7, U12, U18, U19; v1 and v2 with v2 `test_type="V25-시험2"`; +1 byte, then 53,165,455; `V2-3 확인` `same` | **pass** |
| V1 | `V25 SPL#4`: 1920x1080, `glasses=2 problems=0`, `t` > 0; `V25 SPL#1`: `glasses=1 problems=0`, `t` > 0; U2 | **pass**: `t=59.967` and `t=600.183`; reopened at its frame |
| V2 | U4 and the wording recorded | **pass**; wording below, for the user |
| R | the four earlier inspections and two Recipes unchanged; all `sha256_check=same` | **pass, against the V2-4b result**: see below |
| T | no `Traceback` since the run's start; `(build)` | **pass**: four `start:` lines, all `(build)` |
| W | U15 | **pass**: the big window at 4× "이상 없음" |

**R, and when §6 was taken.** The §6 lists already hold the two new
inspections and the two new Recipes, word for word as in §9, so they were
taken after §8, not before. The earlier state is fixed otherwise: §1's
backup counted 60 files, the V2-4b run's 58 inspection files plus the two
Recipe files, so nothing of this run existed then; and in §9 the four
earlier inspections read exactly as at the end of the
[V2-4b run](2026-11-02-v2-4b-windows-result.md) (1907 with v1–v3, 1910
and 1913 untouched, `V2-3 확인` with its saved copy-and-paste edits), all
with `sha256_check=same`. The two earlier Recipes match their inspections'
Glasses and keep `t=0.000`.

**The log, matched to the run:** 14:52:28 the build check (no window,
so no `window:` line); 14:53:03 the measurement's app (page loaded 2.5 s,
then 38.7 s, the reload after its 36 s analysis); 14:56:55 §8's start
(1.7 s); 15:10:57 the restart in U7 (2.4 s).

**Over Remote Desktop:** the frame intervals during the drags are about
31 ms (about 32 Hz, the remote display's rate), not the screen's; A5
judges the redraw time, which does not depend on it. Playback dropped no
frame.

## The resolution refusal (V2)

The app said "영상 해상도 1280×720가 이 Recipe의 1920×1080와 다릅니다."
(the relay shows `x`; the code writes `×`). Read aloud, 720 (칠백이십)
and 1080 (천팔십) end in a consonant, so the particles should be 이 and
과. A wording without the problem: "영상 해상도(1280×720)가 이 Recipe의
해상도(1920×1080)와 다릅니다." The user's call.

## The user's notes (2026-11-02)

1. **Selecting a line to delete it:** a click selects the whole connected
   line; the range delete removes both Oil and Foam, but the user may
   want only one; the reference line cannot be deleted at all today. Line
   selection and delete should work for Oil, Foam and the reference.
2. **Drawing FULL and EMPTY is fiddly** with the point line or the
   pencil: the top or bottom edge is often missed by 1–2 px. An easy way
   to draw FULL and EMPTY is wanted.
3. **A state to click without changing anything:** every tool changes
   something on a click (grab and pencil draw, range selects, pan moves
   the view). A "select" tool, or no tool, is wanted, to look at a point
   of the video or see how a line runs.

## Still open in V2-5

- the slowest PC (§10): A8's run with only the WebView2 runtime; its
  result follows;
- the user's word on the refusal wording and on the three notes (whether
  they go in the first version).
