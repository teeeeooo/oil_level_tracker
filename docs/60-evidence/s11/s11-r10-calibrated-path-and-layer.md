# S11-R10 Calibrated Path and Layer Evidence

## Incorporated private-Windows evidence

The exact R9 secure-Windows replay still produced Base 0/601 numeric Oil after
reviewed Artifact calibration. Of 5,221 initial continuation candidates, 5,002
survived track opposition, but only 288 passed the old per-candidate
motion-coverage gate, 27 retained local cluster/cross-representation support
and none formed a six-frame trajectory. At reviewed 540/634/674 s checkpoints,
nearest R9 candidate error was 46/16/84 px respectively.

Accum confirmed five Foam frames and wrote them to `tracking.csv`, but isolated
line-only graph values were invisible while `is_valid=False`. Two more real
Foam rows at 219/218 px were 17 px above selected Oil at 236/235 px and were
rejected because Foam identity reused Oil temporal jump tolerance. The full
operator-transferred analysis is preserved in the
[R9 Windows diagnostic](../../50-diagnostics/s11/s11-r9-windows-calibrated-observation-diagnostic.md).

## Implementation

R10 keeps one generic detector/resolver and introduces:

- a horizontal, user-resizable Artifact editor with first-view primary actions,
  visible proposal selection and reviewed bulk application;
- bounded vertically distributed calibration proposals;
- a calibration-only sparse motion-keyframe bootstrap with path-level span,
  direction, competition and exact-provenance checks;
- signed Oil/Foam layer identity independent of Oil temporal jump;
- a bounded strong-candidate alias screen only when public Oil is unavailable;
  and
- point markers for isolated finite Foam in static and interactive graphs.

Detector version is `opencv-phase-detector-r10-calibrated-path-and-layer-v1`;
Oil and observation-sequence resolver version is
`r10-calibrated-path-and-layer-v1`.

Logical commits before documentation closeout:

- `dcbcd62` — define R10 design/validation and record R9 Windows cause;
- `dce24ba` — make Artifact calibration first-view usable;
- `588accf` — recover sparse calibrated Oil paths;
- `961201e` — preserve separated Foam and visible graph evidence;
- `76bfff8` — distinguish real Foam layers from inverted/unresolved aliases;
  and
- `e0d2dbb` — establish R10 versions and reproducible replay gates.

## UI evidence

The Artifact editor was rendered at 980×700. The horizontal splitter measured
602/350 px and all primary Artifact actions were visible without scrolling.
The dialog has a resize grip, maximize affordance, 980×650 minimum and
1280×800 default size. The related first-view, selection, bulk-apply and layout
tests passed (12 tests).

## Uncalibrated four-video replay

The exact R10 replay retained the accepted numeric/state safety corpus:

| sample | rows | numeric Oil | public Foam |
|---|---:|---:|---:|
| base_sample_1 | 30 | 19 | 0 |
| sample2 | 5 | 5 | 0 |
| sample3 | 151 | 42 | 5 |
| sample4 | 113 | 76 | 0 |
| total | 299 | 142 | 5 |

Every numeric Oil row has same-frame provenance. Checked truth is numeric at
10/13 points with 5.85 px MAE and 11 px maximum error. Sample3's reviewed
unclear/changing-focus 39–90 s span remains missing. The five existing sample3
Foam rows now carry explicit separated-layer provenance without changing their
coordinates or states.

The manifest is
`sample/output/s11-r10-calibrated-path-and-layer/replay_manifest.json`; the
runner is
`tests/diagnostics/s11_r10_calibrated_path_and_layer_replay.py`.

## User-like Artifact calibration replay

Selecting the reviewed sample4 lower-rim proposal at 3.0 s changed Oil coverage
76→81/113. Public Foam remained zero, checked truth remained 2/5 numeric with
0.5 px MAE/max error, and reviewed visual matches remained seven. The manifest
is `sample/output/s11-r10-artifact-calibration/artifact_calibration_manifest.json`;
the runner is `tests/diagnostics/s11_r10_artifact_calibration_replay.py`.

## Oil/Foam layer and graph gate

Focused tests prove that a dynamic Foam layer at 219/218 px remains public
above selected Oil at 236/235 px even with `temporal_max_jump_px=64`. A strong
unselected duplicate cannot erase this public pair. Inverted public topology
and repeated unresolved strong Oil candidates remain rejectable through their
separate bounded rules. Foam publication does not change Oil provenance.

Static and interactive graphs now render every finite Foam value as a point,
including isolated values on invalid/unknown samples, while retaining missing
gaps. The focused Foam/graph gate passed 22 tests. Local sample4 still produced
zero public Foam after the direction-aware alias correction.

## Performance

Direct debug-disabled detector timing used the same 113 decoded sample4 frames,
official three-frame static learning and the reviewed 3.0 s proposal:

| calibration | R9 total | R10 total | R10 mean/frame |
|---|---:|---:|---:|
| off | 7.146 s | 7.062 s | 62.5 ms |
| on | 7.296 s | 7.182 s | 63.6 ms |

This short local diagnostic excludes video seek, report, capture and debug
finalization. It shows no material R10 per-frame regression, but does not replace
same-machine secure-Windows measurement.

## Repository gate

- R10 detector/version integration gate: 341 passed;
- Foam/graph focused gate: 22 passed;
- exact uncalibrated and user-like calibrated replay contracts: passed;
- full repository regression: 1,562 passed in 114.78 s;
- Python compile: passed; and
- `git diff --check`: passed before documentation closeout.

## Status

R10 implementation and local evidence pass. Secure-Windows Base/Accum replay on
the exact pushed head remains the field gate; no private-field or general-field
accuracy claim is made.
