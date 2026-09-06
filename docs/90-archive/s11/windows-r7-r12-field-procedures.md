# Historical S11 R7–R12 Windows Field Procedures

**Status:** `ARCHIVED` — revision-specific procedures preserved for historical reconstruction only.

These sections were moved from the active Windows checklist during Agent Harness V2 migration. They do not define the current qualification route. Current field work must resolve the candidate from `docs/00-project/work-plan.md` and use `docs/40-operations/s11-current-windows-field-qualification.md`.

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
