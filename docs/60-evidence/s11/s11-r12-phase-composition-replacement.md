# S11-R12 Phase/Composition Replacement Evidence

## Disposition

R12 is implemented and passed the local architecture, replay, provenance,
runtime and repository gates. This authorizes exact-head secure-Windows
Base/Accum replay; it does not establish field accuracy or close S11.

R12 replaces the failed R11 policies. It does not add a second version branch
above them. Motion-only calibrated bootstrap, `foam_distinct_lower_boundary`
authority, unbounded Foam-material continuation, material-mask-bottom topology
veto and shared Oil/Foam graph validity are absent from the final policy.

## Structural and implementation result

The preceding behavior-neutral audit removed 251 lines of confirmed unused
Vision compatibility code. Candidate policy now consumes typed evidence with
explicit phase, optics, artifact, motion and material-texture availability.
Missing evidence cannot satisfy an anchor gate as measured zero.

Oil high-recall proposals retain bounded family admission, but motion and user
calibration cannot create identity. A rapid row change may reacquire only at an
independent same-frame phase anchor backed by strong representation agreement;
anchor-free motion paths remain non-numeric. Foam/residue identity expires by
age, missing duration and drift, applies across candidate families, and cannot
turn vertical separation into Oil authority.

Foam admission accepts a wide coherent layer or a narrower component with
registered dynamic material evolution. Episode linking uses elapsed time and a
bounded motion envelope. Composition uses the ordered fronts rather than the
bottom of a broad raw material mask. CSV and review data now carry
`oil_is_valid` and `foam_is_valid`; legacy `is_valid` retains Oil/state meaning.

## Checked-video replay

The isolated four-video replay processed 299 rows:

| sample | rows | numeric Oil | public/graph-valid Foam |
|---|---:|---:|---:|
| base_sample_1 | 30 | 19 | 0 |
| sample2 | 5 | 5 | 0 |
| sample3 | 151 | 40 | 5 |
| sample4 | 113 | 69 | 0 |
| total | 299 | 133 | 5 |

All 133 numeric Oil rows have an equal-Y selected same-frame candidate. Combined
checked user truth is 10/13 numeric with 5.95 px mean absolute error and 11 px
maximum error. Sample3 retains the reviewed rise anchor at Y245 for Y243 truth,
then preserves its checked drain; its 38.04–90.02 s unclear/focus-change span
remains non-numeric. Sample4 has no reviewed-trajectory range failures under the
existing ±15 px visual audit band.

The accepted fingerprints and manifest are produced by
`tests/diagnostics/s11_r12_phase_composition_replay.py` at
`sample/output/s11-r12-phase-composition/replay_manifest.json`.

## User-like Artifact replay

The sample4 proposal workflow found ten candidates and selected proposal zero,
a normalized line template centered at `(0.5192, 0.8269)`. Reanalysis produced
82/113 numeric Oil, zero Foam, complete same-frame provenance, 2/5 checked truth
at 0.5 px MAE/maximum error, seven strict reviewed-range matches and eleven
finite points inside the padded visual band. Calibration rejected matching
geometry only; it did not create anchor authority for an unmatched row.

The runner is
`tests/diagnostics/s11_r12_artifact_calibration_replay.py`; its manifest is
`sample/output/s11-r12-artifact-calibration/artifact_calibration_manifest.json`.

## Runtime gate

Three direct runs over the same decoded 113 sample4 frames included official
three-frame static learning and excluded video seek, report and debug output.
The R11 baseline was rerun from exact commit `9a39311` in the same session.

| head | detector median | resolver median | total median | mean/frame |
|---|---:|---:|---:|---:|
| R11 baseline (`9a39311`) | 7.072 s | 0.898 s | 7.969 s | 70.5 ms |
| R12 implementation | 7.107 s | 1.085 s | 8.203 s | 72.6 ms |

Total runtime increased 2.9%. Detector work increased 0.5%; the typed completed
window resolver increased 0.187 s over 113 frames. This is not a material
interactive regression and R12 adds no full-frame image pass inside the
resolver. The older R11 evidence's 4.855 s absolute timing was not reused as a
cross-session ratio because the same unchanged R11 head measured 7.969 s in the
current environment.

## Repository gate

- focused authority/trajectory/Foam/composition gate: 122 passed;
- full repository regression: 1,526 passed in 117.27 s;
- exact four-video replay: passed with fixed counts and fingerprints;
- exact user-like Artifact replay: passed;
- Python compile: passed; and
- `git diff --check`: passed before closeout.

## Remaining gate

Replay the exact pushed R12 head on private Windows Base/Accum with the saved
reviewed Artifact templates. Base must not publish the former Y724–873
reflection/bracket path or false Foam and must be evaluated separately for
actual-interface candidate recall at 540/634/674 s. Accum must keep residue
Y190–297 out of Oil, retain independently evidenced lower Oil near Y450, publish
the rapidly rising confirmed Foam front with its own validity and avoid treating
the broad raw mask bottom as topology truth. Coverage alone is not PASS.
