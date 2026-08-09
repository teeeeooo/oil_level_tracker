# S11-R2 Foam/Spatial Authority Repair Evidence

**Status:** `ACCEPTED — source-tree and available-corpus validation`

**Baseline head:** `86937d4f3dd55396b3ecf39efaa4e9a6ec4fb8ab`

**Implementation commit:** `16ea0cd1e63b929db469946ccddd75a8762042fb`

## Accepted change

R2 repairs a bounded authority seam under authoritative accepted-Foam context:

- D5 Foam-separated candidates now require at least `0.30` horizontal material support instead of `0.20`;
- a preliminary relative candidate that fails its Spatial path can no longer stop evaluation of a distinct existing full-path candidate in accepted-Foam context;
- an accepted incumbent is challengeable only when artifact opposition exceeds boundary likelihood by at least `0.20`, its own Foam-excluded Spatial path fails, and the challenger improves boundary-minus-artifact margin by at least `0.08` while satisfying unchanged Spatial safety.

No global boundary, artifact, paired-edge, sector or no-interface threshold changed. The canonical current-frame boundary and serialized temporal reducer remain the only publication and temporal owners.

## Exact four-video replay

The reproducible command is:

```text
PYTHONPATH=src .venv/bin/python -m tests.diagnostics.s11_r2_foam_spatial_replay \
  --output-root sample/output/s11-r2-verified
```

It runs the production `AnalysisPipeline`, `OpenCvPhaseDetector`, static-artifact learning, matching Recipes, explicit `UNKNOWN_REVIEW` initial confirmation and serialized owner at 2 FPS over the accepted qualification windows.

| Video | Baseline numeric | R2 numeric | R2 coverage | Longest missing gap | R2 tracking fingerprint |
|---|---:|---:|---:|---:|---|
| `base_sample_1` | 3 / 30 | 3 / 30 | 10.0% | 8.9 s | `87166f357d7c962fb16a9a27a4def3329b587e27a74efd0671dce981046f3654` |
| `sample2` | 2 / 5 | 2 / 5 | 40.0% | 0.5 s | `912225deb00b1a33504d7541be9a61727049a2a845c29ebd8b7badd7197f06aa` |
| `sample3` | 42 / 151 | 42 / 151 | 27.8% | 17.0 s | `0bbd8a8c3a7c353b0f4a7a6557dc61220f681c7a33eea38ea79c8d75cb268f3c` |
| `sample4` | 62 / 113 | 64 / 113 | 56.6% | 3.5 s | `d37bbd9101fa3f7d3f56524b588c1e22d76eb4849702d12fceeeec3ea2385c37` |
| **Total** | **109 / 299** | **111 / 299** | **37.1%** | — | — |

`base_sample_1` and `sample2` retain their exact full tracking fingerprints. Sample3 retains its exact numeric Oil stream; one non-numeric frame at `38.5385 s` changes only from `OIL_REACQUISITION_PENDING` to `OIL_EVIDENCE_AMBIGUOUS` after the weak Foam-separated candidate loses authority.

The user-confirmed truth surface remains `8/13` numeric with `5.4375 px` MAE, `6.5 px` median error and `11 px` maximum error. R2 therefore improves the unlabelled trajectory surface without sacrificing a confirmed truth anchor.

## Material sample4 stream delta

Direct Glass-ROI inspection classified every raw numeric change:

| Frame / time | Baseline | R2 | Classification |
|---|---:|---:|---|
| `1080 / 36.0 s` | missing | `y=842` | added on the visible material interface; replaces a weak `y≈868` incumbent during current-frame arbitration |
| `1275 / 42.5 s` | `y=884` | missing | removed bottom-structure excursion; insufficient `0.261` horizontal support |
| `1320 / 44.0 s` | missing | `y=845` | added visible interface anchor after the false incumbent no longer controls temporal reacquisition |
| `1455 / 48.5 s` | `y=883` | `y=867` | corrected from the bottom rim to the retained Foam/Oil phase boundary |
| `1590 / 53.0 s` | missing | `y=846` | added distinct full-path candidate after path-invalid preliminary authority is removed |
| `1635 / 54.5 s` | `y=866` | `y=853` | corrected to the stronger current material transition |

The net count is only `+2`, but the graph no longer treats `42.5 s / y=884` as the observed minimum. In the regenerated sample4 report, the highest landmark moves from `41.0 s` to `37.5 s` and the minimum from the false `42.5 s` excursion to `39.5 s`, where the source capture visibly shows the accepted Oil boundary below the accepted Foam front. Solid direct runs, dashed display-only bridges, missing CSV/cursor values and Foam gap semantics remain unchanged.

Generated replay bundles under `sample/output/s11-r2-verified/` are forensic support and remain outside Git authority.

## Rejected changes

The implementation deliberately excludes three failed ablations:

- paired-edge relaxation to `0.95`, which created six explanatory-overlay false numerics in `base_sample_1`;
- a general three-sector weak path, which admitted the same overlay family;
- a D5-wide `paired_edge_strength <= 0.80` ceiling, which removed the user-confirmed `sample4:1680 -> y=866` anchor.

The path-invalid continuation was also restricted to accepted-Foam context after a general version made the retained low-exposure negative numeric.

## Test evidence

Focused and preservation validation:

```text
PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/test_oil_controlled_benchmark.py \
  tests/test_oil_single_frame_observability_contract.py \
  tests/test_s11_spatial_path_probe.py \
  tests/test_s11_spatial_production_fallback.py \
  tests/test_oil_shadow_evidence.py
```

Result: `408 passed in 24.73 s`.

The complete canonical command produced `1442 passed, 7 failed in 91.98 s`. All seven failures were independently reproduced on exact baseline head `86937d4...`; six reproduced directly and the local-corpus offline probe reproduced after supplying the same four ignored MP4 inputs. They are pre-existing stale/synthetic/GUI expectations, including the offline probe's historical `9/13` expectation versus the already accepted `8/13` detector baseline. R2 introduced no new canonical failure.

## Acceptance and remaining gate

R2 is accepted on the available source-tree corpus because it removes/corrects misleading graph anchors, adds defensible material-interface observations, preserves confirmed truth and retained negatives, and does not broaden detector authority outside the diagnosed seam.

This is not general-field detector accuracy PASS and does not close S11. The remaining project gate is final target-Windows field-workflow validation of the exact resulting head and generated user observation report.
