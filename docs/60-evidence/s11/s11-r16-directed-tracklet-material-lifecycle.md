# S11-R16 Directed Tracklet and Material Lifecycle Evidence

## Disposition

R16 is implemented and passed the local structural, causal, provenance,
checked-video, performance and full-regression gates. This record supports an
independent audit of the exact committed candidate. It does not establish
private-field accuracy, supersede R15 as the field authority or close S11.

The validated runtime identity is:

- detector: `opencv-phase-detector-r16-directed-interface-tracklets-v1`;
- sequence resolver: `r16-directed-interface-tracklets-v1`; and
- semantic source/test commit: `ea866ba8f77f9ae49d3efa22d66f952bdd08aa3a`
  (the following documentation-only commit does not alter runtime behavior).

## Implementation result

R16 separates physical row identity, material-phase ownership, publication
eligibility and fixed-lag selection. Directed tracklets terminate ambiguous
merge/split assignments. The phase lifecycle publishes allowed physical IDs
before scoring, preserves distinct IDs across explicit handoffs and keeps the
filled barrier closed until a confirmed drain owner exists. Projection chooses
one deterministic publishable member of the selected same-frame row; it never
pools sibling confidence or carries a coordinate.

The initial visible-interface fill repair links only one unique immediate
predecessor to a later strong dynamic owner. The predecessor contributes owner
chain continuity but not observations, extrema, direction or coordinates.
Foreign branches, ambiguous handoffs, bounded owner loss and material conflict
remain `UNKNOWN`.

The former completed-fill reacquisition veto is absent. The resolver facade is
2,513 lines and `OilPathLifecycleOwner` is 162 lines, below their decomposition
guards of 2,700 and 260. The fixed-lag selector, directed tracklets and phase
lifecycle are separate modules.

## Exact four-video replay

The final local replay processed 299 rows with 164 numeric Oil rows:

| Sample | Rows | Numeric Oil | Tracking fingerprint |
|---|---:|---:|---|
| `base_sample_1` | 30 | 27 | `a784eb475ac29675f6e3369c2b5729f1aac7e7c6836d5fa5f679e081c52c9955` |
| `sample2` | 5 | 3 | `09c8451ac0d27ecbec81092a7da9a1137cf327bcc1fced2fbba0a00fd221e0b3` |
| `sample3` | 151 | 30 | `cdf8ab6598b9e04402fdb63179e250cee3e4deb3bc25bae2e226744671be20f0` |
| `sample4` | 113 | 104 | `a504337fa4338f6f03ccc742cbce55950251af2ddd4aa74ec859a82dbd010624` |
| **Total** | **299** | **164** | — |

Same-frame provenance violations were zero in every sample. Checked truth was
6/13 numeric with 7.667 px mean absolute error and 24.5 px maximum error.
Sample3 had zero numeric Oil in the reviewed 39--64 s completed-fill cap,
seven numeric rows in `90 <= t < 103` and ten at or after 90 s. The audited
97.030/97.531 s rows retained the lower physical owner at Y368/Y368.5 instead
of the unrelated upper branch. Sample4 retained 14/16 reviewed visible rows,
8/16 strict-range matches and 10/10 Foam checks; non-Foam samples had zero
false Foam.

Against the retained R15 replay, numeric deltas were Base `-3`, sample2 `0`,
sample3 `-13` and sample4 `-7` (`187 -> 164`). Candidate-level reconciliation
found the removed rows in owner ambiguity, completed-fill/cap, foreign-branch
or material-conflict windows. The detailed causes are preserved in the
[R16 owner audit](../../50-diagnostics/s11/s11-r16-local-coverage-owner-audit.md).

## Causality and boundedness evidence

The stage confirmation and selector/onset policies each use six sampled
frames. They do not imply a six-frame end-to-end commitment. A composed
counterexample first observes a dynamic owner at frame 3 and confirms it only
at frame 7: a prefix ending at target `t+6` differs in phase reason and owner
metadata. The repository-owned end-to-end horizon is 11 sampled frames, or a
12-frame inclusive envelope through `t+11`. A hostile suffix after `t+11`
cannot alter target Y, physical tracklet, phase, reason or owner chain.

Production-source inspection found no Base/sample identifiers, reviewed
timestamps, truth-Y names or audited Y243/Y316/Y368 coordinates in detector
owners.

## Automated validation

- focused tracklet, phase, resolver, debug, characterization and decomposition
  set: 121 passed in 0.57 s;
- evidence-specific sample3 onset/barrier/drain contracts: 2 passed in 24.13 s;
- canonical repository suite: 1,620 passed in 153.08 s;
- Python compilation of `src` and `tests`: passed;
- production hardcoding search: no matches; and
- `git diff --check`: passed.

The R16 characterization fingerprint is
`c5329baeb0c0dba257b8fe48761d54c7ca4c879427955202c7e0cf0bb9564578`.

## Performance evidence

The checked workload is sample4 from 0--56 s at 2 FPS, debug disabled, using
official static learning, completed-window resolution and bundle output. Three
runs all retained 113 rows, 104 numeric Oil and fingerprint
`a504337fa4338f6f03ccc742cbce55950251af2ddd4aa74ec859a82dbd010624`.

| Measurement | R16 median | Delta from R0 |
|---|---:|---:|
| End-to-end wall time | 11.717 s | -24.3% |
| Real-time factor | 0.209 | -24.5% |
| Detector mean latency | 64.323 ms/frame | -18.5% |
| Completed-window resolution | 0.2021 s | -90.2% |

Accuracy, abstention and provenance were not traded for the speed gains.
Private-Windows/package timing was not available locally.

## Reproducibility artifacts

- replay manifest:
  `/tmp/r16-post-lag-four-video.OMSSpf/replay_manifest.json`;
- performance manifest:
  `/tmp/r16-final-profile.6PA2Vs/performance_profile.json`; and
- final sample3 FULL trace:
  `/tmp/r16-final-s3-debug.nsi4W7/run-01/`.

These ignored local outputs are reproducibility aids, not checked-in truth.
The exact counts, fingerprints and behavioral assertions above remain the
durable evidence if the temporary files are removed.

## Unresolved external gate

Private-Windows Base/Accum replay was not available in this checkout. R15
therefore remains the field authority. R16 still requires an independent audit
of the exact committed head before push and then a replay of that pushed head
with the saved Recipes and Artifact templates. Oil accuracy, Accum initial
EMPTY false-positive suppression, real bottom-entry admission, Foam
publication and CSV equality remain separate external checks.
