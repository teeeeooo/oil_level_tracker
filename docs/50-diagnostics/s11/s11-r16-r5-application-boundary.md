# S11-R16 R5 Application Boundary Evidence

## Classification and scope

This diagnostic records the behavior-preserving R5 clean-architecture move.
It is causal and reproducibility evidence, not detector acceptance authority.
The active milestone and durable detector semantics remain owned by the routed
project, architecture and validation documents.

- measurement date: `2026-08-23`;
- source parent: `a17b53bc5b34c17b0a946ff7f781aae7f3b83e5a` plus the R5 worktree;
- detector/resolver versions and thresholds: unchanged R15 values; and
- private Windows Base/Accum and packaged-runtime verification: `NOT AVAILABLE`.

## Boundary change

Before R5, nine UI modules held 15 direct imports from concrete
`adapters.storage` or `adapters.vision` modules. Those edges covered result
bundle reading, bundle asset resolution, recent history, debug trace access,
debug export, source-video resolution, truth persistence/fixture export and
detector-backed artifact proposal.

R5 replaces all 15 edges with application-owned ports, value/error contracts
or pure domain geometry. The resulting direct UI business-adapter import count
is zero. `bootstrap.py` is the composition root that creates and injects the
concrete implementations. The explicitly retained
`adapters.presentation` imports are Qt-only frame/image conversion details;
they do not acquire videos, read/write business files or own detector policy.

Key ownership decisions:

- review bundle, asset, source-video, debug, recent-history and truth I/O expose
  application port contracts and application-owned failure categories;
- concrete storage/vision exceptions implement those inner contracts, so UI
  cancellation and user-correctable error handling no longer names an adapter;
- `ResultActionService` receives its asset resolver rather than constructing a
  filesystem adapter;
- result-review and analysis-completion collaborators are injected from the
  composition root;
- truth identity is application-owned while JSON persistence and fixture/video
  export remain outer adapters;
- detector-backed artifact proposals are injected through an application port;
  normalized-template-to-source projection is pure domain geometry; and
- no ceremonial port or wrapper was deleted because reachability did not prove
  another unused production owner during this bounded change.

## Behavior and replay gate

The R0 current-frame/debug and completed-window characterization hashes remain
unchanged. The isolated exact R15 replay retained all four accepted row/numeric
counts and fingerprints:

| Sample | Rows | Numeric Oil | Fingerprint |
|---|---:|---:|---|
| `base_sample_1` | 30 | 30 | `0a68c47d131ec3c0414d78c3dd8e61422ab484ba403c7320d4af0e28bd496a34` |
| `sample2` | 5 | 3 | `834c323e96c1df35f9ff17f746510c99dfece43b10cd015d15206a6d11b97b07` |
| `sample3` | 151 | 43 | `c2fe7b1eb3de3ad5b169f61ba06c9ebcc7aec016c6e6a082f3517ca3d517d4c9` |
| `sample4` | 113 | 111 | `2da3ba6cdacb59bda03541243132d0a3ce014b38c49451411a05d5aef928bfe2` |

The replay also retained zero numeric rows without same-frame provenance.

## Performance signal

The same checked-in `sample4` profiler, normal operational configuration and
one-run signal produced:

| Measurement | R0 three-run median | R4 one-run | R5 one-run |
|---|---:|---:|---:|
| End-to-end wall time | 15.486 s | 13.663 s | 13.729 s |
| Real-time factor | 0.277 | 0.244 | 0.245 |
| Detector mean latency | 78.972 ms/frame | 78.312 ms/frame | 78.854 ms/frame |
| Completed-window resolve | 2.055 s | 0.156 s | 0.157 s |

R5 adds dependency injection but no analysis-loop work. The signal retains the
R4 resolver gain without a material detector or resolver regression. Timing is
comparative host evidence only; fingerprints and abstention remain hard gates.

## Verification

```bash
.venv/bin/python -m pytest -q <R5 storage/truth/review/UI/architecture targets>
# 242 passed

.venv/bin/python -m pytest -q <result-review/UI/architecture targets>
# 82 passed

.venv/bin/python -m tests.diagnostics.s11_r15_material_ownership_replay \
  --output-root /tmp/oil-r16-r5-r15-replay
# PASS: four isolated workers and all accepted R15 fingerprints

.venv/bin/python -m tests.diagnostics.s11_r16_performance_profile \
  --output-root /tmp/oil-r16-r5-profile --sample sample4 --repeats 1
# PASS: exact sample4 fingerprint retained
```

An AST guard now fails if any production UI module directly imports a concrete
storage or vision business adapter. Private Windows evidence remains pending
and cannot be inferred from these local results.
