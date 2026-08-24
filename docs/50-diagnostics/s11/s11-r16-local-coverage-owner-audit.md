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

The final sample3 replay publishes seven evidence-safe rows in
`90 <= t < 103` and ten rows from 90 s through the 105 s window:

| Timestamp | Y | Phase reason |
|---:|---:|---|
| 95.0283 | 345.0 | `DRAIN_PHASE_REENTRY` |
| 96.0293 | 359.0 | `DRAIN_OWNER_CONTINUING` |
| 96.5298 | 359.0 | `DRAIN_OWNER_CONTINUING` |
| 97.0303 | 368.0 | `DRAIN_OWNER_CONTINUING` |
| 97.5308 | 368.5 | `DRAIN_OWNER_CONTINUING` |
| 100.0333 | 368.0 | `DRAIN_PHASE_REENTRY` |
| 102.5358 | 335.0 | `DRAIN_PHASE_REENTRY` |

The reviewed 97 s counterexample now keeps lower owner `0105` at Y368/368.5;
the unrelated upper Y226 branch cannot win. Frames 90.0233--94.5278 remain
`UNKNOWN` after the prior owner terminates. Frame 95.5288 is a bounded owner
loss. Frames 98.0313--99.5328 and 100.5338--102.0353 remain `UNKNOWN` where
current material compatibility or unique re-entry evidence fails. Direction,
jump and material conflicts are not overridden to increase the count.

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

- four-video manifest:
  `/tmp/r16-post-lag-four-video.OMSSpf/replay_manifest.json`;
- final sample3 FULL trace:
  `/tmp/r16-final-s3-debug.nsi4W7/run-01/`;
- composed-lag regression:
  `tests/unit/test_oil_interface_tracklets.py`;
- evidence-specific corpus contracts:
  `tests/test_s11_temporal_reacquisition_continuity.py` and
  `tests/test_s11_sequence_observability_integrity.py`.

The `/tmp` artifacts are local reproducibility outputs and are not repository
truth. Counts, fingerprints and assertions are repeated in the R16 validation
evidence record so the acceptance contract does not depend on their retention.
See [R16 local evidence](../../60-evidence/s11/s11-r16-directed-tracklet-material-lifecycle.md).
