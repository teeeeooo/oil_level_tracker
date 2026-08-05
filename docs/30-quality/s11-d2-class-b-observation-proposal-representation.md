# S11-D2 Class-B Observation/Proposal Representation Recovery

## Authority and status

This document owns the next S11 source gate after accepted PR #88 Class-A recovery.
It addresses the remaining sample3 defect where a visually usable Oil boundary is not represented
by any material current-frame S5-B candidate.

**Status:** `PLANNED — documentation gate complete; bounded owner repair next`

**Starting repository identity:** `main @ aaeb0119524faf6d10218af3442ab05d733af8de`

Accepted S11-D1 Foam/Oil context safety and S11-D2 Class-A Spatial corroboration remain authoritative.
The repair must preserve the canonical S5-B observability contract and one serialized temporal owner.

## Evidence that opens this gate

Production sample3 frame `2697` (`89.9899 s`) corresponds to frozen usable visual frame `2700`
(`90.09 s`), Oil range `326–344 px`, Foam absent, partial-state hint.

Current material candidate Y values remain approximately:

`206, 252, 287, 294, 302, 399`

No material candidate represents the frozen Oil range. The current outcome is ambiguous / `NO_UPDATE`.
This survived accepted D1 and D2 Class-A changes and therefore remains a distinct representation defect.
## Current owner boundary

Direct owner inspection places the defect in the shared current-frame representation path:

`extract_raw_observations → build_bounded_proposals → semantic hypotheses`

The raw observation families include Sobel, Canny, Hough and broad REGION_STEP evidence.
Bounded grouping and retained-member/proposal limits then decide which row evidence becomes a material proposal.
The same representation feeds ordinary S5-B and materially adjacent Spatial recovery paths.

This gate therefore remains **Lane C — Independent Review**. It changes shared Oil observability input
representation rather than one isolated presentation/helper behavior.

## Objective

Recover a defensible current-frame representation for the broad sample3 drain-phase transition without
weakening candidacy, identifiability, Foam, Spatial, no-interface or temporal safety contracts.

The Worker must establish where the `326–344 px` evidence is lost: preprocessing/profile formation,
raw-observation retention/ordering, bounded grouping, or another current representation step.
The implementation must add or correct observable evidence, not inject truth proximity.

A successful repair should make the true transition representable before asking later acceptance owners
to judge it. It does not require that every newly represented frame become an immediate stream-level numeric Oil.
## Non-goals and prohibited shortcuts

This gate does not authorize:

- global Oil acceptance/ambiguity threshold lowering;
- truth/frame/video-specific candidate injection;
- temporal interpolation, lookahead or relaxed reacquisition;
- reopening D1 Foam/Oil context authority;
- changing accepted D2 Class-A Spatial corroboration semantics;
- blanket Spatial relaxation;
- forced sample4 numeric Oil recovery;
- initial-state retrospective FULL/EMPTY reconstruction;
- public/result/truth schema or new dependency changes without separately proven necessity;
- S12 UI/UX work.

## Acceptance boundary

Exact-head evidence must show that any recovered `326–344 px` representation is caused by defensible
current-frame observable evidence and remains distinguishable from nearby structural/rim/glare alternatives.

The repair must preserve:

- accepted D2 Class-A current-frame behavior and Foam-front constraint;
- sample2 Spatial anchors `30 → 599`, `60 → 598`;
- D1 sample4 fail-closed Oil `0/113` / Foam `113/113` safety;
- glare/structure/collision and P2/FULL-EMPTY protections;
- canonical-only numeric publication and one serialized temporal owner;
- bounded raw-observation/proposal/resource ownership.
## Validation and replay

The Worker should use exact frame/window evidence around sample3 `2697/2700` and nearest confounders,
then one relevant targeted suite after stabilization. If representation changes affect stream-level proposal
or publication signatures beyond the isolated class, perform a proportional four-video 2 FPS production replay.

The ignored S11-C forensic bundle may be reused for attribution and remains temporary non-Git evidence:

`sample/output/s11-c-full-video-forensics/s11c-20260805T161456/`

fingerprint:
`9dc96fc04f9dcb1e00f5c120650ce6953e26239a0ecb61278cd6287b40519370`

Local-corpus identity, missing/decode-failure and no-partial-aggregate rules remain authoritative.
Full canonical and Windows/private-field validation are later gates, not automatic Worker acceptance.

## Next gate

Worker Build owns source, tests, source-completing documentation and one focused Draft PR.
Fresh independent exact-head Auditor owns the final Lane C Gate and guarded merge/Close after PASS.

If accepted, rerun/retain the four-video production baseline and then decide whether remaining S11 work is
sample4 independent Oil representation, temporal continuity, or controlled Windows field revalidation.
Do not preselect those successors before the Class-B exact-head evidence is known.