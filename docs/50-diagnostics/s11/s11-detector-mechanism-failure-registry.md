# S11 Detector Mechanism Failure Registry

**Status:** durable causal registry; supporting diagnostics, not current gate authority

**Scope:** S11 detector and its observation/projection boundary, from the R1 report/observation repair through the R19 bounded drain-release-chain implementation. This registry groups failures by mechanism, not by revision chronology. Version names identify the attempts that exposed or tested a mechanism; they do not define current runtime behavior. R19 is implementation-current locally but remains field-unqualified pending canonical Windows replay.

## How to read this registry

The labels below deliberately separate evidence strength:

- **Confirmed fact** means directly observed in code, a checked-in replay, a validation assertion, or an operator-transferred field result whose boundary is explicitly stated.
- **Strong inference** means the mechanism is the best explanation supported by multiple observations or by a structural counterfactual, but the decisive counterfactual was not run.
- **Named unknown** means the source record explicitly does not contain the measurement needed to choose between competing explanations. Unknown is not a negative result.

Private Windows bundles cannot be reproduced from this checkout. Their counts and visual classifications are retained as field evidence with that limitation; they never authorize a video-, Glass-, timestamp- or coordinate-specific production rule.

**R18 field update:** The completed operator-transferred causal audit is frozen in [the R18 Windows causal closure](s11-r18-windows-causal-closure.md). Base stayed in `INITIAL_FULL_BARRIER` with zero rapid-refill Oil; lower `Y > 800` entrance rejection is correct safety behavior, while the actual interface's earliest harmful stage is before-or-at `OIL-PHASE-DRAIN` and remains unknown. Accum DRAIN produced 264 release-evaluation rows and zero passed; retained owner `000388:0265` remained a non-updated established snapshot, while its non-update cause and actual drain candidate identity/direction remain unknown. The owner-bounded selector abstain predicate is also unknown. Foam exact eligibility/formation gates are closed, with seven known false ENTRY-SPLASH paths. Compared selected-candidate, completed-sequence and CSV fields were invariant on `1,202/1,202` common rows with zero mismatches. R19 bounded drain-release-chain behavior is implemented and focused-tested locally, but remains field-unqualified; Foam is intentionally outside R19.

## Quick failure index (F01–F10)

Read this index completely before opening detailed entries. Each ID is repeated verbatim in its detailed heading, so use the ID/title with in-page search to navigate. The index is a routing aid, not a replacement for the full entry when its nodes or mechanism are relevant.

| ID / title | Short symptom / mechanism | No-repeat constraint | Current risk / status | Affected semantic logic-map nodes |
|---|---|---|---|---|
| `S11-F01` — Pre-selection authority collapse | Early winner, tracker bit, or Foam mask becomes final Oil authority. | Retain alternatives through one typed Oil owner, then compose Foam once. | Partially retired structurally; live regression class. | `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-SELECTOR`, `FOAM-CANDIDATE`, `SEQUENCE-COMPOSITION` |
| `S11-F02` — Proposal/representation recall starvation | True interface is absent or pruned before typed authority. | Measure proposal/evidence/top-k loss separately; downstream owners cannot recover it. | Open field risk; the completed R18 rerun preserves candidates/tracklets but exact reviewed-interface identity and Y anchors remain unknown. | `FRAME-EVIDENCE`, `OIL-RAW-EVIDENCE`, `OIL-PROPOSAL`, `OIL-HYPOTHESIS`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET` |
| `S11-F03` — Motion/bootstrap authority overreach | Smooth, motion, or calibrated path is promoted without same-frame identity. | Motion is only a bounded witness inside an established physical owner. | Accepted path retired; active regression guard. | `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-SELECTOR` |
| `S11-F04` — Component identity leakage and alias continuation | Y-adjacency, residue, source family, or stale alias merges components or blocks valid continuation. | Require explicit physical handoff; geometry or recurring Y never proves identity. | Open field risk; locally guarded; owner-bounded selector abstain and exact reviewed-interface identity remain unknown after the completed R18 audit. | `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `FOAM-IDENTITY` |
| `S11-F05` — Initial-state and material-phase hard-lock asymmetry | EMPTY/FULL gates lock real owners, fail to close, or admit unsafe rows. | Transitions need evidence-backed phase ownership; state never fabricates a coordinate. | Active, highest-risk recurrence; causal rerun is complete. Base actual interface first loss and Accum partial-release identity/direction remain unknown; R19 is implemented and focused-tested locally, with field validation pending. | `OIL-HYPOTHESIS`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR` |
| `S11-F06` — Foam/Oil/material evidence cross-coupling | Material or Oil evidence masks Oil, vetoes Foam, or changes the other series’ authority. | Keep owners independent; only final same-frame Oil may enter bounded alias comparison. | Open field risk; completed rerun closes exact Foam gates and preserves compared-field invariance, while layered Oil identity/Y remains unknown. Foam is intentionally outside R19. | `FRAME-EVIDENCE`, `OIL-HYPOTHESIS`, `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-SELECTOR`, `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `FOAM-EPISODE`, `SEQUENCE-COMPOSITION` |
| `S11-F07` — Foam episode false dynamics and stale episode identity | Static glare/residue or one motion spike becomes an episode; stale identity persists. | Require bounded formation or stable-layer witness; no brightness/extent-only acceptance. | Active; exact gates are closed by the completed rerun and seven false ENTRY-SPLASH paths are known. Foam remains outside approved R19 scope. | `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `FOAM-EPISODE`, `SEQUENCE-COMPOSITION` |
| `S11-F08` — Lifecycle closure and owner-loss dead ends | FILLING/partial fill cannot close or reverse safely after owner loss. | Confirm a physical owner before transition; no reopen, copy, or ambiguous release. | Active; completed rerun found 264 Accum DRAIN evaluation rows and zero passed, with retained non-updated snapshot; cause and drain candidate identity/direction remain unknown. R19 is implemented and focused-tested locally, with field validation pending. | `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR` |
| `S11-F09` — Coordinate, validity and provenance ambiguity | Current/final/ROI/source values or presentation artifacts are mistaken for observations. | Preserve exact same-frame provenance, independent validity, and no downstream repair. | Active cross-cutting guard; completed causal rerun proves compared-field invariance on `1,202/1,202` rows with zero mismatches; field effectiveness remains FAIL and Y anchors are unavailable. | `OIL-PROJECTION`, `PUBLICATION-PROVENANCE`, `CSV-PUBLICATION`, `TRACE-PUBLICATION`, `RESULT-PRESENTATION` |
| `S11-F10` — Global-threshold or case-specific escape hatch | Broad threshold, private branch, or interpolation hides missing evidence with apparent coverage. | Use generic bounded mechanisms and two-sided controls; no private identity or truth shortcut. | Permanent guard; R19 is implemented as a generic bounded chain with focused local tests, and still has no field proof. | All nodes; especially `FRAME-EVIDENCE`, `OIL-AUTHORITY`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `FOAM-CANDIDATE`, `FOAM-EPISODE` |

## Stable detector node IDs

The [current detector logic map](../../20-architecture/s11-current-detector-logic-map.md) is the authority for these semantic IDs and their implementation owners. They are the cross-reference surface for this registry, not a second proposed module decomposition. `RESULT-PRESENTATION` is reserved for the downstream presentation owner named by the map.

| Node ID | Registry meaning | Must not do |
|---|---|---|
| `FRAME-EVIDENCE` | source-frame acquisition, Glass ROI, preprocessing and optics/exclusion evidence | publish Oil, Foam or state |
| `OIL-RAW-EVIDENCE` | bounded raw Oil edge/phase observations | grant Oil authority |
| `OIL-PROPOSAL` | bounded Y proposals grouped from raw observations | become a published observation |
| `OIL-HYPOTHESIS` | semantic Oil/no-interface hypotheses and current observation | reuse a prior or future state as current image evidence |
| `OIL-CANDIDATE` | typed candidate rows and provenance/eligibility | imply physical identity or publication |
| `FOAM-CANDIDATE` | raw Foam front/material/topology/optics evidence | mask Oil or publish Foam by itself |
| `FOAM-IDENTITY` | observation-only material identity and bounded opposition | publish Foam/Oil/state or veto every lower row |
| `OIL-AUTHORITY` | typed Oil authority tiers and hard-invalid filtering | turn ranking, source family or current selection into identity |
| `OIL-TRACKLET` | bounded directed physical Oil IDs and confirmation | merge components on Y proximity or motion alone |
| `OIL-PHASE-INITIAL` | initial-state barrier and EMPTY/FULL admission | fabricate a coordinate or fail open |
| `OIL-PHASE-FILL` | filling ownership and bounded fill handoff | copy observations or widen initial EMPTY admission |
| `OIL-PHASE-DRAIN` | filled-barrier release, partial-fill reversal and drain ownership | release on ambiguous/reversed/distant evidence |
| `OIL-SELECTOR` | bounded fixed-lag Oil node selection | interpolate, carry or select non-publishable rows |
| `OIL-PROJECTION` | selected same-frame Oil projection | invent/carry/interpolate coordinates |
| `FOAM-EPISODE` | bounded physical Foam episode formation/confirmation | accept brightness, extent or one motion spike alone |
| `SEQUENCE-COMPOSITION` | one Oil/state then Foam composition point | run a second Oil pass or cross-veto independent series |
| `PUBLICATION-PROVENANCE` | final TrackingSample/events validity and provenance | repair detector output downstream |
| `CSV-PUBLICATION` | serialization of final samples/events to CSV | reread candidates or repair coordinates |
| `TRACE-PUBLICATION` | current/final trace annotations and audit evidence | become detector authority |
| `RESULT-PRESENTATION` | downstream graph/report explanation of observed results | invent numeric values or make display bridges samples |

## Failure registry

### S11-F01 — Pre-selection authority collapse

**Affected detector logic node(s):** `OIL-CANDIDATE`/`OIL-AUTHORITY` → `OIL-SELECTOR`; historically also `FOAM-CANDIDATE`/`SEQUENCE-COMPOSITION` when accepted Foam was evaluated before Oil.

**Mechanism/trigger:** The pipeline reduced many current-frame hypotheses to one semantic winner (or ambiguity) before bounded sequence reasoning. A current-frame tracker `selected` bit, shadow continuity, a first finite Foam candidate, or an accepted/pending Foam mask then became an implicit final anchor or Oil-routing authority. Repeated ties became UNKNOWN, while a consistently strong fixed artifact could re-enter as the only surviving candidate. In the R5 field head, current Foam could mask Oil before the supposedly independent sequence owner saw it.

**Intended benefit:** Preserve high-recall alternatives long enough for completed-window comparison of same-frame evidence, motion, persistence, static opposition and material identity; keep Foam/Oil resolution independent while retaining legitimate evidence.

**Observed field failure:** **Confirmed facts:** R5 published `594/601` Base and `600/601` Accum nominally valid rows, but Base was false glare/vertical reflection and Accum remained `EMPTY_NO_INTERFACE`; R4 had only `157/601` and `69/601` numeric rows. R6 field review found ambiguous shadows promoted to final Oil anchors, while many continuation candidates were censored. R7–R10 and R11 then demonstrated that candidate continuity, calibrated bootstrap or distinct-lower separation could still create false authority. **Strong inference:** the earliest reusable loss was ordering/authority, not merely threshold values; the R5 causal diagnostic identifies pre-selection reduction as the earliest architectural loss.

**Attempts/versions:** R2’s accepted-Foam Spatial challenger repaired one bounded incumbent seam; R3/R4 separated structural/static Foam publication from Oil context; R5 introduced sequence-first reasoning but retained current-frame and prior authority leaks; R6 removed some current-frame authority but over-censored; R7 typed tiers; R8–R10 added bootstrap/recovery; R11 reset the architecture; R12–R18 retain one final Oil owner, one Foam owner and one composition point.

**Evidence links:** [R2 authority diagnostic](s11-r2-foam-spatial-authority-diagnostic.md), [R3 root-cause diagnostic](s11-r3-sequence-observability-root-cause.md), [R4 residual diagnostic](s11-r4-windows-residual-authority-diagnostic.md), [R5 current-frame root cause](s11-r5-current-frame-authority-root-cause.md), [R6 field failure](s11-r6-secure-windows-field-failure.md), [detector responsibility architecture](../../20-architecture/s11-detector-responsibility-architecture.md).

**No-repeat rule:** A field, state, `selected`, current tracker, pending Foam, source-family or report value may not become final authority unless its typed contract explicitly proves same-frame evidence and the owning resolver accepts it. Retain alternatives through `OIL-SELECTOR`, resolve Oil once, resolve Foam independently, and compose once at `SEQUENCE-COMPOSITION`.

**Contracts to preserve:** fail-closed ambiguity; no numeric value without same-frame candidate provenance; independent Foam publication when Oil is unknown; no second Oil pass; exact sequence/CSV raw-Y equality.

**Replacement/lesson:** Authority is a typed one-way pipeline: proposals → bounded evidence tiers → physical identity → phase ownership → fixed-lag selection → same-frame projection. More coverage is not a repair when it is obtained by moving the authority seam earlier.

**Current relevance/status:** **Partially retired structurally; still a live regression class.** R12–R18 define the intended ownership, but the field gate remains open and any future resolver change can recreate the seam.

**Confidence:** Confirmed mechanism for historical heads; strong inference for R5’s earliest loss; high confidence that the current ownership contract is the correct prevention boundary.

### S11-F02 — Proposal/representation recall starvation

**Affected detector logic node(s):** `FRAME-EVIDENCE` → `OIL-RAW-EVIDENCE`/`OIL-PROPOSAL`/`OIL-HYPOTHESIS` → `OIL-CANDIDATE`/`OIL-AUTHORITY` (and the retained candidate beam feeding `OIL-TRACKLET`).

**Mechanism/trigger:** The physical interface is absent from the candidate lattice, or present only in a representation that lacks the typed material/phase/optics/coverage fields needed for anchor authority. Top-k pruning and fixed per-member motion requirements can then eliminate the true row before sequence selection. A resolver cannot recover evidence never generated or retained.

**Intended benefit:** Improve recall of slowly changing, low-contrast or distributed interfaces while keeping recovered candidates continuation-only until independent same-frame identity exists.

**Observed field failure:** **Confirmed facts:** R8 Base had no candidate within ±25 px at 539.998 s and 674.007 s; at 634.008 s the nearest was 22 px away but no anchor-backed run formed. R9’s complete funnel had 5,002 continuation candidates stop at `NO_TRAJECTORY_SUPPORT`; its six-frame path count was zero. R10/R11/R12 again reported no candidate near key Base points and actual lower Accum candidates pruned before final authority. R16 independently separated incomplete proposal recall from bounded confirmation failure: at 540 s no ±25 px proposal, at 674 s no ±80 px proposal, and at 684/689 s Accum reviewed-near rows were absent. **Named unknown:** private Base failure cannot be assigned wholly to proposal absence where the required candidate/state fields were not serialized.

**Attempts/versions:** R5 preserved candidate families but lost them in current-frame reduction; R6–R8 added evidence tiers, representation recovery and a calibrated lane; R9–R12 tested dynamic bootstrap and high-recall families; R13–R16 replaced broad authority with typed candidates/tracklets but deliberately left proposal recall as a separately measured input; R17 preserved the beam; R18 does not change candidate generation.

**Evidence links:** [R7 observation-recovery diagnostic](s11-r7-windows-observation-recovery-diagnostic.md), [R8 calibrated diagnostic](s11-r8-windows-calibrated-observation-diagnostic.md), [R9 calibrated diagnostic](s11-r9-windows-calibrated-observation-diagnostic.md), [R10 path/residue diagnostic](s11-r10-windows-path-and-residue-diagnostic.md), [R12 phase-authority diagnostic](s11-r12-windows-phase-authority-diagnostic.md), [R16 tracklet/foam diagnostic](s11-r16-windows-tracklet-and-foam-diagnostic.md), [R16 owner audit](s11-r16-local-coverage-owner-audit.md).

**No-repeat rule:** Never infer recall from coverage, candidate count or a path that is merely smooth. Report candidate-near truth checkpoints, top-k loss, representation availability and first reject stage separately. A new proposal lane must not consume ordinary capacity, become an anchor by motion alone, or alter the shared candidate beam without two-sided negative controls.

**Contracts to preserve:** no interpolation or carry; candidate-only evidence remains non-public; typed unavailable is not measured-clean; initial-EMPTY safety is not widened to fix recall; same-frame source-Y provenance.

**Replacement/lesson:** Treat proposal recall, evidence representation and authority as separate gates. R16’s “partial recall plus bounded confirmation-profile failure” is the correct diagnostic shape; do not compress it into a universal direction/motion or threshold problem.

**Current relevance/status:** **Open field risk.** The completed R18 causal rerun found abundant proposals/confirmed rows, but exact reviewed-interface identity and reviewed Y anchors are unavailable; proposal recall cannot be declared fixed from non-truth candidates. No further causal rerun is required for R19 design input.

**Confidence:** Confirmed for the cited local/field checkpoints; named unknown for the unobservable share of the private Base prefix/suffix.

### S11-F03 — Motion/bootstrap authority overreach

**Affected detector logic node(s):** `OIL-AUTHORITY` → `OIL-TRACKLET` → `OIL-SELECTOR`.

**Mechanism/trigger:** Registered motion, temporal continuity, a calibrated high-recall lane, or future keyframes promoted a path without independent same-frame material/phase identity. A bounded spatially smooth path can still change from reflection to liquid, and a sparse motion witness can retroactively authorize a long prefix.

**Intended benefit:** Recover a slowly moving interface through weak/intermittent appearance while preserving uncertainty and rejecting fixed or changing artifacts.

**Observed field failure:** **Confirmed facts:** R9 required high candidate-local motion coverage and formed no Base path. R10 then made the opposite error: two late motion keyframes retroactively promoted a 480–777.5 s Base path of 583 wrong rows at Y673–937, while reviewed Oil was approximately Y360–465. R11 reduced the run but the same path changed physical identity: reflection at 730.5 s, liquid at 735 s, reflection at 743.5 s. R12 correctly removed that path but retained Base recall gaps. **Strong inference:** motion is useful corroboration but cannot be a physical identity proof by itself.

**Attempts/versions:** R5 sequence-first trajectory; R7 explicit continuation/anchor tiers; R8 dynamic horizon; R9 six-frame calibrated dynamic seed; R10 retroactive calibrated path; R11 bounded bootstrap; R12 removed motion-only authority; R13–R17 require typed anchor/tracklet evidence; R18 preserves the prohibition.

**Evidence links:** [R9 diagnostic](s11-r9-windows-calibrated-observation-diagnostic.md), [R10 diagnostic](s11-r10-windows-path-and-residue-diagnostic.md), [R11 diagnostic](s11-r11-windows-bootstrap-composition-diagnostic.md), [R12 diagnostic](s11-r12-windows-phase-authority-diagnostic.md), [R17 architecture](../../20-architecture/s11-r17-physical-observation-ownership-architecture.md), [R18 architecture](../../20-architecture/s11-r18-lifecycle-closure-architecture.md).

**No-repeat rule:** Motion can discover or continue a candidate only inside a bounded, independently established physical owner. It cannot create an Oil anchor, cross a component handoff, retroactively publish a prefix, or satisfy phase admission without material/anchor evidence.

**Contracts to preserve:** bounded windows and commit horizon; explicit candidate/continuation/anchor tiers; physical track IDs remain distinct; UNKNOWN on insufficient or ambiguous identity; exact same-frame publication.

**Replacement/lesson:** Use motion as one typed witness among material, phase, anchor and geometry contracts. A smooth trajectory is a hypothesis, not an observation.

**Current relevance/status:** **Retired as an accepted design path; active regression guard.** The completed R18 causal rerun does not establish motion/bootstrap causality; this mechanism remains a regression guard while R19 is limited to its approved bounded release-chain design.

**Confidence:** Confirmed for R10/R11; high confidence in the no-motion-only-authority rule.

### S11-F04 — Component identity leakage and alias continuation

**Affected detector logic node(s):** `OIL-AUTHORITY` → `OIL-TRACKLET` → `OIL-PHASE-FILL`/`OIL-PHASE-DRAIN` and `FOAM-IDENTITY`.

**Mechanism/trigger:** Y adjacency, source-family preference, a recurring track, local appearance, broad-mask ordering, or a prior alias decision transferred identity across a physical phase/component change. Graph/run bounds then treated all adjacent `kind == oil` nodes as one path. Conversely, an overly strict distance component prototype censored legitimate continuation without proving identity.

**Intended benefit:** Preserve the same physical Oil or Foam object through representation changes and sparse gaps, while terminating ambiguous splits, incompatible branches and stale aliases.

**Observed field failure:** **Confirmed facts:** R10 Accum selected Foam/residue at Y191–297 instead of the lower Oil near Y450; high motion described moving residue, and candidate-specific conflict could disappear after Foam disappeared. R11 distinct-lower separation granted generic anchor authority and allowed residue family bypasses. R12 92 false residue rows had trajectory support; 85/92 had high texture conflict, while ordinary `oil_hypothesis` rows bypassed the conflict gate. R13 explicitly found local appearance, broad-mask order and adjacency graph edges creating component-free runs. R14 prior alias tracks and unselected Oil proposals vetoed real Foam; signed separation misclassified Oil Y327/Foam Y411 as alias. R15 repaired final-Oil-only symmetric aliasing but still required field validation. R16 found ambiguous split/merge assignment, material-path sibling masking and unsafe reverse re-entry; the final assignment repair made both child ownership and physical-proposal requirements explicit. **Strong inference:** the layered R17 Oil-before-Foam ordering risk is real, but its counterfactual effect on exact layered Oil Y is not proven because no frame-exact truth exists.

**Attempts/versions:** R8–R10 calibrated/recurring paths; R11 distinct-lower and component-mask authority; R12 typed semantic anchors; R13 identity/component replacement; R14 state/Foam ownership; R15 final-Oil-only alias; R16 directed tracklets and reciprocal assignment; R17 physical observation ownership; R18 preserves the handoff and alias boundaries.

**Evidence links:** [R10 diagnostic](s11-r10-windows-path-and-residue-diagnostic.md), [R11 diagnostic](s11-r11-windows-bootstrap-composition-diagnostic.md), [R12 diagnostic](s11-r12-windows-phase-authority-diagnostic.md), [R13 diagnostic](s11-r13-windows-identity-component-diagnostic.md), [R14 diagnostic](s11-r14-windows-state-and-foam-ownership-diagnostic.md), [R16 owner audit](s11-r16-local-coverage-owner-audit.md), [R17 diagnostic](s11-r17-windows-phase-and-episode-diagnostic.md), [R17 field result](../../60-evidence/s11/s11-r17-secure-windows-field-result.md).

**No-repeat rule:** Component identity requires explicit physical ownership and bounded same-family/phase-compatible handoff. Geometry, vertical separation, source family, local appearance, prior alias rejection, unselected candidates and recurring Y are never sufficient. Ambiguous split/merge, inverse topology and stale aliases terminate or abstain.

**Contracts to preserve:** one selected same-frame candidate per public series value; no track-ID or coordinate copy across handoff; final selected Oil only participates in Foam alias comparison; Foam remains publishable without Oil; UNKNOWN on ambiguity.

**Replacement/lesson:** Physical identity is an owner with a lifecycle, not a score bonus or graph edge. R16’s reciprocal assignment and complete-row veto are the minimum anti-leak controls; R17/R18’s explicit phase-local handoff is not a global state mutation.

**Current relevance/status:** **Open field risk, locally guarded.** The completed R18 audit preserves same-frame identity/provenance for compared fields, but exact reviewed-interface identity remains unknown and the owner-bounded selector abstain predicate is not identified. R19 implements bounded recovery locally; canonical Windows replay remains required.

**Confidence:** Confirmed mechanism for R10–R16; strong inference for the layered Oil counterfactual.

### S11-F05 — Initial-state and material-phase hard-lock asymmetry

**Affected detector logic node(s):** `OIL-HYPOTHESIS` → `OIL-PHASE-INITIAL`/`OIL-PHASE-FILL`/`OIL-PHASE-DRAIN` → `OIL-SELECTOR`.

**Mechanism/trigger:** A prior or state proposal was allowed to behave as current image evidence, or a material-phase gate had no valid lifecycle transition to release it. In the opposite direction, a no-owner initial-FULL path was left unconstrained and admitted arbitrary Oil. The same safety gate can therefore either hard-lock a real cycle out or fail open.

**Intended benefit:** Make `FULL`/`EMPTY` image-state evidence explicit, preserve safe no-interface semantics, require real physical ownership for fill/drain phases, and prevent state priors from becoming numeric Oil.

**Observed field failure:** **Confirmed facts:** R5 repeated confirmed initial state through every layer and exposed a boundary only through the matching edge entrance: FULL through the upper band and EMPTY through the lower band. A missed EMPTY entry left Accum `EMPTY_NO_INTERFACE` through the visible rise, high and drain, with first useful Oil only after the visual maximum and `OIL_DROP_START` about 49 s late. R6 removed prior-only numeric rows but made the retrospective state owner `NOT_APPLICABLE` in a way that also removed legitimate report context. R14’s fixed lower structure produced four false Accum Oil runs in the reviewed 480–650 s EMPTY interval, proving the hard guard must reject stationary structures while still admitting real upward entry. R16/R17 preserved that guard and confirmed the Accum 347-row EMPTY absence contract. R17 Base exposed the opposite asymmetry: Base remained OPEN for all 601 rows, with 45 false Oil rows in the FULL prefix, 201 fragmented rows in the drain, and 91 in the FULL suffix because no equivalent initial-FULL barrier existed. **Confirmed R18 causal facts:** Base remained behind `INITIAL_FULL_BARRIER` for all 601 rows; lower `Y > 800` entrance rejection is correct safety behavior, while the actual interface earliest harmful stage is before-or-at `OIL-PHASE-DRAIN` and remains unknown. Accum DRAIN produced 264 evaluation rows and zero passed; retained owner `000388:0265` remained a non-updated snapshot, while its non-update cause and actual drain candidate identity/direction remain unknown. The owner-bounded selector abstain predicate is also unknown. R19 bounded release-chain behavior is approved design only, not implemented or field-proven.

**Attempts/versions:** R5 prior/state lattice; R6 no-prior numeric correction and retrospective repair boundary; R7–R10 typed initial-state interpretation, calibrated lanes and artifact/track safeguards; R11–R14 lower reserve, component and initial-EMPTY repairs; R15–R17 explicit phase ownership with `empty_entrance_motion_enabled`; R18 replaces that boolean with explicit `confirmed_initial_state`, starts FULL behind `FILLED_BARRIER`, and retains EMPTY’s hard allowed-set gate.

**Evidence links:** [R5 field failure](s11-r5-secure-windows-field-failure.md), [R6 field failure](s11-r6-secure-windows-field-failure.md), [R14 diagnostic](s11-r14-windows-state-and-foam-ownership-diagnostic.md), [R16 diagnostic](s11-r16-windows-tracklet-and-foam-diagnostic.md), [R17 field result](../../60-evidence/s11/s11-r17-secure-windows-field-result.md), [R18 validation](../../30-validation/s11-r18-lifecycle-closure-validation.md), [R18 evidence](../../60-evidence/s11/s11-r18-lifecycle-closure.md).

**No-repeat rule:** `FULL`/`EMPTY` is typed current-raster evidence only. A confirmed state may constrain lifecycle admission but cannot create a coordinate. An edge-origin route may be the preferred release witness, but it cannot be the sole permanent route after a real entrance was missed. Any recovery route must remain bounded, physical, directional, material-supported and ambiguous-fail-closed. Do not widen entrance bands, reuse a state prior as image evidence, or leave a no-owner branch unconstrained to recover coverage.

**Contracts to preserve:** 347-row Accum initial-EMPTY absence; real lower-entry upward admission; no prior-only numeric Oil; coordinate-free filled barrier; UNKNOWN on owner loss/ambiguity; no global initial-state mutation.

**Replacement/lesson:** State is a phase input, not an observation. The fix for a hard lock is a measured lifecycle transition with a bounded missed-entrance recovery, not a softer gate, a prior-fed fallback or an absolute edge prerequisite.

**Current relevance/status:** **Active and highest-risk recurrence class.** The completed R18 audit confirms Base remained in the initial-FULL barrier for all 601 frames; lower `Y > 800` entrance rejection is correct safety behavior, while the actual interface's earliest harmful stage is before-or-at `OIL-PHASE-DRAIN` and remains unknown. Accum DRAIN produced 264 evaluation rows and zero passed; its retained non-updated snapshot's cause and actual drain candidate identity/direction remain unknown. The owner-bounded selector abstain predicate is also unknown. R19 implements bounded recovery locally and remains field-unqualified.

**Confidence:** Confirmed R5/R17 asymmetry and R18 source contract; completed causal rerun confirms the compared behavior and named release boundaries; named unknowns remain for the actual Base interface first loss, Accum snapshot/candidate cause and exact reviewed Y anchors.

### S11-F06 — Foam/Oil/material evidence cross-coupling

**Affected detector logic node(s):** `FRAME-EVIDENCE`/`OIL-HYPOTHESIS`/`OIL-CANDIDATE` → `OIL-AUTHORITY`/`OIL-SELECTOR`, and `FOAM-CANDIDATE`/`FOAM-IDENTITY`/`FOAM-EPISODE` → `SEQUENCE-COMPOSITION`.

**Mechanism/trigger:** Foam masks, broad material components, texture conflict, accepted/pending Foam, static overlap, or Oil alias logic were allowed to veto or create authority for the other material. A broad Foam/transition mask was treated as a Foam-only segmentation; a universal material veto suppressed real Oil; a candidate-only Oil or prior alias veto suppressed real Foam.

**Intended benefit:** Use material evidence to reject genuinely contradictory candidates while preserving independent Oil and Foam observation paths and allowing real layered scenes.

**Observed field failure:** **Confirmed facts:** R5 Foam was evaluated before Oil and constrained topology; every Base Foam event was false and Oil followed glare. R7 neutralizing only Foam-derived texture conflict increased Accum from 37 to 136 numeric frames, proving that an Oil veto was suppressing candidates, but topology could not be disabled globally. R8/R9 prior alias continuation rejected a later Foam episode despite a 37 px separated layer; R10 high motion/residue remained Oil; R11 broad component bottom and topology conflict invalidated all nine confirmed Foam rows, including real upward Foam. R12 85/92 false residue rows had high texture conflict, while the reviewed lower Oil also had conflict 1.0; R14 signed/inverted alias condition rejected a real separated Foam layer. R15 removed candidate-only/prior-alias veto and made final-Oil-only symmetric comparison. R17 field replay still had 99 Foam rows, of which 16 entry and 70 post-Foam/drain rows were false; the code proved independent projection but not sufficient episode discrimination. **Strong inference:** the layered Oil selection risk exists, but exact Oil accuracy remains not evaluated without truth anchors.

**Attempts/versions:** R2–R4 Foam/Spatial/static authority repair; R5 pre-Oil Foam masking; R6 optics-aware independent observation; R7 evidence tiers; R8–R10 alias and material-path repairs; R11 broad component/different-family leakage; R12 typed conflict; R13–R15 phase/component and final-Oil alias replacement; R16/R17 independent Foam tracklets; R18 preserves independence and removes the separated-layer shortcut.

**Evidence links:** [R2 diagnostic](s11-r2-foam-spatial-authority-diagnostic.md), [R4 diagnostic](s11-r4-windows-residual-authority-diagnostic.md), [R5 field failure](s11-r5-secure-windows-field-failure.md), [R7 diagnostic](s11-r7-windows-observation-recovery-diagnostic.md), [R8 diagnostic](s11-r8-windows-calibrated-observation-diagnostic.md), [R11 diagnostic](s11-r11-windows-bootstrap-composition-diagnostic.md), [R14 diagnostic](s11-r14-windows-state-and-foam-ownership-diagnostic.md), [R15 evidence](../../60-evidence/s11/s11-r15-state-aware-material-ownership.md), [R17 field result](../../60-evidence/s11/s11-r17-secure-windows-field-result.md), [R18 architecture](../../20-architecture/s11-r18-lifecycle-closure-architecture.md).

**No-repeat rule:** Foam is never an Oil mask, cutoff, Oil-boundary selector or state authority. Oil is never a Foam veto unless final same-frame Oil repeatedly coincides with the same physical boundary under the signed, bounded alias contract. Rejected/pending/unselected evidence cannot veto the other series. Broad material-mask bottoms and vertical separation cannot decide identity.

**Contracts to preserve:** independent Foam publication with Oil unknown; final-Oil-only signed alias comparison; Oil/foam ordering is composition context, not coordinate truth; per-series validity; no universal material-conflict veto; same-frame provenance.

**Replacement/lesson:** Material is evidence with typed ownership. Contradiction is local and phase-aware, not a global mask. R18’s bounded Foam formation must remain independent of Oil and must not restore extent-only or separated-layer authority.

**Current relevance/status:** **Open field risk.** The completed R18 rerun closes the exact Foam eligibility and formation gates and records seven false ENTRY-SPLASH paths. Compared fields remain invariant, but field accuracy remains FAIL; Foam is intentionally outside approved R19 scope.

**Confidence:** Confirmed cross-coupling in R5/R7/R8/R11/R14; confirmed R17 false episode publication; strong inference for layered Oil causality.

### S11-F07 — Foam episode false dynamics and stale episode identity

**Affected detector logic node(s):** `FOAM-CANDIDATE`/`FOAM-IDENTITY` → `FOAM-EPISODE` → `SEQUENCE-COMPOSITION`.

**Mechanism/trigger:** Extent/area/width evolution, one registered motion spike, score/whiteness, broad bounding boxes, static-map miss, or time-only grouping accepted a fixed glare, Y80 residue, downward wall/splash or fragmented component as a Foam episode. Conversely, strict width/admission requirements fragmented or suppressed a real narrow/upward episode. A prior rejected alias/episode track then continued without fresh same-frame coincidence.

**Intended benefit:** Confirm physical Foam fronts with bounded material, topology, dynamic and spatial evidence; preserve real narrow onset and stable layers without publishing residue or static glare.

**Observed field failure:** **Confirmed facts:** R3’s static map and row-coherent controls removed local false episodes but did not prove the private Base component was covered; R4 required two compatible samples. R6/R7 showed static Foam-like terms resembled real Foam, while one dynamic sample was insufficient. R10 false Base/Accum groups satisfied the aggregate R16 episode contract; the bundle did not separate 52 reviewed real rows from 50 false rows. R11 the real Accum Foam front (Y465→218) was admitted only 44 raw/22 eligible/9 public rows, with fixed width causing losses, then all nine were invalidated by composition. R14 had 113 raw/80 eligible/23 public and still rejected a real dynamic trajectory through alias logic. R17 published 16 entry-splash, eight post-Foam Y80 and 62 drain false Foam rows; all had exact same-frame projection, so the first harmful stage was episode association/confirmation. **Strong inference:** front-Y formation is a promising discriminator because reviewed true Foam rose while Y80/wall residue was stationary or opposite. The completed R18 rerun closes the exact eligibility/formation gates and identifies seven false ENTRY-SPLASH paths, but R18 remains field-unqualified.

**Attempts/versions:** R3 learned static opposition and row topology; R4 pending→accepted confirmation; R6 one-motion-sample episode; R7 independent Foam; R8/R9 alias continuation and graph visibility; R10/R11 material tracks and width admission; R12–R17 bounded episode/track owners; R18 deletes extent-only and separated-layer shortcuts and requires bounded upward formation or a bounded stable layer.

**Evidence links:** [R3 sequence diagnostic](s11-r3-sequence-observability-root-cause.md), [R4 residual diagnostic](s11-r4-windows-residual-authority-diagnostic.md), [R6 checked-video reconciliation](s11-r6-checked-video-reconciliation.md), [R16 tracklet/foam diagnostic](s11-r16-windows-tracklet-and-foam-diagnostic.md), [R17 phase/episode diagnostic](s11-r17-windows-phase-and-episode-diagnostic.md), [R18 validation](../../30-validation/s11-r18-lifecycle-closure-validation.md), [R18 evidence](../../60-evidence/s11/s11-r18-lifecycle-closure.md).

**No-repeat rule:** A new episode needs bounded physical front formation or the narrowly specified stable-layer witness. Brightness, score, a single motion spike, extent-only change, downward/constant-Y movement, broad mask, separated Oil layer, prior episode rejection or Oil unavailability cannot substitute. Every public Foam row must be a selected same-frame Foam candidate.

**Contracts to preserve:** independent Foam publication; bounded age/missing/drift; narrow real onset remains eligible when it forms a layer; false episode remains diagnostic; no Oil dependency; exact selected Foam/sequence/CSV equality.

**Replacement/lesson:** Episode identity is physical and bounded. R18’s local formation witnesses are the minimum replacement; field replay must measure both real-episode recall and false-track rejection, not just Foam row count.

**Current relevance/status:** **Active.** The completed R18 rerun records seven false ENTRY-SPLASH paths, zero confirmed POST-FOAM/DRAIN Foam, and the exact eligibility/formation gates. Foam behavior is intentionally outside approved R19 scope; any future Foam change needs its own design and field gate.

**Confidence:** Confirmed false episode stage and local historical mechanisms; strong inference for front formation as field discriminator.

### S11-F08 — Lifecycle closure and owner-loss dead ends

**Affected detector logic node(s):** `OIL-TRACKLET` → `OIL-PHASE-INITIAL`/`OIL-PHASE-FILL`/`OIL-PHASE-DRAIN` → `OIL-SELECTOR`.

**Mechanism/trigger:** A phase could enter FILLING but never close to `FILLED_BARRIER`/`DRAINING`; initial FULL had no predecessor barrier; established partial fill was lost and could not reverse into drain; re-entry could copy IDs/coordinates, accept a reversed/distant row, or reset to unconstrained OPEN. Safe owner loss and genuine phase handoff were not distinct.

**Intended benefit:** Keep material ownership fail-closed while allowing a genuinely established physical phase to survive bounded track loss and reverse direction through one independently confirmed compatible owner.

**Observed field failure:** **Confirmed facts:** R17 Base stayed OPEN all 601 rows, never formed a barrier or DRAINING owner, and published 136 false no-interface-prefix/suffix Oil rows plus 201 fragmented drain rows. Accum formed FILLING for 41 rows but no barrier or DRAINING; the real post-700 s drain was blocked whenever no dynamic owner existed, yielding zero Oil in 160 drain rows. R17’s material-phase failure was not `_drain_phase_reentry` because DRAINING never existed. R16 had a bounded owner-loss gap and explicitly rejected branch hops, but its field boundary remained partial-fill reacquisition after owner loss. R18 adds explicit FULL barrier release and one bounded partial-fill reversal; local tests confirm reversed/distant/ambiguous/material-opposed releases remain UNKNOWN.

**Attempts/versions:** R11–R14 phase/component replacements; R15 state-aware material ownership; R16 directed tracklets and lifecycle; R17 physical ownership; R18 lifecycle closure.

**Evidence links:** [R16 owner audit](s11-r16-local-coverage-owner-audit.md), [R16 field diagnostic](s11-r16-windows-tracklet-and-foam-diagnostic.md), [R17 field result](../../60-evidence/s11/s11-r17-secure-windows-field-result.md), [R17 architecture](../../20-architecture/s11-r17-physical-observation-ownership-architecture.md), [R18 architecture](../../20-architecture/s11-r18-lifecycle-closure-architecture.md), [R18 evidence](../../60-evidence/s11/s11-r18-lifecycle-closure.md).

**No-repeat rule:** A phase transition requires an explicit physical owner and complete current-row material/ambiguity/direction evidence. Do not reopen unconstrained `OPEN` after owner loss, mutate initial state globally, copy observations or IDs across handoff, or release a barrier on a stationary, upward, internal, reversed, distant, provisional or ambiguous row.

**Contracts to preserve:** initial EMPTY hard gate; confirmed FULL coordinate-free barrier; bounded owner-loss/reversal only after established fill; append new IDs without copying observations; UNKNOWN on ambiguity; one owner chain per physical phase.

**Replacement/lesson:** Lifecycle state must close both directions: safe barrier entry and safe owner reacquisition. R18 is a replacement of missing transitions, not a relaxation of material ownership.

**Current relevance/status:** **Active field gate.** Base release admission and Accum partial release remain the narrowed owners. The completed causal rerun freezes the remaining unknowns; R19 adds only the approved bounded release chain and is locally focused-tested, while canonical Windows replay remains unproven.

**Confidence:** Confirmed R17 lifecycle observations, R18 local closure contract and completed transferred causal rerun; field effectiveness remains FAIL and exact reviewed Y anchors are unavailable.

### S11-F09 — Coordinate, validity and provenance ambiguity

**Affected detector logic node(s):** `OIL-PROJECTION` → `PUBLICATION-PROVENANCE`/`CSV-PUBLICATION`/`TRACE-PUBLICATION` → `RESULT-PRESENTATION`; cross-cutting for all upstream nodes.

**Mechanism/trigger:** Current-frame trace was mistaken for completed-window output; ROI-local and source-frame Y were mixed; stale extraction reclassified final Foam as Oil; a single `is_valid` hid independent series validity; graph bridges or report events appeared as observed values; and missing first-reject/stage fields forced causal guesses.

**Intended benefit:** Make every published value auditable from source frame through selected candidate, sequence, CSV and report while keeping presentation helpful without manufacturing observations.

**Observed field failure:** **Confirmed facts:** R1 found the report exposed raw event/debug volume, used indistinguishable solid bridges and lacked physical landmark context; the repair preserved detector fingerprints and added report-only solid/dashed semantics. R3/R7/R11/R17 repeatedly corrected current-frame versus final-sequence interpretation. R11 extraction initially mixed ROI-local and source Y; R12/R17 corrected Foam validity and the 733/754 s intervals: they were unselected Oil proposals plus false Foam, not final Oil. R17 published exact selected-candidate and sequence/CSV equality despite incorrect field effectiveness, proving provenance integrity is necessary but not sufficient for accuracy. **Confirmed R18 causal result:** compared selected-candidate, completed-sequence and CSV fields remain invariant on `1,202/1,202` common rows with zero mismatches. **Named unknowns:** Base actual interface first loss, Accum snapshot non-update cause and drain candidate identity/direction, owner-bounded selector abstain predicate and exact reviewed Y anchors remain unresolved; this does not qualify R18 in the field.

**Attempts/versions:** R1 report presentation; R3 trace/sequence contract; R5–R7 raw versus final authority; R8–R12 final-sequence trace additions and graph validity; R13 per-stage path observability; R14–R18 exact same-frame and CSV contracts.

**Evidence links:** [R1 report diagnostic](s11-user-report-observability-diagnostic.md), [R1 evidence](../../60-evidence/s11/s11-user-observation-report-repair.md), [R3 root-cause diagnostic](s11-r3-sequence-observability-root-cause.md), [R7 reconciliation](s11-r7-checked-video-direct-image-reconciliation.md), [R11 field result](../../60-evidence/s11/s11-r11-secure-windows-field-result.md), [R17 field result](../../60-evidence/s11/s11-r17-secure-windows-field-result.md), [R18 validation](../../30-validation/s11-r18-lifecycle-closure-validation.md).

**No-repeat rule:** Label every trace layer (`current`, `sequence`, `public`), retain source-frame coordinates and frame identity, emit first failing stage and unavailable-vs-clean evidence, keep `oil_is_valid`/`foam_is_valid` independent, and make report bridges endpoint-only display artifacts. Never use report, truth, Recipe or debug metrics as detector authority.

**Contracts to preserve:** selected candidate Y = sequence raw Y = CSV raw Y; no interpolation/carry; per-series validity; complete event/debug audit outside the narrative; source coordinates are not silently crop-adjusted.

**Replacement/lesson:** Provenance is an acceptance contract and a diagnostic instrument, not a detector repair. R1 improves comprehension downstream; it cannot repair missing/wrong observations.

**Current relevance/status:** **Active cross-cutting guard; local contract passes, field accuracy remains separate.** The completed causal rerun confirms selected-candidate, completed-sequence and CSV invariance on `1,202/1,202` common rows with zero mismatches; this does not qualify R18 in the field.

**Confidence:** Confirmed provenance/report defects and repairs; completed causal rerun confirms compared-field invariance, with reviewed Y anchors and upstream physical identity still unknown.

### S11-F10 — Global-threshold or case-specific escape hatch

**Affected detector logic node(s):** all nodes, especially `FRAME-EVIDENCE`, `OIL-AUTHORITY`, `OIL-PHASE-INITIAL`/`OIL-PHASE-FILL`, and `FOAM-CANDIDATE`/`FOAM-EPISODE`.

**Mechanism/trigger:** A local field symptom is “fixed” by lowering a global boundary/Foam/ambiguity threshold, widening the EMPTY entrance, adding a fixed Y/time/Glass/video branch, making Foam depend on Oil, or using interpolation. These changes improve nominal coverage by admitting an unbounded family of artifacts or by hiding missing evidence.

**Intended benefit:** Increase apparent numeric/Foam coverage or recover one reviewed field segment quickly.

**Observed field failure:** **Confirmed facts:** R2 paired-edge relaxation to `0.95` created six explanatory-overlay false numerics; R2 general weak paths admitted overlay candidates; R5–R10 repeatedly showed that coverage gains could be false Foam, fixed lower structures or long residue paths. R14 proved position/Artifact calibration cannot distinguish a stationary lower structure from real lower-entry Oil at the same location. R17/R18 explicitly prohibit private coordinates/timestamps, global relaxation and Recipe retuning. **Strong inference:** these are not merely style concerns; they erase the distinction between evidence availability, physical ownership and uncertainty that the field failures repeatedly exposed.

**Attempts/versions:** Rejected ablations across R2, R5–R10; explicit architecture reset R11; typed ownership R12–R18; R18 validation’s historical non-regression list.

**Evidence links:** [R2 diagnostic](s11-r2-foam-spatial-authority-diagnostic.md), [R5 field failure](s11-r5-secure-windows-field-failure.md), [R10 diagnostic](s11-r10-windows-path-and-residue-diagnostic.md), [R14 diagnostic](s11-r14-windows-state-and-foam-ownership-diagnostic.md), [R18 validation](../../30-validation/s11-r18-lifecycle-closure-validation.md), [R18 architecture](../../20-architecture/s11-r18-lifecycle-closure-architecture.md).

**No-repeat rule:** A repair must be mechanism-bounded, generic across Glasses, and accompanied by two-sided controls, candidate/track/phase evidence and field replay. No private identity, fixed coordinate/time, broad threshold relaxation, global material veto, interpolation or report-side smoothing may enter production control flow.

**Contracts to preserve:** fail-closed UNKNOWN; no hard-coded truth; no candidate-family privilege; no global threshold changes without a separately owned evidence contract; bounded resources and performance.

**Replacement/lesson:** When coverage and physical agreement diverge, stop and locate the earliest evidence/authority seam. Never turn the holdout into a tuning fixture.

**Current relevance/status:** **Permanent guard.** Every future S11 detector change must pass this rule. The completed R18 causal audit and field FAIL do not authorize threshold or case-specific escape hatches; R19 remains generic and bounded, with canonical field proof still required.

**Confidence:** Confirmed rejected changes and recurring field outcomes; high confidence in the guard.

## R1–R18 coverage map

The map is a navigation index, not a second chronology. Each revision is represented by the mechanism(s) it exposed or tested.

| Attempt | Primary registry IDs | What the history contributes |
|---|---|---|
| R1 | `F09` | report/presentation cannot repair detector truth; preserve immutable samples and provenance |
| R2 | `F01`, `F06`, `F10` | accepted-Foam Spatial authority seam; rejected broad threshold/weak-path relaxations |
| R3 | `F01`, `F06`, `F07` | cap invalidity, learned static opposition and row-coherent Foam; residual private-field risk |
| R4 | `F01`, `F06`, `F07`, `F10` | static-overlap boundary, pending confirmation and Foam/Oil ordering repair |
| R5 | `F01`, `F03`, `F05`, `F06`, `F10` | pre-selection loss; false glare Foam; repeated EMPTY prior and late event |
| R6 | `F01`, `F05`, `F06`, `F09` | ambiguous anchor promotion, over-censoring, independent Foam and retrospective-state boundary |
| R7 | `F01`, `F02`, `F03`, `F06` | typed tiers; representation gaps; motion/static separation; independent Foam preservation |
| R8 | `F02`, `F03`, `F04`, `F06`, `F09` | calibrated recall, over-strict local motion, alias continuation and trace limitations |
| R9 | `F02`, `F03`, `F04`, `F06`, `F09` | zero six-frame bootstrap, 17 px alias error, graph/trace observability |
| R10 | `F03`, `F04`, `F06`, `F07`, `F10` | retroactive motion path and moving Foam/residue promoted as Oil |
| R11 | `F01`, `F03`, `F04`, `F06`, `F07`, `F09` | bounded bootstrap still changed identity; distinct-lower authority; broad Foam mask |
| R12 | `F01`, `F04`, `F06`, `F09` | typed authority reset; semantic anchor bypass; per-series Foam validity |
| R13 | `F04`, `F06`, `F09` | local appearance/order/adjacency is not component identity; stage observability |
| R14 | `F04`, `F05`, `F06`, `F07`, `F08` | continuation after anchor loss; EMPTY stationary-structure safety; signed alias bug |
| R15 | `F04`, `F05`, `F06`, `F07` | final-Oil-only symmetric alias; state-aware ownership; field replay still required |
| R16 | `F02`, `F04`, `F06`, `F07`, `F08`, `F09` | directed tracklets, reciprocal assignment, full-row material veto and owner-loss boundary |
| R17 | `F02`, `F04`, `F05`, `F06`, `F07`, `F08`, `F09` | frozen field failure: Base open/full/drain, Accum partial-fill lock, false Foam; provenance passes |
| R18 | `F05`, `F07`, `F08`, `F09`, `F10` | explicit FULL barrier, partial-fill reversal, bounded Foam formation; Windows field FAIL; completed causal rerun freezes release/foam boundaries and named unknowns; compared-field invariance passes; R19 bounded release-chain design approved only |

## Current non-regression contract

The registry does not replace the current architecture or gate. For current ownership, use the [S11 detector responsibility architecture](../../20-architecture/s11-detector-responsibility-architecture.md), [R18 validation contract](../../30-validation/s11-r18-lifecycle-closure-validation.md), [R18 causal closure](s11-r18-windows-causal-closure.md), [R19 architecture](../../20-architecture/s11-r19-bounded-drain-release-chain-architecture.md), and [R19 validation contract](../../30-validation/s11-r19-bounded-drain-release-chain-validation.md). The durable lessons are:

- one generic detector serves every Glass; no private identity or truth coordinate enters control flow;
- current-frame proposals, physical identity, material phase, completed-window selection, composition and projection remain separate owners;
- state priors and report interpretation never create numeric Oil;
- Foam remains independent of Oil, and broad material evidence never becomes a universal Oil veto;
- public values are selected same-frame candidates with exact sequence/CSV raw-Y equality;
- unknown, missing, ambiguous and hard-invalid evidence remain observable and fail closed; and
- every claimed field repair requires a new Windows replay, not coverage or fingerprint substitution.
