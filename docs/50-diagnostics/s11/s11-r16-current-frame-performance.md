# S11-R16 Current-Frame Performance Evidence

## Classification and scope

This is diagnostics evidence for the behavior-preserving current-frame
optimization after R5 and before the R16 resolver change. It does not authorize
threshold, ordering, provenance, schema, detector-version or resolver-version
changes.

- measurement date: `2026-08-23`;
- source parent: `7fcc476cd1649a13d255c56a688f11cfb7ce62bf` plus the
  current-frame optimization worktree;
- workload: checked-in `sample4`, 0--56 s, 2 FPS, 113 frames;
- host/runtime: the macOS, Python, OpenCV and NumPy environment recorded by
  [`s11-r16-refactor-performance-baseline.md`](s11-r16-refactor-performance-baseline.md);
  and
- production owner: the single `OpenCvPhaseDetector` used by both Base and
  Accum.

Private Windows Base/Accum runtime evidence is not present in this checkout and
remains `NOT AVAILABLE`.

## Optimization boundary

The spatial fallback evaluated the same robust top/bottom sector statistics
again for overlapping candidate search windows in one frame. The change keeps
an ephemeral cache inside one
`_spatially_supported_boundary_observation()` call. Its key is the exact sector,
band depth, gap and row. Inputs that are fixed for that call--blurred image,
visible mask and Foam-residual mask--never cross the cache boundary.

The cache stores the exact result of the existing robust median/MAD calculation,
including an unavailable result. Candidate search ranges, tie-breaking keys,
floating-point values, thresholds, candidate ordering and debug projection are
unchanged. There is no cross-frame or cross-glass state and no reuse across a
different mask. A deterministic regression test compares cached and uncached
results and asserts that the second identical lookup performs no robust-statistic
calls.

## Normal operational workload

The R0 baseline is the stable three-run reference. The post-change result is
also three sequential runs of the same repository profiler with debug disabled.

| Measurement | R0 three-run median | Post-change three-run median | Delta |
|---|---:|---:|---:|
| End-to-end wall time | 15.486 s | 11.870 s | -23.4% |
| Real-time factor | 0.277 | 0.212 | -23.5% |
| Detector mean latency | 78.972 ms/frame | 63.747 ms/frame | -19.3% |
| Detector total | 8.924 s | 7.203 s | -19.3% |
| Completed-window resolve | 2.055 s | 0.158 s | -92.3% |

The end-to-end comparison includes the already isolated R4 resolver gain. For
the current-frame change alone, the R5 one-run signal was 13.729 s and
78.854 ms/frame; the corresponding first post-change run was 12.068 s and
64.107 ms/frame, a 12.1% end-to-end and 18.7% detector reduction. Timing is
comparative evidence, not a substitute for the behavior gates below.

## Causal profile

`cProfile` adds instrumentation overhead, so these values identify ownership
rather than normal wall time.

| Function/measurement | Before | After | Delta |
|---|---:|---:|---:|
| `_robust_sector_phase` calls | 155,000 | 79,830 | -48.5% |
| `_robust_sector_phase` cumulative | 6.791 s | 3.440 s | -49.3% |
| `_best_sector_phase` cumulative | 6.984 s | 3.582 s | -48.7% |
| Profiled detector total | 17.905 s | 14.416 s | -19.5% |

The number of candidate path evaluations and `_best_sector_phase` calls remains
683 and 3,380 respectively. The reduction therefore comes from eliminating
duplicate robust statistics, not from skipping candidates or narrowing the
proposal lattice.

## Debug-enabled workload

One immediate before/after run used `DebugTraceLevel.BASIC`, the production
JSONL/image trace writer and the same completed-window bundle path.

| Measurement | R5 before | Post-change | Delta |
|---|---:|---:|---:|
| End-to-end wall time | 18.442 s | 16.762 s | -9.1% |
| Real-time factor | 0.329 | 0.299 | -9.1% |
| Detector mean latency | 79.625 ms/frame | 64.216 ms/frame | -19.4% |
| Detector total | 8.998 s | 7.256 s | -19.4% |

Debug trace selection and image/JSONL output account for work outside the timed
detector call, so the end-to-end percentage is intentionally smaller. The
repository profiler now accepts `--debug-trace-level none|basic|full`; its
default and the normal operational configuration remain `none`.

## Behavior and reproducibility gates

Every timed run retained 113 rows, 111 numeric Oil rows and tracking fingerprint
`2da3ba6cdacb59bda03541243132d0a3ce014b38c49451411a05d5aef928bfe2`.
The BASIC before and after runs retained the same fingerprint as well. The
checked-in current-frame/debug and completed-window characterization tests stay
authoritative for exact field and ordering parity; the isolated four-video R15
replay is rerun before this optimization commit.

```bash
.venv/bin/python -m tests.diagnostics.s11_r16_performance_profile \
  --output-root /tmp/oil-r16-hotpath-after-3 \
  --sample sample4 --repeats 3

.venv/bin/python -m tests.diagnostics.s11_r16_performance_profile \
  --output-root /tmp/oil-r16-hotpath-after-basic \
  --sample sample4 --repeats 1 --debug-trace-level basic
```

The later R16 directed-tracklet change is intentionally excluded from these
numbers and must receive its own causal output and performance evidence.
