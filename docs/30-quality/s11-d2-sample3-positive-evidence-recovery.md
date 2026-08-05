# S11-D2 Sample3 Positive-Evidence Recovery

## Authority and status

S11-D2 is the next S11 source slice after accepted S11-D1. It owns the two reproducible
sample3 current-frame Oil failures separated by S11-C: a visually aligned candidate that
remains non-identifiable, and a visually clear boundary that never becomes a material candidate.

**Status:** `WORKER REPAIRED — Class A recovery plus Foam-front constraint; Class B owner split; fresh exact-head re-audit pending`

**Worker starting repository identity:** `main @ 61de9ef9336bfe200c8a70a692b7ebd749b8565d`

D1 Foam/Oil context safety, P2/FULL-EMPTY preservation, accepted Spatial behavior, the S5-B
observability contract and local-corpus identity rules remain authoritative.

## Evidence that opens S11-D2

S11-D1 exact-head replay preserved sample3 behavior exactly, so the S11-C sample3 findings remain
current after the Foam/Oil routing repair. The ignored S11-C forensic bundle is still available at:

`sample/output/s11-c-full-video-forensics/s11c-20260805T161456/`

with recorded fingerprint:
`9dc96fc04f9dcb1e00f5c120650ce6953e26239a0ecb61278cd6287b40519370`.
### Class A — candidate present but non-identifiable

Production sample3 frame `899` (`29.9966 s`) corresponds to the frozen usable visual annotation
at frame `900` (`30.03 s`), Oil range `310–322 px`, Foam absent, partial-state hint.

Current production contains a candidate at source Y=`321`, directly inside that visual range, but publishes
no Oil. Its representative evidence is boundary `0.240656`, ambiguity `0.580872`, artifact `0.317561`,
broad strength `0.082992`, horizontal coverage `0.058824`, narrow peak `0.991976`, broad-scale consistency
`0.918704`, visibility/availability `1.0`. The canonical outcome remains ambiguous with tracker `NO_UPDATE`.

This is not a proposal-absence defect. D2 must identify which genuinely observable positive evidence is
missing or underrepresented before changing candidacy/identifiability semantics.

### Class B — visible boundary not represented by a material candidate

Production sample3 frame `2697` (`89.9899 s`) corresponds to the frozen usable visual annotation at
frame `2700` (`90.09 s`), Oil range `326–344 px`, Foam absent, partial-state hint.

Current material candidates are centered at source Y approximately `206`, `252`, `287`, `294`, `302`
and `399`; none represents the visual Oil range. Production remains ambiguous with tracker `NO_UPDATE`.

This is not repairable by lowering an acceptance threshold. D2 must inspect proposal/observation construction
and determine why the broad drain-phase transition is not represented.
## Objective

Recover reproducible sample3 Oil boundaries through new or corrected **current-frame positive evidence**
inside the authoritative S5-B path, while preserving its fail-closed observational-equivalence contract.

D2 does not assume Class A and Class B share one implementation defect. The Worker must inspect the actual
proposal, semantic-likelihood, candidacy, identifiability and Spatial owners. If both classes belong to one
bounded S5-B responsibility, one repair may cover both. If evidence proves materially distinct owners or
independently releasable semantics, preserve the same evidence and report the required split/escalation.

The selected mechanism must explain why the recovered boundary is distinguishable from glare, rim,
structural lines, reflection and full-like/no-interface scenes. Numeric recovery itself is not sufficient.

## Worker implementation record — audit pending

### Owner attribution and split decision

The Worker inspected the active raw-observation, proposal, semantic-scoring, typed-current-observation,
Spatial-fallback, Phase-A validation and canonical projection/reducer owners directly. Repository-native
evidence was sufficient, so no external-reference review was needed and no new dependency was considered.

The two D2 classes do **not** share one safe repair mechanism:

- **Class A** already has a material relative-phase proposal and an independently coherent cross-ROI path.
  At exact frame `899`, the relative candidate is source Y=`320` with boundary likelihood about `0.362`,
  aggregate horizontal coverage about `0.014`, broad strength about `0.277`, texture relief about `0.966`
  and an accepted four-sector path `(119, 128, 124, 128)`. The defect is sequencing: Spatial path evidence
  was evaluated only after the scalar typed-current owner had already accepted a boundary, so Spatial could
  validate an accepted candidate but could not supply missing positive identifiability evidence.
- **Class B** has no corresponding safe candidate/path in the frozen `326–344 px` visual range. At exact
  frame `2697`, both the ordinary and relative proposal families remain dominated by other rows, with
  material source candidates `206, 252, 287, 294, 302, 399`. Direct target-range checks do not produce a
  coherent three-sector grayscale phase path. This is an observation/proposal-representation defect, not
  the Class-A sequencing defect, and is deliberately left outside this repair rather than recovered by a
  lower threshold or truth-guided candidate injection.

### Implemented Class-A mechanism

`oil_spatial_fallback.py` now has a secondary current-frame route only when the ordinary relative-phase
owner remains non-boundary. The route does not lower the ordinary boundary or ambiguity floors. It reuses
existing S5-B positive/safety evidence and requires all of the following before one Spatial path is tried:

- available no-interface evidence with likelihood at most `0.40`;
- boundary evidence greater than artifact evidence;
- all broad scales available, broad strength at least `0.12`, scale consistency at least `0.60`, broad
  polarity consistency at least `0.85`, and candidate polarity confidence at least `0.20`;
- narrow peak at least `0.25` with paired-edge strength at most `0.80`;
- visibility/evidence availability, glare/exclusion/border and static-prior safeguards retained from the
  existing low-contrast S5-B route;
- existing single-frame texture relief, phase-ceiling, collision-pressure and reliability safeguards;
- the existing five-sector phase path must accept, and D2 additionally requires at least four sectors,
  bounded span and candidate/path alignment.

The first semantic-order candidate that passes the non-Spatial safety gate owns the only path attempt. If
that path fails, D2 fails closed instead of searching lower-ranked alternatives. Therefore the added work is
bounded to one existing five-sector path evaluation in an already-ambiguous Spatial fallback frame; there
is no new temporal state, result/Recipe/truth schema, dependency or post-owner numeric reconstruction.

### PR #88 Foam-front audit repair

The first exact-head audit found that this secondary selector received the accepted Foam component mask but
not the accepted Foam-front coordinate. That allowed Spatial corroboration to promote an Oil hypothesis above
an authoritative accepted Foam front even though the existing Foam-aware S5-B selector requires Oil to lie
strictly below that front. The bounded repair now passes the same `accepted_foam_front_local_y` into the D2
selector and requires `candidate.representative_local_y > accepted_foam_front_local_y` whenever a front is
present. The D2 gate set, candidate ordering, Spatial path, Foam qualification and temporal owner are otherwise
unchanged. sample3:899-derived adversarial fronts at local Y `125`, `145`, `150` and `155` now remain ambiguous/
`NO_UPDATE`, while a front at `124` still permits the legitimate local-Y `125` D2 boundary at source Y `320`.
Repair-head `2 fps` replay of base, sample2 and sample3 reproduced the prior PR signatures exactly; sample4 was
not rerun because its prior `113/113` frames withheld Foam Oil-routing authority, so the new front-present guard
is unreachable there and the existing `Oil 0/113`, `Foam 113/113` evidence remains valid.

### Representative and replay evidence

Fresh exact-frame evaluation changes sample3 `899` from ambiguity/no numeric Oil to a current-frame canonical
boundary at source Y=`320`, inside the frozen `310–322 px` range. Frozen frame `900` similarly yields Y=`319`.
The accepted candidate remains below the ordinary scalar boundary/coverage floors, so the recovery is caused
by the additional four-sector current-frame phase evidence rather than a global threshold change.

The serialized stream owner remains authoritative. In the proportional `2 fps` four-video comparison, the
new current-frame evidence does **not** bypass reacquisition: sample3 raw Oil stays `42/281` before and after.
Five sample3 rows change only from `ambiguous` to `reacquisition_pending` (`899`, `914`, `3012`, `3057`,
`3132`), all with `NO_UPDATE`; no new stream-level numeric Oil publication is created. This is reported as
current-frame evidence recovery, not temporal/result recovery. The subsequent `914` current-frame boundary
is Y=`301`, too far from Y=`320` for the unchanged temporal owner to confirm the path safely.

The other replay signatures are unchanged: base `0/30` changed rows, sample2 `0/20`, and sample4 `0/113`.
Sample4 remains raw Oil `0/113`, raw Foam `113/113`, with Foam Oil-routing authority withheld `113/113`
for `wide_hollow_structural_or_refractive_component`. Sample2 user-confirmed Spatial anchors remain
`30 → 599` and `60 → 598`. The later sample3 changed rows do not publish numeric Oil; their
`reacquisition_pending` status is retained as explicit evidence for the Auditor rather than being promoted
through a temporal exception.

The S11-C forensic bundle remains unchanged and its hash list still verifies against fingerprint
`9dc96fc04f9dcb1e00f5c120650ce6953e26239a0ecb61278cd6287b40519370` (`207/207` files verified).

## Non-goals and prohibited shortcuts

S11-D2 does not authorize:

- a global Oil boundary/ambiguity threshold reduction;
- candidate injection from frozen/user truth or exact frame/video identifiers;
- temporal interpolation, future-frame lookahead or repetition-based promotion;
- reopening accepted D1 Foam/Oil context authority or S5-A Foam thresholds;
- forced sample4 numeric Oil recovery;
- blanket Spatial relaxation or removal;
- raw FULL/EMPTY appearance as positive Oil-boundary evidence;
- Recipe/result/truth/public schema or new dependency changes without separately proven necessity;
- initial-state retrospective FULL/EMPTY reconstruction or S12 UI/UX work.
## Acceptance boundary

A D2 production repair is acceptable only when exact-head evidence demonstrates all applicable points:

- Class A recovery, if implemented, is caused by genuinely stronger observable positive evidence rather
  than a lower global acceptance floor or route label;
- Class B recovery, if implemented, creates a candidate from defensible current-frame evidence rather
  than truth proximity or temporal reconstruction;
- user-confirmed sample2 Spatial recoveries `30 → 599` and `60 → 598` remain preserved;
- suspicious sample3 full-like/rim-associated Spatial publications are not strengthened merely to gain recall;
- accepted D1 sample4 Foam/Oil context safety remains intact, including no alternate structural numeric path;
- retained glare, structure, collision, P2 and genuine FULL/EMPTY no-interface protections remain fail-closed;
- only canonical S5-B outcomes may publish numeric Oil and the one serialized temporal owner remains unchanged;
- CPU/resource work remains bounded by current desktop-production architecture.

The Worker should use the smallest regression surface that proves the recovered evidence family and its
nearest confounders. Existing frozen visual annotations remain independent evidence and must not be changed
to fit production output.

## Validation and replay

The S11-C bundle may be reused for attribution but remains ignored temporary evidence, not a golden artifact.
After a source repair, local exact-frame/window checks must include the representative sample3 failure class(es)
and retained safety anchors. A proportional four-video production replay is expected before merge whenever the
changed owner can alter stream-level candidate/publication behavior beyond isolated frames.

Absence/wrong-identity/decode-failure behavior for local MP4s remains governed by the accepted portability
contract. Windows canonical and private field validation are later gates, not automatic Worker acceptance.

## Lane and next gate

S11-D2 starts as a **provisional Lane C — Independent Review candidate** because current evidence may require
changing S5-B proposal construction, candidacy/identifiability semantics or the accepted Spatial positive-evidence
boundary. Bounded owner inspection may establish a narrower existing-owner defect, but the Worker must not
self-downgrade audit authority after source mutation.

The current Worker next gate is a fresh independent **S11-D2 exact-head Auditor**. If that gate accepts
this bounded Class-A repair, the remaining Class-B observation/proposal representation defect must be
reassessed as its own source decision rather than being silently folded into this PR. Do not declare S11
complete until the resulting detector baseline is revalidated on the controlled Windows field workflow.
Initial-state retrospective reconstruction and S12 remain separate successor decisions.
