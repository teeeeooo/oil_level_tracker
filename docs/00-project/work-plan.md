# Current Work Plan

**Current milestone:** `S11 — Real-Field Detector Effectiveness Recovery`
**Milestone status:** `ACTIVE`
**Current gate:** O1 accepted locally; O2 label/freeze/evaluation tooling implemented; human label collection and shadow discrimination remain open
**Field disposition:** latest user-reported Windows result remains `FIELD FAIL`; no field-qualified detector is claimed

This document owns only the current engineering state and next transition. Revision-by-revision history belongs in diagnostics, evidence, historical architecture/validation records, and Git history.

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
Next prepare/link one existing regression frame, then complete human questions,
record replies and check status on the work PC. After that, declare separate original
recordings for development/calibration/holdout before choosing a shadow model.
Reviewed private checkpoints are regression cases, not untouched holdout.
Windows work next verifies the new witness on existing reviewed frames and
builds labels locally; no private export or immediate behavioral rerun is
required. A real-image shadow classifier and its operating point remain unbuilt.
Do not add further descriptors without a named discrimination hypothesis.

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
