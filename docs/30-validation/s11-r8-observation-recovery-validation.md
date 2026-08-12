# S11-R8 Observation-Recovery Validation

## Local automated gate

Run focused Oil/Foam, calibration, initial-state, graph/report, benchmark and UI
tests, then the full repository suite. Compile `src` and diagnostics and require
`git diff --check` success.

Run:

```text
python -m tests.diagnostics.s11_r8_observation_recovery_replay
python -m tests.diagnostics.s11_r8_artifact_calibration_replay --proposal-index 0
```

The four-video gate requires 299 rows, 142 numeric Oil rows, 10/13 checked truth
points, detected-point MAE <= 5.85 px, maximum error <= 11 px and same-frame
provenance for every numeric point. Base/sample2/sample4 must publish zero Foam;
sample3 Foam must remain within the reviewed early episodes and its black/reframe
barrier must remain UNKNOWN. Its reviewed completed-fill interval from 39 to
90 s must not reacquire the moving upper material cap as a free interface.

The calibration replay models an actual UI choice: detector proposal 0 at
sample4 3.0 s is the visually reviewed lower rim, not the central Oil boundary.
It must improve or preserve Oil coverage, keep public Foam at zero, retain
same-frame provenance and not worsen checked truth.

Performance profiling uses sample4's 113 frames with debug disabled. Record
total detector and changed-function cumulative time before/after. Optimized
tracking rows must be identical after excluding run identity.

## Secure-Windows Base/Accum gate

Run the exact pushed R8 head twice per Glass:

1. existing Recipe with artifact calibration disabled; and
2. user-calibrated Recipe after reviewing detector proposals in the ellipse
   editor and selecting only persistent glare/rim/scratch structures.

Record the proposal screenshot/list, selected template id/kind/normalized
geometry, Recipe hash, video identity, analysis range, cadence and initial-state
confirmation. Do not auto-select all proposals.

For Base, require zero public Foam and verify acquisition near 540, 634 and
674 s against source frames. Compare Oil coverage, first-acquisition latency,
longest missing run and gross wrong-interface run before/after calibration.
Calibration passes only if an excluded artifact no longer wins while the real
Oil candidate at the same or nearby Y remains eligible outside the selected
geometry.

For Accum, verify Oil rise near 653 s, real Foam onset near 672 s, high near
685 s and recovery/observation near 689 s. Confirm Foam-texture no longer vetoes
Oil, dynamic continuation is bounded and public Foam appears for the confirmed
episode even when Oil/state is unavailable.

For both Glasses:

- every numeric Oil row has an eligible same-frame candidate;
- every public Foam row belongs to a confirmed dynamic episode;
- raw/rejected candidates and calibration ids remain traceable;
- initial-state graph hold creates no numeric Oil and is visibly labeled;
- events/extrema/captures use observed authority; and
- debug-disabled per-frame time is compared with R7 on the same Windows machine.

Any false Base Foam, long artifact Oil track, loss of real Accum Foam, or
calibration that removes the real Oil path is a field failure regardless of
coverage. Windows field status remains pending until this exact-head replay is
returned.
