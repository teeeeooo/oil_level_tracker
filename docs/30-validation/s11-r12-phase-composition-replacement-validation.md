# S11-R12 Phase/Composition Replacement Validation

## Gate status

**Status:** local gate passed. Secure-Windows validation pending.

R12 passes locally only when the replacement policies, replay, provenance,
runtime and full regression gates pass. Local success authorizes a Windows
replay; it does not close S11.

## Structural replacement gate

Tests and source inspection must prove:

- R11 motion-only bootstrap cannot publish Oil;
- `foam_distinct_lower_boundary` is not an anchor route;
- missing material/optics/motion evidence remains explicitly unavailable;
- Foam material identity expires or reseeds at bounded age/drift;
- `material_component_bottom_y` is not a hard Oil/Foam topology veto; and
- graph projection reads separate Oil and Foam validity.

No Base/Accum, filename, timestamp, Recipe identity or truth branch is allowed.

## Candidate and Oil gates

Controlled tests must cover:

1. a moving reflection/liquid/bracket sequence cannot become one authority
   path without independent phase identity at each anchor;
2. motion-only candidates remain admitted but non-numeric;
3. a true phase row from a weaker family survives stronger upper-residue
   candidates through reserved admission;
4. a bounded continuation run may extend only around an independent anchor;
5. a missing conflict feature cannot be treated as conflict `0.0` for an anchor;
6. user Artifact templates reject their matched candidate without granting
   authority to an unmatched row; and
7. every numeric Oil point equals one selected same-frame candidate.

For secure-Windows Base, reviewed Oil at 540/634/674 s is checked in source
coordinates. Late Y724–873 reflection/bracket paths must not become a long
numeric run. Candidate recall and publication accuracy are reported separately.

## Foam and composition gates

Controlled tests must prove:

- a dynamic narrow Foam component may enter the episode funnel;
- static narrow glare cannot use that route;
- rapid monotonic Foam rise survives bounded sampled-frame jumps;
- a short missing-component interval can bridge an episode without inventing a
  coordinate in the missing frame;
- broad material masks may cross Oil without causing a topology conflict when
  `foam_y < oil_y` is otherwise ordered;
- reversed or same-row Oil/Foam remains conflicted;
- confirmed Foam can be graph-valid while Oil/state is unresolved; and
- Oil remains graph-valid when Foam is absent or rejected.

For secure-Windows Accum, the 650–700 s funnel records raw, eligible,
episode-confirmed, public and graph-valid counts. The rising Foam front and the
lower Oil interface must remain separate. Residue around Y190–297 must not
replace reviewed lower Oil around Y450 solely through material persistence.

## Trace integrity gate

Basic trace must be sufficient to identify the first failing stage. For each
selected or near-truth candidate it records:

- representation/source and canonical Y;
- typed evidence values and availability;
- candidate admission and Artifact result;
- material identity/opposition;
- authority tier/reason/failed gates;
- trajectory component and anchor provenance; and
- final selection.

Frame state records both current-frame preview and final sequence positions.
Diagnostic image coordinates state their source/local origin and scale.

## Downstream gate

CSV/bundle round trips preserve `oil_is_valid`, `foam_is_valid` and legacy
`is_valid`. Old bundles without new fields remain readable. Review graphs use
Oil validity for Oil points and Foam validity for Foam points. Events, extrema,
captures and judgments continue to use legacy Oil/state validity and never use
an invalid Foam point as Oil evidence.

## Replay and performance gate

Run focused authority/trajectory/Foam/composition tests, four checked-in videos,
user-like Artifact replay, same-frame provenance and the full repository suite.
Record numeric counts, checked-truth error, Foam counts, longest missing/wrong
run and detector/resolver timing. Coverage is supporting evidence, never the
acceptance oracle.

```bash
.venv/bin/python -m tests.diagnostics.s11_r12_phase_composition_replay
.venv/bin/python -m tests.diagnostics.s11_r12_artifact_calibration_replay
.venv/bin/python -m pytest -q
.venv/bin/python -m compileall -q src tests
git diff --check
```

The exact committed head is then replayed on secure-Windows Base/Accum with the
saved user Artifact templates. Any long wrong-interface run, Foam-absent Base
episode, residue-as-Oil Accum run or loss of independent Foam graph publication
is a field failure regardless of aggregate coverage.
