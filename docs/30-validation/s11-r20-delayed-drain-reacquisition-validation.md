# S11-R20 Delayed Drain Reacquisition Validation

**Status:** `LOCAL PASS / WINDOWS REQUIRED`

This contract validates the
[R20 delayed drain reacquisition architecture](../20-architecture/s11-r20-delayed-drain-reacquisition-architecture.md).
R20 is locally accepted only if it recovers a delayed, fragmented partial-fill
release without weakening R18/R19 safety, identity, ambiguity, provenance or
Foam contracts.

## Focused lifecycle contracts

Positive cases must establish an initial-EMPTY upward fill owner, lose it
before DRAINING, remain UNKNOWN through `maximum_lost_frames + 1` grace, and
then provide a unique fresh anchor outside the retained snapshot jump. The
first fresh anchor starts one attempt; later same-owner continuation and clear
cross-ID anchor handoff use existing R19 bounds; cumulative progress and
directional agreement confirm exactly one current owner; and only that current
same-frame row becomes DRAINING/selectable. Sparse anchors, arbitrarily long
evidence-free ownerless intervals and post-confirmation drain continuation are
required controls. Barrier state and active attempt remain constant-size.

Near-snapshot R19 recovery and direct partial-fill release must remain
byte-equivalent in phase, reason, owner, publication and diagnostics source.
Direct always wins, near-snapshot remains second, and delayed is third.

## Negative and two-sided controls

The following remain UNKNOWN/no-interface and cannot enter DRAINING:

- no established fill, changed context, dynamic fill reappearance or seed
  during ordinary grace;
- continuation-only, candidate-only, provisional, incompatible,
  phase-identity-invalid, material-opposed, motion-only, recurring-Y-only or
  stale-snapshot-only seed;
- stationary lower structure, moving residue/glare or absent strict material
  support;
- upward/reversed, insufficient-progress, excessive-step, excessive-gap,
  stagnating or absolute-window-expired chains;
- duplicate same-owner hypotheses, one-to-many/many-to-one handoff,
  competing physical owners or multiple qualifying chains; and
- any coordinate/ID reuse, interpolation, carry or retrospective backfill.

An ambiguity involving the first delayed qualifying anchor consumes the one
attempt and cannot reseed within the same episode. After any failed/expired
attempt, a new attempt requires a newly established fill episode. Initial FULL
lower-structure safety and initial EMPTY false structures remain rejected.

## Diagnostics and provenance

Each sampled lifecycle diagnostic records R20 version, ownerless-barrier state,
loss epoch/age/grace, established episode/snapshot provenance, snapshot
distance as non-authoritative telemetry, attempt consumption/state, direct/
near/delayed ordering and source, delayed ordered seed predicates and first
failure, active chains, progress/agreement, expiry/reset/ambiguity, qualifying
and selected IDs, lifecycle allowed IDs and existing selector/projection
provenance. Diagnostics cannot change candidate scores, assignment order,
phase, selection or publication.

For every numeric Oil row, assert exactly one selected nested same-frame
candidate, selected Y equals completed-sequence raw Y and CSV raw Y, and no
snapshot/seed coordinate appears on missing frames. UNKNOWN rows retain empty
numeric fields. Foam candidate/identity/episode/composition/publication output
remains identical to the R19 fixture unless a separate design is authorized.

## Integration and resource gates

Run focused lifecycle, authority, tracklet, selector, resolver,
sequence/composition, trace, detection-coordinator, publication and Foam tests;
exact four-video replay in fresh output roots without golden regeneration;
same-frame sequence/CSV provenance checks; controlled performance and bounded
active-context/chain checks; full repository tests; Qt partition; compileall;
changed-document link checks; `git diff --check`; scoped diff review; and:

```text
python3 scripts/check_detector_governance.py --base-ref e3a014f7542654b5e63353a173b8b038be34e2bf --include-worktree
```

Unexpected checked-fixture output changes require source-image review and a
separate disposition. Local success is exactly `LOCAL PASS / WINDOWS REQUIRED`;
it is never field PASS.

## Canonical Windows gate

After the authorized push, replay `windows_sample1_heating_coldstart` and
compare all 1,202 rows and nine reviewed-truth segments against R19/R18. The
field report must separate ownerless-barrier grace, one-attempt consumption,
direct/near/delayed funnel counts, Accum seed authority/phase/material,
chain/ambiguity/selection/provenance, residue controls and Base
`NOT_PROVEN` safety behavior. Foam must remain identical and selected,
sequence and CSV Y mismatch must remain zero. Coverage alone is not success;
without separately reviewed Y anchors the field result remains unqualified.

## History Review / Detector Governance

- Logic-map nodes: `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`,
  `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`,
  `PUBLICATION-PROVENANCE`, `TRACE-PUBLICATION`.
- Failure-registry entries: `S11-F02`, `S11-F04`, `S11-F05`, `S11-F08`,
  `S11-F09`, `S11-F10`.
- Preserved guards: no private identity/coordinate/time/video branch, no
  global threshold relaxation, no motion-only authority, no ID merge, no
  selector/projection repair, no interpolation/carry, ambiguity/material
  fail-closed behavior, exact same-frame provenance and Foam independence.
- R20 evidence disposition: local synthetic and regression evidence is
  implementation evidence; canonical Windows replay remains mandatory and is
  not represented by this local contract.
- Failure-registry impact: `NONE`; existing failure classes remain the durable
  causal authority.
