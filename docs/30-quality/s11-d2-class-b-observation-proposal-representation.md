# S11-D2 Class-B Observation/Proposal Representation Recovery

## Authority and status

This document records the accepted S11-D2 Class-B source gate that followed PR #88 Class-A recovery.
It closes the sample3 representation defect where a visually usable Oil boundary was not represented
by any material current-frame S5-B candidate.

**Status:** `ACCEPTED — repaired semantic ownership passed fresh Lane C re-audit; PR #89 guarded-squash-merged`

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

The repaired four-video 2 FPS production replay preserves publication signatures exactly: base `2/30`,
sample2 `4/20`, sample3 `42/281`, and sample4 Oil `0/113` with Foam `113/113`. Proposal/candidate
signatures change only as supplemental representation: base `22/22`, sample2 `2/0`, sample3 `170/119`,
sample4 `3/3`. Ordinary-hypothesis removals, decision status/reason drift, tracker-action drift,
smoothing-action drift, serialized temporal-state/beam drift and publication drift are all `0` for every
video. Maximum raw observations rise by at most one per frame (`36→37`, `36→37`, `30→31`, `34→35`),
while maximum proposals remain bounded at `10`, `12`, `12`, `10` respectively. The instrumented replay
wall time changed by about `+1.0%` in aggregate; this is proportional diagnostic evidence, not a
field-performance certification.

## Audit repair — semantic capacity ownership

Fresh exact-head review accepted the observable `SOBEL_DISTRIBUTED` mechanism but found that the first
implementation combined ordinary and supplemental semantic hypotheses before the hard
`semantic_hypotheses=10` truncation. A high-scoring supplemental hypothesis could therefore evict an
ordinary hypothesis even though raw/proposal admission already gave ordinary evidence first ownership.

The bounded repair preserves the existing ordinary grouping, compatibility, merge identity and
`_hypothesis_order` behavior, applies the semantic cap to those ordinary hypotheses first, and admits
supplemental hypotheses only from capacity that remains. Supplemental evidence that would merge with an
ordinary semantic group is not allowed to rewrite that ordinary group. The ordinary current-observation
three-hypothesis decision prefix is also retained before supplemental admission; supplemental evidence may
enter the remaining semantic capacity only when it sorts after that prefix. This keeps the Class-B `327 px`
hypothesis material at frame `2697` as the fourth ordered hypothesis while preventing additive representation
from perturbing the serialized temporal beam.

The Auditor's six saturated replacements reproduce on the failing head and are absent after repair:

- sample2 `270`: ordinary `335` was replaced by distributed `476`; repaired full semantics retain `335`;
- sample3 `270`: ordinary `257` was replaced by distributed `340`; repaired semantics retain `257`;
- sample3 `345`: ordinary `260` was replaced by distributed `269`; repaired semantics retain `260`;
- sample3 `360`: ordinary `235` was replaced by distributed `268`; repaired semantics retain `235`;
- sample3 `974`: ordinary `232` was replaced by distributed `242`; repaired semantics retain `232`;
- sample3 `1049`: ordinary `295` was replaced by distributed `306`; repaired semantics retain `295`.

A deterministic saturated-cap regression fixes this ordinary-first contract, and a decision-prefix regression
proves that an intrusive supplemental hypothesis cannot reorder the ordinary decision-facing prefix while a
trailing supplemental hypothesis may still consume genuinely unused semantic capacity.

## Accepted audit, merge and next gate

PR #89 passed fresh **Lane C — Independent Review re-audit** at exact base
`97c13d676b27163836da985b4b2505bb0afa402a` / repaired exact head
`993d78bfcfde7c404a8f9d7cfabe734ac2b298f0` and was native guarded-squash-merged as
`9ba7dba31e11e4039500e4b12d73ee6f85cfc43a`.

Auditor-focused exact-head validation returned `63 passed` on the observation/evidence/temporal/D2 surface
plus `64 passed` on retained no-interface/serialized-owner/cutover/fill safety. The six prior saturated
replacement rows changed from ordinary removals on the failed head to `removed=[] / added=[]` on the repaired
head. A complete 444-row four-video base comparison found zero drift in publication, fill state, decision
status/reason, tracker/smoothing actions, projected Y or serialized temporal state/beam; all `144` semantic
candidate-set changes were additive and ordinary removals were `0`. Frame `2697` retains the material `327 px`
Class-B representation as the fourth ordered hypothesis while remaining ambiguous / `NO_UPDATE`.

The next gate is a **read-only Orchestrator post-D2 successor decision** using this accepted evidence. It must
choose among remaining S11 work without automatically starting temporal relaxation, sample4 independent Oil
recovery, Windows/private-field validation or S12. S11 completion and detector/general-field accuracy PASS are
not implied.