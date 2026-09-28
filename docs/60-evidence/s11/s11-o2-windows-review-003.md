# S11 O2 Windows review-003 — Accum reviewed identity reuse

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

## Next bounded task

Review the same-frame material_path candidate near canonical Y217, if uniquely
present in the current packet. Discover its current input ID and witness geometry;
do not inherit identity or per-sector labels from candidate 19 or Y proximity.
Use an existing explicit judgment only within its verified scope. For new review,
open or provide the exact plain/annotated image paths first, with source Y ticks
and clearly named target geometry. Preserve candidate identity and any explicitly
reviewed path points separately. No synthetic contour, detector rerun, or review
of all remaining candidates is required for that bounded step.

## Detector Governance

- Logic-map nodes: `TRACE-PUBLICATION`, `RESULT-PRESENTATION`.
- Failure-registry entries: `S11-F09`.
- First harmful stage: no new detector failure inferred; this records scoped reuse of an earlier human identity judgment and reported persistence, without promoting scalar Y to full-path truth.
- Logic-map impact: NONE — transferred annotation evidence changes no detector, trace writer, evaluator or UI execution.
- Failure-registry impact: NONE — no new causal mechanism or field repair is established by a single stored identity label.
