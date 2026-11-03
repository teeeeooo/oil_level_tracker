# P-2b re-check: release 2.0.0 with the condensed help — Windows result (2026-11-03)

**Verdict:** every row of the
[re-check request](../40-operations/2026-11-03-p2b-release-recheck-windows-request.md)'s
fixed criteria passes on the build of `11e4745`.

- R's follow-up settles the row the
  [first run](2026-11-03-p2b-release-windows-result.md) left open.
- The rebuilt 2.0.0 shows the condensed editor help, and the user finds
  it short enough.
- Its ZIP replaced the first one in the workstation's release folder.

**Release 2.0.0 is accepted:** `OilLevelTracker-2.0.0.zip`, SHA-256
`f1580ddaab88379cf80ea4a73ca00b3c6bd5150815d36061c62f470bc1069e67`.

- **Source run:** commit `11e4745` (`checked=154 mismatched=0`), a new
  folder from the commit ZIP (`C:\olt-p2b\src-recheck\…`). Python 3.14.3.
- **Who ran it:**
  - the workstation's agent ran §0–§6 and §8;
  - the user checked H1–H3. The slowest PC was not needed.
- **Text recognition and relay:**
  - H1–H3 came back labelled `M1`–`M3`, and `=>` as `->`;
  - several `=` came through as `-`.
- **Corrections the agent made:**
  - §0's first file name was `3b83a138…`. The request copied `3b03a138…`
    from the first result's relay, a transcription slip, and the agent
    used the real file;
  - the diff also held two lines of a terminal prompt (`push.exe`)
    appended to the spill file. They are noise, not listing data, as the
    stray prompt line in the V2-5 re-check was.

## Against the fixed criteria

| ID | Condition | Result |
|---|---|---|
| R | only `V25b 선택 확인`'s lines or `video_missing` → `same` differ; its `version v=1`; `checks_after=7 same_after=7` | **pass**: see below |
| S1 | `checked=154 mismatched=0` | **pass** |
| S2 | `271 passed, 4 skipped` | **pass** (24.30 s) |
| P | `version=2.0.0`, `package=PASS`, ≤ 200 MB, nothing changed, a `zip=` line | **pass**: 162 files, 161.6 MB, started in 1.1 s; `index.html` 38,570 bytes (43,443 before the help was condensed); ZIP 66,437,128 bytes |
| Z | the exe's product and versions; two top entries; entries = files + 1; two items unzipped | **pass**: `product=Oil Level Tracker product_version=2.0.0 file_version=2.0.0`; `top_count=2 guide_name_ok=True app_folder_ok=True`; 163 = 162 + 1; 2 |
| H | H1–H2 O; H3's hash equals §4's | **pass**: the condensed help in the build, "이 정도면 충분함" (H1); the manual in Edge (H2); `f1580dda…` in `C:\0.Coding\0.Release\` (H3) |
| T | no `Traceback`; `start: 2.0.0 (build)` | **pass**: 16:51:47 (the build check) and 16:52:46 (§6), then `window: page loaded 2.7 s after start` |

**R in detail** (the first run's listings before A-7 and after it):
- **Six `analysis` lines** turn `sha256_check=video_missing` into `same`.
  They belong to the inspections of the two field videos: SPL#4, 520
  times, `9f494a6fd0a0`; SPL#1, 8,210 times, `fb03d7428c17`. The user had
  moved those videos and put them back during the run.
- **`V25b 선택 확인`'s block** changes as the submission should:
  - before: `edits saved_at=2026-11-02T08:04:03`, BASE `oil=520/0/0/4`,
    ACCUM, both checked. This is the state the V2-5 re-check left;
  - after: `version v=1 submitted_at=2026-11-03T07:00:42` with
    `report_bytes=109355`, BASE `PASS` and ACCUM `FAIL` as computed, no
    override, then `edits none`.
- No other line differs, and all seven inspections read `same` after.

## Release 2.0.0

- **The ZIP to distribute:** the one above, in `C:\0.Coding\0.Release\`.
  The first run's ZIP (`920dfbef…`) was overwritten there.
- **The slowest PC** still holds the first run's 2.0.0. The only
  difference is the longer editor help. It is a test PC; replacing its
  copy is optional.
- **The tag:** `v2.0.0` marks `11e4745`.
