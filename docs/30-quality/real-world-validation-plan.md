# Real-World Validation Plan

## Authority and scope

This document owns real-video, detector, Workbench, lifecycle, graph, CPU, memory and packaging acceptance obligations discovered during real use. It does not own milestone status or the active next action.

- Long-term milestone state: [project roadmap](../00-project/roadmap.md)
- Active S5-B gate: [current work plan](../00-project/work-plan.md)
- S5-B design: [oil-boundary hypothesis architecture](../20-architecture/s5b-oil-boundary-hypothesis-architecture.md)
- Manual platform procedure: [manual GUI and Windows checklist](./manual-gui-windows-checklist.md)
- Benchmark execution: [golden video regression](./golden-video-regression.md)

## Validation principles

1. Detector accuracy is the primary product risk.
2. Do not tune thresholds without user truth and category-balanced comparison.
3. Prefer bounded OpenCV/NumPy algorithms; no checkpoint or GPU runtime is required.
4. Low or conflicting evidence must remain reviewable rather than forcing a numeric boundary or Foam state.
5. A single video, filename or fixture ID cannot define an exception.
6. Accuracy evidence must be accompanied by CPU, memory, packaging and resource-cleanup evidence.
7. Automatic tests and manual Windows/real-video checks are reported separately.
8. The repository sample is supporting evidence only, never canonical truth.

## Evidence sources

Use the following evidence in descending order of truth authority:

1. user-confirmed/corrected `.oiltruth` annotations;
2. deterministic exported regression fixtures and catalog metadata;
3. controlled base/feature benchmark results from the same dataset/settings/environment;
4. manually reviewed real compressor sequences;
5. repository synthetic/sample probes for architecture and smoke evidence only.

## Detector dataset categories

The regression dataset should visibly cover:

1. clear oil boundary;
2. weak transparent-oil boundary;
3. transparent-oil full/no-interface;
4. transparent-oil agitation, shimmer and refractive motion;
5. real white Foam;
6. glare, reflection, blur and fogging;
7. structural horizontal edge, rim and paired line;
8. rapid oil fill/drain and compressor-start transient;
9. full and empty no-interface;
10. dropout, reacquisition and visible↔no-interface transitions.

Include both successful and failed detector cases. `unusable` truth remains counted by reason but is excluded from accuracy denominators.

## Required metrics

### Oil boundary

- raw and smoothed MAE in px;
- normalized error by effective Glass analysis height;
- median, P90 and P95 error;
- truth-present detection coverage;
- truth-absent false-boundary rate;
- full and empty no-interface false-boundary rates;
- fill-state accuracy;
- ambiguous/review-required rate with reason counts;
- reacquisition and dropout behavior by sequence.

### Foam non-regression

- Foam precision and recall;
- shimmer Foam false-positive rate;
- accepted Foam-front position error when truth exists;
- temporal persistence/rejection behavior;
- Glass-local state isolation.

### Operational

- median and tail per-frame CPU time with debug disabled;
- long-duration retained state and process memory;
- output/package size delta;
- one-folder startup and workflow on a non-CUDA office Windows PC;
- Unicode/long-path behavior;
- cancellation, close and file-lock cleanup.

## S5-B acceptance matrix

| Scenario | Required behavior |
|---|---|
| Clear/weak real boundary | Preserve numeric boundary with traceable broad/narrow evidence and acceptable error |
| Structural line or rim | Raise artifact likelihood without forcing a boundary |
| Real boundary near structure | Preserve both explanations and select only with sufficient evidence/margin |
| Glare/reflection | Keep visibility conflict explicit; do not convert candidate absence into no-interface |
| Full/empty no-interface | Return no numeric boundary and clear stale smoothing after the bounded transition |
| Ambiguous evidence | Return review/unknown behavior rather than a forced numeric position |
| One/multi-sample dropout | Do not display stale current numeric data; recover within bounded temporal rules |
| Rapid fill/drain | Permit bounded reacquisition without permanent jump rejection |
| Visible↔no-interface | Clear and reacquire state deterministically |
| Multiple Glasses | Keep static, temporal, polarity and smoothing state isolated |
| Foam/shimmer | Preserve accepted S5-A behavior under the same controlled dataset |

The feature and base comparison must use identical dataset bytes, benchmark catalog, detector settings, Python/runtime environment and execution mode. Non-comparable fingerprints invalidate the delta.

## Workbench and preflight acceptance

- Five progress steps remain readable at 1280 px and Windows 100%, 125% and 150% scale.
- Video canvas remains usable on a small laptop layout; transport controls have a distinct non-overlapping row.
- User-facing terminology follows `Glass`, `분석 영역`, `유면/유면 경계`, `거품` and optional real-length conversion.
- Settings-panel wheel events do not change values.
- Foam guidance provides interpretation and action without mutating Recipe state.
- Modeless preflight remains usable beside the Workbench, marks stale results and cleans up on close.

## Analysis lifecycle acceptance

The user sees six stages in order:

1. video analysis;
2. event/judgment calculation;
3. result image generation;
4. CSV and snapshot persistence;
5. graph and report generation;
6. bundle finalization.

Frame processing completion is not overall 100%. Completion is emitted only after atomic finalization. Cancellation during any pre-finalization stage leaves no completed bundle or debug staging directory. Closing the Workbench releases worker, video and output resources.

## Result visualization acceptance

- Korean titles, axes, legends, annotations and empty-state text render with an installed system font.
- User-facing series names use `유면` and `거품 경계`.
- Each Glass detail graph covers the full inner-ellipse analysis range and shows reference zero plus upper/lower analysis boundaries.
- Combined graphs cover the union of included Glass ranges.
- Missing/no-interface values remain gaps, never zero.
- Result Review, re-detection comparison and HTML report use the same range and font policy.
- Repeated open/close cycles release Matplotlib callbacks, figures and file handles.

## CPU and memory gate

Record base and feature measurements with debug disabled and identical inputs. Report hardware, OS, Python, package versions, Glass count, sampling settings and video duration.

Acceptance requires:

- no unbounded frame/candidate history;
- bounded per-Glass temporal/static state consistent with architecture limits;
- no material unexplained CPU regression after separating shadow-only instrumentation cost;
- stable long-duration process memory after warm-up;
- no dedicated-GPU or CUDA dependency.

Numerical thresholds are set by the controlled-comparison owner using the accepted baseline and must be recorded in the work-plan closeout, not duplicated in the roadmap.

## Windows and packaging gate

- Run the canonical suite on Python 3.14.
- Build the one-folder distribution on Windows.
- Run on a clean PC without Python or separately bundled font files.
- Complete Workbench, preflight, analysis and Result Review flow.
- Verify Jinja, Qt plugins, OpenCV and Matplotlib resources after relocation.
- Exercise Unicode/long paths, active file locking, cancellation and application close.
- Confirm no video/output/debug handle remains locked after close.

## Evidence reporting

Every validation closeout updates the [work plan](../00-project/work-plan.md) with exact head, dataset/settings fingerprint, result, completed scope, evidence location, findings, gate, next action and unresolved risks. A platform or video not actually exercised is reported as pending, never inferred from another environment.
