# S11-D2 Class-B Observation/Proposal Representation Recovery

## Authority and status

This document owns the next S11 source gate after accepted PR #88 Class-A recovery.
It addresses the remaining sample3 defect where a visually usable Oil boundary is not represented
by any material current-frame S5-B candidate.

**Status:** `IMPLEMENTED — Worker exact-head handoff pending fresh independent audit`

**Worker base identity:** `main @ 97c13d676b27163836da985b4b2505bb0afa402a`

Accepted S11-D1 Foam/Oil context safety and S11-D2 Class-A Spatial corroboration remain authoritative.
The repair must preserve the canonical S5-B observability contract and one serialized temporal owner.

## Evidence that opens this gate

Production sample3 frame `2697` (`89.9899 s`) corresponds to frozen usable visual frame `2700`
(`90.09 s`), Oil range `326–344 px`, Foam absent, partial-state hint.

Pre-repair material candidate Y values were approximately:

`206, 252, 287, 294, 302, 399`

No material candidate represented the frozen Oil range. The pre-repair outcome was ambiguous / `NO_UPDATE`.
This survived accepted D1 and D2 Class-A changes and therefore opened a distinct representation defect.
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

## Worker implementation evidence

The exact loss point was raw Sobel observation emission, not preprocessing, total raw retention,
or proposal capacity at sample3 frame `2697`. The `326–344 px` visual range contains valid Sobel
local maxima at source `327`, `335` and `343 px`, but global top-strength Sobel retention omitted them.

The repair adds at most one internal `sobel_distributed` observation from an observable current-frame
ridge: at least three already-valid Sobel local maxima above the unchanged `0.08` floor, spread across
`20–30 px`, outside the neighborhoods of the ordinary strongest Sobel rows. Ordinary raw observations
and ordinary proposals retain first ownership of their existing resource budgets. The supplemental
observation is added only when raw/proposal capacity remains and never enters D2 Spatial base evidence.

At production frame `2697`, raw observations change `12 → 13` and proposals `6 → 7` with a new
source-Y `327 px` observation (`21 px` span, response `0.187762`) and proposal/hypothesis. The existing
`302 px` competing hypothesis remains material. The `327 px` hypothesis remains ambiguous
(boundary `0.185473`, artifact `0.152396`, ambiguity `0.464123`), so current-frame publication stays
ambiguous / `NO_UPDATE`; no later temporal or canonical owner is weakened.

Literal frame `2700` remains a separate residual observation: it still has no `326–344 px` raw/proposal;
the bounded supplemental representation appears at `386 px` and remains ambiguous. The accepted defect
and regression authority for this gate remain production frame `2697`, which corresponds to the frozen
usable visual reference at `90.09 s`.

The final four-video 2 FPS production replay preserves publication signatures exactly: base `2/30`,
sample2 `4/20`, sample3 `42/281`, and sample4 Oil `0/113` with Foam `113/113`. Proposal/candidate
signatures change only as supplemental representation: base `22/22`, sample2 `2/1`, sample3 `170/149`,
sample4 `3/3`; publication changes are `0` for every video. Maximum raw observations rise by at most
one per frame (`36→37`, `36→37`, `30→31`, `34→35`), while maximum proposals remain bounded at
`10`, `12`, `12`, `10` respectively. The instrumented replay wall time changed by about `+4.1%` in
aggregate; this is proportional diagnostic evidence, not a field-performance certification.

## Next gate

Worker Build owns source, tests, source-completing documentation and one focused Draft PR.
Fresh independent exact-head Auditor owns the final Lane C Gate and guarded merge/Close after PASS.

If accepted, rerun/retain the four-video production baseline and then decide whether remaining S11 work is
sample4 independent Oil representation, temporal continuity, or controlled Windows field revalidation.
Do not preselect those successors before the Class-B exact-head evidence is known.