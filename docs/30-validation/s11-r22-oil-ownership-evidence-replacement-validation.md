# S11-R22 Oil Ownership and Evidence Replacement Validation

**Status:** `LOCAL ACCEPTED — WINDOWS QUALIFICATION REQUIRED`

This contract validates the R22 replacement against the current R21 local
candidate. It does not promote local controls into Windows field evidence.

## Required controls

The focused lifecycle and resolver suites must cover:

- direct, near-snapshot and delayed release ordering, including one delayed
  attempt per established episode;
- a same-owner gradual initial-FULL drain that renews once before expiry and
  releases only after the unchanged minimum displacement and direction gates;
- stationary, oscillating, a single spike after expiry, no-renewal, late-anchor, expired-chain,
  incompatible/material-conflict and cross-ID renewal negatives;
- a prior cross-ID handoff that cannot renew merely because its latest owner is
  present, and a renewed lease that cannot transfer to another owner;
- non-nearest ordered-lower demotion carrying the typed contradiction through
  authority and tracking, including mixed-row members and gap/reappearance;
- delayed bootstrap/qualification reset for the contradicted owner, while a
  sparse continuation without contradiction remains eligible;
- current-frame selected candidate identity and Oil/Foam provenance equality;
- immutable frame decision snapshots and cached confirmation witness
  start/end/count/recent endpoint fields; and
- no numeric output for unavailable, ambiguous, lost or hard-invalid evidence.

## Verification commands

```text
python3 -m compileall -q src tests
python3 -m pytest -q tests/unit/test_oil_phase_lifecycle.py tests/unit/test_oil_evidence_replacement.py tests/unit/test_oil_observation_resolver.py tests/unit/test_oil_interface_tracklets.py tests/test_oil_resolver_decomposition.py
python3 -m pytest -q tests/test_s11_behavioral_repairs_integration.py tests/test_oil_detector_integration.py
python3 scripts/check_detector_governance.py --base-ref 0ad13ea645ca97c7f416e0c30bb3f8375e6b3927 --include-worktree
git diff --check
```

The Main-owned 13-case replay and serial performance comparison must compare
the same inputs and report source/runtime identity. No Windows speed or
accuracy claim follows from local PASS; canonical target-Windows qualification
remains outstanding.

## Acceptance and non-regression

No protected `.oiltruth` annotation, skip/xfail, safety oracle or golden may
be changed to obtain PASS. Every numeric result must remain a selected
same-frame candidate; no carry, interpolation, report-side repair or Foam
authority leakage is permitted. Any material lost guarantee is a decision
blocker for Main review.

## Detector Governance

- Logic-map nodes: `OIL-AUTHORITY`, `OIL-TRACKLET`, `OIL-PHASE-INITIAL`,
  `OIL-PHASE-FILL`, `OIL-PHASE-DRAIN`, `OIL-PROJECTION`.
- Failure-registry entries: `S11-F03`, `S11-F04`, `S11-F08`, `S11-F09`,
  `S11-F10`.
- First harmful stage: Base bounded displacement/admission and Accum retained
  contradictory identity are the targeted boundaries. All 13 replay cases and
  provenance comparisons are unchanged; physical field repair remains unverified.
- Logic-map impact: UPDATED — validation covers the R22 ownership/evidence
  replacement and cached witness contract.
- Failure-registry impact: NONE — validation preserves existing history and
  adds no new field claim.
