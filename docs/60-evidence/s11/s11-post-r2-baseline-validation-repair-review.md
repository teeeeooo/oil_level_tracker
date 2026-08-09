# S11 Post-R2 Baseline Validation Repair Review

Date: 2026-08-09

Reviewed commit: `6ae174fdcd71d8fcab5a8aa85ac6d38667bbe5fe`

Repair implementation: `b350f6126008e24a035eee35f222ce189d694dee`

Status: accepted on the source-tree and available local corpus; final target-Windows field-workflow validation remains open

## Review outcome

Commit `6ae174fd` successfully removed the seven failures that remained after S11-R2. On the exact reviewed commit, the complete canonical suite passed `1449` tests. Its available-corpus R2 replay also preserved the accepted `111/299` numeric Oil stream and all four tracking fingerprints.

The review found three maintenance defects that did not justify reverting that baseline repair:

1. the new low-light accepted-Foam protection was embedded in generic hard current-frame support and could reject a weak, full-width Oil candidate even when the accepted Foam component did not overlap its row;
2. three completed S11-A diagnostic records had been retroactively changed from their fingerprinted historical `14/16` collision result to the current fixture's `16/16` result;
3. the refreshed offline trajectory manifest contained the current `111/299` production stream while still attributing it to the older `4bb52a...` design base, and its prose disagreed with the manifest for the `sample3:1035` support anchors.

## Accepted detector repair

The low-light protection now remains outside generic hard safety. A below-front hypothesis is withheld from comparative and Spatial fallback recovery only when all of the following are true:

- the accepted Foam component leaves less than `0.30` of the effective candidate row outside Foam;
- broad phase strength is below `0.10`; and
- narrow horizontal coverage is at least `0.90`.

The conditions are conjunctive. Accepted-Foam overlap alone cannot reject a real Foam/Oil transition, and weak-broad/full-width texture alone cannot reject a candidate that is spatially separate from the accepted component. The ordinary canonical boundary path, no-interface/visibility/conflict safety, Foam topology and serialized temporal owner are unchanged.

The controlled low-light scene remains non-numeric: its false Oil candidate at source `y=131` has broad strength about `0.035`, narrow coverage `1.0`, and only about `0.188` of its effective row outside the accepted Foam component. A new paired control proves the same scalar candidate remains recovery-eligible with a spatially separate component, remains eligible at exactly `0.30` residual row support, and becomes ambiguous below that floor.

## Documentation and diagnostic provenance repair

- The completed S11-A probe documents again retain their original `14/16` collision figures. Current fixture validation derives its expected P1/P3 count from the current collision surface instead of rewriting historical evidence.
- The offline trajectory manifest is now schema `s11-offline-temporal-trajectory-probe-v2`. It distinguishes estimator design base `4bb52a2718d176874c59a97b9164453165a90c00` from accepted production-stream baseline `16ea0cd1e63b929db469946ccddd75a8762042fb`.
- The v2 manifest fingerprint is `84eaff639c2fe7f264f47dfe1dcab95392c26210e764512c6deb8728c6387a4d`.
- The `sample3:1035` support record now consistently reads `33.033 @ 294` to `35.035 @ 240`, a `2.002 s` unsupported span.

## Validation evidence

Focused Oil/Foam/Spatial preservation:

```text
PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/test_oil_shadow_evidence.py \
  tests/test_foam_phase_detector_integration.py \
  tests/test_s11_spatial_production_fallback.py
```

Result: `89 passed in 8.62 s`.

Offline trajectory v2 diagnostic: `5 passed in 31.14 s`.

Complete canonical suite on the repair tree: `1450 passed in 92.48 s`.

The exact four-video production replay command was:

```text
PYTHONPATH=src .venv/bin/python -m tests.diagnostics.s11_r2_foam_spatial_replay \
  --output-root sample/output/s11-r2-post-review
```

| Video | Numeric Oil | Coverage | Tracking fingerprint |
| --- | ---: | ---: | --- |
| `base_sample_1` | `3/30` | 10.0% | `87166f357d7c962fb16a9a27a4def3329b587e27a74efd0671dce981046f3654` |
| `sample2` | `2/5` | 40.0% | `912225deb00b1a33504d7541be9a61727049a2a845c29ebd8b7badd7197f06aa` |
| `sample3` | `42/151` | 27.8% | `0bbd8a8c3a7c353b0f4a7a6557dc61220f681c7a33eea38ea79c8d75cb268f3c` |
| `sample4` | `64/113` | 56.6% | `d37bbd9101fa3f7d3f56524b588c1e22d76eb4849702d12fceeeec3ea2385c37` |
| **Total** | **`111/299`** | **37.1%** | — |

All four fingerprints exactly match the accepted S11-R2 baseline. The retained truth surface remains `8/13` numeric at `5.4375 px` MAE. Generated replay bundles remain ignored forensic output and are not Git authority.

## Claim boundary

This repair improves authority correctness and provenance; it does not claim a coverage increase or general-field accuracy. The accepted detector/tracking stream is deliberately unchanged. The remaining project gate is still final target-Windows field-workflow validation of the packaged application and user observation report.
