# V2-2 analysis timing (A4) — Windows result (2026-10-29)

**Verdict:** the run is valid. The analysis of SPL#1 takes **87.4 s**, under
the 150 s that lets the screens go on with this design. Hardware decoding
is slower, so the analysis uses software decoding.

- **Request:** [2026-10-29-v2-2-analysis-timing-windows-request.md](../40-operations/2026-10-29-v2-2-analysis-timing-windows-request.md).
  Its criteria were fixed before the run.
- **Source run:** commit `f330e62`, confirmed by R1
  (`checked=46 mismatched=0`). The user had already extracted that
  commit's ZIP into `C:\0.Coding\oil_level_tracker-main`; the hash check
  confirmed it.
- **Environment:** `.venv-v2` from the V2-1 run, reused after the request's
  `pip install -e . pytest`.
- **Relay:** the user relayed the result block as text.

## Environment

| Item | Value |
|---|---|
| Python | 3.14.3 |
| OpenCV / NumPy | 4.14.0.94 (headless) / 2.5.4 |
| pytest | 9.2.0 |
| CPU | AMD Ryzen Threadripper PRO 7945WX, 12 cores, 24 logical processors |
| Power | desktop PC, mains |
| Other load | an e-mail embedding job (about 15 % of the 24 logical processors, 10.4 GB); system load 12 % at the time |

The other job was running during T1–T3, so the times are, if anything, a
little high.

## Results

| ID | Line | Value |
|---|---|---|
| R1 | source check | `checked=46 mismatched=0` |
| R2 | pytest | `87 passed, 2 skipped in 11.62s` |
| — | `Traceback` | none in T1–T3 |

| Run | Video | Decoding | `grab` | `retrieve` | `reduce` | Pass | Draft | `analysis total` |
|---|---|---|---|---|---|---|---|---|
| T1 | SPL#1, 8,210 columns, 98,411 frames | software | 8.2 s | 27.0 s | 45.8 s | 81.3 s | 5.5 s | **87.4 s** |
| T2 | SPL#1 | hardware (`hardware_used=True`) | 21.9 s | 47.5 s | 44.4 s | 114.7 s | 5.6 s | 120.9 s |
| T3 | SPL#4, 520 columns, 7,786 frames, 2 Glasses | software | 1.3 s | 1.6 s | 0.8 s | 3.7 s | 0.1 s | 3.9 s |

| Run | Glass | Context | `mean` | Empty | PNG bytes |
|---|---|---|---|---|---|
| T1 | SPL#1 BASE | 8,210 × 728 | 90.052 | 88 % | 9,836,265 |
| T2 | SPL#1 BASE | 8,210 × 728 | 90.668 | 87 % | 9,795,418 |
| T3 | SPL#4 BASE | 520 × 484 | 148.953 | 5 % | 463,403 |
| T3 | SPL#4 ACCUM | 520 × 298 | 99.990 | 51 % | 302,831 |

- **Sums checked:** in each run `grab + retrieve + reduce` is within 0.9 s
  of the pass, and the pass plus the Glass steps gives `analysis total`.
- **SHA-256:** 0.6 s (T1), 0.5 s (T2), 0.0 s (T3), each finished before the
  pass ended, so it adds nothing to the total.
- The background view and the PNG pieces take 0.3 s each on SPL#1.

## Against the fixed criteria

| ID | Condition | Result |
|---|---|---|
| R1 | `checked=46 mismatched=0` | **pass** |
| R2 | `87 passed, 2 skipped` | **pass** |
| T1 | `analysis total` ≤ 150 s | **87.4 s: the screens go on with this design** |
| T2 | `hardware_used=True`, ≥ 10 % faster than T1, `mean` within 1.0 | `hardware_used=True` and the `mean` differs by 0.616, but the total is 38 % **slower** (120.9 s): **software decoding stays the default** |
| T3 | none | two Glasses of SPL#4 in 3.9 s |
| — | no `Traceback` | **pass** |

## Facts for V2-2

- **A4 has about half its limit to spare on this PC:** 87.4 s of 180 s. The
  draft comparison took 202.1 s for the context image alone, with the
  spike's row median.
- **Where the time goes now:** the row median (`reduce`) is 56 % of the
  pass, taking out the frames (`retrieve`) 33 % and decoding (`grab`)
  10 %. They run one after another in one loop.
- **Hardware decoding loses here** in both decoding and taking out the
  frames. The analysis adapter keeps `hardware=False`.
- **The product code gives the comparison's drafts on Windows too.** The
  empty share per Glass (88 %, 5 %, 51 %) equals method B's weak share in
  the comparison, and the draft time (5.5 s) matches its 5,449 ms. On
  SPL#1, 88 % of the Oil line starts empty, so the point line and the
  pencil (V2-3) do most of that Glass.

## Limits

- **One PC.** This is a 12-core workstation. A4 is accepted on target
  Windows with the one-folder build (Product SSOT §2, V2-5); a slower PC
  shrinks the margin. If one is needed, running the row median on a
  second thread while the next frames are decoded is the first option.
- **The script, not the app.** The whole analysis inside the app, with the
  cache written, is timed again in step 9.
