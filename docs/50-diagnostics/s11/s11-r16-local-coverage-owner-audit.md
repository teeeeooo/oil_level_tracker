# S11-R16 Local Coverage and Owner Audit

## Classification and scope

This diagnostic records the candidate- and tracklet-level reconciliation that
supports the R16 safety-first local contract. It is causal evidence, not a
threshold owner, current milestone status or private-Windows qualification.

The audit used full sequence traces, the four checked-video replay and direct
review already owned by the R13--R15 evidence chain. Production code was not
allowed to use case names, timestamps or truth coordinates. Candidate-level
`minimum_final_confidence` remains unchanged and no sibling confidence is
pooled.

## Independent-audit repair findings

Independent review of candidate head
`178fdf951d7142c39c6a54109cbaece8b204c476` found three lifecycle seams that
invalidated its replay and timing evidence:

- tracklet ambiguity was checked only as many established tracks competing for
  one row. One established track could still split into two near-cost child
  hypotheses and greedily retain its old ID on one child;
- drain release, continuation, successor and phase re-entry used the minimum
  conflict among same-row members even when another current member carried a
  material-path conflict at the veto threshold; and
- phase re-entry enforced an absolute jump but did not reject a new owner that
  reversed materially above the last drain Y.

The repaired tracklet owner now checks ambiguity symmetrically. A split child
belongs to the established parent only when that parent is also the child's
clear predecessor; a genuine near-cost split terminates the parent and assigns
new incompatible child IDs. All four drain transitions apply the complete
current-row material veto, and re-entry applies the ordinary directional
reversal tolerance in addition to the jump bound. Adversarial controls retain
a clearly ranked child and a child with another clear predecessor. The repaired
source/test identity is
`6462a21c327241f9f0e91fe749ed1892abeb0776`.

## Checked-truth coverage is not an owner

The final replay publishes 6 of 13 checked truth rows. Seven rows are
`UNKNOWN`; each is classified by its first evidence seam:

| Case | Truth Y | Same-frame physical evidence | First failing seam | Decision |
|---|---:|---|---|---|
| Base 4.8048 s | 386 | Both annotations map to 5.005 s; admitted row Y392--396, `ANCHOR_TRAJECTORY`, motion/coverage 0.333/0.333 | several admitted physical rows compete; no uniquely stronger owner | `UNKNOWN` |
| Base 5.2052 s | 386 | same 5.005 s sampled row | same physical-owner ambiguity | `UNKNOWN` |
| sample2 0 s | 592 | no eligible row hypothesis | proposal/authority absence | `UNKNOWN` |
| sample2 2 s | 592 | a bounded candidate exists | window-end tracklet has insufficient net progress | `UNKNOWN` |
| sample3 34.5345 s | 243 | row Y243--254, tracklet `0000`, `ANCHOR_TRAJECTORY`, direction `+1`, motion/coverage 0.927/0.867 | foreign opposite-direction row is outside the active fill owner chain | `UNKNOWN` |
| sample4 0 s | 860.5 | no eligible row hypothesis | proposal/authority absence | `UNKNOWN` |
| sample4 49 s | 855 | admitted Y833--834 motion row and Y881 anchor row | `FILLED_CAP_VETO`; neither row is a confirmed phase release from owner `0072` | `UNKNOWN` |

Candidate presence alone was therefore insufficient for a generic recovery.
Base has multiple mature alternatives, sample3 Y243 belongs to a reconciled
foreign branch, and sample4 49 s would require lifting a material barrier into
a branch-hop risk. The two sample2 endpoints and sample4 start require proposal
or observability work, not selector preference.

## Sample3 onset predecessor reconciliation

The prior aggregate R14 assertion rewarded an incorrect upper branch at
Y268/270/280/279. R16 links one immediate predecessor to the later uniquely
activated dynamic owner without merging their physical tracklets:

| Timestamp | Public Y | Physical owner | Phase/reason |
|---:|---:|---|---|
| 30.0300 | 291.5 | `0001` | `OPEN / FILL_ONSET_INTENT_PREDECESSOR` |
| 30.5305 | 296.0 | `0001` | `OPEN / FILL_ONSET_INTENT_PREDECESSOR` |
| 31.0310 | 296.0 | `0001` | `OPEN / FILL_ONSET_INTENT_PREDECESSOR` |
| 31.5315 | 312.0 | `0002` | `FILLING / FILL_MOTION_OWNER` |
| 32.0320--32.5325 | `UNKNOWN` | owner absent | `FILL_MOTION_OWNER` |
| 33.0330--33.5335 | 297.0 / 295.0 | `0002` | `FILL_MOTION_OWNER` |

The owner chain is `0001 -> 0002`. All first four numeric rows are within
26 px of reviewed Y316. The predecessor contributes identity continuity only;
every published coordinate still comes from that exact frame.

At 35.5355 s, successor `0013` is the unique phase handoff but its selector
competition is a genuine near-tie. From 34.0340 through 36.5365 s the lifecycle
therefore abstains whenever the allowed owner is absent or unresolved. At
37.0370 s `FILL_SPAN_MATERIAL_VETO` enters `FILLED_BARRIER`. No Oil is numeric
through the reviewed 39--64 s full/cap interval.

## Why Y243 is not recovered

At 34.5345 s the exact Y243--254 row is admitted, publishable and strong, but
it remains physical tracklet `0000` with downward image direction `+1`.
The active fill owner chain is `0001 -> 0002`; later safe handoff `0013` begins
near Y271. Authorizing `0000` would exchange physical ownership with an
opposite-direction branch merely because it matches a historical truth Y.

The R16 corpus contract therefore requires every numeric onset row to keep
same-frame provenance and requires explicit `UNKNOWN` for 34--39 s. This is a
safety assertion, not a relaxed count target.

## Drain owner audit

The repaired sample3 replay publishes six evidence-safe rows in
`90 <= t < 103`; there are no further numeric rows at or after 97 s:

| Timestamp | Public Y | Physical row | Direction / progress | Track conflict / current minimum / row veto | Publication lifecycle |
|---:|---:|---|---|---|---|
| 91.5248 | 320.0 | `0104 / 123:003` | `+1 / 14 px` | `0.164 / 0.188 / false` | witness |
| 92.5258 | 320.0 | `0104 / 125:002` | `+1 / 14 px` | clean / `0.183 / false` | witness |
| 93.0263 | 333.0 | `0104 / 126:003` | `+1 / 14 px` | clean / `0.120 / false` | confirmed |
| 94.0273 | 336.0 | `0105 / 128:006` | `+1 / 50 px` | `0.312 / 0.156 / false` | confirmed handoff |
| 95.0283 | 345.0 | `0105` | downward continuation | material-clean row | continuing |
| 96.5298 | 342.0 | `0105` | `3 px` bounded jitter | material-clean row | continuing |

This is one reviewed 81--96 s physical sequence, not six independent coverage
exceptions. It starts at Y233 at 81.0143 s, reaches Y288 at 88.0213 s and then
continues through the rows above. Net downward-image progress exceeds 105 px,
numeric gaps stay within 3.51 s and the only allowed local reversal is the
ordinary 3.1 px handoff jitter. Each public Y is one publishable member of its
same-frame physical row.

The audit also explains the censored alternatives. At 96.0293 s the owner row
has current material conflict `0.536`; at 97.0303 s the only drain-like row has
track conflict `0.506`. The old 100.5338 s Y315 result was a new track within
the absolute 32 px jump from prior Y346, but it reversed upward by 31 px and is
now rejected by the normal 2.88 px reversal tolerance. The old 102.5358 s point
depended on that unsafe re-entry. Thus 96.0293 s and every frame from 97 s to
the window end are `UNKNOWN`; the unrelated upper branch, current-row material
conflicts and backwards re-entry cannot reset or inherit drain ownership.

## Commit-horizon counterexample

Tracklet witness confirmation and phase onset intent compose. A synthetic
track first appears at frame 3 but reaches `MOTION_TRAJECTORY` only with frame
7. A prefix ending at target `t+6` therefore differs from the extended result
at target phase reason/owner metadata. Six frames is a stage window, not an
end-to-end commitment.

The repository-owned property sets the exact end-to-end horizon to 11 sampled
frames: six frames for selector/onset influence plus five additional future
frames for a six-frame confirmation window. The adversarial regression proves
that the target is stable after `t+11`, including Y, tracklet ID, phase, reason
and owner chain.

## Reproducibility pointers

- exact-clean-head four-video manifest:
  `/var/folders/s2/wbnr4dhn1z1bk7tcl342s8bw0000gn/T/r16-audit-repair-four-final.fdf1y2xl/replay_manifest.json`;
- candidate-level FULL trace used during the repair:
  `/tmp/r16-drain-veto-audit.oI75nm/oil-debug-trace-s52awykr/debug_trace.jsonl`;
- composed-lag regression:
  `tests/unit/test_oil_interface_tracklets.py`;
- evidence-specific corpus contracts:
  `tests/test_s11_temporal_reacquisition_continuity.py` and
  `tests/test_s11_sequence_observability_integrity.py`.

The temporary artifacts are local reproducibility outputs and are not
repository truth. The candidate trace predates the final directional re-entry
censor and records its causal input; final public behavior is established by
the exact-clean-head manifest and corpus regression. Counts, fingerprints and
assertions are repeated in the R16 validation evidence record so the acceptance
contract does not depend on temporary-file retention.
See [R16 local evidence](../../60-evidence/s11/s11-r16-directed-tracklet-material-lifecycle.md).
