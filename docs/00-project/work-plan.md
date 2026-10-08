# Current Work Plan

**Current milestone:** `S11 — Real-Field Detector Effectiveness Recovery` / `ACTIVE`.
**Current gate:** O1 locally accepted; W4 candidate-identity challenger and O2 acceptance remain OPEN.
**Field disposition:** latest user-reported Windows result remains `FIELD FAIL`.
**Accepted baseline:** R22 behavior with R22-3/O1 diagnostics; report source context and episode-source review are main-adopted. No new detector behavior is adopted by the October 8 intake.
**Next transition:** D1 CLOSED. D2 local control preflight complete; algorithm unselected. WAITING FOR WINDOWS: one saved target-bound Accum drain case (26 candidates), using the prepared query. No D1 rerun or new human judgment is requested.

This is the sole current state, authorization, unknowns and next-action owner.
The [October 8 supplied specification](../70-reference/s11-next-work-2026-10-08/S11-next-work-spec-2026-10-08.md)
is a preserved proposal, with [intake and cleanup evidence](../60-evidence/s11/2026-10-08-next-work-intake.md).
Historical pending prose never reopens a closed experiment or supplies current authority.

## S11 work-item ledger

O1–O5 remain the staged design/acceptance framework. W0–W4 refine O2;
W5/W6/W7 correspond to O3/O4/O5. D0–D6 are the October 8 task aliases below,
not additional milestones or another live status list. IMPLEMENTED, VERIFIED,
ACCEPTED and CLOSED WITHOUT PROMOTION retain their distinct meanings.

| Work item / stage | Current state | Next condition / D mapping | Owner or evidence |
|---|---|---|---|
| O1 extraction | IMPLEMENTED; locally ACCEPTED | Reuse trace-only extraction; no identity authority | [O1 evidence](../60-evidence/s11/s11-r22-3-interface-witness-diagnostics.md) |
| W0 / O2 fixed profile | Windows result transferred; CLOSED WITHOUT PROMOTION | No rerun; candidate identity worsened | [Profile result](../60-evidence/s11/s11-o2-identity-profile-windows-run-001.md) |
| W1 / O2 target and aggregation | Definitions and local controls verified; passive Windows target binding complete | Preserve physical identity, target role and path/scalar distinctions; prediction remains NOT_EVALUATED | [W1](../60-evidence/s11/s11-o2-w1-target-aggregation-controls.md), [binding return](../60-evidence/s11/s11-o2-passive-control-review-001.md#windows-target-binding-returned--closed-without-prediction-evaluation) |
| W2 / O2 scene expansion | Bounded transferred geometry review CLOSED | No repeat inventory/relabeling; unresolved alternatives remain | [W2 reconciliation](../60-evidence/s11/s11-o2-w2-f14865-scene-review.md#geometry-reconciliation-received-and-bounded-w2-closed--2026-10-02) |
| W3 / O2 evaluation | Tools locally verified; Windows target/context audit and D1 return transferred | D1 recorded readout CLOSED with named unknowns; review-001 corrected. D3 reuses evaluator; tooling is not efficacy | [W3 local](../60-evidence/s11/s11-o2-w3-target-evaluation-local.md), [D1 reconciliation](../60-evidence/s11/2026-10-08-next-work-intake.md#d1-saved-record-reconciliation--closed) |
| W4 / O2 challenger | OPEN; prior frozen challengers closed without promotion | D2 control preflight complete; one Windows support/provenance query pending before mechanism selection. D3 not started | [D2 preflight](../60-evidence/s11/2026-10-08-d2-control-preflight.md), [Witness Architecture](../20-architecture/s11-interface-observability-witness-architecture.md#d2-boundary-role-design-entry) |
| O2 acceptance | OPEN; not satisfied | Controls/holdouts, operating point, behavior equality and Windows shadow acceptance required | [O2 gate](../30-validation/s11-interface-observability-witness-validation.md#o2-shadow-acceptance) |
| W5 / O3 support and association | PROPOSED; gated on O2 | D4a: separate implementation plan, typed support and exact physical association | [O3 entry](../30-validation/s11-interface-observability-witness-validation.md#o3-behavior-entry) |
| W6 / O4 handoff and phase | PROPOSED; gated on W5 and separate controls | D4b: bounded reacquisition and closure, with FULL/EMPTY counter-controls | [O4](../20-architecture/s11-interface-observability-witness-architecture.md#stage-o4--handoff-and-phase-behavior) |
| Foam front / episode | Separate proposed work | D5: own design and single-change comparison before integration; no automatic Oil-gate bypass | [Responsibility architecture](../20-architecture/s11-detector-responsibility-architecture.md), [Foam investigation](../50-diagnostics/s11/2026-10-06-foam-structure-reference-audit.md) |
| W7 / O5 field qualification | PENDING integrated candidate | D6: exact runtime, all nine canonical segments, existing report and target resources | [Field gate](../30-validation/s11-interface-observability-witness-validation.md#field-qualification) |
| Report adjuncts | Source context and episode-source review ADOPTED | Reuse existing report; comprehension and numerical identity remain separate unresolved outcomes | [Source context](../60-evidence/s11/2026-10-07-report-source-context-validation.md), [episode review](../60-evidence/s11/2026-10-08-episode-source-review-validation.md) |
| D0 planning intake | Source audit completed; originals and local receipts verified | Planning baseline only; no detector or field acceptance | [Intake record](../60-evidence/s11/2026-10-08-next-work-intake.md) |

W4-R0–R5 remain internal continuation labels: R0 correction and R3 inventory are
complete; R1 is closed without promotion; its censored comparison remains
NOT_ASSESSABLE; R2 entry is unmet. R4 evaluation and R5 disposition apply only to
a new eligible hypothesis. [Joint-context disposition](../60-evidence/s11/s11-o2-joint-context-windows-run-001.md#w4-r0-correction-received-and-w4-r1-disposition--2026-10-02)
and [R3 inventory](../60-evidence/s11/s11-o2-w4-r3-existing-evidence-feasibility.md) retain detail.

## Next transition

1. D1 CLOSED — the stdlib-only reader from `e5d4a04` passed 40 local contracts;
   Windows execution and [saved-record reconciliation](../60-evidence/s11/2026-10-08-next-work-intake.md#d1-saved-record-reconciliation--closed)
   are transferred evidence. Review-001's legacy loss counts are 0 `not_selected` /
   11 tracklet rejections / 12 absent refs, superseding the old 7/7/9 table. Totals are 45 retained / 28
   absent. `None` selection means `NONE_SELECTED`, not automatically
   `FINAL_SELECTION_UNRESOLVED`. Pre-retention and first physical causes remain
   named unknowns. No D1 rerun or additional Windows return is needed.
   Input/tool/output pins remain in the evidence owner; the rest of both
   diagnostic branches stays unadopted.
2. D2 control/reuse design is recorded in the [preflight](../60-evidence/s11/2026-10-08-d2-control-preflight.md).
   Stop for the [bounded Windows query](../40-operations/s11-o2-local-shadow-evaluation.md#d2--existing-target-bound-control-query):
   existing Accum drain f17383, all 26 candidates (4 target/3 real internal/19 other).
   The missing condition is an exact-bound target/non-target distinction with
   observable support/opposition, not more labels or target-definition review.
   Preserve existing idx0/idx20 ambiguity, the separate W3 73/passive 75 inventories,
   and all Mac regression controls. Do not select a nearest-Y/score-ranked negative.
3. D2 must identify a distinct candidate-local observable and a concrete frozen
   algorithm, with target-positive, cue-sharing negative and unresolved controls.
   Separate physical boundary, product role, path support and scalar usability.
   H-ROLE is a proposal name, not an implemented or proven classifier. Keep optical/
   texture opposition and distinguish paired-pulse measurement from boundary support.
   If the distinguishing evidence is unavailable, name that one missing condition
   before requesting Windows work or human judgment; do not add an empty classifier.
4. Before D3, freeze input identities, exposure/partition roles, operating-point
   policy, resource bounds and falsification. Compare wrong-target suppression
   separately from true-target recovery, through W3 and the unchanged report.
   All-abstain and raw output growth are not success. Missing Windows data does
   not justify guessed production behavior; independent data gates remain explicit.
5. O2 acceptance precedes D4a; phase/handoff D4b has its own gate. D5 Foam needs
   independent design and ablation. D6 evaluates the integrated exact runtime.

The endpoint is whether users can understand real rise/fall/reappearance and
Foam onset/disappearance in the existing report. Protect genuine rapid excursions;
short misses can be reported as residual limits, while wrong owners, false extrema
and lost major movement remain consequential. This supplements existing acceptance,
not a new threshold or a replacement for O2/field validation.

## Accepted local candidate

- **Behavior:** locally accepted R22 Oil ownership/evidence replacement. [Architecture](../20-architecture/s11-r22-oil-ownership-evidence-replacement-architecture.md), [validation](../30-validation/s11-r22-oil-ownership-evidence-replacement-validation.md), [evidence](../60-evidence/s11/s11-r22-ownership-evidence-replacement.md).
- **Diagnostic runtime:** `opencv-phase-detector-r22-3-interface-witness-diagnostics-v1`.
- **Completed-window resolver:** `r22-oil-ownership-evidence-replacement-v1`; unchanged by diagnostics.
- **Protected comparisons:** R21 behavior and R22-2 native-path diagnostics, retaining R22-1 measurements. No R23 behavior was promoted.
- **Report:** source context adopted from `0a60b11`; episode-source review code `52003aa` adopted through `ae47d5c`. These do not repair detector identity or establish independent comprehension.

R22 evidence retains canonical/Qt/replay/performance results, truth and tracking
fingerprints. O1 trace growth is about fourfold: captures remain bounded. Existing
R22-3 bundles/v1 labels stay usable; no runtime revision or rerun is required for D1.

## Closed work and preserved review obligations

Completed chronology stays in the linked owners. These retained conclusions
prevent repeated questions and unsafe reuse of previously exposed controls.

| Topic | Preserved result / limitation | Detail owner |
|---|---|---|
| October 7 adoption | A0B, report wording/display cap and Oil event compatibility adopted; A1 diagnostic lineage complete; paired scorer rejected; A0Q unresolved | [Adoption checkpoint](../60-evidence/s11/2026-10-07-audit-adoption-checkpoint.md), [report adoption](../60-evidence/s11/2026-10-07-report-context-adoption.md), [event compatibility](../60-evidence/s11/2026-10-07-event-compatibility.md), [A1](../60-evidence/s11/2026-10-07-a1-measurement-lineage.md) |
| sample4 Oil controls | Seven exact Oil correspondences and three rejected targets bound; four correct observations protected. Wrong-target subtypes remain one unresolved/two tentative. Same Y, family or tracklet is not transferable truth | [Lineage and replies](../50-diagnostics/s11/2026-10-07-sample4-interval-candidate-lineage.md), [binding](../60-evidence/s11/2026-10-07-a2-target-binding.md) |
| Temporal context | User requires static and temporal evidence; one actual boundary moves rapidly through 42.5–44 s. Short forward correspondence confirmed, other seeds/directions drift. No intermediate Y/speed truth; standalone matcher rejected | [Human reply](../50-diagnostics/s11/2026-10-07-sample4-temporal-context-human-reply.json), [patch comparison](../60-evidence/s11/2026-10-07-a2-patch-correspondence.md) |
| Region/texture hypotheses | A/B interpretation closed; fixed joint region exchange loses all seven targets. Fixed side texture and earlier locality/color/profile/paired-scale models closed without promotion; no threshold continuation | [Region exchange](../60-evidence/s11/2026-10-07-a2-region-exchange.md), [episode evidence](../60-evidence/s11/2026-10-08-episode-source-review-validation.md), [color disposition](../60-evidence/s11/s11-o2-color-side-local.md#denominator-reconciliation-closed-and-bounded-region-disposition) |
| Latest delivery experiments | H1/H1b fail terminal/ownership safety; LabPics, cellular and selector trials closed without promotion. Three sample4 targets fail before selector entry; no new Windows first cause is established. Both branches remain unmerged | [Windows-first closeout](https://github.com/teeeeooo/oil_level_tracker/blob/e5d4a0430ea69beab59736396a2817c09b5efd69/docs/60-evidence/s11/2026-10-08-windows-first-detector-closeout.md), [cellular closeout](https://github.com/teeeeooo/oil_level_tracker/blob/e5d4a0430ea69beab59736396a2817c09b5efd69/docs/60-evidence/s11/2026-10-08-cellular-selector-closeout.md) |
| Windows passive controls | 75-candidate batch retains 13 interface/62 non-interface and target roles 10 target/3 real internal/62 other. Individual/group attribution preserved; binding returned, NOT_EVALUATED. W3's 73-candidate inventory is distinct; no index-only joins | [Passive review and binding](../60-evidence/s11/s11-o2-passive-control-review-001.md) |
| Product target | Uppermost actual fluid boundary; optional species classification. Internal real interfaces stay non-target; Foam remains a separate series. No repeated target-definition or material question | [Product contract](../rotary_oil_level_tracker_ssot_spec.md#다층-유체의-추적-대상) |
| Local source review | Existing corpus/joins reusable as regression. sample2 Foam-gap differs from sample4 Foam–air boundary; base qualitative Oil offset and new Foam observation do not overwrite historical scalar truth | [Local reuse and replies](../60-evidence/s11/2026-10-06-local-corpus-target-reuse.md) |
| Foam geometry | sample4 rim C1 versus Foam-region C2 correspondence known; actual column support differs from bbox relation. Mixed central structures and sample2 reflected features remain unresolved; no blanket veto removal | [Owner audit](../50-diagnostics/s11/2026-10-06-local-oil-foam-owner-audit.md) |
| Foam front/motion | A/C/D Foam, B mixed; red marks tentative, 14/16 s clicks approximate. Central circular features are structures, but exact front/structure split remains unassigned. Appearance/motion-only selectors rejected | [Front alternatives](../60-evidence/s11/2026-10-06-foam-front-alternatives.md), [residuals](../60-evidence/s11/2026-10-06-boundary-temporal-residuals.md), [selection feasibility](../60-evidence/s11/2026-10-06-foam-edge-selection-feasibility.md) |
| ROI / paired-pulse controls | Existing ellipse works; human-ROI recipe remains unadopted. Inner/outer clicks retain uncertainty. Oil Y854 confirmed at 14 s; selected Y821 unresolved. Pulse correction failed safety and was restored; diagnostic reason repair accepted. Collision controls and opposition remain required | [Structure/ROI/authority audit](../50-diagnostics/s11/2026-10-06-foam-structure-reference-audit.md) |
| sample3 reappearance | FILLED_CAP_VETO occurs in 87/92 missing rows of the audited long gap; those candidates are not thereby true Oil. Phase repair needs identity and two-sided controls | [Episode audit](../60-evidence/s11/2026-10-08-episode-source-review-validation.md) |

## Current authorization boundary

The current October 8 instruction authorizes the agreed staged work, checking
and safely disposing of the sibling results folder, and autonomous logical commits
and push. **Stop and report when user judgment or work on Windows is required.**
This stop instruction governs the next transition; retained commands are not
permission to run private media or claim field acceptance.

Earlier bounded report adoptions are complete. Prior detector-development grants
permit the relevant bounded local investigation, subject to the O2/behavior gates;
they do not authorize unrelated changes. Main owns implementation and final review;
the user's no-further-sub-agent instruction remains in force.

Excluded are unbounded retention/recovery, relaxed truth/safety, silent golden
regeneration, private case/Glass/time/Y branches, interpolation/carry/report repair,
a whole-detector rewrite, and speculative Accum changes without reviewed identity.
D5 is planned separate work, not current authorization to mix Foam changes into D1.

## Preserved contracts

- One generic detector serves every Glass; reviewed coordinates and private identity never control production.
- Numeric Oil/Foam values remain exact same-frame selected candidates; validity and ownership stay independent.
- FULL/EMPTY never fabricate coordinates or copy physical IDs across rapid-refill handoff.
- Ambiguous, unavailable, lost or hard-invalid evidence fails closed without downstream repair.
- Physical identity, product target, path localization and scalar eligibility have separate truth and acceptance.
- Known recordings/checkpoints are regression, not untouched holdout; missing support, model abstention and truth uncertainty differ.
- New-run hashes do not prove old-run immutability; nested channels/gains are not independent successes.

## Open field risks and named unknowns

R22 is not field-qualified. Base release/refill/full closure and Accum initial
entry, continuity/layered/post-Foam ownership and drain re-entry remain field
uncertainties. Generic controls do not establish their private first cause.
Candidate identity, cue-sharing optical counter-controls, scalar truth, calibration
and a real-image operating point remain unresolved. A0Q Qt stability and independent
report comprehension stay open separately from detector research.

Historical sample4 `0f202947...` differs from the current `e447626b...` replay;
`d50c143` reproduces the current result with unchanged media, while the old decoder/
Python/OpenCV environment remains unknown. Keep the golden unchanged and use the
[runtime provenance diagnostic](../50-diagnostics/s11/s11-r21-replay-runtime-provenance-diagnostic.md).
The canonical source companion fingerprint/operator provenance remains pending;
an O2 bundle-link hash alone does not close it or invalidate linked labels.

Additional review of existing recordings is permitted; comparative filming is
unavailable. Record session lineage/prior exposure and freeze development,
calibration and holdout roles before new pixel inspection/model selection.
Existing Mac recordings and SPL#1 stay regression; nearby frames/Glasses are not
independent holdout. Do not repeat the independent-video availability question.
Existing partition locks and idx0/idx20 ambiguity remain pinned. Windows records
are attributed reports; full private CSV/media were not read locally.

## Active follow-up design

The [physical-interface proposal](../20-architecture/s11-physical-interface-evidence-repair-design.md),
[Witness Architecture](../20-architecture/s11-interface-observability-witness-architecture.md)
and [Witness Validation](../30-validation/s11-interface-observability-witness-validation.md)
remain the design/acceptance owners. Update them when D2 makes a concrete decision;
the supplied specification does not silently replace their contracts.
Independent support, association, committed handoff and initial-FULL observation
remain separate later gates. Failed descriptors do not prove physical unobservability.

## Current authority links

- [Roadmap](roadmap.md), [execution policy](execution-policy.md), [retained commitments](retained-commitments.md)
- [Document roles](../README.md#s11-audit-specifications-and-execution-routing), [recall index](recall-index.md)
- [Detector Skill](../../.agents/skills/s11-detector-change/SKILL.md), [governance](../30-validation/s11-detector-change-governance.md)
- [Logic map](../20-architecture/s11-current-detector-logic-map.md), [failure registry](../50-diagnostics/s11/s11-detector-mechanism-failure-registry.md)
- [Canonical Windows truth](../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md), [field procedure](../40-operations/s11-current-windows-field-qualification.md)
- [O2 saved-output operations](../40-operations/s11-o2-local-shadow-evaluation.md)

Update current state in place; detailed completed results belong in their evidence
owners. Dated source audits and frozen machine artifacts retain their original bytes.
