# S11-R17 Physical Observation Ownership Evidence

## Disposition

R17 is locally accepted and remains `WINDOWS_PENDING`. The exact private
Base/Accum field replay was not available in this checkout, so this evidence
does not claim field accuracy or close S11.

The corrected detector/runtime identity is
`opencv-phase-detector-r17-physical-observation-ownership-v2`; the sequence
resolver identity is `r17-physical-observation-ownership-v2`.

## Implemented replacement

Oil physical identity no longer receives initial-state or entrance-band input.
Tracklets measure their own direction and retain the best measured bounded
failure evidence instead of exporting default zeros. Initial EMPTY entry,
material completion and bounded re-entry remain owned by
`oil_phase_lifecycle.py`. A lost fill owner can transfer only to one distinct,
independently confirmed, directionally compatible and material-clean tracklet;
coordinates and extrema are never copied between IDs.

Foam time-only grouping and average-score acceptance were deleted. The episode
owner now builds bounded physical front tracks and requires registered dynamic
support plus front or component-extent evolution. Same-boundary Oil alias
rejection remains post-Oil, while valid Foam remains independent of Oil
availability. Projection and CSV contracts were not changed.

The implementation is carried by:

- `eca376a` — physical Oil identity and phase-state separation;
- `5891060` — physical Foam-front evolution;
- `d1b9fee` — R17 runtime identity; and
- `b20eed5` — final design correction after the rejected admission experiment;
- `63187d4` — checked-truth correction design and mandatory replay gate;
- `1d02943` — bounded drain ownership and continuing-anchor publication
  correction; and
- `006f08c` — R17-v2 identity plus the executable 13-case replay contract.

## Rejected implementation experiment

A row-diverse candidate-capacity replacement was implemented and tested, then
deleted. It displaced the reviewed sample3 bottom-entry owner: the first onset
row became unavailable, following rows moved from the reviewed Y≈316 corridor
to Y268–280, and a foreign branch reopened around 38–40 s. Restoring the
existing authority-ranked bounded beam returned both corpus contracts to PASS.
No dead row-diversity helper or fallback remains in production or tests.

This failure is retained because it repeats an S11 lesson: proposal diversity
cannot be increased by admitting weaker rows without a physical selection
contract. R17 therefore repairs ownership and episode identity only; it does
not claim to repair every Base proposal-recall gap observed on Windows.

## Checked-truth omission and correction

The first R17 acceptance ran the four qualification videos but did not call the
R14 `user_truth_audit`/`_aggregate_truth` contract. That was a validation gap.
Running it later produced only 6/13 numeric truth, 7.67 px MAE and 24.5 px
maximum error, and failed first on sample3 late-drain coverage (6 rows).

Code/trace review found two correctable ownership seams:

- a strong directionally correct drain successor was blocked by accumulated
  texture conflict even when current physical motion and a clean material
  anchor proved the row; and
- a Base same-frame candidate on an already continuing anchor trajectory was
  removed solely by the current-frame confidence seam.

R17-v2 adds typed alternatives for those two cases without changing global
thresholds. The drain alternative exists only after a drain phase has already
been established, and material rows still need a clean anchor-authoritative
material witness. The publication alternative requires a continuing
`ANCHOR_TRAJECTORY`, complete trajectory support and no current hard
contradiction. Initial release, same-row material veto, geometry, ambiguity and
same-frame projection contracts remain unchanged.

## Automated validation

- Oil/Foam owner and S11 lifecycle contracts: 138 passed;
- detector integration, controlled benchmarks and production cutover: 343
  passed;
- Foam-focused regression after preserving the reviewed second sample3
  episode: 45 passed;
- canonical repository suite: 1,644 passed in 152.83 s;
- Python compilation of `src` and `tests`: passed; and
- `git diff --check`: passed.

The R17 completed-window characterization fingerprint is
`92dae92fe7d420fe90c9fafcdd0690992ff4ea30c1dce122117a6e6a5cc382e1`.

## Checked four-video replay

The fixed 2 FPS qualification windows produced 299 rows and 162 numeric Oil
rows. Fingerprint regeneration was treated as a review event. The executable
R17 replay now runs the R14 truth audit as part of its acceptance contract.

| Sample | Rows | Numeric Oil | Foam episodes | Tracking fingerprint |
|---|---:|---:|---:|---|
| `base_sample_1` | 30 | 28 | 0 | `5879657ce71ced5970c13272867f61def7d7972195b5d264a3cf63c99f1122b7` |
| `sample2` | 5 | 3 | 0 | `decaea14a5cdb052333470702acd2bd10075e67fe4fc3835dc69e8cce2a57572` |
| `sample3` | 151 | 27 | 2 | `be3c94709e01ab952e9de94816f1ef10e1de5743080a7164ec929e2f96471f92` |
| `sample4` | 113 | 104 | 1 | `575dddcc1c5f51de915608a67b5f073421643f99553f14e12f71552e48f0e5cb` |

Checked truth is 8/13 with 9.0 px MAE and 24.5 px maximum error. Sample3 keeps
the foreign 34–39 s branch and completed-fill cap non-numeric, restores the
reviewed physical drain successor through 101.53 s, and increases numeric late
drain rows from six to twelve. Sample4 retains eight strict reviewed-range
matches. Every numeric Oil row retains same-frame provenance.

The five raw checked-truth abstentions remain visible in the manifest:

| Sample/time | Classification |
|---|---|
| `sample2` 0.0 s and 2.0 s | checked Oil truth conflicts with provisional no-interface review |
| `sample3` 34.5345 s | newer source review identifies Y≈243 as the foreign/opposite branch; safety abstention |
| `sample4` 0.0 s | no publishable same-frame proposal; unresolved proposal-recall miss |
| `sample4` 49.0 s | nearby tracklets have opposed direction/high material conflict; unresolved identity miss |

R14 reported 10/13, 8.5 px MAE and 26 px maximum error. R17-v2 therefore does
not claim raw coverage parity. It improves Base truth coverage and maximum
error while retaining the newer sample3 safety correction; the remaining
sample4 misses stay explicit rather than being filled by a conflicting row.

The reproducibility manifest is
`/tmp/s11-r17-corrected-final-audit/replay_manifest.json`. It is an ignored
local artifact; the durable counts, hashes and abstention set are recorded
above and in the checked diagnostic script.

## Performance

An exact-clean-head profile ran at
`006f08ce0523e240b56a3f2cce662ecc5a9b8c77` using sample4, 0–56 s, 2 FPS,
debug disabled, official static learning and bundle output. Three runs all
retained 113 rows, 104 numeric Oil and the sample4 fingerprint above.

| Measurement | R17 median |
|---|---:|
| End-to-end wall time | 11.646 s |
| Real-time factor | 0.208 |
| Detector mean latency | 64.009 ms/frame |
| Completed-window resolution | 0.2027 s |

This is faster than the first R17 median and is not a material performance
regression. The manifest is
`/tmp/s11-r17-v2-perf/performance_profile.json`.

## Remaining external gate

The next authority is a new private-Windows Base/Accum replay. It must report
Base Oil recovery at the reviewed 540/634/674 s anchors, zero Base Foam, Accum
initial-EMPTY suppression, real bottom-entry admission, truth-near continuity
including post-702 s reacquisition, the 52 reviewed real versus 50 reviewed
false Foam rows, and exact selected-candidate/sequence/CSV equality. Until that
passes, R17 is a locally accepted implementation rather than a field-qualified
detector.
