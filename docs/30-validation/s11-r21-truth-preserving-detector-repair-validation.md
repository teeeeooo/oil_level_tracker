# S11-R21 Truth-Preserving Detector Repair Validation

**Status:** `LOCAL VALIDATION COMPLETE / WINDOWS REQUIRED`

This specification validates the
[R21 architecture](../20-architecture/s11-r21-truth-preserving-detector-repair-architecture.md)
against source base `d50c14300b6e0d5be6c03c4487d96c4032fa7857`.
It preserves the checked-in reviewed truth and does not promote local synthetic
controls into field truth.

## A — tracklet semantic separation

Required regressions must prove that:

- established `tracklet_direction/progress/agreement` remain the original
  confirmation-witness semantics;
- a mature bounded recent window can independently report a real reversal;
- fixed-lag retro-admitted observations fall back to their confirmed witness
  until a recent window has enough observations; and
- the additive recent fields do not alter row identity, candidate authority,
  ordinary continuation/handoff or selector semantics.

The existing composed `t+11` end-to-end commitment and branch/split tests remain
mandatory.

## B — Base initial-FULL cycle

A full-raster integration must run through current-frame candidate generation
and completed sequence resolution with confirmed initial `FULL`:

`FULL -> slow downward-image drain -> rapid topward refill -> FULL`.

Acceptance requires:

- no numeric Oil during the initial no-interface prefix;
- sustained numeric same-frame Oil through the drain;
- an R20-scale lifecycle case using effective height `772.2137404580153 px`
  and release minimum `19.305343511450385 px`, where individual 10 px
  tracklet witnesses remain below threshold but the unchanged bounded recovery
  chain earns release from cumulative 2 px/sample progress;
- fail-closed abstention on an insufficient first reversal witness;
- same-owner refill closure when identity survives the reversal; and
- a high-speed full-raster case whose first refill jump exceeds the ordinary
  32 px tracklet bound, forms a distinct fresh tracklet, and closes only after
  that owner is independently confirmed with reason
  `DRAIN_REFILL_HANDOFF_CONFIRMED`;
- fresh-owner closure is unavailable while the old drain owner still has any
  current-frame row, even when that row cannot continue downward; an unrelated
  upper owner must not steal the active drain phase;
- distinct old/new tracklet IDs in a permitted phase handoff, one same-frame
  closing candidate, `FILLED_BARRIER`, and no numeric carry in the following
  suffix;
- duplicate qualifying refill owners remain ambiguous and ordinary lower drain
  re-entry remains unchanged; and
- no change to material-conflict, entrance, authority or global candidate
  thresholds.

Existing adversarial controls must still prove that material-conflicted or
strong-motion-only rows cannot release the filled barrier.

## C — Foam truth preservation

The Sample3 reviewed oracle is unchanged: the first accepted Foam observation
must be no later than `30.60 s`. Do not move that oracle to the later 37 s
formation merely to match an implementation.

Stable-layer unit acceptance requires two dynamic rows plus one bounded
same-layer extent-changing row to confirm when all outer segment gates pass.
The existing exactly-two substantial footprint exception remains. Negative
controls must continue rejecting static top rows, descending residue, stale
preludes, one-motion spikes, narrow two-frame residue, insufficient material,
Oil alias and expired gaps.

Every witness remains bounded to at most four frame offsets and 2.0 source
seconds; no whole-track future support is permitted.

## D — initial-EMPTY controlled continuity

A full-raster initial-`EMPTY` control must prove a slow lower-entry rise with an
explicit unavailable frame. The unavailable frame remains nonnumeric; the
immediately preceding and following real observations remain numeric, later
fresh observations complete the fill barrier, and every numeric row retains
same-frame selected-candidate equality.

No production relaxation is required for a faster synthetic sequence that
creates multiple physical hypotheses; ambiguity must remain fail-closed.

## E — additive decision-witness observability

Oil witness acceptance requires one bounded per-frame join of existing refs,
phase/publishable layer membership, allowed owner IDs, final selected member and
already-computed direct/recovery/delayed evaluations. Predicate booleans are
serialized as explicit `true`/`false`; an unvisited branch is
`NOT_EVALUATED`, and a genuinely missing legacy/schema field is `UNAVAILABLE`.
The witness must not call detector predicates, confidence formulas or selector
logic a second time.

Foam witness acceptance requires the existing bounded episode diagnostics to
be serialized with candidate/track identity, local window bounds, formation
branch/predicates, Oil alias and final confirmation outcome. Per-frame window
records are capped at eight with explicit truncation. The nested schema is
`r21-decision-witness-v1` and must survive the normal sequence JSONL annotation.
Recent trajectory fields must also remain visible in the final candidate trace.

Authoritative detector outputs are unchanged by this observability surface:
selected Oil/Foam Y, phase, owner IDs, events, CSV, cardinality and ordering
remain the outputs of their existing owners. Trace data is never an authority
or coordinate source.

## F — checked-video and publication non-regression

The existing Sample3 owner/barrier/drain oracle must pass unchanged apart from
the restoration of its original early-Foam requirement. In particular:

- the first four onset rows remain numeric and within the reviewed tolerance;
- the 34.5345 s reviewed handoff remains preserved;
- no numeric Oil appears in the 37–81 s filled barrier;
- the reviewed 81–96 s drain ownership/handoffs remain intact;
- the conflict/reversal suffix remains UNKNOWN; and
- every numeric Oil/Foam result preserves exact same-frame provenance.

The four-video corpus, controlled benchmark fingerprints and package/runtime
identity must be checked on the final clean candidate head. Any unexpected
output delta requires source-image reconciliation before promotion.

## Required local commands

```text
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest -q tests/unit/test_oil_interface_tracklets.py tests/unit/test_oil_phase_lifecycle.py tests/unit/test_oil_observation_resolver.py tests/unit/test_foam_episode_resolver.py tests/test_s11_behavioral_repairs_integration.py
.venv/bin/python -m pytest -q tests/test_s11_sequence_observability_integrity.py
.venv/bin/python -m pytest -q
python3 scripts/check_detector_governance.py --base-ref d50c14300b6e0d5be6c03c4487d96c4032fa7857 --include-worktree
git diff --check
```

Run the supported headless Qt partition, relative-document link check and the
repository four-video replay/performance workflow before final local closure.
