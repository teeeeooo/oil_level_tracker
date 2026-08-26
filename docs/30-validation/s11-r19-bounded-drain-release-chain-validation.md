# S11-R19 Bounded Drain-Release Chain Validation

**Status:** `LOCAL PASS / WINDOWS REQUIRED`

This contract validates the
[R19 architecture](../20-architecture/s11-r19-bounded-drain-release-chain-architecture.md).
R19 is accepted locally only if it recovers a fragmented, physically
continuous drain release without weakening R18's initial-state, material,
identity, ambiguity, Foam or publication contracts.

## Focused positive contracts

### Initial FULL

Construct independently confirmed anchor-authoritative rows whose physical
tracklet IDs fragment, whose individual R18 release evaluations do not have
sufficient downward progress, and whose same-frame Y observations form one
unique top-origin downward chain.

Verify:

- the direct release path remains unqualified;
- the recovery chain starts only from an entrance-relative row;
- ordinary bounded same-ID continuation and clear cross-ID handoff accumulate
  source-Y progress without merging tracklet IDs;
- the chain remains nonnumeric until cumulative progress and directional
  agreement meet the existing drain contract;
- the unique current row becomes the sole `DRAINING` owner on confirmation;
- the owner chain contains distinct observed IDs in order; and
- no earlier frame is rewritten or backfilled.

### Established partial fill

Create a real initial-EMPTY lower-entry fill owner, retain its established-fill
snapshot, then provide fragmented anchor-authoritative rows beginning within
one ordinary jump of that snapshot and descending through multiple ordinary
hops whose total distance exceeds one jump.

Verify:

- the existing direct partial release remains unqualified;
- recovery seeds from the retained fill Y only after the dynamic fill owner is
  absent;
- each adjacent hop satisfies the existing jump and reversal limits;
- cumulative chain progress, not copied fill or tracklet progress, confirms;
- the current physical row becomes the sole drain owner; and
- existing drain continuation/handoff owns every later frame.

## Focused negative contracts

The following cases must remain UNKNOWN/no-interface and must not enter
`DRAINING`:

1. initial FULL rows whose entrance-relative position is outside the existing
   drain entrance band, including a strong moving lower structure;
2. initial EMPTY with no established fill;
3. provisional, incompatible, material-opposed, non-anchor-authoritative seed
   rows, or non-anchor-authoritative cross-tracklet handoffs;
4. upward or stationary chains that never reach positive minimum progress;
5. a single jump larger than `maximum_jump_px * gap`;
6. an upward reversal beyond the existing handoff tolerance;
7. a gap beyond `maximum_lost_frames + 1`;
8. a continuously observed but nonprogressing seed after
   `fill_evidence_window_frames`;
9. an always-slowly-progressing chain that exceeds the total
   `fill_evidence_window_frames` span before reaching the drain minimum;
10. one predecessor with two equivalent successors, two predecessors for one
   successor, duplicate eligible seed hypotheses for one physical owner, or
   two simultaneously qualifying recovery chains; every such recovery
   ambiguity keeps the entire current frame UNKNOWN/no-interface;
11. a partial-fill row outside the one-jump seed bound from the retained fill;
12. any attempt to reuse a prior coordinate after a gap; and
13. any attempt to mark a recovery chain as a physical tracklet or merge IDs.

An active partial-fill chain must also reset when the retained established-fill
owner, owner-chain, last frame/Y anchor context or release stage changes; it
may not accumulate evidence across a changed fill snapshot.

## Existing direct-path non-regression

Retain all R18 tests proving:

- one direct initial-FULL release works without recovery;
- one direct partial-fill release works without recovery;
- direct ambiguity fails closed;
- completed-fill, owner-at-entrance and initial-EMPTY safety behavior remains;
- drain continuation, successor handoff, loss and re-entry remain bounded; and
- material conflict cannot release a barrier.

Focused assertions must show direct release has priority and produces the same
phase, reason, allowed owner and publication as R18.

## Diagnostic contract

For every sampled frame, assert the R19 lifecycle diagnostic records the
recovery stage, active-chain state, ordered predicates, qualifying/selected
IDs, ambiguity/reset outcome and direct-versus-recovery source.

Diagnostic tests must distinguish:

- no recovery rows from a function that was not reached;
- evaluated chains with zero qualifiers;
- a chain reset for loss, stagnation, material opposition or ambiguity;
- direct release from recovery release; and
- phase owner-chain provenance from physical tracklet identity.

Existing R18 release-evaluation fields retain their prior meaning. The new
diagnostics may not affect candidate scores, assignment order, phase decisions
or publication other than the explicitly designed recovery transition.

## Same-frame publication and compatibility

For every R19 numeric Oil row:

1. exactly one selected nested same-frame Oil candidate exists;
2. the selected candidate tracklet equals the allowed current owner;
3. selected candidate Y equals sequence raw Y and CSV raw Y;
4. no prior chain coordinate appears on an unobserved frame; and
5. UNKNOWN stays invalid and numeric fields stay empty.

Recipe schema, old bundle readers and result graph semantics remain unchanged.
Foam candidates, episode decisions and publications must be behavior-identical
to R18 on the compared local fixtures because Foam is outside R19.

## Local replay and regression gates

Run, in order:

1. focused lifecycle and selector unit tests;
2. Oil observation resolver and sequence-composition tests;
3. Foam episode and Foam integration tests as non-regression;
4. exact four-video checked replay and its audit assertions;
5. same-frame sequence/CSV provenance tests;
6. controlled detector benchmarks and the accepted resolver performance gate;
7. full repository tests;
8. Python compilation;
9. detector governance; and
10. `git diff --check` plus scoped diff review.

No golden fingerprint is regenerated automatically. Any changed local replay
result requires source-image review and a separate evidence disposition.

## Canonical Windows field gate

After local acceptance, run the canonical
`windows_sample1_heating_coldstart` recipe and compare all 1,202 same-frame
rows against the frozen R18 causal bundle.

The R19 field report must enumerate all nine reviewed-truth segments and the
new release-chain diagnostics. At minimum it must establish:

- Base FULL-prefix and FULL-suffix remain numeric-Oil absent;
- Base DRAIN gains a unique physical release chain or remains safely absent;
- a lower `Y > 800` structure never seeds or confirms recovery;
- Base rapid refill closes without numeric Oil in the following FULL segment;
- Accum EMPTY remains Oil/Foam absent;
- Accum entry is not regressed;
- Accum DRAIN gains a unique stepwise release chain or remains safely absent;
- no wall residue becomes the recovery owner;
- Foam outputs are same-frame identical to R18 unless a separately designed
  Foam change is later authorized; and
- selected candidate, sequence and CSV equality has zero mismatch.

Coverage alone is not success. If a new numeric row cannot be traced to one
selected current candidate and one unique recovery chain, the field gate
fails. If no safe chain exists, the result remains field-failed but the design
must stay fail-closed rather than widening a gate.

## Stop conditions

Stop and reject R19 if implementation requires a new field-tuned threshold,
source/video identity, coordinate exception, motion-only seed, unbounded path,
physical-ID merge, retrospective coordinate, weakened initial-EMPTY gate,
lower-structure admission, Foam behavior change or provenance mismatch.

Local success is `LOCAL PASS / WINDOWS REQUIRED`, never field PASS.
