# S11 Physical Interface Evidence Repair Validation

**Contract status:** proposed acceptance for the
[physical-interface design](../20-architecture/s11-physical-interface-evidence-repair-design.md).
The cases below are required future checks, not completed PASS results.

The original extraction stage is the trace-only
[Interface Observability Witness Architecture](../20-architecture/s11-interface-observability-witness-architecture.md).
Its [public baseline probe](../50-diagnostics/s11/s11-transparent-interface-detector-direction-assessment.md)
completed only candidate/descriptor characterization: every one of 13 usable
truth frames retained a candidate within 8 px under seven photometric variants,
while a median 23–24 Oil candidates and 3–4 near-truth candidates remained per
frame. This does not satisfy Evidence gate A, label remote candidates as false,
or justify a classifier threshold.

## October 15 exploratory comparison

This bounded comparison is authorized separately from full physical-witness acceptance.
Default launch must preserve R22 outputs. With the option enabled, cover current
stationary/upward bounded-confirmed observation under initial FULL, normal downward release,
loss and reacquisition, multiple-owner ambiguity and permutation, typed identity
contradiction, material/Artifact/hard-invalid opposition, image-supported no-interface
states, initial EMPTY and post-fill/refill barriers. Existing stationary **drain-release**
negative tests remain unchanged; the added observation mode does not classify drainage.

Exercise actual resolver and detector construction, GUI factory propagation,
same-frame selected-candidate/sequence/CSV equality, explicit direction uncertainty,
absence of invented drain-start events and independent Foam. Debug ON/OFF must give
the same observations. Reuse existing regressions at their qualified scopes; do not
change goldens or relabel a skipped/quarantined source as a pass.

Freeze vessel-interior ROI before replay and keep it identical across OFF/ON. Existing
baseline results are reusable only for matching source/setup/run conditions. Local
physical review records both recoveries and false positives; numeric-row gain alone
is insufficient. The bounded Windows CSV/review-004 intake is now closed; the
authorized order is cost-first, RGB, then Local XY as separate comparisons. The canonical
nine segments remain required for formal field acceptance. No further model fit or
physical-witness acceptance is implied by this comparison.

Version 2 additionally covers all three transferred evidence shapes: confirmed
continuation-only rows, confirmed direct rows below anchor authority, and provisional
rows already admitted by bounded confirmation. Verify a never-admitted provisional
row still fails, and an incompatible anchor cannot lend identity to another row.
Current observations may extend toward the top but ordinary loss must still be
UNKNOWN; this stage does not add top-exit FULL inference. Retain the v1 local
comparisons and compare v2 on the same frozen inputs without relabeling gains as
physical recall. GUI wiring is unchanged; its passing propagation checks are
reusable, while actual detector/resolver construction and output provenance run
on the changed source.

## October 16 top-exit FULL comparison checks

- Explicit OFF preserves the v2 reference and all numeric candidate/CSV values.
  ON must also preserve every numeric Oil node, independent Foam coordinates and
  candidate admission; only supported coordinate-free state rows may change.
- Positive: one mature selected owner rises over the bounded confirmation window
  to the configured top, then disappears on a usable unopposed frame. Check FULL
  at disappearance and continued absence, empty raw/smoothed Oil coordinates,
  exact source-frame witness and distinct temporal-state flags/validity/CSV.
- Negative/reset: mid-height loss, stationary top, downward/reversed trajectory,
  owner switch, provisional/unconfirmed or material-opposed owner, competing or
  unselected admitted current Oil, censored spike, current EMPTY, black/glare/
  unavailable raster, missing quality fields and stale/nonpositive sample time.
  New interface after FULL remains numeric and ends the old state episode;
  subsequent blank must not resume stale FULL. No initial-FULL prior-only output.
- Exercise detector/resolver and every GUI factory/launch flag, final sample and
  CSV/trace publication, debug equality, permutation and bounded suffix influence.
  Compare configured geometry top with the effective mask's reachable limit;
  masked/uncertain physical exit is not a passing FULL transition.
- Windows compares ④ with ⑧ v2+top-exit-full, all three rejected mechanisms OFF.
  First check endpoint reachability and physical-top correspondence using existing
  ④ inputs. If margin excludes the endpoint band, return that small preflight and
  do not run a whole video that cannot satisfy the condition. Local evidence is
  retained in [the October 16 record](../60-evidence/s11/2026-10-16-top-exit-full.md).
  Reuse existing reviews and canonical buckets; inspect the 674–675 s transition
  and its preceding selected-owner evidence. Do not infer a missing exact exit
  frame from the timeline. Keep 721 s wrong output as the next separate task,
  reporting changes rather than censoring it under the FULL assumption.

## Top-exit v3 promotion acceptance — 2026-10-22

**PRE-REGISTERED 2026-10-22, before any detector output for new evidence was
produced or viewed.** The feasibility check before this section looked only at
retained source frames of sample5–7 (no detector output). These criteria govern
stage 2 of the
[promotion preparation](../20-architecture/s11-physical-interface-evidence-repair-design.md#october-22-top-exit-promotion-preparation):
production default ON for the IFO v2 + top-exit v3 pair. Stage 1, the
integrated-candidate designation, needs no new evidence. Criteria, bounds and
windows do not change after outputs are seen (the
[P0 comparison procedure](s11-interface-observability-witness-validation.md#local-residual-bounds-and-extremum-display--2026-10-20)).

**Arms.** Both arms run on one frozen pushed head, with the same video, Recipe,
session, sampling rate and debug level, and with cost-first, RGB and Local XY
OFF.
- **Candidate:** IFO v2 + top-exit v3.
- **Reference:** IFO v2 alone, as ④. On a Glass without a confirmed initial
  FULL, IFO v2 is inactive, so there the reference equals the production default.

**Truth.** Each new window gets a human review before its detector output is
read. Per Glass, the review records:
- the initial state at the window start;
- each transition into FULL, as a time or a window;
- each drain that starts from FULL;
- every interval that never becomes full.

Detector output is not truth. SPL#1 480–780 s is the design case and does not
count as an unseen positive.

**Evidence classes.** Timing uses C4 (±2 s of the reviewed, possibly
approximate, time). False states are classified by C5. Both bounds come from the
[October 20 bounds](s11-interface-observability-witness-validation.md#local-residual-bounds-and-extremum-display--2026-10-20).

| Class | Evidence | Pass criteria |
|---|---|---|
| **P — unseen positive** | A reviewed transition into FULL that was not used to design v1–v3. Candidates: SPL#1 after 780 s; SPL#2/3 only if the user opens them | P1: the first top-exit FULL row lies within ±2 s of the reviewed transition; a reviewed window widens by 2 s on each side. P2: no FULL row before that bound. P3: through the reviewed FULL interval every row is FULL or a D2b fail-closed UNKNOWN, with no numeric Oil row, and the episode does not end more than 2 s before the reviewed end. P4: rows before the confirmed closure equal the reference |
| **R — release after FULL** | A reviewed drain that starts while a top-exit FULL episode is active | R1: the episode ends within ±2 s of the reviewed drain start. R2: no FULL row from 2 s after the drain start until the next reviewed FULL. The first numeric Oil after the release and its C3 gap are reported, not scored here |
| **N — negative** | Every reviewed never-full interval: the four existing local controls rerun at the frozen head; sample5 (water) and sample7 (milk) under the entry conditions below; any never-full interval in the new windows, especially with the level, Foam or glare near the top | N1: zero top-exit FULL rows. N2: rows, events and report equal between the arms, ignoring `run_id` |
| **U — unchanged elsewhere** | Every run above | U1: outside pending and FULL-episode frames, every row equals the reference |

**Decision rule.**
- **Minimum evidence:** at least one unseen positive, at least one release, and
  every negative. More cases strengthen the decision but do not change the
  criteria.
- **Pass:** every criterion passes, and the net A/B/C/U comparison shows no new
  A. A pass enables the user's default decision; it does not flip the default.
- **Fail:** any failure blocks the default. Diagnose the first harmful stage;
  no tuning or threshold change follows a result (F10). A rule change is a new
  version with its own freeze.
- **Known limit:** no positive yet covers a Glass without an initial FULL that
  reaches FULL, where top-exit acts alone. Unless such a case is found, the
  default decision must state this limit.

**Local negative entry conditions (sample5, sample7).**
- **Why these two:** they are the only local recordings with an initially empty
  glass that fills.
  - sample6 is excluded: the vessel's top is outside the frame, so the ROI
    cannot hold the physical top (OTR-1 D1).
  - The two public compressor recordings are excluded for camera motion, edited
    slides and reframing.
- **Recipe:**
  - The ellipse is the vessel interior where liquid can move, from the inner
    rim to the top of the solid base.
  - It is chosen on an empty frame and frozen before any run. It is not fitted
    to the settled level.
  - Margin 0.08, production default detector settings, no exclusions.
- **Truth:** before any run, the user confirms from shown frames that each glass
  starts EMPTY and never becomes full.
- **Run:** the whole video at 2 fps, debug NONE, with a confirmed initial EMPTY,
  through the existing top-exit comparison entry in a managed run.
- **Reported, not scored:** fill-cap events (the sample4 outcome G type) and the
  initial-state reconstruction status. These inform G and E3.

**Windows SPL#4 entry conditions (2026-10-22).** Written from the user's answers
before any detector output on this recording exists. The criteria table above
is unchanged; this fixes how it applies here.
- **Source:** `SPL#4_Cooling_onoff_#2.mp4`, the user's Windows "sample4"
  ([evidence](../60-evidence/s11/2026-10-22-top-exit-promotion-evidence.md#windows-spl4-user-alias-sample4--2026-10-22)).
  - **User-reported:** 53,165,455 bytes, 4 min 20 s, 30 fps, 1920×1080. The
    first relay read 53,165,445, a typo. The request's size check stopped
    before any run, and the user confirmed 53,165,455 from the file
    properties (2026-10-22).
  - **Unseen:** a separate recording from SPL#1–3 and from the Mac
    `sample4.mp4`; no v1–v3 design step or control used it.
  - **Identity check:** the run first records its SHA-256, decoded fps and
    frame count; a size mismatch stops it.
- **Recipe:** the user's existing Windows Recipe for this recording, with its
  Artifact, unchanged.
  - Before the run, the user confirms on an overlay that each ellipse is the
    vessel interior (OTR-1 D1); otherwise the run stops.
  - The run records the Recipe SHA-256, both ellipses and the 27 % band ends.
- **Run:** 0–90 s at 2 fps with FULL debug, both arms as above.
  - Both Glasses are confirmed EMPTY at the start.
  - No compressor start; the judgment is not scored.
  - 90–260 s is neither run nor read, so it stays unseen for later evidence.
- **Truth (the user's visual review, 2026-10-22; times approximate):**
  - **BASE:** EMPTY at 0 s; Oil enters from about 11 s. FULL is reached at
    24–25 s and holds, filled with Oil, until 63 s, where a drain from FULL
    starts. The glass is not FULL after that through 90 s.
  - **Accum:** EMPTY at 0 s; never Oil-FULL in 0–90 s.
  - **Foam at the top is not FULL:** when Foam reaches the top while the Oil
    level is below it (BASE from about 65 s, Accum from about 28 s), the expected
    Oil output is not FULL.
- **Frozen windows:**

  | Glass | Check | Window |
  |---|---|---|
  | BASE | P1 | first FULL row in 22.0–27.0 s |
  | BASE | P2 | no candidate-only FULL row before 22.0 s |
  | BASE | P3 | from the first FULL row to 61.0 s |
  | BASE | R1 | episode end in 61.0–65.0 s |
  | BASE | R2 | no candidate-only FULL row in 65.0–90.0 s; no later reviewed FULL |
  | Accum | N1, N2 | 0–90 s |
  | Both | U1 | 0–90 s |

- **How the criteria read here (frozen with the windows):**
  - **FULL row:** `FULL_NO_INTERFACE` or `FULL_WITH_FOAM`. A FULL row identical
    in both arms is production-default output; it is reported, not attributed
    to the candidate. N1 counts top-exit FULL rows (`OIL_TOP_EXIT_FULL`).
  - **First FULL row:** the first row with `OIL_TOP_EXIT_FULL`
    (`TOP_EXIT_FULL_CONFIRMED`).
  - **P3 rows:** each carries `TOP_EXIT_FULL_CONFIRMED` or
    `TOP_EXIT_FULL_CONTINUING` (FULL), or `TOP_EXIT_FULL_FRAME_UNAVAILABLE` (the
    D2b UNKNOWN). None has an Oil coordinate.
  - **Episode end:** the row that carries the top-exit `episode_end`
    (`DRAIN_RELEASE` or `EMPTY_EVIDENCE`; the type is reported).
  - **Row equality (P4, N2, U1):** fill state, raw Oil and Foam Y, their
    validity and flags, as in ⑩. N2 also compares the Accum events and its
    report card.
  - **U1 excludes** `PENDING` rows and the episode, from the first FULL row to
    the row before the episode end.
- **Timing refinement (the user's choice):** the approximate windows are scored
  first.
  - **Undecided:** the first FULL row lies within 2 s outside its window
    (20.0–22.0 s or 27.0–29.0 s), or the episode end does (59.0–61.0 s or
    65.0–67.0 s). That check is UNDECIDED, not failed.
  - **Review:** a Windows human review then looks only at 22–27 s or 61–65 s, on
    raw frames without overlays. It records the first frame at which the glass
    is full of Oil, or at which the level is visibly below the top.
  - **Scoring:** the check is scored once against that time ±2 s, and the
    result is final. The windows that depend on it (P2's bound, P3's end, R2's
    start) move with it.
  - **Elsewhere:** further out, the check fails without review; inside its
    window, it passes without review.
  - **Limit:** that review would come after the output is seen.
- **What it supplies:**
  - **BASE:** one unseen positive and one release. On an EMPTY start IFO v2 is
    inactive, so top-exit acts alone: the known limit's missing case.
  - **Accum:** one negative with Foam at the top.
- **Local negatives:** they ran at `cba4067`/`60d6a9d`. If the frozen head of
  the SPL#4 run differs, the six controls rerun there before the decision.

## Contested fill-owner gate checks — 2026-10-22

**Status: FROZEN 2026-10-22 with the design, before any code or run.** These
checks accompany the
[contested fill-owner gate](../20-architecture/s11-physical-interface-evidence-repair-design.md#october-22-contested-fill-owner-gate).
They do not change after results.
**Local result:** [PASS on all six controls](../60-evidence/s11/2026-10-22-fill-owner-contest-local.md)
(run at `2cb0b52`).

**Unit (synthetic lifecycle layers):**
- A contested survivor gives `FILL_OWNER_CONTESTED` with an empty allowed set.
- A single owner that was never contested publishes as before.
- After a contest, a fresh uncontested chain publishes as before.
- A handoff successor of a contested chain is gated.
- Re-entry and a current-anchor handoff by a contested tracklet are gated.
- Fill-span completion and drain releases are not gated.
- The marks clear at `FILLED_BARRIER` and at `DRAINING`.
- With the option OFF the lifecycle output is identical, and the existing suites
  pass unchanged.

**Wiring:**
- The flag reaches the lifecycle through the real GUI detector-factory paths.
- The detector and the completed resolver versions carry
  `+fill-owner-contest-v1`.
- Cost-first, candidate RGB and Local XY combinations are refused.

**Local controls.** Six controls with the same Recipes, ROI inputs and initial
states as the top-exit negatives (run 003), at 2 fps with debug NONE.
- **Arms:** the reference is IFO v2 + top-exit v3; the candidate adds the gate.
- **Identity anchor:** the reference arm must equal the kept top-exit arm of runs
  001/002 (rows, events, report; `run_id` aside). Otherwise the run is void.

| Check | Controls | Prediction (pass condition) |
|---|---|---|
| C1 identity | base_sample_1-full, sample2-full, sample4-interior-full, sample4-original-unknown | None reports `FILL_OWNER_AMBIGUOUS` in the reference. Rows, phases, events and report are equal between the arms (version aside) |
| C2 removal | sample5-empty | 32 frames become `FILL_OWNER_CONTESTED`: 20.0–22.0, 35.5–36.0 and 40.5–52.5 s. The 17 numeric rows at 20.0, 36.0, 40.5, 41.5, 42.0, 42.5, 43.5, 44.0, 46.0, 46.5, 47.0, 48.0, 48.5, 49.0, 49.5, 50.0 and 50.5 s become UNKNOWN. The rows at 8.5, 9.0, 24.5, 25.5, 54.0 and 54.5 s are unchanged |
| C3 known loss | sample7-empty | 24 frames become `FILL_OWNER_CONTESTED`: 22.0–33.5 s. 0016's 20 rows (22.0–31.5 s) become UNKNOWN; the 9.5 s row is unchanged. The user judged these rows correct before any run, so this is a pre-registered loss of 20 correct rows, accepted by the user. Exactly these rows must go; the loss is reported against C2's 17 removed wrong rows |

**Stop conditions.** Any of these fails the check, with no promotion and no
retuning:
- a numeric Oil row added, or moved in Y, in any control;
- any difference in a C1 control;
- any Foam coordinate change;
- a FULL or EMPTY state change;
- a gated frame outside the predicted set.

Events, the retrospective and the report may change in C2 and C3 only as a
consequence of the removed rows. Every such change is reported.

**Windows (step 7, later):**
- **SPL#4 0–90 s, reference vs candidate.** Predicted: the 14 rows at
  27.5–34.0 s become UNKNOWN if 0018 shared the 22.5–27.0 s ambiguity, and
  nothing else changes.
- **SPL#1 under ⑩ conditions.** Rows change only after a `FILL_OWNER_AMBIGUOUS`.
  Every changed row is listed with its phase reason and owner.
- **Promotion** is a separate decision.

## Cost-first comparison checks

The option repeats the frozen first-sort intervention; it does not claim physical
identity or full acceptance. Verify these boundaries before the Windows handoff:

- Default/explicit OFF preserve R22 and FULL+observation-v2 behavior and versions.
  The new flag is independent of the initial-FULL flag and reaches all four GUI
  detector factories, Oil config, tracklet policy and serialized runtime versions.
- A competing established/provisional predecessor case changes the chosen
  association under ON, but does not give the provisional track anchor evidence
  or numeric authority. Reciprocal matching, split/crossing abstention, loss bounds,
  permutation and commit horizon retain their established controls in both modes.
- Exercise the completed resolver and existing publication contracts. A lower
  assignment cost cannot bypass material/identity vetoes or turn missing evidence
  into FULL; final values remain same-frame selected candidates.
- Reuse the initial-FULL replay runner and frozen ROI inputs for base_sample_1 and
  sample4. Compare v2 against v2+cost-first with raw-input equality, candidate/CSV
  provenance, all changed rows and final Foam effects. Keep previous v2 records
  as OFF equality controls; debug capture must not change observations.
- On Windows use the corrected buckets and qualified multiple-choice review-004
  evidence, not a unique-Y accuracy score. Check f15896, 721 s and the FULL suffix
  along with changed scenes and Accum/Foam. Do not reopen the full CSV audit or
  promise to repair every blank frame. Source/ROI/settings must match the pair.

Top-exit FULL is after the three comparisons, not an entry requirement. Windows
results can close this candidate as effect, no effect/regression, or insufficient
evidence; no follow-up threshold tuning or default promotion is automatic.

## Candidate-local RGB comparison checks

- The packaged weights must equal the frozen candidate-model artifact. Reproduce
  all available retained variant logits within the prior `1e-4` tolerance and
  every retained decision, including the known rim false accepts. Shared-strip
  convolution must agree with independently evaluated patches.
- Preserve exact floor/ceil support, effective/glare masking, source/crop mapping
  and the excluded central gap. Missing patches and variant disagreement remain
  in the population as UNAVAILABLE/UNKNOWN, never fabricated zeros or negatives.
- RGB compatibility is only an additional completed-Oil eligibility condition:
  it cannot override hard-invalid/artifact/phase/ownership rejection. Disabled
  execution must neither load weights nor annotate/change raw inputs.
- Verify the real GUI factory's four detector entry paths and independent
  initial-FULL flag, reject cost-first stacking, and identify ON in detector and
  completed resolver versions. Test missing/corrupt weights and missing enabled
  annotations without a silent fallback.
- Reuse the existing local comparison runner on frozen base/sample4 inputs.
  Compare OFF with retained v2, compare unmodified raw proposal/Foam content
  after removing only added RGB annotations, and check exact same-frame
  selection/CSV equality. Compare final Foam and FULL/NONE debug results.
- Windows compares ④ v2 with ⑥ v2+RGB, reusing review-004/005 uncertainty and
  the canonical BASE/Accum timeline. Neither positive model scores, local
  arithmetic equality nor fewer false outputs establishes field acceptance.

## Validation layers

1. Exercise raster-derived witnesses before authority. Tests which directly
   inject `representation_support` or a success enum cannot validate extraction
   or independent support. Such helpers remain appropriate for isolated state
   transition tests only.
2. Compose witness → authority → tracklet → lifecycle → selector → projection.
   Check the selected physical structure and exact provenance, not numeric
   count alone. Include multiple candidate competitors and permutations.
3. Run the relevant existing R22/R21 controls and public-video truth/replays.
   Record the implementation baseline, candidate identity and runtime. Any
   changed tracking fingerprint requires row-level physical explanation; do not
   replace truth/goldens merely to obtain PASS.
4. Qualify the implemented candidate on target Windows separately. Human-reviewed
   checkpoints and complete canonical segments remain field acceptance input.

## Required two-sided controls

Retain the [October 16 peer screen](../50-diagnostics/s11/2026-10-16-corroboration-peer-screen.md#same-frame-positive-and-rim-counterexample)
as an E3/E4 counter-control: the accepted f1140 material candidate and the
separately reviewed same-frame rim must not be separated merely by raising the
legacy scalar support floor or requiring zero-support legacy seed authority.
Preserve actual raw BoundaryKind when reusing the frozen model-preparation
inventory; seven historical unreviewed Foam entries were declared Oil there.
The complete 187-unit roster and original labels remain unchanged. This
candidate-level negative result adds neither a completed-output loss claim nor
Windows efficacy or a new universal numeric acceptance threshold.

The [native-geometry screen](../50-diagnostics/s11/2026-10-16-corroboration-geometry-screen.md#executed-results)
adds an E3/E4 availability control: none of the 85 positive-contribution pairs
has both captured native paths. Its common-native G2 comparison is **not
assessable**, not a physical failure/pass. Verify the existence and lineage of
both measured contour inputs before testing a consumer. A scalar center, peak
hull or nearest edge cannot fill a missing native path; a separately re-observed
contour must be typed and qualified as new evidence. Preserve weak/practically
accepted candidates, all alternatives and missing-input records. Rejecting the
entire support population cannot satisfy positive preservation. The 4,136 basic
grayscale band checks (2,867 distinct windows) validate arithmetic only, not
material-role discrimination, detector output or report comprehension.

The fixed [CRW-1 paired-raster screen](../50-diagnostics/s11/2026-10-16-raster-partition-screen.md#execution-result)
adds measurable sector hypotheses without qualifying a continuous native contour.
Its matched-column/position masks, tied alternatives, censoring and exact raster
lineage are required input controls for reuse. Retain f1200's accepted/other
partition counts of 3/4 and f1320's 2/2 tie as counterexamples to count-only
physical authority; do not raise/lower that cutoff or shift the extraction window
to fit them. A shared re-observed row is the same extraction, not independent
support. The direct-loop arithmetic result cannot establish semantic independence.
Evaluate useful preservation at reviewed-frame/episode scope: keeping two of four
practical alternatives can still represent the public frame. A single remaining
opposition or missing candidate is not automatically a whole-report failure;
its actual selected duration, extrema and movement impact must be measured.
Conversely, 7/8 sparse frame groups with descriptive support is not evidence that
continuous movement, Windows identity or report comprehension has improved.

| ID | Positive case | Negative / invariant | Required observation |
|---|---|---|---|
| E1 | Textured Oil/Foam interface, both proposal peers high in broad texture | Internal stripe/residue with similar scalar texture and boundary scores | Only the interface receives positive local partition evidence |
| E2 | Clean direct interface, curved or low-contrast distributed boundary | Glare, wall boundary, homogeneous opaque FULL, single-sector edge | Usable sectors, opposition and availability explain each decision |
| E3 | Independent edge and region evidence on the same contour | Duplicate candidates, renamed same-source descendants, disjoint contours at nearby median Y | Independence cannot be manufactured by candidate count or family aliases |
| E4 | Valid support with one weak representation retained as raw peer | Hard-invalid peer; missing mask/context/provenance; unavailable texture | Missing and hard-invalid evidence never grants the new high-texture route |
| E5 | High broad texture with complete positive interface witnesses through authority, phase and selection | A contradictory member/history edge mixed into the same row/tracklet | Typed material compatibility is consumed consistently; raw scalar values remain intact and true contradictions cannot be averaged away |
| T1 | Genuine rapid movement with matching distributed structure | Wrong stationary stripe replaced by actual stationary interface within the old jump bound | True motion retains identity; false-to-real association splits or abstains and does not contribute displacement |
| T2 | Genuine reversal, curved contour, photometric change with supported identity | Competing branches, ambiguous registration, incompatible partitions | Direction uses only certified edges; ambiguity stays UNKNOWN |
| T3 | Bounded loss and same-interface reacquisition | Unresolved predecessor followed by strong current anchors | Fresh confirmation cannot authorize a false prefix or inherit its progress/lease |
| H1 | Established fill loses its row; unique independently identified compatible successor | Continuation-only successor or merely near-Y candidate | Committed transfer updates the allowed owner for subsequent frames without copying ID/history |
| H2 | Independently verified non-material and material representations of the same boundary | Old valid owner still competes; multiple successors; expired snapshot | Family label is not a privilege; ambiguity remains fail-closed |
| H3 | Positively contradicted predecessor with unique fresh interface | Predecessor merely absent or unavailable | Owner correction creates a fresh direction-neutral episode only with the required positive evidence |
| V1 | Initially FULL, newly visible stationary interface with strong partition witness | Stationary reflection, internal stripe, uniform opaque FULL, unverified anchor corridor | New observed-interface route selects the real current row and never labels stationarity as drainage |
| V2 | Observed interface later drains, rises rapidly or closes as FULL | Upward/no-progress data forced through drain release; missing current row | Existing directional gates govern motion state; loss yields no numeric value immediately |
| V3 | Established fill stabilizes then reverses | Initial EMPTY static lower structure; stale owner reopening OPEN | Initial EMPTY safety and constrained loss context remain intact |
| P1 | Numeric output through each new transition | Candidate missing, invalid, contradicted or from another frame | Selected candidate source Y equals sequence and CSV raw Y; Oil/Foam validity stays independent |
| D1 | Basic/detailed trace, one-shot/incremental execution and candidate permutation | Diagnostic recomputation, pre-sort offset treated as serialized index | Output equality; stable provenance; trace reports actual gates and chain-specific causes |

## Acceptance gates and operating points

The [rejected R23 experiment](../50-diagnostics/s11/s11-r23-native-polarity-rejection.md)
adds four raster-to-tracklet positive controls in
`test_real_curve_can_move_and_reverse_photometric_polarity_before_confirmation`.
A true curved interface may translate while contrast polarity and exposure
change; both movement directions and initial polarities must remain supported.
Three common sectors with opposite signs are not enough for an identity veto.
Keep positional uncertainty separate from a confirmed different-structure
label, and preserve assignment ambiguity when testing negative evidence.
The BASE f14362 sector 2 human review is a localization-mismatch label only;
it must not be used as a certified material/structure negative.

**A — Evidence:** choose and document normalized partition, similarity and
registration operating points using labeled public/synthetic rasters with
held-out negatives. Record which cases were used to select values and which
were held out. Include resolution, crop offset, tilt, texture and exposure
variation. A score change without improved identity discrimination does not
satisfy this gate.

**B — Association and handoff:** all relevant E/T/H controls pass end to end,
including the compound high-texture-peer plus successor-owner case. The
synthetic motion probe from the R22 investigation is a trigger pattern, not
sufficient physical truth by itself. Use explicitly constructed different
image structures and an equally fast genuine-motion positive control.

**C — Initial-FULL extension:** all V controls pass with extraction enabled,
especially the stationary interface versus internal-structure pair. Do not
activate the proposed phase if those images are not distinguishable using the
implemented witnesses. Unknown on insufficient evidence is preferable to a
fake drain or false FULL-prefix measurement. Failure here does not justify
loosening existing release predicates.

**D — Candidate acceptance:** preserve relevant protected R22/R21 truth,
including initial EMPTY absence, FULL prefix/suffix absence, rapid refill,
bounded lease/expiry, contradiction reset, delayed attempt semantics and
independent Foam. Use the current canonical test/replay owner for final scope.
Measure runtime and peak memory on identical public inputs because evidence
extraction and descriptor history add work. Descriptor count and history length
must have explicit fixed bounds; no unbounded frame retention or all-history
matching. Report regressions and throughput impact, not an unsupported speedup.

The unchanged R22 stationary *drain release* negatives remain required. Add
separate tests for the proposed visible-interface observation state; do not
rename old failing inputs as real interfaces to make them pass. Any protected
expectation needing change must first have independently reviewed physical
evidence and an explicit acceptance decision.

## Target-Windows checkpoints

Follow the [current Windows procedure](../40-operations/s11-current-windows-field-qualification.md)
and [canonical reviewed truth](windows-sample1-heating-coldstart-reviewed-truth.md).
Inspect one bounded question per operator request. The
[transferred checkpoint record](../50-diagnostics/s11/s11-r22-reviewed-interface-causal-findings.md)
identifies the existing guide-reviewed frames; recheck frame and source-Y
mapping for a new run rather than assuming candidate IDs survive a revision.

- BASE: show that the false predecessor is not published as Oil and cannot
  create the real boundary's motion history; then inspect visible-interface
  admission separately from drain admission.
- Accum: verify actual-boundary witness, independent peers, authority, committed
  owner and final selected boundary through the first missing transition.
- Then evaluate every canonical segment, including early entry and late drain
  not explained by the checkpoint investigation. Do not replace segment truth
  with the current detector's shape or numeric row count.

Require current-frame coordinates and user-reviewed physical identity for
changed rows. If an interval's visibility is disputed, obtain explicit human
review before amending its canonical truth; LVLM-only estimates do not suffice.
Local gate completion never changes FIELD FAIL to field-qualified.

## Design-only verification

For this documentation change, run the detector governance checker against the
pre-change head, local link checks and `git diff --check`. Detector test/replay
execution is not required to validate prose and is not claimed as implementation
acceptance. On implementation, use the staged gates above and proportionate
focused tests before the broader candidate suite.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F02`, `S11-F03`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F08`, `S11-F09`, `S11-F10`.
- First harmful stage: BASE association across a reviewed location mismatch and Accum boundary-owner exclusion are distinct targets; private physical-identity continuity remains unresolved. The local polarity-only association prototype failed protected truth and photometric positive controls. Contested fill-owner draft: on sample5 and sample7 the first harmful stage is `OIL-PHASE-FILL`, where a survivor of `FILL_OWNER_AMBIGUOUS` becomes the publishing owner by attrition; on SPL#4 this is inferred, not confirmed.
- Existing feature coverage: the new E3/E4 control reuses fixed current-frame candidate kinds, original raster/visibility and O1 native/center evidence without changing Recipe, masks, Artifact/static setup or experimental modes. The 187-unit population retains all accepted, opposed and unassessed records and the seven historical declared-kind mismatches. The fill-owner checks reuse the top-exit negative controls (same Recipes, ROI inputs and initial states as run 003), the comparison runner and the kept runs 001/002 as the identity anchor.
- Execution scope: linked native geometry availability and CRW-1 paired-raster input checks only; the latter has 123 focused tests and separate direct-loop arithmetic. No continuous contour qualification, completed sequence, private Windows replay or actual reader response is supplied by this change. Earlier RGB/initial-FULL/top-exit checks retain their scopes. Partial descriptive support does not establish a physical classifier or report acceptance. The 2026-10-22 top-exit promotion criteria are pre-registered before any new evidence; no run, review or Windows execution accompanies them. The 2026-10-22 contested fill-owner checks were frozen before any code or run; the only execution behind them is the closed desk run `s11-fill-owner-contest-desk-20261022-001` over kept FOA-1 readouts, plus the user's sample7 judgment.
- Logic-map impact: NONE — this adds a validation precondition for a proposed witness, not a production route or a new consumer. The fill-owner checks add a frozen validation section only.
- Failure-registry impact: NONE — existing identity/provenance/no-threshold-shortcut guards cover missing contour input; prior rejected comparisons and full physical-witness acceptance are unchanged. The fill-owner attrition path fits F04, F05 and F08; no new entry.
