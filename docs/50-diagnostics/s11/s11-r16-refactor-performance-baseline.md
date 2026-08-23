# S11-R16 Refactor Performance Baseline

## Classification and scope

This is a diagnostic baseline for the behavior-preserving R0--R5 refactor and
the later R16 detector replacement. It does not define the current milestone
gate, authorize changed detector output or establish private-Windows speed.

- measurement date: `2026-08-23`;
- source head: `d90d5165cf787f5884389512afabe451ab41e18d`;
- detector: `opencv-phase-detector-r15-state-aware-material-ownership-v1`;
- resolver: `r15-state-aware-material-ownership-v1`;
- host: macOS 26.5.2 arm64, Python 3.14.4, OpenCV 4.14.0, NumPy 2.5.1;
- workload: checked-in `sample4`, 0--56 s, 2 FPS, 113 rows, debug disabled;
- pipeline: official start/middle/end static learning, completed-window
  resolution and finalized output bundle; and
- repetitions: three sequential runs in one shell session.

The private Windows Base/Accum corpus was not available in this checkout, so
its end-to-end and packaged-runtime timing is `NOT AVAILABLE`.

## Reproducible profiler

The repository-owned runner is
`tests/diagnostics/s11_r16_performance_profile.py`. It wraps the official
analysis path without changing production instrumentation and rejects a run if
the accepted R15 row count, numeric count or tracking fingerprint changes.

```bash
.venv/bin/python -m tests.diagnostics.s11_r16_performance_profile \
  --output-root /tmp/oil-r16-profile \
  --sample sample4 \
  --repeats 3
```

The generated `performance_profile.json` records per-run measurements, host
identity, detector latency distribution, stage totals, RTF and tracking
fingerprint.

## Baseline result

All three runs retained 113 rows, 111 numeric Oil rows and fingerprint
`2da3ba6cdacb59bda03541243132d0a3ce014b38c49451411a05d5aef928bfe2`.

| Measurement | Three-run median |
|---|---:|
| End-to-end wall time | 15.486 s |
| Real-time factor (`wall / 56 s`) | 0.277 |
| Detector mean latency | 78.972 ms/frame |
| Detector total | 8.924 s |
| Video open/read/close | 3.854 s |
| Completed-window resolve | 2.055 s |
| Static learning | 0.009 s |
| Application outcome assembly | 0.012 s |
| Bundle output | 0.565 s |

Individual end-to-end times were 15.596, 15.422 and 15.486 seconds. Individual
detector means were 78.697, 78.972 and 79.499 ms/frame. The median run's
detector median/p95 were 83.022/92.526 ms.

## Function-level bottlenecks

A separate `cProfile` run adds instrumentation overhead and is not used as the
wall-time baseline. Its call graph identifies the optimization owners:

1. current-frame Oil evaluation is dominated by
   `oil_spatial_fallback._best_sector_phase` and repeated robust sector
   statistics;
2. completed-window resolution repeatedly constructs
   `OilCandidateEvidence.from_candidate` while computing representation,
   authority, track opposition and projection; and
3. `OilObservationResolver._candidate_refs` and
   `_apply_track_opposition` dominate the resolver, while Viterbi itself is a
   small fraction of the measured time.

The profiled resolver constructed typed evidence 188,782 times for 113 frames,
including 60,216 representation-family lookups. This is direct evidence for a
single typed-evidence normalization boundary during R4. It does not authorize
cache behavior that changes a field's availability or value.

## Acceptance use

- R0--R5 must preserve the fixed characterization and R15 replay fingerprints.
- Optimizations may remove duplicate evidence construction, repeated searches,
  unnecessary materialization and avoidable I/O only after parity is proved.
- R16's directed tracklet owner must be bounded/incremental rather than
  repeatedly rebuilding an unbounded whole-window graph.
- Accuracy, fail-closed abstention, candidate ordering and same-frame
  provenance cannot be traded for speed.
- No exact speedup threshold was supplied. Final evidence must report the
  before/after result on this same workload and disclose any unavailable
  private-Windows measurement.
