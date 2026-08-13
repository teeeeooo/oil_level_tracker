# S11-R9 Calibrated Observation Evidence

## Implementation

R9 adds responsive multi-select artifact calibration, calibration-only
high-recall Oil proposals, a no-qualified-path dynamic bootstrap, current-evidence
Foam alias continuation and final sequence trace annotation. Detector version is
`opencv-phase-detector-r9-calibrated-observation-v1`; Oil and composition
resolver version is `r9-calibrated-observation-v1`.

Logical commits before documentation closeout:

- `dcb5cc9` — responsive proposal UI, selection highlight and bulk apply;
- `19bbd23` — calibrated high-recall generation and dynamic Oil recovery;
- `41fa67f` — preserve Foam that is vertically separated from Oil;
- `a6489f7` — append compact final sequence diagnostics to raw trace;
- `f4de1e7` — disable calibrated recovery when a qualified path exists; and
- `08e9237` — establish R9 versions and reproducible replay gates.

## R8 Windows evidence incorporated

The private R8 replay produced Base 0/601 numeric and Accum 189/601 numeric.
Exact coordinate reconciliation showed that Base lacked a candidate within
±25 px at 540 and 674 s and had only one at 634 s; artifact removal alone was
therefore insufficient. Accum's real Foam around 411 px was suppressed through
a stale alias track even though final Oil was around 448 px. The detailed
record is the [R8 Windows diagnostic](../../50-diagnostics/s11/s11-r8-windows-calibrated-observation-diagnostic.md).

## Local replay

The exact R9 uncalibrated replay retained the R8 safety baseline:

| sample | rows | numeric Oil | public Foam |
|---|---:|---:|---:|
| base_sample_1 | 30 | 19 | 0 |
| sample2 | 5 | 5 | 0 |
| sample3 | 151 | 42 | 5 |
| sample4 | 113 | 76 | 0 |
| total | 299 | 142 | 5 |

All numeric Oil has same-frame provenance. Checked truth is numeric at 10/13
points with 5.85 px MAE and 11 px maximum error. Sample3's reviewed unclear and
changing-focus 39–90 s interval remains non-numeric.

The official manifest is
`sample/output/s11-r9-calibrated-observation/replay_manifest.json`; the runner
is `tests/diagnostics/s11_r9_calibrated_observation_replay.py`.

## User-like calibration and safety correction

Selecting the reviewed sample4 lower-rim proposal at 3.0 s changed coverage
76→81/113. Public Foam remained zero, checked truth remained 2/5 numeric with
0.5 px MAE/max error, and reviewed visual matches remained 7.

An intermediate implementation reached 112/113 but drifted 25–47.5 px from the
late truth. It was rejected. The correction prevents high-recall candidates
from consuming normal capacity, semantic/cross-representation corroboration or
path selection when a qualified path already exists. The corrected replay
restored the established events and truth behavior.

The official manifest is
`sample/output/s11-r9-artifact-calibration/artifact_calibration_manifest.json`;
the runner is `tests/diagnostics/s11_r9_artifact_calibration_replay.py`.

## Performance

Direct debug-disabled detector timing over the same sample4 113 frames was:

| calibration | detector total | mean/frame |
|---|---:|---:|
| off | 7.146 s | 63.2 ms |
| on | 7.296 s | 64.6 ms |

Calibration added about 2.1% detector time in this local run. This timing
excludes video seek, report, capture and debug-trace finalization and is not
directly interchangeable with the earlier cProfile cumulative values.

## Repository gate

- Python compile for `src` and R9 diagnostic runners: passed;
- R9 detector/version focused gate: 341 passed;
- Oil/Foam/calibration/trace focused gates: passed;
- full repository regression: 1,557 passed in 114.95 s; and
- `git diff --check`: passed before documentation closeout.

## Status

R9 implementation and local validation pass. Secure-Windows R9 Base/Accum
validation remains pending, so no final private-field or general-field accuracy
claim is made.
