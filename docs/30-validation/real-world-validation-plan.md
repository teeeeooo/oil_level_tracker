# Real-World Validation Plan

## Authority and scope

This document owns real-video, detector, Workbench, lifecycle, graph, CPU, memory and packaging acceptance obligations discovered during real use. It does not own milestone status or the active next action.

- Long-term milestone state: [project roadmap](../00-project/roadmap.md)
- Active gate and next action: [current work plan](../00-project/work-plan.md)
- S5-B design: [oil-boundary hypothesis architecture](../20-architecture/s5b-oil-boundary-hypothesis-architecture.md)
- S11 current detector gate: [S11 real-field detector effectiveness contract](s11-real-field-detector-effectiveness.md)
- Manual platform procedure: [manual GUI and Windows checklist](../40-operations/manual-gui-windows-checklist.md)
- Benchmark execution: [golden video regression](golden-video-regression.md)

## Validation principles

1. Detector accuracy is the primary product risk.
2. Do not tune detector thresholds without user-confirmed/corrected truth. Category-balanced real-video comparison remains the preferred acceptance evidence when representative acquisition is feasible.
3. If the domain owner records further representative real-video acquisition as externally infeasible, bounded detector repair may proceed only against the audited available corpus and its frozen regression dataset; base/feature comparison must keep dataset bytes, catalog, settings and runtime environment identical.
4. Categories absent from that available corpus remain explicit residual validation gaps and their metrics remain `not_evaluated`/unavailable; available-corpus repair cannot establish category-balanced or general-field detector-accuracy PASS.
5. Prefer bounded OpenCV/NumPy algorithms; no checkpoint or GPU runtime is required.
6. Low or conflicting evidence must remain reviewable rather than forcing a numeric boundary or Foam state.
7. A single video, filename or fixture ID cannot define an exception.
8. Detector/runtime acceptance evidence must include CPU, memory and resource-cleanup evidence; the Windows packaging baseline was accepted in S10 and is revalidated proportionally only when later changes materially invalidate it.
9. Automatic tests and manual Windows/real-video checks are reported separately, and Windows PASS is never inferred from another platform.
10. The repository sample is supporting evidence only, never canonical truth.

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
- User-facing terminology follows `Glass`, `분석 영역`, `유면/유면 경계` and
  `거품`. Workbench provides no real-length conversion editor; legacy
  `mm_per_pixel` data remains read-compatible only.
- Settings-panel wheel events do not change values.
- Foam guidance provides interpretation and action without mutating Recipe state.
- Current-scene guidance contains status, observed state, position and at most
  one concrete action; generic `핵심 내용` / `다음 행동` narration is absent.
- Initial-state confirmation survives analysis-end, compressor, sampling,
  detector-setting and presentation changes that do not alter the video,
  analysis start, selected initial state or enabled-Glass set; its visible
  question uses user-facing labels rather than serialized enum names.
- Shared transport keeps playback controls separate from a full-width seek bar
  and supports frame, ±5/±10-second and direct-time movement.
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

- Korean titles, axes, external graph controls, annotations and empty-state text render with an installed system font.
- User-facing series names use `유면` and `거품 경계`.
- Each Glass detail graph covers the full inner-ellipse analysis range and shows reference zero plus upper/lower analysis boundaries.
- Combined graphs cover the union of included Glass ranges.
- Missing/no-interface values remain non-numeric and are never converted to zero, CSV samples or overlay positions.
- Oil rendering uses solid segments for consecutive finite observed anchors and dashed graph-only bridges across missing runs. Each bridge uses only its stored endpoints while restrained UNKNOWN/no-interface indication exposes the intervening evidence state; an all-missing Oil series stays empty.
- Foam rendering preserves intermittent gaps and does not connect across absent Foam observations.
- Static reports label observed highest/lowest Oil and bounded physical landmarks, embed Glass-focused source captures and keep raw debug/event volume outside the main narrative.
- Result Review, re-detection comparison and HTML report use the same range and font policy.
- Result Review defaults to major physical events, preserves access to every
  stored event, and uses compact markers without persistent per-event text.
- General and Debug navigation/detail surfaces remain separate; raw trace data
  is collapsed and candidate comparison uses the bounded five-column summary.
- Repeated open/close cycles release Matplotlib callbacks, figures and file handles.

## CPU and memory gate

Record base and feature measurements with debug disabled and identical inputs. Report hardware, OS, Python, package versions, Glass count, sampling settings and video duration.

Acceptance requires:

- no unbounded frame/candidate history;
- bounded per-Glass temporal/static state consistent with architecture limits;
- no material unexplained CPU regression from the production typed-hypothesis pipeline and its bounded instrumentation;
- stable long-duration process memory after warm-up;
- no dedicated-GPU or CUDA dependency.

Numerical thresholds are set by the controlled-comparison owner using the accepted baseline and must be recorded in the work-plan closeout, not duplicated in the roadmap.

## S5-C canonical and Qt lifecycle gate

The canonical test process has one application owner: the session-scoped `qapp`
fixture in `tests/conftest.py`. Its default `qapp_cls` is pytest-qt's
`QApplication`; `QCoreApplication.instance()` therefore resolves to that same object
once GUI tests begin. A separate `QCoreApplication` process is not used because the
Qt Core/value and QObject-only tests do not require an application instance.

`QT_QPA_PLATFORM=offscreen` is injected only while the test `QApplication` is first
constructed and is then restored. Tests requesting `qapp` or `qtbot` are marked
`qt_app` during collection. pytest-qt owns registered-widget close/delete teardown.
Before that close step, the repository teardown hook gives an ordinary registered dirty
`MainWindow` a teardown-only `Discard` response so test cleanup cannot block on the
production S9-A modal. Tests whose subject is unsaved-close behavior still exercise
Save / Discard / Cancel and rejected-close lifecycle explicitly; production close logic
is not bypassed. Each controller test continues to own its worker-thread shutdown.

After registered widgets close, the repository fixture verifies that no visible top-level
widget or global `QThreadPool` task remains; it does not force-delete QObjects, quit
threads or drain deferred deletes globally. The canonical command remains
`python -m pytest`. The focused diagnostic command is `python -m pytest -m qt_app`;
it selects the same acceptance tests and is not an additional duplicate pipeline
obligation. Headless non-interactive subprocess tests receive an explicit source-tree
`PYTHONPATH`, UTF-8 child I/O, closed stdin, and no Qt platform variable, so their import
contract does not depend on editable installation, host text locale, inherited pytest
capture handles or prior GUI test order.

S5-C acceptance requires both GUI-before-headless and headless-before-GUI focused
orders to pass. Process isolation is introduced only if direct evidence later proves
that incompatible application classes are required; broad suite serialization and
per-test GUI subprocesses remain prohibited.

## S7 annotated-MP4 source-tree gate

S7 is accepted historical implementation evidence. Any future change that materially invalidates the annotated-MP4 owner must continue to prove that selected-Glass export covers only the saved analysis interval, queries final tracking state with actual decoded timestamps, preserves numeric gaps, and uses stored debug trace only on the exact matching decoded frame. The export remains a derivative artifact outside the official bundle and original source video.

Failure and cancellation evidence must show bounded temporary-file cleanup plus deterministic reader/writer/debug-resource release. Result Review integration must keep encoding off the GUI event loop, preserve playback/viewer state, and stop export-owned work safely on Viewer close. Completed S7 evidence is preserved under [`../60-evidence/s7/`](../60-evidence/s7/); later proportional revalidation must not reinterpret the old macOS/source-tree evidence as a new Windows result.

## Final Windows and packaging release gate

S10 completed this gate on the accepted release baseline: Windows canonical, supported-DPI GUI, PyInstaller one-folder build/relocation, clean-PC execution, resources/fonts, Unicode/long paths and cancellation/file-lock/application-close obligations were directly exercised and accepted.

A post-S10 packaging maintenance repair now owns deterministic Windows Qt platform bootstrap inside the PyInstaller GUI artifact. The custom runtime hook runs before PyInstaller package runtime hooks and the GUI entry script, forces `QT_QPA_PLATFORM=windows` only on Windows packaged startup, and does not become a source-tree or CLI/headless dependency. The packaged application must therefore start without a user/system QPA prerequisite and must override a conflicting inherited QPA value rather than accept it as authority.

Future source work does not automatically rerun the entire S10 gate. Re-execute only platform/package evidence materially invalidated by the changed owner or release input, and never infer Windows behavior from another platform.

## Evidence reporting

Every completed validation closeout records exact head, dataset/settings fingerprint, result, completed scope, evidence location, findings and unresolved risks under [`../60-evidence/`](../60-evidence/) or another explicitly owned evidence artifact. The [work plan](../00-project/work-plan.md) retains only the current decision-bearing baseline and next action. A platform or video not actually exercised is reported as unavailable/not-run for that evidence, never inferred from another environment.
