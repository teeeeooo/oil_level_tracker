# Manual GUI and Windows Acceptance Checklist

This document owns manual GUI, real-video, Windows and packaging obligations. It does not own milestone status; use the [roadmap](../00-project/roadmap.md) and [current work plan](../00-project/work-plan.md).

## Workbench and video
- Launch the packaged app on a 100%, 125%, and 150% Windows display scale.
- At 1280 px window width, verify all five Workbench progress steps remain identifiable on one line without overlap or clipping.
- On a small laptop display, verify the center video remains large enough to edit the selected Glass.
- Verify the video canvas and transport bar have a clear boundary and never overlap during resize.
- Open MP4, MKV, AVI and MOV samples supported by the deployed OpenCV backend.
- Verify play/pause, step, seek and 0.5×/1×/1.5×/2×/4× behavior.
- Verify start/end/compressor markers numerically through session fields and report.
- Verify Korean labels do not clip or wrap awkwardly at 100%, 125%, and 150% display scale.

## Glass and analysis region editor
- Add three Glass items and alternate selection.
- Confirm the current-scene detection summary remains readable above the Glass list without hiding its add/delete/copy actions.
- Open **분석 영역 편집** and drag the ellipse from center; confirm it cannot leave the frame.
- Resize with left/right/top/bottom/corner handles; confirm minimum size and no inverted geometry.
- Drag the zero line to top/bottom and confirm it remains inside the ellipse.
- Add, move, resize and delete multiple exclusion rectangles.
- While dragging and resizing an exclusion, confirm the selected Glass ellipse geometry remains unchanged unless the ellipse itself is intentionally manipulated.
- Verify stored `.oilrecipe` coordinates match source pixels after window resizing.
- Scroll the settings panel while the pointer is over spin boxes and combo boxes; confirm values do not change and the panel continues scrolling.
- Verify keyboard arrows, direct entry and arrow buttons still edit wheel-safe controls.
- Toggle **실제 길이 환산 — 선택 사항** off/on and confirm px-only operation, valid mm display and saved `None` behavior.
- Confirm Foam guidance separates detection interpretation and recommended action.
- Use **초기 상태 설정으로 이동** and confirm the selected Glass remains selected, the initial-state field receives focus and the Recipe is not changed automatically.

## S9-B Workbench zoom, pan and fit
- At 100%, 125% and 150% Windows display scale, open a small sight-glass scene and confirm **확대**, **축소**, **맞춤** and **100%** remain visible without reducing the canvas below a usable editing area.
- Confirm the initial Workbench frame and every actual video/Profile context replacement enter Fit mode with the complete source frame visible at the correct aspect ratio.
- Use **확대**/**축소** and `Ctrl`+wheel on the canvas; confirm scale changes smoothly while ellipse, zero-line and exclusion overlays remain registered to the same source-frame coordinates.
- In a zoomed view, drag with the middle mouse button to pan and confirm ordinary left-button ellipse move/resize, zero-line drag and exclusion move/resize remain unambiguous.
- Seek, step and play through multiple frames while manually zoomed/panned; confirm the same-context view transform is retained rather than returning to Fit on every frame.
- Resize the Workbench while Fit is active and confirm the frame refits to the viewport. Repeat while manually zoomed and confirm the manual scale is preserved instead of collapsing back to Fit.
- Replace the current test video, load/new a Profile, and enter the same-Profile new-video workflow; confirm the old context transform is discarded and the replacement starts in Fit.
- At high zoom, edit all eight ellipse resize directions plus ellipse position, zero line and exclusion geometry; save/reload and confirm persisted coordinates still match source pixels with existing minimum-size and frame-bound rules.
- Exercise zoom/pan/fit without editing geometry and confirm Profile dirty state, undo/redo availability, Analysis Session values, readiness/preflight state and saved Result data do not change.
- Scroll the settings panel over spin/combo controls after using canvas zoom shortcuts and confirm its wheel-safe behavior still prevents accidental value changes.
- Open **분석 영역 편집** and the wizard/video preview consumers and confirm their frame display and existing private-copy/apply/cancel behavior remain intact.

## S9-C field ↔ overlay interaction polish
- At 100%, 125% and 150% Windows display scale, focus center X/Y, width and height controls; confirm the selected ellipse is clearly the active geometry target while the selected Glass identity remains visible.
- Focus the zero-line and margin controls; confirm only the corresponding zero line or inner detection margin receives the stronger active affordance and the ellipse remains the selected Glass geometry.
- Add at least two exclusion zones, select each list entry in turn and confirm the exact matching rectangle is highlighted with no cross-zone ambiguity.
- Click/drag/resize the ellipse, zero line and each exclusion overlay; confirm the settings panel reveals the matching geometry/zero-line/exact-exclusion context without repeatedly stealing keyboard focus during drag.
- Trigger existing error and warning validation on a field that is also an active interaction target; confirm validation border/meaning remains visible and first-issue routing/focus still works.
- Cause benign preview/validation/panel refreshes while geometry, margin, zero-line and an exclusion are active; confirm the same target is rebound after overlay rebuild without resetting the current manual zoom/pan transform.
- Change the selected Glass, then add/delete exclusions; confirm old Glass targets and deleted exclusion ids are cleared rather than highlighting stale overlays or list entries.
- Exercise highlight-only field/overlay interaction without changing values and confirm Profile dirty truth, undo/redo count, Analysis Session, readiness/preflight and detector state do not change.
- Inspect the normally selected ellipse at Fit and high zoom: confirm all eight resize directions remain available but handle markers are restrained circular affordances rather than dominant squares.
- At each Windows display scale, acquire all eight resize handles comfortably; confirm the small visual marker still has a practical hit target, active resize handle is obvious, minimum size/frame bounds hold and saved source-pixel coordinates remain accurate.
- Repeat the shared-canvas check in **분석 영역 편집** and wizard/video preview consumers; confirm consumers that do not provide an active target retain their existing display and ROI private-copy/Apply/Cancel behavior.

## Multiple-point preflight
- Open the modeless **여러 시점 점검** window and confirm the Workbench video geometry does not shrink.
- Resize the preflight window and its result table columns.
- Operate the Workbench and preflight window at the same time.
- Run, cancel and rerun without duplicate signal handling.
- Select a result row and confirm the Workbench selects the correct Glass and seeks to the correct timestamp.
- Change profile, video, analysis time, Glass or detector settings and confirm the prior result becomes stale.
- Close and reopen the preflight window; confirm the last result/stale state is retained appropriately.
- Close the Workbench while preflight is open or running; confirm the window closes and no video file lock or orphan process remains.

## Initial-state confirmation and retrospective reconstruction — post-implementation obligations
- With a populated saved Profile, start a new analysis session and confirm final analysis remains blocked until every enabled Glass has an explicit current-run initial-state confirmation; a loaded/copied/default value alone must not count.
- Confirm `AUTO` cannot satisfy final-analysis readiness.
- Explicitly confirm `UNKNOWN_REVIEW` for a genuinely indeterminate initial scene; confirm final-analysis readiness may proceed while no retrospective FULL/EMPTY interpretation is granted from that prior.
- Confirming an unchanged selected initial state must not by itself dirty the reusable Profile.
- Replace the video, prepare a same-Profile new video, change analysis start, change the selected initial-state value, enable an unconfirmed Glass, and establish a new analysis session; each material context change must invalidate only the affected current-run confirmation authority as specified by the product contract.
- Run preflight with unresolved confirmation and verify it can inspect the setup without silently establishing user confirmation.
- Exercise both GUI and available programmatic/headless final-analysis paths and confirm they enforce equivalent confirmation authority.
- Review a result with accepted retrospective FULL/EMPTY and confirm the original observed state, including observed `UNKNOWN_REVIEW`, remains separately visible.
- Confirm retrospective state exposes accepted/unresolved/conflict provenance and that conflict routes to review rather than rewriting observation.
- Confirm missing numeric Oil remains absent from samples and overlays. In graphs, verify consecutive finite observations use solid segments, a missing-run connection uses a dashed endpoint-only bridge, no retrospective FULL/EMPTY anchor is fabricated, and observed `UNKNOWN_REVIEW`/no-interface bands remain visible between anchors.
- Open a legacy v1 observed-only bundle in the new reader and confirm its original meaning remains readable; verify a v1-only consumer does not silently present a newer retrospective-semantics bundle as ordinary v1.
- In re-detection, confirm CURRENT/local scope cannot silently rebuild the initial sequence without full leading context, while a full-sequence rerun keeps its retrospective provenance separate from the saved official result.
- For an R7 result, confirm at least two anchor-grade observations with compatible
  direction can infer the leading FULL/EMPTY prefix while raw detector rows,
  observed coverage and numeric Oil remain unchanged. Continuation-only evidence
  must not confirm the prior.

> Retrospective acceptance cases above exercise legacy/current-frame compatibility.
> They do not authorize detector-sample rewriting and do not execute or approve
> the final Windows field-workflow check.

## Preview/debug
- Rapidly scrub seek bar and verify only latest preview appears.
- Change margin, confidence, Canny and foam settings and verify preview refresh.
- Inspect all six debug tabs and candidate reject reasons.
- Export selected-frame debug artifacts and open every PNG/CSV/JSON.

## S5-A Foam and transparent-oil discrimination
- Validate real diffuse white Foam, low-light Foam and partial Foam fronts against user-recorded truth.
- Validate transparent-oil agitation, refractive shimmer and heat-haze-like motion without Foam.
- Include compressor startup immediately after energizing, when fluid motion is fastest.
- Include clipped glare, moving Glass reflection, blur and fogging.
- Run Glass 1, 2 and 3 independently and together; verify Foam temporal state never crosses Glass boundaries.
- Verify a one-sample transient shimmer is rejected and sustained Foam remains accepted.
- Verify a moving Foam front remains continuous within the configured jump limit and a discontinuous jump restarts persistence.
- In Workbench preview and modeless preflight, inspect Foam decision flags without changing the official Recipe unintentionally.
- Run full analysis, then inspect Foam whiteness, texture, glare-excluded, combined-evidence and accepted-component images in Result Review debug.
- Run partial re-detection with changed Foam settings and confirm every additive setting appears in the comparison.
- Record user truth for representative Foam and shimmer scenes and run the external S1 benchmark dataset.
- Measure median Windows CPU frame time with debug disabled and compare against the accepted exact-head baseline.
- Run a long-duration 1–3 Glass analysis and confirm memory remains bounded and no frame history accumulates in the Foam gate.
- Build and run the one-folder package on a general office Windows PC without CUDA or any GPU-compute runtime dependency.
- Repeat with Unicode and long paths, active file locking, cancellation and application close; confirm video/output/debug resources are released.

### S11-R7 secure Base/Accum holdout

- Record the exact R7 commit, source/package identity, private video hash or
  approved internal identity, matching Recipe identity, sampling window/cadence
  and initial-state confirmations before comparison. The tested source must match
  the exact pushed head named by the [current work plan](../00-project/work-plan.md).
- Review original source frames, configured-ROI overlays, tracking CSV, events and
  `report.html` together. Aggregate valid coverage or state distribution alone is
  not an oracle.
- For every numeric Oil row, confirm an eligible same-frame candidate and
  `SEQUENCE_SAME_FRAME_CANDIDATE` provenance. Verify no coordinate is carried,
  interpolated or projected from the initial state through an unavailable frame.
- Separate image-supported state, `R7_OIL_ANCHOR`, `R7_OIL_CONTINUATION`,
  unavailable and retrospectively inferred prefix counts. Initial FULL/EMPTY
  interpretation must not count as observed detector coverage or create a
  numeric coordinate.
- On Base, verify direct review still shows no Foam and require zero public Foam
  frames/episodes. Confirm initial FULL is context only, then verify the real
  top-entering descent, lowest observed point and recovery are acquired without
  following the persistent glare/caustic row.
- On Accum, verify EMPTY is retained only while the image supports no interface.
  Confirm acquisition of the rising Oil boundary before the former mid-Glass
  lock-in, the bounded turbulent Foam episode, the highest observed point and the
  later fall.
- For Base and Accum, record first-acquisition latency after each visually clear
  entry, longest missing run, longest gross-wrong-interface run, public Foam
  frames/episodes and image-supported versus context-only state duration.
- Inspect raw/rejected/pending Foam around every public episode. Confirm rejected
  or static Foam-like glare is never resurrected by the episode resolver and
  never masks, selects or vetoes Oil. A raw high Foam score alone is not a public
  Foam observation.
- For the earliest accepted Oil before/through each physical transition, capture
  the source frame with configured ellipse, zero line, final Oil and public Foam
  guides. Record source Y and `zero_line_y - source_y`; do not diagnose direction
  from the sign alone without checking the overlay.
- Compare visual rise/fall/high/low/Foam transition times with stored events and
  captures. Do not backdate an event through missing observations. Confirm report
  extrema and captures come only from observed samples.
- Open `report.html` and verify solid observed runs, dashed display-only bridges
  across missing Oil samples, gap-preserving Foam and no line outside observed
  endpoints. Dashed bridges must add no CSV value, event, capture guide or cursor
  coordinate.
- Treat any Base public Foam episode, Accum EMPTY lock-in through visible Oil, or
  long fixed-glare/caustic Oil track as a field failure regardless of nominal
  coverage. Preserve the earliest source frame, overlay and relevant evidence;
  do not respond by globally lowering Foam/Oil/ambiguity thresholds.
- Record the result as new R7 evidence. Do not rewrite the historical R4/R5/R6
  evidence documents or compare against their exact output fingerprints as a
  pass criterion.

### S11-R8 secure Base/Accum observation recovery

- Record the exact pushed R8 SHA, detector/resolver versions, private video and
  Recipe identities, analysis bounds, cadence and current-run initial-state
  confirmations.
- Run each Glass first with artifact templates disabled. Then open the ellipse
  editor, run **Detector 후보 찾기**, inspect proposals against source frames and
  select only persistent glare/rim/scratch geometry. Save the proposal list,
  selected template ids/kinds/normalized coordinates and calibrated Recipe.
  Never accept every proposal automatically.
- Repeat the identical analysis with calibration enabled. Compare numeric Oil,
  first acquisition, longest missing run, longest wrong-interface run, public
  Foam, event/capture timing and debug-disabled frame time. Coverage alone is
  not a pass criterion.
- Confirm `R8_CALIBRATED_ARTIFACT_REJECTED` and
  `calibrated_artifact:<template-id>` appear for matching candidates, raw
  candidate scores remain inspectable and the same Y outside the selected
  horizontal geometry is not excluded.
- Confirm selected artifacts do not consume the ordinary candidate budget. A
  real Oil candidate competing with an artifact must remain in the completed
  sequence and may gain coverage; if all candidates are excluded the frame must
  remain `UNKNOWN_REVIEW`.
- On Base, require zero public Foam and inspect 540 s descent, 634 s low and
  674 s recovery. The chosen Oil path must not follow the calibrated glare,
  rim or scratch.
- On Accum, inspect 653 s rise, 672 s real Foam onset, 685 s high and 689 s
  observation. Confirm Foam texture does not veto Oil, real dynamic Foam is
  public even when Oil/state is unavailable, and Foam/Oil alias rejection does
  not remove the distinct real Foam layer.
- For every numeric Oil row require an eligible same-frame candidate and
  `SEQUENCE_SAME_FRAME_CANDIDATE`. For every public Foam row require a confirmed
  dynamic episode. Inspect alias and topology flags independently.
- If no Oil is observed for the entire window, confirm the user-confirmed
  FULL/EMPTY initial state is drawn to analysis end only as the labeled
  **확정 초기 상태 유지 가정** background. CSV numeric Oil and observed coverage
  must remain empty/unchanged.
- Compare debug-disabled median/total frame time with R7 on the same machine.
  Record detector time separately from video seek, report and capture time.
- Treat false Base Foam, a persistent artifact Oil path, lost real Accum Foam,
  calibration that suppresses actual Oil, or unlabeled initial-state projection
  as field failure regardless of aggregate coverage.

### S11-R9 secure Base/Accum calibrated observation

- Record the exact pushed R9 SHA, detector/resolver versions, private video and
  Recipe identities, analysis bounds, cadence and current-run initial-state
  confirmations. Preserve the R8 result as the comparison baseline.
- At 100%, 125% and 150% Windows scale, open **분석 영역 편집** and resize the
  window. Confirm the scrollable lower settings pane never overlays the video
  and the splitter keeps both panes usable.
- Run detector proposals. Click one, Ctrl/Shift-select several and use
  **모든 후보 선택**; confirm every selected point/line/region is highlighted
  on the source image and deselection removes only its highlight.
- Use **선택 후보 일괄 Artifact 지정** only after reviewing the selection.
  Confirm exactly those normalized templates are added and Apply/Cancel, Recipe
  dirty state, undo/redo and exclusion geometry remain correct. Select-all is
  not permission to accept an actual Oil boundary blindly.
- Run both Glasses without templates, then with the reviewed artifact set.
  Record proposal/template geometry, numeric Oil, public Foam, first acquisition,
  longest missing and wrong-interface runs, events/captures and debug-disabled
  detector time.
- On Base, review source-frame overlays near 540, 634 and 674 s. Record the exact
  reviewed Y and all candidates within ±25 px. Do not reuse the invalid ~660
  detector row or old-bundle 366/580/327 values as R9 truth.
- For any Base recovery, inspect `r9_calibrated_high_recall_candidate_count`,
  `r9_calibrated_dynamic_seed`, authority, cluster and trajectory. Bootstrap
  must remain absent when an ordinary qualified path exists and must reject a
  static or similarly strong competing path. Require zero public Base Foam.
- On Accum, inspect 653 s rise, the distinct Oil/Foam layers near 672 s, the
  high near 685 s and later observation near 689 s. Confirm both separated
  coordinates may be public and stale alias history alone does not reject Foam.
- In each captured `debug_trace.jsonl` record, keep top-level raw current-frame
  evidence separate from the final `sequence` member. Confirm sequence Oil Y,
  authority, trajectory, selected bit and reject stage match `tracking.csv`.
- Require same-frame candidate provenance for every numeric Oil and a confirmed
  dynamic episode for every public Foam. Missing frames must not receive carried
  or interpolated coordinates.
- If a Glass has zero Oil observations, verify only the labeled **확정 초기 상태
  유지 가정** graph background reaches analysis end. CSV Oil, observed coverage,
  extrema, events and captures must remain unmodified.
- Treat overlap/clipping, invisible selection, wrong bulk application, a long
  artifact path, false Base Foam, lost distinct Accum Foam, or material Windows
  performance regression as failure regardless of aggregate coverage.

### S11-R10 secure Base/Accum calibrated path and layer

- Record the exact pushed R10 SHA, detector/resolver versions, private video,
  Recipe/template identities, analysis bounds, cadence and confirmed initial
  states. Preserve R9 results as the comparison baseline.
- At 100%, 125% and 150% scale open **분석 영역 편집**. At first view confirm
  video is left, Artifact guidance/actions are right, **Detector 후보 찾기** and
  bulk actions are visible without scrolling, and resize/maximize plus both
  splitters remain usable at the minimum window size.
- Find proposals, exercise single/multiple/select-all selection and verify the
  exact point/line/region highlights. Apply only reviewed proposals and confirm
  precisely those templates persist; automatic detector acceptance is invalid.
- Replay Base with the reviewed templates. Around 540, 634 and 674 s record the
  reviewed source Y, nearest calibrated candidates, `r10_calibrated_path_member`,
  `r10_calibrated_motion_keyframe`, authority/trajectory and first reject stage.
  Record first acquisition, numeric coverage, longest missing and wrong-path
  runs. Require zero public Base Foam and reject static/wrong-path coverage.
- Replay Accum and inspect Oil rise, Foam onset, separated layers, highest Oil
  and recovery independently. Every confirmed finite Foam row must be visible
  in CSV and as a graph point even when `is_valid=False` or adjacent rows are
  missing.
- For any Foam alias rejection record Foam Y, exact public/strong Oil Y,
  signed `OilY - FoamY`, effective identity tolerance and branch. A positive
  separated layer above tolerance must retain both rows; inverted or
  near-coincident topology may be rejected. Oil temporal jump is not identity.
- Match final `sequence` trace to `tracking.csv`, graph, events and captures.
  Require exact same-frame provenance for numeric Oil and a confirmed dynamic
  episode for public Foam. Do not accept carried/interpolated coordinates.
- If Oil remains all-missing, confirm only the labeled **확정 초기 상태 유지
  가정** background reaches analysis end. CSV Oil, observed coverage, extrema,
  events and captures must remain empty/unchanged.
- Compare debug-disabled detector total/mean time with R9 on the same Windows
  machine. Treat hidden controls, wrong selection, false Base Foam, lost Accum
  Foam, a wrong Oil path or material runtime regression as field failure.

### S11-R11 secure Base/Accum bounded path and material identity

- Record the exact pushed SHA and confirm detector version
  `opencv-phase-detector-r11-bounded-bootstrap-and-material-identity-v1` and
  sequence resolver version `r11-bounded-bootstrap-and-material-identity-v1`.
- Reuse the R10 private videos, Recipe/template identities, bounds, cadence and
  confirmed initial states. Do not redraw truth from detector overlays.
- On Base, inspect 540, 634 and 674 s plus the complete 480–777.5 s window.
  Record `r10_calibrated_motion_keyframe`, `r10_calibrated_path_member`,
  `authority_reason`, failed gates and every numeric run. The two late R10
  keyframes must not promote the old 583-frame lower-structure prefix.
- On Accum, inspect actual Oil near Y450 and the Foam/residue track Y191–297.
  Record `r11_foam_material_identity`, distinct-lower reserve, authority reason,
  selected source/Y and first reject stage. Residue must not become public Oil;
  separately evidenced lower Oil must remain admissible.
- Record Foam and Oil independently around onset, highest Oil, disappearance
  and recovery. A public Foam row requires a confirmed dynamic episode; an Oil
  row requires exact same-frame candidate provenance.
- In Artifact-calibrated replay, classify the sample4-like wide/dense dynamic
  Foam episodes by direct video review. Do not accept or reject them merely
  because R10 Oil-alias behavior differed.
- Report Base/Accum numeric coverage, longest missing run, wrong-interface run,
  public Foam count, checked point errors, events/captures and debug-disabled
  mean frame time. Coverage alone is never PASS.

### S11-R12 secure Base/Accum phase/composition replacement

- Record the exact pushed SHA and confirm detector version
  `opencv-phase-detector-r12-phase-composition-replacement-v1` and sequence
  resolver version `r12-phase-composition-replacement-v1`.
- Reuse the private Base/Accum videos, bounds, cadence, confirmed initial states
  and saved reviewed Artifact templates. Do not redraw truth from a selected
  detector row or mix source and ROI-local coordinates.
- On Base inspect 540, 634 and 674 s, plus the former late Y724–873 run. For the
  nearest actual-Oil and selected candidates record evidence availability,
  authority reason, representation/semantic support, trajectory, final
  selection and first reject stage. Registered motion alone must never establish
  a path; require zero public Base Foam.
- On Accum inspect the actual lower Oil near Y450, Foam front, and former residue
  Y190–297 independently from onset through disappearance. Record bounded Foam
  material identity age/row/opposition, selected authority and whether the lower
  Oil candidate survived admission. Vertical separation alone is not authority.
- For Foam record raw, dynamic-narrow/wide eligible, episode-confirmed, CSV
  finite and graph-valid counts. Confirm rapid rising-front jumps may stay in one
  bounded episode without inventing coordinates in missing frames.
- Compare `foam_y` directly with `oil_y` for composition. A broad raw material
  mask or `material_component_bottom_y` crossing Oil is diagnostic only and must
  not invalidate otherwise ordered fronts. Reversed or near-coincident fronts
  remain reviewable conflicts.
- Confirm `oil_is_valid` and `foam_is_valid` in CSV and graph independently.
  Confirmed Foam may be visible when Oil/state is unresolved; invalid Foam must
  not affect Oil events, extrema, captures or judgment.
- Match every numeric Oil/Foam row to exactly one selected same-frame candidate
  in final `sequence`. Missing rows must remain missing. Record longest missing
  and wrong-interface run, event/capture agreement and debug-disabled detector
  and resolver time separately.
- Treat any long Base reflection/bracket Oil path, Accum residue-as-Oil path,
  false Base Foam, lost dynamic Accum Foam, shared-validity graph loss or material
  runtime regression as failure regardless of aggregate coverage.

## S5-B oil boundary and temporal tracking
- Validate a real, visually clear oil boundary and a weak transparent-oil boundary against user-recorded truth.
- Validate transparent-oil agitation, shimmer and heat-haze-like motion without forcing a numeric boundary.
- Validate structural horizontal lines, Glass rim, glare and reflection separately and together with a real oil boundary.
- Include low lighting, blur and fogging; verify conflicting evidence produces review rather than a forced position.
- Validate full no-interface and empty no-interface scenes; raw and smoothed numeric positions must remain blank.
- Validate rapid filling, rapid draining and the immediate compressor-startup transient without permanent jump rejection.
- Validate one-sample and multi-sample oil-boundary dropout; a missing current sample must not display a stale smoothed number.
- Insert a deliberately misleading strong line, then verify bounded recovery to the true oil path.
- Validate visible-to-no-interface and no-interface-to-visible transitions, including stale smoothing removal and bounded reacquisition.
- Run Glass 1, 2 and 3 independently and together; verify oil path, smoothing, polarity and reacquisition state remain isolated.
- Exercise Workbench preview, modeless preflight, full analysis and partial re-detection with the same representative scenes.

### Legacy pre-cutover inspection
- Before S5-B2 cutover, inspect the current production path's consensus source support, signed contrast/polarity, static overlap, no-interface decision, path margin, tracker update and reacquisition metrics to understand legacy behavior.
- Treat these legacy metrics as cutover-context and compatibility/debug evidence only; they are not the acceptance owner for the new typed hypothesis pipeline.

### S5-B1 typed foundation evidence
- Inspect immutable raw-observation identity and provenance from source evidence through every derived view.
- Inspect proposal Y span/diameter, members per proposal and total proposal count.
- Confirm proposal construction does not create a transitive-chaining bridge between otherwise separate evidence groups.
- Inspect broad region-step evidence separately from narrow line/pulse evidence.
- Inspect continuous boundary likelihood, continuous artifact likelihood and ambiguity likelihood with its reason.
- Inspect the soft static-prior contribution and confirm it does not erase contradictory current evidence.
- Inspect typed boundary, no-interface, ambiguous and unavailable projection outcomes.
- Inspect raw-observation, proposal, hypothesis and temporal-state resource counts and confirm each remains bounded.

### S5-B2 cutover audit
- Confirm the typed hypothesis pipeline exclusively owns production oil selection, no-interface and temporal decisions.
- Confirm official `PhaseDetection`, candidate rows and debug metrics are one-way projections from the accepted typed temporal decision.
- Confirm legacy generator, consensus, scorer, no-interface and `OilTemporalPath` metrics or state do not exercise production selection authority or provide fallback.

### Cross-stage validation
- Record user truth and run an external S1 regression dataset containing real oil boundary, reflection, structure, no-interface, dropout and rapid-flow categories.
- Measure Windows CPU median and long-duration memory with debug disabled; compare against the accepted exact-head baseline and verify bounded path state.
- Build and run the Windows one-folder package on a general office PC with an integrated/basic GPU and with no CUDA or dedicated GPU compute runtime.
- Repeat with Unicode and long paths, active file locking, cancellation and application close; confirm video, output and debug resources are released.

## Analysis lifecycle and cancellation
- Run 1-, 2- and 3-Glass analyses with a long real compressor video.
- Confirm the dialog displays all six stages in order: 영상 분석, 이벤트와 판정 계산, 결과 이미지 생성, CSV와 snapshot 저장, graph와 보고서 생성, bundle 마무리.
- Confirm frame analysis completion remains below overall 100% and stages 2–6 stay visible.
- On a slow disk, confirm graph/report and bundle-finalization progress remains visible rather than appearing frozen.
- Cancel separately during each of the six stages and confirm no completed bundle is exposed before atomic finalization.
- Confirm cancellation or failure removes the temporary result directory and debug staging directory.
- Confirm the completion dialog appears only after the final result directory and manifest are visible.
- Cancel immediately before finalization, then test a late cancel after finalization; confirm only the pre-finalization case is discarded.
- Close the Workbench while analysis is running and confirm the worker thread exits without an orphan thread, process, video lock or output lock.
- Exercise a long Unicode output path and a deeply nested Windows path.
- Open report offline with network disconnected.
- Confirm full/empty rows have blank numeric levels in CSV.
- Open Result Review from a Foam/review case and use **사용자 정답으로 확인**; confirm Glass, frame and timestamp context are retained and the official result bundle is unchanged.

## Result visualization
- Open Result Review on Windows with Malgun Gothic available and verify Korean title, axes, legend, annotations and empty-state text.
- Open the partial re-detection comparison and verify Korean graph labels and table headers: 공식/재검출 유면 and 공식/재검출 거품 경계.
- Open the offline HTML report and verify every combined/detail graph renders Korean text without repeated missing-glyph warnings.
- Verify negative y-axis tick labels and minus signs remain readable.
- Test Glass 1–3 with different ellipse positions, vertical radii, margin ratios and zero-line positions.
- Confirm each Glass detail graph includes the full inner-ellipse analysis area, 기준선 0 and both analysis boundaries even when observed values occupy a narrow band.
- Confirm exclusion rectangles do not reduce the graph's full vertical analysis range.
- Verify a Glass with valid `mm_per_pixel` uses mm on its detail graph and a px-only Glass stays in source pixels.
- Verify a mixed-scale combined graph remains in px and covers the union of all included Glass analysis ranges.
- Verify full/empty no-interface data and all-missing Oil series never become zero-valued lines or synthetic points.
- On an intermittent Oil series, verify Result Review and generated report show one readable path through the same stored finite anchors: direct consecutive observations are solid, edges crossing missing samples are dashed, and the intervening UNKNOWN/no-interface bands remain visible while cursor/overlay values stay absent at missing samples.
- Verify intermittent Foam remains gap-preserving and is not connected across absent Foam observations.
- In `report.html`, verify the main Glass section explains the observed start/end movement and marks the observed highest/lowest Oil; it must not foreground raw enum/confidence/debug rows.
- Verify each highest/lowest landmark has an inline source capture, and each retained Foam episode has a start capture plus an end capture only when a later non-Foam sample exists.
- Verify no Glass exposes more than twelve landmark cards or more than three report Foam episodes, while complete tracking/event data remains available in CSV and Result Review.
- Inspect representative captures from small and large Glass ROIs. Confirm the crop keeps the Glass visible with useful context and the ellipse, zero, stored Oil and stored Foam guides align with the source frame.
- Disconnect networking and confirm every graph/capture link in `report.html` resolves from the finalized result bundle.
- Sustain Result Review playback and repeated cursor updates long enough to expose cumulative layout drift; confirm the graph plotting area and overall layout do not progressively shrink or collapse.
- Repeatedly open and close Result Review and re-detection windows; confirm Matplotlib callbacks, fonts and file handles do not accumulate.

## Packaging
- Run the Windows canonical suite with Python 3.14.
- Before packaged startup, confirm the user/system does not require a preconfigured `QT_QPA_PLATFORM`; clear any inherited value in the validation shell and do not persist a user/system environment change.
- Build and verify the one-folder distribution on Windows in the supported Python 3.14 environment used as the project release baseline.
- Confirm `RotaryOilLevelTracker.exe` opens the native Windows GUI without external QPA setup; the package runtime bootstrap must select the `windows` Qt platform before the GUI entry script.
- For one bounded conflict probe, launch once with only the child-process environment set to `QT_QPA_PLATFORM=offscreen` and confirm the packaged GUI still opens normally, proving the package-owned Windows selection overrides a bad inherited value. Remove the probe value immediately afterward; it is not an installation prerequisite.
- Record the interpreter actually used; do not claim an unexecuted patch version or Windows result.
- Copy `dist/RotaryOilLevelTracker` to a clean machine without Python or separately bundled font files.
- Run the complete Workbench, preflight, analysis and Result Review workflow from the one-folder package.
- Confirm Windows Malgun Gothic is selected on a clean PC and the application does not require a repository font binary.
- Generate HTML/CSV in a user-writable output folder.
- Confirm Jinja template, Qt plugins and matplotlib resources resolve after relocation.
- Repeat output generation with file-locking software active and confirm resources are released after close.

> These are manual follow-up items. A GitHub-only validation run does not claim that they were performed.
