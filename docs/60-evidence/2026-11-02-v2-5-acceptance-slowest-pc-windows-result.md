# V2-5 acceptance on the slowest PC — Windows result (2026-11-02)

**Verdict:** A8's run part passes: the workstation's build, moved as a
ZIP and run with nothing built there, opened and carried an inspection
from analysis to a submitted report. **L-zip is open:** the result does
not carry the ZIP's SHA-256 line (§10's first command), so that the
package run is the workstation's (`zip_sha256=e1a4464b…a109d`) rests on
the user's word until the line comes.

- **Request:** [§10](../40-operations/2026-11-02-v2-5-acceptance-windows-request.md),
  the ZIP of the `daf381a` build made on the workstation
  ([workstation result](2026-11-02-v2-5-acceptance-workstation-windows-result.md)).
- **Who ran it:** the user alone (no agent on that PC). The log names
  Windows 11 build 26100.

## Against the fixed criteria

| ID | Condition | Result |
|---|---|---|
| L-zip | §10's SHA-256 equals §4's `zip_sha256` | **open**: the line is not in the result |
| A8-r | L1–L7 all O | **pass**: the app opened from the moved folder, analysed, edited, submitted and opened its report |
| L-T | no `Traceback`; `(build)` | **pass**: one `start:` line, `(build)`, and `window: page loaded 6.6 s after start` |

## For reference (Product SSOT §2: not acceptance limits on this PC)

| What | Value |
|---|---|
| L1, double-click to the inspection list (stopwatch) | about 9.8 s; the log counts 6.6 s from the app's own start (the build's unpacking and Python's start come before) |
| L3, analysing SPL#1 (68 min, stopwatch) | **156.0 s**, under the workstation's 180 s limit even here (163.0 s through the source's server on 2026-10-30) |
| L4, dragging and drawing | no delay |
| L5, playback | the editor's video smooth; the big window at 4× takes 0.1–0.2 s to start after Space, then plays without a break |

## The user's note on the header (L6)

The user found no field for the report header (압축기 모델, 시험 종류)
in the editor once the inspection had started, having left it empty in
the setup. Since V2-4b the editor's right column has no 검사 정보
section (the order the user set: 원본 영상, 편집, 판정, Glass, 분석); the
header is entered in the analysis setup and **checked and edited in the
"제출" dialog**. The request's L6 and U10 wrongly said "검사 정보에"
(carried over from the V2-4 request), which pointed at a section that is
no longer there. The submission went through and the report opened.
