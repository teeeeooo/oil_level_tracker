# S11 passive control review — first batch intake

Date: 2026-10-06. Basis: user-transferred Windows reports; first-case intake
followed by the final batch return and user clarifications below. Earlier
continuation and pending-target statements are historical; the final target
clarification supersedes them.
Procedure: [first bounded batch](../../40-operations/s11-o2-local-shadow-evaluation.md#passive-control-review--first-bounded-batch).
Current gate and next action remain owned by the [work plan](../../00-project/work-plan.md#next-transition).

## Reported first-case result

| Field | Transferred value |
|---|---|
| case_id | `w4-passive-001-accum-drain` |
| Glass / frame / time | Accum / 17383 / 725.02 s |
| Reviewed segment | `WS1-ACCUM-DRAIN` |
| visibility / revision_count | `visible` / 2 |
| Answers used | 2/2 for this case; 2/6 for the batch |

| Candidate input index | Source | canonical_y | Reported stored identity | Human boundary explanation |
|---|---|---|---|---|
| 10 | `material_path` | 304 | `interface` | 유체1/유체2 경계 (중간 경계). oil_air 후보로 분류되었으나 실제로는 두 유체 사이의 경계 |
| 13 | `material_path` | 291 | `interface` | 유체2/공기 경계 (상부 유면). 2개 유체 층 구조에서 상부 유체의 표면 |

These are two distinct boundary roles reported by the human reviewer at this
frame. Preserve both explanations and their actual stored identities. The
report does not identify the composition of fluid 1 or fluid 2, or explicitly
bind either boundary to the application's target Oil surface. The `oil_air`
proposal kind is not independent physical truth. Canonical Y values are not
reviewed contours; native-path coordinates were not supplied in this return.

“Two fluid layers” is the reviewer's scene interpretation, not a new composition
measurement or proof of separation throughout the drain interval. No identity
or temporal linkage is transferred to f16280, f14386 or f14865. Existing
idx0/idx20 and f14865 ambiguity and historical labels remain intact.

## Target semantics before evaluation

The [review contract](../../20-architecture/s11-interface-observability-witness-architecture.md#separate-review-questions)
asks about the Oil interface. The current
`tests/diagnostics/s11_interface_shadow_evaluation.py::summarize` consumes
`identity=interface` as a positive label; explanatory notes do not automatically
exclude a different material boundary from those counts.

Consequently, this intake is **not clearance to use both annotations as target
Oil positives**. Preserve the Windows replies/labels/history as reported, with
the distinct boundary roles in notes. Target-material mapping remains pending
before any training, target-specific evaluation or label promotion using this
case. This is a procedural hold on that use, not a new enforced schema field.
Do not silently rewrite either answer to non_interface/uncertain, assign a
shared entity ID, or choose upper/lower by geometry. No additional first-case
judgment is requested within its exhausted two-answer allowance.

## Reported artifacts and preservation

Windows folder: `data/w4-passive-review-001/`.

- `selection.json`, `selection-manifest.json`: three selected cases and provenance.
- `prepared/packet.json`: reported 75 candidates across the batch.
- `prepared/labels.json`: first-case answers and review history.
- `accum_drain_f17383_plain.png`, `accum_drain_f17383_guide.png`, `gen_display.py`.
- `replies/reply-001.json`: idx10 answer; `reply-002.json`: idx13 answer and idx10 note correction.
- `other-recordings-metadata.json`: only SPL#1 found in the searched scope;
  this does not establish that other recordings do not exist.

Reported labels SHA-256:
`ee1d0b2dc17993eb7ca11de4f4ebb30bc57c4dc7a777d6a0bf11e134814f1633`.
Reported original ROI hash prefix `3a4cc326…` was unchanged before/after; a full
hash was not supplied. Existing review-001/002/003 and region outputs were
reported unchanged. No detector rerun, model training or comparative filming
was reported. These private artifacts/images were not independently opened or
rehashed in this repository intake.

## First-case continuation (historical)

| Case | Reported state | Remaining allowance |
|---|---|---|
| Accum drain / frame17383 | First-case review complete; target mapping pending | 0 |
| BASE full / frame17383 | Pending | 2 |
| Accum post-Foam / frame16543 | Pending | 2 |

Continue the latter two prepared cases, checking their exact record/Glass
against the existing manifest. Reuse the prepared packet and current labels;
do not restart selection or prepare a replacement batch. Display plain RGB and
the packet-derived guide, and obtain actual answers without imposing expected
labels or the first case's layered interpretation. If a reviewer describes
multiple boundary types, retain that distinction in the same answer; unknown
material names remain unknown. Stop after the remaining four answers at most,
or report unavailable/uncertain outcomes under the existing procedure.

All SPL#1 cases retain their existing recording group and regression partition.
Same-frame Glasses do not provide independent recordings. The batch has not
established a cue-sharing opposing control or met sample/acceptance obligations.
No additional measurement, training, threshold, W4-R2 entry or field promotion
follows from this return. FIELD FAIL / NOT_EVALUATED remain unchanged under the
[O2 acceptance owner](../../30-validation/s11-interface-observability-witness-validation.md#o2-shadow-acceptance).
The [reviewed timeline](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md#reviewed-timeline)
is not rewritten from this single-frame interpretation.

## Final batch return — all 75 candidates reported labeled

The user subsequently reported the following complete label inventory:

| Case | Visibility | Candidates | interface | non_interface | uncertain | unreviewed |
|---|---|---|---|---|---|---|
| accum-drain / f17383 | visible | 26 | 7 | 19 | 0 | 0 |
| base-full | not_visible | 21 | 0 | 21 | 0 | 0 |
| accum-postfoam / f16543 | visible | 28 | 6 | 22 | 0 | 0 |
| Total | | 75 | 13 | 62 | 0 | 0 |

The final return omits the BASE frame number; f17383 is retained from the
earlier batch report, not a fresh verification of the final labels file.
Reported `revision_count`: **12**. Reported final labels SHA-256:
`55672fe9182129a3baef8ba8df57f12fdcd252d9296f2bb1ad4903d855ae02a8`.
This is a later labels revision, not a conflicting checksum for the first-case
revision. Neither private labels version has been independently rehashed here.

| Case / reported boundary role | Reported interface candidate indices | Approximate canonical Y |
|---|---|---|
| accum-drain: upper fluid2/air | 4, 13, 17, 24 | 290–292 |
| accum-drain: lower fluid1/fluid2 | 5, 10, 18 | 302–304 |
| accum-postfoam: one reported surface band | 5, 6, 10, 19, 20, 25 | 186–198 |

The supplied sums and positive-index counts are internally consistent: 26+21+28
=75, 7+6=13 and 19+21+22=62. Multiple proposals at one boundary are not independent
physical controls. Approximate canonical Y groupings do not establish native-path
agreement, interval truth, material identity or continuity across frames.

### Attribution and scope reconciled — user clarification

The original handoff allowed six candidate answers; the final inventory contains
75 labels and twelve revisions. The user subsequently clarified the actual review:

> native path가 있는 후보를 먼저 확인하고, 그 중 실제 경계면에 근접한 몇개의 후보를 추가 판독함.
> 경계면에서 먼 후보들은 일괄 non_interface 판정함.
> case2의 경우 oil이 가득 찬 상태라 모두 non_interface였음.

This confirms user-directed expanded review, including group judgments; the
original workload cap does not invalidate those answers. The attribution/scope
question is closed. No repeat review or automatic relabeling is requested.

| Review basis | User-confirmed action | Interpretation limit |
|---|---|---|
| Candidate-guided review | Native-path candidates first, then additional candidates close to the actual boundary | The clarification does not enumerate which individual indices received separate inspection |
| Group negative judgment | Candidates far from the boundary were assigned non_interface together by the user | Preserve as a human group judgment, not individually inspected artifact types or a reusable Y-distance cutoff |
| Full-scene group negative judgment | BASE case2 was Oil-full and the user judged all candidates non_interface | Preserve the explicit 21-candidate group judgment and not_visible scene state; no inference that Oil is absent |

The inventory remains 75 labeled candidates, not 75 separately inspected physical
objects or independent observations. Keep the actual replies/history and each
candidate's recorded attribution. Do not invent an index-to-review-basis mapping
from Y or source family when the summary does not provide it. This clarification
establishes the review method, not a byte-level audit of Windows records.

**Disposition: reported labeling complete; user/group attribution clarified.**
The reported labels remain unchanged. First-case target Oil mapping is still
unresolved; candidate kind and relative height do not settle which of the two
reported boundaries is the application's target. No model fitting or target
Oil evaluation using those unresolved positives follows from this clarification.
Final-run original-input preservation was not restated in the summary; the
earlier preservation claim applies to the earlier stage only.

The next question is the material identity of fluid1/fluid2, if known, and which
boundary should represent the product's Oil height. Unknown is a valid answer.
This is target clarification, not a request to repeat candidate review. BASE
negatives and post-Foam positives provide additional user-reviewed development
labels with the stated review bases; they do not establish matched optical
opposition, independent holdout success or O2 acceptance. In particular, remote
negatives cannot alone test rejection of artifacts sharing the surface's local
appearance. FIELD FAIL / NOT_EVALUATED remain unchanged.

## Target resolved — uppermost actual fluid boundary

The user clarified that fluid1 is liquefied refrigerant and fluid2 is Oil, and
that material-species classification is optional rather than required. The
requested tracked boundary is the **uppermost actual fluid boundary**: upper
of two, uppermost of three, and similarly for further layers. This is a
user-specified product target, not an agent inference from canonical Y.

The [product specification](../../rotary_oil_level_tracker_ssot_spec.md#다층-유체의-추적-대상)
owns this definition. The chemical interpretation is attributed to the user;
no new chemical measurement was performed. Target clarification is closed and
no repeat image judgment or further fluid-classification answer is needed.

Applied to the previously supplied candidate groups:

| Case / group | Candidate indices | Physical review retained | Target role |
|---|---|---|---|
| accum-drain upper Oil/air | 4, 13, 17, 24 | interface | Target positive (4) |
| accum-drain lower refrigerant/Oil | 5, 10, 18 | interface | Real internal boundary, non-target (3) |
| accum-postfoam single reported surface | 5, 6, 10, 19, 20, 25 | interface | Target positive (6) |
| Remaining candidates across all three cases | As supplied in the final inventory | non_interface (62) | Reported non-target; retain individual/group review attribution |

This is a semantic mapping from user-provided groups and the clarified target,
not a private-file projection or a new labels revision. The physical inventory
remains **13 interface / 62 non_interface**. Its target interpretation is
**10 target / 3 real internal non-target / 62 other non-target**; the latter
62 do not receive invented artifact subclasses. These are candidate counts,
not independent boundary samples, model predictions, or accuracy measurements.

The original labels SHA and revision_count remain those in the final return;
no private labels/replies were edited. The current evaluator cannot consume this
mapping automatically. Before a target-specific run, bind an explicit versioned
target-truth snapshot to case/input-index/witness and original label provenance,
retaining physical identity and the user's target instruction separately. Do not
silently feed all 13 broad-interface positives into a target evaluation or erase
the three genuine lower-interface observations. Formal mapping is the next
preparation step, not a request for another scene review or detector replay.

Identifying the uppermost real boundary still requires rejecting reflections,
structures and residue and recognizing unavailable/ambiguous targets. Minimum Y
over raw proposals is not that discrimination. A lower visible interface must not
stand in for an occluded target. Independent Foam ownership, same-frame numeric
provenance, FULL no-interface and UNKNOWN behavior are retained. The new internal
boundary group provides a relevant target distinction but does not by itself
establish a classifier, matched optical counter-control, independent holdout or
O2 acceptance. FIELD FAIL / NOT_EVALUATED remain unchanged.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`.
- Failure-registry entries: `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: no new detector failure is established; the evidence-use risk is conflating a real internal boundary with the now-clarified uppermost target when evaluating historical broad-interface labels.
- Logic-map impact: NONE — attributed review intake and procedural target-mapping hold only; candidate generation, authority and evaluator code are unchanged.
- Failure-registry impact: NONE — retain physical-role/provenance distinctions without geometry-based identity transfer or a private-case rule.
