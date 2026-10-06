# S11 passive control review — first batch intake

Date: 2026-10-06. Basis: user-transferred Windows reports; first-case intake
followed by the final batch return below. Earlier continuation instructions are
historical and are superseded by the final-return disposition.
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

### Attribution and scope reconciliation pending

The original handoff allowed at most two candidate answers per case (six total),
whereas this return reports 75 labeled candidates and twelve revisions. Those
counts alone cannot distinguish explicit human review of candidate groups from
agent propagation of a boundary/scene judgment. Revision count is not a count
of separately judged candidates. The supplied summary does not include the
intervening replies or explain the expansion of review scope.

Ask the user once whether they directly reviewed all candidates individually or
as explicitly identified groups, whether labels were extended by the agent, or
whether both occurred. Do not infer misconduct or discard genuine judgments
from the scope difference alone. Explicit user-directed expanded review, if
confirmed, takes precedence over the original workload cap. Conversely, nearby
Y, shared source, or scene visibility is not by itself a direct candidate review;
`not_visible` must not silently supply 21 individual human explanations.

Preserve the reported files and history without bulk relabeling. Until attribution
is clarified, record the batch as **reported labeling complete; review provenance
pending**, not 75 independently verified human judgments or accepted evaluation
truth. First-case target Oil mapping also remains unresolved. No repeat image
review, new candidate collection or model fitting is requested by this intake.
Final-run original-input preservation was not restated in this summary; the
earlier preservation claim applies to the earlier stage only.

The next action is attribution clarification and target-boundary mapping before
using these labels in target-specific evaluation. BASE negatives and post-Foam
positives may supply further development controls if their attribution is
established; they do not independently establish matched optical opposition,
holdout success or O2 acceptance. FIELD FAIL / NOT_EVALUATED remain unchanged.

## Detector Governance

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`.
- Failure-registry entries: `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: no new detector failure is established; the identified evidence-use risk is conflating a reported material boundary with target Oil identity before evaluation.
- Logic-map impact: NONE — attributed review intake and procedural target-mapping hold only; candidate generation, authority and evaluator code are unchanged.
- Failure-registry impact: NONE — retain physical-role/provenance distinctions without geometry-based identity transfer or a private-case rule.
