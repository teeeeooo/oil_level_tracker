# Current Work Plan

**Current milestone:** `S11 — Real-Field Detector Effectiveness Recovery`
**Milestone status:** `ACTIVE`
**Current gate:** O1 accepted locally; W4 candidate-identity challenger and calibrated O2 acceptance remain OPEN. Candidate-conditioned region competition is implemented and verified locally as an offline appearance prototype. The Windows region run is reported COMPLETE and both transfer items are closed on user-confirmed saved values. A bounded appearance distinction is visible, but whole-candidate and chromatic identity benefit remain unestablished.
**Field disposition:** latest user-reported Windows result remains `FIELD FAIL`; no field-qualified detector is claimed.

This document owns current state, authorization, unknowns and the next transition.
Completed execution detail belongs in linked evidence. Historical pending wording
in audits or evidence does not reopen a closed experiment.

## S11 work-item ledger

[Document relationships](../README.md#s11-audit-specifications-and-execution-routing)
map September O1–O5 to October W0–W7. This is the only live W-status list.
IMPLEMENTED, VERIFIED (within the stated scope) and ACCEPTED are distinct.
CLOSED WITHOUT PROMOTION ends an experiment without satisfying O2 acceptance.

| Work item / stage | Current status | Boundary / next condition | Evidence or owner |
|---|---|---|---|
| O1 extraction | IMPLEMENTED; locally ACCEPTED | Trace-only production equality; no identity authority | [O1 evidence](../60-evidence/s11/s11-r22-3-interface-witness-diagnostics.md) |
| W0 / O2 fixed profile | Windows result VERIFIED by transferred report; CLOSED WITHOUT PROMOTION | Candidate identity worsened; no rerun requested | [Profile result](../60-evidence/s11/s11-o2-identity-profile-windows-run-001.md) |
| W1 / O2 targets and aggregation | Source review, target contract and counter-controls VERIFIED locally | Candidate identity, local path support and scalar eligibility stay separate; challenger remains open under W4 | [W1 controls](../60-evidence/s11/s11-o2-w1-target-aggregation-controls.md) |
| W2 / O2 bounded scene expansion | Frame14865 scene and geometry review COMPLETE on transferred evidence; bounded handoff CLOSED without identity promotion | Two unresolved boundary alternatives; four native paths and nineteen center-only candidates; no formal relabeling | [W2 reconciliation](../60-evidence/s11/s11-o2-w2-f14865-scene-review.md#geometry-reconciliation-received-and-bounded-w2-closed--2026-10-02) |
| W3 / O2 shadow outputs and evaluation | IMPLEMENTED and VERIFIED locally; existing-data Windows target/context audit VERIFIED by transferred report | Preserve v1 compatibility and calibration guards; scalar truth remains absent; no efficacy claim | [Local evidence](../60-evidence/s11/s11-o2-w3-target-evaluation-local.md), [Windows audit](../60-evidence/s11/s11-o2-w3-target-audit-windows-run-001.md) |
| W4 / O2 one challenger | Local-position and fixed color-side experiments CLOSED WITHOUT PROMOTION; candidate-identity challenger OPEN | Color information retained; incremental identity benefit NOT ESTABLISHED; R2 entry unmet | [Paired-scale result](../60-evidence/s11/s11-o2-w4-paired-scale-windows-run-001.md), [color-side assessment](../60-evidence/s11/s11-o2-color-side-local.md#added-information-assessment-and-measurement-disposition--2026-10-06) |
| O2 acceptance | OPEN; not satisfied | Independent development/calibration/holdout roles, fixed operating point and required Windows shadow acceptance remain unresolved | [O2 acceptance](../30-validation/s11-interface-observability-witness-validation.md#o2-shadow-acceptance) |
| W5 / O3 support and association | PROPOSED; entry pending O2 acceptance | Separate behavior plan, typed support/physical association controls and exact same-frame provenance | [O3 entry](../30-validation/s11-interface-observability-witness-validation.md#o3-behavior-entry) |
| W6 / O4 handoff and phase | PROPOSED; entry pending W5 | Separate handoff and phase changes with positive/negative controls; no time/polarity shortcut | [O4 architecture](../20-architecture/s11-interface-observability-witness-architecture.md#stage-o4--handoff-and-phase-behavior) |
| W7 / O5 field qualification | PENDING integrated behavior candidate | Exact runtime, canonical segments, accuracy/coverage/resources; local or shadow PASS cannot substitute | [Field qualification](../30-validation/s11-interface-observability-witness-validation.md#field-qualification) |

W4-R0–R5 are internal W4 continuation steps, not another milestone:

- R0 correction is COMPLETE on transferred evidence; the old statistic's origin remains unresolved.
- R1 appearance-to-identity proposal is CLOSED WITHOUT PROMOTION; the censored comparison remains NOT_ASSESSABLE.
- R2 entry is unmet; color-side measurement does not establish identity gain.
- R3 saved-material inventory is COMPLETE on transferred evidence; no additional linked human-reviewed physical control was recovered. Do not repeat inventory.
- R4 (reuse W3 to evaluate outputs/abstention) and R5 (O2 acceptance or hypothesis closure) remain conditional, not newly authorized execution by their presence in the [dated W4 audit](../50-diagnostics/s11/s11-w4-progress-audit-and-continuation-plan-2026-10-01-ba1bd6a.md).

The [joint-context disposition](../60-evidence/s11/s11-o2-joint-context-windows-run-001.md#w4-r0-correction-received-and-w4-r1-disposition--2026-10-02)
and [R3 inventory](../60-evidence/s11/s11-o2-w4-r3-existing-evidence-feasibility.md)
own their detailed returns. Human idx0/idx20 ambiguity, formal labels and prior
scores remain pinned. This is not a general impossibility finding for spatial classifiers.

## Next transition

Review the already-saved complete main/auxiliary/unresolved comparisons
(480/144/480 rows) across X and BW before choosing a continuation or closing the
region hypothesis. The [region return and reconciliation](../60-evidence/s11/s11-o2-color-side-local.md#transfer-reconciliation-closed--user-confirmation)
closes both transfer items: the source/receipt code hash matches its pin, and the
missing ribbon row is 1536 train pixels, 504 test pixels and heldout MSE
0.006130124755688663. Do not request those confirmations again or rerun the model.
Execution/receipts/input preservation are reported COMPLETE, not independently
rehashed here. Full comparison CSV contents have not been received locally.

At the prescribed Accum slice, partition improves on smooth much more for idx10
than idx15, already in gray. The auxiliary slice favors a ribbon explanation;
the unresolved idx20 changes model ordering with support. These are bounded
appearance observations, not whole-candidate identity. Partition has the lowest
error for both main candidates in all four excerpt views, so ordering alone
does not distinguish them. Do not request
another descriptor run, fit new widths/cutoffs, or treat lower MSE as identity.
No full-CSV stability or incremental color benefit is established from excerpts.

W4-R1 remains closed, R2 entry unmet, O2 open and W5/O3 gated. Existing labels,
idx0/idx20 human ambiguity, original outputs and FIELD FAIL remain unchanged.

## Accepted local candidate

- **Behavior:** locally accepted R22 Oil ownership/evidence replacement; candidate generation and Foam are preserved. [Architecture](../20-architecture/s11-r22-oil-ownership-evidence-replacement-architecture.md), [validation](../30-validation/s11-r22-oil-ownership-evidence-replacement-validation.md), [local evidence](../60-evidence/s11/s11-r22-ownership-evidence-replacement.md).
- **Current diagnostic runtime:** `opencv-phase-detector-r22-3-interface-witness-diagnostics-v1` (O1 trace-only extraction).
- **Completed-window resolver:** `r22-oil-ownership-evidence-replacement-v1`; unchanged by diagnostics.
- **Comparisons:** R21 is the protected behavioral predecessor; R22-2 native-path diagnostics is the protected diagnostic baseline, retaining R22-1 measurements. No R23 behavior was promoted.

R22 local evidence owns canonical/Qt/replay/performance measurements, protected
truth and complete tracking fingerprints. These do not establish field repair.
O1 trace growth is approximately fourfold; captures must remain bounded.
Existing R22-3 bundles and v1 labels remain usable; no R22-4 or detector rerun is
required for the current measurement.

## Current authorization boundary

The user authorized replacement of the Oil temporal identity and phase/evidence
core, relevant tests/diagnostics, measured comparison and replaced-path cleanup
on 2026-09-09. Main owns implementation and final review; the subsequent request
for no further sub-agent work remains in force.

R22-1 authorized measurement with unchanged R22 decisions. The 2026-09-16 R22-2
and 2026-09-17 behavioral requests included implementation, verification, commit
and push for those scopes. The R23 polarity prototype failed protected observations
and was removed; its rejection is not a reason to request the same authorization
again. These historical grants do not authorize unrelated changes or publication.
The fixed color-side measurement is complete. The current user request authorizes
implementation and preparation up to the Windows execution point. The user has returned that Windows
saved-output run. Current follow-up is cross-X/BW interpretation of existing results; no automatic private rerun or broader field qualification
is authorized.

Outside the detector replacement scope remain unrelated candidate-generation,
Foam or UI changes; unbounded retention/recovery; relaxed truth/safety criteria;
silent golden regeneration; automatic private-media replay; private video/Glass/
time/coordinate branches; interpolation/carry/report repair; and speculative
Accum behavior without reviewed physical identity and two-sided controls.
No new descriptor or universal sign/threshold rule follows merely from old results.
Choose a new mechanism only with a distinct observable and justified controls.

## Preserved contracts

- One generic detector serves every Glass; reviewed coordinates and private identity never control production.
- Numeric Oil/Foam values are selected same-frame candidates with exact provenance.
- Oil and Foam validity/ownership remain independent through their defined composition point.
- FULL/EMPTY context never fabricates coordinates; physical IDs are not copied across rapid-refill handoff.
- Ambiguous, unavailable, lost or hard-invalid evidence fails closed without downstream repair.
- Candidate identity, path localization and scalar eligibility have separate truth and acceptance; partial truth cannot be rewritten to fit pooling.
- Known checkpoints remain regression, not untouched holdout; missing support, unknown winners and model abstention are distinct from truth uncertainty.
- New-run hashes do not prove old-run immutability; nested gains are not independent successes.

## Open field risks and named unknowns

R22 is not field-qualified. Generic local Base controls do not establish the
cause or repair of private Windows failures. Accum initial entry, continuity,
layered/post-Foam ownership and drain re-entry remain field uncertainties.
Candidate identity, scalar truth, calibration and a real-image operating point
remain unresolved; reuse W3 evaluation without interpreting its implementation
as classifier efficacy. Failed descriptors do not prove physical unobservability.

Sample4's current `e447626b...` replay differs from historical `0f202947...`.
The detached `d50c143` comparison reproduces the current result with unchanged
media identity; the historical Python/OpenCV/decoder environment remains unknown.
The golden stays unchanged; [runtime provenance](../50-diagnostics/s11/s11-r21-replay-runtime-provenance-diagnostic.md)
owns the details. The canonical source companion's fingerprint also remains
pending despite an O2 bundle-link source hash; reconcile full identity/operator
provenance without invalidating linked labels or demanding another detector run.

SPL#2/#3 are deferred until SPL#1 improvement, not current inputs or assigned
holdout. Scene expansion requires a named gap, without preference for post-780 s.
Partition changes are deferred unless a concrete experiment requires them.
Windows reports are attributed evidence; private inputs were not read locally.

## Active follow-up design

The [physical-interface proposal](../20-architecture/s11-physical-interface-evidence-repair-design.md)
and [witness architecture](../20-architecture/s11-interface-observability-witness-architecture.md)
own bounded observation redesign; [witness validation](../30-validation/s11-interface-observability-witness-validation.md)
owns acceptance. Independent support/association, committed fill handoff and
initial-FULL direction-neutral observation remain separate later behavior gates.
Controlled acquisition/structured-background options may be evaluated where
fixture access permits. A whole-detector rewrite or scalar threshold tuning is
not authorized by the [direction assessment](../50-diagnostics/s11/s11-transparent-interface-detector-direction-assessment.md).

Fixed-score, locality, profile, structure-context, row-profile and paired-scale
investigations are closed at their recorded scopes without promotion. Their
original outputs and corrections remain in [completed evidence](../60-evidence/README.md).
Do not reopen them or the completed W2 geometry handoff because old prose says pending.
The [recall index](recall-index.md) routes targeted causal review.

## Current authority links

- [Roadmap](roadmap.md), [execution policy](execution-policy.md), [retained commitments](retained-commitments.md)
- [Detector-change Skill](../../.agents/skills/s11-detector-change/SKILL.md), [governance](../30-validation/s11-detector-change-governance.md)
- [Current logic map](../20-architecture/s11-current-detector-logic-map.md), [failure registry](../50-diagnostics/s11/s11-detector-mechanism-failure-registry.md)
- [Canonical Windows reviewed truth](../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md), [field procedure](../40-operations/s11-current-windows-field-qualification.md)

Update this document when the current state or next transition changes; replace
resolved prose with its evidence link. Milestone changes belong in the roadmap.
