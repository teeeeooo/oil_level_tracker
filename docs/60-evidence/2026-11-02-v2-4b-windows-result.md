# V2-4b video window and copy and paste — Windows result (2026-11-02)

**Verdict:** V2-4b closes. Every row of the
[request](../40-operations/2026-11-02-v2-4b-windows-request.md)'s fixed
criteria passes. The full-size video window and copy and paste work as
the user asked; one finding remains for the window: playing at a higher
speed stutters in the big window (below).

- **Source run:** commit `f2d6850` (`checked=100 mismatched=0`), a new
  folder from the commit ZIP.
- **Who ran it:** the Windows agent ran §0–§4 and §6; the user worked the
  app (§5). Python 3.14.3.
- **Text recognition:** the O/X column came through as `0`; the user
  confirms O (2026-11-02). The row labels W1–W12 came through as M1–M12,
  and `[B]` as `[0]`.

## Against the fixed criteria

| ID | Condition | Result |
|---|---|---|
| S1 | `checked=100 mismatched=0` | **pass**; no `MISMATCH` line |
| B | `files_src` = `files_backup` | **pass**: 58 and 58 |
| S2 | `248 passed, 4 skipped` | **pass** (22.38 s) |
| C | W1–W12, P1–P9 all O | **pass** |
| T | no `Traceback` in either run | **pass**: stdout and stderr empty in both runs |
| R1 | `inspections=4 unreadable=0` | **pass** |
| R2 | `V2-3 확인`: `saved_at` later than §3; `compressor=20.2`; BASE drawn counts above §3 for Oil and Foam; BASE `checked=no`; ACCUM line unchanged | **pass**: `saved_at` `2026-11-02T03:05:01` after `2026-10-30T03:02:06`; BASE `oil=22/28/371/28` (drawn 0 → 371), `foam=38/0/383/38` (drawn 0 → 383); `checked=no`; the ACCUM line identical |
| R3 | 1907, 1910, 1913 identical to §3 (1910 `edits none`); all `sha256_check=same` | **pass** |
| R4 | `video-window.json` has integer `x`, `y`, `width`, `height`; width ≥ 960, height ≥ 600 | **pass**: `{"x": 1894, "y": -225, "width": 1936, "height": 1048}` |

`[place-before]` was `없음`, so the file in §6 is this run's. Its
negative `y` is a second monitor placed higher than the first; W11 and
W12 opened the window there again.

## The user's notes

- **W6 (speed):** the two windows stay in step, but **at a higher speed
  the big window's video stutters**; the editor's small video does not.
- **W8:** the big window's Oil line follows an edit with a small delay;
  not a problem in practice. (The editor sends the lines 300 ms after a
  change, by design.)
- **P1:** the user deleted part of the Oil line and drew one cycle.
- **P4:** where a copy overlaps the line, it joins smoothly. (A paste
  writes the copied heights, with no snap; the join is the line between
  neighbouring samples.)
- **Overall:** apart from the stutter, built as asked; copy and paste is
  useful for the on-off tests.

## The stutter, as diagnosed (not yet fixed)

The big window plays its own `<video>` and jumps (`currentTime = …`)
whenever it is more than `DRIFT_SEC = 0.25` s of video time from the
editor's (`video-window.js`, `follow`). That threshold does not grow with
the speed: at 4× it is about 60 ms of wall time, and a decoder drawing a
large frame at 4× falls that far behind easily. Each jump is a seek, which
decodes from the previous key frame in a long video, so the window keeps
seeking instead of playing. The editor's video never seeks while playing,
so it does not stutter. A fix would correct small drift by nudging
`playbackRate` and seek only on a large drift.

## Not seen on Windows yet

- two decoders at once on the slowest PC (V2-5);
- from V2-1: a Recipe saved at a frame other than the first, a redirected
  Documents folder, and the wording of the resolution refusal (V2-5).
