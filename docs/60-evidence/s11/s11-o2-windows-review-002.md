# S11 O2 Windows review-002 — candidate identity and partial path agreement

Recorded: 2026-09-18. Source: user-transferred Windows review summary. Original
media, local labels and receipts were not opened on this machine. This is bounded
human-review evidence, not a classifier score or Windows field qualification.
[Work plan](../../00-project/work-plan.md) owns current status; the
[O2 procedure](../../40-operations/s11-o2-local-shadow-evaluation.md) and
[validation contract](../../30-validation/s11-interface-observability-witness-validation.md)
own the workflow and acceptance. This does not revise
[canonical reviewed truth](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md).

## Reported identity and persistence

| Item | Value |
|---|---|
| Bundle-generation ZIP commit | `d7c1ebe`, user-attested |
| Label-tool ZIP commit | `e3fac4b`, user-attested |
| Detector | `opencv-phase-detector-r22-3-interface-witness-diagnostics-v1` |
| Resolver | `r22-oil-ownership-evidence-replacement-v1` |
| Witness | `interface-observability-witness-trace-v1` |
| Result semantics | `2` |
| Target | BASE, source frame `14386` |
| Persisted revision | `4` (latest transferred update; revisions 2–4 added three candidates) |
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

## Remaining inventory and next transition

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
identity/partial-path contract. The current evaluator treats an `interface` label
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

## Detector Governance

- Logic-map nodes: `TRACE-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F09`.
- First harmful stage: none newly inferred; the current evaluator does not encode the transferred partial-path qualifications in its localized-support indicator; no actual model score or new detector cause is inferred.
- Logic-map impact: NONE — evidence and next-review routing do not alter detector, diagnostic-tool or UI execution.
- Failure-registry impact: NONE — a human-reviewed candidate does not establish a new causal detector failure or field repair.
