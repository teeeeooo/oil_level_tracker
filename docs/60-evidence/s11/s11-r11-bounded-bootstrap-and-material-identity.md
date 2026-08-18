# S11-R11 Bounded Bootstrap and Material Identity Evidence

## Result

R11 completed the activated detector-debt reset and the two evidence-backed
behavior repairs. The exact local head passes repository, replay, calibration,
same-frame provenance and runtime gates. Private Windows Base/Accum accuracy is
still pending and remains the release gate.

## Structural reset

Five production-unreachable selectors and their obsolete behavior tests were
removed after the production-cutover guard proved absence:

- `candidate_generators.py`;
- `candidate_scorer.py`;
- `oil_candidate_consensus.py`;
- `oil_no_interface.py`; and
- `oil_temporal_path.py`.

The change removed 3,489 source/test lines. Candidate evidence and authority
are now named modules with explicit tier, reason and failed-gate trace fields.
R6/R8/R9 candidate-family assembly moved out of `OpenCvPhaseDetector.detect`,
and Foam material identity and immutable sequence row types have independent
owners. `opencv_phase_detector.py` fell from 1,081 to 892 lines and
`oil_observation_resolver.py` from 2,718 to 2,614 lines; remaining global-path
and run-bound logic stays a later cohesion target rather than being moved during
the correctness change.

Before intentional behavior changes, four-video replay remained exactly R10:
299 rows, 142 numeric Oil and all four tracking fingerprints unchanged.

## R11 behavior

Calibrated bootstrap now splits excessive motion-keyframe gaps and promotes
only the first/last locally distributed keyframes plus a two-frame edge. It
requires at least two keyframes, local span/direction, minimum member count and
keyframe density. A regression fixture proves two late keyframes cannot promote
a 100-frame prefix.

Eligible Foam fronts now seed an observation-only material identity. Nearby
continuous material-path rows inherit candidate-local opposition even after
public Foam disappears. The track cannot publish coordinates or state. A
material-path candidate on that track is candidate-only, while a sufficiently
separated calibrated lower boundary is reserved and may receive the explicit
`foam_distinct_lower_boundary` authority reason. Registered dynamic material
authority additionally requires `material_texture_conflict < 0.50`; other
material anchor routes use their own conflict bound.

Trace output again exposes `authority`, `authority_reason`, failed gates,
candidate-local Foam-material opposition and selected-candidate opposition.
Frame-level Artifact rejection count is explicitly separate from the selected
candidate's match.

## Local replay

The reproducible uncalibrated R11 runner produced:

| sample | rows | numeric Oil | public Foam |
|---|---:|---:|---:|
| base_sample_1 | 30 | 19 | 0 |
| sample2 | 5 | 5 | 0 |
| sample3 | 151 | 40 | 5 |
| sample4 | 113 | 65 | 0 |
| total | 299 | 129 | 5 |

Every numeric Oil row has exact same-frame candidate provenance. Checked truth
is numeric at 10/13 points with 5.95 px MAE and 11 px maximum error. Sample4
numeric rows remain inside the reviewed padded trajectory band, and sample3's
reviewed changing-focus/unclear interval remains conservative.

The manifest is
`sample/output/s11-r11-bounded-material-identity/replay_manifest.json`; the
runner is
`tests/diagnostics/s11_r11_bounded_material_identity_replay.py`.

## User-like Artifact replay

Selecting proposal 0 at 3.0 s, as the user does in the Artifact editor,
increased sample4 Oil coverage from 65 to 92/113. Checked truth improved from
2/5 to 3/5 numeric with 4.0 px MAE and 11 px maximum error; reviewed visual
matches increased to eight. Same-frame provenance remained complete.

Ten Foam points appeared in two episodes at 39.5–47.0 s after the old Oil alias
no longer suppressed them. These candidates have width 0.56–0.63, fill
0.45–0.62 and registered internal/dynamic motion at 1.0 on most confirmed
frames. Local visual truth labels this interval `unclear`, so this is retained
as explicit Windows-review evidence, not claimed as correct Foam.

The manifest is
`sample/output/s11-r11-artifact-calibration/artifact_calibration_manifest.json`;
the runner is `tests/diagnostics/s11_r11_artifact_calibration_replay.py`.

## Runtime and repository gate

Three direct runs over the same decoded 113 sample4 frames included official
three-frame static learning and excluded seek/report/debug finalization:

| calibration | runs (s) | median | mean/frame |
|---|---|---:|---:|
| off | 4.855, 4.859, 4.851 | 4.855 s | 43.0 ms |
| on | 4.967, 4.966, 4.976 | 4.967 s | 44.0 ms |

This is below the R10 local reference of 7.062/7.182 s and shows no material
runtime regression on this machine.

- focused R11 authority/resolver/detector gate: 402 passed;
- full repository regression: 1,524 passed in 117.55 s;
- exact four-video R11 replay: passed;
- exact user-like Artifact replay: passed;
- Python compile: passed; and
- `git diff --check`: passed before documentation closeout.

## Remaining gate

Run the exact pushed R11 head on private Windows Base/Accum. Base must not
reproduce the 583-frame lower-structure path. Accum must keep residue Y191–297
out of Oil while retaining a separately evidenced lower interface near Y450.
The sample4 calibrated Foam episodes require direct visual classification.
Coverage alone is not acceptance.
