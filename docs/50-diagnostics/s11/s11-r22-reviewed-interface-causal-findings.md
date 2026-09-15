# R22 Reviewed Interface Causal Findings

## Evidence boundary

This investigation combines operator-transferred Windows reports and direct
user review of guide images with local source inspection at
`706f398c0684cc2a68ecfa250729caa9a7b8927e`. The private media and full trace were
not inspected on this host. A resolver version string identifies the reported
run as R22 but does not establish that its source is byte-identical to this
checkout. No raw media, private paths or business identifiers are included.

The [canonical reviewed truth](../../30-validation/windows-sample1-heating-coldstart-reviewed-truth.md)
continues to own interval acceptance. The following human-reviewed checkpoints
supplement its approximate intervals; they do not redefine an entire interval.
All Y values below are source-frame coordinates, positive downward. Pixel
coordinates supplied by guide-image review remain approximate physical anchors,
even when a candidate has an exact fractional coordinate.

## Confirmed transferred observations

| Checkpoint | User-reviewed physical boundary | Trace observation | Supported failure boundary |
|---|---|---|---|
| Accum source frame 16280 | Near Y=213 | Y=213 calibrated candidate belongs to tracklet `000388:0186`, admitted, continuation-only; allowed owner remains `000381:0181` | Actual-boundary candidate exists; phase allowed-set excludes its tracklet before selector scoring |
| BASE source frame 14362 | Near Y=412.5 | Tracklet `000234:0207` observes material-path Y=438 | This member is not the reviewed Oil boundary |
| BASE source frame 14374 | Near Y=412.5 | The same tracklet observes material-path Y=412.5 | False-to-real association creates an apparent 25.5 px upward movement |
| BASE source frame 14386 | Near Y=411.5 | Same tracklet, material-path Y=411.5, anchor-eligible, admitted, direct interface | Direct initial-FULL release fails only `downward_direction`; progress 26.5 exceeds minimum 19.305 |

BASE frames use the trace crop origin `(0, 211)`, size `578 x 773`, without
resize. Accum frame 16280 was re-extracted using its exact zero-based source
index; its reviewed crop origin Y is 32. Internal resolver frame offsets must
not be substituted for source indices.

### Accum authority and independent support

The frame-16280 Y=213 candidate has initial, post-track and final authority
`CONTINUATION_ELIGIBLE`, `ordered_lower=1`, `cross_representation_support=0`,
no typed identity contradiction and no track opposition. Its failed authority
gates mention texture conflict and independent/cross-representation support.
There is no observed authority demotion between those three recorded stages.

A same-frame material-path peer at Y=217 exists in both candidate collections.
Its raw candidate is eligible and not rejected, but its sequence entry has no
tracklet and the coarse `TOP_K_PRUNED_OR_HARD_INVALID` reason. Its raw row
support is `0.8055925369262695`, terminal partition support
`0.6902692373842001`, and texture conflict `0.6665736003996448`.

Current source computes `row_support * (1 - 0.25 * terminal_support)`, then
excludes peers with conflict at least 0.60 from cross-representation support.
Those transferred values reproduce the reported conflict. Even terminal
support 1 would leave this row's conflict above 0.60. This establishes a
specific peer exclusion, not proof that this peer alone should grant authority.
Source-family count and Y proximity do not establish independent identity.

The actual-boundary tracklet has a phase-admitted, publishable witness row, but
is absent from the allowed set. Current `_constrain_layer` enforces that set
before scoring. The current temporary fill handoff also requires an
anchor-eligible material-path member; a calibrated anchor alone is insufficient.
These are separate seams, so fixing cross support alone is not a demonstrated
end-to-end repair.

### BASE recovery is a separate failure path

Tracklet `000269:0239` has two separate recovery lifecycles. Both have a recorded
lease renewal. At the 646.0204 to 646.4792 transition, candidates remain, but
tracklet admission changes to false with `CONTINUATION_EVIDENCE_EXPIRED`.
The chain's observation count and last observation then stop advancing.
The chain later disappears alongside a common `loss_window_expired` diagnostic;
the common field is not proven to identify this chain specifically.

This proves that admission can stop observations while the recovery lease
remains live. It does not establish this tracklet's physical identity or justify
extending its admission lifetime. It is distinct from tracklet `000234:0207`.

## Local mechanism checks and limits

Local read-only probes reported during this investigation found:

- With both nearby synthetic lower-interface representations carrying high
  texture conflict, independent support can collapse for both. A layered
  resolver fixture changed from eight numeric rows to none when both lower
  peers were changed to conflict 0.67; either peer alone remained sufficient
  in that fixture. This is a mechanism control, not a private-video replay.
- A lifecycle helper admitted a temporary material anchor handoff, while a
  non-material anchor or material continuation control left the old allowed
  owner. Other helper attributes were held fixed.
- A synthetic material-path sequence `130, absent, absent, 130, 104.5, 103.5,
  103` remains one tracklet and reports recent progress 26.5 at the penultimate
  observation. A jump greater than the configured 32 px bound splits the
  corresponding control. Existing seven focused tracklet tests passed in the
  latest read-only review. These probes do not reconstruct the Windows
  candidate competitors, image evidence or exact assignment cost.

Current track matching allows compatible representation classes within the
jump/prediction bounds without invoking its representation bridge. The class
is only direct versus ordered-lower. A shared class is therefore insufficient
to demonstrate that two image structures are one physical interface. The
transferred false-to-real association and the local control support reviewing
this seam; they do not prove that every bounded jump is wrong.

Splitting the false BASE predecessor removes the fabricated upward progress.
It does not create downward evidence: the reviewed real boundary is nearly
stationary across these frames. Association repair alone cannot be claimed to
satisfy the existing initial-FULL release contract.

## Superseded interpretations and unresolved scope

- BASE frame 14386 has an actual-boundary candidate; the earlier LVLM range
  Y=435--455 and candidate-absence conclusion are withdrawn. Its source is
  `material_path`, not the earlier reported calibrated source.
- Accum frame 16280 uses the human-reviewed Y=213, not LVLM Y=137 or 123.
  Rejected candidates must remain in nearest-candidate inventories. The earlier
  assertion that there were no candidates near the true interface is withdrawn.
- BASE lease renewal did occur. A universal minimum-progress diagnosis does
  not describe the frame-14386 candidate.
- BASE frame 550 s, Accum frame 678.51 s and other earlier LVLM-only coordinates
  are not upgraded to human-reviewed truth by these corrections. No claim of
  continuous visibility throughout a long gap follows from sparse checkpoints.
- BASE 638--652 s opacity was reported by the Windows agent, not established
  here by a new human review. Do not silently rewrite canonical interval truth.
- Accum entry delay, the full later gap, post-724 s loss, and false/true identity
  across the complete drain remain unresolved. Increased numeric coverage is
  not evidence of increased accuracy.

The [proposed repair design](../../20-architecture/s11-physical-interface-evidence-repair-design.md)
uses these findings without encoding private timestamps, Y values or Glass IDs.

## Detector Governance

- Logic-map nodes: `FRAME-EVIDENCE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F08`, `S11-F09`, `S11-F10`.
- First harmful stage: BASE reviewed false-to-real association is at OIL-TRACKLET; Accum actual-boundary owner exclusion is observed at phase-to-selector admission, with a separately supported upstream cross-representation peer exclusion. Exact private-run branch causality beyond these facts is not established.
- Logic-map impact: NONE — this records evidence and current-source checks without changing executing behavior.
- Failure-registry impact: NONE — these are bounded instances of the existing identity, material, initial-state and provenance failure classes, not a rewrite of historical field results.
