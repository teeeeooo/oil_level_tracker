# V2-3 editor on the slowest PC (A5, A6) — Windows result (2026-10-30)

**Verdict:** the run is valid. On a PC of the slowest class, with SPL#1:
- **A5 passes** with a wide margin: the lines redraw while dragging takes
  5.9 ms at the median and 23.9 ms at most (limits 16 / 50 ms).
- **1× playback passes** (A6-p) in the `<video>`: Edge plays SPL#1's H.264.
- **The exact frame fails** (A6-s): 230 ms at the median against 100 ms,
  and the `<video>`'s own seek is slower still (352 ms). By the fixed
  criteria, making the frame reading faster comes first.
- **The cheaper median passes** (A4-m2): the `uint8` partition went into
  the app (`908f624`).

- **Request:** [2026-10-29-v2-3-editor-slowest-pc-windows-request.md](../40-operations/2026-10-29-v2-3-editor-slowest-pc-windows-request.md).
  Its criteria were fixed before the run.
- **Source run:** commit `8a96b22`, confirmed by
  `source=1da92bcf0279 files=54`.
- **Who ran it:** the user, in a terminal on the slowest PC (no coding
  agent there), at 08:39 on that PC's clock. They relayed the script's
  Markdown result as text; the notes the request asked for (monitor, the
  Edge window's visibility, other programs) were not relayed.

## Environment

| Item | Value |
|---|---|
| CPU | Intel Xeon E5-1620 v3 @ 3.50 GHz, 4 cores, 8 logical |
| RAM / GPU / OS | 15.9 GB / NVIDIA Quadro K620 / Windows 11 Enterprise |
| Software | Python 3.15.2, OpenCV 4.14.0.94 (headless), NumPy 2.5.4, Playwright 1.64.1, Edge 156.0.4314.50 |
| NumPy SIMD | AVX2 yes; AVX512F, AVX512_SKX and AVX512_ICL no |
| Video | `SPL#1_Heating_coldstart.mp4`, 683,165,477 bytes, 1920 × 1080, 23.976 fps, 98,413 frames, `h264` |
| Key frames | 394, every 250 frames exactly (10.4 s) |
| Recipe, window | `SPL#1_test1_607bccb`, one Glass; 1920 × 1040 |
| Codecs Edge reports | H.264 `probably`, HEVC `no` |

## Results

**Analysis through the app's server** (no window): **163.0 s**, 8,210
samples.

**A5, lines redraw while dragging (ms):**

| Scene | Count | Median | 95 % | Max | Frame interval median | 95 % | Max |
|---|---|---|---|---|---|---|---|
| Pencil, whole view (three lines end to end) | 180 | 7.6 | 11.9 | 13.0 | 16.7 | 16.8 | 83.2 |
| Grab-and-drag, whole view | 241 | 5.9 | 14.7 | 23.9 | 16.7 | 16.8 | 33.5 |
| Grab-and-drag, 10× zoom | 240 | 4.8 | 8.5 | 17.4 | 16.7 | 16.8 | 33.3 |
| **All** | 661 | **5.9** | 12.0 | **23.9** | | | |

The counts add up (180 + 241 + 240 = 661) and the overall maximum is the
largest scene maximum.

**A6, exact frames (ms):**

| Way | Count | Median | 95 % | Max |
|---|---|---|---|---|
| Exact frame (server) | 40 | **230** | 403 | 413 |
| For reference: the `<video>`'s seek | 20 | 352 | 551 | 704 |

**A6, 1× playback:** the `<video>`, 60.0 s of wall time, **59.4 s**
advanced, **0** waiting or stalled events, 0 of 1,546 frames dropped.

**A4, the row medians:** every way gave the app's values (`기준` or `같음`).

| Way | 1 thread, ms/frame | Ratio | 4 threads, ms/frame | Ratio |
|---|---|---|---|---|
| `int16` sort (the app's, before) | 7.19 | 1.00 | 2.34 | 1.00 |
| `int32` sort, channel first | 2.35 | 3.06 | 1.01 | 2.32 |
| `int16` partition | 2.70 | 2.67 | 1.04 | 2.26 |
| **`uint8` partition** | 2.63 | 2.73 | 0.95 | **2.46** |
| 8-bit counting | 8.20 | 0.88 | 3.59 | 0.65 |

The table keeps the app's way, the two fastest and the slowest; the
relayed result has eleven rows.

| Context pass, 1231.4–1351.4 s | Run 1 | Run 2 | `grab` | `retrieve` | `reduce` | `wait` |
|---|---|---|---|---|---|---|
| `int16` sort (before) | 4.71 | 4.39 | 3.00 | 1.25 | 2.61 | 0.01 |
| `uint8` partition | 4.22 | 4.22 | 2.83 | 1.24 | 1.03 | 0.01 |
| `int32` sort, channel first | 4.27 | 4.22 | 2.86 | 1.23 | 1.11 | 0.01 |

No error was reported (`오류: 없음`).

## Against the fixed criteria

| ID | Condition | Result |
|---|---|---|
| M1 | `source=1da92bcf0279 files=54` | **pass** (relayed as `source-1da92bcf0279`; the script prints `=`, a transcription slip) |
| M2 | Xeon E5-1620 v3 or a similar 4-core CPU | **pass** |
| M3 | `샘플 8210개` | **pass** |
| A5 | overall median ≤ 16 ms and maximum ≤ 50 ms | **pass**: 5.9 / 23.9 ms |
| A5-f | each scene's frame-interval median ≤ 20 ms | **pass**: 16.7 ms in all three |
| A6-s | exact frame median ≤ 100 ms | **fail**: 230 ms, and the `<video>` seek is 352 ms, so both miss: **make the frame reading faster first** |
| A6-p | `<video>`, ≥ 59.0 s advanced, 0 waiting or stalled, ≤ 1 % dropped | **pass**: 59.4 s, 0, 0 % |
| A6-c | the way is `frames (대체)` | not reached: the `<video>` plays SPL#1 |
| A4-m1 | every output `기준` or `같음` | **pass** |
| A4-m2 | the fastest identical way ≥ 1.5 with threads, and its pass no longer | **pass**: the `uint8` partition, 2.46; 8.44 s against 9.10 s. **It went into the app** |
| — | the context pass's difference | 0.33 s less per run over 120 s of video, so about **11 s less** over SPL#1's 68 min (an estimate) |
| — | the analysis through the app's server | 163.0 s against 169.7 s for the adapter alone in V2-2 (see below) |
| — | `오류: 없음` | **pass** |

## Facts for V2-3 and V2-5

- **Drawing is not the bottleneck on that PC.** Even with all three lines
  drawn end to end over 8,210 samples, the redraw stayed under a frame
  (16.7 ms) at the 95th percentile in every scene. The only frame
  intervals above 33 ms are the maxima (83.2 ms once while drawing with the
  pencil), not the medians. Nothing needs to get lighter before the point
  line.
- **An exact frame costs about the distance to the previous key frame.**
  SPL#1 has a key frame every 250 frames. OpenCV seeks to the key frame
  before the target and decodes forward, so a random time decodes 125
  frames on average and up to 250: the median (230 ms) and the maximum
  (413 ms) match 1.6–1.8 ms per decoded frame. On macOS three local
  samples took 39–54 ms at the median for the same seek and read, nearly
  all of it in the seek. Only stepping forward up to 15 frames reads on
  without seeking.
- **The `<video>` does not help.** Its seek (352 ms at the median) is
  slower than the server's exact frame, so showing the paused picture
  from it does not reach 100 ms either.
- **What the app adds to the analysis is small.** The adapter alone took
  169.7 s in V2-2; the faster draft search (`ae4873c`) was expected to save
  about 7 s there, which leaves about 163 s, the same as the 163.0 s
  measured through the app's server. The 60.6 s against 46.4 s on the
  workstation in V2-2 was the other job, as the user traced. The window
  (pywebview) is still to be timed in V2-5.
- **A4 margin:** 163.0 s leaves 17 s of the 180 s limit; the `uint8`
  partition should add about 11 s more, still to be confirmed in a run.
- **Playback counted more frames than the video has** for 60 s (1,546
  against about 1,424 at 23.976 fps). Chromium's `totalVideoFrames` counts
  frames decoded, not shown; none were dropped, so this does not change
  A6-p.
