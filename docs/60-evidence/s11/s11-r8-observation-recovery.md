# S11-R8 Observation-Recovery Evidence

## Implementation

R8 implements one generic detector with independent Oil/Foam authority, bounded
high-recall representation, dynamic continuation recovery, user-selected
artifact templates, confirmed-initial-state graph hold and vectorized hot paths.
Detector version is `opencv-phase-detector-r8-observation-recovery-v1` and the
sequence/Oil resolver version is `r8-observation-recovery-v1`.

Logical commits before final validation:

- `1480c59` — R8 observation recovery and calibration foundation;
- `4eba1bb` — reject Foam tracks aliasing observed Oil;
- `bb52d24` — vectorize repeated Oil raster windows;
- `cdcfab3` — preserve Oil proposal capacity after user calibration;
- `976775d` — carry confirmed initial state through all-missing graphs; and
- `ccd16ba` — separate coincident Foam and Oil evidence;
- `1215a8c` — require drain motion before completed-fill reacquisition; and
- `e40a64b` — keep initial-state hold out of events and judgment;
- `1cdd650` — add exact R8 replay and user-calibration gates; and
- `a2519c4` — keep artifact raster proposal work outside the UI layer.

## Local replay

The exact R8 replay produced:

| sample | rows | numeric Oil | public Foam |
|---|---:|---:|---:|
| base_sample_1 | 30 | 19 | 0 |
| sample2 | 5 | 5 | 0 |
| sample3 | 151 | 42 | 5 |
| sample4 | 113 | 76 | 0 |
| total | 299 | 142 | 5 |

All numeric Oil rows have same-frame provenance. Checked user truth is numeric at
10/13 points with 5.85 px MAE and 11 px maximum error. Sample3 retains two early
Foam episodes and its 67 s black/reframe frame is UNKNOWN. Sample4's 25-frame
false Foam sequence is rejected as an Oil-boundary alias.
Sample3's 39–90 s completed-fill interval remains non-numeric; its moving upper
material cap no longer becomes a false maximum.

The reproducible manifest is
`sample/output/s11-r8-observation-recovery/replay_manifest.json` and the runner
is `tests/diagnostics/s11_r8_observation_recovery_replay.py`.

## User-like artifact calibration

At sample4 3.0 s, the UI-equivalent proposal list placed the visually reviewed
lower rim first: `r6_material_path`, source Y 884, normalized center
`(0.5192, 0.8269)`, width 0.4038 and height 0.0962. Selecting only that line
changed Oil coverage from 76/113 to 81/113. Public Foam stayed zero,
same-frame-provenance failures stayed zero and checked truth stayed 2/5 numeric
with 0.5 px MAE/max error.

The manifest is
`sample/output/s11-r8-artifact-calibration/artifact_calibration_manifest.json`.
This is evidence that the workflow can release candidate competition; it is not
permission to auto-accept proposals or to claim the same artifact on Windows.

## Performance

Python profiling of the same sample4 113-frame replay showed:

| measurement | before | after |
|---|---:|---:|
| total profile | 33.01 s | 20.35 s |
| detector cumulative | 27.31 s | 14.63 s |
| material-path generation | 8.61 s | 1.36 s |
| robust sector phase | 12.27 s | 6.81 s |

The optimization reduced detector cumulative time about 46%. Tracking content
was identical after removing run id. The remaining dominant cost is the legacy
spatial fallback; further architectural simplification is deferred until the R8
Windows result shows whether it still contributes necessary field recall.

## Repository gate

- Python compile: passed for `src` and diagnostic runners;
- patch whitespace: `git diff --check` passed;
- focused completed-fill/initial-state gate: 60 passed;
- UI boundary/proposal adapter gate: 20 passed; and
- full repository regression: 1,547 passed in 115.28 s.

## Status

Local implementation and replay are accepted. Secure-Windows R8 Base/Accum
validation, including calibration-off/on comparison and packaged performance,
is pending. No final field-performance claim is made.
