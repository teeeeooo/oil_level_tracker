# V2-2 analysis timing on the slowest PC (A4) — Windows result (2026-10-29)

**Verdict:** the run is valid. On a PC of the slowest class the analysis of
SPL#1 takes **169.7 s**: under the 180 s limit, but in the 150–180 s band.
The screens go on, and the analysis must get faster before V2-5. Hardware
decoding is slower on both PCs, so the analysis uses software decoding
only.

- **Request:** [2026-10-29-v2-2-slowest-pc-timing-windows-request.md](../40-operations/2026-10-29-v2-2-slowest-pc-timing-windows-request.md).
  Its criteria were fixed before the run.
- **Source run:** commit `2d43f4c`, confirmed on both PCs by
  `source=5f11f4928d2d files=38`.
- **Who ran it:** the user, in a terminal on the slowest PC (no coding
  agent there), and the Windows agent on the workstation (the request's
  optional §6). Both relayed the script's Markdown result as text.

## Environment

| Item | Slowest PC | Workstation |
|---|---|---|
| CPU | Intel Xeon E5-1620 v3 @ 3.50 GHz, 4 cores, 8 logical | AMD Ryzen Threadripper PRO 7945WX, 12 cores, 24 logical |
| RAM | 15.9 GB | 127.1 GB |
| GPU | NVIDIA Quadro K620 | NVIDIA RTX 4000 Ada Generation |
| OS | Windows 11 Enterprise | Windows 11 Enterprise |
| Python | 3.15.2, as relayed | 3.14.3 |
| OpenCV / NumPy | 4.14.0.94 (headless) / 2.5.4 | the same |
| Form, power, disk | desktop, mains; the video on an SSD | desktop, mains |
| Notes | the CPU stood at about 96 % during the software run (user) | the e-mail embedding job may still have been running |

The request asked for Python 3.14 on the slowest PC; the relayed line reads
3.15.2. The work is inside OpenCV and NumPy, and the picture is identical
(`mean` below), so this does not change the verdict.

## Results (seconds)

| PC | Run | HW used | `grab` | `retrieve` | `reduce` | `wait` | Pass | Glass steps | SHA-256 | **Total** |
|---|---|---|---|---|---|---|---|---|---|---|
| Slowest | software | False | 113.4 | 45.4 | 87.5 | 0.2 | 159.8 | 10.0 | 4.9 | **169.7** |
| Slowest | hardware | True | 254.8 | 130.1 | 100.8 | 0.2 | 386.4 | 10.9 | 2.2 | **397.3** |
| Workstation | software | False | 15.1 | 24.7 | 49.2 | 0.1 | 40.4 | 6.0 | 0.7 | **46.4** |
| Workstation | hardware | True | 17.4 | 94.7 | 43.9 | 0.1 | 113.3 | 5.9 | 0.5 | **119.3** |

| PC | Run | Glass | Context | `mean` | Empty | Draft |
|---|---|---|---|---|---|---|
| Slowest | software | BASE | 8,210 × 728 | 90.052 | 88 % | 9.2 |
| Slowest | hardware | BASE | 8,210 × 728 | 90.668 | 87 % | 10.0 |
| Workstation | software | BASE | 8,210 × 728 | 90.052 | 88 % | 5.4 |
| Workstation | hardware | BASE | 8,210 × 728 | 90.668 | 87 % | 5.3 |

- `reduce` is summed over the worker threads; it overlaps the pass.
- **Sums checked:** in every run the pass plus the Glass steps gives the
  total within 0.1 s, and `grab + retrieve` is within 1.5 s of the pass.
- No run reports an error; every SHA-256 finished before its analysis.

## Against the fixed criteria

| ID | Condition | Result |
|---|---|---|
| S1 | `source=5f11f4928d2d files=38` | **pass**, on both PCs |
| S2 | Xeon E5-1620 v3 or a similar 4-core CPU | **pass** |
| C1 | software BASE `8210x728`, `mean` within 1.0 of 90.052 | **pass**: 90.052 exactly, on both PCs |
| T1 | software total | **169.7 s, in the 150–180 s band: the screens go on; reduce it before V2-5** |
| T2 | hardware ≥ 10 % faster than software | 397.3 s, 134 % **slower**: **software decoding only** |
| — | `오류: 없음` | **pass** |

## Facts for V2-2 and V2-5

- **The worker threads work.** On the workstation the total fell from
  87.4 s to 46.4 s with an identical picture, as expected.
- **The slowest PC is limited by decoding with every core busy.** Its pass
  is almost all `grab` and `retrieve` (158.8 of 159.8 s); the medians are
  hidden (`wait` 0.2 s), and the CPU stood at about 96 %. So more threads
  do not help, and two decoders over halves of the range are no longer a
  candidate: only less CPU work makes it faster.
- **The estimate before the run was too low.** It put this PC at 110–140 s.
  Decoding took 113.4 s there against 15.1 s on the workstation (7.5×),
  sharing four cores with the medians; `retrieve` scaled by 1.8× and the
  draft by 1.7×, as expected.
- **Hardware decoding is out.** It is slower on both PCs, in decoding and
  in taking the frames back from the GPU (`grab` and `retrieve`).
- **The margin is about 10 s,** before the app's own work (writing the
  cache, the UI). That is too thin for acceptance.

## Candidates for less CPU work, before V2-5

1. **The draft after the pass** (9.2 s on that PC, on the critical path):
   a faster exact form of the dynamic programming, or running it while the
   video is read.
2. **Cheaper medians on that CPU** (87.5 s of worker time competing with
   decoding): selecting the two middle ranks in 8-bit gives the same
   values; it was not faster on Apple M1, but that CPU lacks the vector
   sort NumPy uses on newer ones. A one-minute benchmark on that PC
   decides it.
3. **Converting only the Glass band to RGB** instead of the whole frame
   (`retrieve`, 45.4 s, on the decoder's own thread): OpenCV cannot do it.
   It needs a decoder that hands out the YUV planes (PyAV), a new
   dependency that weighs on the package (A8) and moves pixel values by
   rounding. That is the user's decision, if 1 and 2 are not enough.
