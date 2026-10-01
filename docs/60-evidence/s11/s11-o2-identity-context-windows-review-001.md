# S11 O2 identity context — transferred Windows review and reconciliation

Date: 2026-10-01. Reported checkout: `89acfb0`.
Scope: existing review-002/003 images, replies, labels and packet geometry only.
This records the user's context report and subsequent source/coordinate correction.
Private JSON, images and generation scripts were not inspected locally. Windows
observations below are transferred evidence, not an independent image assessment.
No detector/scorer change, new human label, calibration or field qualification is
claimed. FIELD FAIL remains unchanged.

[Source audit](s11-o2-identity-context-source-audit.md) defines the preceding local
sampling controls. [W1 architecture](../../20-architecture/s11-interface-observability-witness-architecture.md#w1-target-and-aggregation-contract--design-boundary)
and [validation](../../30-validation/s11-interface-observability-witness-validation.md#w1-aggregation-challenger-controls--not-yet-acceptance-evidence)
continue to separate candidate identity, local path agreement and scalar truth.

## Reported scope and preservation

- review-002: BASE frame 14386, timestamp 600.016 s; idx0, idx10, idx11, idx20;
  active `labels-v2.json` revision 14.
- review-003: Accum frame 16280, timestamp 679.012 s; idx10, idx15;
  active `labels.json` revision 4, v2 schema.
- Original report states labels/packets/bundle links were read-only and revisions
  preserved. Only abbreviated hashes were supplied; they cannot be independently
  rehashed here. The correction does not supply a new full before/after receipt.
- Source association was reported as `human_attestation`. Packet hash references
  establish the recorded receipt association, not independent video rehashing.
- Coarse reviewed-truth interval descriptions do not prove instantaneous motion,
  filling state or Foam disappearance in these individual still images.

## Reconciled findings

| Item | Transferred finding | Consequence |
|---|---|---|
| review-002 idx10 geometry | labels/packet agree: X [130,236] Y378; [236,343] Y363; [343,449] Y354 | No stored coordinate mismatch reported |
| idx10 human record chronology | reply-004/006 describe S1 near and S2/S3 away; reply-010 explicitly creates new path judgments off/near/off, retained in current labels | Preserve current off/near/off and whole-candidate interface. Earlier prose is historical disagreement, not a second active truth set |
| idx10 claimed image observation | "S1 closest, S2/S3 away" was subsequently identified as old reply text, not a fresh visual observation | Withdraw the original report's claim of independent image corroboration for this statement |
| idx10 historical PNG provenance | reply-004/006/010 do not identify image filenames; exact reply-to-PNG association not established | Do not attribute a saved PNG to those historical judgments without evidence; missing association does not by itself invalidate current labels |
| review-003 idx15 geometry | labels/packet/generation code agree on [317,328,313,295,296] across the five X bins | The earlier [314,328,315,295,296] was reported as model image-text misreading, not a stored-data discrepancy |
| review-003 idx10 geometry | labels/packet/generation code agree on [209,210,217,219,220] | Native path remains distinct from the reference annotation and candidate center |
| idx10 reference annotation | Human record says Y213; report reads RefY212 from guide; no guide generator or stored numeric source for 212 found | Source of the reported 212 remains unknown, including possible image-text error. Do not silently round or replace human Y213; canonical_y217 is another distinct quantity |

For review-003 the common X bins are [1218,1303], [1303,1388], [1388,1473],
[1473,1558], [1558,1643]. Packet geometry and exact label geometry are the numeric
sources for joins. Matching hardcoded values in a guide generator corroborates
its intended overlay; that helper is not a new authority over packet/labels and
does not prove which code produced a particular PNG. Further model OCR retries
are not requested.

## Field meanings checked locally

- `identity_review`, `path_reviews`, artifact tags and human notes belong to
  labels/replies. They are not automatic witness measurements.
- [BandWitness](../../../src/oil_tracker/adapters/vision/oil_interface_witness.py)
  and [band extraction](../../../src/oil_tracker/adapters/vision/oil_interface_diagnostics.py)
  retain per-band `glare_fraction`, alongside brightness/gradient measurements.
  Absence of a semantic reflection classifier is not absence of local glare or
  brightness-transition measurements. These fields do not reconstruct a human
  rationale or certify physical identity.
- The transferred correction reports all-zero glare bands for review-002 idx0
  and review-003 idx10 and nonzero far-below glare for idx15 (about 0.098–0.114).
  Other candidates' extraction output was truncated. No abnormality threshold,
  artifact identity or exhaustive nonzero-band inventory follows; no rerun is
  needed merely to finish that inventory for this question.
- Witness `NOT_EVALUATED` concerns the O1 diagnostic decision. The production
  [phase identity owner](../../../src/oil_tracker/adapters/vision/oil_phase_identity.py)
  exists separately. Human interface identity does not override `rejected=true`;
  production rejection and human truth are separate axes.
- idx16 is also human-labeled interface, so its proximity to idx0 is not a
  negative identity counterexample. Nor is Y the only demonstrated difference
  between idx0 and idx20: the supplied report did not establish a discriminating
  visual cue independent of known truth Y.

## Frozen note duplication — provenance limit, no repair

The user reports identical idx10-related notes at candidate indices 0/11/20 in
frozen r10, with `identity=unreviewed`, `basis=legacy_v1_case`, `at=null`.
idx10 has `basis=legacy_v1_annotation`. Current idx0/11/20 notes instead have
individual `direct_human_review` attribution. Frozen r10 remains unchanged and
is not the current revision-14 label source.

Local inspection of [migrate](../../../tests/diagnostics/s11_review_records.py)
shows explicit fallback:
`original.get('review_note', case['review_note'])`, with legacy attribution rather
than a fresh human review. This can preserve one case note on several candidates.
The reported pattern is compatible with that behavior; duplication alone does
not establish corruption or a migration bug. Exact private origin remains
unverified without the original v1 snapshot and generating revision. That
historical attribution is not candidate-specific rationale. No frozen rewrite
or further historical investigation is required for the current identity question.

## Decision and remaining information

Close this bounded document/coordinate reconciliation. Retain current labels and
prior score results; do not relabel, exclude an inconvenient pair or tune a score
in response to historical disagreement. The private images may contain useful
context, but this report has not established an independently observed,
discriminating feature that justifies one new identity mechanism.

The user's initial short answer named still-image boundary/region appearance.
The subsequent, more specific clarification supersedes a still-image-only reading:

> 빛반사 및 정지 이미지 전, 후 프레임의 움직임으로 판단하였으나 이 시점의 idx0과 idx20은 둘 다 유면이라고 판정해도 될 만큼 사람이 봐도 유사한 수준이었음

The human reader used light-reflection appearance **and movement in preceding and
following frames**, and found idx0/idx20 sufficiently similar in this still image
that either could be judged an interface. Thus this pair is not an established
clear static positive/negative control. The clarification supplies evidence about
rationale and human ambiguity, not a formal replacement identity/path label,
numeric contour, or proof that both candidates represent the same physical owner.
No further demand for a uniquely discriminating static cue is justified here.

Preserve revision-14 labels and historical score outputs unchanged. Attach this
qualification to their interpretation rather than deleting a difficult pair,
changing an evaluation denominator, or relabeling to improve scores. It does not
invalidate all prior negative controls: in particular idx0-versus-idx11 structure
ordering is a separate failure and is not resolved by ambiguity about idx20.
Any future formal label reconsideration requires its own attributed revision and
separately versioned evaluation; none is performed by this report.

### Further direct clarification: ambiguity persists with temporal context

The user then specified the observation and duration: boundary rise/fall together
with apparent interface formation, viewed approximately five seconds before and
five seconds after the still (about ten seconds total). These are approximate
human recollections, not verified extraction timestamps or a newly executed clip.
The reader could not determine whether two apparent layers were actual interfaces
or residual liquid on the glass reflecting light. Both looked like real interfaces.
idx20 had somewhat stronger reflection, which motivated submitting idx0 as the
interface; the reader explicitly noted that actual interfaces can also reflect
strongly and did not reach a certain physical conclusion.

This supersedes the proposed next step of obtaining temporal context to resolve
this particular pair: such context was already used and did not resolve it for the
human reader. Do not ask for the same clip again without a distinct observable
and purpose. Do not infer that temporal evidence never helps elsewhere, that both
candidates are physically identical, or that the software must assign either one
as interface/non-interface. Reflection strength and coherent/formation-like motion
are not established discriminators here.

The next design decision is uncertainty handling under ambiguous reference truth,
reusing existing separated identity/local-path/scalar evaluation owners. Existing
binary labels and historical counts remain reproducibility records with this
explicit qualification, not definitive proof of physical ordering for idx0/idx20.
No silent exclusion, denominator change, label revision, or retrospective success
claim is made. A machine UNRESOLVED output would itself need a supported inference
rule and controls; human uncertainty here is not a hardcoded runtime decision.
No extra human clarification is needed for this rationale. Additional collection
is conditional on a different evidence-bearing question, not a longer scan by
default. No Windows rerun, new labels, production change or broader video search
is requested at this step.

## Local verification

Source inspection only for field ownership and legacy attribution; no runtime or
test code changed and no detector experiments repeated. Documentation links,
S11 governance and whitespace checks cover this evidence/status update.
Private file preservation and image claims remain user-reported as stated above.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-AUTHORITY`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F04`, `S11-F09`, `S11-F10`.
- First harmful stage: transferred report interpretation mixed old human prose with new image observation and misread guide numbers; the detector's physical-identity failure stage remains unknown.
- Logic-map impact: NONE — evidence reconciliation and next-action routing only; no measurement, identity, selection or publication behavior changes.
- Failure-registry impact: NONE — existing geometry/provenance and no-private-truth-shortcut guards are preserved; no new field repair is claimed.
