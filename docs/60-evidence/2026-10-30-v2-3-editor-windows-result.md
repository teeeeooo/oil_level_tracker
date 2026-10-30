# V2-3 editor on the workstation — Windows result (2026-10-30)

**Verdict:** the run is valid, and V2-3 does not close yet. Every row of the
[request](../40-operations/2026-10-30-v2-3-editor-windows-request.md)'s
fixed criteria passes except two:
- **R2 fails:** the SPL#1 edit inspection's saved edits hold no drawn Oil
  sample and no "cannot judge" stretch.
- **The console row fails:** a `ConnectionAbortedError` traceback appeared
  in the app's console while the video streamed. The Windows agent marked
  the row O because the line did not come at a window close, but the
  criterion is "no `Traceback` line in the §5 console". Fixed in `9bd9f9c`.

The time limits pass on the workstation with wide margins: A4 39.3 s
(limit 180), A5 2.8 / 8.9 ms (16 / 50), the exact frame 56 ms (100), and
1× playback in the `<video>`.

The failed rows and the user's notes go to
[a re-check](../40-operations/2026-10-30-v2-3-editor-recheck-windows-request.md)
of only what they touch.

- **Source run:** commit `3cbe46e` (`checked=86 mismatched=0`); the
  measurement confirmed `source=4f9cb83ac6d9 files=54` (relayed with `-`).
- **Who ran it:** the Windows agent ran §0–§4 and §7; the user worked the
  app (§6) and relayed the agent's Markdown with their own notes.

## Environment

| Item | Value |
|---|---|
| CPU | AMD Ryzen Threadripper PRO 7945WX, 12 cores, 24 logical |
| RAM / GPU / OS | 127.1 GB / NVIDIA RTX 4000 Ada (and a remote display adapter) / Windows 11 Enterprise |
| App venv | Python 3.14.3, pywebview 6.2.1, pythonnet 3.2.1, clr_loader 0.3.1, opencv-python-headless 4.14.0.94, NumPy 2.5.4, pytest 9.2.0 |
| Browser | WebView2 156.0.4314.50; the measurement in Edge 156.0.4314.50 with Playwright 1.64.1 |
| NumPy SIMD | AVX2, AVX512F, AVX512_SKX and AVX512_ICL all yes |
| Codecs Edge reports | H.264 `probably`, HEVC `probably` |

## Against the fixed criteria

| ID | Condition | Result |
|---|---|---|
| S1 | `checked=86 mismatched=0` | **pass** |
| S2 | `198 passed, 4 skipped` | **pass** (21.68 s) |
| M1 | `source=4f9cb83ac6d9 files=54` | **pass** |
| M2 | this workstation's CPU | **pass** |
| M3 | `샘플 8210개` | **pass** |
| A4 | analysis through the app's server ≤ 180 s | **pass**: 39.3 s |
| A5 | overall median ≤ 16 ms, max ≤ 50 ms | **pass**: 2.8 / 8.9 ms over 660 redraws |
| A6-s | exact frame median ≤ 100 ms | **pass**: 56 ms (95 % 95, max 104) |
| A6-p | `<video>`, ≥ 59.0 s, 0 waiting or stalled, ≤ 1 % dropped | **pass**: 59.6 s, 0, 0 of 1,552 |
| E | E1–E17 all O | **pass** (E11 is a note) |
| E14 | the close question; Cancel keeps the window; no question after saving | **pass**, see below |
| N | N1–N11 all O | **pass** |
| R1 | `unreadable=0`, inspections 3 + 1 | **pass**: 4 |
| R2 | the SPL#1 edit inspection's edits: compressor moved, Oil edited and drawn ≥ 1, Foam and reference drawn ≥ 1, `cannot_judge` ≥ 1, memos ≥ 1 | **fail**: Oil drawn 0 and `cannot_judge=0`; the rest holds (compressor 474.8 against 485.0, Oil edited 1,347, Foam drawn 75, reference drawn 700, one memo) |
| R3 | `V2-3 확인`: folder, name, range 0–210 s, ANALYSED, not partial, same SHA-256, `times` equal, Oil edited 0 in both Glasses | **pass**: 421 samples, `oil=421/0/0/26` and `421/0/0/168` |
| R4 | the other two V2-2 inspections `edits none`, same SHA-256 | **pass** |
| — | no `Traceback` line in the §5 console | **fail**: `ConnectionAbortedError: [WinError 10053]` from `api.py` `_send` → `wfile.write`, while the video streamed |

**E14:** the WinForms question read "저장하지 않은 편집이 있습니다. 저장하지
않고 닫을까요?" with 확인 and 취소. The user's note says "'취소' 누르면 창이
그대로 닫힘", which could read as the window closing. It is read as the
question box closing: E15 (Ctrl+S, then X again) ran in the same app
session, which needs the window to have stayed.

## R2: why the drawn Oil and the stretch are missing

Nothing in the code loses a drawn sample or a stretch on the way to the
file; the run's sequence most likely removed them, and the request did not
guard against it. Not proven: the re-check shows it.
- **Only two operations turn a drawn sample into something else:** Delete
  (empty, `EDITED`) and undo. A grab keeps `DRAWN`. The Foam and reference
  samples drawn in the same run were saved as `DRAWN`, and the save and
  load round trip, "cannot judge" included, is tested.
- **Delete emptied the Oil line only** (the 2026-10-29 rule), so a range
  over the E5 pencil stroke and the E6 point line made them empty Oil
  samples. E7 told the user to pick "몇 초", not a place away from the
  drawings.
- **The point lines that Delete "did not erase"** (the user's E7 note) were
  most likely drawn into the reference line: "그릴 선" was still 참조
  after E5, the reference line is dashed like a point line, and 700 drawn
  reference samples (350 s) is long for "한 구간" with the pencil.
- **"판단 불가 풀기" clears what the selected range covers.** The range
  stayed selected after U (the user's E7 note), so clearing without
  selecting a part again clears the whole stretch.

The user then decided (2026-10-30, Product SSOT §6): Delete empties the
line chosen in "그릴 선", and another tool lets the range go.

## The user's notes and what followed

| Note | Outcome |
|---|---|
| E3: typing the end of the view showed times before the start ("-"), with an empty graph and image; wants a way back to the whole view | **Fixed** (`8c9ea35`): the view stays inside the analysed range; "전체 보기" in the graph header. The axis showed `-0:02`… after a pan past the start, which a smoke check now reproduces |
| E4: the snap makes little difference | Noted: the edges in these pictures are weak. No change |
| E5: wants straight lines, meaning level or upright (Shift in Paint), from a switch because Shift pans | **Added** (`8c9ea35`, user's request): the pencil's "수평·수직" switch |
| E6: the point line bends to edges even with the snap off; asks for an opinion | **User's decision:** the point line follows the snap, along the edges with it on and straight with it off (`8c9ea35`) |
| E7: what Delete erases is unclear | **User's decision:** Delete empties the line chosen in "그릴 선"; the button names it (`8c9ea35`) |
| E7: "판단 불가 풀기" runs out of the panel | **Fixed** (`8c9ea35`): the range buttons wrap |
| E7: the range stays after picking another tool | **Fixed** (`8c9ea35`): another tool lets it go |
| N8: the list shows `V2-3 확인` twice | **Fixed** (`8c9ea35`): the folder line is left out when it repeats the name |

## Facts for later

- **A4 on the workstation:** 39.3 s through the app's server for SPL#1,
  against 60.6 s in V2-2 with another job running and 46.4 s for the
  adapter alone. The `uint8` median and the faster draft search are in.
- **The medians there:** the `uint8` partition took 0.47 ms a frame with
  four threads, against 1.16 ms for the `int16` sort (2.5×), the same
  ratio as on the slowest PC. `int32` sorting, channel first, is a little
  faster on this CPU (AVX-512) at 0.38 ms; the context pass differs by
  0.01–0.03 s per 120 s of video, so it is not worth a change.
- **Exact frames:** 56 ms at the median on the workstation against 230 ms
  on the slowest PC, about the 7.5× decoding ratio expected; the
  `<video>`'s seek is slower here too (219 ms).
- **N9 needed nothing:** the copy could be renamed with the app open, so
  no video session held the file.
- **N6:** 421 samples (two a second over 210 s).
- **A likely transcription slip:** `V2-3 확인`'s edits show
  `saved_at=2026-10-30T02:06:00`, before its `created_at` (03:00:51). The
  merge after the re-analysis saves at the analysis end, which reads
  `03:02:06`. No criterion reads it.
