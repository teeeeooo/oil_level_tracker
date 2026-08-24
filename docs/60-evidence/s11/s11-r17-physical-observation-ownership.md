# S11-R17 Physical Observation Ownership Evidence

## Disposition

R17 is locally accepted and remains `WINDOWS_PENDING`. The exact private
Base/Accum field replay was not available in this checkout, so this evidence
does not claim field accuracy or close S11.

The detector/runtime identity is
`opencv-phase-detector-r17-physical-observation-ownership-v1`; the sequence
resolver identity is `r17-physical-observation-ownership-v1`.

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
- `b20eed5` — final design correction after the rejected admission experiment.

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

## Automated validation

- Oil/Foam owner and S11 lifecycle contracts: 138 passed;
- detector integration, controlled benchmarks and production cutover: 343
  passed;
- Foam-focused regression after preserving the reviewed second sample3
  episode: 45 passed;
- canonical repository suite: 1,639 passed in 153.43 s;
- Python compilation of `src` and `tests`: passed; and
- `git diff --check`: passed.

The R17 completed-window characterization fingerprint is
`33d9b6733abaca0485aaa4836a5d6a51e93bc144ad6e89af9ee2d962817b7a05`.

## Checked four-video replay

The fixed 2 FPS qualification windows produced 299 rows and 155 numeric Oil
rows. Fingerprint regeneration was treated as a review event; counts and the
reviewed sample3 safety assertions were checked before recording them.

| Sample | Rows | Numeric Oil | Foam episodes | Tracking fingerprint |
|---|---:|---:|---:|---|
| `base_sample_1` | 30 | 27 | 0 | `6cc4478bf93b83911b111d261ba610a8ac3a1f220829a35036a504e48e9814f8` |
| `sample2` | 5 | 3 | 0 | `decaea14a5cdb052333470702acd2bd10075e67fe4fc3835dc69e8cce2a57572` |
| `sample3` | 151 | 21 | 2 | `f9d7dae6bcf43f290c7668dbed4efbec91da69831d59418910cf896b95b868e0` |
| `sample4` | 113 | 104 | 1 | `575dddcc1c5f51de915608a67b5f073421643f99553f14e12f71552e48f0e5cb` |

Oil counts match the repaired R16 local stream. Sample3 preserves both reviewed
dynamic Foam episodes at 30.53–32.53 s and 37.04–38.04 s, keeps the foreign
34–39 s branch and completed-fill cap non-numeric, preserves same-frame drain
witnesses through 96.53 s, and rejects the unsafe later re-entry. The first R17
Foam implementation rejected the second real episode because an absolute
component-width change was too strict; using relative component evolution
restored it without reopening the constant-glare unit cases.

The reproducibility manifest is
`/tmp/s11-r17-replay-final.80kTMm/replay_manifest.json`. It is an ignored local
artifact; the durable counts and hashes are recorded above.

## Performance

An exact-clean-head profile ran at
`b20eed5fd30ff2fa0cd8ba6043111cd1f1e2374c` using sample4, 0–56 s, 2 FPS,
debug disabled, official static learning and bundle output. Three runs all
retained 113 rows, 104 numeric Oil and the sample4 fingerprint above.

| Measurement | R17 median |
|---|---:|
| End-to-end wall time | 11.818 s |
| Real-time factor | 0.211 |
| Detector mean latency | 64.569 ms/frame |
| Completed-window resolution | 0.2031 s |

This is approximately 1% above the recorded R16 end-to-end median and is not a
material performance regression. The manifest is
`/tmp/s11-r17-perf.XzPlTY/performance_profile.json`.

## Remaining external gate

The next authority is a new private-Windows Base/Accum replay. It must report
Base Oil recovery at the reviewed 540/634/674 s anchors, zero Base Foam, Accum
initial-EMPTY suppression, real bottom-entry admission, truth-near continuity
including post-702 s reacquisition, the 52 reviewed real versus 50 reviewed
false Foam rows, and exact selected-candidate/sequence/CSV equality. Until that
passes, R17 is a locally accepted implementation rather than a field-qualified
detector.
