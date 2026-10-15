# Initial-FULL observation comparison

Status: version 1 causal intake and version 2 local checks are complete. The
returned final CSV comparison confirms 185→303 numeric BASE outputs across 601
matched rows. The [latest return and user timing correction](#reconciled-return-and-user-timeline-correction--2026-10-15)
close aggregate/IFO checks and supersede earlier physical timing interpretations
below. New phase-specific counts and human candidate correspondence remain pending.
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

This subsection records the frozen **version 1** result. The v2 comparison is below.

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

This checkpoint precedes the completed three-record reply below; its outstanding
requests are retained as the diagnosis sequence, not new requests.

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

## Three-record predicate intake

The operator transferred three tables from the existing ③ FULL+ON JSONL, then
confirmed the exact false predicate keys separately. The initial table B had ten
boolean headers but nine values per row, so it was not used to align predicates.
The corrected key lists below supersede that malformed alignment. Table C has
66 Oil candidates (21/22/23); the following retains the relevant admitted rows,
not a physical truth label or a local inspection of the private JSONL.

| Source record | Evaluated tracklet / row | Confirmed false ON predicates | Current candidate evidence |
|---|---|---|---|
| f13271, 553.5113 s, `f000013271_921e1a1dece0` | `oil-tracklet:000132:0124` / `oil-row:000147:000` | `anchor_eligible`, `interface_identity` | Y364/365/356/364; CONTINUATION_ELIGIBLE, continuation_only, continuing, admitted=1; no tracklet failure |
| f15884, 662.4952 s, `f000015884_9f631e05c5c9` | `oil-tracklet:000357:0309` / `oil-row:000365:001` | `anchor_eligible` | Y421/420/409; CONTINUATION_ELIGIBLE, continuing, admitted=1; Y409 is direct_interface with no authority failed gates |
| f15908, 663.4962 s, `f000015908_9c682a88811b` | `oil-tracklet:000366:0319` / `oil-row:000367:002` | `current_confirmed_owner`, `anchor_eligible` | Y418; CONTINUATION_ELIGIBLE, direct_interface, provisional but admitted=1; no authority/tracklet failure |

At f15908 the separate Y413.5 anchor belongs to `oil-tracklet:000366:0320` /
`oil-row:000367:001`, which is unadmitted with `INCOMPATIBLE_BRANCH`. Its authority
must not be combined with the Y418 row. Provisional lifecycle plus admitted=1 is
consistent with an earlier witness admitted by the builder's bounded later
confirmation, not permission to publish a never-confirmed provisional row.

All three records have IFO evaluated=true, blocked_by_current_state=false,
qualifying IDs=[], and motion `filled_barrier / INITIAL_FULL_BARRIER`.
Recovery stage is `initial_full`, with qualifying IDs=[], selected ID=null and
ambiguous=false in all three. Reset reason is `evidence_window_expired` at f15884
and null at the others. Thus no recovery release was committed at these points.

Raw outcomes are ambiguous / `competing_boundary_artifact_or_no_interface_evidence`
at f13271/f15908, and boundary_accepted / `continuous_shadow_boundary` at f15884.
All three have `oil_no_interface_reason=not_available` and FULL likelihood 0.
Against `oil_runtime_metrics`, this establishes the zero as the default for a raw
outcome other than `NoInterfaceOutcome`. It does not establish that every upstream
no-interface calculation was skipped, or that the physical scene is not FULL.
At the existing state threshold it supplies no FULL node.

The requested read-only intake is complete; no further JSON/table extraction is
needed for these three losses. It supports the
[v2 admission correction](../../20-architecture/s11-physical-interface-evidence-repair-design.md#version-2-admission-correction),
not a claim that all 51 differences are real interfaces or that admitting them
alone repairs the actual ~663.6 s top exit. Exact physical owner continuity and
post-FULL false observations still require Windows source review.

## Version 2 local verification

The existing lifecycle observation branch now consumes bounded confirmation and
continuation authority instead of requiring a fresh anchor/direct identity and
current confirmation in every frame. Existing motion runtime, recovery leases,
candidate generation, association, FULL/EMPTY state rules and Foam owners are
unchanged. Version suffix is `+initial-full-observation-v2`; default OFF is unchanged.
Focused admission and actual detector/resolver tests pass (83 tests), including
all three reported evidence shapes, bounded provisional admission, unsupported and
incompatible controls, same-frame Y and direction uncertainty. The related
lifecycle/tracklet/authority/JSONL/event/report suites pass (181 tests): **264 total**.
GUI wiring is unchanged and its earlier propagation checks remain applicable.

The verified v2 source is commit `4c72ebbf038d577290aedcf29a7d33345c5de628`.
The managed run `sample/output/s11-initial-full-v2-20261015-001` is closed. It reuses
`tests.diagnostics.s11_initial_full_comparison`, the frozen ROI inputs from the
first comparison and both prior windows, at 2 Hz with explicit FULL as a mechanism
stress condition. The local base video is not the private Windows BASE video.

| Local input | Rows | Oil OFF / v1 / v2 | v1→v2 added / removed / changed Y | Foam OFF / v2 |
|---|---:|---:|---:|---:|
| base_sample_1, 0–14.4 s | 30 | 3 / 9 / 12 | 4 / 1 / 4 | 0 / 0 |
| sample4 interior, 0–56 s | 113 | 0 / 10 / 16 | 6 / 0 / 0 | 76 / 76 |

The 143 OFF rows equal v1 exactly. All original OFF numeric Oil points survive
unchanged under v2. Both modes have identical raw inputs. Every numeric result
matches its current selected candidate and exported CSV Y. All Foam coordinate,
confidence and validity fields match; neither comparison adds a drain event.
NONE and FULL debug runs have identical rows, phase predicates and events on all
286 mode/sample rows, with equal raw-input fingerprints. Full bundles/CSV/HTML
were produced through the real analysis/export owners before temporary cleanup.

The widened allowed set can change the selector's competition. V2 is **not a
superset of v1**: local base loses the old Y367 point at 4.004 s and changes four
other coordinates while adding four points. Its changed times span 1.001–5.005 s;
sample4 adds points at 12, 15, 16.5, 37, 37.5 and 38 s. Complete changed-row values
are retained in `evidence/summary.json`; physical identity is `NOT_EVALUATED` for
every changed point. Counts establish publication behavior, not recovery/accuracy.
The trial remains opt-in; Windows must assess the real refill and FULL-suffix
oppositions before further motion/state work or promotion.

Only two complete NONE comparison JSONs, the exact source patch and the summary
are retained under ignored `sample/output/` (867,301 bytes total). The summary
SHA-256 is `5fc13d51b75eacadbbe47106a990b5e467c692f63e6bbeb0ba2202f4508b482d`.
FULL duplicate comparison files and
temporary bundles/images were removed. One mid-run check observed 753,909,667
bytes of temporary FULL output against the planned 350,000,000-byte budget; the
writer then completed and cleaned that output. The final artifact check passes
for all 77 managed runs. This does not establish peak-budget compliance; a later
FULL replay needs a larger explicit allowance or a smaller trace window.

## Operator-reported non-Oil tracking from 721.01 s

The operator reports actual non-Oil tracking from source-video time 721.01 s,
visually suspected to be heat shimmer, including with OFF. A subsequent Windows
readout binds the candidate-level observation to **BASE** and
`oil-tracklet:000474:0424` in all four bundles. These are transferred observations;
private images and complete tracks have not been inspected locally.

| Candidate-level checkpoint | Reported result in all four bundles |
|---|---|
| Extent | f17191 at ~717.0 s through f17994 at ~750.5 s; Y675–748 |
| Candidate occurrences | 116, including multiple source members per frame; not 116 distinct final-output frames |
| ~721 s | two admitted members, material_path Y694 and calibrated_high_recall Y690; the material row is ANCHOR_ELIGIBLE/direct_interface |
| ~723 s | three admitted members at Y705–707; continuing lifecycle |
| Reported stored motion fields | direction in {0, 1}, net progress 19 px, motion support 0.36 and coverage 0.44 |

The transferred extent starts before the user's noticed 721.01 s onset. It is a
candidate-track extent, not proof of continuous selected output throughout
717–750.5 s. Same tracklet/member evidence in OFF/v1/v2 establishes a non-Oil
candidate shared by the compared modes; it does not establish identical final
Oil publication. In particular, the earlier ① FULL+OFF BASE final CSV count was
zero. The IFO `motion_phase=filled_barrier` also describes the underlying motion
runtime, not necessarily the final frame phase after the observation projection.

This entire BASE interval is inside canonical `WS1-BASE-FULL-SUFFIX`: no actual
Oil interface is visible after ~663.6 s. That reviewed truth and the user's source
observation support treating these as non-Oil candidates. A non-monotonic sampled
Y sequence alone is not proof of a nonphysical boundary or of heat shimmer. The
optical cause and the exact candidate-to-visible-object correspondence remain
unverified. No new physical truth interval or automatic shimmer classifier follows.

Source review corrects the motion interpretation:

- Stored direction 0/+1 is not an up/down reversal: source Y increases downward,
  +1 is down and -1 would be up; zero carries no signed direction in that field.
- `_finalize_track` writes the first confirmation witness's `net_progress_px`,
  direction and agreement onto admitted witness/continuation observations.
  Repeated 19 px can therefore describe that bounded confirmation window rather
  than each current movement or the whole 33.5 s track. Separate `recent_*` fields
  describe newer windows; do not read one historical sign as instantaneous motion.
- Current motion-confirmation thresholds are support >=0.50 and coverage >=0.50.
  Reported 0.36/0.44 do not by themselves prove motion-confirmation passed. The
  builder also supports ANCHOR_CORRIDOR and ANCHOR_TRAJECTORY; continuation can use
  anchor grace, a bounded anchor corridor or aggregate motion under other criteria.
  Current continuation metrics alone cannot exclude an earlier motion confirmation;
  the later profile reply below identifies the anchor route for v2.
- Members from several source families are grouped into one row hypothesis. Their
  count is neither multiple independent physical observations nor proof of a
  duplicate-counting bug. No source-family veto or monotonicity filter is justified
  by this summary.

### Final output and confirmation reply received

The subsequent eight-row Windows reply resolves publication at the two requested
samples. A number below is the final CSV Oil Y, with `oil_is_valid=True`; a blank
is `UNKNOWN_REVIEW`, invalid, with no selected candidate.

| Bundle | f17287 / 721.012 s | f17335 / 723.014 s |
|---|---|---|
| ① FULL+OFF | blank; `filled_barrier`, allowed `[]` | blank; `filled_barrier`, allowed `[]` |
| ② UNKNOWN+OFF | Y694; `open`, unconstrained; PARTIAL_VISIBLE | Y707; `open`, unconstrained; DRAINING_VISIBLE |
| ③ FULL+ON v1 | blank; `filled_barrier`, allowed `[]` | blank; `filled_barrier`, allowed `[]` |
| ④ FULL+ON v2 | Y694; `observed_interface`, allowed `000474:0424`; PARTIAL_VISIBLE | blank; `filled_barrier`, allowed `[]` |

The nonempty selections are reported as `000474:0424`. Thus v2 exposes a false
Oil output at 721 s that v1 blocked, while the UNKNOWN+OFF reference already
published it. Shared upstream candidates do not imply unchanged false-output
extent. At 723 s v2 retains the reported material veto and correctly withholds a
number. This establishes the two checkpoints, not the whole 717–750.5 s output
extent. Heat shimmer remains an unverified optical explanation.

The confirmation extraction was returned for **④**, rather than the requested
③: f17263 at ~720 s, `material_path`, row `oil-row:000480:003`, profile
`anchor_corridor`, confirmation start/end `480/485`, established direction `+1`,
recent direction `-1`, established progress 19 px and recent progress 10 px.
Record that bundle attribution rather than silently treating it as a v1 result.
It identifies an anchor-confirmation route, not a motion-threshold bypass.

The source assigns these start/end values from `hypothesis.frame_offset`, a
zero-based index in the per-Glass analysis sequence, not a source-video frame
number. At the reported 2 fps, indices 480–485 span **five intervals / about
2.5 s**, approximately 720–722.5 s, not 0.5 s. `_finalize_track` can admit the
earlier members of that bounded witness retrospectively. Established direction
and `recent_direction` describe different windows, potentially overlapping and
including later samples in the confirmation witness. Their opposite signs are
not two consecutive instantaneous measurements or proof of a physical Oil
reversal. Exact window times come from the corresponding saved sample timestamps.

The f17287 provenance discrepancy is **closed by the follow-up**. The original
selected-candidate object is:

```json
{"candidate_offset":9,"source":"material_path","y":694.0,"tracklet_id":"oil-tracklet:000474:0424","row_hypothesis_id":"oil-row:000482:002"}
```

Selected Y694 equals final CSV Y694. The previous claim that `y` was absent was
an extraction omission, not a serializer defect. Do not request this object again.

## Windows v2 summary — final output reconciliation

The operator relayed the first v1/v2 comparison and asked to check it before the
separate 721.01 s observation. Its supported result is that all reported IFO
predicates pass at f13271/f15884/f15908 under v2, versus the previously identified
v1 failures. The returned summary additionally reports these unchanged values:

| Reported quantity | Same v1/v2 value | Evidence limit |
|---|---|---|
| Record extent | f11508 at 479.98 s through f18701 at 779.99 s, 1,202 rows | Record bounds are not the first/last numeric BASE observation; filter by Glass and final Oil value |
| Refill candidate/tracklet summary | `000357:0309`, `000366:0319/0320`; admitted counts `3+0+1+4` | Existing association/admission counts do not establish selected Oil Y or physical refill continuity |
| BASE 663.6–780 s | 233 rows, ambiguous 218 / reacquisition 15; Oil candidates 5,233 / admitted 303 | Raw outcomes and candidate counts do not count final numeric observations or final FULL states |
| Accum | ambiguous 568 / boundary 17 / reacquisition 15; Foam count 591 | Final Foam coordinates/validity equality is not supplied by these totals |
| Remaining IFO false keys in FULL suffix | material veto at 723 s/f17335; identity contradiction at 771 s/f18486 | These can be correct protection against false positives in a no-interface interval; do not relax them merely because they fail |

The initial conclusion “only predicates changed; no numeric restoration” is
superseded by the final CSV reply below. `oil_decision_status` is a raw hypothesis
outcome; final projection retains raw metrics while separately writing
`sequence_resolved_kind`, final positions and `fill_state`. In the current source,
a qualifying IFO row changes the frame's actual phase to `OBSERVED_INTERFACE` and
its allowed tracklet IDs. Publishability, bounded selection and projection can
still prevent a number. This is not a trace-text-only change.

Existing local v1/v2 comparison records have identical raw-input fingerprints but
different numeric counts (9→12 and 10→16), illustrating why unchanged raw inputs
cannot prove final output equality. This is an interpretation check, not evidence
that Windows improves. No new experiment is run for this reconciliation.

### Final BASE CSV reconciliation received

| Final CSV quantity | ③ v1 | ④ v2 |
|---|---|---|
| BASE rows | 601 | 601 |
| Nonempty raw Oil Y | 185 | 303 |
| `oil_is_valid=True` | 185 | 303 |
| First numeric Oil time | 550.01 s | 548.51 s |
| Last numeric Oil time | 773.98 s | 775.48 s |
| `FULL_NO_INTERFACE` | 0 | 0 |

The increase is **118 net numeric rows**, not necessarily 118 newly recovered
frames: newly nonempty and newly empty frames require a paired comparison. V2's
303 numeric rows are reported as PARTIAL_VISIBLE; 298 rows remain empty. Neither
these empties nor the reported 154 empties within 548–776 s are all misses: that
range includes the no-interface FULL suffix. Similarly, later numeric output in
that suffix is false output, not improved tracking. The approximate ~550 s truth
boundary alone cannot classify the first 548.51 s observation as correct or false.

The six-row checkpoint table now establishes actual sequence-to-CSV recovery:

| Frame / time | Allowed v2 tracklet | v1 final result | v2 final result |
|---|---|---|---|
| f13271 / 553.5 s | `000132:0124` | filled_barrier, allowed `[]`, unknown, Y null, UNKNOWN_REVIEW, invalid | observed_interface, oil, sequence/CSV Y364, PARTIAL_VISIBLE, valid |
| f15884 / 662.5 s | `000357:0309` | filled_barrier, allowed `[]`, unknown, Y null, UNKNOWN_REVIEW, invalid | observed_interface, oil, sequence/CSV Y409, PARTIAL_VISIBLE, valid |
| f15908 / 663.5 s | `000366:0319` | filled_barrier, allowed `[]`, unknown, Y null, UNKNOWN_REVIEW, invalid | observed_interface, oil, sequence/CSV Y418, PARTIAL_VISIBLE, valid |

This closes the question of whether the observation repair reaches final output.
It does not establish that Y409/418 are the actual rising interface. Taken alone,
409→418 increases source Y, and 663.0 s is missing; neither a continuous rise nor
a verified top exit follows. Original-video correspondence and the last visible
interface remain necessary before implementing a FULL transition from this path.
Final Accum/Foam equality is also not supplied by the earlier raw candidate totals.

### Empty-output witness interpretation

`OilPathLifecycleOwner.resolve` stores `phase_admitted`/`publishable` row-ID sets
from the layers built **before** `OilMaterialPhaseLifecycleOwner` applies its
allowed-ID decision. These names describe preliminary layer membership, not the
final phase's permission or a promise of selection. The witness `selection` is
the final projected path, after bounded selection and trajectory-spike suppression.

| Returned examples | Supported interpretation |
|---|---|
| f13139 / 548 s; f13367 / 557.5 s; f15896 / 663 s; f17239 / 719 s; f17251 / 719.5 s | Barrier with no preliminary eligible/publishable row reported. A physical miss needs visible-interface correspondence; 663 s is in the actual refill review window, while 719 s is FULL. |
| f17263 / 720 s | OBSERVED_INTERFACE and preliminary eligibility coexist with final unknown. Scores/ambiguity or later suppression can still abstain; the returned fields do not identify the exact stage. This is a no-interface interval, so its empty output is not a recovery target. |
| f18486–18509 / 771–772 s | Preliminary eligible/publishable rows can coexist with the final barrier. An empty allowed set makes `_constrain_layer` return only unknown. The reported identity contradiction at 771 s is consistent with protective rejection, not proof of a newly broken selector. |

Do not remove a veto or force selection just to reduce the 298 empty rows. Keep
the 723/771 s no-interface controls. The remaining bounded Windows work is the
[refill owner and false-output follow-up](../../40-operations/s11-current-windows-field-qualification.md#refill-owner-and-false-output-follow-up):
correctly segmented final output deltas and original-video correspondence around
662–664.5 s. The selected-candidate object is now reconciled above. Current code already has
`_drain_refill_closure` / `_drain_refill_handoff` for established drain owners;
IFO v2 only changes the frame observation decision and creates no motion runtime
owner. A future repair must reuse that ownership boundary with verified evidence,
not treat every disappearance or the known 663.6 s timestamp as FULL.

### Refill follow-up received — corrections and remaining evidence

The transferred follow-up reports 119 newly numeric frames and one lost frame,
giving the already established net increase of 118. Its physical segment labels
are **not accepted**: they use 480–663.5 / 663.5–665 / 665–670 / 670–780 s,
which differ from the canonical reviewed 480–~550 / ~550–662 / 662–~663.6 /
~663.6–780 s. The subsequent reply explicitly confirms those boundaries were
arbitrary approximations, not a new source-video review. Canonical truth remains
unchanged; that clarification is closed.

Retain the numbers as reported time buckets, not as corrected physical segments:

| Returned interval | Returned label (unqualified) | Rows | v1 numeric | v2 numeric | New / lost |
|---|---|---|---|---|---|
| 480–663.5 s | FULL PREFIX | 367 | 143 | 194 | 52 / 1 |
| 663.5–665 s | DRAIN | 3 | 1 | 3 | 2 / 0 |
| 665–670 s | RAPID REFILL | 9 | 5 | 9 | 4 / 0 |
| 670–780 s | FULL SUFFIX | 221 | 36 | 97 | 61 / 0 |
| Reported total | not a complete physical segmentation | 600 | 185 | 303 | 119 / 1 |

The 600 bucketed rows versus the earlier 601 total are consistent with the first
sample at 479.98 s falling outside a strict 480 s start, but the excluded row has
not been explicitly returned. Keep an outside-interval row in the corrected
accounting. The one lost frame lies in the mixed 480–663.5 s bucket; it cannot be
called a FULL-prefix loss without its frame/time and source correspondence.
Under unchanged reviewed truth, the entire reported 670–780 s bucket is inside
the FULL suffix: its numeric 36→97 increase is **61 added false Oil outputs**.
Thus at least 61 of the reported 119 newly numeric frames are in that no-interface
subinterval; this inference uses the transferred counts and is not a local CSV audit.

The six returned samples bind selected values and final CSV, but contain no
original-video visibility, actual interface Y, or match judgment:

| Frame / actual time | Selected tracklet | Selected Y = CSV Y | Final state |
|---|---|---|---|
| f15872 / 661.995 s | `000357:0309` | 433.5 | PARTIAL_VISIBLE / observed_interface |
| f15884 / 662.495 s | `000357:0309` | 409 | PARTIAL_VISIBLE / observed_interface |
| f15896 / 662.996 s | none | null / empty | UNKNOWN_REVIEW / INITIAL_FULL_BARRIER |
| f15908 / 663.496 s | `000366:0319` | 418 | PARTIAL_VISIBLE / observed_interface |
| f15920 / 663.997 s | `000366:0319` | 425 | PARTIAL_VISIBLE / observed_interface |
| f15932 / 664.497 s | `000366:0319` | 411 | PARTIAL_VISIBLE / observed_interface |

433.5→409 decreases source Y; 409→418 **increases** it. The latter is not an
upward trajectory, and it also crosses two selected tracklet IDs. A selected-ID
switch is not proof of a legitimate material-phase handoff or of the same real
interface. The final two rows fall after the canonical approximate top exit;
they cannot be counted as restored refill solely from their observed-interface
label. 664.497 s is only the last row in this requested six-sample window, not
the final numeric observation of the run. The last physically visible interface
and the Glass top remain unreviewed in this reply.

At f15896 the returned candidate-level evidence localizes an earlier rejection:

| Tracklet | Returned candidate Y values | Admission / failure |
|---|---|---|
| `000366:0319` | 417, 419, 407 | all 0 / INCOMPATIBLE_BRANCH |
| `000366:0320` | 420 | 0 / INCOMPATIBLE_BRANCH |
| `000357:0308` | 397, 393, 402 | all 0 / INCOMPATIBLE_BRANCH |

`build_interface_layers` requires `_phase_admitted(ref)`, which excludes both
unadmitted and incompatible tracklet members. `_rows` and IFO evaluate only the
remaining phase-layer rows. These seven candidates therefore do **not** pass IFO;
they are excluded before it. `ifo.evaluated=true` means that the initial-FULL
context was evaluated, not that every raw candidate was evaluated. No false keys
in an empty evaluations array must be recorded as no evaluated rows, not all-pass.
For an actual evaluated row, v2 `passed=true` would add its ID to the qualifying
set and expose OBSERVED_INTERFACE. The raw evaluations count, current-state block
flag and qualifying IDs are the only missing summary needed to resolve the
reported “all pass but still barrier” wording.

This localizes the supplied candidates' loss to tracklet branch compatibility;
it does not yet identify a rejected **real** refill interface or establish which
association alternative should win. `_ambiguities` runs before assignment order
is chosen. Cost-first sorting would not directly undo the same current-frame
conflicted set; different preceding associations could change that set, but this
requires a separate comparison. Preserve the optional mechanism order without
treating INCOMPATIBLE_BRANCH as evidence that cost-first must solve the case.
No compatibility veto, IFO predicate or selector is relaxed on this readout.

The next handoff corrects the mechanical interval aggregation, requests only the
small f15896 IFO summary, and separates actual video inspection from trace lookup.
If the Windows agent cannot view the original, record that access limit and leave
the physical match to the operator; another candidate table cannot substitute for
it. No new run, source revision, hash check or complete JSON transfer is needed.

### Boundary recount — overlapping totals not accepted

The next reply retains the canonical physical timeline but snaps aggregation
boundaries to f13187 / 550.01 s, f15872 / 661.99 s and f15908 / 663.50 s, counting
boundary samples on both sides. It returns:

| Returned bucket | Rows | v1 numeric | v2 numeric | New / lost | Net |
|---|---|---|---|---|---|
| 480–550.01 s | 140 | 1 | 4 | 3 / 0 | +3 |
| 550.01–661.99 s | 225 | 143 | 189 | 47 / 1 | +46 |
| 661.99–663.50 s | 4 | 1 | 3 | 2 / 0 | +2 |
| 663.50–780 s | 234 | 42 | 110 | 68 / 0 | +68 |
| Overlapping sum | 603 | 187 | 306 | 120 / 1 | +119 |

These are not a valid partition of the previously reported 601 unique BASE rows.
Changing segment membership cannot change the fixed-cohort totals 185→303 or
119 new−1 lost=118. The returned totals add two v1 numeric occurrences and three
v2 numeric occurrences; their extra net one is a counting discrepancy, not a
detector change or an allowed boundary tolerance. Do not replace the accepted
aggregate with +119 or treat the row-count discrepancy as harmless.

The procedure's numeric aggregation cutoffs remain 550 / 662 / 663.6 s, applied
to actual CSV time, without snapping to the nearest sample. Under that accounting,
f13187 at 550.01 s and f15872 at 661.995 s belong only to DRAIN, while f15908 at
663.496 s belongs only to RAPID REFILL. Approximate physical transition truth is
separate from this deterministic bookkeeping. OUTSIDE preserves samples such as
the reported first 479.98 s row; every matched row belongs to exactly one bucket.
Do not reconstruct a final segment table by subtracting guessed duplicate values;
the actual unique frame pairs must be grouped once.

The reply locates the one lost output in DRAIN, but still supplies no frame/time.
The claimed 68 new FULL-suffix outputs and other bucket totals remain provisional
until deduplication and fixed-boundary aggregation pass. The earlier reported
670–780 s subinterval remains separate evidence; it is not replaced by this
overlapping table. Also distinguish **new outputs** from **all v2 outputs**:
even 110/303 would be about 36%, so this table does not establish that most of
v2's total numeric observations are FULL-suffix false positives. It does support
continuing the review of false outputs among additions, without certifying the
DRAIN candidates as actual interfaces.

This reply answers the timeline-clarification question, not the outstanding
f15896 IFO cardinality or original-video correspondence checks. The operator
clarifies that the df00806 questions have not yet been forwarded; send the updated
procedure as one replacement handoff. Those items remain pending, not an already
running Windows review. No additional detector experiment or expanded evidence
request follows.

## Reconciled return and user timeline correction — 2026-10-15

The latest Windows reply reports 601 unique keys in each BASE CSV, equal key
sets and zero timestamp differences. Its disjoint table, using the then-current
550/662/663.6 s boundaries, is arithmetically consistent:

| Old time bucket (not current phase truth) | Rows | v1 Oil | v2 Oil | New | Lost | Net |
|---|---|---|---|---|---|---|
| 480 ≤ t < 550 | 139 | 0 | 3 | 3 | 0 | +3 |
| 550 ≤ t < 662 | 225 | 143 | 189 | 47 | 1 | +46 |
| 662 ≤ t < 663.6 | 3 | 0 | 2 | 2 | 0 | +2 |
| 663.6 ≤ t ≤ 780 | 233 | 42 | 109 | 67 | 0 | +67 |
| OUTSIDE | 1 | 0 | 0 | 0 | 0 | 0 |
| Total | 601 | 185 | 303 | 119 | 1 | +118 |

OUTSIDE is f11508@479.9795 s. The sole lost row is
f15776@657.9907 s, v1 Y437→v2 empty. These are received Windows measurements,
not a local inspection of the private bundles. They close the earlier arithmetic
discrepancy; the overlapping 603-row/+119 table remains rejected.

At f15896@662.996 s, IFO `evaluations` is an existing empty array (zero rows),
`blocked_by_current_state=False`, and `qualifying_tracklet_ids=[]`. This closes
the pending cardinality question: there were no evaluated/passing IFO rows.
The seven admitted=0 `INCOMPATIBLE_BRANCH` candidates were excluded before IFO;
their actual physical identity remains unqualified. Do not request this summary again.

The Windows agent also supplied an ffmpeg/LVLM image interpretation, explicitly
not a human review. It reports visible interfaces in all six 662–664.5 s images,
two selected-Y matches, visibility near the top at about 674 s and uncertainty
at 675 s. These are retained as agent interpretations, not exact-Y truth or
candidate labels. An empty output at f15896 has no selected line; whether it
misses the actual interface still needs human correspondence review. Different
tracklet IDs alone do not establish different
physical interfaces. Clearly bind BASE/Accum views before recording human idx
judgments. The claimed pixel error band and the later right-view observation do
not qualify additional truth.

After locating the original 2026-08-25 09:52 KST message behind the old truth,
the user explicitly corrected their own BASE record to **550–652 s gradual
descent, 652–674 s level recovery, FULL reached within 674–675 s**. This direct
correction owns the updated [reviewed truth](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md#base-timeline-correction--2026-10-15)
and JSON. It is not an automatic adoption of the LVLM's candidate coordinates.

Consequences for earlier interpretations in this record:

- The 662–664.5 s six-frame set is mid-refill, not a top-exit window. The old
  662/663.6 s boundaries and post-663.6 absence claims are superseded throughout.
- f15776@657.9907 s is a lost output during refill, not drain. Its correctness
  remains unreviewed; a missing numeric row is not automatically a true loss.
- The old 663.6–780 s counts (42→109, 67 new) remain time-bucket measurements,
  but cannot be presented as FULL-suffix false-output counts. Neither can the
  old 670–780 s 36→97 counts. Repartition actual matched rows; do not derive
  new phase counts or false-output proportions from the old aggregate table.
- Totals 601 / 185→303 / 119 new−1 lost=118 and the f15896 IFO result remain
  valid. The 721 s user-identified non-Oil output remains in the full suffix.
- Count 674 ≤ t < 675 separately as FULL_TRANSITION; precise transition time
  and source Y remain unknown. Use 675 s as a post-transition accounting cutoff,
  never as a detector rule or invented exact annotation. The old 674 s/Y435
  anchor does not become qualified solely because timing changed.

The next Windows request is one corrected disjoint CSV table, followed by only
needed image/idx review using the existing O2 persistence workflow. Completed
total/IFO/lost-row checks and the user's corrected interval need no repeated
question. Cost-first assignment → candidate-local RGB → Oil-only Local XY stays
the approved individual trial order, followed by FULL closure and integrated
validation. No source behavior or field disposition changes in this correction.

### Historical truth reference preservation

The publication hook detected that closed browser-review run
`sample/output/s11-round2-browser-20261014-002` reused the editable truth JSON
with its pre-correction digest. To preserve that historical dependency, its exact
6,304 bytes were restored from Git `7a57064046b0c650f552f6e4d9e2ceb73002972f`
to `sample/output/s11-reviewed-truth-preservation-20261015-001/evidence/reviewed-truth-20260825.json`.
SHA-256 remains `278e4ecaf6820d5952fff81f597044b8fb5efa2f0c27f1dcd3bf25d671518a2e`.
That managed maintenance run also retains `reference-relocation.json` with the
original reuse entry, original marker digest, replacement path and reason.

The closed browser marker changes only the reuse path and adds explicit
`reuse_reference_history`; its expected truth bytes/hash, retained payloads,
measurements and verdict remain unchanged. This is a historical snapshot, not
current truth or a browser rerun. The redundant scratch marker copy was removed
by the normal closeout; no historical evidence was deleted. All 78 managed runs
pass the artifact check. The snapshot is local/ignored; the pinned Git object
remains the source for recovering its exact bytes.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `PUBLICATION-PROVENANCE`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F04`, `S11-F05`, `S11-F08`, `S11-F09`, `S11-F10`.
- First harmful stage: v1's three observation-barrier losses reach final sequence/CSV under v2. The shared non-Oil candidate is confirmed through anchor_corridor and is newly published at 721 s versus v1, with selected/CSV equality now confirmed. The f15896 seven-candidate loss is before IFO at tracklet branch compatibility; which candidate is the actual refill interface remains unknown. Zero final FULL rows remain. Incorrect transferred segment labels are not physical truth, and no new selector defect is established at 720/771 s.
- Existing feature coverage: local comparisons use ellipse/margin masks and shared preprocessing with exclusions/templates empty and Local XY OFF; new local ROI remains separate from regression inputs. Windows intake reports initial FULL/OFF, UNKNOWN/OFF and FULL/ON with the same window/cadence/Glass IDs, and FULL/FULL/BASIC trace. Actual Windows ROI/Artifact/static preparation values are not supplied by the returned table; bundle names do not establish configuration. User excludes hash/environment checks for this read-only intake.
- Execution scope: earlier v2 implementation/local verification remain recorded above. Current documentation-only work records the received disjoint total/IFO result and applies the user's explicit BASE timing correction to the canonical truth and Windows counting procedure. Historical bucket measurements stay intact; their obsolete phase/false-output interpretations are superseded. No private media or bundles are inspected locally, no detector source changes or new experiments run, and no physical interface is inferred from a selected tracklet or LVLM estimate. Existing ROI/Artifact coverage unknowns remain unchanged; exact correspondence still requires displayed-image human review.
- Logic-map impact: NONE — this intake distinguishes the existing raw, phase, selector and final-publication responsibilities; v2 ownership and the map updated in `4c72ebb` remain unchanged.
- Failure-registry impact: NONE — existing barrier, identity and provenance entries cover this trial; no physical failure is declared solved by preflight.
