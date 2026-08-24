# S11-R17 Physical Observation Ownership Evidence

## Disposition

R17 is locally accepted and remains `WINDOWS_PENDING`. The exact private
Base/Accum field replay was not available in this checkout, so this evidence
does not claim field accuracy or close S11.

The corrected detector/runtime identity is
`opencv-phase-detector-r17-physical-observation-ownership-v3`; the sequence
resolver identity is `r17-physical-observation-ownership-v3`.

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
- `006f08c` — R17-v2 identity plus the executable 13-case replay contract;
- `3aeae2a` — authoritative checked-truth architecture and validation contract;
  and
- `54374fe` — bounded representation correction, transient current-anchor
  ownership and R17-v3 runtime identity.

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

## Checked-truth authority correction

The first R17 acceptance ran the four qualification videos but did not call the
R14 `user_truth_audit`/`_aggregate_truth` contract. R17-v2 added that audit but
then made a second authority error: it treated detector-internal phase/track
interpretation as permission to reclassify usable checked truth. The sample3
frame 1035/Y243 annotation was called a newer-reviewed foreign branch even
though the user truth had never changed. The sample2 endpoint truth was also
treated as subordinate to provisional no-interface review. Both conclusions
are withdrawn.

The 13 usable `.oiltruth` cases are product authority until a new user-reviewed
truth revision replaces them. Trace state, track direction, phase ownership and
provisional overlays can explain a miss but cannot redefine the annotation.

Code/trace review found two bounded ownership seams:

- sample2 2.0 s had a strong material anchor inside the normal spatial and
  prediction bounds, but a representation-class change split it from the
  established same-family track; and
- sample3 34.5345 s had an anchor-authoritative material-path row with strong
  registered motion at Y244, but its accumulated track direction disagreed
  with the active fill owner and prevented same-frame selection.

Two broader implementations were tried and deleted:

- bypassing both representation and stale-velocity checks recovered sample2
  but reduced sample3 to 11 numeric rows and removed the reviewed 100 s drain;
- adopting the sample3 current anchor into the persistent fill chain recovered
  Y243 but increased sample3 to 60 numeric rows and reopened the 37 s
  full-material barrier.

R17-v3 keeps the normal prediction bound and permits only a same-family,
anchor-authoritative, registered-motion representation correction. For the
sample3 seam, one clear current material anchor may transiently own the frame
inside gap-scaled phase geometry; it is recorded in that frame's owner chain but
does not mutate the accumulated phase chain. Ambiguity remains UNKNOWN, the
following gap stays empty, and the completed-material barrier remains closed.

## Automated validation

- focused owner, S11 continuity, detector integration, controlled benchmark and
  production-cutover suite: 417 passed in 65.03 s;
- focused completed-window characterization after explicit fingerprint review:
  3 passed;
- canonical repository suite: 1,646 passed in 153.23 s;
- Python compilation of `src` and `tests`: passed; and
- `git diff --check`: passed.

The R17 completed-window characterization fingerprint is
`40dcf6a2176fb580cca67a248ba3e9d0be521949f4eb15490f2c859a504c0bfa`.

## Checked four-video replay

The fixed 2 FPS qualification windows produced 299 rows and 162 numeric Oil
rows. Fingerprint regeneration was treated as a review event. The executable
R17 replay now runs the R14 truth audit as part of its acceptance contract.

| Sample | Rows | Numeric Oil | Foam episodes | Tracking fingerprint |
|---|---:|---:|---:|---|
| `base_sample_1` | 30 | 28 | 0 | `5879657ce71ced5970c13272867f61def7d7972195b5d264a3cf63c99f1122b7` |
| `sample2` | 5 | 4 | 0 | `85713bc131a808d81d073bec5bff8d035604cb4c1912ba6412c1b5c448fe4976` |
| `sample3` | 151 | 29 | 2 | `feb7e139269894b0aa86d692722acb4512e487dd0b71367fa88859e67745d5a1` |
| `sample4` | 113 | 101 | 1 | `bc3a61417c26a3b64e2d66a6cd836c66b45be3dbb17f602dcb1e5eb6b77f78c2` |

Checked truth is 11/13 with 9.6364 px numeric-only MAE and 24.5 px maximum
error. Missing truth is excluded from ordinary MAE, so the executable gate also
charges each miss a 24.5 px penalty: coverage-adjusted MAE improves from
14.9615 px for R17-v2's 8/13 baseline to 11.9231 px. Sample3 frame 1035 resolves
to Y244 for 1 px error; the following gap and 37–81 s material barrier remain
non-numeric; reviewed late drain still has twelve numeric rows and Y368 at
100.03 s. Sample4 retains eight strict reviewed-range matches. Every numeric
Oil row retains same-frame provenance.

The two remaining checked-truth misses remain visible in the manifest:

| Sample/time | Classification |
|---|---|
| `sample2` 0.0 s | no publishable same-frame physical owner at the first decoded frame |
| `sample4` 0.0 s | no publishable same-frame proposal; unresolved proposal-recall miss |

R14 reported 10/13, 8.5 px MAE and 26 px maximum error. R17-v3 therefore does
not define the current target or override checked truth. R17-v3 exceeds its raw
coverage by one case and lowers maximum error to 24.5 px, while numeric-only MAE
is 1.1364 px higher because the newly numeric sample4 49 s case contributes a
22 px error instead of being excluded as a miss.

The reproducibility manifest is
`/tmp/s11-r17-final-verified/replay_manifest.json`. It is an ignored
local artifact; the durable counts, hashes and remaining-miss set are recorded
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
