# S11-R16 Directed Tracklet and Material Lifecycle Validation

## Acceptance boundary

R16 is a replacement candidate for the R15 private-Accum admission failure and
the overlapping identity/phase/selection responsibilities accumulated across
R13--R15. Local regression authorizes an independent exact-commit audit; it
does not replace a new private-Windows Base/Accum replay or supersede R15 as
the field authority.

**Local status:** `PASS` — exact execution results, fingerprints and runtime
identity are preserved in the
[R16 evidence record](../60-evidence/s11/s11-r16-directed-tracklet-material-lifecycle.md).
The current action and promotion sequence are owned by the
[work plan](../00-project/work-plan.md).

The design under test is the
[R16 architecture](../20-architecture/s11-r16-directed-tracklet-material-lifecycle-architecture.md).
Candidate-level causes are recorded in the
[R16 owner audit](../50-diagnostics/s11/s11-r16-local-coverage-owner-audit.md).

## Structural and causal gates

Automated evidence must prove all of the following:

- same-frame alternatives share a row hypothesis while preserving exact
  candidate offsets and physical tracklet IDs;
- ambiguous merge/split assignments terminate rather than exchange identity;
- tracklet confirmation/loss, phase intent and selection remain bounded;
- material phase emits the only allowed physical owner set before scoring;
- filled phase exposes no Oil candidate;
- unique compatible drain successors or re-entry may transfer phase ownership
  without merging physical IDs;
- ambiguous successors yield `UNKNOWN` and preserve a still-valid owner chain;
- non-publishable-only rows never enter selector scoring;
- a non-publishable representative cannot censor a publishable same-row
  sibling;
- candidate-order reversal selects the same deterministic physical member;
- the post-selector publication check is an assertion and cannot re-decide an
  owner;
- a composed confirmation/onset counterexample proves `t+6` is not an
  end-to-end commit, while data after `t+11` cannot change target Y, physical
  tracklet, phase, reason or owner chain; and
- every numeric result equals one selected Oil candidate from the same frame.

No production source may contain Base/Accum identifiers, reviewed timestamps,
truth Y values or source-family authority exceptions.

## Evidence-specific checked-video contract

The former R14/R15 aggregate `>=10/13` coverage check is superseded for R16 by
an evidence-specific safety contract:

- the first four sample3 onset rows are numeric, preserve the explicit phase
  owner/predecessor chain and remain within 26 px of reviewed Y316;
- the reconciled foreign opposite-direction branch from 34--39 s is
  explicitly `UNKNOWN`;
- the reviewed completed-fill cap contains zero numeric Oil;
- every numeric row retains exact same-frame provenance;
- the seven audited lower drain re-entry/continuation points remain numeric;
- owner-absence, bounded-loss and material-conflict windows remain
  `UNKNOWN`;
- sample4 reviewed-range and Foam controls do not regress; and
- checked numeric truth error is bounded independently of coverage.

This changes the corpus assertion, not production thresholds. Checked-truth
coverage remains diagnostic and cannot authorize a row. Any changed
four-video fingerprint requires candidate-level reconciliation.

## Performance and decomposition gates

The sample4 0--56 s, 2 FPS, debug-disabled workload must be measured through
the official static-learning, analysis, completed-window and bundle path. Every
timed repetition must match the accepted R16 row count and fingerprint.
Performance may improve through bounded tracklets, responsibility extraction,
cached typed evidence or duplicate-work removal; it may not trade away
accuracy, fail-closed abstention, ordering or provenance.

`oil_observation_resolver.py` must remain at or below 2,700 lines and
`OilPathLifecycleOwner` at or below 260 lines. The fixed-lag selector, directed
physical tracklets and material lifecycle remain separate owners. The legacy
completed-fill reacquisition method must have zero production definitions or
calls.

## Required local commands

```bash
.venv/bin/python -m compileall -q src tests

.venv/bin/python -m pytest -q \
  tests/unit/test_oil_interface_tracklets.py \
  tests/unit/test_oil_phase_lifecycle.py \
  tests/unit/test_oil_observation_resolver.py \
  tests/unit/test_jsonl_debug_trace.py \
  tests/test_r16_refactor_characterization.py \
  tests/test_oil_resolver_decomposition.py

.venv/bin/python -m pytest -q \
  tests/test_s11_temporal_reacquisition_continuity.py \
  tests/test_s11_sequence_observability_integrity.py

.venv/bin/python -m pytest -q
```

The four-video replay and three-repeat performance runner must additionally
enforce accepted output fingerprints. Their exact commands and results belong
to the evidence record, not this contract.

## Private-Windows gate

Only a head that passes independent exact-commit audit and is then pushed may
be replayed. In addition to the R15 Base/Foam checks, Accum initial EMPTY must
report physical tracklet IDs, row-hypothesis IDs, material phase, allowed owner
chain, motion/coverage and first publication failure. The audited
anchor-before-lower-observation pattern must be evaluated without coordinate,
timestamp or video-identity exceptions. Final Oil, Foam and CSV values remain
separate PASS conditions.

Coverage alone is not PASS. R16 remains a replacement candidate until this
external gate succeeds.
