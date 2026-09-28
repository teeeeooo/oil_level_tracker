# S11 O2 Windows review-003 — Accum candidate identity reviews

Recorded: 2026-09-28. Source: user-transferred Windows completion report.
Private media, packet, labels and bundle receipt were not opened or rehashed on
this machine. This is bounded annotation-workflow evidence, not classifier or
field qualification. The [work plan](../../00-project/work-plan.md) owns current
sequencing; the [O2 procedure](../../40-operations/s11-o2-local-shadow-evaluation.md)
and [validation contract](../../30-validation/s11-interface-observability-witness-validation.md)
own workflow and acceptance. This does not amend
[canonical reviewed truth](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md).
Private filenames, absolute paths and business identifiers are omitted here.

## Reported execution and candidate binding

| Item | Transferred value |
|---|---|
| Review | review-003, newly created |
| Bundle | Existing R22-3 bundle reused; no detector rerun |
| Target | Accum, source frame 16280, timestamp 679.0117 s |
| Partition | regression, previously reviewed checkpoint |
| Recording group | recording-A, same original recording group as review-002 |
| Bundle/source receipt | Registered, s11-o2-bundle-link-v1 |
| Candidate input index | 19, discovered in current packet rather than assumed |
| Kind / source | oil_air / calibrated_high_recall |
| Canonical Y | 213, source-frame Y |
| Witness geometry | candidate_center only, five sectors spanning X [1199,1661), Y213 |
| Witness SHA-256 | 8ccc113e5dc3cf1a6738bb10e6be0ee6cd2419ab9f19796e7852e64a3ac70b20 |

The report identifies reuse of the existing bundle but does not independently
restate its detector/resolver/witness version fields or continuation-tool commit.
Earlier user-attested ZIP identities are not newly verified execution hashes.
The overall X extent does not specify each sector's individual interval and must
not be substituted for that geometry when recording path judgments.

## Human judgment reuse and scope

Windows reported checking the same video, exact zero-based frame, Glass,
source-frame coordinate, source and kind against the earlier direct human review
that confirmed the interface near Y213. The stored candidate identity is
**interface**, with review basis **prior_direct_review_exact_geometry_checked**.
No repeated image question was asked. Discarded LVLM readings Y137 and Y123 were
not used as truth.

Visibility is **visible**. No contour or path_reviews were generated. Identity
reuse does not certify a horizontal Y213 line across all five sectors, numeric
position tolerance, or another candidate's native path. The report's unusual
phrase about correspondence is treated as its claimed matching result, not a
separate technical verification method.

## Reported persistence and remaining scope

- Revision **0 → 1**; logical label SHA prefix **fdceb10b... → 373594f7...**.
  Only prefixes were supplied; no full hash is reconstructed here.
- Inventory: **27 candidates = 1 interface + 26 unreviewed**.
- Review-002 revision 14 / SHA prefix `102919b6...` and visibility remain unchanged.
  Its r10 frozen snapshot (`ce9c4373...`) and NOT_EVALUATED readiness report were
  reported preserved. Neither is an evaluation of review-003.
- No code modification or detector rerun was reported. Review-003 freeze,
  prediction evaluation, owner strings and classifier-status output were not
  included in this summary; do not infer those checks from identity completion.

This closes the requested single-candidate identity task by user report. The
frame remains partially reviewed. Alongside the BASE records it supplies another
regression example; it does not establish independent-recording diversity or
holdout performance.

## Revision 2 — material_path identity reviewed directly

The subsequent user-transferred report identifies the current packet's
`candidate_input_index=10`, `source=material_path`, `kind=oil_air`, canonical
source Y217. Witness SHA:
`315e0aee4d41f428b166106519c5af0bb140b74a1b7f3ad6f60a36bb58d74fd4`.
Its native path has five sectors with source Ys spanning 209–220. Individual
current sector coordinates were not included in this report.

The guide displayed the native path in cyan and reference Y213 in white. The user
was asked whether the path, considered as a whole, represents the actual liquid
interface and answered **interface**. Earlier evidence explicitly deferred this
candidate's physical judgment, so a new direct question was appropriate; no label
was inferred from Y213 proximity. The stored basis is **direct_human_review**.
The reference line is not certified contour truth across all X positions.

- Revision **1 → 2**; logical label SHA prefix **373594f7... → de4ac088...**.
- Inventory: **27 = 2 interface (IDs 10 and 19) + 25 unreviewed**.
- No path_reviews or contour were generated. Candidate 10's identity does not
  certify any of its five sector positions or establish independent support for
  candidate 19; shared feature derivation remains a separate question.
- This report does not restate owner values, visibility status, other-review
  hashes or freeze/evaluation checks. The earlier reported state is retained as
  historical evidence, without claiming a new verification of those fields.

## Revision 3 — five native-path positions reviewed directly

The user reports a slightly inclined interface and directly confirms all five
candidate 10 native-path positions as **near_interface**. S1–S5 below are the
review display labels, not assumed array indices. Source X extents are half-open
under the existing geometry contract; Y is source-frame Y.

| Display segment | Source X | Native source Y | Judgment |
|---|---|---|---|
| S1 | [1218, 1303) | 209 | near_interface |
| S2 | [1303, 1388) | 210 | near_interface |
| S3 | [1388, 1473) | 217 | near_interface |
| S4 | [1473, 1558) | 219 | near_interface |
| S5 | [1558, 1643) | 220 | near_interface |

- Revision **2 → 3**; logical label SHA prefix **de4ac088... → da8bbb92...**.
- Candidate 10 native-path summary: near 5, off 0, uncertain 0, unreviewed 0;
  reviewed point count 5, qualitative review coverage 1.0.
- Identities 10 and 19 remain interface; visibility remains visible. There are
  still 25 unreviewed identities out of 27 proposals.
- No candidate-center reviews or contour were generated. Full qualitative
  review coverage does not establish numeric error, an accepted tolerance,
  independent support, or classifier performance.
- Review-002 revision 14 / SHA prefix `102919b6...`, its frozen r10 snapshot
  (`ce9c4373...`) and NOT_EVALUATED readiness report were reported unchanged.
- No code change, detector rerun, freeze or evaluate was performed in this step.
  Stored reviewer/basis fields were not restated in this transferred summary;
  the user explicitly reports direct confirmation of the five positions.

## Next bounded task after revision 3

Pause additional candidate questions and freeze the review-003 revision-3 labels
to a new immutable snapshot, followed by no-prediction readiness evaluation using
the existing procedure. Verify the unchanged source labels and retain unreviewed
proposals explicitly. Neither file exists by the evidence reported here yet.
Keep review-002's r10 artifacts intact; do not combine reviews in this step.
The next analysis can bind stored labels to witness measurements to examine
identity discrimination separately from path localization. This small regression
set does not select an operating threshold or qualify a classifier.

## Detector Governance

- Logic-map nodes: `TRACE-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F09`.
- First harmful stage: no new detector failure inferred; this records scoped reuse and a subsequent direct candidate identity judgment, without promoting scalar Y or whole-candidate identity to full-path truth.
- Logic-map impact: NONE — transferred annotation evidence changes no detector, trace writer, evaluator or UI execution.
- Failure-registry impact: NONE — no new causal mechanism or field repair is established by a single stored identity label.
