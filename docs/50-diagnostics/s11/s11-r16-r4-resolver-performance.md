# S11-R16 R4 Resolver Performance Evidence

## Classification and scope

This is diagnostics evidence for the behavior-preserving R4 resolver
decomposition. It does not authorize R16 output changes or replace private
Windows qualification.

- measurement date: `2026-08-23`;
- source parent: `0104b558367661f12df5452194c8e12f92d66e91` plus the R4 worktree;
- detector/resolver versions: unchanged R15 versions;
- workload and host: the same checked-in `sample4`, 0--56 s, 2 FPS, macOS
  environment recorded by
  [`s11-r16-refactor-performance-baseline.md`](s11-r16-refactor-performance-baseline.md);
- debug: disabled; and
- repeat count: one comparative run. The R0 three-run median remains the
  authoritative baseline.

## Behavior gate

The R4 run retained 113 rows, 111 numeric Oil rows and tracking fingerprint
`2da3ba6cdacb59bda03541243132d0a3ce014b38c49451411a05d5aef928bfe2`.
The checked-in R0 current-frame/debug and completed-window characterization
hashes also remained unchanged.

## Result

| Measurement | R0 three-run median | R4 one-run signal |
|---|---:|---:|
| End-to-end wall time | 15.486 s | 13.663 s |
| Real-time factor | 0.277 | 0.244 |
| Detector mean latency | 78.972 ms/frame | 78.312 ms/frame |
| Completed-window resolve | 2.055 s | 0.156 s |

The resolver signal is about 13.1 times faster and the end-to-end signal is
about 11.8% faster. Detector latency stayed within the R0 range; the measured
gain came from the completed-window boundary rather than altered current-frame
evidence or thresholds.

## Causal profile

R0 cProfile evidence recorded 188,782 calls to
`OilCandidateEvidence.from_candidate` for this workload. The same cProfile
workload after R4 recorded 2,611 calls, a 72.2-times reduction. The remaining
count equals the run-local candidate normalization boundary: each input
candidate dictionary is converted once into immutable typed evidence, which
is then retained by its candidate reference through admission, opposition,
path and projection policies.

A checked-in regression test instruments this boundary and fails if a
completed window normalizes any candidate more than once. Candidate ordering,
coarse component identifiers and every persisted field remain unchanged in
R4.

## Limitations

- A single run is a comparative signal, not a stable cross-host benchmark.
- The private Windows Base/Accum corpus and packaged runtime were not available
  in this checkout, so their R4 timing remains `NOT AVAILABLE`.
- Directed branch-aware tracklets and lifecycle semantics are intentionally
  deferred to the isolated R16 change.
