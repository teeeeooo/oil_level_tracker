# Current Work Plan

**Current milestone:** `S11 — Real-Field Detector Effectiveness Recovery`
**Milestone status:** `ACTIVE`
**Current gate:** R22 Oil ownership/evidence replacement is locally accepted; target-Windows accuracy and throughput qualification is next
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

## Current authorization boundary

On 2026-09-09 the user authorized replacement of the Oil temporal identity and
phase/evidence core, relevant tests and diagnostics, measured performance
comparison, and cleanup of replaced execution paths. Main owns design and final
acceptance. The user subsequently requested no further sub-agent work; Main
now completes implementation, cleanup, verification and review directly.
This supersedes the prior pause on another detector revision for this bounded
replacement. R21 local acceptance is historical baseline evidence, not evidence
that its transferred Windows failures are fixed.

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

Retained but non-current work is owned by [`retained-commitments.md`](retained-commitments.md).

## Next transition

The authorized core replacement, cleanup and local verification are complete.
Next, qualify R22 accuracy and throughput on target Windows with the existing
reviewed evidence. Preserve FIELD FAIL until that acceptance owner is satisfied.
Candidate-generation recall and the dominant reader/detect performance costs
remain separate measured follow-ups; local controls and macOS timings do not
establish Windows success.

## Current authority links

- [Project roadmap](roadmap.md)
- [Repository execution policy](execution-policy.md)
- [S11 detector-change Skill](../../.agents/skills/s11-detector-change/SKILL.md) and [mechanical governance contract](../30-validation/s11-detector-change-governance.md)
- [Current detector logic map](../20-architecture/s11-current-detector-logic-map.md)
- [R22 architecture](../20-architecture/s11-r22-oil-ownership-evidence-replacement-architecture.md)
- [R22 validation](../30-validation/s11-r22-oil-ownership-evidence-replacement-validation.md)
- [R22 local evidence](../60-evidence/s11/s11-r22-ownership-evidence-replacement.md)
- [Detector mechanism failure registry](../50-diagnostics/s11/s11-detector-mechanism-failure-registry.md)
- [Canonical Windows reviewed truth](../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md)
- [Current-candidate Windows field procedure](../40-operations/s11-current-windows-field-qualification.md)
