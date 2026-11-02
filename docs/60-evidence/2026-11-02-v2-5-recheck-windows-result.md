# V2-5 re-check on the workstation — Windows result (2026-11-02)

**Verdict:** every row of the
[re-check request](../40-operations/2026-11-02-v2-5-recheck-windows-request.md)'s
fixed criteria passes on the one-folder build of `8448e79`. The select
tool, deleting a picked line, FULL/EMPTY made easy and the new refusal
wording work as the user decided, and A4–A6 hold in the new build's
window. With the [workstation run](2026-11-02-v2-5-acceptance-workstation-windows-result.md)
and the [slowest PC](2026-11-02-v2-5-acceptance-slowest-pc-windows-result.md),
**V2-5 closes and the first version is accepted.**

- **Source run:** commit `8448e79` (`checked=108 mismatched=0`), a new
  folder from the commit ZIP. Python 3.14.3; WebView2 156.0.4314.58.
- **Who ran it:** the Windows agent ran §0–§6 and §9; the user created
  the inspection and worked the build (§7–§8). §4 ran over Remote Desktop.
- **Text recognition:** the O/X column came through as `0` (O, as in the
  earlier runs); `[B]` as `[0]`; the relay writes `x` for the code's `×`.
  A stray PowerShell prompt line in §9 is not output.

## Against the fixed criteria

| ID | Condition | Result |
|---|---|---|
| S1 | `checked=108 mismatched=0` | **pass** |
| B | the two counts equal | **pass**: 93 and 93 (`C:\olt-v25d-backup`) |
| S2 | `261 passed, 4 skipped` | **pass** (23.89 s) |
| A8-b | `package=PASS`, ≤ 200 MB, nothing changed | **pass**: 121 files, 159.6 MB, started in 1.1 s |
| A4–A6 | in `WebView2 (앱 창)`; ≤ 180.0 s with 8,210 samples; A5 ≤ 16 / ≤ 50 ms; exact frame ≤ 100 ms; 1× `<video>` ≥ 59.0 s, 0 waiting, ≤ 1 % dropped; no error | **pass**: 35.5 s; **2.2 / 9.3 ms**; 50 ms (max 93); 59.8 s, 0, 0 of 1,504; `오류: 없음`; window to the list 3.2 s |
| C | N1–N13 all O | **pass**; N13 reads "영상 해상도(1280×720)가 이 Recipe의 해상도(1920×1080)와 다릅니다." |
| R | `V25b 선택 확인` saved, no version; the other six as in §5; all seven `same` | **pass** |
| T | no `Traceback`; `(build)` | **pass**: three `start:` lines (the build check, the measurement, §6), all `(build)` |

**The new inspection matches the steps:** after the undos the BASE Oil
line is the draft again (`oil=520/0/0/4`), the Foam drawn in the session
remains (64 drawn samples), the reference shows 54 edited samples (drawn
in N7, then deleted), and both Glasses are checked (N12, the "제출"
dialog opened and cancelled). Nothing was submitted.

**Measured page size:** 1424 × 861, the app window not maximized this
time (1920 × 1009 in the first run); A5 passes either way.

## The user's note

"없음, 모두 OK" — nothing further.
