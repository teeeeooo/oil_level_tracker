# S6-B Additional Real-Video Sample Intake and Qualification Evidence

**Worker result:** `COMPLETE ON FEATURE HEAD — AWAITING FRESH AUDIT`
**Milestone:** `S6 — Real-video and Windows validation gate` remains `ACTIVE`
**Branch:** `feature/s6-additional-real-sample-qualification`
**Task-start main:** `ab61b68d5f9b0df5d40148cc661a370cd2be5214` (`docs: close S6-A sample qualification`)
**Scope:** macOS source-tree intake, deterministic Recipe and real CLI/result-bundle qualification
**Next gate:** `S6-B Additional Real-Video Sample Qualification Fresh Exact-Head Auditor`

This evidence records the actual bytes, sequential decode boundary, visual suitability, fixed-geometry analysis window and production CLI behavior for three local-only videos. The videos have no user-confirmed `.oiltruth`; this is execution and reviewability evidence, not detector physical-accuracy acceptance.

## Execution environment

- Host: macOS `26.5.2`, Apple arm64
- Python: repository `.venv`, `3.14.4`
- OpenCV: `4.14.0`
- Execution: `PYTHONPATH=src .venv/bin/python -m oil_tracker.cli analyze`
- Detector settings: exact `DetectorSettings()` production defaults
- Sampling: `2.0 FPS`
- Generated evidence root: `sample/output/s6-additional-real-samples/worker-ab61b68-20260731T022639Z/`
- Environment mutation: none; no install, dependency, source, threshold or packaging change

## Local input identity and sequential decode

| Video | Size / SHA-256 | OpenCV metadata | Sequential decode | Last usable frame / timestamp |
|---|---|---|---|---|
| `sample2.mp4` | `1,970,224 B`; `73c6586ac167b7c6267c5729c04f05399a3fadc09852d367c49762501285634f` | `h264`, `720×1280`, `30 FPS`, declared `288` frames / `9.6 s` | `286` usable frames, indices `0–285` | `285 / 9.500000 s`; usable end-exclusive `9.533333 s` |
| `sample3.mp4` | `10,001,682 B`; `c2a45b2b3aa025dea405bfecad79228547f80bf8e1a9e337a400cc09f29f3c04` | `h264`, `1280×720`, `29.9700299700 FPS`, declared `4,202` / `140.206733 s` | `4,199` usable frames, indices `0–4198` | `4198 / 140.073267 s`; usable end-exclusive `140.106633 s` |
| `sample4.mp4` | `16,224,936 B`; `ee971b3871d806ff194117eb64960cca3ad158e8ae3d1be4097ebc20fe472892` | `h264`, `1080×1234`, `30 FPS`, declared `1,684` / `56.133333 s` | `1,682` usable frames, indices `0–1681` | `1681 / 56.033333 s`; usable end-exclusive `56.066667 s` |

All three files remain ignored by `sample/*.mp4`. The lower sequential counts are bounded decode observations and are not labelled corruption or transmission damage.

### `sample3.mp4` tail nuance

Independent random seeks reproduced the reported boundary: frame `4198` decodes successfully, while `4199–4201` do not. Sequential decode also ends cleanly after frame `4198`. The production metadata still reports `4,202` frames, so the controlled analysis end must remain within the directly usable range. No transcode, repair or replacement was attempted.

## Visual intake and suitability

### sample2 — suitable with bounded steady window

The portrait handheld clip shows a compressor sight glass with a visible horizontal phase boundary and a strong fluorescent reflection crossing the glass. Frames `0`, `30` and `60` retain stable fixed geometry; later frames progressively zoom and reframe. The accepted qualification window is therefore `0.0–2.0 s`. The reflection remains inside the ellipse and is not hidden by an exclusion.

### sample3 — suitable with fill/drain window

After a Thermo King title and dark lead-in, the clip shows a compressor sight glass through low-level, filling/agitated, high-level and draining appearances. Blur, glare and camera movement are present. Frames around `900`, `1500` and `3000` keep a stable fixed ellipse; the accepted full window is `30.03–105.0 s`. A fresh `75.08–105.0 s` drain window was added to expose history-sensitive behavior. Intro, late reframing and outro remain intake evidence but are outside the Recipe geometry window.

### sample4 — suitable full usable window

The static portrait overview shows a small compressor sight glass below the compressor body. Hoses and yellow labels remain outside the ellipse. The phase appearance changes across the sequence while framing stays stable, so the accepted window is `0.0–56.0 s`.

All three are compressor sight-glass videos with reviewable phase evidence. Suitability means the fixed geometry and usable window support repeatable execution; it does not mean the visible phase or detector output has verified physical truth.

## Deterministic Recipes

| Recipe | Recipe / Glass ID | Geometry | SHA-256 |
|---|---|---|---|
| `sample/sample2.oilrecipe` | `da570374-9f2a-5b7d-8388-ce11a21a6af3` / `0aff9b80-002e-54e1-b1a3-fff1ec97a183` | center `(355,490)`, radii `(170,170)`, zero `490` | `061a190996318ecc2520644f21922ca82de24dc5accb91536f127bb3accaa458` |
| `sample/sample3.oilrecipe` | `090a3115-56a1-59a2-a043-7ecab8db0b7d` / `c21a62cd-e0e0-545c-8f7f-ee2384f036a9` | center `(835,315)`, radii `(120,120)`, zero `315` | `66a5ba8cc01933349e02e463b8155463610c658afbfc0893340c62197a715b43` |
| `sample/sample4.oilrecipe` | `cc5dd2c8-ddae-5888-bacc-ccbd940bdcd8` / `ecb6e1ec-0259-5982-a35f-7cb1f7075af2` | center `(595,850)`, radii `(52,52)`, zero `850` | `53688394709e7f0b15f637e991a48840e5f46333f30e67b9d9d7a3feead5b849` |

Every Recipe uses schema `1`, deterministic timestamp `2026-07-31T00:00:00+00:00`, `AUTO`, `mm_per_pixel=null`, margin `0.08`, no exclusions, default recovery judgment and exact production-default detector settings. Repository load/save round-trip equality and `DetectorSettings()` equality passed.

Analysis windows and compressor starts are CLI Session values, not persisted Recipe fields. No geometry, exclusion or setting was chosen from detector output.

## Production CLI results

| Run | Session window | Exit / lifecycle | Result | Samples | Events | Flagged rows | Raw/smoothed oil numeric | Raw/smoothed Foam numeric |
|---|---|---|---|---:|---:|---:|---:|---:|
| sample2 steady | `0.0–2.0 s`; start `0.0` | `0`; stages `1/6–6/6` | `REVIEW_REQUIRED` | 5 | 9 | 5 | `0 / 0` | `3 / 3` |
| sample3 full | `30.03–105.0 s`; start `30.03` | `0`; stages `1/6–6/6` | `REVIEW_REQUIRED` | 151 | 19 | 144 | `0 / 0` | `0 / 0` |
| sample3 drain fresh | `75.08–105.0 s`; start `75.08` | `0`; stages `1/6–6/6` | `REVIEW_REQUIRED` | 61 | 12 | 56 | `0 / 0` | `0 / 0` |
| sample4 full | `0.0–56.0 s`; start `0.0` | `0`; stages `1/6–6/6` | `FAIL` | 113 | 6 | 113 | `0 / 0` | `113 / 113` |

Exact commands follow this form:

```bash
PYTHONPATH=src .venv/bin/python -m oil_tracker.cli analyze \
  --recipe sample/<sample>.oilrecipe --video sample/<sample>.mp4 \
  --output <fresh-run-root> --start <start> --end <end> \
  --compressor-start <start> --sampling-fps 2.0
```

Diagnostic wall/RSS values were sample2 `10.27 s / 205,357,056 B`, sample3 full `48.64 s / 202,899,456 B`, sample3 fresh `22.09 s / 201,424,896 B`, and sample4 `31.56 s / 212,893,696 B`. They are short source-tree diagnostics, not official CPU, memory or long-duration acceptance.

## Recorded detector behavior

- sample2 produced three `UNKNOWN_REVIEW` and two `FULL_WITH_FOAM` rows. No numeric oil was published; Foam was published on three rows.
- sample3 full produced 144 `UNKNOWN_REVIEW` and seven `FULL_NO_INTERFACE` rows. The fresh drain run produced 56 `UNKNOWN_REVIEW` and five `FULL_NO_INTERFACE` rows. Neither run published numeric oil or Foam.
- sample4 classified all 113 rows as `FULL_WITH_FOAM`, published Foam on every row and ended with `JUDGMENT_FAIL`: “Stable recovery above zero was not detected.” No numeric oil was published.

These values are unverified detector outputs. In particular, sample4's continuous Foam classification and final `FAIL` are not claims that physical Foam exists or that the compressor failed an engineering test.

### sample3 full-history versus fresh drain

The two sampling grids differ by about one source frame over most of the overlap. Twenty-eight nearest pairs were within `0.033367 s`: all retained `null` oil and Foam publications; one pair differed between `FULL_NO_INTERFACE` and `UNKNOWN_REVIEW`, and four pairs differed in ambiguity-related flags. The single exact shared frame agreed in state, publications and flags. The differences are preserved as review-sensitive temporal/sampling behavior, not normalized away.

## Result-bundle integrity

Repository `ResultBundleReader` reopened all four bundles. For every bundle:

- manifest, tracking/events CSV, Recipe/session snapshot, review index, report and analysis log exist;
- all JSON and CSV files parse;
- all report-local references resolve inside the bundle;
- all graph and capture PNGs decode;
- no hidden temporary, `.tmp`, `.part` or staging artifact remains;
- the Recipe snapshot bytes exactly equal the tracked Recipe;
- the manifest Recipe hash equals the repository stable canonical Recipe hash;
- no video or output handle remains after process exit.

Validated asset counts were sample2 `11` PNGs, sample3 full `21`, sample3 fresh `14`, and sample4 `8`. The ignored machine-readable inspection summary is stored at `qualification-summary.json` under the evidence root.

## Truth and acceptance limitations

No `.oiltruth` accompanies sample2, sample3 or sample4. Therefore:

- no MAE, normalized error, precision, recall or false-positive/negative truth is reported;
- numeric `null` remains `null` and is not converted into a presumed level;
- `REVIEW_REQUIRED` remains a valid engineering outcome;
- sample4 `FAIL` remains a judgment result, not detector-accuracy truth;
- macOS source-tree runs do not establish Windows, GUI/DPI, packaging, relocation or clean-PC acceptance;
- these clips do not establish official long-duration CPU or memory stability.

## Final classification and next gate

All three intake decisions are complete. Each video is suitable only within its documented fixed-geometry window, and every required CLI run finalized a readable bundle without a source/runtime blocker. S6 remains `ACTIVE`; S7 remains `PLANNED` and has not started.

The next owner is the `S6-B Additional Real-Video Sample Qualification Fresh Exact-Head Auditor`. That Auditor must inspect the complete PR and adjacent Recipe/video/bundle owners, independently verify the final exact head and focused evidence, and only after `AUDIT: PASS` may own guarded merge, checkout synchronization and bounded post-merge Close.

## Intentional non-runs

This Worker did not run or claim detector tuning, user-truth accuracy, Windows GUI/DPI or canonical validation, official long-duration stability, PyInstaller, relocated/clean-PC execution, Unicode/long-path or Windows file-lock/cancellation acceptance, merge, PR Ready transition, audit approval, S6 Close or S7 start.
