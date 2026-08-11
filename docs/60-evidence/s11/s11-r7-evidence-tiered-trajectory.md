# S11-R7 Evidence-Tiered Trajectory — Local Implementation Evidence

**Evidence disposition:** `LOCAL PASS — SECURE WINDOWS HOLDOUT PENDING`

## Implemented head

- R7 design commit: `e9f3851`
- production implementation and focused regression commit: `1380cf0`
- isolated checked-video replay tool commit: `62e57f7`
- explicit mid-Glass initial-state regression commit: `da2a3ec`
- detector version: `opencv-phase-detector-r7-evidence-tiered-v1`
- final observation version: `r7-evidence-tiered-trajectory-v1`

This record proves the checked-in local corpus and repository regression only.
The [work plan](../../00-project/work-plan.md) owns the remaining private-Windows
gate.

## Delivered responsibility changes

- Replaced the final R6 selected-candidate authority with explicit
  `HARD_INVALID`, `CANDIDATE_ONLY`, `CONTINUATION_ELIGIBLE` and
  `ANCHOR_ELIGIBLE` tiers.
- Removed current-frame `candidate.selected`, temporal reason, margin and tracker
  action from completed-analysis anchor authority.
- Required every public Oil coordinate to come from an eligible candidate in
  that same frame; missing rows remain missing.
- Added candidate-local, registered and exposure-compensated Oil raster change,
  independent from Foam motion.
- Added same-frame competing-partition handling, weak-member trend checks,
  fixed-track opposition with bounded dynamic relief and isolated-spike
  censoring.
- Required multi-frame registered material evolution for public Foam episodes;
  Foam remains unable to select, mask or veto Oil.
- Restored separate leading-prefix FULL/EMPTY interpretation from a current-run
  confirmed prior plus two compatible R7 anchor observations. It changes no raw
  sample, observed coverage or numeric coordinate.
- Restricted extrema, crossings, drop events and report captures to
  anchor-supported evidence.
- Consolidated terminal dark-cap topology in one shared module instead of
  layering another revision-specific rule branch.

## Repository validation

Commands completed on macOS in the source checkout:

```text
.venv/bin/pytest -q
1525 passed in 183.97s

.venv/bin/pytest -q \
  tests/unit/test_oil_observation_resolver.py \
  tests/unit/test_foam_episode_resolver.py \
  tests/test_temporal_raster_evidence.py \
  tests/test_initial_state_retrospective_reconstruction.py \
  tests/test_s11_sequence_observability_integrity.py \
  tests/test_s11_temporal_reacquisition_continuity.py \
  tests/test_oil_detector_integration.py \
  tests/test_foam_phase_detector_integration.py \
  tests/test_oil_controlled_benchmark.py \
  tests/test_foam_controlled_benchmark.py \
  tests/test_detector_benchmark_integration.py \
  tests/test_oil_production_cutover.py \
  tests/unit/test_events.py \
  tests/unit/test_report_presentation.py
425 passed in 79.97s

.venv/bin/python -m tests.diagnostics.s11_r7_evidence_tiered_replay \
  --output-root sample/output/s11-r7-evidence-tiered-qualification
PASS
```

The replay runs each video in a fresh process. A combined in-process
detector-plus-report run retained enough decoded/Matplotlib/OpenCV resources to
be terminated before sample3 in the constrained worker; process isolation makes
the validation resource boundary deterministic without changing detector code.

## Deterministic four-video replay

All inputs matched the hashes captured by the replay manifest. Generated bundles
remain ignored forensic output; the checked-in script, source videos, Recipes,
truth/provisional annotations and fingerprints are the reproducibility authority.

| Sample | Rows | Numeric Oil | Public Foam frames / episodes | Checked truth numeric | Detected-point MAE | Max error |
|---|---:|---:|---:|---:|---:|---:|
| `base_sample_1` | 30 | 13 | 0 / 0 | 2 / 3 | 10.0 px | 10.0 px |
| `sample2` | 5 | 5 | 0 / 0 | 3 / 3 | 5.5 px | 11.0 px |
| `sample3` | 151 | 28 | 3 / 2 | 2 / 2 | 5.0 px | 9.0 px |
| `sample4` | 113 | 62 | 0 / 0 | 2 / 5 | 0.5 px | 0.5 px |
| **Total** | **299** | **108** | **3 / 2** | **9 / 13** | **5.28 px** | **11.0 px** |

`108/299 = 36.1%` is publication density, not detector accuracy. Unclear,
no-interface, black/reframed and deliberately censored frames remain in the
denominator.

Tracking fingerprints:

| Sample | SHA-256 |
|---|---|
| `base_sample_1` | `ac7a4f0182145f89fbecd82fe5f2dfca81fb9f9b098148364aa32539c045df04` |
| `sample2` | `126464a910bca4d014adb26c3a7f9d902801408e64d249f6ea02d6d13a803852` |
| `sample3` | `59ce7b90d6ea253f16b422271bcff514cfb9b618fda95bec16024e50b352c338` |
| `sample4` | `b8ab53db8aa31db643ae9355924dfb8abd75a793797530ddcecaea376b5c1c44` |

Fingerprints detect unintended output drift. They are not truth and are not a
production branch.

## Direct-image and report reconciliation

- Every one of the 108 numeric Oil rows has
  `SEQUENCE_SAME_FRAME_CANDIDATE` provenance.
- Sample3's black/reframe frame near `67 s` is `UNKNOWN_REVIEW` with no Oil.
- Sample3 has no synthesized numeric Oil from `37.54` to `92.03 s`; the later
  drain is a separate observed run with at least 15 retained samples.
- Sample4 publishes no Foam, and the visually rejected lower-rim/internal
  partition timestamps at `2.5`, `3.0`, `7.5`, `9.5`, `18.5`, `19.0`, `20.0`
  and `35.5 s` are non-numeric.
- Sample4 has eight numeric provisional-visible checkpoints, six inside the
  exact annotated range and all eight inside the range with a 12 px visual
  tolerance.
- The four generated reports contain 20 captures and 22 landmarks. Extrema and
  lifecycle captures derive from R7 anchors rather than continuation-only
  points.

The causal frame review and remaining limitations are recorded in the
[R7 direct-image diagnostic](../../50-diagnostics/s11/s11-r7-checked-video-direct-image-reconciliation.md).

## Claim and next gate

Local R7 is safer and more physically coherent than the field-failed R5/R6
owners, but it is not a general accuracy claim. Important local gaps remain,
including conservative sample3 Foam/full publication and late sample4
reacquisition.

The release gate is an exact-head replay on the private Windows Base/Accum
workflow. Base must publish zero Foam and follow the real descent/recovery;
Accum must leave initial EMPTY when visible Oil enters, retain the bounded real
Foam episode and follow high/fall. A failure there reopens R7 rather than being
repaired downstream in the report.
