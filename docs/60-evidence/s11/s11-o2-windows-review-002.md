# S11 O2 Windows review-002 — candidate identity and partial path agreement

Recorded: 2026-09-18. Source: user-transferred Windows review summary. Original
media, local labels and receipts were not opened on this machine. This is bounded
human-review evidence, not a classifier score or Windows field qualification.
[Work plan](../../00-project/work-plan.md) owns current status; the
[O2 procedure](../../40-operations/s11-o2-local-shadow-evaluation.md) and
[validation contract](../../30-validation/s11-interface-observability-witness-validation.md)
own the workflow and acceptance. This does not revise
[canonical reviewed truth](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md).

## Original revision-4 checkpoint — reported identity and persistence

| Item | Value |
|---|---|
| Bundle-generation ZIP commit | `d7c1ebe`, user-attested |
| Label-tool ZIP commit | `e3fac4b`, user-attested |
| Detector | `opencv-phase-detector-r22-3-interface-witness-diagnostics-v1` |
| Resolver | `r22-oil-ownership-evidence-replacement-v1` |
| Witness | `interface-observability-witness-trace-v1` |
| Result semantics | `2` |
| Target | BASE, source frame `14386` |
| Persisted revision | `4` at the original checkpoint; subsequent revisions are recorded below |
| Visibility / contour | `visible` / empty |
| Candidate inventory | 23: four interface, 19 unreviewed |
| Owners / classifier | no missing owners / `NOT_EVALUATED` |

prepare/link-bundle/status/record succeeded by report. The final status read
retained candidate input index 9's interface judgment. Source-video association
remains the registered human attestation, not a retroactive proof from a digest.
Executed source bytes were not independently compared with either ZIP commit.

## Reviewed candidate and paths

`candidate_input_index=9`, `source=material_path`, `canonical_y=411.5`.
The agent displayed four native-sector paths with Y ticks. The user judged all
four near the actual interface, and candidate 9 was recorded as `interface`.

| Sector | Source X extent (half-open) | Native source Y | Review basis |
|---|---|---|---|
| 1 | [130, 236) | 382 | Previous R22-2 user judgment reused after reported coordinate correspondence check |
| 2 | [236, 343) | 406 | New user confirmation |
| 3 | [343, 449) | 419 | New user confirmation |
| 4 | [449, 555) | 417 | Previous R22-2 user judgment reused after reported coordinate correspondence check |

These are reviewed candidate path positions, not independently measured exact
truth coordinates or tolerance intervals. The summary describes visual agreement
with the curved interface; no additional physical meniscus model is inferred.
Sector positions must not be replaced with scalar Y411.5 at all X locations.
Since contour is empty, quantitative localization error remains unmeasured.
The per-sector judgments appear in the transferred report; whether their full
provenance is retained in the candidate's local review_note has not been reported.

## Additional human judgments — revisions 2–4

| Revision | Input ID | Source / canonical Y | Reported native sector Ys | User label |
|---|---|---|---|---|
| 2 | 8 | material_path / 397 | s1=397, s2=396, s3=397, s4=405 | interface |
| 3 | 12 | material_path / 381 | s1=381, s2=381, s3=357 | interface |
| 4 | 10 | material_path / 363 | s1=378, s2=363, s3=354 | interface |

The user judged each proposal holistically as an interface while explicitly
acknowledging that parts of candidates 12 and 10 depart into air/glass regions.
The agent reports preserving these qualifications in review_note. Keep the labels
and their scope; neither relabel them automatically as structure/reflection nor
treat every native path point as a certified positive. Contour remains empty.
All four reviewed positives are material_path; this is a selected review subset,
not evidence that that source family is intrinsically correct. Proposals without
paths were deferred for this batch, not removed or labeled negative.

### Report arithmetic and comparable-X limits

The reported candidate Ys can be subtracted from the reference candidate 9's
listed sector Ys for an arithmetic check. Such subtraction measures proposal
separation, not error against an independently measured contour. The update does
not give the added candidates' source_x_range; validate identical X extents before
using these as same-sector geometric comparisons.

| Candidate | Listed-sector delta to candidate 9, source Y positive down |
|---|---|
| 8 | s1 +15, s2 -10, s3 -22, s4 -12 px |
| 12 | s1 -1, s2 -25, s3 -62 px |
| 10 | s1 -4, s2 -43, s3 -65 px |

Thus the blanket description of candidate 8 as 10–22 px above the reference is
incorrect for s1. Comparing candidate 12's s2 with reference s1 cannot establish
same-X agreement: s2's listed reference is 406, not 382. These are report-scope
corrections, not reinterpretations of the user's image judgments. The reported
24 px within-path Y spans for candidates 12 and 10 are arithmetic summaries,
not shape correctness or physical localization tolerances.

## Remaining inventory and next transition at revision 4

Reviewed interface IDs: `8, 9, 10, 12`. Unreviewed IDs:
`0–7, 11, 13–22` (19). No unresolved judgments or errors were reported.
Source counts remain 8 oil_hypothesis, 5 material_path, 6 calibrated_high_recall,
3 phase_transition_scan and 1 distributed_sobel_path. Owners remain populated;
classifier status remains NOT_EVALUATED. Freeze/evaluate completion is not reported.

The original sector judgments for candidate 9 remain valid within their reviewed
scope. Alongside [review-001](s11-o2-windows-review-001.md), this provides a
no-visible-interface case and four human-reviewed interface proposals. It does
not establish a balanced classifier dataset or field effectiveness; these remain
regression examples, not holdout.

Before using these labels for localization acceptance, reconcile the candidate
identity/partial-path contract. At that checkpoint the v1 evaluator treated an `interface` label
with an INTERFACE_SUPPORTED prediction as localized frame support without requiring
a contour. It computes quantitative per-sector errors only where reviewed contour
intervals match exact X extents. It cannot consume partial-path qualifications from
free-text notes. No predictions have been evaluated here, so no actual inflated
score is claimed; using these holistic labels as all-points-positive training truth
or demonstrated localization success would be unsupported.

Preserve this review as-is, apart from correcting arithmetic/attribution in notes
through the normal history-preserving workflow. Do not require the user to relabel
or re-answer clear judgments merely to fit the current schema. The next design
obligation is to distinguish candidate identity from sector-level path agreement
and localization uncertainty before further large-scale annotation or acceptance.
Record the reported X extents and qualifications; do not synthesize contour truth
from the candidate/reference Ys. No detector, labeling-schema or GUI change is
implemented by this evidence update.

## Follow-up recorded 2026-09-28 — migration and revisions 7–14

These results were transferred by the user after the original report. The repository
record was not updated at each transfer; this dated addition closes that recording
gap without inventing Windows execution dates. Private labels, media, reply files,
and receipts have not been opened or independently rehashed on this machine.
The [v2 implementation evidence](s11-o2-scoped-review-semantics.md) supersedes the
historical evaluator limitation above. Its local tests do not verify these private
records. The actual migration/continuation code commit was not reported; do not
reuse the initial label-tool ZIP commit as its verified execution identity.

### Migration checkpoint

Windows reported v1-to-v2 migration at **revision 6**, after revisions 5 and 6
corrected candidate 12/10 notes. Migration preserved those corrections, four
interface IDs `8, 9, 10, 12`, 19 unreviewed candidates, visibility `visible`, empty
contour, all 23 legacy annotations and six review-history entries. Initial v2
`path_reviews` were empty. Source file SHA prefix `4f01b02b...`, source logical
SHA prefix `eec322dc...`; migration reviewer `reviewer-001`, note
“판정 변경 없이 v2 형식으로 변환”. Original labels and six history snapshots remained
unchanged. V2 history initially contained one migration source snapshot.
Bundle-link and packet binding were reported unchanged.

### Explicit native-path reviews

Each row below is a separately stored geometry judgment, not an inference from
candidate identity. Source X intervals are half-open; Y is source-frame Y.

| Revision | Candidate ID | Sector | Source X | Source Y | Judgment |
|---|---|---|---|---|---|
| 7 | 9 | 1 | [130, 236) | 382 | near_interface |
| 7 | 9 | 2 | [236, 343) | 406 | near_interface |
| 7 | 9 | 3 | [343, 449) | 419 | near_interface |
| 7 | 9 | 4 | [449, 555) | 417 | near_interface |
| 8 | 8 | 1 | [130, 236) | 397 | near_interface |
| 8 | 8 | 2 | [236, 343) | 396 | near_interface |
| 8 | 8 | 3 | [343, 449) | 397 | near_interface |
| 8 | 8 | 4 | [449, 555) | 405 | off_interface |
| 9 | 12 | 1 | [130, 236) | 381 | near_interface |
| 9 | 12 | 2 | [236, 343) | 381 | near_interface |
| 9 | 12 | 3 | [343, 449) | 357 | off_interface |
| 10 | 10 | 1 | [130, 236) | 378 | off_interface |
| 10 | 10 | 2 | [236, 343) | 363 | near_interface |
| 10 | 10 | 3 | [343, 449) | 354 | off_interface |
| 11 | 11 | 1 | [130, 236) | 901 | off_interface |
| 11 | 11 | 2 | [236, 343) | 925 | off_interface |
| 11 | 11 | 3 | [343, 449) | 922 | off_interface |

Reviewer: `reviewer-001`. Candidate 9 uses
`prior_direct_review_exact_geometry_checked`: sectors 1/4 reuse R22-2 judgments,
sectors 2/3 reuse the earlier direct review. Revisions 8–10 use
`direct_human_review`; candidate 11 was newly reviewed directly as well.
Candidate 11 witness SHA:
`7c85ecfea15ab916eab7eea7a3c8858d2a8bfac875a08d48a4006ef62facb26`.

Candidate identities 8/9/10/12 remain **interface** despite off-interface path
portions. Candidate 11 became **non_interface**, tag **structure**, with the
user's lower-glass structure note retained. The approximate Y400/500-pixel
separation description is not measured contour truth. Candidate 10's explicit
latest s1=off / s2=near / s3=off judgments take precedence over older descriptive
reference-Y comparisons; no answer is reinterpreted to fit a presumed contour.
The duplicate transferred revision-8 report represents one revision, not two.

### Revision-10 frozen readiness snapshot

Windows reported successful freeze and no-prediction evaluate, with unchanged
source revision 10 / label SHA prefix `ab7cb1fd...` before and after:

- `frozen-review-002-r10.json`: `s11-o2-frozen-labels-v2`, content SHA
  `ce9c43739863cff4164cf909cd89ab506d138106bab3d827a40e33efe2e642dd`;
  packet SHA prefix `efc1f63c...`.
- `readiness-review-002-r10.json`: `s11-o2-shadow-report-v2`, source labels v2,
  **NOT_EVALUATED**, `auto_acceptance=false`, `prediction_sha256=null`.
  Frozen-label digest matched by report; field disposition remained **FIELD FAIL**.
- Four interface candidates: native near **10**, off **4**, uncertain/unreviewed
  **0**. Their qualitative review coverage was 1.0; no numeric tolerance follows.
- Localization: eligible 14, matched 0, unmatched 14; `not_measured`, mean/p95
  distance null, `full_path_localization_pass=null` because contour is empty.
- Identity-unreviewed 19 at this snapshot; native-unreviewed 3 (candidate 11).
  Candidate-center unreviewed **107 is the all-proposals total across all 23
  candidates**, not a count belonging only to the 19 identity-unreviewed ones.
- Supported-proposal count 0 means no predictions were supplied, not model rejection.

Status `labels_sha256` and frozen `content_sha256` use different hash payloads,
not different hash algorithms. Freeze excludes the top-level packet locators;
this does not claim that every nested path field is excluded. These two digests
need not match. Both r10 artifacts remain unchanged through the later reports and
must not be described as evaluating revision 14.

### Revisions 12–14 — additional identity-only review

| Revision | ID | Source | Canonical Y | Identity | Artifact tags |
|---|---|---|---|---|---|
| 12 | 0 | oil_hypothesis | 382 | interface | none reported |
| 13 | 16 | calibrated_high_recall | 381 | interface | none reported |
| 14 | 20 | phase_transition_scan | 406 | non_interface | reflection, residue |

All three have candidate-center geometry only. No path review was generated from
these identity judgments. Candidate 20's two tags describe the user's combined
interpretation; they are not two independent negative samples. Different labels
on nearby scalar Ys do not establish a source-family causal rule or numeric
localization error against a curved interface.

### Reported revision/hash progression and preservation

| Revision | Labels logical SHA (prefix when only prefix supplied) | Change |
|---|---|---|
| 6 after migration | `ee85a428...` | v2, no revision increment |
| 7 | `7ec2b712...` | candidate 9 native path |
| 8 | `08368892...` | candidate 8 native path |
| 9 | `7f0f6b69...` | candidate 12 native path |
| 10 | `ab7cb1fd...` | candidate 10 native path |
| 11 | `9233cb9d06123776601f1f51a37bf634a4d3f69be568fdcd42ecdfa50afac46b` | candidate 11 identity/path |
| 12 | `b4114c8f73768676ed4d0aaded8ec08183ada37d4207e464ff3a5490b6c47378` | candidate 0 identity |
| 13 | `7dee59cbb7d0bb2802988903f37e3feb7b4707e12cb63dd827efa428acde9314` | candidate 16 identity |
| 14 | `102919b6e6b8ad1ac8d558e9db426ee5e55c5f555a3e080c3067e7b89e23beeb` | candidate 20 identity/tags |

Latest transferred inventory: **interface 6** (`0, 8, 9, 10, 12, 16`),
**non_interface 2** (`11, 20`), **uncertain 0**, **unreviewed 15**
(`1–7, 13–15, 17–19, 21–22`). All five material-path proposals have native-path
reviews: **17 points = near 10 + off 7**, no uncertain/unreviewed native points.
Candidate-center reviews remain unreviewed; native coverage is not transferred.
Visibility remains visible, contour empty, owners populated (`label_owner` and
`split_owner`: `reviewer-001`, existing split rationale preserved). Original v1
labels/history, existing identity notes, packet binding, and r10 artifacts were
reported preserved. No detector rerun or code change was reported for these steps.
These are regression annotations, not untouched holdout or classifier accuracy.

### Open work after this transferred checkpoint

The remaining 15 identities are intentionally unreviewed; the frame is not fully
labeled. No new r14 freeze or model prediction has been reported. The proposed
next bounded case is Accum f16280, calibrated_high_recall Y213 in the existing
R22-3 bundle, with exact current candidate binding and scoped prior-review reuse.
At that checkpoint review-003 completion had not been reported. The subsequent
[review-003 record](s11-o2-windows-review-003.md) now captures its bounded
Accum identity-review completion. The durable
Windows labels remain the original annotation owner; this document retains the
shareable summary and corrections needed to resume engineering without relying
on chat history. Current sequencing remains owned by the work plan.

## Detector Governance

- Logic-map nodes: `TRACE-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F09`.
- First harmful stage: no new production failure inferred. The original v1 identity/localization conflation is historical; subsequent reports exercise v2 scoped records and no-model readiness. Missing repository follow-up records are reconciled here, not treated as classifier evidence.
- Logic-map impact: NONE — evidence and next-review routing do not alter detector, diagnostic-tool or UI execution.
- Failure-registry impact: NONE — a human-reviewed candidate does not establish a new causal detector failure or field repair.
