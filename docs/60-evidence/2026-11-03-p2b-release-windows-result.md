# P-2b release 2.0.0 — Windows result (2026-11-03)

**Verdict:** every row of the
[release request](../40-operations/2026-11-03-p2b-release-windows-request.md)'s
fixed criteria that came back passes on the build of `008c13f`, except R.
**R is not shown:** the inspection listings before and after were not
relayed, so R waited on a read-only follow-up (below).

**Later:** the follow-up ran in the
[re-check](2026-11-03-p2b-release-recheck-windows-result.md), and R
passes.

What the run shows:
- the workstation built `OilLevelTracker-2.0.0.zip`, with the exe's version
  and the ZIP's two top entries as intended;
- the app unzipped from it shows the version in the help and on a new
  report;
- **the manual opens in Edge** from the build on both PCs, the check P-2
  left to this run;
- on the slowest PC, the user installed the same ZIP with only the
  install guide, no help needed, and the inspection made by the old build
  opened in 2.0.0.

- **Source run:** commit `008c13f` (`checked=154 mismatched=0`), a new
  folder from the commit ZIP (`C:\olt-p2b\src\…`). Python 3.14.3.
- **Who ran it:**
  - the workstation's agent ran A-0 to A-6 and A-8;
  - the user checked W1–W6 on the workstation and all of B on the
    slowest PC.
- **Text recognition and relay:**
  - W1–W6 came back labelled `M1`–`M6`;
  - several `=` came through as `-` (`files_src-101`);
  - the "최저 사양 PC" block repeats the workstation's A-section lines
    word for word (the same `C:\olt-p2b\src\…` paths, times and counts).
    The slowest PC has no agent and ran none of them, so they are taken as
    a copy. Only B-1, L1–L6, B-6 and the note are the slowest PC's;
  - the A-5 and A-8 listings stayed in the agent's spill files, with only
    `inspections=7 unreadable=0` relayed;
  - the user's folder name in paths is written `<사용자>` here.

## Against the fixed criteria

| ID | Condition | Result |
|---|---|---|
| S1 | `checked=154 mismatched=0` | **pass** |
| B | the two counts equal | **pass**: 101 and 101 (`C:\olt-p2b-backup`) |
| S2 | `271 passed, 4 skipped` | **pass** (23.70 s) |
| P | `version=2.0.0`, `package=PASS`, ≤ 200 MB, nothing changed, a `zip=` line | **pass**: 162 files, 161.6 MB, started in 1.1 s; ZIP 66,439,236 bytes, SHA-256 `920dfbef…71407` |
| Z | the exe's product and versions; `top_count=2 guide_name_ok=True app_folder_ok=True`; entries = files + 1; two items unzipped | **pass**: `product=Oil Level Tracker product_version=2.0.0 file_version=2.0.0`; 163 = 162 + 1; 2 |
| W | W1–W5 all O; product version "2.0.0" | **pass**: the Korean name and the styled guide, its manual link (W1); "버전 2.0.0" (W2); the manual in Edge with figures and clips (W3); v1 submitted, page 1 reads "V25b 선택 확인 · Oil Level Tracker 2.0.0" (W4); Properties show 2.0.0 for both versions (W5) |
| R | `V25b 선택 확인` has `version v=1`; the other lines as in A-5; all `same` | **not shown** here: only `inspections=7 unreadable=0` before and after came back. W4 shows the submission. **Passed** by the re-check's follow-up |
| T | no `Traceback`; this run's `start:` lines `start: 2.0.0 (build)` | **pass**: two lines, 15:22:16 (the build check) and 15:23:12 (A-6), then `window: page loaded 3.4 s after start` |
| L | L1–L6 all O | **pass**: the hash equals A-3's (L1); the Korean name in the ZIP and the folder, the styled guide (L2); installed with the guide alone, nothing unclear, no "Windows의 PC 보호" window (L3); the old build's submitted SPL#1 inspection, its v1 and report open (L4); "버전 2.0.0" and the manual in Edge (L5); the desktop shortcut (L6) |
| LT | no `Traceback`; the last `start:` line `start: 2.0.0 (build)` | **pass**: 16:06:51 and 16:09:34 on 11-03, after the two `2.0.0.dev0` lines of the V2-5 build |

## Deviations

- **Not through the shared folder.** The ZIP went to the workstation's
  `C:\0.Coding\0.Release\`, and the user carried it to the slowest PC
  (B-1). So copying from the shared folder was not exercised. L1's hash
  shows the copy arrived intact.
- **No SmartScreen window** (L3). A file copied from the workstation
  carries no download mark. A ZIP downloaded through a browser or a
  messenger may still show it; the guide covers that case.
- The install location on the slowest PC was not recorded.
- **A source video was elsewhere for part of the run.** The user reported
  it afterwards in the conversation. The app could not find a source video
  because the user had put the sample video in another folder. Once it was
  moved back, the check passed.
  - This exercised the source warning and "다시 확인" in 2.0.0.
  - A listing taken while the video was away shows its inspections as
    `sha256_check=video_missing`. R's follow-up allows for that.

## R's follow-up (read-only, the workstation's agent)

The first file's name was `3b83a138…`. The `3b03a138…` below is a slip in
the relay; the re-check's agent used the real file.

The two spill files hold A-5 and A-8. Run this, then relay every line of
its output verbatim:

```powershell
$dir = Join-Path $env:USERPROFILE '.cline-sr\data\sr\tool-result-spills\1793686553645_i7t1d'
$before = Get-Content -LiteralPath (Join-Path $dir 'run_commands-call_3b03a138fe34411997f1460c-1-result-fc0a1e46-0161-419a-bb5f-1df14929700c.txt')
$after = Get-Content -LiteralPath (Join-Path $dir 'run_commands-call_a47d0d48c589468e82b4c205-0-result-a8d9cbdf-4d46-42c8-acce-65b365322ad1.txt')
Compare-Object $before $after | ForEach-Object { "$($_.SideIndicator) $($_.InputObject)" }
"checks_after=$(($after | Select-String 'sha256_check=').Count) same_after=$(($after | Select-String 'sha256_check=same').Count)"
```

**R passes when:**
- every differing line either belongs to `V25b 선택 확인` or only turns
  `sha256_check=video_missing` into `sha256_check=same` (the moved video);
- the `=>` side has `V25b 선택 확인`'s `version v=1` line;
- the last line is `checks_after=7 same_after=7`.

## The user's note

The editor's F1 help is too long and wordy. The manual has the details,
so the help should be condensed. This is a request for the app, not a
failed row.

**What followed:**
- The user put it into 2.0.0: every key and mouse action, each in a few
  words (`11e4745`).
- This ZIP (`920dfbef…`) is therefore not the one to distribute.
- The [re-check](../40-operations/2026-11-03-p2b-release-recheck-windows-request.md)
  rebuilds it and carries R's follow-up.
