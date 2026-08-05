# S11-D1 Foam Structural/Refractive Discrimination and Oil Context Safety

## Authority and status

S11-D1 is the first source-repair slice after the completed S11-C full-video forensic diagnostic.
It addresses the proven shared boundary where accepted S5-A Foam evidence becomes routing authority
inside S5-B Oil observation. It does not authorize a general detector retune or the separate sample3
candidate-generation/identifiability repair.

**Status:** `ACCEPTED — fresh Lane C exact-head audit PASS; PR #87 guarded-squash-merged`

**Worker starting repository identity:** `main @ 5feb973c41adeac176a96efc0efbc3b435c2bbb3`

The S5-A Foam contract, S5-B observability architecture, accepted P2/FULL-EMPTY preservation,
Spatial production behavior and local-corpus identity rules remain authoritative.

## Evidence that opens S11-D1

S11-C replayed all four local videos through the real production stream and met its exit criterion.
The strongest new causal evidence is sample4:

- production Foam publication: `113/113`;
- production Oil publication: `110/113`;
- accepted Foam evidence is structurally associated with a bright U-shaped lower rim/refractive region;
- when only accepted Foam context is withheld from the Oil owner, Oil publication falls from `110` to `0`;
- at representative frames the accepted Foam front lies on or near the visual Oil transition and changes
  which lower candidate can qualify for Foam-separated Oil recovery.
The direct conclusion is narrower than "Foam is wrong everywhere": some sight-glass structural/refractive
appearances satisfy the current S5-A whiteness/texture/component criteria strongly enough to become
accepted Foam, and that accepted context can materially alter S5-B Oil admissibility and ranking.

The same S11-C evidence also proves other residual Oil defects, but they are not D1 scope:

- sample3:899 has a correct-Y candidate that remains non-identifiable because positive support is weak;
- sample3:2697 has a visually clear boundary for which no material candidate is generated;
- Spatial is required for valid sample2 recovery but also owns suspicious sample3 full-like acceptances.

These observations justify later S11-D2/S11-D3 work; they do not justify broadening D1 before its own
Foam/Oil responsibility boundary is repaired and replayed.

## Objective

Prevent non-Foam structural/rim/refractive sight-glass evidence from silently acquiring Foam routing
authority over Oil while preserving genuine Foam detection and the existing S5-B fail-closed ambiguity
contract.

D1 SHOULD prefer genuinely discriminative evidence or safer context handoff semantics over a global
score shift. The implementation is not preselected by this document.

The repair must answer two separate questions:

1. why the observed U-shaped structural/refractive component currently qualifies as accepted Foam;
2. when Foam evidence is accepted, what proof is sufficient before that context may mask, constrain or
   re-route an otherwise plausible Oil boundary.
## Bounded external-reference gate

Before choosing a production mechanism, the Worker SHOULD perform a short evidence-focused review of
maintained/credible sources only where they can inform the existing owners. The review is advisory,
not acceptance authority.

Useful questions are limited to:

- which bubble/foam morphology or spatial-consistency features distinguish dispersed Foam from vessel
  rim/refraction/structural brightness;
- which liquid-boundary evidence families remain robust under transparent or low-transparency vessel
  optics without globally weakening ambiguity;
- how multi-line/cross-ROI consistency can reject local structural outliers while preserving valid
  flat or near-horizontal interfaces.

Do not preselect ML, graph-cut, Hough, circularity thresholds, component-count rules or a new dependency.
External ideas must be adapted only if they fit the current S5-A/S5-B ownership, packaging and CPU
contracts more safely than a repository-native solution.

## Accepted implementation record

### Bounded reference review

The Worker stopped the reference review once the repository-native ownership choice was clear:

- OpenCV 4.x `imgproc` shape/connected-components documentation confirms that component geometry and
  occupancy statistics are maintained upstream primitives already available in the current dependency set.
- Laupsien et al., *Physics of Fluids* (2019), DOI `10.1063/1.5088945`, uses bubble morphology including
  eccentricity and solidity as verification evidence. D1 adopts only the general morphology principle;
  it does not import paper-specific circularity/eccentricity thresholds.
- Musić et al., *Sensors* (2023), DOI `10.3390/s23167126`, documents glass-container refraction/reflection
  artifacts and uses morphology/blob selection for a low-cost image pipeline. Bobovnik et al., *Sensors*
  (2021), DOI `10.3390/s21082676`, detects a transparent-vessel liquid level on multiple vertical lines
  specifically to reject local bubble/droplet outliers. D1 adopts the spatial-consistency principle only.

ML, graph-cut, Hough, new dependencies and paper-specific shape thresholds were rejected as unnecessary
for the proven D1 boundary.

### Responsibility boundary and mechanism

Current production had one implicit authority: once `FoamTemporalGate` accepted an S5-A candidate,
`OpenCvPhaseDetector` always passed that candidate front and mask into S5-B. That context both selected
Foam-separated Oil recovery and removed the same mask from Spatial evidence. S5-A publication therefore
silently granted S5-B masking/routing authority.

D1 preserves S5-A classification, temporal acceptance, Foam publication, fill-state input and Foam tracker
updates. It adds a stateless `evaluate_foam_oil_context_authority` check only at the S5-A → S5-B handoff.
The observed unsafe class is a component that spans most of the ROI but is hollow across many individual
rows, matching the bright U-shaped rim/refractive structure seen in S11-C. Routing authority is withheld
only when all four conditions hold:

- component width ratio is at least `0.70`;
- component bounding-box fill ratio is below `0.30`;
- at least `0.25` of component rows span at least `0.35` of the component width;
- median occupied/span compactness on those wide rows is below `0.65`.

An accepted Foam candidate that matches this structural pattern remains published as Foam but contributes
neither front nor mask to S5-B. S5-B then evaluates its independent evidence and remains fail-closed when
that evidence is non-identifiable. No detector setting, Recipe/public schema, temporal state, dependency,
truth input or post-owner numeric reconstruction is added.

### Development evidence

On the preserved S11-C sampled rows, the final authority guard withholds `0/8` accepted base-sample
contexts, `0/10` sample2 contexts and `0/20` sample3 contexts, while withholding `113/113` sample4
contexts. Replaying the same 113 sample4 frame/time rows changes raw Oil publication from `110/113` to
`0/113`; Foam remains `113/113`, all 113 Oil outcomes are `ambiguous`, and no alternate structural Oil
candidate is promoted. The user-confirmed sample2 anchors remain `30 → 599` and `60 → 598`.

The ignored S11-C bundle remains unchanged and retains fingerprint
`9dc96fc04f9dcb1e00f5c120650ce6953e26239a0ecb61278cd6287b40519370`.

## Non-goals and prohibited shortcuts

S11-D1 does not include:

- global Foam threshold increase/decrease as the sole repair;
- global Oil boundary/ambiguity threshold retuning;
- sample4/video-name/Recipe-specific branching;
- sample3 candidate-generation or positive-evidence recovery;
- trajectory interpolation or initial-state retrospective reconstruction;
- persisted/public schema, Recipe or truth changes;
- new dependency or ML model without separately proven necessity;
- weakening genuine Foam, glare, structure, no-interface or observational-equivalence protections.
## Acceptance boundary

A production repair is acceptable only if exact-head evidence shows all of the following:

- the sample4 structural/rim/refractive class no longer obtains unsafe Foam routing authority;
- genuine Foam acceptance remains protected by the existing S5-A regression set;
- sample4 Oil is not merely recovered by promoting another structural candidate or by globally weakening
  ambiguity/identifiability;
- user-confirmed sample2 Spatial Oil recoveries remain preserved;
- retained glare, structure, collision and FULL/EMPTY no-interface protections remain fail-closed;
- no new hidden temporal state, post-owner numeric reconstruction or truth-derived production input is added;
- CPU/resource behavior remains bounded within the existing architecture.

The repair SHOULD include minimal regression cases that prove both sides of the responsibility boundary:
a structural/refractive non-Foam case that cannot control Oil routing, and genuine Foam cases that still can.
Use the smallest exact local frames/windows and compact expectations needed to prevent recurrence.

## S11-C artifact retention

The ignored S11-C forensic bundle is intentionally preserved through D1 because it contains the exact
representative images, masks and counterfactual evidence needed for source attribution:

`sample/output/s11-c-full-video-forensics/s11c-20260805T161456/`

Recorded bundle fingerprint:
`9dc96fc04f9dcb1e00f5c120650ce6953e26239a0ecb61278cd6287b40519370`

It remains temporary, Git-ignored evidence and must not become a golden artifact. Cleanup belongs to the
S11 merge/close owner after D1/D2 no longer need it.

## Next gate

S11-D1 passed fresh **Lane C — Independent Review** at exact base `5feb973c41adeac176a96efc0efbc3b435c2bbb3` / exact head `ac468a73fa8e890b0855ed63afb2979ca4378c42` and was native guarded-squash-merged as `0f4558dd3723a1923854274039112714a97fca71`.

Auditor-focused validation returned `109 passed`, and the exact-head four-video replay preserved every base/sample2/sample3 Oil/Foam/fill-state signature. sample2 `30 → 599` and `60 → 598` remained intact. sample4 retained Foam `113/113`, withheld Oil-context authority `113/113`, changed Oil from the preserved S11-C baseline `110/113` to `0/113`, and promoted no alternate numeric Oil path.

The next source gate is **S11-D2 — sample3 positive-evidence recovery** for the separate candidate-present-but-non-identifiable and candidate-not-generated defects. Spatial reconciliation remains an acceptance constraint rather than a blanket threshold task. The S11-C forensic bundle remains preserved as temporary ignored evidence through the next decision-bearing work.

S11 completion, Windows field PASS, detector/general-field accuracy PASS, sample4 independent Oil recovery, initial-state retrospective reconstruction and S12 are not implied.