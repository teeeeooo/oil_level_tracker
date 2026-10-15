# Initial-FULL observation comparison

Status: local implementation and OFF/ON analysis complete; corrected Windows
three-bundle audit received. Early admission delay is localized; middle/refill
observation predicates and raw no-interface outcome type remain unreported.
The option remains default OFF. Private bundles were not inspected on Mac;
no complete physical qualification is claimed.

The [fixed Work Plan order](../../00-project/work-plan.md#fixed-execution-order--2026-10-15)
and [bounded design](../../20-architecture/s11-physical-interface-evidence-repair-design.md#october-15-initial-full-observation-comparison)
own this comparison. Original historical results and regression Recipes remain frozen.

## ROI preparation

The prior read-only review found rim points inside sample4's saved mask and whole
rectangular crops in the closed water/beer/milk path studies. Those failures do not
establish performance with an interior ROI. This run uses the local base recording
and sample4; sample2's short fixed window and quarantined sample3 remain regression
context. The closed public cup/source probes are not rerun or silently converted
into full analysis inputs.

- Local base: retain Recipe ellipse `(696, 366, 145, 148)`, margin `0.08`; stored
  full-source views show it already follows the inner sight glass. The overlaid
  High/1/3/Low graphics are internal artifacts, not outside-rim errors.
- sample4: prepare a separate comparison Recipe with ellipse `(595, 842, 37, 34)`,
  margin `0.08`, zero-line/calibration and other settings unchanged. This is an
  agent-selected inner-glass geometry from existing source views, not a physical
  boundary label. Inspect its mask at the retained beginning/middle/end frames
  before any detector comparison; preserve the original `(595, 850, 52, 52)` Recipe.
- Both use existing 2 Hz analysis windows and ordinary static preparation; explicit
  initial FULL is a mechanism stress condition for local replay, not a new physical
  truth assertion about either recording. UNKNOWN/EMPTY remain mechanical controls.
- Private Windows BASE/Accum geometry cannot be certified on Mac. The operator must
  check the interior and full movement range in Windows, save one Recipe, and use
  it for both OFF/ON runs. No private media transfer is needed.

The managed run `sample/output/s11-initial-full-roi-20261015-001` is closed with
three retained files: the separate sample4 Recipe, input/hash manifest and one
five-frame mask overlay. Source frames 0/450/900/1470/1680 were visually checked
before detector execution. At source X595, the frozen mask includes Y813/833/835/842/844
and excludes the reviewed rim Y880/882/887; geometry validation passes. These are
mask-membership checks, not new physical labels or proof of complete interface recall.
The unchanged base Recipe is reused; its duplicate copy was discarded.

## Local mechanism result

The optional `--initial-full-observation` mode reuses existing confirmed current
anchors and the bounded selector. It publishes a current candidate under unresolved
initial FULL without asserting drainage. It does not change raw candidates,
association, motion state, recovery leases or existing drain/refill transitions.
`PARTIAL_VISIBLE` plus `OIL_DIRECTION_UNCONFIRMED` preserves location and uncertainty;
these points cannot create drain-start events or assert direction in the report.
The full physical-witness redesign remains unaccepted.

Both comparisons use the frozen ROI above, 2 Hz, ordinary static preparation and
explicit initial FULL as a mechanism stress condition. The local `base_sample_1`
recording is **not** the private Windows BASE recording. The managed run
`sample/output/s11-initial-full-replay-20261015-002` retains the complete OFF/ON
rows, lifecycle predicates, events, report presentation and input/runtime identity.

| Local input / window | Rows | Oil OFF → ON | New direction-unconfirmed points | Foam OFF → ON |
|---|---:|---:|---:|---:|
| base_sample_1 / 0–14.4 s | 30 | 3 → 9 | 6 | 0 → 0 |
| sample4 interior / 0–56 s | 113 | 0 → 10 | 10 | 76 → 76 |

All raw candidate inputs are exactly equal between OFF/ON. Existing numeric Oil
points remain unchanged. Every numeric final Y equals the selected current
candidate and exported CSV raw Y. Foam raw Y, confidence and validity match on
every row of these two comparisons. There is no new Oil drain-start event.
Base has seven observed-interface phase rows but six numeric outputs: downstream
selection still rejects one. The phase mode is not an unconditional numeric bypass.

The report retains numeric candidates and their extrema. Base's direction summary
still uses its original three direction-supported observations, with an added
uncertainty note for six candidates. sample4 states that ten candidate positions
are shown and direction is unresolved. Full bundles were generated and their CSV
and HTML checked, then discarded after extracting the compact evidence.

**Remaining limits:** the new base points are at 2.0–5.5 s; sample4's are at
3.5–17.0 s. This does not establish recovery of sample4's later reviewed interface,
the true identity of these newly selected points, or readable Windows motion.
No new physical labels were assigned. Excluding the previously reviewed rim
coordinates from the ROI does not exclude every internal artifact. Long output
gaps remain. More numeric rows are mechanism evidence, not a correctness score.

Runtime: macOS arm64, CPython 3.14.4, OpenCV 4.14.0 / package 4.14.0.94,
NumPy 2.5.1, PySide6 6.11.1, Matplotlib 3.11.1; FFMPEG backend.
Analysis-only times were 6.64/6.59 s (base OFF/ON) and 8.95/8.35 s (sample4).
These four local runs are not a Windows performance qualification.

| Retained comparison file | SHA-256 |
|---|---|
| `evidence/base_sample_1/comparison.json` | `825d5b8033a663e2e483226061b5ad2d8cfbe99ec086125d70bb59f44b0eb7ce` |
| `evidence/sample4/comparison.json` | `994ade8224ee16536a511df2d8363a662380be1570ad8a2f3f1074baa05a864a` |

The preceding replay `001` aborted before detector execution because the harness
compared the canonical base Recipe bytes to its discarded reserialization hash.
It was closed with no output. Replay `002` uses the original input hash; no source
Recipe or detector parameter was changed to recover the run.

## Verification and Windows handoff

The complete implementation/tests/handbook scope is committed and pushed as
`6d2f06950ea091f769c72435f873cdcc39de3b27`, reviewed against
`7d224fe66b7c809bb277688446e7b9e1ce219614`. Ten runtime source files captured by
the debug-equivalence run match that commit byte-for-byte. The worktree was clean
at publication. Subsequent handoff-only documentation pins this source without
changing the detector. The [source ZIP](https://github.com/teeeeooo/oil_level_tracker/archive/6d2f06950ea091f769c72435f873cdcc39de3b27.zip)
supports both OFF and ON; no Windows Git installation is needed.

Key extracted-file identity checks, under `src/oil_tracker/adapters/vision/`:

| File | SHA-256 |
|---|---|
| `oil_phase_lifecycle.py` | `35ba5017a20fadc5040586aab6a6becd5e5f9450b4326b6a004ffd4a044f11a9` |
| `oil_observation_resolver.py` | `143c54a3ecdc5b5cbb46b18ae51e74eb27f6ac44f418cb16aab6a37b3cc46039` |
| `opencv_phase_detector.py` | `167ef8c3f9bbb69a2639d664c870403f4e7adaa0ba7ea80fc7708a86a8e88e2d` |

Focused lifecycle/publication/event/report tests: **113 passed**. Additional
tracklet, Foam, lifecycle, identity, facade/decomposition, trace/bundle and Windows
bootstrap regression tests: **181 passed**. Actual Qt bootstrap/argument routing:
**4 passed**, including preview, analysis, preflight and redetection factories.
These are local engineering checks, not a Windows execution or reader acceptance.

Required debug NONE/FULL comparison also passes: **286 rows**, covering both
videos and both OFF/ON variants, have identical raw input hashes, complete tracking
rows, phases, events and report semantics (run IDs excluded). Each FULL run used
the real trace writer and bundle publication. Managed run
`sample/output/s11-initial-full-debug-20261015-001` retains only
`evidence/debug-equivalence.json`; identical FULL outputs are discarded and the
complete NONE records are reused. Governance, changed-document links, artifact
closeout and whitespace checks pass.

Use the [current Windows procedure](../../40-operations/s11-current-windows-field-qualification.md#october-15-first-initial-full-comparison)
for the two GUI launches, frozen interior ROI and segment readout. Stop here for
Windows work. Cost-first, RGB and Local XY remain conditional on that result.

## Windows interim feedback — initial UNKNOWN

The operator reports temporarily selecting initial `UNKNOWN_REVIEW` (알 수 없음)
and seeing BASE follow actual Oil movement closely, with two exceptions:

| Operator observation | Comparison focus |
|---|---|
| The interface is missed when it first descends into view from a full Glass | FULL-to-visible entry, corresponding to the reviewed BASE drain onset |
| The rising interface becomes `UNKNOWN_REVIEW` when it exits the Glass at the top | Refill closure and subsequent FULL/no-interface meaning |

The operator subsequently clarified that the earlier description as “empty” meant
the missing FULL interpretation: the actual state was already `UNKNOWN_REVIEW`.
This correction supersedes the initial EMPTY wording. It does not establish an
EMPTY-to-UNKNOWN improvement in ON.

These are attributable qualitative observations, not locally inspected pixels or
measured frame coverage. The report supplies no exact timestamps, Y anchors,
false-positive counts, run manifest or confirmed OFF/ON setting for that UNKNOWN
run. Other canonical segments and Foam are unassessed by this interim feedback.
The canonical physical truth and field FAIL remain unchanged.

Improved tracking with UNKNOWN is evidence to investigate state-dependent
publication; it does not prove that the initial-FULL barrier is the only loss or
that all raw candidates are correct. The two transition symptoms remain distinct.
UNKNOWN is an exploratory control, not a replacement for the reviewed FULL start.

At this interim checkpoint the operator was running ON, with its result and BASE
initial state still pending. The subsequent result is recorded below. The new
option requires explicit initial FULL; leaving UNKNOWN selected does not exercise
`_observe_initial_full_interface`.

## Windows FULL+ON result — operator report

The operator now confirms ON with BASE initially FULL and reports:

- BASE Oil is detected, unlike the previously reported zero-detection ordinary
  FULL launch. This establishes partial usefulness at operator-report scope.
- The first descending interface after a full/no-interface period is still missed.
- When the rising interface leaves the top, the display says `직접 유면 확인 어려움`.
  The operator clarifies that the preceding run also had `UNKNOWN_REVIEW` there.
- Detection rate is lower than the preceding R22-3 run without an initial value.
  Follow-up confirms additional real-interface misses during middle downward and
  upward movement as well, not only at first appearance.

The renderer maps `직접 유면 확인 어려움` to `UNKNOWN_REVIEW`; it is not FULL.
Both runs therefore leave the expected refill-to-FULL interpretation unmet; no
state-classification improvement is established. The requested behavior is to
track the rising real interface while visible and report coordinate-free
`FULL_NO_INTERFACE` when it reaches and disappears beyond the vessel top. This
agrees with the [reviewed BASE rapid-refill/suffix truth](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md#reviewed-timeline).
Ordinary loss partway up the vessel does not establish top exit. No exact exit
frame or state duration is supplied. First descent appearance, middle-motion
misses and top-exit FULL publication remain separate failures.

The UNKNOWN-start/R22-3 comparison and FULL+ON comparison change initial condition
as well as mode. They do not by themselves isolate a same-condition ON regression.
No exact percentages, metric definition, matched ROI/session receipt, counts or
lost-frame intervals are available yet. The follow-up establishes additional
true-interface loss qualitatively; it cannot be dismissed as removal of false
observations or a coverage-denominator difference. Existing completed runs are
needed to locate the first additional loss and distinguish absent numeric output
from a present but confidence-invalid observation. No repeat analysis or extra
candidate run is requested solely for this inspection.

The operator subsequently confirms three completed bundles are available:
① initial FULL+OFF, ② initial UNKNOWN+OFF and ③ initial FULL+ON. Inspect all three.
Use ①↔③ as the primary mode comparison with initial FULL held fixed, ①↔② for the
initial-state difference under OFF, and ②↔③ to locate the reported extra visible-
interface misses. Other source/ROI/session conditions still require verification
before attributing either controlled comparison to its single changed factor.
Bundle availability is confirmed; their contents have not been inspected on Mac.

Source inspection explains why the paths can differ, without claiming the first
harmful Windows predicate: UNKNOWN starts OPEN; FULL starts FILLED_BARRIER. The ON
route adds only current confirmed anchor/direct-or-ordered-lower candidates with
strict identity/material clearance, outside current no-interface opposition and
release ambiguity. It does not change the motion runtime to OPEN and stops applying
after an ordinary drain/refill transition. Candidate creation, association and
confirmation are unchanged. Actual lost-frame diagnostics are still needed to
decide whether cost-first association addresses the next observed loss.

There is also a separate source-backed refill/publication distinction:

- `_drain_refill_closure` / `_drain_refill_handoff` can close the phase owner to
  `FILLED_BARRIER` after a qualifying topward trajectory; they do not emit a final
  `FULL_NO_INTERFACE` result.
- `_state_and_unknown_nodes` creates a `full` node only from current
  `oil_no_interface_full_likelihood` meeting the state evidence threshold.
- `_constrain_layer` reduces an empty allowed-owner set to UNKNOWN, including
  when a `full` node existed before that filter. After the terminal owner is gone,
  `_transition_barrier` can produce this empty set with `FILLED_CAP_VETO`.
- Projection publishes FULL only when the selected node is `full`. The initial-
  FULL ON option does not modify these ordinary refill/state paths.

These facts explain how internal closure and the user's required FULL display can
diverge. They do not prove that the Windows trajectory reached closure: the saved
trace must distinguish missing closure from a closed phase blocked at state-node
creation or selection. Use the [completed-bundle inspection handoff](../../40-operations/s11-current-windows-field-qualification.md#october-15-completed-bundle-inspection)
before choosing the repair; reporting all UNKNOWN as FULL would erase that
distinction and does not meet the request.

This is a qualitative intake, not a complete nine-segment qualification. Other
canonical segments, Foam, exact position accuracy and physical false-positive
counts remain unassessed here. Source and runtime identity are operator-reported
rather than verified from a new bundle. The candidate stays opt-in and FIELD FAIL;
the detector source, canonical truth and optional-candidate order are unchanged.

## Windows three-bundle audit intake — reconciliation required

The user relayed a Windows agent's read-only CSV/trace inspection. Reported setup
is the same video, Glass IDs, 480–780 s window and 2 FPS; Accum starts EMPTY in all
three. Debug levels are FULL / FULL / BASIC. The ON resolver suffix was found in
the third trace. Hash/environment checks were deliberately excluded by the user;
none are requested to reconcile these contents. No private pixels or bundles were
transferred to Mac and no analysis was rerun.

| Bundle | Reported BASE numeric / UNKNOWN rows (601 total) | Reported visible states | Retrospective interpretation |
|---|---|---|---|
| ① FULL+OFF — `R22-3개선_add_artifact_20260918` | 0 / 601 | None | ACCEPTED initial FULL hold; observed 0, effective 1 |
| ② UNKNOWN+OFF — `initial_modify-BASE_non-initial-condition_20261015` | 309 / 292 | DRAINING 68, FILLING 77, PARTIAL 164 | NOT_APPLICABLE; observed approximately 0.514 |
| ③ FULL+ON — `initial_ON_20261015` | 185 / 416 | PARTIAL 185 | UNRESOLVED; observed approximately 0.308 |

These establish reported numerical publication, not physical recall. In particular,
①'s retrospective ACCEPTED/effective 1 is a prior-state hold with no coordinates;
it is not successful tracking or field acceptance. The returned 143/91 segment
counts have no supplied segmentation definition and are not used as a continuity
improvement metric. Accum is reported ACCEPTED in ① (two entrance observations)
and UNRESOLVED in ②/③; no Foam or nine-segment readout was returned.

At 548.5 s/frame 13151, ① reportedly retains a row at Y363, tracklet
`oil-tracklet:000132:0124`, with `phase_admitted=true` and `publishable=true`, but
direct release fails `downward_direction` and `minimum_progress`; allowed IDs are
empty. ② publishes Y363 there. At 550 s/frame 13187, ③ publishes Y367 through
`INITIAL_FULL_INTERFACE_OBSERVED` with direction uncertainty. This supports partial
early publication recovery. It does not close the user's first-appearance miss:
the cited ON point is 1.5 s later than the cited UNKNOWN point, and the first
physical appearance has no frame-exact annotation in this intake.

The returned interpretation requires the following corrections before a repair:

1. **Physical timing:** the existing reviewed BASE refill is 662–about 663.6 s;
   about 663.6–780 s is FULL with no visible interface. The reported numerical
   outputs at 774/775.5 s belong to that no-interface suffix under the supplied
   time/Glass binding. They cannot establish the real rising interface's top exit.
   Their presence conflicts with reviewed absence; their exact structure identity
   is unreviewed. Inspect 662–664 s for the requested FULL transition instead of
   substituting the last numerical row in the whole CSV.
2. **Coordinate/direction:** source Y increases downward. `dir=+1` and Y367→735
   do not prove ascent; `dir=-1` is topward track history. Track history and final
   FILLING/DRAINING labels can disagree because `_visible_state` uses neighbouring
   selected points. Neither label certifies that the row is the real interface.
3. **Runtime versus frame projection:** `_observe_initial_full_interface` changes
   the current record's phase/allowed IDs, not the underlying motion runtime.
   `observed_interface` followed by `INITIAL_FULL_BARRIER` is not proof that a
   real refill closed and then re-entered the initial state. The unresolved initial
   motion barrier can have persisted throughout both frames. Ordinary refill
   closure branches exist, but their execution at the real transition is not shown.
4. **Trace field paths:** `release_stage`, `release_evaluated`, `established_fill_*`
   and `recovery_*` are siblings of `initial_full_observation` under
   `sequence.state.sequence_material_phase_diagnostics`, not inside it. Raw FULL
   likelihood is under `state.oil_no_interface_full_likelihood`, outside the final
   `sequence` snapshot. Missing values at the wrong path do not establish a BASIC
   storage limitation. The writer uses the same metadata/sequence serialization
   for captured BASIC and FULL records; captured frames/images can differ.
5. **Gate meaning:** `sequence_selected_authority_tier=HARD_INVALID` is also the
   default when there is no selected candidate; it does not prove every raw
   candidate is invalid. A passed recovery subpredicate is not a committed release;
   check qualifying/selected IDs, ambiguity and the final reason. An empty allowed
   set explains final UNKNOWN at that frame but not why the eligible observation
   set was empty or whether a real top-exit interface was lost there.

The user's earlier report of additional real middle-motion misses remains recorded.
The aggregate 309→185 difference cannot measure those misses separately from
false observations in no-interface intervals. The actual first missing middle row
and its failing ON predicate were not supplied. The whole-window rates therefore
do not choose cost-first association or a FULL-state change on their own.

Next use the [bounded saved-record recheck](../../40-operations/s11-current-windows-field-qualification.md#october-15-audit-reconciliation)
at early appearance, one middle-drain loss and the real 662–664 s refill. No detector
change, new replay or adoption follows from the unsupported 774 s top-exit reading.
FIELD FAIL, the generic detector contract and the optional-candidate order remain.

## Corrected Windows checkpoint intake

The subsequent Windows reply corrects the 774 s interpretation, source-Y direction
and field paths. It reports that ③ first publishes at 550 s after three missing
sampled rows at 548.5/549/549.5 s where ② publishes Y363/367/367. At 548.5 s,
direct release fails downward direction and minimum progress (4 px versus 19.3 px);
the ON observation evaluations additionally fail `current_confirmed_owner` and
`anchor_eligible`. Thus the 1.5 s output delay has an identified admission cause.
This is not proof that those early ② rows all depict the real physical interface.

The first reported post-550 s ②-numeric/③-missing row is 553.5 s/frame 13271 (②
Y364); additional examples are 554.5/555.5/556.5 s. The reported total of 51
differences covers **548–663 s**, including the initial three rows and refill;
it is not a count for the requested 550–662 s drain alone or a verified physical
miss count. Only empty allowed/qualifying IDs are returned for the middle loss;
the row-specific ON failure predicates have not yet been supplied.

In the real refill window, ③ is UNKNOWN from 662.5 through 664.5 s, then publishes
Y409 at 665 s. Its 662.5/663.5 s records retain `INITIAL_FULL_BARRIER`, empty allowed
and qualifying sets, and raw FULL likelihood 0. Output at 665 s remains inconsistent
with the reviewed FULL suffix, not a recovered rising interface. The ② sequence
409→418→418→425→411 at 662.5–664.5 s does not by itself demonstrate a continuous
topward trajectory; final direction labels/negative track history are not physical
identity evidence. The exact top-reaching owner is still unestablished.

Source inspection resolves two remaining interpretation issues without a rerun:

- `oil_runtime_metrics` writes FULL likelihood **0.0 by default whenever the raw
  outcome is not `NoInterfaceOutcome`**. Zero is a stored value, but does not prove
  a no-interface evaluation returned zero. Read `oil_decision_status`,
  `oil_decision_reason` and `oil_no_interface_reason` alongside it. At the current
  state threshold 0.58, zero supplies no `full` node regardless of why it is zero.
  Removing an allowed-set restriction alone therefore cannot publish FULL at
  these points under the existing state-node rule.
- `established_fill_present` describes the OPEN/FILLING established-fill chain,
  not every drain/refill owner. In the cited initial-FULL records, motion remains
  behind the initial barrier; the per-frame observation projection does not
  transition that runtime. Its false value is not evidence that every fill/refill
  branch was evaluated and failed. The retained claim that recovery “passed” also
  remains unqualified until qualifying/selected IDs and final reason show a
  committed release.

Do not infer that the first-frame confirmation/anchor failure also explains every
middle/refill gap. The [remaining extraction](../../40-operations/s11-current-windows-field-qualification.md#remaining-three-record-extraction)
is limited to ③ at 553.5/662.5/663.5 s: actual ON predicate results, relevant Oil
candidate metadata and raw outcome status/reason. This uses existing serializers;
no new helper, video analysis, hash/environment verification or threshold change
is needed. No detector behavior is changed from this incomplete causal record.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `PUBLICATION-PROVENANCE`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F04`, `S11-F05`, `S11-F08`, `S11-F09`, `S11-F10`.
- First harmful stage: corrected transferred 548.5 s data identifies direct release direction/progress and ON current-confirmation/anchor failures. The first reported middle gap is 553.5 s; its actual ON predicates and those at 662.5/663.5 s remain unreported. FULL likelihood zero prevents a current full node, but its default-versus-no-interface-outcome origin is unknown. Source separates motion runtime, frame projection and state publication; physical identity/onset remain separately unverified.
- Existing feature coverage: local comparisons use ellipse/margin masks and shared preprocessing with exclusions/templates empty and Local XY OFF; new local ROI remains separate from regression inputs. Windows intake reports initial FULL/OFF, UNKNOWN/OFF and FULL/ON with the same window/cadence/Glass IDs, and FULL/FULL/BASIC trace. Actual Windows ROI/Artifact/static preparation values are not supplied by the returned table; bundle names do not establish configuration. User excludes hash/environment checks for this read-only intake.
- Execution scope: earlier bounded local real-entry analysis and controls, followed by operator feedback and a relayed Windows agent CSV/trace audit. Current work reconciles that text against source, serializer paths and canonical reviewed truth without loading private media, replaying analysis, running new experiments or changing detector code. Returned counts/checkpoints are attributed transferred evidence, not locally verified bundle contents.
- Logic-map impact: NONE — this update corrects operator feedback and traces the already-mapped lifecycle, state-node and allowed-set selection responsibilities without changing the pinned source. The optional observation projection and GUI/event/report consumers were already mapped in implementation commit `6d2f069`; that earlier source change had impact UPDATED.
- Failure-registry impact: NONE — existing barrier, identity and provenance entries cover this trial; no physical failure is declared solved by preflight.
