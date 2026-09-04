# S11-R20 Windows Evidence Consolidation and Reuse Inventory

**Status:** `FIELD FAIL / PUBLICATION PROVENANCE PASS — DESIGN INPUT ONLY`

## Scope and evidence boundary

This record consolidates the closed R20 Windows report intake for the private
sample `windows_sample1_heating_coldstart` and inventories repository owners
that a fresh design may reuse. It is R20-only. It does not perform a new
Windows investigation, compare R19 revisions, choose a successor mechanism,
or claim that any behavior is implemented or field-qualified by this record.

The private Windows bundle, raw trace/checkpoints, source video, source hash,
and frame-exact reviewed-Y annotations are not available in this checkout.
The Check01–Check07 measurements below are therefore explicitly attributed to
the user-authorized intake. Repository documents are used as current authority
where available; absent bundle claims remain `USER-REPORT / NOT LOCALLY
VERIFIED`. The essential findings are reproduced here so this record does not
depend on an external home-directory intake path.

The repository's current implementation and local evidence remain separate
authority:

- [current logic map](../../20-architecture/s11-current-detector-logic-map.md)
  names executing owners;
- [R20 architecture](../../20-architecture/s11-r20-delayed-drain-reacquisition-architecture.md)
  and [R20 validation contract](../../30-validation/s11-r20-delayed-drain-reacquisition-validation.md)
  define intended scope and acceptance;
- [R20 local evidence](s11-r20-delayed-drain-reacquisition.md) records local
  validation only (`LOCAL PASS / WINDOWS REQUIRED`); and
- [reviewed truth](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md)
  (the canonical path is linked below in the source register) owns physical
  interval behavior, not detector output.

## Source register and availability

| Source | Availability | Use and limits |
|---|---|---|
| `docs/30-validation/windows-sample1-heating-coldstart-reviewed-truth.md` | Repository, tracked | Canonical interval/ordering truth. No source hash or exact Y anchors; private video is not stored. |
| `docs/50-diagnostics/s11/s11-r18-windows-causal-closure.md` | Repository, tracked | Transferred R18 causal record and provenance boundary. It is not a locally replayable Windows bundle. |
| `docs/60-evidence/s11/s11-r20-delayed-drain-reacquisition.md` | Repository, tracked | R20 local tests/replay/provenance/performance evidence. It does not exercise or qualify the private Windows case. |
| `src/oil_tracker/adapters/vision/` and `tests/` | Repository, tracked | Current code and test owners used for reuse inventory; source inspection is not a Windows result. |
| External user-supplied workflow intake | External user-supplied provenance (not repository evidence) | Provenance for Check01–Check07 report statements reproduced below; exact artifact path is retained in workflow metadata, not this portable record. |
| External workflow metadata | External workflow metadata (routing only; not detector evidence) | Base/phase routing only; its `evidence` and `findings` arrays were empty at intake. Exact artifact path is retained outside the repository record. |
| User-reported current source hash | User-authorized intake, not locally verified | `fb03d7428c1711f7853dc176c869243cd456f664889cdce4e61d7c2918a1060b`; an attribute of the reported current source video only, not a repository-verified hash or historical run/binary identity. |
| `sample/*.mp4` and ignored `sample/output/` bundles | Repository workspace, local corpus | Four local sample videos and historical local outputs only; they are not the private Windows sample and cannot verify Check01–Check07. |
| Private R20 Windows bundle/checkpoints/raw trace | Not present | No local path, hash, byte identity, or independent replay claim is made. |

The user-reported R20 bundle identity is
`sample/oil_level_analysis_R20개선_add_artifact_modify_20260902_141443`, run
`abf69f7d-487d-4396-b13b-6a2abe7917f2`, resolver
`r20-delayed-drain-reacquisition-v1`. This name and run ID are retained as
intake provenance only; no matching local bundle was found.

## Correction precedence and interpretation contract

The reviewed-truth document has precedence over detector output, graph shape,
prior selected rows, and stale reports. Targeted corrections in this record
supersede earlier pasted interpretations where the raw bundle is unavailable;
they do not turn a user report into independent verification. Conflicts that
cannot be resolved locally remain unknown.

- Source coordinates are `source_frame_y` pixels and increase downward. Source
  timestamps are seconds; offsets are decoded-frame positions. A rising
  interface normally has decreasing source Y, and a falling interface has
  increasing source Y.
- `current`/raw candidate fields, completed `sequence` fields, and `public`
  sample/CSV fields are separate layers. A finalized sequence-to-CSV match is
  publication provenance, not physical accuracy.
- Tracklet IDs, row hypotheses, owner-chain IDs, and release sources are
  diagnostics/ownership metadata with distinct semantics. A selected delayed
  tracklet is not proof that its seed was the original physical interface.
- `release_evaluations` are evaluation records, not raw-proposal counts or a
  sequential funnel. A debug label or modal failed predicate is not, alone,
  the first harmful stage.
- The current checkout computes lifecycle `_rows` with the median of member Y
  values ([`oil_phase_lifecycle.py:2921`](../../../src/oil_tracker/adapters/vision/oil_phase_lifecycle.py#L2921))
  and tracklet row hypotheses with the median
  ([`oil_interface_tracklets.py:482`](../../../src/oil_tracker/adapters/vision/oil_interface_tracklets.py#L482)).
  Check07A's private-report arithmetic-mean wording and the four-member Y252
  arithmetic remain `USER-REPORT / UNVERIFIED`; no raw member checkpoint is
  available to reconcile them. Current source semantics therefore must not be
  presented as proof that the historical report used the same source/binary.

## Consolidated field result

The intake reports 1,202 rows (601 per Glass), with canonical first-sample
override for `479.9795` seconds. It reports finalized Oil `36` and Foam `18`
rows, with sequence-to-CSV matching. Those are publication/provenance claims,
not accuracy claims, and the bundle is not locally present.

| Scope | Reported observation | Disposition |
|---|---|---|
| Base Oil | Visible drain and rapid-refill behavior had `0` publication | **FAIL**; exact Y and earliest physical loss are not evaluated/proven. |
| Base Foam | `0` publication | Compatible with reviewed Foam absence, but does not qualify Oil behavior. |
| Accum Foam | `7` pre-672 published rows where reviewed Foam was absent | **FAIL** for field behavior; episode-confirmation provenance is reported PASS. |
| Overall R20 field behavior | Base/Accum report does not meet reviewed physical behavior | **FAIL**; no field qualification. |
| Publication provenance | Finalized candidate → sequence → CSV rows reportedly match (`36` Oil, `18` Foam) | **PASS as reported**, not locally verified and not an accuracy result. |
| Delayed route | `0` numeric publications in the delayed route | Target was ineffective in this report; this is not proof that the bounded design is universally invalid. |

## Nine-segment disposition

The reviewed-truth authority requires all nine segment IDs. The table below is
the complete disposition possible from the user-report intake. A segment-level
count, selected-Y range, or physical identity is not inferred from a Glass-wide
count. `NOT_EVALUATED` means the report did not provide the evidence needed for
that segment, not that the segment passed or failed.

| Segment ID | Reported observation available here | Disposition |
|---|---|---|
| `WS1-BASE-FULL-PREFIX` | Base has `0` reported Oil and `0` Foam overall; no segment-level row split | `NOT_EVALUATED` for segment attribution; reviewed truth expects no boundary |
| `WS1-BASE-DRAIN` | Reviewed visible drain is reported with `0` Base Oil publication | **FAIL** at interval behavior; exact Y/first loss `NOT_EVALUATED` |
| `WS1-BASE-RAPID-REFILL` | Reviewed visible rapid refill is reported with `0` Base Oil publication | **FAIL** at interval behavior; exact Y/closure `NOT_EVALUATED` |
| `WS1-BASE-FULL-SUFFIX` | Base has `0` reported Oil and `0` Foam overall; no segment-level row split | `NOT_EVALUATED` for segment attribution; reviewed truth expects no boundary |
| `WS1-ACCUM-EMPTY` | No segment-level final Oil/Foam split is available in the intake | `NOT_EVALUATED` |
| `WS1-ACCUM-ENTRY-SPLASH` | Seven final Foam rows were reported before the reviewed `672 s` Foam boundary; Oil presence is not segment-joined to truth | **FAIL** for Foam absence; Oil identity/direction `NOT_EVALUATED` |
| `WS1-ACCUM-FOAM-LAYERED` | No report evidence proves the reviewed upper-Foam/lower-Oil ordering in this segment | `NOT_EVALUATED` |
| `WS1-ACCUM-POST-FOAM` | No segment-level final Foam absence/Oil-owner evidence is available | `NOT_EVALUATED` |
| `WS1-ACCUM-DRAIN` | `22` reported Oil rows occur in `711.0020–724.0150 s`, but no reviewed-Y/member join is available | `NOT_EVALUATED` for physical identity/accuracy; overall field remains **FAIL** |

## Check01–Check07 corrected observations

All entries in this section are `USER-REPORT / NOT LOCALLY VERIFIED` unless a
repository authority is explicitly named. “Observation” is what the intake
states; “bounded reading” records the narrow interpretation allowed for fresh
design work; “unknown” prevents an unsupported causal upgrade.

### Check01 — delayed-chain seed and continuation

The intake reports the delayed attempt consumed transition at `684.5172 s`,
offset `409`, tracklet `000396:0196`; active offsets `409/410` had current Y
`370 -> 366`, net `0 -> -4`, so positive-progress qualification failed. The
later `685.5182 s`, offset `411` observation is the reset/barrier-label event
carrying `step_bound`, not the consumed transition; no rearm followed. The
selected delayed tracklet field means “delayed release,” not seed identity.
`step_bound` is a continuation matching failure, not frame-count expiration and
not the positive-progress predicate itself. The first drain release at
`711.002 s` was reported direct.

**Bounded reading:** delayed-chain evaluation reached a bounded continuation
failure/consumption boundary; it does not prove that the route was never
evaluated or that all candidate evidence was absent.

**Unknown:** the specific failing continuation predicate requires matched
observed-row and policy evidence from the missing bundle/checkpoint.

### Check02 — owner loss and a sufficient continuation blocker

The prior accepted drain owner was reported as `000484:0257` at `724.015 s`,
Y `365`. At `724.5155 s`, an eligible candidate at Y `345` existed. The
reported reversal threshold was `365 - 6.9984 = 358.0016`; the candidate failed
that reversal check, while absolute jump `20 <= 32` passed. This is a
sufficient continuation blocker, not necessarily the first or only failed
predicate. No successor qualified in the report; a previously disputed
successor count is intentionally omitted.

**Bounded reading:** the report places the observed block at
`OIL-PHASE-DRAIN`, but the actual visible-interface cause is unproven. The
debug residual `GLOBAL_PATH_OR_RUN_BOUND` is not causal authority.

### Check03/03A — re-entry closure

Termination was reported at `726.5175 s`, offset `493`; the last accepted row
was offset `488`, with `maxlost=3`. There were `108` post-termination frames
and `550` reconstructed rows. Of the initial `548` confirmed failures, two
were reclassified by 03A as nonqualifying: offsets `512/513`, tracklet
`000504:0270`, Y `368/366`; strict material was false because
`tracklet_material_conflict=.6199 >= .45`, and strong motion was false because
`motion_trajectory != anchor_trajectory`. The report therefore states all
`550` rows nonqualifying and `0` re-entry.

The prior owner’s last sequence candidate was reported at offset `501`,
`730.4797 s`; grouped Y `356.5` came from members `358/355`.

**Bounded reading:** this closes a reported predicate path, not physical
interface correctness. Any branch claim must be tied to actual source and
source identity when the bundle is available.

### Check04/04A — Base release funnel

The report states `DRAIN=225` rows, rapid-refill `=3`, and Oil `=0` for both
(**FAIL**). Direct DRAIN had `265` evaluation records across `194` frames;
first failed direction was `191`, minimum progress `62`, entrance `12`, with
`0` passed. The target direct cohort had `267` records including refill `2`.

Recovery DRAIN admission had `265` rows all passing common admission; anchor
requirement passed on `198`; combined anchor+entrance seed eligibility was
`192`, with first failures anchor `67` and entrance `6`. The 04A entrance
table’s `192` is a conditional cumulative pass, not standalone entrance
success; standalone direct entrance was false on `20` rows.

Active chain summaries covered `202` frames and `269` summary entries with
`25` visible incarnations. Exact creation-event count is **NOT_PROVEN** and
must not be called `269`. Net bins were negative `58`, zero `38`, positive
below minimum `173`, at/above minimum `0`; the reported threshold was
`19.305343511450385`, with first failure positive `96` / minimum `173`.
Handoff ambiguity was reported at offset `263`, `611.4859 s`. Base reasons
were initial barrier `600` plus ambiguity `1` (`601`); target reasons were
`227 + 1` (`228`).

**Bounded reading:** this is an observed initial-full lifecycle block with no
numeric Base publication. The actual interface’s first harmful stage remains
unknown. No threshold tuning follows from these bins.

### Check05/05A — Foam false positives and episode provenance

Seven false-positive timestamps were reported:
`658.9917`, `659.4922`, `659.9927`, `668.5012`, `669.0017`, `671.0037`, and
`671.5042` seconds. Current raw evidence existed for four
(`659.4922`, `659.9927`, `669.0017`, `671.5042`); three were pending/current
`None` and later episode-finalized. The intake states all seven were final
episode-confirmation authority (**field FAIL**, publication provenance PASS).

Tracks `0020`, `0032`, and `0036` were reported; `0036` crosses the `672 s`
truth boundary. Later evidence was included in segment evaluation, but the
necessity of post-672 evidence was **NOT_EVALUATED**; no counterfactual is
claimed. Candidate `selected` is not the same as current raw publication;
`positions.raw_foam_y` is the relevant raw field. Raw object identity remains
unknown.

### Check06/06A/06B — entry and intermittent fill

The reported interval `653.4862–678.5112 s` has `51` frames: `14` present and
`37` missing. Entry missing `32` was divided into allowed-empty `30`,
unresolved `668.5012` one, and owner-absent `669.0017` one. Intermittent
missing frames were `670.0027`, `672.5052`, `673.0057`, `676.0087`, and
`676.5092`; each reportedly had an allowed owner but no same-frame candidate.
The harmful stage—raw detection versus association—is unknown and must not be
called `OIL-TRACKLET` without evidence.

The report corrects owner `000248:0098` at `653.4862–657.4902`: trace
`owner_chain` derives `_FillChain.owners` through `_selected_owner_chain`,
which is real chain metadata, not a display annotation. Dynamic/established
owner first appeared at `668.5012`, tracklet `000351:0147`, with transition at
`673.5062` to `000381:0181`; retro onset `668.0007` is a distinct event.

At `668.5012`, two nodes shared rhid `oil-row:000377:004`; the serialized rhid
does not prove publishability. Confidence was reported as partial `4/13`
components; the runtime confidence threshold is not proven. A continuing-
anchor exception failed on provisional status, motion trajectory, and texture
conflict `.9935`; the full publishability-OR-confidence branch is unresolved.
Selector abstain was confirmed `0`, unresolved `1`. Grouping, owner metadata,
and publishability must remain separate.

### Check07/07A — final gap, delayed evaluation, and row aggregation

The last publication was reported at `678.5112 s`, followed by release at
`711.0020 s`: elapsed `32.4908 s`; first missing `679.0117 s` to release was
`31.9903 s`, or `64` missing samples. Phase counts were filling `4`, open
`60`, draining `0`. `delayed_reacquisition_evaluated=True` covered `60`
frames, not `60` seed attempts or `60` evaluation records; publication was
`0`.

At `679.0117 s`, prior owner `000381:0181` had zero candidate nodes in both
layers, while established context retained owner Y `238`. Direct gap
evaluation had `95` records, all failing: downward direction `88`, maximum
jump `6`, current material conflict `1`. The first release tracklet was
`000448:0233`; its comparison around `710.0010 s` changed material conflict
`.657 -> .347` from false to true while other predicate booleans remained true.
“Previous” means the same-tracklet evaluation, not simply the previous sample.

Release evaluation Y `252` and finalized selected Y `247` reportedly share rhid
`oil-row:000462:002` with four members, and selected Y `247` equals sequence
and CSV Y. The current checkout's lifecycle and tracklet row aggregation is
source-backed `median`; 07A's private-report arithmetic-mean wording and its
four-member arithmetic remain `USER-REPORT / UNVERIFIED`. Without the raw
row-join checkpoint, the relationship between that report wording and the
historical run remains **UNRESOLVED**.

## Observation, inference, and unknown ledger

| Class | Consolidated content |
|---|---|
| Observed / repository-backed | Reviewed segment behavior and source-coordinate contract; current R20 owner/version paths; local R20 validation and four-video provenance evidence; no local private bundle. |
| Observed / user-reported | R20 bundle/run identity, 1,202 rows, finalized 36/18 counts, Check01–Check07 values, Base/Accum field dispositions, and publication matching. |
| Bounded inference | The delayed/owner-loss report is useful design input at lifecycle/phase and bounded-chain seams. Check02’s reported drain-stage block is sufficient evidence of a blocker, not first-cause identity. Publication equality is necessary provenance, not accuracy. |
| Named unknown | Private source identity/hash; exact reviewed Y anchors; Base interface first loss; exact Accum drain candidate/identity and snapshot behavior; owner-bounded selector abstain predicate; Check01 continuation predicate; Check03 branch/source identity; Check04 chain creation count; Check05 raw object identity/post-672 necessity; Check06 raw-versus-association stage and confidence branch; Check07 mean-versus-median and row-member joins. |

## Source-owner and reuse inventory

This inventory names compatible existing owners and mechanisms only. A fresh
design gate must independently decide `REUSE`, `ADAPT`, or `NEW`; this record
does not select an architecture or a behavior change.

| Current owner / path | Reusable capability | Boundary to preserve |
|---|---|---|
| `FRAME-EVIDENCE` / `OIL-RAW-EVIDENCE` / `OIL-PROPOSAL` / `OIL-CANDIDATE` — `src/oil_tracker/adapters/vision/phase_frame_detection.py`, `oil_shadow_observations.py`, `phase_candidate_assembler.py` | Bounded source-frame masks, raw observations, proposals, candidate-family provenance and evidence-availability diagnostics. | A present proposal is not a reviewed interface; missing evidence remains unavailable, and top-k/proposal counts cannot be called recall or authority. |
| `OIL-AUTHORITY` — `src/oil_tracker/adapters/vision/oil_observation_resolver.py`, `oil_candidate_authority.py`, `oil_phase_identity.py` | Typed `HARD_INVALID`, `CANDIDATE_ONLY`, `CONTINUATION_ELIGIBLE`, `ANCHOR_ELIGIBLE`; common-admission, phase/material/optics diagnostics. | Candidate presence is not physical identity; candidate-only/continuation rows do not bootstrap a chain. |
| `OIL-TRACKLET` — `src/oil_tracker/adapters/vision/oil_interface_tracklets.py` | Bounded directed IDs, one-to-one assignment, confirmation profiles, explicit handoff and ambiguity termination. | Do not stretch a tracklet across delayed distance, borrow IDs, or call motion/direction alone identity. |
| `OIL-PHASE-INITIAL` / `OIL-PHASE-FILL` / `OIL-PHASE-DRAIN` — `src/oil_tracker/adapters/vision/oil_phase_lifecycle.py` | Initial EMPTY hard gate; coordinate-free FULL barrier; established-fill context; direct and bounded release/continuation state; explicit release-source and failure diagnostics. | State is not a coordinate; ownerless context must be bounded; ambiguity, material opposition, reversal, gap and expiry fail closed. |
| `OIL-SELECTOR` — `src/oil_tracker/adapters/vision/oil_interface_selector.py` | Lifecycle allowed-ID filtering, fixed-lag selection, owner-chain transitions, publishability assertions and UNKNOWN. | Selector cannot recover an upstream missing owner or invent a delayed identity. |
| `OIL-PROJECTION` — `src/oil_tracker/adapters/vision/oil_observation_resolver.py` | Selected same-frame candidate projection; no-coordinate state/unknown; raw-vs-sequence provenance. | Never copy snapshot/seed Y, interpolate, carry, or backfill. |
| `FOAM-CANDIDATE` / `FOAM-IDENTITY` — `src/oil_tracker/adapters/vision/foam_front_detector.py`, `foam_material_identity.py` | Independent raw Foam material/topology evidence and bounded observation-only identity/opposition. | Current/pending/finalized labels and material opposition do not by themselves prove a Foam episode or veto unrelated Oil. |
| `SEQUENCE-COMPOSITION` / `FOAM-EPISODE` — `src/oil_tracker/adapters/vision/observation_sequence_resolver.py`, `src/oil_tracker/adapters/vision/foam_episode_resolver.py` | Single Oil-then-Foam composition point; independent Foam candidate/episode authority and selected-Y provenance. | Foam cannot mask Oil or repair Oil; no combined Foam change is implied by the seven false rows. |
| `PUBLICATION-PROVENANCE` / `CSV-PUBLICATION` — `src/oil_tracker/application/services/detection_processing.py`, `src/oil_tracker/application/services/analysis_outcome.py`, `src/oil_tracker/adapters/reporting/csv_exporter.py` | Independent `oil_is_valid`/`foam_is_valid`; final sample/event and CSV serialization; exact selected-Y equality checks. | Publication PASS does not establish field accuracy or reviewed physical identity. |
| `TRACE-PUBLICATION` — `src/oil_tracker/adapters/storage/jsonl_debug_trace_writer.py` and lifecycle diagnostics | Layered current/sequence snapshots, release source, owner chain, predicate/failure telemetry and provenance. | Trace labels are observational; they cannot alter admission, ranking, selection, or publication. |
| Validation/diagnostic owners — `tests/unit/test_oil_phase_lifecycle.py`, resolver/tracklet/trace/coordinator/integration tests, and R20 local evidence | Existing two-sided lifecycle, ambiguity, material, bounded-resource, same-frame and local non-regression checks. | No source tests or detector run were authorized here; reuse means future design/validation input only. |

## Design-gate constraints and non-goals

The evidence supports a narrow, evidence-preserving design discussion but does
not dictate a mechanism:

- Keep Base’s reviewed full-prefix/suffix no-interface safety and treat its
  visible drain/refill publication failure as **FAIL / first stage unknown**.
- Keep Accum’s initial-empty suppression and distinct fill/drain ownership;
  do not convert a delayed row, snapshot, state prior, debug label, or graph
  bridge into a coordinate.
- Keep independent Foam authority and publication; the seven pre-672 rows are
  not permission to couple Foam to Oil or to infer a counterfactual.
- Keep current/finalized/public layers, source-Y units, row/track/owner IDs,
  explicit publication provenance, fail-closed ambiguity, and bounded state.
- Do not widen thresholds, add a Glass/video/timestamp/Y branch, merge IDs,
  interpolate/carry, regenerate goldens, or claim a Windows PASS from local
  four-video evidence.
- Decide separately whether any next step is behavior change, instrumentation
  only, or a gated design; this record does not make that decision.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `OIL-PROPOSAL`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `FOAM-EPISODE`, `SEQUENCE-COMPOSITION`, `PUBLICATION-PROVENANCE`, `CSV-PUBLICATION`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F07`, `S11-F08`, `S11-F09`, `S11-F10`
- First harmful stage: Base visible drain/refill and Accum delayed/owner-loss boundaries are not proven beyond the reported lifecycle/continuation blockers; Check06 raw-detection versus association stage is unknown; Foam false publications are observed at episode confirmation; publication is not the harmful stage.
- Logic-map impact: NONE — this consolidation records field/report provenance and reuse inventory without changing current implementation ownership or control flow.
- Failure-registry impact: NONE — existing F02/F04/F05/F06/F07/F08/F09/F10 mechanisms remain the causal guards; no new durable mechanism is asserted.
