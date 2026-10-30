# V2-3 editor re-check on the workstation — Windows result (2026-10-30)

**Verdict:** every row of the
[re-check request](../40-operations/2026-10-30-v2-3-editor-recheck-windows-request.md)'s
fixed criteria passes, so V2-3 closes. The two rows that failed in
[the first run](2026-10-30-v2-3-editor-windows-result.md) pass:
- **R2:** the SPL#1 edits now hold 141 drawn Oil samples, 8 edited Foam
  samples and two "cannot judge" stretches.
- **The console:** no traceback, though C1 played the video and clicked
  through it.

The user's C4 note found that an upright pencil stroke did not draw a
vertical line. It is fixed after the run (`ca7d3ee`) and not yet seen on
Windows.

- **Source run:** commit `8c9ea35` (`checked=86 mismatched=0`).
- **Who ran it:** the Windows agent ran §0–§4 and §6; the user worked the
  app (§5). Python 3.14.3.

## Against the fixed criteria

| ID | Condition | Result |
|---|---|---|
| S1 | `checked=86 mismatched=0` | **pass** |
| S2 | `201 passed, 4 skipped` | **pass** (20.93 s) |
| C | C1–C12 all O | **pass** |
| T | no `Traceback` line in the §4 console until the window closed | **pass**: nothing printed at all |
| R1 | `inspections=4 unreadable=0` | **pass** |
| R2 | `20261029-1913_SPL#1_Heating_coldstart`: `saved_at` later than §3's, compressor as in §3, Oil drawn ≥ 1, Foam edited ≥ 1, `cannot_judge` ≥ 1, memos as in §3 | **pass**: `saved_at=…04:17:51` against `…02:25:47`; `compressor=474.8` both times; `oil=6722/1347/141/7297`; `foam=8127/8/75/8135`; `cannot_judge=2`; `memos=1` |
| R3 | the other three inspections' `edits` lines as in §3, and all four `sha256_check=same` | **pass**: the two `edits none` lines and the `V2-3 확인` lines are identical |

**The counts agree with the steps:**
- **Oil:** 141 samples moved from draft to drawn and the empty count fell
  by 141, so the user drew where the draft was empty. Edited stayed at
  1,347.
- **Foam:** C7 deleted Foam where it had none. The 8 samples became
  `EDITED` and stayed empty (8,135 empty before and after); the Oil line
  there was untouched.
- **"Cannot judge":** C8 cleared part of a marked stretch, which split it
  into two stretches over 5 samples; the valid count leaves those out
  (`empty=7292` = 7,297 − 5).

## The user's notes

| Note | Outcome |
|---|---|
| C1: clicking the graph while playing pauses and moves there | As designed; no console output |
| C4: an upright stroke, dragged a little slanted, came out diagonal, not vertical | **Fixed** (`ca7d3ee`): an upright stroke moved only the pressed sample, which shows as a spike between its neighbours (or a dot where they are empty). It now joins the pressed height to the pointer's between the pressed sample and the next: as steep as the samples allow, 0.5 s wide |
| C7: tested where there was no Foam line | Allowed by the step; the counts above show the Delete reached Foam |
| Overall: what edge does the point line follow with the snap on, and why does the draft not follow it? | Answered to the user; see below |

**The point line and the draft follow the same edges.** Both use the edge
strength of the context image: the brightness step between the rows above
and below, blurred over 5 columns and full at a step of 24 levels
(`adapters/video/draft.py`).
- **The draft** takes one best path across the whole video. It then
  empties the stretches where that path's edge is weak: a mean below 0.25
  over 5 s, for at least 2 s.
- **The point line** takes the best path between the user's points and
  never empties it. Where the draft was left empty, the path still settles
  on the strongest step it can find, however faint: glare, the glass wall,
  noise.
- **The 8 px snap** (`lines.snap`) is separate. It settles a grab, a
  pencil press or a clicked point on the strongest step in its column.

The Windows agent's own answer said the draft does not follow these edges.
That was wrong, and it was corrected for the user.

## Not seen on Windows yet

- the upright stroke (`ca7d3ee`);
- from V2-1: a Recipe saved at a frame other than the first, a redirected
  Documents folder, and the wording of the resolution refusal.
