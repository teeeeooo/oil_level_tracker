# S11-D2 Sample3 Positive-Evidence Recovery

## Authority and status

S11-D2 is the next S11 source slice after accepted S11-D1. It owns the two reproducible
sample3 current-frame Oil failures separated by S11-C: a visually aligned candidate that
remains non-identifiable, and a visually clear boundary that never becomes a material candidate.

**Status:** `PLANNED — documentation gate complete; source-owner inspection and repair next`

**Starting repository identity:** `main @ 7d1e7e4d7effec2b1bb58f8d458b459d72af7eab`

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

After accepted D2 repair, rerun the local production replay and reassess residual sample3/sample4/field gaps.
Do not declare S11 complete until the resulting detector baseline is revalidated on the controlled Windows field
workflow. Initial-state retrospective reconstruction and S12 remain separate successor decisions.
