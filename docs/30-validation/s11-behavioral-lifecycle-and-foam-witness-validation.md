# S11 Behavioral Lifecycle and Foam Witness Validation

**Status:** `LOCAL ACCEPTANCE COMPLETE / WINDOWS REQUIRED`

This is the active work and acceptance specification for the
[behavioral lifecycle and Foam witness architecture](../20-architecture/s11-behavioral-lifecycle-and-foam-witness-architecture.md).
The comparison baseline is the clean source head
`119f218f2cf232e90f8e591e28feaab54f6fb42f`; no R19 investigation head and no
forced revision identifier may be substituted.

The completed local execution, independent repair audit and final Sol review
are recorded in the [behavioral lifecycle and Foam witness evidence](../60-evidence/s11/s11-behavioral-lifecycle-and-foam-witness.md).

Local evidence may establish a generic behavioral improvement and preserve
the accepted contracts. It cannot declare the reported Windows field failure
repaired. A future Windows qualification must replay the canonical source and
reviewed truth separately.

## Acceptance gates

### A — delayed drain readiness

The baseline-vs-new witness must establish a real initial-`EMPTY` fill owner,
lose it, pass ordinary grace and present a material-clean independently
identified upward anchor outside snapshot reach. The baseline must consume its
one delayed attempt on that non-draining anchor and never release. The new
implementation must leave the attempt available and publish nothing. A later
distinct clean downward anchor, followed by bounded same-owner and/or
reciprocal handoff observations, must consume the attempt and enter
`DRAINING` only on its qualifying current row, with unchanged release progress
requirements.

Required A controls:

- zero, stationary and upward/not-ready anchors leave the attempt available;
- positive direction with insufficient final chain progress may seed but cannot
  release until the unchanged chain threshold is reached;
- ready seed followed by reversal, material conflict, ambiguity, excessive
  gap/jump, stagnation or expiry consumes/fails permanently for that episode;
- duplicate ready anchors remain consuming ambiguity, while two non-ready
  anchors do not create ambiguity or consumption;
- no established fill, initial `FULL`, grace-period seed, candidate-only,
  continuation-only, provisional, unknown, incompatible, stale-snapshot-only
  or material-opposed row qualifies; and
- direct and near-snapshot success and precedence are unchanged.

Diagnostics must show the same shared readiness predicate used by actual
admission, including direction, directional agreement and positive progress.
Earlier gaps remain nonnumeric and IDs remain distinct.

### B — bounded Foam witness authority

The baseline-vs-new witness must use a long dynamic constant-front/no-extent
prelude followed by a genuine rising suffix. The baseline whole-segment
evaluation must confirm the prelude; the new resolver must leave rows beyond
the local suffix influence unconfirmed while the local rising suffix publishes.
Every evaluated witness must be within inclusive `<=4` frame offsets and
`<=2.0` source seconds. Appending or changing evidence beyond that future
horizon must not change an earlier frame's confirmation or selected Y.

The stable-layer witness must contain two narrow dynamic observations followed
by a static extent-changing third row. The old total-row shortcut must accept;
the new dynamic-support count must reject. Positive controls must include a
true three-dynamic stable layer, the substantial two-dynamic footprint
exception, upward formation with bounded sparse gaps and long sustained upward
formation through overlapping windows.

Required B controls:

- static top row, downward residue, exposure-only/single-motion spike,
  insufficient material/coherence, final same-frame Oil alias, ineligible raw
  candidate, missing coordinate and expired gap remain rejected;
- Foam with Oil unknown remains independently publishable, and Foam-only
  metamorphic changes do not alter Oil fields or path decisions;
- a passing non-aliased window confirms only its own same-frame members and
  cannot authorize an aliased or distant window through track ID;
- dynamic stable support counts only rows satisfying
  `min(internal_motion, dynamic_support) >= 0.15`; exactly-two exception rows
  must both be dynamic and meet the existing area/width footprint; and
- overlapping passing windows count as one maximal connected accepted-support
  episode per associated track, with deduplicated frame IDs and missing frames
  still absent.

## Integration and provenance gates

The A positive witness must use real `BoundaryCandidate` construction and the
completed sequence path, not only hand-built private lifecycle references. The
integration must trace selected candidate Y through sequence resolution,
`TrackingSample` and CSV, asserting exact raw-Y equality for every new numeric
row, one selected same-frame candidate and no snapshot/carry/interpolation.
Composition must continue to resolve Oil first and Foam independently; trace
diagnostics remain non-authoritative.

Run the existing four-video corpus with the checked-in recipes and reviewed
truth in fresh output roots, without regenerating goldens. Report all 13 truth
cases, coverage, MAE and maximum error; include sample3 completed-fill and
late-drain gates, sample4 range and same-frame provenance. Compare only with
the current baseline. Inspect source images for every unexpected output delta;
unchanged corpus output is acceptable only with the decisive synthetic and
integration improvements above.

## Required validation commands

Record exact commands, logs, exit status, environment and artifact paths in
the external implementation card. At minimum run:

```text
python3 -m pytest -q tests/unit/test_oil_phase_lifecycle.py tests/unit/test_foam_episode_resolver.py
python3 -m pytest -q tests/unit/test_oil_interface_tracklets.py tests/unit/test_oil_observation_resolver.py tests/unit/test_oil_candidate_authority.py tests/test_detection_run_coordinator.py tests/unit/test_foam_phase_detector_integration.py tests/test_oil_detector_integration.py
python3 -m pytest -q
python3 -m compileall -q src tests
git diff --check
python3 scripts/check_detector_governance.py --base-ref 119f218f2cf232e90f8e591e28feaab54f6fb42f --include-worktree
```

Run the relevant Qt partition in the repository's supported headless mode,
the exact four-video corpus recipe, link checks and a scoped diff review. Any
regression, missing positive witness, provenance mismatch or unsafe assertion
relaxation is `NEEDS_SOL`; do not tune the horizon or thresholds to private
timestamps.

## Deferred and field boundary

Base release and rapid refill, Accum initial entry/fill continuity/layered
behavior and strict drain continuation/re-entry remain individually deferred
until their missing physical candidate/identity evidence and transition
contracts are available. This work does not lower global thresholds, invent
coordinates, reopen the Windows investigation, compare against R19, regenerate
goldens or claim Windows PASS. The optional decision-witness package remains
separate retained design-only work.

## History Review

- Logic-map nodes: `OIL-CANDIDATE`, `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`, `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-SELECTOR`, `OIL-PROJECTION`, `FOAM-CANDIDATE`, `FOAM-IDENTITY`, `FOAM-EPISODE`, `SEQUENCE-COMPOSITION`, `PUBLICATION-PROVENANCE`, `CSV-PUBLICATION`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F02`, `S11-F03`, `S11-F04`, `S11-F05`, `S11-F06`, `S11-F07`, `S11-F08`, `S11-F09`, `S11-F10`
- Prior mechanisms reviewed: R16/R17 physical ownership and field failures, R18 lifecycle/Foam closure, R19 bounded release-chain validation, R20 delayed-reacquisition local contract, canonical reviewed truth, and the R20 consolidation with its named unknowns.
- Prior mechanisms rejected: count-only acceptance, global threshold changes, motion-only authority, whole-track future support, total-row stable support, ID/coordinate merging, unbounded retries/windows, post-hoc publication repair and private field-specific tuning.
- Preserved contracts: bounded current evidence, initial-state hard gates, distinct IDs, strict material/ambiguity handling, independent Foam, same-frame selection/projection and exact sequence/CSV provenance.
- Difference from prior failures: acceptance requires baseline-vs-new red/green behavioral witnesses at the two approved seams while keeping all other authorities and field disposition unchanged.
- Logic-map impact: `UPDATED — acceptance now covers the implemented delayed readiness and bounded Foam witness details in the existing owners.`
- Failure-registry impact: `UPDATED — evidence requirements distinguish F07 bounded episode authority and F08 delayed lifecycle admission without adding a causal class.`

## Detector Governance

- Logic-map nodes: `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `FOAM-EPISODE`, `PUBLICATION-PROVENANCE`, `TRACE-PUBLICATION`
- Failure-registry entries: `S11-F07`, `S11-F08`, `S11-F09`, `S11-F10`
- First harmful stage: delayed attempt admission after established owner loss and Foam episode confirmation; field source identity and reviewed-Y effectiveness remain unavailable locally.
- Logic-map impact: `UPDATED — the current owner details and validation gates are revised for the accepted local behavior.`
- Failure-registry impact: `UPDATED — existing failure guards are routed through the acceptance witness; no new failure entry is required.`
