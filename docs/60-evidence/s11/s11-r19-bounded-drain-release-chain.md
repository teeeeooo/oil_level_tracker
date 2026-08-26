# S11-R19 Bounded Drain-Release Chain Validation Evidence

**Status:** `LOCAL PASS / WINDOWS REQUIRED`

## Scope and source identity

This record covers the independent local validation of R19 at source HEAD
`2b6532178abfb52a280774949e21d83b97cd0629` (`fix(detector): fail closed on
recovery ambiguity`). The implementation commits validated were:

- `4e2f5908c5ecc754afab38c5e678edbfff7318e3` — bounded drain-release chain;
- `2b6532178abfb52a280774949e21d83b97cd0629` — recovery ambiguity fail-closed.

The worktree was clean before this evidence update. No production code or test
files were changed during validation. R19 changes the bounded Oil lifecycle
owner and the detector/resolver version labels only. Foam implementation files
were unchanged; the Foam diagnostic schema remains
`r18-field-causal-observability-v1`, and Recipe/schema settings are unchanged.

## Validation commands and results

All tests and replay commands used the repository `.venv/bin/python`.

| Gate | Command | Result |
|---|---|---|
| R19 lifecycle | `.venv/bin/python -m pytest tests/unit/test_oil_phase_lifecycle.py -q` | `74 passed in 0.16s` |
| Focused resolver/tracklet/Oil/Foam/sequence | `.venv/bin/python -m pytest -q tests/unit/test_oil_observation_resolver.py tests/test_oil_resolver_decomposition.py tests/unit/test_oil_interface_tracklets.py tests/unit/test_oil_candidate_authority.py tests/unit/test_oil_supplemental_path.py tests/test_oil_serialized_owner.py tests/test_oil_detector_integration.py tests/test_oil_controlled_benchmark.py tests/unit/test_foam_episode_resolver.py tests/test_foam_phase_detector_integration.py tests/test_foam_controlled_benchmark.py tests/test_s11_sequence_observability_integrity.py tests/test_initial_state_retrospective_reconstruction.py tests/test_detection_run_coordinator.py` | `512 passed in 63.75s` |
| Controlled benchmark/performance tests | `.venv/bin/python -m pytest -q tests/test_detector_benchmark_integration.py tests/test_detector_benchmark_runner.py tests/test_detector_benchmark_metrics.py tests/test_oil_controlled_benchmark.py tests/test_foam_controlled_benchmark.py tests/test_controlled_dataset_identity.py tests/test_oil_plateau_evidence_performance.py` | `340 passed in 42.26s` |
| Canonical repository suite | `.venv/bin/python -m pytest` | `1690 passed in 156.87s` |
| Qt partition (README-described focused partition) | `.venv/bin/python -m pytest -m qt_app -q` | `245 passed, 1445 deselected in 10.25s` |
| Compilation | `.venv/bin/python -m compileall -q src tests` | passed |
| Governance, implementation range | `.venv/bin/python scripts/check_detector_governance.py --base-ref 4e2f590^ --head-ref 2b65321` | passed |
| Governance, current clean worktree | `.venv/bin/python scripts/check_detector_governance.py --base-ref 0dbe06a --head-ref 2b65321 --include-worktree` | passed |
| Diff whitespace | `git diff --check` | passed |
| Changed-doc relative links | repository has no dedicated link checker; an equivalent read-only `.venv/bin/python` check resolved `313` changed-document relative links | `313/313`, no missing targets |

## Focused safety contracts

The lifecycle suite covers initial-FULL and established-partial fragmented
release chains, bounded same-owner continuation, clear one-to-one handoff,
positive progress/directional agreement, duplicate-seed and multi-chain
ambiguity, material/authority opposition, jump/reversal/loss limits, absolute
evidence-window expiry, initial-EMPTY suppression, changed partial-fill context,
same-frame publication and diagnostic schema. Direct release remains first and
authoritative; recovery publishes only the unique current row and never copies
an earlier coordinate or merges physical tracklet IDs.

## Exact four-video replay and R18 comparison

The existing deterministic R18 harness was run first into a fresh `/tmp`
directory with `--skip-fingerprint-check` so no golden could be regenerated:

```text
.venv/bin/python -m tests.diagnostics.s11_r18_lifecycle_closure_replay \
  --root /Users/sunjaekim/Developer/oil_level_tracker \
  --output-root /tmp/s11-r19-independent-replay.N72Y4c \
  --skip-fingerprint-check
```

It processed `299` rows and `162` numeric Oil rows. A second fresh run with
fingerprint checking enabled also passed all frozen R18 expected counts and
fingerprints. Per-sample results were:

| Sample | Rows | Numeric Oil | Foam episodes | R18 tracking fingerprint |
|---|---:|---:|---:|---|
| `base_sample_1` | 30 | 28 | 0 | `5879657ce71ced5970c13272867f61def7d7972195b5d264a3cf63c99f1122b7` |
| `sample2` | 5 | 4 | 0 | `85713bc131a808d81d073bec5bff8d035604cb4c1912ba6412c1b5c448fe4976` |
| `sample3` | 151 | 29 | 2 | `feb7e139269894b0aa86d692722acb4512e487dd0b71367fa88859e67745d5a1` |
| `sample4` | 113 | 101 | 1 | `0f2029475506c87aac3ec46bf118b3ae9a1ead0da45eb0d214e1d23ececf9154` |
| **Total** | **299** | **162** | **3** | — |

The four generated `tracking_data.csv` row sequences were byte-identical to
the preserved R18 rows after excluding the per-run UUID column. `events.csv`
rows were likewise identical after excluding that UUID. Stable sample summary,
all audit payloads and all R18 contract fields were identical. The checked
truth aggregate was `13` cases, `11` numeric, `9.6363636364 px` MAE,
`24.5 px` maximum error and `11.9230769231 px` coverage-adjusted MAE;
sample3 completed-fill numeric count was `0`, late-drain numeric count `12`,
and sample4 visible-range matches were `8`. Same-frame provenance was `PASS`,
with zero numeric rows lacking same-frame provenance. The two retained checked
truth misses remain sample2 frame `0`/Y`592.0` and sample4 frame `0`/Y`860.5`.

The invariant replay is behavior evidence, not Windows field qualification.
The R19 recovery path is safely a no-op on these checked local videos, while
the existing Oil and Foam outputs remain unchanged.

## Performance evidence

The accepted resolver performance harness was run at the exact clean R19 head
for sample4, 0–56 s, 2 FPS, debug disabled, official static learning and
official bundle output, with three repeats:

```text
.venv/bin/python -m tests.diagnostics.s11_r16_performance_profile \
  --root /Users/sunjaekim/Developer/oil_level_tracker \
  --output-root /tmp/s11-r19-performance.klLUw5 \
  --sample sample4 --repeats 3 --behavior-owner R19 \
  --expected-numeric-oil-count 101 \
  --expected-tracking-fingerprint 0f2029475506c87aac3ec46bf118b3ae9a1ead0da45eb0d214e1d23ececf9154 \
  --source-head 2b6532178abfb52a280774949e21d83b97cd0629
```

All three repeats retained `113` rows, `101` numeric Oil rows and the expected
fingerprint. Median end-to-end time was `11.8011 s` (real-time factor
`0.2107`), detector mean latency `64.7493 ms/frame`, and completed-window
resolution `0.2057 s`. Compared with the preserved R18 profile (`11.7267 s`,
`0.2094`, `64.7271 ms/frame`, `0.2016 s`), these macOS measurements are a
small comparative variation, not a Windows throughput claim.

## Remaining Windows gate

Canonical `windows_sample1_heating_coldstart` replay remains required. It must
compare all `1,202` rows against the frozen R18 causal bundle, enumerate all
nine reviewed-truth segments, and verify unique recovery-chain provenance (or
safe absence) for Base and Accum drain. It must preserve lower-structure
rejection, initial-EMPTY suppression, exact selected-candidate/sequence/CSV
equality and Foam behavior. Until that private Windows replay is run and
reviewed, S11 remains active and this result is `LOCAL PASS / WINDOWS REQUIRED`,
never field PASS.

## Detector Governance

- Logic-map nodes: `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `FOAM-CANDIDATE`, `FOAM-EPISODE`, `PUBLICATION-PROVENANCE`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F05`, `S11-F07`, `S11-F08`, `S11-F09`, `S11-F10`
- First harmful stage: canonical Windows field effectiveness remains untested for R19; the R18 causal boundary is before-or-at `OIL-PHASE-DRAIN` for Base and before or inside partial-fill release for Accum, while local checked-video behavior is invariant.
- Logic-map impact: NONE — R19 uses the existing lifecycle owner and does not change node ownership or boundaries.
- Failure-registry impact: NONE — this evidence records local validation and does not alter the durable causal mechanisms.
