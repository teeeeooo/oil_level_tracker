# Current Work Plan

**Current milestone:** `S11 — Real-Field Detector Effectiveness Recovery`
**Milestone status:** `ACTIVE`
**Current gate:** O1 accepted locally; fixed-score/locality/profile Windows experiments closed without promotion; W1 source review and target counter-controls verified locally; W3 separated shadow-output/evaluation implemented and verified locally; existing-data Windows target/context audit reported complete; W4 hypothesis/control selection is next; aggregation challenger and calibrated O2 acceptance remain open
**Field disposition:** latest user-reported Windows result remains `FIELD FAIL`; no field-qualified detector is claimed

This document owns only the current engineering state and next transition. Revision-by-revision history belongs in diagnostics, evidence, historical architecture/validation records, and Git history.

## S11 work-item ledger

[Document relationships and routing](../README.md#s11-audit-specifications-and-execution-routing)
explain the September O1–O5 plan and October W0–W7 follow-up. This ledger owns
live work-item status. The dated audits and evidence remain historical inputs;
current architecture and validation own implementation and acceptance contracts.

Status terms distinguish **PROPOSED**, **CONTRACT DEFINED**, **IMPLEMENTED**,
**VERIFIED** (only for its stated scope) and **ACCEPTED** by the relevant gate.
**CLOSED WITHOUT PROMOTION** ends an experiment while rejecting its adoption;
it is not calibrated O2 acceptance. A blocked or conditional later item remains
visible with its dependency, rather than silently disappearing or becoming done.
These states do not change the execution policy's formal completion requirements.

| Work item / stage | Current status | Entry / completion boundary | Owner and evidence |
|---|---|---|---|
| O1 extraction (pre-W baseline) | IMPLEMENTED; locally ACCEPTED | Preserve trace-only production equality and exact provenance; no identity authority | [O1 contract](../20-architecture/s11-interface-observability-witness-architecture.md#o1-implemented-measurement-contract), [local evidence](../60-evidence/s11/s11-r22-3-interface-witness-diagnostics.md) |
| W0 / O2 fixed profile experiment | VERIFIED by transferred Windows report; CLOSED WITHOUT PROMOTION | Reproduction, receipt and input preservation reported; candidate identity worsens against combined; no rerun requested | [Specification](../50-diagnostics/s11/s11-o2-fixed-score-experiment.md#candidate-identity-profile-mode), [local checks](../60-evidence/s11/s11-o2-identity-profile-local.md), [Windows result](../60-evidence/s11/s11-o2-identity-profile-windows-run-001.md) |
| W1 / O2 targets and aggregation | VERIFIED locally for source review, target contract and counter-controls; no identity rule promoted | Partial-positive/glare expectations, identity rationale and unresolved accounting reproduced; a validated aggregation challenger remains OPEN under W4 | [W1 architecture](../20-architecture/s11-interface-observability-witness-architecture.md#w1-target-and-aggregation-contract--design-boundary), [W1 controls](../30-validation/s11-interface-observability-witness-validation.md#w1-aggregation-challenger-controls--not-yet-acceptance-evidence), [local evidence](../60-evidence/s11/s11-o2-w1-target-aggregation-controls.md) |
| W2 / O2 bounded scene expansion | CONDITIONAL; collection deferred, not completed | Current fixtures and existing labels suffice for target/evaluator work; no new scene can resolve identical supplied observables by labeling alone. Name a discriminating context/geometry gap and its positive/negative controls before collecting | [October W2 proposal](../50-diagnostics/s11/s11-detector-improvement-audit-and-work-spec-2026-10-01.md), [review operations](../40-operations/s11-o2-local-shadow-evaluation.md), [deferral rationale](../60-evidence/s11/s11-o2-w1-target-aggregation-controls.md#decision-and-remaining-gap) |
| W3 / O2 shadow outputs and evaluation | IMPLEMENTED and VERIFIED locally for v2 prediction import, separated targets and scripted controls; existing-data Windows audit VERIFIED by transferred report | Preserve v1 compatibility and calibrated guards; scalar eligibility remains unverified without its own truth; no classifier efficacy claimed | [W3 contract](../20-architecture/s11-interface-observability-witness-architecture.md#w3-separated-shadow-targets), [validation](../30-validation/s11-interface-observability-witness-validation.md#w3-separated-target-and-audit-controls), [local evidence](../60-evidence/s11/s11-o2-w3-target-evaluation-local.md), [Windows audit](../60-evidence/s11/s11-o2-w3-target-audit-windows-run-001.md) |
| W4 / O2 one challenger | PROPOSED; mechanism not selected; context availability checked, physical discrimination unproven | Use W1 controls and the W3 audit to select one mechanism; static/glare absence and global material magnitude are not identity certificates; fix one hypothesis/endpoint and use the W3 evaluation target; record benefit, regression or rejection | [October W4 proposal](../50-diagnostics/s11/s11-detector-improvement-audit-and-work-spec-2026-10-01.md), [V2 controls](../30-validation/s11-interface-observability-witness-validation.md#v2--raster-controls-before-shadow-classification); no W4 completion evidence |
| O2 acceptance (between W4 and W5) | OPEN; not satisfied | Valid development/calibration/holdout roles, fixed operating point and required Windows shadow acceptance; regression rank gains cannot substitute | [O2 acceptance](../30-validation/s11-interface-observability-witness-validation.md#o2-shadow-acceptance); independent data/operating-point requirements unresolved |
| W5 / O3 support and association | PROPOSED; entry pending O2 acceptance | Separate behavior plan plus typed support/physical association controls; exact same-frame provenance and ambiguity protection | [O3 architecture](../20-architecture/s11-interface-observability-witness-architecture.md#stage-o3--independent-support-and-association), [O3 entry](../30-validation/s11-interface-observability-witness-validation.md#o3-behavior-entry); no behavior acceptance |
| W6 / O4 handoff and phase | PROPOSED; entry pending W5 | Handoff and phase observation are separate changes with separate positive/negative controls; do not relax gates based on elapsed time or polarity alone | [O4 architecture](../20-architecture/s11-interface-observability-witness-architecture.md#stage-o4--handoff-and-phase-behavior), [parent validation](../30-validation/s11-physical-interface-evidence-repair-validation.md); no behavior acceptance |
| W7 / O5 field qualification | PENDING integrated behavior candidate | Exact runtime, all canonical segments and required accuracy/coverage/resource evidence; no earlier local/shadow PASS substitutes | [Field acceptance](../30-validation/s11-interface-observability-witness-validation.md#field-qualification), [Windows procedure](../40-operations/s11-current-windows-field-qualification.md); FIELD FAIL retained |

**Immediate action — local W4 hypothesis/control selection:** the [Windows W3
audit](../60-evidence/s11/s11-o2-w3-target-audit-windows-run-001.md) reports exact
reference reproduction, COMPLETE and 12 preserved inputs at `038a303`. Context
and recorded funnel facts are available. BASE 8/9 have admitted row flags but no
final selection; Accum 10 is absent from retained refs. Neither result isolates
the causal rejecting gate. Material magnitude changes direction across reviews,
and static/glare absence is shared by true and false candidates.

Review one geometry-preserving partial-support/opposition mechanism against W1's
partial-positive, isolated-glare/structure and identical-observable controls before
fixing a W4 formula/primary endpoint. No threshold, new descriptor, production
gate relaxation or challenger adoption follows from this audit alone. No further
Windows run, labels or video collection is requested now; W2 remains conditional.
The detailed private JSON stays available for a named follow-up question. W4
efficacy, independent scalar truth and calibrated O2 acceptance remain open.

At each W transition, update the affected row and immediate action here, linking
(1) the implemented/rejected decision, (2) exact checked code/input and scoped
verification evidence, and (3) remaining conditions/next action. Change the
architecture/validation when their contract changes, operations when executable
steps change, and evidence when results arrive. Preserve rejected results and
existing audit text. Explicitly record a skipped/conditional item and its reason;
never infer completion from a document, commit, tool exit code or local test alone.

## Accepted local candidate

R22 is the current locally accepted candidate. It replaces Oil phase/evidence
orchestration with explicit state and a bounded release engine, carries typed
identity contradictions through admission, adds one strictly bounded same-owner
initial-FULL evidence renewal, and caches confirmation witnesses. Replaced
execution paths have been removed; candidate generation and Foam are preserved.

Runtime identity: `opencv-phase-detector-r22-oil-ownership-evidence-replacement-v1`.
Main completed direct review, 1763 canonical tests, 252 Qt tests, all four video
replays and a three-pair serial performance comparison. All 13 protected truth
cases and four complete tracking fingerprints match R21. Total timing was
11.964 s versus 12.007 s on the measured macOS sample; no speedup is claimed.

- [R22 architecture](../20-architecture/s11-r22-oil-ownership-evidence-replacement-architecture.md)
- [R22 validation](../30-validation/s11-r22-oil-ownership-evidence-replacement-validation.md)
- [R22 completed local evidence](../60-evidence/s11/s11-r22-ownership-evidence-replacement.md)

R21 is the protected comparison predecessor. R18–R21 remain historical evidence,
not alternate current owners. Existing truth misses remain and field repair is
not established by these checks.

R22-2 is the protected diagnostic baseline over the accepted R22 behavior:
`opencv-phase-detector-r22-2-interface-path-diagnostics-v1`. The completed resolver
identity remains R22 intentionally. Its [architecture](../20-architecture/s11-r22-2-interface-path-diagnostics-architecture.md)
retains R22-1 candidate-centered measurements and adds the existing generators'
native path geometry, provenance and same-X band comparisons. This is not a new
behavior or field acceptance. R22-1 remains the diagnostic comparison predecessor;
its [local evidence](../60-evidence/s11/s11-r22-1-interface-diagnostics.md) is retained.
The [R22-2 local evidence](../60-evidence/s11/s11-r22-2-interface-path-diagnostics.md)
records 1,781 passing tests, unchanged tracking/event rows and preserved old
diagnostics in all four public comparisons.

## Current authorization boundary

On 2026-09-09 the user authorized replacement of the Oil temporal identity and
phase/evidence core, relevant tests and diagnostics, measured performance
comparison, and cleanup of replaced execution paths. Main owns design and final
acceptance. The user subsequently requested no further sub-agent work; Main
now completes implementation, cleanup, verification and review directly.
This supersedes the prior pause on another detector revision for this bounded
replacement. R21 local acceptance is historical baseline evidence, not evidence
that its transferred Windows failures are fixed.

The user subsequently authorized R22-1 measurement extraction and trace output
with unchanged R22 decisions, followed by sequential Windows evidence collection.
On 2026-09-16 the user authorized consolidation and diagnostic improvements as
R22-2, implementation, verification, commit and push. This extends diagnostic
collection with native path evidence.
On 2026-09-17 the user authorized the next behavioral implementation, verification,
commit and push. The first R23 native-polarity association prototype failed
protected public observations and was removed from production. This is an
acceptance failure, not a requirement for another permission request. R22-2
remained the diagnostic baseline at that decision; no R23 behavior was promoted.
The current diagnostic runtime is R22-3 as recorded below.

Outside this replacement's authority:

- unrelated candidate-generation, Foam or UI changes;
- unbounded evidence retention, unconditional recovery expiry removal or relaxed
  truth/safety criteria to manufacture a pass;
- regeneration or silent replacement of a checked tracking fingerprint/golden merely to fit the current environment;
- automatic replay of private Windows media or reinterpretation of local controls as field proof;
- case-specific video/Glass/timestamp/coordinate behavior, interpolation, carry or report-side repair; or
- speculative Accum-specific behavior changes without reviewed physical identity and two-sided controls.

The local Sample4 replay currently produces `e447626b...` rather than the historical checked `0f202947...`. A clean detached `d50c143` baseline produces the same current `e447626b...`, and its tracking rows are identical to R21 apart from run identity. The R20-era sample authority records the same Sample4 media SHA-256 (`ee971b...`) as the current file, so the evidence does not support media replacement as the cause. The historical golden was not changed; the unresolved provenance gap is the exact historical Python/OpenCV/video-decoder runtime, now guarded for future runs by the [R21 replay runtime provenance diagnostic](../50-diagnostics/s11/s11-r21-replay-runtime-provenance-diagnostic.md).

## Preserved contracts

- one generic detector serves every Glass; no private identity or reviewed coordinate enters production control flow;
- numeric Oil/Foam values remain selected same-frame candidates with exact provenance;
- Oil and Foam validity/ownership remain independent through their defined composition point;
- confirmed FULL/EMPTY state constrains lifecycle but never fabricates a coordinate;
- physical tracklet identities are not copied across a rapid-refill phase handoff;
- ambiguous, unavailable, lost, or hard-invalid evidence fails closed rather than being repaired downstream; and
- detector changes remain governed by the current logic-map/failure-registry history-review contract.

## Open field risks and named unknowns

R22 is not field-qualified. The controlled Base cycle proves generic local behavior for bounded slow drain and rapid refill, but it does not prove that the private Windows Base failure had the same cause or is repaired. Accum initial entry, continuity/layered/post-Foam ownership and drain re-entry remain field uncertainties. Historical R18 causal unknowns remain constraints where reviewed physical identity or exact Y anchors were unavailable.

## Active follow-up design

The user requested a combined repair design after sequential Windows checks
and direct guide-image review. The [corrected checkpoint investigation](../50-diagnostics/s11/s11-r22-reviewed-interface-causal-findings.md)
records BASE association across a reviewed localization mismatch and Accum
actual-boundary owner exclusion with a separate cross-representation texture
gate. Later human review identifies BASE f14362 sector 2 as near the interface
but offset; a different physical structure is not established. BASE f14386
sector 1 Y382 and sector 4 Y417 are separately reviewed near-interface points.
These bounded findings do not establish the cause of every missed interval.

The [physical-interface evidence proposal](../20-architecture/s11-physical-interface-evidence-repair-design.md)
and its [acceptance gates](../30-validation/s11-physical-interface-evidence-repair-validation.md)
define local interface witnesses, verified physical association, committed fill
handoff and a separately gated direction-neutral observation phase. These
behavioral changes remain proposals. R22-1 Windows measurements exposed sampling
center sensitivity, including opposite near-band signs on nearby Accum candidates
sharing diagnostic peaks. R22-2 captures native path geometry to examine that
uncertainty. Both are trace-only measurements, not the proposed classifier or
ownership changes. Real-video discrimination, operating points and stationary-interface versus reflection
acceptance remain unvalidated.

The [2026-09-17 detector direction assessment](../50-diagnostics/s11/s11-transparent-interface-detector-direction-assessment.md)
reviewed the repository history, public truth, private checkpoint findings and
external liquid-interface/sensing references. It rejects both a whole-detector
rewrite and continued scalar-threshold tuning. The chosen boundary is a bounded
observation-layer redesign that preserves the downstream R22 safety/provenance
contracts. The subordinate [Interface Observability Witness Architecture](../20-architecture/s11-interface-observability-witness-architecture.md)
and [validation contract](../30-validation/s11-interface-observability-witness-validation.md)
own the next trace-only implementation stage. Its public baseline probe found a
candidate within 8 px on all 13 usable truth frames across the original and six
photometric variants, but retained a median 23–24 Oil candidates and 3–4
near-truth candidates per frame. This supports a discrimination/observability
problem on the public set, not a field-success claim or an operating threshold.

Retained but non-current work is owned by [`retained-commitments.md`](retained-commitments.md).

## Next transition

Windows native-path collection for the previous bounded question is complete.
The [rejected R23 experiment](../50-diagnostics/s11/s11-r23-native-polarity-rejection.md)
records why common-sector contrast inversion alone cannot veto association. Do
not ask for another private rerun of that removed prototype.

Stage O1 is implemented as diagnostic runtime
`opencv-phase-detector-r22-3-interface-witness-diagnostics-v1`, preserving the R22
resolver. The [measurement contract](../20-architecture/s11-interface-observability-witness-architecture.md)
defines fixed scales, descriptive peak/plateau hulls, geometry-vs-localization
separation, exact raw candidate joins and shared-raster lineage. The
[supplemental review](../50-diagnostics/s11/s11-observation-redesign-execution-review.md)
is retained as supporting rationale after integration into current owners.

[O1 local evidence](../60-evidence/s11/s11-r22-3-interface-witness-diagnostics.md)
records passing extraction, canonical suites and 12 public-window mode comparisons.
Debug trace size increases about fourfold; use bounded captures. The
[O2 local preparation/evaluation tool](../40-operations/s11-o2-local-shadow-evaluation.md)
now prepares exact-frame packets, combines local labels, freezes recording-group
partitions and evaluates imported predictions without changing the detector.
Its [local evidence](../60-evidence/s11/s11-o2-evaluation-foundation.md) covers
provenance/partition guards and metric arithmetic, not classifier accuracy.
The offline tool also registers relocatable bundle/source receipts and records
human replies with revision checks, snapshots and resume status. Keep these files
outside the replaceable ZIP checkout. Existing R22-3 bundles and v1 labels remain
usable; no detector rerun or R22-4 revision is required. The
[durable-record evidence](../60-evidence/s11/s11-o2-durable-review-records.md)
records local persistence controls, not Windows qualification or a new classifier.
The user-transferred [Windows review-001](../60-evidence/s11/s11-o2-windows-review-001.md)
now records successful v2 migration at revision 3: BASE f11508 has no visible
interface and 23 non-interface candidates. The bounded record remains closed by
user report. The [Windows review-002](../60-evidence/s11/s11-o2-windows-review-002.md)
follow-up records migration plus revisions 7–14: BASE f14386 has six interface,
two non-interface and 15 intentionally unreviewed candidate identities. All five
native paths have explicit reviews (10 near / 7 off); candidate-center geometry
remains unreviewed and contour is empty. Whole-candidate identity does not certify
all path points. The revision-10 frozen/readiness files remain unchanged snapshots,
not evaluations of revision 14; no predictions were supplied (NOT_EVALUATED).
These are transferred Windows reports, not locally inspected private artifacts.
Bundle/initial label-tool ZIP commits d7c1ebe/e3fac4b are user-attested; the later
migration/continuation execution commit was not reported.

The [v2 review-semantics implementation](../60-evidence/s11/s11-o2-scoped-review-semantics.md)
separates identity, path agreement, contour truth and overlapping artifact tags.
Windows migration and bounded record/freeze/readiness use are now reported; do not
ask the user to repeat them. Source labels/history and bundle links stay on Windows
outside the replaceable code checkout. New transferred results and corrections
belong in the existing per-review evidence records when received; update this
current owner when the gate or next transition changes, without duplicating the
full revision history here.

The transferred [Windows review-003](../60-evidence/s11/s11-o2-windows-review-003.md)
now records Accum f16280 revision 3: calibrated_high_recall Y213 (input ID 19)
is interface through prior direct-review reuse, and material_path Y217 (input ID
10) is interface through a new direct human judgment. All five candidate 10
native-path positions were then directly reviewed near_interface. There are 25
unreviewed identities, no candidate-center reviews and no contour; visibility is
visible. It shares recording-A with review-002 and remains regression. These
bounded identity/path tasks are complete by report; numeric localization and
classifier effectiveness remain unmeasured. Its revision-3 freeze and no-prediction
readiness now succeeded by Windows report: NOT_EVALUATED, unchanged source labels,
and existing review-002 artifacts preserved. The later direct field report resolves
the contour wording: labels.cases[].contour exists and is [] in every review;
review-003 lacks contour_review attribution, not the human contour array.
The [transferred comparison report](../60-evidence/s11/s11-o2-windows-review-comparison.md)
records reported Windows outputs covering 73 proposals and 55 native points.
Subsequent inspection of ten code photographs withdrew two OCR-based findings:
the actual reviewer nesting and aggregation indentation are correct. The prior
claim that those errors prevent the photographed code from running is withdrawn.
Windows now reports a separate v2 comparator using existing validators and exact
geometry keys, separate judgment/missing states, production median computation,
26 passing synthetic tests, new outputs and matching input pre/post file hashes.
Null counts reconcile to 9/165 and review-002 interface geometry to 14 points;
old code/results remain preserved. These are transferred checks, not local source
or private-data verification. No human labels are invalidated by old report errors.
The corrected follow-up now confirms revisions 3/14/3, zero reported failed or
duplicate native joins, new-run pre/post file preservation and explicit native-only
measurement scope. Candidate-center identities are counted, but their features
are not compared. These preparation checks are complete by Windows report; do not
repeat them without changed inputs. The production percentile API was inspected
locally: 0.5 denotes median; private script/data execution remains on Windows.
BASE near/off signed_delta ranges overlap at every width; Accum's unreviewed
points cannot supply negative labels. All 110 larger-width native measurements
report truncated peak lists, not absent band measurements or certified false paths.
The next transferred comparison separates BASE interface proposals' 10 near
versus four off points and keeps three non-interface structural points separate.
Its detailed rows and summaries disagree on medians, sign counts, and one
normalization calculation; these are report inconsistencies, not established
private-data or detector defects. The two targeted Windows checks now report
packet-to-JSON agreement for candidate 9 / sector 2 / width 16 and identify
the C-group width-8 median discrepancy as a Markdown maximum-to-median copy
error. Correct normalized_delta=-0.43024128331146505 and near_below
gray_std=0.025348553697232056 also differ from the earlier transferred row;
the stage of that transfer discrepancy remains unspecified. The denominator
exists only in the packet, and arithmetic agreement does not identify the
historical runtime formula. Windows has now regenerated the report from JSON,
reports zero detail-to-summary differences and matching input pre/post hashes.
The corrected numbers support a bounded observation: above-band normal alignment
separates BASE's ten interface/near from four interface/off points at widths
16/24, but all three structural controls lie inside the near range. This is a
conditional localization hypothesis from one frame, not an identity classifier
or accepted threshold. Numeric report repair is no longer the next blocker.
Review-003 now reports revision 4 / SHA prefix 5cbebd88: candidate 15 is
non_interface with five off native points, and candidates 10/19 remain interface.
The new negative is 76–118 px below candidate 10 at common X intervals. This
supplies an identity-negative/off comparator, not the still-missing interface/off
localization control. The r4 comparison is now reported complete with unchanged
inputs: signed/normalized delta ranges are disjoint for candidates 10 and 15 at
all three Accum widths, while above/below alignment each overlaps at two widths.
Candidate 15 does have slightly negative delta at width 18; do not infer a
zero-sign rule or count signed/normalized delta as independent votes. Combined
with BASE, no universal sign or alignment gate is justified. Stop repeated
per-candidate descriptive reports on these frames; keep r3 snapshots historical.
The [Windows video inventory](../60-evidence/s11/s11-o2-video-inventory.md) now
confirms separately recorded SPL#2/3 exist, but the user defers both until after
SPL#1 improvement; they are not current O2 inputs or assigned holdout. SPL#1's
post-780 s region contains more rising/falling-interface scenes, not confirmed
novel phenomena. The user clarified that unexamined scenes inside 480–780 s may
be equally useful. Do not prioritize post-780 s exploration or partition-tool
changes as prerequisites. Reviews 001/002/003 remain regression; current partition
guards are unchanged. Independent-recording qualification remains a later gate.

**First executable experiment is now implemented locally:**
[`s11_shadow_experiment.py`](../../tests/diagnostics/s11_shadow_experiment.py)
reads current v2 labels/packets and compares fixed contrast-only, alignment-only
and combined contrast/alignment/local-context scores. The
[experiment contract](../50-diagnostics/s11/s11-o2-fixed-score-experiment.md)
fixes its formulas and limits; the [Windows procedure](../40-operations/s11-o2-local-shadow-evaluation.md#고정-점수-shadow-실험--기존-라벨로-실행)
was used for the first reported Windows run. No partition change or new labels
were required. Existing validators, hashes and percentile owner are reused.

Scores are label-blind; automatic evaluation keeps candidate identity ordering,
interface-only near/off ordering, and identity-negative controls separate.
Native and candidate-center geometry remain distinct, including exact-center
measurement reuse without copying human labels. Matched-scale/point support is
used for fair ablations; missing support, all-negative frames, unknown winners,
ties and reversed pairs remain visible. Inputs are immutable, outputs are new,
and a final hash receipt marks successful publication.

This is an **EXPLORATORY_UNCALIBRATED ranking experiment**, not a trained or
calibrated identity/location classifier. It emits no production decisions,
chooses no operating threshold, computes no numeric localization without contour,
and cannot be imported as calibrated shadow predictions. V3 and all partition
rules remain unchanged. The [first Windows result](../60-evidence/s11/s11-o2-fixed-score-windows-run-001.md)
reports successful execution on revisions 3/14/4 with unchanged inputs. Its artifact
fingerprint matches local commit `29ec2f9`; private output files were not inspected
here. Combined scores have mixed results: BASE identity correct=5/12 versus
contrast=6/12, and same-X location correct=5/7 versus alignment=7/7; Accum's
reviewed identity pairs are correct=2/2. This does not support promotion.

The [reversal follow-up](../60-evidence/s11/s11-o2-fixed-score-reversal-followup.md)
reports BW16 locality-induced reversal for BASE idx8/idx10, retained by separate
score medians despite two other scales ordering correctly. Idx0/idx11 still fails
all methods with different geometry and partial support. This is not proof that
the true interface has weaker physical information. The ten unscorable location
pairs trace to one off point lacking far-above evidence, so locality also limits
matched-support coverage. The subsequent Windows confirmation resolves the
output checks: idx8 Y405 has raw C/A scores .4896/.6598 on all three scales but
null combined and all matched scores; idx11 Y922 causes exactly two unscorable
identity-negative controls. There is no remaining original-data request for this
run. Null score and zero available-scale count remain distinct.

Controlled locality ablation is now implemented in the same experiment owner
with `--locality-ablation --reference <v1 experiment.json>`. The
[Windows ablation procedure](../40-operations/s11-o2-local-shadow-evaluation.md#locality-제거-대조-실험--첫-실행-결과-보존)
was executed in the reported Windows run. It compares `(C*A)^(1/3)` against
`(C*A*L)^(1/3)`, holding exponent,
scale/point medians and geometry policy fixed. The required old reference must
match current input identities/hashes and recomputed v1 scores/evaluation exactly
before new outputs are published; old files are preserved.

`common_support` compares four methods on exactly the old support.
`ca_supported` separately compares C/A/without_locality on expanded C/A-available
support. Newly scorable pair outcomes are not common-support improvements;
retained pair ordering can also change when added scales/points change medians,
and is reported explicitly. Automatic summaries name improvements, regressions
and persistent failures; no manually transcribed metric table is needed.
Root/receipt schema `s11-o2-locality-ablation-v1` and a separate ablation spec
fingerprint distinguish the new run. No fitting, thresholds or production
classification are added. BASE identity failures are not assumed solved.

The [first ablation result](../60-evidence/s11/s11-o2-locality-ablation-windows-run-001.md)
reports exact v1 reproduction and seven unchanged inputs. On BASE common support,
WL fixes two same-X location orders with no regression there, but candidate
identity and same-X negative controls each regress twice with no improvement.
C/A-supported coverage adds ten all-X location comparisons, only three correct;
the newly scorable same-X pair is reversed. Accum's reviewed identity/control
orders are unchanged. Do not promote locality removal or infer an additive
weighting fix from this result. Do not sum nested task gains/losses.

The locality Windows investigation is complete at this scope. The subsequent
W0 experiment was implemented as `--identity-profile` in the existing score tool:
compare four-band two-region shape against ramp/local-excursion templates,
evaluating candidate identity separately from path localization. The
[fixed-score diagnostic](../50-diagnostics/s11/s11-o2-fixed-score-experiment.md)
owns the hypothesis and known structural-step ambiguity. This is a fixed offline
profile comparison, not a physical-interface classifier or production change.
The [operations identity-profile procedure](../40-operations/s11-o2-local-shadow-evaluation.md)
uses the same active revisions 3/14/4 and original v1 reference, with a new output
folder. [Local identity-profile evidence](../60-evidence/s11/s11-o2-identity-profile-local.md)
records 164 focused passing tests, including 22 new controls. The
[first Windows identity-profile result](../60-evidence/s11/s11-o2-identity-profile-windows-run-001.md)
now reports exact v1 reproduction, COMPLETE and seven preserved inputs at
`2bce8ea`. BASE identity is 2 correct / 10 reversed versus combined 5/7; Accum is
1/1 versus combined 2/0. Profile adds no correct transitions versus combined and
regresses three BASE pairs plus one Accum pair. Expanded profile support adds
no scorable identity pairs or changed outcomes. W0 closes without promotion;
no additional Windows report is needed to accept that bounded outcome.

The user-supplied [October audit](../50-diagnostics/s11/s11-detector-improvement-audit-and-work-spec-2026-10-01.md)
remains unchanged. W1's target distinctions and two-sided controls are specified
in the existing witness architecture/validation owners and
[verified locally](../60-evidence/s11/s11-o2-w1-target-aggregation-controls.md),
without scorer or schema changes. Candidate identity, local path support and scalar
eligibility must be evaluated separately. Partial interface truth cannot be
rewritten to fit median pooling, and max pooling cannot certify isolated glare.
A higher negative profile score does not establish a smaller step residual or a
physical shape collision; the first causal loss remains unresolved.

The [work-item ledger](#s11-work-item-ledger) owns the immediate action and
remaining W-stage dependencies. The audit's reported oracle/test runs remain
attributed to that audit, not repeated evidence.

Prior ablation validation recorded 129 focused tests passed (14 ablation controls
plus the prior 115), and comparison against actual 29ec2f9 scorer output on a
synthetic packet. Native Windows ablation execution is user-reported complete; private outputs
were not independently read here. The partial reported artifact hash matches the
local fingerprint's supplied portions. Field efficacy remains unaccepted.
Unknown top-ranked candidates remain unknown. Do not sum nested task improvements
as independent successes; partial candidate counts refer to points, not merely
scales. Additional scene requests must follow a named gap, without preference
for post-780 s.

The first three-method Windows experiment is user-reported complete; calibrated
classification and private-field effectiveness remain unaccepted. Detector,
selector, production witness code and labels are unchanged by the ablation tool.
The canonical source companion's fingerprint remains pending despite a reported
O2 bundle-link source hash. Reconcile that metadata using verified full local
identity and operator provenance; this gap alone does not invalidate linked O2
labels or require another detector run.
The existing evaluator can score imported candidate decisions but has no separate
predicted near/off contract: candidate identity and path localization need
distinct outputs/evaluation in the eventual shadow implementation. Earlier
reported validation remains accepted within its scope.
No new descriptor, detector rerun or universal sign/threshold rule is authorized
by these observations. Classifier/operating-point acceptance remains open; new-run
hashes do not prove old-run immutability retroactively.
Keep these already reviewed checkpoints in regression, not untouched holdout.
Link human labels to witness measurements locally on Windows for a named
discrimination hypothesis before choosing a shadow model. Changing partition
contracts is deferred unless the concrete experiment requires it. A real-image
classifier and operating point remain unbuilt.
No private export, further descriptor expansion without a named hypothesis, or
immediate behavioral detector rerun is required.

Independent support/association, committed fill handoff and initial-FULL
direction-neutral observation remain later separate behavioral gates. In
parallel, evaluate fixed/controlled acquisition and structured-background options
where fixture access permits. Failure of current descriptors alone does not
prove physical unobservability; human-visible misses remain evaluation failures.
Preserve FIELD FAIL until target-Windows accuracy/throughput qualification is
actually satisfied; diagnostic equality and local controls do not establish
Windows effectiveness.

## Current authority links

- [Project roadmap](roadmap.md)
- [Repository execution policy](execution-policy.md)
- [S11 detector-change Skill](../../.agents/skills/s11-detector-change/SKILL.md) and [mechanical governance contract](../30-validation/s11-detector-change-governance.md)
- [Current detector logic map](../20-architecture/s11-current-detector-logic-map.md)
- [R22 architecture](../20-architecture/s11-r22-oil-ownership-evidence-replacement-architecture.md)
- [R22 validation](../30-validation/s11-r22-oil-ownership-evidence-replacement-validation.md)
- [R22 local evidence](../60-evidence/s11/s11-r22-ownership-evidence-replacement.md)
- [Detector mechanism failure registry](../50-diagnostics/s11/s11-detector-mechanism-failure-registry.md)
- [Detector direction assessment](../50-diagnostics/s11/s11-transparent-interface-detector-direction-assessment.md)
- [Interface observability witness architecture](../20-architecture/s11-interface-observability-witness-architecture.md)
- [Interface observability witness validation](../30-validation/s11-interface-observability-witness-validation.md)
- [Canonical Windows reviewed truth](../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md)
- [Current-candidate Windows field procedure](../40-operations/s11-current-windows-field-qualification.md)
