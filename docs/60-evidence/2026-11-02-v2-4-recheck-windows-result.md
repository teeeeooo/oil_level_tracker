# V2-4 re-check on the workstation — Windows result (2026-11-02)

**Verdict:** V2-4 closes. Every row of the
[re-check request](../40-operations/2026-10-30-v2-4-recheck-windows-request.md)'s
fixed criteria passes, R3 after the user's word on what was typed (below).
The changes after the [first run](2026-10-30-v2-4-judgment-report-windows-result.md)
work as the user asked: the level-only pencil, the right column, the memo
list, the header checked in the submit dialog, and the report's new
page 1.

- **Source run:** commit `b66f387` (`checked=95 mismatched=0`).
- **Who ran it:** the Windows agent ran §0–§4 and §6; the user worked the
  app and the browser (§5). Python 3.14.3.
- The O/X column came through as `0` (text recognition); the user's
  overall note, "전반적으로 요청한대로 이상 없이 구현 됨", confirms O.

## Against the fixed criteria

| ID | Condition | Result |
|---|---|---|
| S1 | `checked=95 mismatched=0` | **pass** |
| B | `files_src` = `files_backup` | **pass**: 49 and 49 |
| S2 | `242 passed, 4 skipped` | **pass** (21.01 s) |
| C | K1–K12, R1u–R4u all O | **pass** |
| T | no `Traceback` until the window closed | **pass**: stdout and stderr empty |
| R1 | `inspections=4 unreadable=0` | **pass** |
| R2 | SPL#4 1907: header `V24-모델` / `V24-시험3`; v1 and v2 as in §3; v3 `report_bytes` ≥ 1; v3 ACCUM `override=PASS reason_chars=13`, BASE `override=-` with `checked_at` after §3's `saved_at`; `edits none` | **pass**: v3 `report_bytes=102267`; BASE `checked_at=2026-11-02T00:46:55` after `2026-10-30T07:27:14` |
| R3 | SPL#1 1913: header `test_type="V24-68분"`; v1 as in §3; v2 `report_bytes` 1–5,000,000 (A7); `edits none` | **pass, the header by the user's word**: the header reads `test_type="V24-시험"`; the user typed that in R2u (user, 2026-11-02). The value typed in the submit dialog was saved, as in K10. v2 `report_bytes=379159` for 68 minutes |
| R4 | 1910 and `V2-3 확인` as in §3; all `sha256_check=same` | **pass**: identical lines |

**A transcription slip, not a change:** §3 gives 1907's ACCUM cache
`empty=39.9%` and §6 `empty=50.8%`. 520 samples cannot give 39.9 % (207
is 39.8 %, 208 is 40.0 %); 50.8 % is 264 of 520, the edits' `empty=264`,
and `cache_written=3.9` shows the cache file untouched. The 39.9 % is the
`V2-3 확인` line's (168 of 421), copied one line off.

## The user's notes

- R3u: the 68-minute report opened quickly.
- Overall: as asked, and the app's speed is fine.
- **Two new features**, both for the first version (user, 2026-11-02;
  Product SSOT §6):
  - the source video at full size in a window of its own, from a button
    on the editor's video;
  - copying a stretch of the Oil and Foam lines and pasting it, for tests
    that cycle the compressor on and off.

## Not seen on Windows yet

- from V2-1: a Recipe saved at a frame other than the first, a redirected
  Documents folder, and the wording of the resolution refusal.
