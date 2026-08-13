# S11-R9 Calibrated Observation Validation

## Local automated gate

Run focused UI, calibration, Oil/Foam resolver, trace, initial-state/report,
detector integration and benchmark tests, followed by the complete repository
suite. Compile `src` plus the diagnostic runners and require
`git diff --check` success.

Run the reproducible video gates:

```text
python -m tests.diagnostics.s11_r9_calibrated_observation_replay
python -m tests.diagnostics.s11_r9_artifact_calibration_replay
```

The uncalibrated four-video gate remains 299 rows, 142 numeric Oil, 10/13
checked truth, MAE <= 5.85 px and maximum error <= 11 px. Every numeric row
requires same-frame provenance. Base/sample2/sample4 public Foam remains zero;
sample3 retains the reviewed early Foam and its unclear/reframed 39–90 s span
remains non-numeric.

The user-like sample4 calibration must remain 81/113 numeric, public Foam zero,
checked truth 2/5 numeric with 0.5 px MAE/max error, and seven reviewed visual
matches. The exact counts are a local regression alarm, not a general-field
coverage target. A test must prove that a qualified existing path disables
calibrated bootstrap, while no-calibration, static and competing-path cases do
not gain authority.

Measure sample4 detector-only time over the same 113 frames with debug disabled,
both calibration off and on. Calibration overhead must remain bounded and must
not restore the pre-R8 Python-loop hot path.

## Secure-Windows UI gate

At 100%, 125% and 150% scale, open **분석 영역 편집** and verify:

- the settings/proposal area does not overlap the video at the target window
  size and both panes remain resizable/scrollable;
- single and multi-selected proposals visibly highlight the exact source
  point/line/region;
- **모든 후보 선택** selects the list and overlays;
- bulk Artifact apply creates only the selected normalized templates; and
- cancel/apply, Recipe dirty state and existing exclusion editing remain intact.

## Secure-Windows Base/Accum gate

Run the exact pushed R9 head on the same private Base/Accum inputs. Record SHA,
detector/resolver versions, video/Recipe identity, bounds, cadence and confirmed
initial states. For each Glass preserve an uncalibrated reference, then review
proposals and apply only visually persistent glare/rim/scratch artifacts. A
reviewed bulk selection is allowed; automatic unreviewed acceptance is not.

For Base, require zero public Foam and inspect source-frame Oil near 540, 634
and 674 s. Do not reuse the invalid ~660 or old-bundle 366/580/327 truth values.
Record whether a candidate exists within ±25 px of the reviewed source-frame Y,
whether calibrated high-recall generated it, whether dynamic seed activated,
first acquisition, longest missing run and longest wrong-interface run. Any
promoted static/competing path fails.

For Accum, inspect the rise near 653 s, distinct Oil/Foam layers near 672 s,
high near 685 s and later observation near 689 s. Oil and Foam may both be
public. A prior alias track may reject the new Foam episode only when the R9
trace shows new same-frame coincidence evidence.

Open `debug_trace.jsonl` and use the final `sequence` member rather than
source-code reverse calculation. Verify authority, trajectory, selection and
reject stage agree with `tracking.csv`. Every numeric Oil requires a selected
same-frame candidate; every public Foam requires a confirmed dynamic episode.

If Base still has no numeric Oil, its confirmed initial state must appear to
analysis end only as the labeled graph background with empty CSV Oil. Compare
debug-disabled frame time to R8 on the same machine. Coverage alone never
overrides wrong-interface, false-Foam or missing-real-Foam failure.
